#!/usr/bin/env bash
# ollama_commands.sh - the terminal commands for Ollama, with a comment on each.
# Do NOT run this whole file blindly; copy one line at a time so you understand each step.

# 1. Install (pick your OS). macOS and Windows: download the app from https://ollama.com/download
#    Linux: the site shows a one-line install script; read it before running it.

# 2. Check that it is installed and the background server is running
ollama --version              # prints the installed version
curl http://localhost:11434   # should reply "Ollama is running"

# 3. Download a small model (browse names at https://ollama.com/library; names change over time)
ollama pull llama3.2:1b       # ~1 GB, runs on most laptops

# 4. Chat in the terminal (type /bye to quit)
ollama run llama3.2:1b

# 5. One-shot answer without entering chat mode
ollama run llama3.2:1b "Explain a context window in one sentence."

# 6. See what is downloaded / loaded in memory, and remove a model
ollama list
ollama ps
ollama rm llama3.2:1b

# 7. Call the REST API with curl (the server listens on port 11434)
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2:1b",
  "messages": [{"role": "user", "content": "Why is the sky blue?"}],
  "stream": false
}'
