#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>

from pathlib import Path
import importlib.util
import sys
import os
import shutil
import time
import requests
from io import StringIO
from invoke import Context, Collection, Config
import contextlib
import pytest
import yaml
from cookiecutter.main import cookiecutter

EXTRA_ADDONS = {
    "6.0": ("l10n-spain", "city"),
    "6.1": ("reporting-engine", "report_xls"),
    "7.0": ("reporting-engine", "report_xls"),
    "8.0": ("reporting-engine", "report_xlsx"),
    "9.0": ("reporting-engine", "report_xlsx"),
    "10.0": ("reporting-engine", "report_xlsx"),
    "11.0": ("reporting-engine", "report_xlsx"),
    "12.0": ("reporting-engine", "report_xlsx"),
    "13.0": ("reporting-engine", "report_xlsx_boilerplate"),
    "14.0": ("reporting-engine", "report_fillpdf"),
    "15.0": ("reporting-engine", "report_xlsx"),
    "16.0": ("reporting-engine", "sql_export_excel"),
    "17.0": ("reporting-engine", "sql_export_excel"),
    "18.0": ("reporting-engine", "sql_export_excel"),
    "19.0": ("reporting-engine", "report_xlsx"),
}


def _get_preferred_client_type():
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    raise RuntimeError("Need install podman or docker (with compose)")

def switch_project_mode(container_engine: str, project_path: str |  Path, mode: str):
    invoke_task(container_engine, project_path, "down")
    return invoke_task(container_engine, project_path, "mode", mode)

def wait_for_odoo(ip_address, port):
    from requests.exceptions import RequestException

    url = f"http://{ip_address}:{port}"
    for _ in range(120):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                break
        except RequestException:
            pass
        time.sleep(3)
    else:
        raise TimeoutError("Odoo did not start on time")

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
        invoke_env = kwargs.get("invoke_env")
        if invoke_env:
            ctx.config.run.env.update(invoke_env)
            kwargs.pop("invoke_env")
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
    parser.addoption("--no-cache", action="store_true", default=False)

@pytest.fixture(scope="session")
def env_info(pytestconfig):
    odoo_ver = pytestconfig.getoption("odoo_version")
    client_type = pytestconfig.getoption("client_type") or _get_preferred_client_type()
    no_cache = pytestconfig.getoption("no_cache")
    odoo_ver_int = int(float(odoo_ver))
    return {
        "ip": "127.0.0.1",
        "ports": {
            "odoo": f"{odoo_ver_int}069",
            "pgweb": f"{odoo_ver_int}081",
            "roundcube": f"{odoo_ver_int}090",
            "debugpy": "5678",
        },
        "options": {
            "odoo_version": odoo_ver,
            "no_cache": no_cache,
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
            "_debugpy_port": env_info["ports"]["debugpy"],
        }
    )
    project_path = Path(result_dir)
    assert project_path.exists(), "The template has not been rendered"
    with open(project_path / "addons" / "addons.yaml", "r+") as f:
        data = yaml.safe_load(f) or {}
        extra_addon_repo, extra_addon_name = EXTRA_ADDONS[env_info["options"]["odoo_version"]]
        data[extra_addon_repo] = [extra_addon_name]
        yaml.dump(data, f, sort_keys=False, default_flow_style=False)
    try:
        # Use CI Mode
        switch_project_mode(env_info["client_type"], project_path, "ci")
        # Build
        invoke_task(env_info["client_type"], project_path, "build", no_cache=env_info["options"]["no_cache"])
        # Initialize Odoo
        invoke_task(env_info["client_type"], project_path, "db", "init")
        yield project_path
    finally:
        switch_project_mode(env_info["client_type"], project_path, "dev")
        invoke_task(env_info["client_type"], project_path, "destroy-this-project", force=True)
