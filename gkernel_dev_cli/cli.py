from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click


PACKAGE_DIR = Path(__file__).resolve().parent
WORKFLOWS_DIR = PACKAGE_DIR / "workflows"
RESOURCE_SCRIPTS_DIR = PACKAGE_DIR / "resources" / "scripts"


SCRIPT_MAP = {
    "check-updates": "check_updates.py",
    "update-packages": "update_packages.py",
    "update-linux-patches": "update_linux_patches.py",
    "push-changes": "push_changes.py",
    "check-rt-changes": "check_rt_changes.py",
    "check-linux-patch-patches": "check_linux_patch_patches.py",
}

RESOURCE_SCRIPT_MAP = {
    "vanilla-scraper": "vanilla_scraper.py",
    "gentoo-sources": "gentoo_sources.py",
}


def run_script(script_name: str, script_dir: Path = WORKFLOWS_DIR) -> int:
    script_path = script_dir / script_name
    if not script_path.exists():
        raise click.ClickException(f"Script not found: {script_path}")

    result = subprocess.run([sys.executable, str(script_path)], cwd=script_dir)
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


@main.command("resource", help="Run one of the resource maintenance scripts.")
@click.argument("script", type=click.Choice(sorted(RESOURCE_SCRIPT_MAP.keys()), case_sensitive=False))
def run_resource_script(script: str) -> None:
    script_name = RESOURCE_SCRIPT_MAP[script]
    rc = run_script(script_name, script_dir=RESOURCE_SCRIPTS_DIR)
    if rc != 0:
        raise click.ClickException(f"Resource script '{script}' failed with exit code {rc}")


def _register_resource_shortcut_commands() -> None:
    for resource_name, script_name in RESOURCE_SCRIPT_MAP.items():

        @main.command(resource_name, help=f"Shortcut for: gkernel-dev resource {resource_name}")
        def _resource_command(name: str = resource_name, script: str = script_name) -> None:
            rc = run_script(script, script_dir=RESOURCE_SCRIPTS_DIR)
            if rc != 0:
                raise click.ClickException(
                    f"Resource script '{name}' failed with exit code {rc}"
                )


_register_resource_shortcut_commands()


if __name__ == "__main__":
    main()
