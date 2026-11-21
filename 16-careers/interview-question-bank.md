# Interview question bank (137 questions with model answers)

Generated from `code/question_bank_data.py` by `build.py` - edit the Python file, not this one.
Levels: **junior** = expected of any entry-level candidate · **mid** = 1-3 years · **senior** = deeper design and judgement.

How to practise: cover the answer, say yours out loud (about one minute), then compare. Notebook `02-mock-interview-quiz.ipynb` and `code/quiz_runner.py` run quizzes from the same questions.

## Contents

- [Python](#python) (18)
- [Machine Learning](#machine-learning) (19)
- [Deep Learning](#deep-learning) (14)
- [LLMs](#llms) (20)
- [RAG](#rag) (14)
- [Agents](#agents) (12)
- [LLM System Design](#llm-system-design) (10)
- [LLMOps](#llmops) (10)
- [AI Trainer & Data](#ai-trainer--data) (8)
- [Behavioural](#behavioural) (12)

## Python

**1. What is the difference between a list and a tuple?** *(junior)*

> Both are ordered sequences. A list is mutable (you can add, remove or change items) and uses square brackets; a tuple is immutable and uses round brackets. Use tuples for fixed records (like coordinates) or as dictionary keys, because immutable objects can be hashed; use lists when the collection changes.

**2. What is a dictionary and how fast is a lookup?** *(junior)*

> A dictionary maps keys to values, like a phone book. It is implemented as a hash table, so looking up, adding or deleting a key takes constant time on average, regardless of size. Keys must be hashable (strings, numbers, tuples of immutables).

**3. What is a list comprehension? Give an example.** *(junior)*

> A compact way to build a list from another iterable in one expression: [x * x for x in nums if x > 0] squares only the positive numbers. It is usually clearer and a little faster than an equivalent for-loop with append. Dict and set comprehensions use the same idea with {}.

**4. What do *args and **kwargs mean?** *(junior)*

> *args collects any extra positional arguments into a tuple; **kwargs collects extra keyword arguments into a dictionary. They let a function accept a flexible number of inputs, and are common in wrappers and decorators that pass arguments through to another function.

**5. How do you handle errors in Python?** *(junior)*

> With try/except: put risky code in try, catch specific exceptions in except (for example except FileNotFoundError), optionally use else for code that runs only if no error happened and finally for cleanup that always runs. Catch the narrowest exception you can and never silently swallow errors with a bare except.

**6. What is a virtual environment and why use one?** *(junior)*

> A virtual environment is an isolated folder with its own Python interpreter and installed packages. Each project gets its own versions, so upgrading a library for one project does not break another. You create one with python -m venv .venv, activate it, and record dependencies in requirements.txt.

**7. What is the difference between == and is?** *(junior)*

> == checks whether two objects have equal values; is checks whether they are the very same object in memory. Use is only for singletons such as None (if x is None); use == for comparing values.

**8. Explain mutable default arguments and why they are a bug risk.** *(mid)*

> Default values are created once, when the function is defined, not each time it is called. So def add(item, bucket=[]) shares the same list across calls and keeps growing. The fix is a default of None and creating a new list inside the function.

**9. What is a generator and when would you use one?** *(mid)*

> A generator is a function that uses yield to produce values one at a time, pausing between them. It uses almost no memory because it never builds the whole sequence. Use it for streaming large files, reading datasets in batches, or streaming LLM tokens to a user.

**10. What is a decorator?** *(mid)*

> A decorator is a function that takes a function and returns a new function that adds behaviour around it, applied with the @name syntax. Common uses are logging, timing, caching (functools.lru_cache), retries and registering web routes as in FastAPI's @app.get.

**11. Explain the GIL and its effect on threads.** *(mid)*

> In the standard CPython interpreter the Global Interpreter Lock lets only one thread run Python bytecode at a time. Threads therefore help with I/O-bound work (waiting on network or disk) but not CPU-bound pure-Python work; for that use multiprocessing or libraries like NumPy and PyTorch that release the GIL in native code. Recent Python versions offer an optional free-threaded build, but most production code still assumes the GIL.

**12. What is the difference between threading, multiprocessing and asyncio?** *(mid)*

> Threading runs several threads in one process: good for I/O waits, limited by the GIL for CPU work. Multiprocessing runs separate processes with their own memory: true parallel CPU work, but higher overhead. Asyncio runs many tasks in one thread that voluntarily pause at await points: very efficient for thousands of concurrent network calls such as LLM requests.

**13. How would you read a 20 GB CSV file that does not fit in memory?** *(mid)*

> Process it in chunks rather than loading it all: pandas.read_csv with chunksize, a generator that reads line by line, or tools built for out-of-core data such as Polars lazy mode, DuckDB or Dask. Also read only the needed columns and use smaller data types.

**14. What are type hints and do they change how code runs?** *(mid)*

> Type hints annotate expected types, like def f(x: int) -> str. Python does not enforce them at run time, but tools such as mypy and editors use them to catch bugs, and libraries like pydantic and FastAPI read them to validate data. They make code easier to read and maintain.

**15. How do you write and run tests in Python?** *(mid)*

> Write functions starting with test_ that use assert, usually with pytest, and run python -m pytest. Keep tests small and independent, use fixtures for shared setup, and mock external services such as LLM APIs so tests are fast, free and repeatable. Run them automatically in CI on every push.

**16. Reverse a string and check if it is a palindrome.** *(junior)*

> s[::-1] reverses a string using slicing with step -1. A palindrome check that ignores case and spaces: clean = ''.join(c.lower() for c in s if c.isalnum()); return clean == clean[::-1]. Mention the time complexity is O(n).

**17. Find the two numbers in a list that add up to a target.** *(mid)*

> Use a dictionary of value to index while scanning once: for each number, check if target minus number is already in the dictionary; if yes, return both indices; otherwise store the number. This is O(n) time and O(n) memory, versus O(n squared) for checking every pair.

**18. What is Big-O notation? Give the complexity of common operations.** *(mid)*

> Big-O describes how running time or memory grows as input size n grows, ignoring constants. Examples: list index access O(1), searching an unsorted list O(n), dictionary lookup O(1) average, sorting O(n log n), nested loops over the same list O(n squared). Interviewers want you to state it for your solution and suggest improvements.


## Machine Learning

**19. What is the difference between supervised and unsupervised learning?** *(junior)*

> Supervised learning trains on examples with known answers (labels), for example emails marked spam or not, and learns to predict labels for new data. Unsupervised learning has no labels and finds structure on its own, for example clustering customers into groups. There is also self-supervised learning, where labels come from the data itself, which is how LLMs are pre-trained (predict the next token).

**20. Classification vs regression?** *(junior)*

> Classification predicts a category (spam / not spam, which digit); regression predicts a number (house price, delivery time). Different metrics follow: accuracy, precision, recall, F1 and ROC-AUC for classification; MAE, RMSE and R squared for regression.

**21. Why do we split data into train, validation and test sets?** *(junior)*

> The model learns from the training set; the validation set is used to choose settings (hyperparameters) and compare models; the test set is touched once at the end to estimate performance on truly unseen data. Evaluating on data the model trained on would give an over-optimistic score.

**22. What is overfitting and how do you prevent it?** *(junior)*

> Overfitting is when a model memorises the training data, including its noise, so it scores well in training but badly on new data. Signs: training score much higher than validation score. Remedies: more data, simpler models, regularisation (L1/L2, dropout), early stopping, cross-validation and data augmentation.

**23. Explain the bias-variance trade-off.** *(mid)*

> Bias is error from a model that is too simple to capture the pattern (underfitting); variance is error from a model so flexible that it changes a lot with small changes in training data (overfitting). Making a model more complex usually lowers bias but raises variance; the goal is the sweet spot with lowest total error on unseen data.

**24. Precision vs recall - explain with an example.** *(junior)*

> Precision: of everything the model flagged as positive, how much was really positive. Recall: of all real positives, how many the model found. For a cancer screening test, recall matters most (do not miss sick patients); for a spam filter, precision matters (do not hide real emails). F1 is their harmonic mean when you need a balance.

**25. What is a confusion matrix?** *(junior)*

> A table that counts predictions against true labels: true positives, false positives, true negatives and false negatives. Accuracy, precision, recall and F1 can all be computed from it, and it shows which kinds of mistakes the model makes.

**26. Why is accuracy misleading on imbalanced data, and what do you do?** *(mid)*

> If 99% of transactions are legitimate, a model that always says 'legitimate' is 99% accurate but useless for catching fraud. Use precision, recall, F1, PR-AUC or ROC-AUC, look at the confusion matrix, and consider class weights, resampling, or choosing a decision threshold based on business cost.

**27. What does ROC-AUC measure?** *(mid)*

> The ROC curve plots true positive rate against false positive rate at every decision threshold; AUC is the area under it. It is the probability that the model ranks a random positive example above a random negative one: 0.5 is random guessing, 1.0 is perfect. It is threshold-independent, but on very imbalanced data the precision-recall curve is often more informative.

**28. How does a decision tree work, and why use a random forest?** *(junior)*

> A decision tree asks a series of yes/no questions about features, choosing at each step the split that best separates the classes (for example by Gini impurity). Single trees overfit easily. A random forest trains many trees on random samples of rows and features and averages their votes, which reduces variance and usually generalises much better.

**29. What is gradient boosting and how is it different from a random forest?** *(mid)*

> Gradient boosting builds trees one after another, each new tree correcting the errors of the ones before; a random forest builds independent trees in parallel and averages them. Boosting (XGBoost, LightGBM, CatBoost) is often the strongest choice for tabular data but needs more careful tuning to avoid overfitting.

**30. What is cross-validation?** *(junior)*

> K-fold cross-validation splits the data into k parts, trains on k-1 parts and validates on the remaining one, repeating k times so every part is used for validation once. Averaging the scores gives a more reliable estimate than a single split, which matters most with small datasets.

**31. What is data leakage? Give an example.** *(mid)*

> Leakage is when information that would not be available at prediction time sneaks into training, producing unrealistically good scores. Examples: scaling using statistics of the full dataset before splitting, including a 'refund issued' column when predicting fraud, or random splits of time-series data so the model sees the future. Prevent it with pipelines fitted only on training data and time-aware splits.

**32. Why do we scale features, and which models need it?** *(junior)*

> Features on very different scales (age 0-100, income 0-1,000,000) can dominate distance calculations and slow gradient-based training. Distance- and gradient-based models such as k-NN, SVM, k-means, linear/logistic regression with regularisation and neural networks need scaling; tree-based models do not. Fit the scaler on training data only.

**33. Explain L1 vs L2 regularisation.** *(mid)*

> Both add a penalty on large weights to the loss to reduce overfitting. L2 (ridge) penalises squared weights and shrinks all weights smoothly; L1 (lasso) penalises absolute weights and can push some exactly to zero, acting as feature selection.

**34. How does k-means clustering work?** *(junior)*

> Choose k, place k centres, assign every point to its nearest centre, move each centre to the mean of its points, and repeat until assignments stop changing. It is fast and simple but you must pick k (elbow method, silhouette score), it assumes roughly round clusters, and it needs scaled features.

**35. How do you handle missing values?** *(mid)*

> First understand why they are missing. Options: drop rows or columns with many missing values, impute with mean/median/mode, use model-based imputation, add an 'is_missing' indicator, or use models that handle missing values natively (many gradient boosting libraries). Always fit imputation on training data only.

**36. Your model does well offline but badly in production. What could be wrong?** *(mid)*

> Common causes: training/serving skew (features computed differently in production), data drift (users or the world changed), leakage that inflated offline scores, a different class balance, bugs in the pipeline, or latency limits forcing a weaker model. Investigate by logging production inputs and predictions, comparing distributions with the training data, and building a monitoring dashboard.

**37. What is a scikit-learn Pipeline and why use it?** *(junior)*

> A Pipeline chains preprocessing steps and a model into one object, so fit and predict run every step in order. It prevents leakage (preprocessing is fitted only on training folds during cross-validation), keeps code short and makes the whole thing easy to save and deploy.


## Deep Learning

**38. What is a neural network, in simple terms?** *(junior)*

> Layers of simple units (neurons) that each compute a weighted sum of their inputs and pass it through an activation function. Stacking layers lets the network learn complex patterns. Training adjusts the weights so the network's predictions get closer to the correct answers.

**39. Why do we need activation functions?** *(junior)*

> Without a non-linear activation, any stack of layers collapses into one linear function and cannot learn curved patterns. ReLU (max(0, x)) is the default in hidden layers because it is cheap and trains well; sigmoid and softmax turn outputs into probabilities; GELU is common in transformers.

**40. What is backpropagation?** *(junior)*

> The algorithm that computes how much each weight contributed to the error. It applies the chain rule of calculus backwards from the loss through every layer to get the gradient for each weight; an optimiser such as SGD or Adam then nudges weights in the direction that reduces the loss.

**41. What is gradient descent and what does the learning rate do?** *(junior)*

> Gradient descent repeatedly moves the weights a small step downhill on the loss surface, in the direction of the negative gradient. The learning rate is the step size: too large and training diverges or bounces around; too small and it is very slow or gets stuck.

**42. SGD vs Adam?** *(mid)*

> SGD updates every weight with the same learning rate (often with momentum). Adam keeps running averages of each weight's gradients and their squares, giving every weight its own adaptive step size, so it usually converges faster with less tuning. AdamW, which handles weight decay correctly, is the standard for training transformers.

**43. What are epochs, batches and iterations?** *(junior)*

> An epoch is one full pass through the training data. A batch is the subset of examples used for one weight update; an iteration is one such update. With 10,000 examples and batch size 100, one epoch has 100 iterations.

**44. What is dropout and why does it help?** *(mid)*

> During training, dropout randomly switches off a fraction of neurons in each step, so the network cannot rely on any single neuron and learns more robust features. It is a regularisation technique that reduces overfitting; it is turned off at inference time (model.eval() in PyTorch).

**45. What are vanishing and exploding gradients?** *(mid)*

> In deep networks, gradients multiplied through many layers can shrink towards zero (early layers stop learning) or grow huge (training becomes unstable). Fixes include ReLU-family activations, careful weight initialisation, normalisation layers (BatchNorm, LayerNorm), residual connections and gradient clipping.

**46. How does a convolutional neural network (CNN) work?** *(junior)*

> A CNN slides small learned filters over an image to detect local patterns such as edges, then combines them in deeper layers into shapes and objects. Pooling reduces the spatial size. Sharing the same filter across the image needs far fewer weights than a fully connected network and gives some translation invariance.

**47. What is transfer learning?** *(mid)*

> Starting from a model already trained on a large dataset and adapting it to your task, instead of training from scratch. You can freeze most layers and train a new head, or fine-tune all or some layers with a small learning rate. It needs much less data and compute; it is how almost all practical vision and NLP work is done today.

**48. Batch normalisation vs layer normalisation?** *(mid)*

> Both rescale activations to keep training stable. BatchNorm normalises each feature across the examples in a batch, which works well for CNNs but depends on batch size. LayerNorm normalises across the features of each single example, independent of batch size, which is why transformers use it.

**49. Describe the PyTorch training loop.** *(junior)*

> For each batch: run the forward pass to get predictions, compute the loss, call optimizer.zero_grad() to clear old gradients, loss.backward() to compute new gradients, and optimizer.step() to update weights. Switch to model.eval() and torch.no_grad() for validation, and track training and validation loss each epoch.

**50. How do you know if your network is overfitting, and what do you try first?** *(mid)*

> Training loss keeps falling while validation loss starts rising. Try, roughly in order: more or augmented data, early stopping at the best validation epoch, dropout or weight decay, a smaller model, and checking for leakage between training and validation sets.

**51. Why are GPUs used for deep learning?** *(mid)*

> Neural network training is dominated by huge matrix multiplications, which can be split into thousands of independent small calculations. GPUs have thousands of simple cores and very high memory bandwidth, so they run these in parallel far faster than CPUs. GPU memory (VRAM) often limits the model and batch size you can use.


## LLMs

**52. How does a large language model generate text?** *(junior)*

> It predicts the next token given all previous tokens, picks one (by sampling from the predicted probabilities), appends it, and repeats. It was pre-trained on huge amounts of text to predict next tokens, then further tuned with instruction data and human feedback to follow instructions and be helpful and safe.

**53. What is a token, and why do tokens matter?** *(junior)*

> A token is a chunk of text the model works with, often a word piece; in English one token is roughly three to four characters. Context limits, speed and price are all measured in tokens, so long prompts cost more, run slower and may not fit in the context window. Other languages and code can use more tokens per word.

**54. What do temperature and top-p control?** *(junior)*

> Both control randomness when choosing the next token. Temperature rescales the probabilities: low (near 0) makes the model pick the most likely tokens, giving focused, repeatable answers; high makes output more varied. Top-p (nucleus sampling) only samples from the smallest set of tokens whose probabilities add up to p. Use low randomness for extraction and code, higher for brainstorming.

**55. What is a context window?** *(junior)*

> The maximum number of tokens the model can consider at once, covering the system prompt, conversation history, retrieved documents and its own output. Anything beyond it is cut off or must be summarised. Even within the window, models can pay less attention to information buried in the middle of very long contexts, so ordering and relevance matter.

**56. What is a hallucination and how do you reduce it?** *(junior)*

> A fluent but false or unsupported statement. Reduce it by grounding the model in retrieved sources (RAG) and asking it to cite them, allowing 'I don't know', lowering temperature, constraining output formats, verifying with tools or a second check, and evaluating faithfulness on a test set.

**57. Explain self-attention in simple terms.** *(mid)*

> For each token, the model asks which other tokens are relevant to understanding it. Each token produces a query, a key and a value vector; the query is compared with every key to get attention weights, and the token's new representation is the weighted sum of the values. Multi-head attention does this several times in parallel to capture different kinds of relationships.

**58. What are the main stages in training a chat model?** *(mid)*

> Pre-training on very large text corpora to predict the next token; supervised fine-tuning (SFT) on example instruction-response pairs written or checked by people; and preference tuning such as RLHF (reward model plus reinforcement learning) or DPO, using human or AI judgements of which answer is better. Safety training and evaluations run throughout.

**59. What is RLHF, and what is DPO?** *(mid)*

> RLHF (reinforcement learning from human feedback): people rank model answers, a reward model learns to predict those preferences, and the LLM is optimised (classically with PPO) to get high reward without drifting too far from the original model. DPO (direct preference optimisation) skips the separate reward model and RL loop and trains directly on chosen-versus-rejected answer pairs, which is simpler and more stable.

**60. When would you use prompting, RAG or fine-tuning?** *(junior)*

> Start with prompting: cheapest and fastest to change. Add RAG when the model needs knowledge it does not have, such as private or frequently changing documents, and when you want citations. Fine-tune when you need a consistent style, format or narrow skill that prompting cannot reliably produce, or to make a smaller cheaper model do a specific task well. They combine: a fine-tuned model can still use RAG.

**61. What is LoRA and why is it popular?** *(mid)*

> Low-Rank Adaptation freezes the original model weights and trains small extra matrices added to some layers, representing the weight change as the product of two thin matrices. It trains a tiny fraction of the parameters, needs far less GPU memory, and produces small adapter files you can swap per task. QLoRA does the same on a 4-bit quantised base model to save even more memory.

**62. What is quantisation?** *(mid)*

> Storing model weights with fewer bits, for example 8-bit or 4-bit integers instead of 16-bit floats. It cuts memory and often speeds up inference, letting bigger models run on smaller GPUs or laptops, at the cost of some quality loss that is usually small at 8-bit and noticeable but acceptable at 4-bit for many tasks.

**63. How do you get reliable structured output (JSON) from an LLM?** *(junior)*

> Describe the exact schema and give an example, use the provider's structured output, JSON mode or tool-calling features where available, keep temperature low, and always validate the result with a schema library such as pydantic. On failure, retry with the validation error message, then fall back to a safe default.

**64. How do you estimate the cost of an LLM feature?** *(junior)*

> Cost per call = input tokens times input price plus output tokens times output price (prices quoted per million tokens on the provider's pricing page). Multiply by calls per user and number of users. Then cut costs with shorter prompts, caching, smaller models for easy requests, limiting output length and batching where offered.

**65. How do you choose which model to use?** *(mid)*

> Define the task and build a small evaluation set first. Compare candidate models on quality for your task, latency, cost, context length, data privacy rules, availability of fine-tuning, and whether you need open weights to self-host. Often the answer is a mix: a small, cheap model for routine requests and a stronger one for hard cases.

**66. What is prompt injection, and how do you defend against it?** *(mid)*

> Text that tries to override the model's instructions, either typed by the user or hidden in documents and web pages the model reads (indirect injection). No single fix exists. Layer defences: treat retrieved content as data, not instructions; give tools least privilege; require human approval for risky actions; filter inputs and outputs; and test with red-team prompts.

**67. What is the KV cache?** *(mid)*

> During generation, the model stores the keys and values computed for previous tokens so it does not recompute them for every new token. It makes generation much faster but uses a lot of GPU memory that grows with context length and number of concurrent requests; serving systems such as vLLM manage it carefully with techniques like PagedAttention.

**68. What are embeddings?** *(junior)*

> Lists of numbers (vectors) that represent the meaning of text, so that similar meanings end up close together. You compare them with cosine similarity. They power semantic search, RAG retrieval, clustering, deduplication and recommendation.

**69. Why might an LLM give different answers to the same prompt?** *(mid)*

> Sampling randomness (temperature, top-p), small differences in the prompt or context, provider-side model updates behind the same name, and non-determinism in GPU computation and batching. For repeatability use low temperature, pin model versions where possible, log prompts and outputs, and evaluate on sets rather than single examples.

**70. How do you evaluate an LLM application?** *(mid)*

> Build a test set of realistic inputs from real usage and error analysis. Score outputs with code-based checks where possible (format, exact facts), LLM-as-judge with clear rubrics calibrated against human labels, and periodic human review. Track scores per release in CI and monitor production with user feedback and sampled reviews.

**71. What is speculative decoding?** *(senior)*

> A speed-up where a small fast draft model proposes several next tokens and the large model checks them all in one forward pass, accepting the ones it agrees with. Output quality is the same as the large model's, but generation is faster because the large model runs fewer sequential steps.


## RAG

**72. What is RAG and why use it?** *(junior)*

> Retrieval-augmented generation: before answering, search a knowledge base for relevant passages and put them in the prompt so the model answers from them. It gives the model private or up-to-date knowledge without retraining, reduces hallucination, and allows citations so users can check the source.

**73. Walk me through a RAG pipeline.** *(junior)*

> Offline: load documents, clean them, split into chunks, embed each chunk, and store vectors plus metadata in an index. Online: embed the user's question, retrieve the top-k similar chunks (optionally hybrid search and reranking), build a prompt with the chunks and instructions to cite them, generate the answer, and log everything for evaluation.

**74. How do you choose chunk size?** *(mid)*

> Chunks must be small enough to be specific and fit several into the prompt, but large enough to keep meaning. A few hundred tokens with some overlap is a common starting point; respect document structure (headings, paragraphs) where possible. Then tune empirically by measuring retrieval hit rate on an evaluation set.

**75. What is a vector database? Name some.** *(junior)*

> A store optimised for finding the vectors closest to a query vector, usually with approximate nearest-neighbour indexes, plus metadata filtering. Examples: FAISS (a library), Chroma, Qdrant, Weaviate, Milvus, Pinecone, and pgvector inside PostgreSQL. For small projects an in-memory FAISS index is often enough.

**76. What is hybrid search and why use it?** *(mid)*

> Combining keyword search (such as BM25) with vector search. Keywords catch exact terms such as product codes, names and error messages that embeddings can miss; vectors catch paraphrases. Results are merged, for example with reciprocal rank fusion, and usually beat either method alone.

**77. What is a reranker?** *(mid)*

> A model (often a cross-encoder) that reads the question and each candidate chunk together and scores relevance more accurately than embedding similarity. You retrieve a wider set, for example top 30, cheaply, then rerank to keep the best 3 to 5 for the prompt. It improves precision at the cost of some latency.

**78. How do you evaluate a RAG system?** *(mid)*

> Evaluate retrieval and generation separately. Retrieval: hit rate or recall at k and MRR on questions with known relevant chunks. Generation: faithfulness (is every claim supported by the retrieved text?), answer relevance, and correctness against reference answers, using LLM-as-judge plus human spot checks. Diagnose failures as retrieval misses versus generation mistakes.

**79. Users say the RAG bot gives wrong answers. How do you debug it?** *(mid)*

> Collect failing examples and look at traces. Check whether the right chunk was retrieved: if not, fix chunking, embeddings, add hybrid search, metadata filters or query rewriting. If it was retrieved but the answer is still wrong, fix the prompt, order of context, or model choice, and add a citation requirement. Turn the failures into a regression test set.

**80. What is cosine similarity?** *(mid)*

> A measure of how similar two vectors' directions are: the dot product divided by the product of their lengths. It ranges from -1 to 1, where 1 means pointing the same way. It ignores vector length, which makes it suitable for comparing embeddings; with normalised vectors it equals the dot product.

**81. How do you keep a RAG index up to date?** *(mid)*

> Build an ingestion pipeline that detects new, changed and deleted documents (timestamps or content hashes), re-chunks and re-embeds only those, and updates or removes their vectors. Store document IDs and versions in metadata. If you change the embedding model, re-embed everything, because vectors from different models are not comparable.

**82. How would you handle access control in RAG?** *(senior)*

> Store permissions (user, group, tenant) as metadata on every chunk and filter at retrieval time so users can only retrieve what they are allowed to see; never rely on the LLM to hide content after retrieving it. Mirror the source system's permissions, keep them synced, and audit-log which documents were used for each answer.

**83. What is query rewriting?** *(mid)*

> Using an LLM to turn the user's question into a better search query before retrieval: resolving pronouns from chat history ('what about its price?'), expanding abbreviations, splitting multi-part questions, or generating several variants. It improves recall, especially in conversational assistants.

**84. Long context windows are huge now. Do we still need RAG?** *(senior)*

> Often yes. Stuffing everything into the context costs more per call, is slower, may exceed the limit for large knowledge bases, and models can miss details in very long contexts. RAG also gives access control, freshness and citations. For a small, fixed document set, putting it all in context (with prompt caching) can be simpler, so measure both.

**85. What metadata would you store with each chunk?** *(junior)*

> Document ID and title, source URL or path, section heading, page number, created/updated date, author or owner, access permissions, language and chunk position. Metadata enables filtering (only this product, only recent docs), citations, permission checks and updates.


## Agents

**86. What is an AI agent?** *(junior)*

> A system where an LLM decides which actions to take in a loop: it reasons about the goal, calls tools (search, code, APIs), observes results, and continues until done. Unlike a fixed workflow, the model chooses the next step. The basic recipe is LLM plus tools plus a loop plus some memory.

**87. What is tool calling (function calling)?** *(junior)*

> You describe available tools to the model with a name, a description and a JSON schema for the arguments. Instead of plain text, the model can return a structured request to call a tool with arguments; your code runs the tool and sends the result back; the model then continues. The model never runs code itself, your application does.

**88. Explain the ReAct pattern.** *(junior)*

> Reason plus Act: the model alternates between thinking about what to do, taking an action with a tool, and reading the observation, repeating until it can answer. It makes multi-step tasks possible and leaves a readable trace of why each step was taken.

**89. When should you NOT use an agent?** *(mid)*

> When the steps are known in advance, a fixed workflow (chain or pipeline) is cheaper, faster, more predictable and easier to test. Agents add cost, latency and failure modes such as loops and wrong tool use. Use them when the path genuinely depends on intermediate results, and start with the simplest design that works.

**90. What is LangGraph?** *(mid)*

> A library for building agents and workflows as graphs: nodes are steps (LLM calls, tools, functions), edges decide what runs next, and a shared state object flows through. It supports cycles, branching, checkpoints to pause and resume, human-in-the-loop approval and persistence, giving more control than a free-running agent loop.

**91. What is the Model Context Protocol (MCP)?** *(mid)*

> An open protocol that standardises how AI applications connect to external tools and data. An MCP server exposes tools, resources and prompts; an MCP client inside an AI app discovers and calls them. It means a tool integration written once can be used by many different assistants and agents.

**92. How do you give an agent memory?** *(mid)*

> Short-term memory is the conversation and working state within the context window, trimmed or summarised as it grows. Long-term memory stores facts, preferences or past results outside the model, in a database or vector store, and retrieves relevant items when needed. Decide explicitly what is saved, for how long, and how users can see or delete it.

**93. How do you make agents safe and reliable?** *(mid)*

> Least-privilege tools, input validation on tool arguments, sandboxes for code execution, human approval for irreversible or costly actions, step and budget limits to stop loops, timeouts and retries, full tracing of every step, and evaluation on realistic task sets including adversarial cases.

**94. Single agent or multi-agent?** *(senior)*

> Start with one agent and good tools. Multi-agent designs (a planner with specialists, or a supervisor routing to workers) help when tasks split into distinct skills, need separate contexts, or can run in parallel, but they add coordination overhead, cost and new failure modes. Choose multi-agent only when evaluations show a clear gain.

**95. How do you evaluate an agent?** *(mid)*

> Define tasks with clear success criteria and measure task success rate, number of steps, cost, latency and safety violations. Also evaluate the trajectory: were the right tools called with sensible arguments? Use traces to find failure patterns, and keep a regression suite that runs before changes ship.

**96. What makes a good tool description for an LLM?** *(junior)*

> A clear, specific name; a description of what the tool does, when to use it and when not to; precise argument names, types and descriptions with examples; and helpful error messages returned to the model so it can recover. Fewer, well-designed tools beat many overlapping ones.

**97. An agent keeps looping and never finishes. How do you fix it?** *(senior)*

> Read the traces to find why: unclear goal, a tool returning unhelpful errors, missing information, or no explicit stopping condition. Fixes: a maximum step count and budget, clearer success criteria in the prompt, better tool errors, a planning step, state that records what was already tried, and escalation to a human when stuck.


## LLM System Design

**98. Design a customer-support chatbot over a company's help-centre articles.** *(mid)*

> Clarify requirements: languages, traffic, latency target, escalation to humans, privacy. Ingestion: crawl articles, chunk by heading, embed, store in a vector DB with metadata (product, updated date, URL). Serving: FastAPI service with guardrails, query rewriting from chat history, hybrid retrieval plus reranking, a prompt that must cite articles and say 'I don't know', and a handoff tool to create a ticket. Ops: tracing, cost and latency dashboards, feedback buttons, a weekly eval set from real conversations, and re-indexing when articles change.

**99. Design a system to summarise 10,000 long documents every night.** *(mid)*

> This is an offline batch job, so optimise cost and reliability over latency. Use a job queue and worker pool with rate limiting, provider batch APIs where available (usually cheaper), chunk long documents and use map-reduce summarisation (summarise sections, then summarise the summaries), cache results by document hash so unchanged files are skipped, retry failures with backoff, store outputs with the model version used, and sample outputs for quality review.

**100. How would you reduce the cost of an LLM app by 50%?** *(senior)*

> Measure first: cost per feature, per request and token breakdown. Then: route easy requests to a smaller model; shorten prompts and retrieved context; cap output length; cache identical or similar requests and use provider prompt caching for long fixed prefixes; batch offline jobs; remove agent loops that call the model repeatedly; and check that quality on the eval set stays acceptable after each change.

**101. How would you reduce latency for a chat assistant?** *(senior)*

> Stream tokens so the first words appear fast (time to first token); use a smaller or faster model where quality allows; shrink the prompt; run retrieval and other independent steps in parallel; cache frequent answers and embeddings; keep services close to the model provider's region; and set timeouts with fallbacks. Track p50 and p95, not averages.

**102. Design a document question-answering feature for PDFs users upload.** *(mid)*

> Upload to object storage, process asynchronously with a job queue: extract text (OCR for scanned pages, table handling), chunk, embed and index per user with access control. Show processing status. At question time retrieve only from that user's documents, answer with page citations, and handle 'not found in your documents'. Add file size limits, malware scanning, PII handling and deletion when the user removes a file.

**103. How do you serve an open-weight model for many users?** *(senior)*

> Use an inference server such as vLLM or TGI on GPUs, which provides continuous batching, efficient KV-cache memory and an OpenAI-compatible API. Choose model size and quantisation to fit GPU memory, run several replicas behind a load balancer with autoscaling on queue length, add a gateway for auth, rate limits and routing, and monitor GPU utilisation, tokens per second, latency and errors.

**104. How would you add guardrails to an LLM product?** *(mid)*

> Layer them. Input: schema validation, length limits, rate limiting, PII redaction, prompt-injection and abuse classifiers. Model: clear system prompt, least-privilege tools, retrieved content marked as untrusted data. Output: schema validation, policy and safety checks, PII redaction, citation checks. Plus logging of blocked events, human review queues, and regular red-team testing.

**105. How do you roll out a new prompt or model version safely?** *(senior)*

> Version prompts and configuration like code. Run the offline eval suite and compare with the current version; then shadow-test (run both, show users the old one) or A/B test with a small percentage of traffic, watching quality signals, latency, cost and errors. Keep an instant rollback path. Record which version produced each response in traces.

**106. What would you monitor for an LLM app in production?** *(mid)*

> Request rate, latency (p50/p95, time to first token), error rate by type (4xx, 429, 5xx, timeouts), token usage and cost per feature and user, guardrail block rate, refusal rate, user feedback, eval scores on sampled traffic, and drift in inputs (length, language, topic). Each metric needs a threshold, an alert and an owner.

**107. Design an AI coding assistant that answers questions about a large codebase.** *(senior)*

> Index the repository: parse files into functions and classes, embed code chunks and docstrings, and also build a symbol and call graph for precise lookups. At query time combine semantic search, keyword search for identifiers and graph navigation; give the model tools to open files and search, keeping it read-only by default. Respect repository permissions, re-index on each commit, and evaluate on real developer questions with known answers.


## LLMOps

**108. How would you deploy a Python model as an API?** *(junior)*

> Wrap it in a FastAPI app with typed request and response models, load the model once at start-up, add a health endpoint, write tests with TestClient, package it in a Docker image with pinned dependencies, and run it on a server or managed container service behind HTTPS, with secrets passed as environment variables.

**109. What is Docker and why is it useful?** *(junior)*

> Docker packages an application with its runtime, libraries and settings into an image that runs the same way on any machine with Docker. A running copy of an image is a container. It removes 'works on my machine' problems and is the standard unit for deploying services.

**110. What is CI/CD?** *(junior)*

> Continuous integration automatically builds and tests every change pushed to the repository; continuous delivery or deployment automatically packages and releases changes that pass. Tools include GitHub Actions and GitLab CI. For LLM apps, include a small evaluation step so prompt changes cannot silently reduce quality.

**111. How do you manage API keys and other secrets?** *(junior)*

> Never put them in code, notebooks, git, Docker images or front-end code. Use environment variables, a .env file locally (git-ignored, with a .env.example of placeholders), CI secret stores, and a secret manager in production. Use least privilege and spend limits, and if a key leaks, revoke it immediately and rotate.

**112. What is observability for LLM apps? Name a tool.** *(mid)*

> Recording enough detail about each request to understand behaviour later: a trace per request with spans for retrieval, model calls and tools, including prompts, outputs, tokens, cost, latency and user feedback. Tools include Langfuse, LangSmith, Arize Phoenix and W&B Weave.

**113. What is drift and how do you detect it?** *(mid)*

> Drift is when production inputs or outputs change compared with what the system was built and tested on, for example new topics, longer prompts, or a provider model update changing behaviour. Detect it by comparing recent distributions with a baseline (mean shifts, PSI), tracking refusal and answer-length rates, and re-running a fixed eval set regularly.

**114. Why use p95 latency instead of average latency?** *(mid)*

> Averages hide the slow tail. p95 tells you the time within which 95% of requests finish, which reflects what regular users actually experience on bad days; a few very slow requests can make the average look fine or terrible without describing anyone. Service-level objectives are usually written on percentiles.

**115. How do you handle LLM provider errors and rate limits?** *(mid)*

> Set timeouts on every call, retry only temporary errors (429, 5xx, timeouts) with exponential backoff and jitter and a maximum number of attempts, respect Retry-After headers, and fail over to a backup model or provider when one is down. Queue non-urgent work, and monitor error rates by type.

**116. What is vLLM and why is it fast?** *(mid)*

> An open-source inference server for open-weight LLMs. It is fast mainly because of continuous batching (finished requests leave the GPU batch and new ones join after every step, so the GPU never idles) and PagedAttention (KV cache stored in small blocks allocated on demand, wasting little memory so more requests fit). It exposes an OpenAI-compatible API.

**117. How do you A/B test two prompts in production?** *(senior)*

> Randomly assign users (not individual requests, to keep experiences consistent) to prompt A or B, log the version on every trace, and compare pre-chosen metrics: task success, user feedback, eval scores on sampled traffic, latency and cost. Run long enough for statistical confidence, watch guardrail metrics, and keep a rollback switch.


## AI Trainer & Data

**118. What does an AI trainer or data annotator do?** *(junior)*

> They create and judge data used to train and evaluate AI models: writing ideal answers, ranking or rating model responses against a rubric, checking facts, finding errors in code or reasoning, labelling text or images, and writing adversarial prompts to find weaknesses. Accuracy, consistency and clear written justification matter most.

**119. What is a rubric and how do you use it?** *(junior)*

> A rubric is a written set of criteria for judging a response, such as correctness, instruction-following, completeness, safety, and style, often with a scale and examples. You score each criterion separately against the guideline, not your personal taste, and write a short justification pointing to concrete evidence in the response.

**120. How would you compare two model responses to the same prompt?** *(junior)*

> Read the prompt carefully and note every requirement. Check each response for factual accuracy (verify claims), whether it follows all instructions, completeness, clarity, safety and formatting. Decide which is better and by how much, and justify with specific examples, for example 'Response B ignores the 100-word limit and contains an incorrect date'.

**121. What is inter-annotator agreement and why does it matter?** *(mid)*

> A measure of how often different annotators give the same label to the same item, beyond what chance would produce; Cohen's kappa is a common statistic for two annotators. Low agreement signals unclear guidelines or a genuinely ambiguous task, and noisy labels that will train or evaluate a model badly.

**122. How do you evaluate code written by an AI model?** *(junior)*

> Run it rather than trusting it: check it executes, passes the stated requirements and edge cases, and handles errors. Review correctness, efficiency, security issues (such as injection or hard-coded secrets), readability and whether it actually answers the prompt. Report concrete failing inputs when it is wrong.

**123. What is a preference pair?** *(junior)*

> Two responses to the same prompt where an annotator marks one as chosen (better) and the other as rejected. Large sets of such pairs train reward models for RLHF or are used directly by DPO to teach a model which answers people prefer.

**124. How do you spot a scam AI-training job offer?** *(junior)*

> Red flags: asking you to pay for training, equipment or 'registration'; payment only in gift cards or crypto; no verifiable company website or reviews; pressure to act immediately; requests for bank passwords; and messages from personal accounts. Real platforms have public sites, clear pay terms and identity checks done through official channels.

**125. What makes a good adversarial (red-team) prompt?** *(mid)*

> It targets a specific, realistic weakness, such as a factual trap, a conflicting instruction, a long multi-step requirement or a safety boundary, and has a clear expected behaviour so the failure can be judged objectively. Good red-teamers document the category, why the model failed and a minimal version of the prompt, while following the platform's safety rules.


## Behavioural

**126. Tell me about yourself.** *(junior)*

> Prepare a 60 to 90-second story: who you are now (your current role or studies and focus), two or three highlights that prove relevant skills (a project with a measurable result, a hackathon, an internship), and why this role and company are the logical next step. Keep it professional and tailored to the job description.

**127. Why do you want to work here?** *(junior)*

> Show you researched them: mention the product, a recent launch or blog post, their tech stack or mission, and connect it to your skills and goals. Avoid generic answers such as 'it's a big company'. Ending with how you would contribute is stronger than only what you will gain.

**128. Tell me about a project you are proud of.** *(junior)*

> Use STAR: Situation (the problem and context), Task (your responsibility), Action (what you did, with technical detail and decisions you made), Result (measurable outcome and what you learned). Be clear about your own contribution versus the team's, and be ready for deep follow-up questions about trade-offs.

**129. Describe a time you failed or made a mistake.** *(junior)*

> Choose a real but not catastrophic example. Explain briefly what happened, take ownership without blaming others, describe what you did to fix it, and focus on what you changed afterwards (for example, you now add tests or evaluations before shipping). Interviewers are checking honesty and learning.

**130. Tell me about a disagreement with a teammate.** *(mid)*

> Show you can disagree respectfully and resolve with evidence: describe the different views, how you listened and understood their reasons, how you proposed testing both options or used data to decide, and the outcome. Stress the working relationship stayed good, and that you can commit once a decision is made.

**131. How do you keep up with the fast pace of AI?** *(junior)*

> Give specific habits: which newsletters, papers, podcasts or communities you follow, and how you turn reading into practice, such as rebuilding a new technique in a small project, writing a short blog post, or trying new model releases on your own evaluation set. Mention filtering hype by testing claims yourself.

**132. Explain a technical concept to a non-technical person.** *(mid)*

> Pick a concept like RAG or embeddings and use an everyday analogy (RAG is an open-book exam: the model looks up the right pages before answering). Avoid jargon, check understanding, and connect it to why it matters for them, such as fewer wrong answers or lower cost. Interviewers test communication, not only knowledge.

**133. How do you prioritise when you have too much to do?** *(mid)*

> Clarify goals and deadlines with stakeholders, estimate effort and impact, do high-impact or blocking work first, break large tasks into small deliverables, and communicate early about what will slip and why. Give a concrete example where this worked.

**134. Where do you see yourself in a few years?** *(junior)*

> Show ambition aligned with the role: deepening skills in an area the company needs (for example production LLM systems), taking ownership of larger projects, and mentoring others. Avoid answers that suggest you will leave soon or that are unrelated to the job.

**135. Describe a time you had to learn something quickly.** *(mid)*

> Use STAR with a concrete example, such as learning a new framework for a hackathon or internship. Explain your learning method (official docs, small experiments, asking experts), how you delivered on time, and what you would do the same way again.

**136. Have you used AI tools to write code? How do you ensure quality?** *(mid)*

> Be honest: most engineers now use AI assistants. Explain that you review every line, understand it before committing, write or run tests, check for security issues and licence concerns, and use the tools mainly to speed up boilerplate and exploration while keeping design decisions yourself.

**137. Do you have any questions for us?** *(junior)*

> Always ask two or three thoughtful questions: what success looks like in the first 90 days, how the team evaluates and ships AI features, the biggest technical challenge right now, how mentoring and code review work, or what the interviewer enjoys about the job. Avoid asking only about salary and holidays in early rounds.


## Multiple-choice warm-up (33 questions)

**M1. (Python)** What does [x*2 for x in range(3)] produce?  
A) [0, 2, 4] · B) [2, 4, 6] · C) [0, 1, 2] · D) (0, 2, 4)  
*Answer: A - range(3) gives 0, 1, 2; each is doubled; square brackets make a list.*

**M2. (Python)** Which type can be used as a dictionary key?  
A) list · B) dict · C) tuple of strings · D) set  
*Answer: C - Keys must be hashable (immutable); a tuple of strings is.*

**M3. (Python)** Average time complexity of a dictionary lookup?  
A) O(n) · B) O(log n) · C) O(1) · D) O(n log n)  
*Answer: C - Dictionaries are hash tables: constant time on average.*

