#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>
from invoke import task, Collection
from pathlib import Path
from io import StringIO
import shutil
import os
import subprocess


#-----------------
# HELPERS
#-----------------

def _get_preferred_client_type():
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    raise RuntimeError("podman or docker (with compose plugin) is required")


DEFAULT_CONTAINER_ENGINE = _get_preferred_client_type()


def _get_container_ids(c) -> tuple[str, str]:
    env = c.config.run.env
    return (
        str(env.get("PUID", os.getenv("PUID", os.getuid()))),
        str(env.get("PGID", os.getenv("PGID", os.getgid()))),
    )


def _run_container_cmd(
    c,
    command: str,
    check: bool = False,
    stdin: str = None,
    pty: bool = False,
    disown: bool = False,
    hide: bool = False,
    compose: bool = False,
    env: dict = None,
) -> str:
    """Execute a command using docker or podman."""
    client_type = c.config.get("isodoo_container_engine", DEFAULT_CONTAINER_ENGINE)
    final_cmd = f"{client_type} compose {command}" if compose else f"{client_type} {command}"
    if compose:
        puid, pgid = _get_container_ids(c)
        env = {"PUID": puid, "PGID": pgid, **(env or {})}
    result = c.run(
        final_cmd,
        in_stream=StringIO(stdin) if stdin else None,
        pty=pty,
        warn=not check,
        hide=hide,
        disown=disown,
        env=env,
    )
    # Clean unwanted podman/docker warnings
    clean_lines = [
        line
        for line in result.stdout.splitlines(keepends=True)
        if "The input device is not a TTY" not in line
    ]
    return "".join(clean_lines)


def _run_compose_service(c, service: str, command: str, volumes: list[str] | None = None, env: dict[str, str] | None = None, tty: bool = False, no_entrypoint: bool = False, **kwargs):
    cmd = ["run", "--rm"]
    if tty:
        cmd.append("-it")
    if no_entrypoint:
        cmd += ['--entrypoint', '/bin/sh']
    if volumes and isinstance(volumes, list):
        for volume in volumes:
            cmd += ['-v', volume]
    if env and isinstance(env, dict):
        for key, value in env.items():
            cmd += ['-e', f"{key}={value}"]
    cmd += [service, command]
    return _run_container_cmd(c, " ".join(cmd), compose=True, **kwargs)


#-----------------
# CONTAINER TASKS
#-----------------

@task(optional=["detach", "build", "no_cache"], help={
    "services": "Comma-separated list of services",
})
def up(c, services: str = "", detach: bool = True, build: bool = False, no_cache: bool = False, force_recreate: bool = False):
    # Symlink
    link = "compose.yaml"
    if not os.path.islink(link) and not os.path.exists(link):
        print("No compose.yaml detected... Fallback to 'dev' mode...")
        mode(c, "dev")
    cmd = ["up"]
    if detach:
        cmd.append("-d")
    if build:
        cmd.append("--build")
    if no_cache:
        cmd.append("--no-cache")
    if force_recreate:
        cmd.append("--force-recreate")
    if services:
        cmd += [s.strip() for s in services.split(",")]
    _run_container_cmd(c, " ".join(cmd), compose=True)


@task(optional=["remove_volumes"], help={
    "services": "Comma-separated list of services",
    "remove_volumes": "Mark volumes to be removed (data loss!)",
})
def down(c, services: str = "", remove_volumes=False):
    cmd = ["down"]
    if remove_volumes:
        cmd.append("--volumes")
    if services:
        cmd += [s.strip() for s in services.split(",")]
    _run_container_cmd(c, " ".join(cmd), compose=True)


@task(help={
    "services": "Comma-separated list of services",
})
def start(c, services: str = ""):
    cmd = ["start"]
    if services:
        cmd += [s.strip() for s in services.split(",")]
    _run_container_cmd(c, " ".join(cmd), compose=True)


@task(help={
    "services": "Comma-separated list of services",
})
def stop(c, services: str = ""):
    cmd = ["stop"]
    if services:
        cmd += [s.strip() for s in services.split(",")]
    _run_container_cmd(c, " ".join(cmd), compose=True)


