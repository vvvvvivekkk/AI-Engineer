# Module 05 — Trainer Notes

Read `concepts.md` and run all four notebooks yourself first, ideally once locally and once on Colab with a GPU runtime, so you have seen both `device: cpu` and `device: cuda`. Plan two sessions of about 2 hours (weeks 9 and 10).

---

## 1. What students should be able to do after the sessions

- Draw a neuron and explain weights, bias and activation using the "should I go to the party?" example.
- Explain why activations are needed (without them, layers collapse into one straight line).
- Explain gradient descent with the foggy-hill analogy and say what the learning rate controls.
- Create tensors, check `.shape`/`.dtype`/`.device`, and use autograd to get a gradient.
- Write an `nn.Module` and the five-step training loop from memory, and explain each line.
- Plot training and validation loss, and diagnose healthy / overfitting / underfitting curves.
- Build a CNN for 8×8 images and trace tensor shapes through it.
- Apply dropout and early stopping, and save/load a `state_dict`.

## 2. Teaching sequence and timing

### Session 1 (2 hours) — "From neuron to training loop"

| Time | Activity | Materials | Notes |
|---|---|---|---|
| 0:00–0:10 | Hook: show the digits; "logistic regression gets ~96%; how do phone cameras recognise faces?" | Notebook 02 first images | Motivate learned features. |
| 0:10–0:25 | Neuron (party example) and activations | Slides 3–4 | Ask a student to be the neuron and "decide" with weights you give. |
| 0:25–0:35 | Layers, MLP, logits, parameter counting | Slide 5, Excel Parameter Counter | Have students count parameters for 64→128→10 on paper. |
| 0:35–0:50 | Loss and gradient descent (foggy hill); backprop (football replay) | Slides 6–8 | Draw the parabola; walk the steps. |
| 0:50–1:15 | Live-code notebook 01: tensors, autograd, gradient descent by hand, then `nn.Linear` | Notebook 01 | Do the `lr = 1.5` experiment live. Show gradients accumulating. |
| 1:15–1:20 | Break | | |
| 1:20–1:50 | Notebook 02: `nn.Module`, `DataLoader`, training loop line by line, loss curves | Slides 10–13 | Students say the five steps aloud before you run the cell. |
| 1:50–2:00 | Save/load weights; recap; set Exercises 1–5 | Slide 17 | Exit ticket: "Write the five lines inside the batch loop." |

### Session 2 (2 hours) — "CNNs, overfitting and GPUs"

| Time | Activity | Materials |
|---|---|---|
| 0:00–0:10 | Recap: students write the training loop on paper; compare | — |
| 0:10–0:30 | Convolution (torch on a wall) and pooling; notebook 03 parts 1–2 | Slide 14, Notebook 03 |
| 0:30–0:50 | Build the CNN; shape tracing; Excel conv shape calculator | Slide 15, Notebook 03 parts 3–4 |
| 0:50–1:05 | Train MLP vs CNN; look at learned filters | Notebook 03 parts 5–6 |
| 1:05–1:10 | Break | — |
| 1:10–1:40 | Overfitting on 200 images; dropout; early stopping | Slide 16, Notebook 04 |
| 1:40–1:50 | GPUs and Colab: switch runtime live and rerun notebook 02 | Slide 18 |
| 1:50–2:00 | Common mistakes; set Exercises 6–12 | Slides 19–20 |

## 3. Common student mistakes and how to fix them