**M4. (Python)** What is printed by: def f(a=[]): a.append(1); return a; f(); print(f())  
A) [1] · B) [1, 1] · C) [] · D) Error  
*Answer: B - The default list is created once and shared between calls.*

**M5. (Python)** Which is best for thousands of concurrent network calls in one process?  
A) multiprocessing · B) asyncio · C) a for-loop · D) recursion  
*Answer: B - asyncio handles many I/O waits efficiently in a single thread.*

**M6. (Machine Learning)** A spam filter flags 10 emails; 8 are spam. What is its precision?  
A) 0.2 · B) 0.8 · C) 1.25 · D) Cannot tell  
*Answer: B - Precision = true positives / predicted positives = 8/10.*

**M7. (Machine Learning)** Training accuracy 99%, validation accuracy 70%. Most likely problem?  
A) Underfitting · B) Overfitting · C) Perfect model · D) Too little training  
*Answer: B - A large train-validation gap is the classic sign of overfitting.*

**M8. (Machine Learning)** Which model does NOT need feature scaling?  
A) k-NN · B) Logistic regression with L2 · C) Random forest · D) SVM  
*Answer: C - Tree splits compare values within one feature, so scale does not matter.*

**M9. (Machine Learning)** Fitting a scaler on the full dataset before splitting causes...  
A) Faster training · B) Data leakage · C) Underfitting · D) Nothing  
*Answer: B - Test-set statistics leak into training; fit preprocessing on training data only.*

