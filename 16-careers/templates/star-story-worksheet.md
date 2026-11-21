# STAR story worksheet

Prepare 6-8 stories. Each can answer several behavioural questions. Write bullet notes, not a script, and practise saying each in about 2 minutes.

| # | Theme | Situation (context, 1-2 lines) | Task (your responsibility) | Action (what YOU did - most detail here) | Result (numbers + lesson) | Questions it answers |
|---|---|---|---|---|---|---|
| 1 | Project I'm proud of | | | | | Tell me about a project; technical deep-dive |
| 2 | A failure or mistake | | | | | Tell me about a failure; a time you were wrong |
| 3 | Disagreement / conflict | | | | | Conflict with a teammate; handling feedback |
| 4 | Learning fast | | | | | Learning something new quickly; ambiguity |
| 5 | Tight deadline | | | | | Pressure; prioritisation |
| 6 | Helping others / leadership | | | | | Leadership; mentoring; teamwork |
| 7 | Using data to decide | | | | | Data-driven decision; measuring impact |
| 8 | Going beyond the brief | | | | | Initiative; ownership |

## Example (filled in)

- **Situation:** In a college hackathon our RAG chatbot answered about a third of test questions wrongly two hours before the demo.
- **Task:** I owned retrieval and had to fix accuracy without rewriting the app.
- **Action:** I wrote 30 test questions with the correct source pages, measured hit rate (0.63), found that chunks split tables in half, switched to heading-based chunking with overlap and added BM25 hybrid search, re-running the test after each change.
- **Result:** Hit rate rose to 0.87 and we placed 4th of 60 teams. Lesson: build a small eval set *first*; I now start every RAG project that way.
