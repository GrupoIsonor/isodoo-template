#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>
from invoke import task, Collection
from pathlib import Path
import shutil
import os


#-----------------
# HELPERS
#-----------------

def _get_preferred_client_type():
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    raise RuntimeError("podman or docker (with compose plugin) is required")


DEFAULT_CLIENT = _get_preferred_client_type()
DEFAULT_COMPOSE_ENV = "dev"


def _run_container_cmd(
    c,
    command: str,
    check: bool = False,
    stdin: str = None,
    pty: bool = True,
    compose: bool = False,
) -> str:
    """Execute a command using docker or podman."""
    client_type = c.config.get("client_type", DEFAULT_CLIENT)
    compose_env = c.config.get("compose_env", DEFAULT_COMPOSE_ENV)
    if compose_env not in ("dev", "ci"):
        raise RuntimeError("Invalid compose env. Valid are: dev or ci")
    final_cmd = f"{client_type} compose -f compose/{compose_env}.yml {command}" if compose else f"{client_type} {command}"
    result = c.run(
        final_cmd,
        in_stream=stdin,
        pty=pty,
        warn=not check,
        hide=False,
    )
    # Clean unwanted podman/docker warnings
    clean_lines = [
        line
        for line in result.stdout.splitlines(keepends=True)
        if "The input device is not a TTY" not in line
    ]
    return "".join(clean_lines)


def _run_compose_service(c, service: str, command: str, extra_opts: str = ""):
    """Run a one-off command inside a compose service."""
    cmd = f"run --rm -it -l traefik.enable=false {extra_opts} {service} {command}"
    return _run_container_cmd(c, cmd, compose=True)


#-----------------
# CONTAINER TASKS
#-----------------

@task(help={
    "database": "Database name (default: odoodb)"
})
def git_aggregate(c, database: str = "odoodb"):
    """Update git-tracked addons (moouro, etc.) inside the Odoo container."""
    _run_compose_service(c, "odoo", f"isodoo_update_addons -d {database}")


@task
def shell(c):
    """Open an Odoo shell inside the running container."""
    _run_compose_service(c, "odoo", "odoo shell")


@task(positional=["action", "modules"], help={
    "action": "install or upgrade",
    "modules": "Comma-separated list of modules"
})
def module(c, action: str, modules: str):
    """Install or upgrade Odoo modules."""
    if action not in ["install", "upgrade"]:
        raise ValueError("Action must be 'install' or 'upgrade'")
    option = "-u" if action == "upgrade" else "-i"
    _run_compose_service(
        c,
        "odoo",
        f"odoo -d odoodb {option} {modules} --stop-after-init",
    )


@task(help={
    "database": "Database name (default: odoodb)"
})
def click_odoo_update(c, database: str = "odoodb"):
    """Run click-odoo-update on the specified database."""
    _run_compose_service(c, "odoo", f"click-odoo-update -d {database}")


@task(help={
    "image_tag": "Custom image tag (optional)",
    "push": "Push image to registry after successful build (default: False)",
    "no_cache": "Build without using cache (default: False)",
})
def build(c, image_tag: str = None, push: bool = False, no_cache: bool = False):
    """Build the isodoo Docker image."""
    build_cmd = [
        "build",
        "-f", "compose/Dockerfile",
        "--target", "isodoo-runtime-private",
        "--build-context", "deps=./deps",
        "--build-context", "addons=./addons",
    ]
    if no_cache:
        build_cmd.append("--no-cache")
    if image_tag:
        build_cmd.extend(["-t", image_tag])
    if c.config.get("client_type", DEFAULT_CLIENT) == "podman":
        build_cmd.extend(["--format", "docker"])
    # Context path must be the last argument
    build_cmd.append("compose/")
    _run_container_cmd(c, " ".join(build_cmd))
    if push and image_tag:
        print(f"→ Pushing image {image_tag}...")
        _run_container_cmd(c, f"push {image_tag}")

@task(help={
    "cmd": "The command to launch",
})
def compose(c, cmd: str):
    _run_container_cmd(c, cmd, compose=True)


#-----------------
# MAIN COLLECTION
#-----------------

ns = Collection(
    git_aggregate,
    shell,
    module,
    click_odoo_update,
    build,
    compose,
)

ns.configure({
    "client_type": DEFAULT_CLIENT,
    "compose_env": DEFAULT_COMPOSE_ENV,
})