**M10. (Machine Learning)** ROC-AUC of 0.5 means...  
A) Perfect · B) Random guessing · C) Always wrong · D) 50% accuracy exactly  
*Answer: B - AUC 0.5 = the model ranks positives above negatives no better than chance.*

**M11. (Deep Learning)** Which call clears old gradients in PyTorch?  
A) loss.backward() · B) optimizer.step() · C) optimizer.zero_grad() · D) model.eval()  
*Answer: C - Gradients accumulate by default, so they are zeroed before each backward pass.*

**M12. (Deep Learning)** Why use ReLU instead of no activation?  
A) Faster disk access · B) Adds non-linearity · C) Removes need for data · D) Reduces parameters  
*Answer: B - Without non-linearity, stacked layers collapse into one linear function.*

**M13. (Deep Learning)** Dropout is active during...  
A) Training only · B) Inference only · C) Both · D) Neither  
*Answer: A - It regularises training; model.eval() turns it off.*

**M14. (Deep Learning)** Validation loss rises while training loss falls. Best first action?  
A) Train longer · B) Early stopping / regularise · C) Raise learning rate · D) Remove validation set  
*Answer: B - This is overfitting; stop at the best validation epoch or regularise.*

**M15. (LLMs)** Roughly how many characters is one English token?  
A) 1 · B) 3-4 · C) 10 · D) 50  
*Answer: B - A common rule of thumb is about four characters per token.*

