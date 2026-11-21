# SOURCES

The nine source repositories this curriculum was researched from, their licences, and how each is used. Licences were checked on 2026-11-21. If you reuse material, check the licence again, because licences can change.

Checked on 2026-11-21 by reading each repository's LICENSE file. For the three repos with no LICENSE file in the clone, the GitHub repo page was also checked; none showed a licence.

**General policy for the curriculum:** we **link** to resources and write our **own** descriptions and analysis. We do not copy README text, tables or prompt text into course material, whatever the licence says. Permissive licences (CC0, MIT, Apache-2.0, CC-BY-4.0) would allow more reuse, but linking plus original commentary keeps every source on the same simple footing.

| # | Source | Licence | Reuse allowed | How we use it |
|---|--------|---------|---------------|---------------|
| 1 | openbestof/awesome-ai | None found | Link only | Tool and framework discovery |
| 2 | x1xhlol/system-prompts-and-models-of-ai-tools | GPL-3.0 | Link + our own analysis only | Prompt-design case studies |
| 3 | pietro93/awesome-ai-training-jobs | CC0-1.0 | Anything (we still only link) | AI-trainer careers module |
| 4 | taivop/awesome-data-annotation | None found | Link only | Annotation tools list |
| 5 | opendilab/awesome-RLHF | Apache-2.0 | Yes, with attribution | RLHF papers, code, datasets |
| 6 | ashishpatel26/500-AI-...-Projects-with-code | None found | Link only | Project ideas |
| 7 | Eric-LLMs/awesome-ai-engineering | CC-BY-4.0 | Yes, with attribution | LLMOps, agents, MCP, memory, evals |
| 8 | dipakkr/awesome-ai-engineering | MIT (2018, Deepak Kumar) | Yes, keep the notice | Beginner Python/ML/math, careers |
| 9 | dave-nachman/awesome-ai-engineering | CC0-1.0 | Anything | AI-engineering reading and tools |

---

## 1. openbestof/awesome-ai
- **URL:** https://github.com/openbestof/awesome-ai
- **Licence:** No licence file found — all rights reserved by default; we only link. (The clone holds only `readme.md`. The GitHub page shows no LICENSE file and no licence entry.)
- **Summary:** A catalogue of open-source AI software, laid out as tables with an icon, name, one-line description and star badge for each entry. Categories: AI APIs and cookbooks (OpenAI, Anthropic, Gemini, Groq, Mistral, Cohere, LiteLLM), AI cloud platforms, local LLM backends (llama.cpp, Ollama, vLLM, LocalAI), chat front-ends (Open WebUI, LibreChat, LM Studio, Jan), Stable Diffusion tools, code assistants, autonomous-agent frameworks (AutoGen, CrewAI, MetaGPT, AutoGPT, LlamaIndex), knowledge managers / "chat with your docs" apps, eval tools, LLM app frameworks (LangChain, Dify, Flowise), training libraries, vector databases (Chroma, Qdrant, Weaviate, Milvus), course repos and audio tools. Last commit was May 2024, so some entries are old (for example, old repo paths for Ollama and CrewAI).
- **How we use it:** For tool discovery in modules 07, 09, 10, 11 and 14. Links only, and we prefer current official docs where they exist.

## 2. x1xhlol/system-prompts-and-models-of-ai-tools
- **URL:** https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools
- **Licence:** GNU GPL v3 (`LICENSE.md`). Caveat: the files are claimed system prompts of commercial products (Cursor, Devin, Lovable, v0, Perplexity, Notion AI, Claude Code and others), collected from leaks or extraction. The repo owner almost certainly does not own the copyright in those texts, so the GPL notice may not cover them. Their authenticity and how current they are cannot be verified either.
- **Summary:** About 30 folders, one per product, holding prompt `.txt` files and often a tools `.json`/`.yaml` (function schemas). Also an "Open Source prompts" folder (Cline, Bolt, Codex CLI, Gemini CLI, RooCode, OpenCode and others). The README is mostly sponsorship and donation text.
- **How we use it:** Only for our own structural analysis in `08-system-prompt-patterns.md`, with links to folders. **No prompt text is reproduced.** Learners are told to treat the prompts as unverified case studies.

## 3. pietro93/awesome-ai-training-jobs
- **URL:** https://github.com/pietro93/awesome-ai-training-jobs
- **Licence:** CC0 1.0 Universal (public domain dedication).
- **Summary:** An awesome-list explaining what AI-training / RLHF / data-annotation freelance work is, with a platform table (Mercor, Micro1, Turing, SME Careers, Alignerr, Rex, Vetto, Ethos, Mindrift) giving rough pay bands. Also has job listings by expertise, getting-started and scam-awareness guides, and per-platform interview guides. Nearly every guide points to aitrainer.work, the site that maintains the list. **The platform sign-up links in the README carry referral codes**, so the list has a commercial interest.
- **How we use it:** In the careers module (`12-ai-trainer-jobs.md`, `16-careers.md`). We link to the neutral review/guide pages or to platform home pages, and **we do not reuse the referral links**.

## 4. taivop/awesome-data-annotation
- **URL:** https://github.com/taivop/awesome-data-annotation
- **Licence:** No licence file found — all rights reserved by default; we only link. (The GitHub page shows no licence.)
- **Summary:** A tool list grouped by data type: image/video (open source and commercial), text, multimodal/point-cloud, embeddable UI components, and other (genomics, audio, human-in-the-loop). The author recommends CVAT for computer vision. Last updated June 2022, so some commercial entries may be defunct (for example, Figure Eight and DataTurks).
- **How we use it:** The annotation-tools half of module 12 and of `12-ai-trainer-jobs.md`.

