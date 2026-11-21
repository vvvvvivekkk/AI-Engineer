"""
dpo_loss.py - the Direct Preference Optimization (DPO) loss in a few lines of PyTorch.

loss = -log sigmoid( beta * [ (pi_c - ref_c) - (pi_r - ref_r) ] )
  pi_c / pi_r   = policy log-probability of the chosen / rejected answer
  ref_c / ref_r = frozen reference model log-probability of the same answers

Run:  python code/dpo_loss.py
"""
import torch                                         # tensors + automatic gradients
import torch.nn.functional as F                      # logsigmoid


def dpo_loss(pi_c, pi_r, ref_c, ref_r, beta=0.1):
    """Average DPO loss over a batch. All inputs are 1-D tensors of log-probs."""
    chosen_reward = beta * (pi_c - ref_c)            # implicit reward of the chosen answer
    rejected_reward = beta * (pi_r - ref_r)          # implicit reward of the rejected answer
    return -F.logsigmoid(chosen_reward - rejected_reward).mean()


if __name__ == "__main__":
    # Toy numbers from concepts.md section 7.
    pi_c = torch.tensor([-12.0], requires_grad=True)   # we want gradients for the policy values
    pi_r = torch.tensor([-15.0], requires_grad=True)
    ref_c, ref_r = torch.tensor([-14.0]), torch.tensor([-13.0])   # reference is frozen
    loss = dpo_loss(pi_c, pi_r, ref_c, ref_r)
    loss.backward()                                    # compute gradients
    print(f"loss = {loss.item():.3f}")                 # about 0.513
    print(f"d loss / d pi_c = {pi_c.grad.item():+.4f}  (negative -> raise chosen)")
    print(f"d loss / d pi_r = {pi_r.grad.item():+.4f}  (positive -> lower rejected)")
    # When the policy equals the reference the margin is 0 and loss = log(2).
    same = dpo_loss(ref_c, ref_r, ref_c, ref_r)
    print(f"loss when policy == reference = {same.item():.4f}")