**M16. (LLMs)** For extracting fields into JSON, temperature should be...  
A) High · B) Low · C) Exactly 2 · D) Irrelevant  
*Answer: B - Low temperature gives focused, repeatable outputs.*

**M17. (LLMs)** Which adds private, changing knowledge without retraining?  
A) Fine-tuning · B) RAG · C) Quantisation · D) Higher temperature  
*Answer: B - RAG retrieves documents at question time.*

**M18. (LLMs)** LoRA trains...  
A) All weights · B) Small added low-rank matrices · C) Only the tokenizer · D) Only embeddings  
*Answer: B - The base model is frozen; small adapter matrices are trained.*

**M19. (LLMs)** DPO differs from classic RLHF because it...  
A) Needs no human data · B) Skips the separate reward model and RL loop · C) Only works on images · D) Uses higher temperature  
*Answer: B - DPO trains directly on chosen/rejected pairs.*

**M20. (RAG)** Hybrid search combines...  
A) Two LLMs · B) Keyword (BM25) and vector search · C) CPU and GPU · D) Train and test data  
*Answer: B - Keywords catch exact terms; vectors catch paraphrases.*

**M21. (RAG)** A reranker is typically a...  
A) Bi-encoder · B) Cross-encoder · C) Tokenizer · D) Vector database  
*Answer: B - Cross-encoders read query and passage together for more accurate scoring.*

