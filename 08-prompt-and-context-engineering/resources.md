# Module 08 — Resources

Curated from the course's source catalogues (see the root `SOURCES.md` for licences). Links only; descriptions are ours. Fast-changing pages (model names, API features) — always check the official docs.

## Official provider guides (start here)
| Resource | Why it is worth your time |
|---|---|
| [Anthropic documentation](https://docs.anthropic.com) | Vendor guidance on clear instructions, examples, XML tags, role prompting, long-context tips and structured output via tool use. |
| [OpenAI prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering) | Short official strategies: clear instructions, reference text, splitting complex tasks. |
| [Google AI for Developers](https://ai.google.dev) | Gemini's prompting and structured-output guides — a third vendor view to compare. |

## Learning prompting techniques
| Resource | Why it is worth your time |
|---|---|
| [Prompt Engineering Guide (site)](https://www.promptingguide.ai/) | Well-organised explanations of few-shot, chain-of-thought, ReAct and more, with examples. |
| [Prompt Engineering Guide (repo)](https://github.com/dair-ai/Prompt-Engineering-Guide) | The same guide plus papers, lectures and notebooks. |
| [Anthropic courses](https://github.com/anthropics/courses/tree/master) | Free interactive notebook tutorial with an exercise for each prompting technique. |
| [Prompt Engineering — Lilian Weng](https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/) | Research-grounded survey of why prompting methods work. Intermediate. |
| [The Prompt Report](https://trigaten.github.io/Prompt_Survey_Site/) | A systematic taxonomy of prompting techniques — a vocabulary reference. Advanced. |
| [Awesome Prompt Engineering](https://github.com/promptslab/Awesome-Prompt-Engineering) | Curated papers, tools and courses. |
| [awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts) | Many role-style prompts — use them as a critique exercise: what is weak about each? |

## Context engineering
| Resource | Why it is worth your time |
|---|---|
| [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) | Argues for owning your prompts and your context window explicitly — the core idea of context engineering. |
| [Letta (MemGPT)](https://github.com/letta-ai/letta) | Treats the context window like computer memory, with paging and summarising. Advanced design to study. |
| [Prompt Engineering for LLMs (O'Reilly book, paid)](https://learning.oreilly.com/library/view/prompt-engineering-for/9781098156145/) | Book-length treatment of assembling context, by GitHub Copilot engineers. |

## Structured output and guardrails
| Resource | Why it is worth your time |
|---|---|
| [Pydantic documentation](https://docs.pydantic.dev/) | The schema/validation library used in notebook 02. |
| [Instructor](https://python.useinstructor.com/) | Typed structured outputs with Pydantic validation and automatic retries — the notebook 02 loop, productised. |
| [Outlines](https://github.com/outlines-dev/outlines) | Constrained generation (regex, JSON schema) that guarantees format with local models. |
| [Guardrails](https://github.com/guardrails-ai/guardrails) | Validates and corrects model outputs against rules — a safety layer around prompts. |

## Security: prompt injection
| Resource | Why it is worth your time |
|---|---|
| [OWASP Top 10 for LLM Applications](https://genai.owasp.org/) | The security community's list of top LLM-app risks; prompt injection is at the top. (Official OWASP GenAI project site.) |

## Prompt versioning and testing
| Resource | Why it is worth your time |
|---|---|
| [Promptfoo](https://github.com/promptfoo/promptfoo) | Regression-tests prompts across models; catches changes that break behaviour. |
| [Langfuse (prompt management)](https://langfuse.com/) | Stores, versions and A/B-tests prompts linked to traces (module 14). |
| [Pezzo](https://github.com/pezzolabs/pezzo) | Open-source prompt management and versioning. |
| [PromptSource](https://github.com/bigscience-workshop/promptsource) | Shows how prompt templates are written and versioned at dataset scale. |

## Real AI-tool system prompts (case studies)
| Resource | Why it is worth your time |
|---|---|
| [x1xhlol/system-prompts-and-models-of-ai-tools](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools) | Collected (leaked/extracted, **unverified**) system prompts of Cursor, Devin, Lovable, Manus, Perplexity, v0 and more. Study for structure only; do not copy text. Our analysis: [system-prompt-analysis.md](system-prompt-analysis.md). |

## Models used in the notebooks
| Resource | Why it is worth your time |
|---|---|
| [HuggingFaceTB/SmolLM2-135M-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct) | The tiny offline model card — size, training data and limits. |
| [Anthropic models overview](https://docs.anthropic.com/en/docs/about-claude/models) / [OpenAI models](https://platform.openai.com/docs/models) | Current model names to put in `ANTHROPIC_MODEL` / `OPENAI_MODEL` (they change often). |
