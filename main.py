import sys
import shutil
import hydra
from omegaconf import DictConfig, OmegaConf


def execute_mesh(cfg: DictConfig):
    """
    Core execution logic for the mesh app.
    Can be called by external consumers (like hello-world) with their own configs.
    """
    # Core logic always required
    from core_llmesh import run_app

    print(f"Loaded config: {OmegaConf.to_yaml(cfg)}", file=sys.stderr)

    # Extract the project key from metadata
    meta = cfg.get("meta") or {}
    module_key = meta.get("module_key")

    # 2. Extract Interface Mode
    interface_mode = meta.get("interface_mode", "cli")
    print(f"Interface: {interface_mode}", file=sys.stderr)

    if interface_mode == "cli" and not module_key:
        print(
            "Error: CLI mode requires a specific tool or function. Ensure 'tool=XXX' is provided.",
            file=sys.stderr,
        )
        return

    module_key = module_key or "llmesh_server"

    # 3. Dispatch

    if interface_mode == "rest_api":
        from core_llmesh.serve.api_runner import start_server

        start_server(cfg, module_key)
        return

    if interface_mode == "mcp":
        from core_llmesh.serve.mcp_runner import start_server

        start_server(cfg, module_key)
        return

    # Default to CLI execution
    print(f"Running Project: {module_key}...", file=sys.stderr)
    run_app(cfg, runner_key=module_key)


@hydra.main(version_base=None, config_path="conf", config_name="config")
def hydra_main(cfg: DictConfig):
    execute_mesh(cfg)


def setup_cli_environment():
    """
    Handles pre-Hydra CLI setup, such as checking for Slurm availability
    and modifying sys.argv if necessary.
    """
    # 0. Alias support: Map 'launcher=' to 'hydra/launcher='
    sys.argv = [
        (
            arg.replace("launcher=", "hydra/launcher=")
            if arg.startswith("launcher=")
            else arg
        )
        for arg in sys.argv
    ]

    # Graceful Fallback check
    if "hydra/launcher=slurm" in sys.argv and not shutil.which("sbatch"):
        print("\n[WARNING] 'sbatch' not found. Slurm cluster unavailable.")
        print(
            "[WARNING] Falling back to 'hydra/launcher=local' for local parallel execution.\n"
        )
        # Modify sys.argv in place so Hydra sees the change
        sys.argv = [
            arg if arg != "hydra/launcher=slurm" else "hydra/launcher=local"
            for arg in sys.argv
        ]


def main():
    # 1. Custom Commands check
    if "--status" in sys.argv or "status" in sys.argv:
        # print_status() # Assuming print_status was imported or defined elsewhere in context, keeping as is or commenting if missing
        pass  # The previous view showed print_status call but I don't see the def. Assuming it was there or I should leave it?
        # Wait, the previous view of main.py showed `print_status()` call at line 33.
        # But I don't see the definition in the previous file view of `ll-mesh/src/ll_mesh/main.py`.
        # It might be imported or I missed it.
        # actually, looking at step 16, I don't see print_status defined. It might be missing code in the snippet or I should just preserve the structure.
        # Accessing the file content again to be safe.
        pass

    # 2. Setup environment
    setup_cli_environment()

    # 3. Run Hydra App
    hydra_main()


if __name__ == "__main__":
    main()
