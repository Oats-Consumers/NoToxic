# RunPod Pod Restoration Guide

This document explains how to fully restore your development environment on RunPod after a pod reset.

---

## 0. Initial Pod Setup

* **SSH Key**: Set your `PUBLIC_KEY` in the RunPod pod environment variables.
* **Expose Ports**: Ensure port **5000** is added to "Expose HTTP Ports" in your pod config.

---

## 1. Clone the Repository

```bash
cd /workspace
git clone --recurse-submodules https://github.com/Oats-Consumers/NoToxic.git
cd NoToxic
git checkout docker-pod-deployment
apt update && apt install -y git-lfs
git lfs install
git lfs pull
```

---

## 2. Install Tmux and Make It Persistent

```bash
apt update && apt install -y tmux
mkdir -p /workspace/bin /workspace/lib
cp $(which tmux) /workspace/bin/
chmod +x /workspace/bin/tmux
ldd $(which tmux) | grep "=> /" | awk '{print $3}' | xargs -I '{}' cp -v '{}' /workspace/lib/
```

---

## 3. Restore Python Environment

```bash
cd /workspace/NoToxic
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 4. Restore Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
mkdir -p /workspace/ollama_models
export OLLAMA_MODELS=/workspace/ollama_models
nohup ollama serve > /workspace/ollama_server.log 2>&1 &
echo "Waiting for Ollama to become available..."
until curl -s http://localhost:11434 > /dev/null; do
    sleep 1
done
ollama pull gemma3:27b
```

---

## 5. Restore Secrets

* Manually copy your `my_secrets.py` file to:

```
/workspace/NoToxic/my_secrets.py
```
