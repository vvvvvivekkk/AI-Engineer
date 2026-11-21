<!-- nav:start -->
> [🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 11 AI Automation](../11-ai-automation/README.md) · [13 Fine-tuning (LoRA / QLoRA) ➡️](../13-fine-tuning/README.md)  
> **🏷️ Module 12 · Data Annotation & RLHF**  
> [📖 Lesson](concepts.md) · [📄 PDF handout](pdf/12-data-annotation-and-rlhf-handout.pdf) · [🎞️ Slides](slides/12-data-annotation-and-rlhf.pptx) · [📓 Notebooks](notebooks/) · [✍️ Exercises](exercises.md) · [✅ Solutions](solutions/) · [🧑‍🏫 Trainer notes](trainer-notes.md) · [🔗 Resources](resources.md)
<!-- nav:end -->

# Module 12 - Data Annotation, RLHF and Evaluations (week 20)

This module explains where an AI model's "taste" comes from: humans labelling data, comparing answers, and grading outputs. You will label data yourself, measure how much annotators agree (Cohen's kappa), train a tiny **reward model** (a model that scores answers), compute the **DPO** loss (a simpler way to teach a model human preferences), design an evaluation **rubric** (scoring guide), and learn what **AI trainer** jobs involve and how to get one.

## Learning goals

By the end you can:
1. Explain why labelled data quality decides model quality, and name six annotation types.
2. Choose a labelling tool (Label Studio, Argilla, CVAT, doccano, Prodigy) for a given job.
3. Write annotation guidelines with definitions, examples and edge cases.
4. Compute Cohen's kappa by hand and with scikit-learn, and say what the number means.
5. Draw the RLHF pipeline (SFT → reward model → PPO) and explain each stage.
6. Explain DPO, compute its loss on toy numbers, and say why it is simpler than PPO.
7. Write preference data in JSONL format.
8. Design an eval with a rubric, use an LLM-as-judge safely, and know the main biases.
9. Describe AI trainer work, the main platforms, and how to pass qualification tests.

## Prerequisites

- Module 02 (pandas, numpy) and module 05 (PyTorch basics: tensors, loss, `backward()`, optimizer).
- Module 07 (what an LLM is, tokens, probabilities) helps for sections 6-7.

## Time estimate

- Reading `concepts.md`: 75 minutes.
- Notebooks: about 2 hours in total.
- Exercises: 2-3 hours.
- Classroom session: 2 hours (see `trainer-notes.md`).

## Which tool to use, and why

| Notebook | Where | Why |
|---|---|---|
| 01-annotation-and-kappa | Colab or local Jupyter | Pure pandas/scikit-learn, runs in seconds anywhere |
| 02-reward-model | Colab or local Jupyter | Tiny PyTorch model on word counts; CPU is plenty |
| 03-dpo-loss-demo | Colab or local Jupyter | Toy tensors, plus one small model download (~270 MB) for real log-probs |
| 04-evals-rubric-and-judge | Colab or local Jupyter | Works offline; uses Claude only if `ANTHROPIC_API_KEY` is set |

Use **Colab** if you do not have Python set up (click the badge at the top of each notebook). Use **VS Code** for the scripts in `code/`. To try a real labelling tool, install Label Studio locally (`pip install label-studio`, then `label-studio start`) and paste `code/label_studio_config.xml` into a new project.

## API keys

Nothing here needs a key. If you want notebook 04 and `code/llm_judge.py` to use a real LLM judge, copy `.env.example` to `.env` and put your own key there. Never commit `.env`.

## File map

| Path | What it is |
|---|---|
| `concepts.md` | The main lesson - read this first |
| `images/` | Diagrams (PNG) and their Mermaid sources (`.mmd`) |
| `notebooks/01-annotation-and-kappa.ipynb` | Label reviews, confusion matrix, kappa by hand and with sklearn, gold questions, adjudication |
| `notebooks/02-reward-model.ipynb` | Synthetic preference pairs → tiny reward model → reward hacking demo |
| `notebooks/03-dpo-loss-demo.ipynb` | DPO loss by hand and in PyTorch, gradients, beta, a toy policy, real log-probs |
| `notebooks/04-evals-rubric-and-judge.ipynb` | Rubric, offline/Claude judge, judge-vs-human kappa, position bias, win rate |
| `code/kappa.py` | Cohen's and Fleiss' kappa from scratch |
| `code/reward_model.py` | Reward model trained on `data/preference_pairs_sample.jsonl` |
| `code/dpo_loss.py` | DPO loss and its gradients |
| `code/llm_judge.py` | Rubric grading with Claude or an offline stand-in |
| `code/label_studio_config.xml` | Label Studio interface for A/B preference labelling |
| `data/preference_pairs_sample.jsonl` | 20 example preference pairs (prompt / chosen / rejected) |
| `data/reviews_to_label.csv` | 20 reviews for the labelling exercise |
| `slides/12-data-annotation-and-rlhf.pptx` | Teaching deck with speaker notes |
| `pdf/12-data-annotation-and-rlhf-handout.pdf` | Printable version of `concepts.md` |
| `excel/annotation-toolkit.xlsx` | Guideline template, kappa calculator (live formulas), kappa scale, rubric template |
| `excel/ai-trainer-job-tracker.xlsx` | Track platforms, applications, assessments, earnings |
| `exercises.md` / `solutions/` | 12 exercises (easy → hard) and worked solutions |
| `trainer-notes.md` | How to teach this module |
| `resources.md` | Curated further reading |
| `build.py` | Regenerates images, notebooks, slides, PDF and Excel |

Rebuild everything: `python 12-data-annotation-and-rlhf/build.py` (from the repo root).

<!-- nav:start -->
---
[🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 11 AI Automation](../11-ai-automation/README.md) · [13 Fine-tuning (LoRA / QLoRA) ➡️](../13-fine-tuning/README.md)
<!-- nav:end -->
