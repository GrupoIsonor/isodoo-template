#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>
from invoke import task, Collection
from pathlib import Path
import shutil
import os


#-----------------
# CONTAINER TASKS
#-----------------

def _get_preferred_client_type():
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    raise RuntimeError("Need install podman or docker (with compose)")

DEFAULT_CLIENT = _get_preferred_client_type()

def _compose_raw(
    c, command: list[str], check: bool = False, stdin: str = None, pty: bool = True
) -> str:
    client_type = c.config.get('client_type', DEFAULT_CLIENT)
    final_cmd = f"{client_type} compose {command}"
    result = c.run(
        final_cmd,
        in_stream=stdin,
        pty=pty,
        warn=not check,
    )
    output = result.stdout
    clean_lines = [
        line
        for line in output.splitlines(keepends=True)
        if "The input device is not a TTY" not in line
    ]
    clean_output = "".join(clean_lines)
    return clean_output

def run_service(c, service: str, command: str):
    return _compose_raw(c, f"run --rm -it -l traefik.enable=false {service} {command}")

@task
def git_agreggate(c):
    run_service(c, "odoo", "isodoo_update_addons")

@task
def shell(c):
    run_service(c, "odoo", "odoo shell")

@task(positional=['action', 'modules'])
def module(c, action, modules):
    if action not in ["install", "upgrade"]:
        raise ValueError("Invalid action: install, upgrade")
    option = "-u" if action == "upgrade" else "-i"
    run_service(c, "odoo", f"odoo -d odoodb {option} {modules} --stop-after-init")

@task
def click_odoo_update(c, database="odoodb"):
    run_service(c, "odoo", f"click-odoo-update -d {database}")


#-----------------
# PROJECT TASKS
#-----------------

@task
def mode(c, mode):
    if mode not in ["prod", "demo", "ci", "dev"]:
        raise ValueError("Mode must be prod/demo/ci/dev")
    # Check no services running
    if os.path.exists("compose.yml") and _compose_raw(c, ["ps", "-q"]).strip():
        raise RuntimeError("Stop services first")
    project_root = Path(c.cwd)
    # Symlink
    target = project_root / "compose" / f"{mode}.yml"
    link = "compose.yml"
    if os.path.islink(link) or os.path.exists(link):
        os.unlink(link)
    os.symlink(target, link)
    # Create Mode Dirs
    if mode == "dev":
        git_dir = project_root / "addons" / "git"
        git_dir.mkdir(parents=True, exist_ok=True)


#-----------------
# MAIN
#-----------------

ns = Collection(git_agreggate, shell, module, click_odoo_update, mode)
ns.configure({"client_type": DEFAULT_CLIENT})
