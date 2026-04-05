## How to setup and run Gemma-4 locally
```bash
sudo apt update && sudo apt install python3-venv -y
python3 -m venv ~/ai_env
source ~/ai_env/bin/activate
pip install -U huggingface_hub
hf auth login
sudo chown -R $USER:$USER ~/.cache/huggingface
hf download unsloth/gemma-4-E4B-it-GGUF gemma-4-E4B-it-Q4_K_M.gguf --local-dir ~/.cache/huggingface/gemma4
docker run --gpus all \
  -p 8080:8080 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -e HF_TOKEN=$(cat ~/.cache/huggingface/token) \
  ghcr.io/ggml-org/llama.cpp:server-cuda \
  -hf ggml-org/gemma-4-E4B-it-GGUF \
  --port 8080 \
  --n-gpu-layers 99 \
  --ctx-size 32768 \
  --host 0.0.0.0

curl http://localhost:8080/v1/chat/completions -H "Content-Type: application/json" -d '{
  "model": "gemma-4",
  "messages": [
    {"role": "system", "content": "You are a precise research assistant."},
    {"role": "user", "content": "If I have three boxes, one with gold, one with silver, and one empty, and the labels are all wrong, how do I find the gold box by opening only one?"}
  ],
  "temperature": 0.0
}'
```

## Setup Opencode
```bash
curl -fsSL https://opencode.ai/install | bash
cat <<EOF > ~/.config/opencode/opencode.json
{
  "\$schema": "https://opencode.ai/config.json",
  "model": "local-gemma/gemma-4",
  "provider": {
    "local-gemma": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Local Gemma 4 Server",
      "options": {
        "baseURL": "http://localhost:8080/v1",
        "apiKey": "sk-no-key-required"
      },
      "models": {
        "gemma-4": {
          "name": "Gemma 4 (Reasoning Enabled)",
          "limit": {
            "context": 32768,
            "output": 4096
          }
        }
      }
    }
  },
  "autoupdate": false
}
EOF
```
