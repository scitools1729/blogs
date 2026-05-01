### What is Inspect SWE?
`inspect_swe` is an extension package for the [Inspect AI](https://inspect.aisi.org.uk/) framework. It integrates popular autonomous software engineering (SWE) agents and CLI tools directly into Inspect so they can be evaluated on standard benchmarks or used as solvers in Inspect tasks.

#### Supported Agents
The package currently provides wrappers for four major SWE agents:

- claude_code(): Anthropic's Claude Code (runs in unattended mode).
- codex_cli(): OpenAI's Codex CLI.
- gemini_cli(): Google's Gemini CLI.
- mini_swe_agent(): A lightweight version of SWE-agent.

### How It Works (The Architecture)
Inspect SWE agents are built using Inspect's `sandbox_agent_bridge()`. This is a crucial architectural feature because:

- Isolation: The SWE agent's binary (e.g., Claude Code) runs securely inside the Inspect sandbox container (like Docker).
- Proxying API Calls: The agent's LLM API calls are intercepted and proxied back out to the host-side Inspect framework.
- Model Agnostic: Because of this proxying, you can run an agent like Claude Code using any model that Inspect supports, not just Anthropic models.
- Observability: You retain all of Inspect's powerful features like exact token counting, time limits, and comprehensive log transcripts of the agent's internal thought process.

### Basic Usage Example
You can use these agents directly in your Python task definitions. Here is an example of using Claude Code to solve a task:
```bash
from inspect_ai import Task, task
from inspect_ai.dataset import json_dataset
from inspect_ai.scorer import model_graded_qa
from inspect_swe import claude_code

@task
def system_explorer() -> Task:
    return Task(
        dataset=json_dataset("dataset.json"),
        solver=claude_code(
            system_prompt="You are an ace system researcher.",
            disallowed_tools=["WebSearch"]
        ),
        scorer=model_graded_qa(),
        sandbox="docker",
    )
```
Since we will be running a local LLM model (e.g., gemma-4 on vLLM), our goal is to wire up Inspect SWE to route its agentic actions via our local model instead of a proprietary API.

Here is the absolute simplest use case to test this setup: having an agent write a simple Python script inside a secure Podman sandbox using your local model.

### 1. Create a simple task file (hello_eval.py)
Create a Python file with a basic `Task` that asks the agent to perform a file system operation. We'll use the `mini_swe_agent()` here as it's a great lightweight open-source agent harness.
```bash
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_swe import mini_swe_agent

@task
def write_hello_world() -> Task:
    return Task(
        dataset=[
            Sample(
                input="Create a python file named hello.py in the current directory that prints 'Hello from Gemma!'."
            )
        ],
        # You can use mini_swe_agent(), claude_code(), etc.
        solver=mini_swe_agent(),
        # A sandbox is required so the agent can safely execute code
        sandbox="docker",
    )
```

### 2. Ensure Podman is running
Because `inspect_swe` uses the `sandbox_agent_bridge()`, the agent needs an environment to execute commands. Make sure Podman is running.

### 3. Run the evaluation
First, set env variables:
```bash
export OPENAI_BASE_URL="http://<YOUR_URL>:<YOUR_PORT>/v1"
export OPENAI_API_KEY="dummy_key"
```

Second, run instpect eval
```bash
inspect eval hello_eval.py --model openai/gemma-4
```

### What happens when you run this?
1. Inspect will spin up a temporary Podman container.
2. It will inject the `mini_swe_agent` into that container.
3. The agent will read the prompt and start thinking about how to solve it.
4. Crucially, every time the agent tries to call an LLM to think or act, that API call is securely proxied out of the Podman container, back to the host, and routed to local gemma-4 model.
5. The agent will write the file, `Inspect` will evaluate if it succeeded, and the container will be destroyed.

------------------------------------

Supported Agents
The package currently provides wrappers for four major SWE agents:

claude_code(): Anthropic's Claude Code.
codex_cli(): OpenAI's Codex CLI.
gemini_cli(): Google's Gemini CLI.
mini_swe_agent(): A lightweight version of SWE-agent.

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
