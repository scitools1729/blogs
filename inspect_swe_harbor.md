```bash
#!/bin/bash

# 1. Load podman if your HPC uses a module system (uncomment if needed)
# module load podman

# 2. Create and activate a fresh virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install the required dependencies
pip install inspect-ai inspect-swe inspect-harbor

# 4. Configure Inspect to use your local OpenAI-compatible server
# Replace these with your actual endpoint and a dummy key if your server doesn't require one
export OPENAI_BASE_URL="http://YOUR_LOCAL_IP:8000/v1"
export OPENAI_API_KEY="dummy-key-required-by-client"

# 5. Generate the Python smoke test file
cat << 'EOF' > smoke_test.py
from inspect_ai import task, Task
from inspect_harbor import hello_world
from inspect_swe import mini_swe_agent

@task
def podman_smoke_test():
    base_task = hello_world()
    
    # Extract the Harbor sandbox config (usually a tuple like ("docker", "/path/to/compose.yaml"))
    original_sandbox = base_task.sandbox
    
    # Safely swap "docker" for "podman" while keeping the compose.yaml path
    if isinstance(original_sandbox, tuple) and original_sandbox[0] == "docker":
        sandbox = ("podman", original_sandbox[1])
    elif original_sandbox == "docker":
        sandbox = "podman"
    else:
        sandbox = "podman"

    return Task(
        dataset=base_task.dataset,
        scorer=base_task.scorer,
        solver=mini_swe_agent(),
        sandbox=sandbox
    )
EOF

# 6. Execute the evaluation
# Be sure to keep the 'openai/' prefix so Inspect knows which API client to use, 
# followed by the exact name of the model you are hosting.
inspect eval smoke_test.py --model openai/your-exact-model-name

# 7. (Optional) View the results
# inspect view

```
