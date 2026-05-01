#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>

from pathlib import Path
import importlib.util
import sys
import os
import shutil
from io import StringIO
from invoke import Context, Collection, Config
import contextlib
import pytest
from cookiecutter.main import cookiecutter


def _get_preferred_client_type():
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    raise RuntimeError("Need install podman or docker (with compose)")

def switch_project_mode(container_engine: str, project_path: str |  Path, mode: str):
    invoke_task(container_engine, project_path, "down")
    return invoke_task(container_engine, project_path, "mode", mode)

def invoke_task(container_engine: str, project_path: str | Path, task_name: str, *args, **kwargs):
    project_path = Path(project_path).resolve()
    tasks_path = project_path / "tasks.py"
    if not tasks_path.exists():
        raise FileNotFoundError(f"tasks.py not found in {project_path}")
    module_name = f"tasks_{project_path.name}"
    spec = importlib.util.spec_from_file_location(module_name, tasks_path)
    tasks_module = importlib.util.module_from_spec(spec)
    old_cwd = os.getcwd()
    old_path = sys.path[:]
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    try:
        os.chdir(project_path)
        sys.path.insert(0, str(project_path))
        spec.loader.exec_module(tasks_module)
        if hasattr(tasks_module, "ns") and isinstance(tasks_module.ns, Collection):
            collection = tasks_module.ns
        else:
            collection = Collection.from_module(tasks_module)
        task = collection[task_name]
        config = Config()
        ctx = Context(config=config)
        ctx.config.run.pty = False
        ctx.config.run.echo = False
        ctx.config.run.hide = True
        ctx.config.run.warn = True
        ctx.config.run.in_stream = False
        ctx.config["isodoo_container_engine"] = container_engine
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            result = task(ctx, *args, **kwargs)
        return {
            "return": result,
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
        }
    finally:
        os.chdir(old_cwd)
        sys.path[:] = old_path
        if module_name in sys.modules:
            del sys.modules[module_name]

def pytest_addoption(parser):
    parser.addoption("--odoo-version", action="store", default="6.0")
    parser.addoption("--client-type", action="store", default=None)

@pytest.fixture(scope="session")
def env_info(pytestconfig):
    odoo_ver = pytestconfig.getoption("odoo_version")
    client_type = pytestconfig.getoption("client_type") or _get_preferred_client_type()
    odoo_ver_int = int(float(odoo_ver))
    return {
        "ip": "127.0.0.1",
        "ports": {
            "odoo": f"{odoo_ver_int}069",
        },
        "options": {
            "odoo_version": odoo_ver,
        },
        "client_type": client_type,
    }

@pytest.fixture(scope="session")
def project_tmpl(env_info, tmp_path_factory):
    tmpdir = tmp_path_factory.mktemp("isodoo-render")
    result_dir = cookiecutter(
        template=".",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "project_name": "Test isOdoo Project",
            "project_slug": "test-isodoo-project",
            "odoo_version": env_info["options"]["odoo_version"],
        }
    )
    project_path = Path(result_dir)
    assert project_path.exists(), "The template has not been rendered"
    try:
        # Initialize Odoo
        switch_project_mode(env_info["client_type"], project_path, "ci")
        invoke_task(env_info["client_type"], project_path, "module", "install", "base")
        yield project_path
    finally:
        switch_project_mode(env_info["client_type"], project_path, "dev")
        invoke_task(env_info["client_type"], project_path, "down", remove_volumes=True)
