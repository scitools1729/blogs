import os
import subprocess
from dataclasses import dataclass
from core_llmesh import Primitive
from rich.console import Console
from collections.abc import Mapping, Iterable

@dataclass
class InspectScriptRunner(Primitive):
    """
    Generic Primitive for executing custom InspectAI evaluation scripts.
    Typically used for local research scripts like 'vrs_baseline.py'.
    """
    name: str = "inspect_script_runner"

    def __init__(self):
        super().__init__(self.name)

    def run(self, **kwargs):
        console = Console()
        
        # 1. Parameter Extraction
        tasks = kwargs.get("tasks", [])
        if isinstance(tasks, str):
            tasks = [tasks]
            
        target_id = kwargs.get("target_id")
        api_base_url = kwargs.get("api_base_url")
        api_key = kwargs.get("api_key")
        limit = kwargs.get("limit")
        max_connections = kwargs.get("max_connections")
        task_args = kwargs.get("task_args", {})
        
        if not tasks:
            return {"status": "error", "message": "'tasks' parameter is required."}
        if not target_id:
             return {"status": "error", "message": "'target_id' parameter is required."}

        # Resolve paths via Hydra
        try:
            from hydra.core.hydra_config import HydraConfig
            output_dir = HydraConfig.get().runtime.output_dir

            # --- LLMESH PATH RESOLUTION FIX ---
            # Infer the user's terminal invocation directory purely from the hydra output path
            # Core-llmesh injects: {original_cwd}/.llmesh_runs/{module_name}/outputs/...
            normalized_out = output_dir.replace("\\", "/")
            if "/.llmesh_runs" in normalized_out:
                invoke_dir = os.path.normpath(normalized_out.split("/.llmesh_runs")[0])
            else:
                invoke_dir = os.getcwd()
            # --- END FIX ---

        except Exception:
            output_dir = os.getcwd()
            invoke_dir = os.getcwd() # Added for fallback

        try:
            from hydra.utils import get_original_cwd
            original_cwd = get_original_cwd()
        except Exception:
            original_cwd = os.getcwd()

        # --- LLMESH PATH RESOLUTION FIX ---
        # Normalize the paths to fix the absolute path bug and support terminal paths
        resolved_tasks = []
        for t in tasks:
            # Get the absolute path from the perspective of the terminal that invoked the command
            abs_task = os.path.abspath(os.path.join(invoke_dir, t))
            
            # Convert it back to a relative path from the perspective of the module (`original_cwd`)
            # This fixes `NotImplementedError: Non-relative patterns are unsupported` in inspect_ai
            rel_task = os.path.relpath(abs_task, original_cwd)
            
            # Ensure cross-compatibility if on Windows
            rel_task = rel_task.replace("\\", "/") 
            resolved_tasks.append(rel_task)
        # --- END FIX ---

        # 2. Command Construction
        cmd = ["inspect", "eval"]
        cmd.extend(resolved_tasks) # <-- Changed from tasks to resolved_tasks
        cmd.extend(["--model", target_id])
        cmd.extend(["--log-dir", output_dir])
        cmd.extend(["--display", "rich"])
        
        if limit is not None:
             cmd.extend(["--limit", str(limit)])
        if max_connections is not None:
             cmd.extend(["--max-connections", str(max_connections)])
             
        # Robust task_args handling (fixes the bracket/list issue)
        if task_args and isinstance(task_args, Mapping):
            for k, v in task_args.items():
                val = ",".join(map(str, v)) if isinstance(v, Iterable) and not isinstance(v, str) else str(v)
                cmd.append("-T")
                cmd.append(f"{k}={val}")
             
        # 3. Environment Variable Injection
        env = os.environ.copy()
        if target_id.startswith("openai/"):
             if api_base_url: env["OPENAI_BASE_URL"] = api_base_url
             if api_key: env["OPENAI_API_KEY"] = api_key
        elif target_id.startswith("vllm/") or target_id.startswith("hf/"):
             if api_key: env["HF_TOKEN"] = api_key

        # Execution Logging
        console.log(f"[{self.name}] Executing Script: {' '.join(cmd)}")

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

    def get_tool_definition(self):
        return {
            "name": self.name,
            "description": "Executes custom InspectAI Python evaluation scripts located in the local workspace. Use this tool when you need to run specific file-based evaluations, such as custom red-teaming scripts or local baseline tasks (e.g., 'tasks/vrs_baseline.py'). Provides full environment isolation and API key injection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": ["string", "array"],
                        "description": "The relative or absolute path(s) to the Python script(s) containing the Inspect @task or @solver definitions."
                    },
                    "target_id": {
                        "type": "string",
                        "description": "The target model identifier (e.g., 'openai/gpt-4o', 'anthropic/claude-3-opus-20240229', 'mockllm/model')."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Optional limit on the number of samples to process. Use small numbers (e.g., 1 or 5) for healthchecks and debugging."
                    },
                    "task_args": {
                        "type": "object",
                        "description": "Optional dictionary of runtime arguments that will be mapped to the script's task parameters."
                    }
                },
                "required": ["tasks", "target_id"]
            }
        }