**M22. (RAG)** Faithfulness measures whether...  
A) Retrieval was fast · B) Answer claims are supported by retrieved text · C) The user was happy · D) Chunks are small  
*Answer: B - Faithfulness = grounded in the provided context.*

**M23. (RAG)** After changing the embedding model you must...  
A) Do nothing · B) Re-embed all documents · C) Only re-embed new docs · D) Delete metadata  
*Answer: B - Vectors from different models are not comparable.*

**M24. (Agents)** In tool calling, who executes the tool?  
A) The LLM · B) Your application code · C) The user · D) The vector DB  
*Answer: B - The model only requests a call; your code runs it and returns the result.*

**M25. (Agents)** Steps are fixed and known in advance. Best design?  
A) Multi-agent system · B) Autonomous agent · C) Fixed workflow / chain · D) Fine-tuning  
*Answer: C - Workflows are cheaper, faster and more predictable when the path is known.*

**M26. (Agents)** MCP standardises...  
A) GPU drivers · B) How AI apps connect to tools and data · C) Model training · D) Tokenisation  
*Answer: B - MCP servers expose tools/resources that MCP clients can use.*

**M27. (LLMOps)** p95 latency of 3 s means...  
A) Average is 3 s · B) 95% of requests finish within 3 s · C) 5% finish within 3 s · D) Max is 3 s  
*Answer: B - Percentile definition.*