@task(help={
    "services": "Comma-separated list of services",
})
def pull(c, services: str = "", ignore_buildable: bool = False, ignore_pull_failures: bool = False):
    # Symlink
    link = "compose.yaml"
    if not os.path.islink(link) and not os.path.exists(link):
        print("No compose.yaml detected... Fallback to 'dev' mode...")
        mode(c, "dev")
    cmd = ["pull"]
    if ignore_buildable:
        cmd.append("--ignore-buildable")
    if ignore_pull_failures:
        cmd.append("--ignore-pull-failures ")
    if services:
        cmd += [s.strip() for s in services.split(",")]
    _run_container_cmd(c, " ".join(cmd), compose=True)


@task(optional=["force"], help={
    "services": "Comma-separated list of services",
    "force": "Skip confirmation (default: False)",
})
def destroy_this_project(c, services: str = "", force: bool = False):
    cmd = ["down", "--rmi", "all", "--volumes"]
    if services:
        cmd += [s.strip() for s in services.split(",")]
    if not force:
        confirm = input("Delete all (images, volumes, containers)? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return
    _run_container_cmd(c, " ".join(cmd), compose=True)


@task(help={
    "database": "Database name (default: {{ cookiecutter.odoo_db_name }})",
})
def git_aggregate(c, database: str = "{{ cookiecutter.odoo_db_name }}"):
    _run_compose_service(c, "odoo", f"isodoo_update_addons -d {database}")


@task(help={
    "interface": "Preferred REPL (ipython|ptpython|bpython|python)",
    "file": "Python script to be run after the start of the shell",
    "database": "Database name (default: {{ cookiecutter.odoo_db_name }})",
})
def shell(c, interface: str = "ipython", file: str | None = None, database: str = "{{ cookiecutter.odoo_db_name }}"):
    client_type = c.config.get("isodoo_container_engine", DEFAULT_CONTAINER_ENGINE)
    shell_cmd = [client_type, "compose", "run", "--rm", "odoo", "odoo", "shell", "-d", database, "--no-http", "--shell-interface", interface]
    if file:
        shell_cmd += ["--shell-file", file]
    subprocess.call(shell_cmd)


@task(positional=["action", "modules", "database"], optional=["core", "extra", "private"], help={
    "action": "install or upgrade",
    "modules": "Comma-separated list of modules",
    "database": "Database name (default: {{ cookiecutter.odoo_db_name }})",
})
def module(c, action: str, modules: str = "", core: bool = False, extra: bool = False, private: bool = False, database: str = "{{ cookiecutter.odoo_db_name }}"):
    """Install or upgrade Odoo modules."""
    if action in ("install", "upgrade"):
        folders = []
        if core:
            folders.append("/var/lib/odoo/core/*")
        if extra:
            folders.append("/var/lib/odoo/extra/*")
        if private:
            folders.append("/var/lib/odoo/private/*")
        mod_list = []
        if folders:
            cmd = f"-c \"ls -1d {' '.join(folders)} 2>/dev/null || true\""
            result = _run_compose_service(c, "odoo", cmd, no_entrypoint=True, hide=True)
            mod_list.extend(line.strip().split('/')[-1] for line in result.splitlines() if line.strip())
        if modules:
            mod_list.extend(m.strip() for m in modules.split(",") if m.strip())
        if not mod_list:
            print("No modules selected")
            return
        option = "-u" if action == "upgrade" else "-i"
        final_modules = ",".join(mod_list)
        print("Modules:", final_modules)
        _run_compose_service(
            c, "odoo",
            f"odoo -d {database} --no-http --stop-after-init --workers=0 --max-cron-threads=0 {option} {final_modules}"
        )
    elif action == "list":
        installed_mods = _run_compose_service(
            c, "odoo", "click-odoo",
            stdin="mods=env['ir.module.module'].search([('state','=','installed')]).mapped('name');import json;print('|||',json.dumps(mods));",
            hide=True,
        )
        installed_mods = installed_mods.split("|||")[-1].strip()
        print(installed_mods)
        return installed_mods
    else:
        raise ValueError("Action must be 'install', 'upgrade' or 'list'")


@task(help={
    "database": "Database name (default: {{ cookiecutter.odoo_db_name }})",
})
def click_odoo_update(c, database: str = "{{ cookiecutter.odoo_db_name }}"):
    _run_compose_service(c, "odoo", f"click-odoo-update -d {database}")


@task(help={
    "action": "init",
    "database": "Database name (default: {{ cookiecutter.odoo_db_name }})",
})
def db(c, action: str, database: str = "{{ cookiecutter.odoo_db_name }}"):
    if action not in ["init"]:
        raise ValueError("Action must be init")
    if action == "init":
        load_lang = "{{ cookiecutter.odoo_base_language }}"
{%- if cookiecutter.odoo_version|float < 19 %}
        _run_compose_service(
            c, "odoo",
            f"odoo -d {database} --no-http --stop-after-init --workers=0 --max-cron-threads=0 --load-language {load_lang} -i base",
        )
{%- else %}
        _run_compose_service(
            c, "odoo",
            f"odoo db init {database} --language {load_lang}",
            env={
                'PSQL_WAIT_TIMEOUT': '0',
            }
        )
{%- endif %}

@task(help={
    "name": "Module name",
})
def scaffold(c, name: str):
    _run_compose_service(
        c, "odoo",
        f"odoo scaffold {module} /tmp/addons",
        volumes=["./addons/private:/tmp/addons"]
    )

@task(help={
    "dst": "URL to check",
})
def check_connection_code(c, dst: str):
    result = _run_compose_service(c, "odoo", "-c \"curl -s -o /dev/null -w '%{http_code}' " + dst + "\"", no_entrypoint=True)
    return result


@task(optional=["push", "no_cache"], help={
    "mode": "prod or dev (default: prod)",
    "image_tag": "Image tag (default: <project_folder>_odoo)",
    "push": "Push image to registry after successful build (default: False)",
    "no_cache": "Build without using cache (default: False)",
})
def build(c, mode="prod", image_tag=None, push: bool = False, no_cache: bool = False):
    """Build the isodoo Docker image."""
    if mode not in ["prod", "dev"]:
        raise ValueError("Mode must be prod/dev")
    build_cmd = [
        "build",
        "-f", "compose/Dockerfile",
        "--build-context", "deps=./deps",
        "--build-context", "addons=./addons",
    ]
    puid, pgid = _get_container_ids(c)
    if mode == "prod":
        build_cmd += [
            "--target", "isodoo-runtime-private",
            "--build-arg", f"PUID={puid}",
            "--build-arg", f"PGID={pgid}",
        ]
    else:
        build_cmd += [
            "--target", "isodoo-runtime-private-dev",
            "--build-arg", f"PUID={puid}",
            "--build-arg", f"PGID={pgid}",
        ]
    if not image_tag:
        project_name = Path(os.getcwd()).name.lower().replace(" ", "_")
        image_tag = f"{project_name}-odoo"
    if no_cache:
        build_cmd.append("--no-cache")
    build_cmd.extend(["-t", image_tag])
    if c.config.get("isodoo_container_engine", DEFAULT_CONTAINER_ENGINE) == "podman":
        build_cmd.extend(["--format", "docker"])
    # Context path must be the last argument
    build_cmd.append("compose/")
    _run_container_cmd(c, " ".join(build_cmd))
    if push and image_tag:
        print(f"→ Pushing image {image_tag}...")
        _run_container_cmd(c, f"push {image_tag}")


#-----------------
# PROJECT TASKS
#-----------------

@task(help={
    "mode": "The project mode (dev|ci)",
})
def mode(c, mode: str):
    if mode not in ["ci", "dev"]:
        raise ValueError("Mode must be dev/ci")
    # Check no services running
    if os.path.exists("compose.yaml") and _run_container_cmd(c, "ps -q", compose=True, pty=False).strip():
        raise RuntimeError("Stop services first")
    project_root = Path(c.cwd)
    # Symlink
    target = project_root / f"{mode}.yaml"
    link = "compose.yaml"
    if os.path.islink(link) or os.path.exists(link):
        os.unlink(link)
    os.symlink(target, link)
    # Create Mode Dirs
    if mode == "dev":
        git_dir = project_root / "addons" / "git"
        git_dir.mkdir(parents=True, exist_ok=True)
    print(f"Project mode changed to {mode}")
    return mode


#-----------------
# MAIN COLLECTION
#-----------------

ns = Collection(
    up,
    down,
    stop,
    start,
    pull,
    destroy_this_project,
    git_aggregate,
    shell,
    module,
    db,
    scaffold,
    click_odoo_update,
    check_connection_code,
    build,
    mode,
)

ns.configure({
    "isodoo_container_engine": DEFAULT_CONTAINER_ENGINE,
})
