from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click


ROOT_DIR = Path(__file__).resolve().parent.parent


SCRIPT_MAP = {
    "check-updates": "check_updates.py",
    "update-packages": "update_packages.py",
    "update-linux-patches": "update_linux_patches.py",
    "push-changes": "push_changes.py",
    "check-rt-changes": "check_rt_changes.py",
    "check-linux-patch-patches": "check_linux_patch_patches.py",
}


def run_script(script_name: str) -> int:
    script_path = ROOT_DIR / script_name
    if not script_path.exists():
        raise click.ClickException(f"Script not found: {script_path}")

    result = subprocess.run([sys.executable, str(script_path)], cwd=ROOT_DIR)
    return result.returncode


@click.group(help="Gentoo kernel source development helper commands.")
def main() -> None:
    """Top-level CLI group."""


@main.command("run", help="Run one of the consolidated maintenance workflows.")
@click.argument("workflow", type=click.Choice(sorted(SCRIPT_MAP.keys()), case_sensitive=False))
def run_workflow(workflow: str) -> None:
    script_name = SCRIPT_MAP[workflow]
    rc = run_script(script_name)
    if rc != 0:
        raise click.ClickException(f"Workflow '{workflow}' failed with exit code {rc}")


def _register_shortcut_commands() -> None:
    for workflow, script_name in SCRIPT_MAP.items():
        
        @main.command(workflow, help=f"Shortcut for: gkernel-dev run {workflow}")
        def _workflow_command(workflow_name: str = workflow, script: str = script_name) -> None:
            rc = run_script(script)
            if rc != 0:
                raise click.ClickException(
                    f"Workflow '{workflow_name}' failed with exit code {rc}"
                )


_register_shortcut_commands()


if __name__ == "__main__":
    main()