**M28. (LLMOps)** Which errors should be retried?  
A) 400 Bad Request · B) 422 Validation · C) 429 and 5xx · D) 401 Unauthorized  
*Answer: C - Only temporary failures are worth retrying.*

**M29. (LLMOps)** Where should a production API key live?  
A) In the Dockerfile · B) In the front-end · C) In a secret manager / env var · D) In a public notebook  
*Answer: C - Keep secrets out of code, images and browsers.*

**M30. (LLMOps)** vLLM's continuous batching mainly improves...  
A) Model accuracy · B) GPU utilisation / throughput · C) Tokenisation · D) Disk usage  
*Answer: B - Slots are refilled every step so the GPU stays busy.*

**M31. (AI Trainer & Data)** Cohen's kappa measures...  
A) Model accuracy · B) Agreement between two annotators beyond chance · C) Token count · D) Latency  
*Answer: B - It corrects raw agreement for chance.*

**M32. (AI Trainer & Data)** A 'job' asks you to pay a registration fee first. This is...  
A) Normal · B) A red flag · C) Required by law · D) A bonus  
*Answer: B - Legitimate platforms do not charge you to work.*

**M33. (Behavioural)** STAR stands for...  
A) Skills, Tools, Aims, Results · B) Situation, Task, Action, Result · C) Start, Try, Analyse, Repeat · D) Story, Theme, Arc, Resolution  
*Answer: B - The standard structure for behavioural answers.*

