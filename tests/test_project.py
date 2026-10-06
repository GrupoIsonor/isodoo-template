#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>

import time
import socket
import importlib.util
import shutil
import pytest
from pathlib import Path
from cookiecutter.main import cookiecutter
from conftest import invoke_task, switch_project_mode, wait_for_odoo


def test_project_structure(project_tmpl_ci, project_tmpl_dev):
    assert (project_tmpl_ci / "addons" / "git").is_dir()
    assert (project_tmpl_ci / "compose.yaml").is_file()
    assert not (project_tmpl_ci / "macros").exists()
    assert not (project_tmpl_ci / "recipes").exists()
    assert not (project_tmpl_ci / "_helpers.jinja").exists()
    assert (project_tmpl_dev / "addons" / "git").is_dir()
    assert (project_tmpl_dev / "compose.yaml").is_file()
    assert not (project_tmpl_dev / "macros").exists()
    assert not (project_tmpl_dev / "recipes").exists()
    assert not (project_tmpl_dev / "_helpers.jinja").exists()


@pytest.mark.parametrize(("odoo_version", "has_precommit"), [("10.0", False), ("19.0", True)])
def test_precommit_files_match_odoo_support(tmp_path, odoo_version, has_precommit):
    project_path = Path(cookiecutter(
        template=".",
        output_dir=str(tmp_path),
        no_input=True,
        extra_context={
            "project_name": f"Pre-commit Odoo {odoo_version}",
            "project_slug": f"pre-commit-odoo-{odoo_version.replace('.', '-')}",
            "odoo_version": odoo_version,
        },
    ))
    assert (project_path / ".pre-commit-config.yaml").is_file() == has_precommit
    assert (project_path / ".pylintrc").is_file() == has_precommit


def test_debugpy(project_tmpl_dev, env_info):
    try:
        invoke_task(env_info["client_type"], project_tmpl_dev, "up", services="odoo", force_recreate=True, detach=True, invoke_env={'DEBUGPY_ENABLED': 'true'})
        host = env_info['ip']
        port = int(env_info['ports']['debugpy'])
        for _ in range(90):
            try:
                with socket.create_connection((host, port), timeout=3):
                    break
            except OSError:
                time.sleep(3)
        else:
            pytest.fail("debugpy is not working")
    finally:
        invoke_task(env_info["client_type"], project_tmpl_dev, "down")

def test_squid(project_tmpl_dev, env_info):
    invoke_task(env_info["client_type"], project_tmpl_dev, "up", services="odoo", force_recreate=True, detach=True)
    wait_for_odoo(env_info["ip"], env_info["ports"]["odoo"])
    result = invoke_task(env_info["client_type"], project_tmpl_dev, "check-connection-code", dst="http://www.amazon.com")
    assert result["return"].strip() == "403"
    result = invoke_task(env_info["client_type"], project_tmpl_dev, "check-connection-code", dst="https://www.google.com/generate_204")
    assert result["return"].strip() == "204"
    invoke_task(env_info["client_type"], project_tmpl_dev, "down")
