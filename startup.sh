#!/bin/bash

# --- Environment variables ---
echo 'export OLLAMA_MODELS=/workspace/ollama_models' >> ~/.bashrc
echo 'export PATH="/workspace/bin:$PATH"' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH="/workspace/lib:$LD_LIBRARY_PATH"' >> ~/.bashrc

# Apply them immediately to this session
export OLLAMA_MODELS=/workspace/ollama_models
export PATH="/workspace/bin:$PATH"
export LD_LIBRARY_PATH="/workspace/lib:$LD_LIBRARY_PATH"

# --- Install Ollama ---
curl -fsSL https://ollama.com/install.sh | sh

# --- Start Ollama in tmux ---
tmux has-session -t ollama 2>/dev/null
if [ $? != 0 ]; then
  tmux new-session -d -s ollama 'OLLAMA_MODELS=/workspace/ollama_models ollama serve'
  echo "✅ Started Ollama in tmux session 'ollama'"
fi

# --- Start backend in tmux ---
tmux has-session -t backend 2>/dev/null
if [ $? != 0 ]; then
  tmux new-session -d -s backend 'cd /workspace/NoToxic && source venv/bin/activate && python backend/app.py'
  echo "✅ Started backend in tmux session 'backend'"
fi
