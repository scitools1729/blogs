```bash
# contents of .env
HF_HUB_OFFLINE=0
HF_DATASETS_OFFLINE=0
HF_HOME=./.cache/huggingface
OPENAI_BASE_URL=http://localhost:8080/v1
OPENAI_API_KEY=DUMMY

# packages added
uv add inspect-ai
uv add inspect-evals
uv add openai
```

```bash
uv run inspect eval inspect_evals/mmlu_0_shot --model openai/gemma-4-E4B-it-GGUF --limit 10 -T max_non_cot_tokens=2048 --display conversation
```

```bash
uv run inspect eval inspect_evals/arc_easy --model openai/gemma-4-E4B-it-GGUF --limit 3 --display conversation
```

```bash
uv run inspect eval inspect_evals/cyse2_interpreter_abuse \
  --model openai/gemma-4-E4B-it-GGUF \
  --model-role grader='{"model": "openai/gemma-4-E4B-it-GGUF", "base_url": "http://localhost:8080/v1"}' \
  --limit 3 \
  --display conversation
```
```bash
uv run inspect eval inspect_evals/cyse2_prompt_injection \
  --model openai/gemma-4-E4B-it-GGUF \
  --model-role grader='{"model": "openai/gemma-4-E4B-it-GGUF", "base_url": "http://localhost:8080/v1"}' \
  --limit 3 \
  --display conversation
```
