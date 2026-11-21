# Module 12 - Resources

Curated from the course source-notes (which draw on the community lists *opendilab/awesome-RLHF*, *taivop/awesome-data-annotation* and *pietro93/awesome-ai-training-jobs*). Each link has one line on why it is worth your time. Links were checked when the catalogue was written (late 2026); products change, so confirm details on the official pages.

## Start here
- [Illustrating RLHF - Hugging Face blog](https://huggingface.co/blog/rlhf) - the clearest visual walkthrough of SFT → reward model → PPO. Read after section 6 of `concepts.md`.
- [Your AI Product Needs Evals - Hamel Husain](https://hamel.dev/blog/posts/evals/) - why careful human labelling of your own outputs is the root of good evals.
- [Reinforcement Learning from Human Feedback - Nathan Lambert (online book)](https://rlhfbook.com/) - a full, current book on preference data, reward models, PPO, DPO and evaluation.

## Papers (read the abstract and figures first)
- [Training language models to follow instructions with human feedback (InstructGPT)](https://arxiv.org/abs/2203.02155) - the paper that made RLHF the standard recipe for chat assistants.
- [Deep reinforcement learning from human preferences](https://arxiv.org/abs/1706.03741) - the original idea of learning a reward from pairwise human comparisons.
- [Learning to summarize from human feedback](https://arxiv.org/abs/2009.01325) - preference-trained models beat much larger supervised ones on a clear task.
- [Constitutional AI](https://arxiv.org/pdf/2212.08073.pdf) - replaces much human labelling with AI feedback guided by written principles (RLAIF).
- [Reward Hacking in RL - Lilian Weng](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/) - why reward models get gamed; context for notebook 02's hacking demo.

## Video
- [RLHF: Progress and Challenges - John Schulman](https://www.youtube.com/watch?v=hhiLw5Q_UFg) - first-hand account of why RLHF works and where it struggles.

## Hands-on code and datasets
- [RLHF in Notebooks](https://github.com/ash80/RLHF_in_notebooks) - step-by-step notebooks (GPT-2, reward model, PPO) small enough for Colab; the natural next step after our notebooks 02-03.
- [TRL - Transformer Reinforcement Learning](https://github.com/huggingface/trl) - Hugging Face library with SFT, reward modelling, DPO and RL trainers.
- [Anthropic HH-RLHF dataset](https://github.com/anthropics/hh-rlhf) - a real chosen/rejected preference dataset; inspect it to see real preference labels.
- [Stanford Human Preferences (SHP)](https://huggingface.co/datasets/stanfordnlp/SHP) - naturally occurring preferences across 18 domains, good for reward-model exercises.

## Annotation tools
- [Label Studio](https://github.com/heartexlabs/label-studio) - one configurable tool for text, images, audio and rating LLM answers; our default lab tool.
- [Rubrix (now Argilla)](https://github.com/recognai/rubrix) - Python-first curation of text and LLM feedback; the old repo name points to the current project.
- [CVAT](https://github.com/opencv/cvat) - the standard open tool for image and video labelling (boxes, polygons, tracking).
- [doccano](https://github.com/chakki-works/doccano) - the simplest web tool for text NER and classification.
- [Prodigy](https://prodi.gy/) - paid, scriptable active-learning annotator from the spaCy team.
- [Potato](https://github.com/davidjurgens/potato) - built for human evaluation and preference collection.
- [labelme](https://github.com/wkentaro/labelme) - a light, fully offline desktop polygon labeller.
- [awesome-dataset-tools](https://github.com/jsbroks/awesome-dataset-tools) - a wider list of dataset and labelling utilities.

## AI trainer jobs
Important: many sign-up links on the web carry referral codes. The links below are independent review and guide pages; find each platform's official site yourself. Pay figures on any site are self-reported and vary - check current listings. A real platform never charges you to join.

- [Platform comparison](https://aitrainer.work/platforms) - pay, requirements and reviews side by side; start here to choose where to apply.
- [Beginner's guide to AI training](https://aitrainer.work/guides/what-is-ai-training-beginner-guide) - what the work involves and who qualifies.
- [How to find AI training jobs](https://aitrainer.work/guides/how-to-find-ai-training-jobs) - how to pick and sequence platforms.
- [Is AI training legit or a scam?](https://aitrainer.work/guides/is-ai-training-legit-scam-guide) - warning signs and how to check a platform.
- [What are rubrics in AI training?](https://aitrainer.work/guides/what-are-rubrics-ai-training) - the rubric grading tested in assessments; pairs with section 9.4.
- [What is adversarial AI training?](https://aitrainer.work/guides/what-is-adversarial-ai-training) - red-teaming and safety tasks explained.
- [AI training for developers](https://aitrainer.work/guides/best-ai-training-platforms-developers-coders) - which platforms want coders and what code-review tasks involve.
- [Jobs: coding & software](https://aitrainer.work/jobs/coding) and [Jobs: entry-level](https://aitrainer.work/jobs/entry-level) - live listing categories most relevant to this course.
- [Mercor AI interview guide](https://aitrainer.work/guides/mercor-ai-interview-guide) - preparing for an automated screening interview.
- [SME Careers assessment guide](https://aitrainer.work/guides/sme-careers-application-assessment-guide) - what one platform's application test covers.
- [Running AI training on multiple platforms](https://aitrainer.work/guides/full-time-ai-training-multiple-platforms) - smoothing out gaps between projects.
- [AI Trainer Academy](https://aitrainer.work/academy) - free RLHF-fundamentals course for would-be raters (note: the site earns from referrals).

Platform review pages (no referral): [Mercor](https://aitrainer.work/platforms/mercor) · [Micro1](https://aitrainer.work/platforms/micro1) · [Turing](https://aitrainer.work/guides/turing-ai-training-review) · [SME Careers](https://aitrainer.work/guides/sme-careers-review) · [Alignerr](https://aitrainer.work/guides/alignerr-review) · [Ethos](https://aitrainer.work/guides/ethos-expert-network-review)
