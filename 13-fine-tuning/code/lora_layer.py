"""
lora_layer.py - a LoRA (Low-Rank Adaptation) linear layer written from scratch.

LoRA keeps a pre-trained weight matrix W frozen and learns a small change:
    output = W x + (alpha / r) * B A x
where A has shape (r, in_features) and B has shape (out_features, r).

Run:  python code/lora_layer.py      (runs a small self-test)
"""
import math                      # for sqrt in the initialisation
import torch                     # tensors and autograd
import torch.nn as nn            # neural-network building blocks


class LoRALinear(nn.Module):
    """Wrap an existing nn.Linear with a trainable low-rank update."""

    def __init__(self, base: nn.Linear, r: int = 8, alpha: float = 16, dropout: float = 0.0):
        super().__init__()
        self.base = base                                   # the pre-trained layer
        for p in self.base.parameters():
            p.requires_grad = False                        # freeze W and its bias
        d, k = base.out_features, base.in_features         # W has shape (d, k)
        self.A = nn.Parameter(torch.empty(r, k))           # A: r x k
        nn.init.kaiming_uniform_(self.A, a=math.sqrt(5))   # small random values (same idea as peft)
        self.B = nn.Parameter(torch.zeros(d, r))           # B: d x r, zeros -> no change at start
        self.scaling = alpha / r                           # how strongly the update is applied
        self.dropout = nn.Dropout(dropout)                 # optional regularisation on the input
        self.merged = False                                # becomes True after merge()

    def forward(self, x):
        out = self.base(x)                                 # the frozen layer's normal output
        if not self.merged:                                # add the low-rank update unless merged
            out = out + (self.dropout(x) @ self.A.T @ self.B.T) * self.scaling
        return out

    @torch.no_grad()
    def merge(self):
        """Fold B A into W so inference costs nothing extra."""
        if not self.merged:
            self.base.weight += self.scaling * (self.B @ self.A)
            self.merged = True

    def trainable_parameters(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def add_lora(model: nn.Module, target_names, r=8, alpha=16):
    """Replace every nn.Linear whose attribute name is in target_names with a LoRALinear."""
    for name, child in model.named_children():
        if isinstance(child, nn.Linear) and name in target_names:
            setattr(model, name, LoRALinear(child, r=r, alpha=alpha))   # swap the layer in place
        else:
            add_lora(child, target_names, r, alpha)                    # look deeper inside
    return model


if __name__ == "__main__":
    torch.manual_seed(0)
    base = nn.Linear(4096, 4096)                                       # size of a 7B-model attention matrix
    layer = LoRALinear(base, r=8, alpha=16)
    print(f"trainable: {layer.trainable_parameters():,} of {base.weight.numel():,} "
          f"({100 * layer.trainable_parameters() / base.weight.numel():.2f}%)")
    x = torch.randn(2, 4096)
    print("unchanged at start:", torch.allclose(base(x), layer(x)))
    with torch.no_grad():
        layer.B.normal_(std=0.01)                                      # pretend we trained
    before = layer(x)
    layer.merge()
    print("merge keeps outputs:", torch.allclose(before, layer(x), atol=1e-4))
