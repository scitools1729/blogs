Here is the complete list of change points required to refactor the module name from mod-inspect-eval to mod-inspectAI-eval across the entire workspace. 

1. File and Directory Name Changes
- Module Root Directory: Rename mod-inspect-eval/ to mod-inspectAI-eval/
- Internal Python Package: Rename mod-inspectAI-eval/src/mod_inspect_eval/ to mod-inspectAI-eval/src/mod_inspectAI_eval/
2. Workspace Config Updates
- Root pyproject.toml: Change "mod-inspect-eval" to "mod-inspectAI-eval" in the members array under [tool.uv.workspace].
- uv.lock: Will need to be regenerated via uv sync after the rename to reflect the new workspace member path.
3. Module File Content Updates
- mod-inspectAI-eval/pyproject.toml:
  - Change name = "mod-inspect-eval" to name = "mod-inspectAI-eval".
- mod-inspectAI-eval/README.md:
  - Update the # mod-inspect-eval header.
  - Update the two uv run llmesh run-module mod-inspect-eval ... healthcheck commands to use mod-inspectAI-eval.
- mod-inspectAI-eval/src/mod_inspectAI_eval/main.py:
  - Change the inline module import from import mod_inspect_eval to import mod_inspectAI_eval.
4. Documentation & Artifacts Constraints
- Clean up any .egg-info cache directories left over from the old build (e.g., src/mod_inspect_eval.egg-info).
-  Update task.md and implementation_plan.md in our conversation artifacts to reflect the new name tracking.

This captures all the plumbing! Let me know when you'd like me to execute this refactor, or if there is anything else you'd like to adjust with the casing beforehand (e.g., mod-inspectai-eval vs mod-inspectAI-eval).
