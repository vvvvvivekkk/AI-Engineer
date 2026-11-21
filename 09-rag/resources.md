# Module 09 — Resources

Curated from the course's source catalogues plus official documentation of the libraries used. Links only; descriptions are ours. Features, prices and model rankings change quickly — check official pages (as of late 2026).

## Learn the ideas
| Resource | Why it is worth your time |
|---|---|
| [Pinecone Learning Center](https://www.pinecone.io/learn/) | Clear beginner explainers on embeddings, vector search and RAG basics (vendor-written, but neutral in tone). |
| [Vector databases — a 4-part series (The Data Quarry)](http://thedataquarry.com/posts/vector-db-1/) | A neutral comparison of how vector databases differ: indexing, storage, hybrid search. |
| [What AI Engineers Should Know About Search (Doug Turnbull)](https://softwaredoug.com/blog/2024/06/25/what-ai-engineers-need-to-know-search) | A search expert's reminder that retrieval quality (BM25, relevance tuning) matters as much as the LLM. |
| [Weaviate Academy](https://academy.weaviate.io/) | Free short courses on vector search concepts and hybrid retrieval. |
| [LangChain for LLM Application Development (DeepLearning.AI)](https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/) | A short guided course building document Q&A step by step. |

## Go deeper: techniques and reference code
| Resource | Why it is worth your time |
|---|---|
| [RAG Techniques (Nir Diamant)](https://github.com/NirDiamant/RAG_Techniques) | Dozens of notebook implementations (chunking, reranking, HyDE, fusion, graph RAG) to compare side by side. |
| [Awesome RAG](https://github.com/frutik/Awesome-RAG) | Further index of RAG papers and tools. |
| [Delveta](https://github.com/Eric-LLMs/Delveta) | A configurable production-style pipeline (query rewrite → hybrid recall → RRF → rerank → relevance check) with a golden-set evaluation. Advanced. |
| [LLMs-Lab](https://github.com/Eric-LLMs/LLMs-Lab) | Standalone modules on RAG optimisation, function calling and agents. |
| [awesome-sentence-embedding](https://github.com/Separius/awesome-sentence-embedding) | Background on the embedding models that drive retrieval quality. |

## Libraries used in this module (official docs)
| Resource | Why it is worth your time |
|---|---|
| [Sentence Transformers](https://www.sbert.net/) | Docs for the embedding (bi-encoder) and cross-encoder models we use, plus pretrained model lists. |
| [all-MiniLM-L6-v2 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) | Our embedding model: what it was trained on, its 384-dimension output and limits. |
| [ms-marco-MiniLM-L-6-v2 model card](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2) | Our reranker. |
| [FAISS](https://github.com/facebookresearch/faiss) | The vector-search library; its wiki explains flat, IVF and HNSW indexes. |
| [rank_bm25](https://github.com/dorianbrown/rank_bm25) | The small BM25 library used in notebook 02. |

## Vector databases (official pages)
| Resource | Why it is worth your time |
|---|---|
| [Chroma](https://github.com/chroma-core/chroma) | Embedded, pip-installable vector store — the easiest first "real" database. |
| [Qdrant](https://github.com/qdrant/qdrant) | Production-grade open-source vector DB with filtering and hybrid search; runs in Docker. |
| [pgvector](https://github.com/pgvector/pgvector) | Vector columns and similarity search inside PostgreSQL. |
| [Pinecone](https://www.pinecone.io/) | Fully managed cloud vector database (paid tiers). |
| [Milvus](https://github.com/milvus-io/milvus) | Scale-out vector database — shows what changes at billions of vectors. |
| [txtai](https://github.com/neuml/txtai) | All-in-one local embeddings database plus pipelines. |

## Frameworks and apps
| Resource | Why it is worth your time |
|---|---|
| [LlamaIndex](https://www.llamaindex.ai/) | Data framework for ingesting, indexing and querying documents; RAG-first design. |
| [LangChain](https://www.langchain.com/) | Widely used framework with document loaders, text splitters and retriever integrations. |
| [Ollama](https://ollama.com) | Serves embedding and chat models locally, so a full RAG stack can run offline with a capable generator. |
| [PrivateGPT](https://github.com/imartinez/privateGPT) / [LocalGPT](https://github.com/PromtEngineer/localGPT) | Readable reference apps for fully private "chat with your documents". |
| [AnythingLLM](https://github.com/Mintplex-Labs/anything-llm) | No-code desktop RAG app — useful to show non-coders what RAG does. |

## Evaluation and debugging
| Resource | Why it is worth your time |
|---|---|
| [DeepEval](https://github.com/confident-ai/deepeval) | Pytest-style RAG metrics (faithfulness, answer relevancy) to measure the effect of changes. |
| [Arize Phoenix](https://github.com/Arize-ai/phoenix) | Traces retrieval steps and visualises embeddings to debug bad answers. |
