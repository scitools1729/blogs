import pytest
from unittest.mock import patch, MagicMock
from omegaconf import OmegaConf
import sys

# Import the core logic directly
from core_llmesh.main import execute_mesh

@patch("core_llmesh.run_app")
def test_execute_mesh_cli_valid(mock_run_app):
    """Verifies CLI mode executes if a module_key is correctly provided."""
    cfg = OmegaConf.create({
        "meta": {
            "interface_mode": "cli",
            "module_key": "my_test_tool"
        }
    })
    
    execute_mesh(cfg)
    mock_run_app.assert_called_once_with(cfg, runner_key="my_test_tool")

@patch("core_llmesh.run_app")
def test_execute_mesh_cli_missing_key(mock_run_app, capsys):
    """Verifies CLI mode safely aborts if the module_key is missing."""
    cfg = OmegaConf.create({
        "meta": {
            "interface_mode": "cli"
        }
    })
    
    execute_mesh(cfg)
    mock_run_app.assert_not_called()
    
    # Assert the error was properly printed to stderr
    captured = capsys.readouterr()
    assert "CLI mode requires a specific tool" in captured.err

@patch("core_llmesh.serve.mcp_runner.start_server")
def test_execute_mesh_mcp_fallback(mock_start_server):
    """Verifies MCP mode successfully falls back to 'llmesh_server' if no key is provided."""
    cfg = OmegaConf.create({
        "meta": {
            "interface_mode": "mcp"
        }
    })
    
    execute_mesh(cfg)
    mock_start_server.assert_called_once_with(cfg, "llmesh_server")

@patch("core_llmesh.serve.api_runner.start_server")
def test_execute_mesh_rest_api_fallback(mock_start_server):
    """Verifies REST API mode successfully falls back to 'llmesh_server' if no key is provided."""
    cfg = OmegaConf.create({
        "meta": {
            "interface_mode": "rest_api"
        }
    })
    
    execute_mesh(cfg)
    mock_start_server.assert_called_once_with(cfg, "llmesh_server")
