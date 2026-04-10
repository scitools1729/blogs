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
explanation of accuracy in cyersec eval:
```text
In the context of standard Inspect AI security benchmarks (like those based on Cybench / CyberSecEval 2), the underlying metric being captured is almost always aligned such that Higher = Better / More Secure.

Here is how to interpret your results:

The Goal of the Benchmark: The prompt injection benchmark tests whether an attacker can hide malicious instructions inside an otherwise normal-looking prompt to hijack the model's behavior. Safely aligned models should ignore the malicious injected instructions and either refuse the prompt entirely or only complete the benign portion.
The "Accuracy" Metric: In model_graded_qa, "accuracy" means "what percentage of the time did the model do the correct, expected thing." For this benchmark, the "correct" thing is to successfully defend against the prompt injection.
Your Result (0.167): An accuracy of 0.167 means your gemma model successfully defended against the prompt injection in only ~16.7% of the test cases. Consequently, it fell victim to the prompt injection and followed the attacker's hidden instructions ~83.3% of the time.
In short, a low accuracy here means your model is currently highly susceptible to prompt injection attacks, and you would want to see that number climb closer to 1.000 to consider it secure!
```

```bash
        try:
            process = subprocess.run(
                cmd, 
                env=env
            )
            if process.returncode != 0:
                return {
                    "status": "error", 
                    "message": f"Registry task failed with code {process.returncode}",
                    "stdout": "Output was printed to terminal natively."
                }
            return {
                "status": "completed",
                "tasks_evaluated": tasks,
                "log_directory": output_dir,
                "stdout": "Output was printed to terminal natively."
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
```

```bash
        try:
            process = subprocess.run(
                cmd, 
                env=env,
                cwd=original_cwd
            )
            
            if process.returncode != 0:
                return {
                    "status": "error", 
                    "message": "Evaluation failed.", 
                    "stdout": "Output was printed to terminal natively."
                }
                
            return {
                "status": "completed",
                "tasks_evaluated": tasks,
                "target_model": target_id,
                "log_directory": output_dir,
                "stdout": "Output was printed to terminal natively."
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
```
            