## 5. opendilab/awesome-RLHF
- **URL:** https://github.com/opendilab/awesome-RLHF
- **Licence:** Apache License 2.0.
- **Summary:** A research-paper index for reinforcement learning from human feedback, listed year by year from before 2020 up to 2026 (many recent OpenReview/ICLR papers on DPO and GRPO variants). It also has sections for codebases (TRL, OpenRLHF, veRL, DeepSpeed-Chat, an RLHF-in-notebooks tutorial, the Potato annotation tool), preference datasets (Anthropic HH-RLHF, Stanford SHP, OpenAI summarize-from-feedback, LIMA), blogs (Hugging Face's illustrated RLHF post, Lilian Weng on reward hacking) and books (Nathan Lambert's RLHF book). The README's "detailed explanation" section was machine-generated, so we do not rely on it.
- **How we use it:** Modules 12 (RLHF concepts, preference data) and 13 (post-training libraries). Links only.

## 6. ashishpatel26/500-AI-Machine-learning-Deep-learning-Computer-vision-NLP-Projects-with-code
- **URL:** https://github.com/ashishpatel26/500-AI-Machine-learning-Deep-learning-Computer-vision-NLP-Projects-with-code
- **Licence:** No licence file found — all rights reserved by default; we only link. (The GitHub page shows no licence.)
- **Summary:** One table of 103 links to other project collections: Medium/blog roundups ("10 ML projects on regression", "6 sentiment analysis projects", "4 chatbot projects"), Data-Flair idea lists, and many awesome-lists (awesome-machine-learning, awesome-nlp, learnopencv, awesome-production-machine-learning). There is no code in the repo itself, and it is pre-LLM in focus. Many links are blog posts that may be paywalled or have moved.
- **How we use it:** As a source of project *ideas* for `15-projects.md`. We reimplement everything ourselves on small offline data.

## 7. Eric-LLMs/awesome-ai-engineering
- **URL:** https://github.com/Eric-LLMs/awesome-ai-engineering
- **Licence:** Creative Commons Attribution 4.0 International (CC-BY-4.0).
- **Summary:** A "full-stack AI engineering playbook" with chapters on LLMs in production, private AI infrastructure (vLLM, SGLang, Ollama, Ray, LiteLLM, DeepSpeed, Unsloth, LLaMA-Factory, PEFT, TRL, OpenRLHF, veRL, guardrails tools), building agents (Claude Code, Codex CLI and other reference agents), MCP (spec, SDKs, servers, registry, FastMCP, A2A), agent memory (Mem0, Letta, LangMem, Graphiti) and agent evaluation (LangSmith, Langfuse, Phoenix, DeepEval, Promptfoo, OpenAI Evals). Each chapter comes with mind maps and slide PDFs stored in `summaries/`.
- **How we use it:** Modules 09, 10, 13 and 14. Links only. If we ever adapt a mind map or slide, we must credit "Eric-LLMs, CC-BY-4.0".

## 8. dipakkr/awesome-ai-engineering
- **URL:** https://github.com/dipakkr/awesome-ai-engineering
- **Licence:** MIT License, Copyright (c) 2018 Deepak Kumar.
- **Note:** Despite the repo name, the README is the long-running **"A to Z Resources for Students"** list (badges point to `dipakkr/A-to-Z-Resources-for-Students`). It is a general student list, not an AI-engineering list.
- **Summary:** Beginner coding resources, Python tutorials, ML/DL/LLM courses and books, research-paper sites, datasets, Git/Docker resources, interview prep (DSA, aptitude), student developer packs, open-source programmes (GSoC, Outreachy), hackathon portals, internship portals and people/channels to follow. Subfolders hold extra notes (`ML/ML.md` with maths-for-ML links, `Python/Python.md`, `Projects/Projects.md`, cheat sheets).
- **How we use it:** Modules 00–05 (beginner Python, data, maths, ML/DL courses) and 16 (careers, internships, hackathons). Links only.

## 9. dave-nachman/awesome-ai-engineering
- **URL:** https://github.com/dave-nachman/awesome-ai-engineering
- **Licence:** CC0 1.0 Universal.
- **Summary:** A short, high-quality list for working AI engineers. Guides (Anthropic courses, OpenAI Cookbook, Prompt Engineering Guide, RAG Techniques, applied-llms.org), podcasts, conference talks, key articles (Hamel Husain on evals, Eugene Yan on LLM patterns and LLM-as-judge, Lilian Weng on agents and prompting, Chip Huyen on agents, 12-Factor Agents), books, blogs, and tools (LangChain, LlamaIndex, Instructor, Outlines, LiteLLM, Langfuse, LangSmith, Inspect, Gradio, Streamlit, vLLM, TGI, Axolotl).
- **How we use it:** Modules 07–10, 13, 14 and 16. Links only.

---

## Official documentation
Modules also link to official documentation (python.org, pytorch.org, scikit-learn.org, huggingface.co, docs.anthropic.com, platform.openai.com, ai.google.dev, ollama.com, LangGraph, CrewAI, modelcontextprotocol.io, n8n.io, docs.vllm.ai, langfuse.com, and others). Each module's `resources.md` and the root `RESOURCES-MASTER.xlsx` list every link along with where it came from.

## What we did NOT do
- We did not copy README tables, descriptions or code from any source. All explanations are our own.
- We did not reproduce any system prompt from source 2. Module 08 contains only our structural analysis, with links to the folders.
- We did not reuse referral or affiliate links from source 3.