1. **Forgetting `optimizer.zero_grad()`.** Symptom: loss behaves erratically or explodes. Fix: show the gradient-accumulation cell in notebook 01; make "zero, backward, step" a chant.
2. **Adding softmax before `CrossEntropyLoss`.** Symptom: training is very slow, accuracy stuck. Fix: the loss takes raw logits and applies softmax itself; remove the extra softmax (use it only when you want to *display* probabilities).
3. **Labels with the wrong dtype.** Symptom: `RuntimeError: expected scalar type Long but found Float`. Fix: `torch.tensor(y, dtype=torch.long)`.
4. **Model and data on different devices.** Symptom: `Expected all tensors to be on the same device`. Fix: `model.to(device)` once, and `xb.to(device), yb.to(device)` for every batch.
5. **Forgetting `model.eval()` / `torch.no_grad()` when evaluating.** Symptom: accuracy changes every time you run it (dropout still active), or memory grows. Fix: always pair `model.eval()` with `with torch.no_grad():`, and `model.train()` at the start of each epoch.
6. **Wrong input shape for `Conv2d`.** Symptom: `Expected 3D (unbatched) or 4D (batched) input`. Fix: reshape to `(batch, channels, height, width)`: `x.reshape(-1, 1, 8, 8)`.
7. **`Linear` input size mismatch after flattening.** Symptom: `mat1 and mat2 shapes cannot be multiplied (64x128 and 512x10)`. Fix: push a fake batch through and print shapes after each layer (notebook 03 shows how).
8. **Converting a GPU tensor to NumPy directly.** Symptom: `can't convert cuda:0 device type tensor to numpy`. Fix: `t.detach().cpu().numpy()`.
9. **Looking only at training loss.** Symptom: "my loss is 0.001, it's perfect!" Fix: always plot validation loss too (notebook 04 shows train loss near 0 while validation loss rises).
10. **Learning rate far too high or low.** Symptom: loss becomes `nan` or barely moves. Fix: try 1e-2, 1e-3, 1e-4 (Exercise 5).

## 4. Questions to check understanding (with answers)

1. **Q:** What would happen if we removed all ReLUs from a deep MLP?
   **A:** The whole network collapses into one linear function — no more power than linear/logistic regression.
2. **Q:** In one sentence, what does `loss.backward()` do?
   **A:** Computes the gradient of the loss with respect to every weight and stores it in each weight's `.grad`.
3. **Q:** Why do we call `optimizer.zero_grad()` every batch?
   **A:** PyTorch adds new gradients to existing ones; without zeroing, gradients from earlier batches would pile up.
4. **Q:** Training loss keeps falling, validation loss started rising at epoch 20. What do you do?
   **A:** It is overfitting: use early stopping (keep epoch-20 weights), add dropout or weight decay, or get more data.
5. **Q:** What is the output shape of `Conv2d(1, 16, 3, padding=1)` on a batch of shape (32, 1, 8, 8)? And after `MaxPool2d(2)`?
   **A:** (32, 16, 8, 8), then (32, 16, 4, 4).
6. **Q:** Why does a CNN need far fewer parameters than an MLP for images?
   **A:** Weight sharing — each small filter is reused at every position instead of having a separate weight for every pixel pair.
7. **Q:** What is the difference between an epoch and a batch?
   **A:** A batch is a small group of examples used for one weight update; an epoch is one full pass over all training examples (many batches).
8. **Q:** Why might a GPU *not* speed up our 8×8 digit models?
   **A:** The data and models are so small that the time spent moving data to the GPU and launching work outweighs the parallel maths.
9. **Q:** What do you need in order to load a saved `state_dict`?
   **A:** The model's class definition (code) to rebuild the same architecture, then `load_state_dict(torch.load(path, map_location=device))`.

## 5. Adapting for faster or slower groups

**Slower groups**
- Spend all of session 1 on notebook 01 and the first half of notebook 02; leave CNNs for session 2 and skip learned-filter visualisation.
- Use `nn.Sequential` everywhere first; introduce the `nn.Module` class version later.
- Print the training loop on paper and have students annotate each line with the analogy (shoot, see the miss, forget, work out the fix, adjust).
- Skip checkpoints; keep `state_dict` save/load only.

**Faster groups**
- Add `nn.BatchNorm2d` after each conv and compare training speed.
- Try `torch.optim.SGD(momentum=0.9)` vs Adam; plot both loss curves.
- Add a learning-rate scheduler (`torch.optim.lr_scheduler.StepLR`).
- Train on Colab GPU and time one epoch on CPU vs GPU with a much larger hidden size (e.g. 4096) to see when the GPU starts to win.
- Exercise 11 extended: implement shift-with-zero-padding augmentation and compare with wrap-around.

## Practical tips

- Run every notebook once before class; Colab's first `import torch` takes a few seconds.
- If a student's laptop is slow, the notebooks already set `torch.set_num_threads(1)` on CPU, which is fastest for these tiny models.
- Keep the training-loop diagram (`images/training-loop.png`) visible during all coding.
