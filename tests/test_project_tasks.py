#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>

import requests
import pytest
import subprocess
import json
import os
from pathlib import Path
from conftest import EXTRA_ADDONS, invoke_task, switch_project_mode, wait_for_odoo


def test_task_mode(project_tmpl, env_info):
    # Dev Mode
    result = switch_project_mode(env_info["client_type"], project_tmpl, "dev")
    assert "mode changed to dev" in result['stdout'].lower()
    compose_link = project_tmpl / "compose.yaml"
    assert compose_link.exists() and compose_link.is_symlink(), "Symlink compose.yaml not found"
    assert compose_link.resolve().name == "dev.yaml"
    # CI Mode
    switch_project_mode(env_info["client_type"], project_tmpl, "ci")
    assert (project_tmpl / "compose.yaml").resolve().name == "ci.yaml"

def test_task_module(project_tmpl, env_info):
    switch_project_mode(env_info["client_type"], project_tmpl, "ci")
    extra_mod = EXTRA_ADDONS[env_info["options"]["odoo_version"]][1]
    result = invoke_task(env_info["client_type"], project_tmpl, "module", action="list")
    mods = json.loads(result["return"])
    assert "contacts" not in mods
    assert extra_mod not in mods
    invoke_task(env_info["client_type"], project_tmpl, "module", action="install", modules="contacts")
    result = invoke_task(env_info["client_type"], project_tmpl, "module", action="list")
    mods = json.loads(result["return"])
    assert "contacts" in mods
    invoke_task(env_info["client_type"], project_tmpl, "git-aggregate")
    invoke_task(env_info["client_type"], project_tmpl, "module", action="install", extra=True)
    result = invoke_task(env_info["client_type"], project_tmpl, "module", action="list")
    mods = json.loads(result["return"])
    assert extra_mod in mods

def test_task_git_aggregate(project_tmpl, env_info):
    # Ensure CI Mode
    switch_project_mode(env_info["client_type"], project_tmpl, "ci")
    result = invoke_task(env_info["client_type"], project_tmpl, "git-aggregate")
    assert "addons updated!" in result['stdout'].lower()

@pytest.mark.parametrize("project_mode", ["ci", "dev"])
def test_task_pull_up_stop_start_down(project_tmpl, env_info, project_mode):
    switch_project_mode(env_info["client_type"], project_tmpl, project_mode)
    if project_mode == "dev":
        invoke_task(env_info["client_type"], project_tmpl, "build", mode="dev", invoke_env={'UID': os.getuid(), 'GID': os.getgid()})
    # Up
    invoke_task(env_info["client_type"], project_tmpl, "up", detach=True, force_recreate=True)
    wait_for_odoo(env_info["ip"], env_info["ports"]["odoo"])
    if project_mode == "dev":
        # pgweb
        r = requests.get(f"http://{env_info['ip']}:{env_info['ports']['pgweb']}", timeout=5)
        assert r.status_code == 200
        # roundcube
        r = requests.get(f"http://{env_info['ip']}:{env_info['ports']['roundcube']}", timeout=5)
        assert r.status_code == 200
    # Stop
    invoke_task(env_info["client_type"], project_tmpl, "stop")
    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(f"http://{env_info['ip']}:{env_info['ports']['odoo']}", timeout=5)
    # Start
    invoke_task(env_info["client_type"], project_tmpl, "start")
    wait_for_odoo(env_info["ip"], env_info["ports"]["odoo"])
    # Down
    invoke_task(env_info["client_type"], project_tmpl, "down")

def test_task_click_odoo_update(project_tmpl, env_info):
    switch_project_mode(env_info["client_type"], project_tmpl, "ci")
    result = invoke_task(env_info["client_type"], project_tmpl, "click-odoo-update")
    assert "starting..." in result['stdout'].lower()

def test_task_build(project_tmpl, env_info):
    switch_project_mode(env_info["client_type"], project_tmpl, "ci")
    image_tag = "test-isodoo-dummy"
    # Build
    invoke_task(env_info["client_type"], project_tmpl, "build", image_tag=image_tag)
    # Verify exists
    result = subprocess.run(
        [env_info["client_type"], "images", "-q", image_tag],
        capture_output=True, text=True
    )
    assert result.stdout.strip(), f"The image {image_tag} was not created"
    # Clean
    subprocess.run([env_info["client_type"], "rmi", "-f", image_tag], check=True)

def test_task_pull(project_tmpl, env_info):
    switch_project_mode(env_info["client_type"], project_tmpl, "dev")
    result = invoke_task(env_info["client_type"], project_tmpl, "pull", ignore_buildable=True)
    assert "pulled" in result['stdout'].lower()
