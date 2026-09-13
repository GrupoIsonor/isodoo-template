#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>

import requests
import pytest
import subprocess
import json
import os
from pathlib import Path
from conftest import EXTRA_ADDONS, invoke_task, wait_for_odoo


def test_task_module(project_tmpl_ci, env_info):
    extra_mod = EXTRA_ADDONS[env_info["options"]["odoo_version"]][1]
    result = invoke_task(env_info["client_type"], project_tmpl_ci, "module", action="list")
    mods = json.loads(result["return"])
    assert "contacts" not in mods
    assert extra_mod not in mods
    invoke_task(env_info["client_type"], project_tmpl_ci, "module", action="install", modules="contacts")
    result = invoke_task(env_info["client_type"], project_tmpl_ci, "module", action="list")
    mods = json.loads(result["return"])
    assert "contacts" in mods
    invoke_task(env_info["client_type"], project_tmpl_ci, "git-aggregate")
    invoke_task(env_info["client_type"], project_tmpl_ci, "module", action="install", extra=True)
    result = invoke_task(env_info["client_type"], project_tmpl_ci, "module", action="list")
    mods = json.loads(result["return"])
    assert extra_mod in mods

def test_task_git_aggregate(project_tmpl_ci, env_info):
    result = invoke_task(env_info["client_type"], project_tmpl_ci, "git-aggregate")
    assert "addons updated!" in result['stdout'].lower()

def test_task_up_stop_start_down_ci(project_tmpl_ci, env_info):
    # Up
    invoke_task(env_info["client_type"], project_tmpl_ci, "up", detach=True, force_recreate=True)
    wait_for_odoo(env_info["ip"], env_info["ports"]["odoo"])
    # Stop
    invoke_task(env_info["client_type"], project_tmpl_ci, "stop")
    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(f"http://{env_info['ip']}:{env_info['ports']['odoo']}", timeout=5)
    # Start
    invoke_task(env_info["client_type"], project_tmpl_ci, "start")
    wait_for_odoo(env_info["ip"], env_info["ports"]["odoo"])
    # Down
    invoke_task(env_info["client_type"], project_tmpl_ci, "down")

def test_task_up_stop_start_down_dev(project_tmpl_dev, env_info):
    # Up
    invoke_task(env_info["client_type"], project_tmpl_dev, "up", detach=True, force_recreate=True)
    wait_for_odoo(env_info["ip"], env_info["ports"]["odoo"])
    # pgweb
    r = requests.get(f"http://{env_info['ip']}:{env_info['ports']['pgweb']}", timeout=5)
    assert r.status_code == 200
    # roundcube
    r = requests.get(f"http://{env_info['ip']}:{env_info['ports']['roundcube']}", timeout=5)
    assert r.status_code == 200
    # Stop
    invoke_task(env_info["client_type"], project_tmpl_dev, "stop")
    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(f"http://{env_info['ip']}:{env_info['ports']['odoo']}", timeout=5)
    # Start
    invoke_task(env_info["client_type"], project_tmpl_dev, "start")
    wait_for_odoo(env_info["ip"], env_info["ports"]["odoo"])
    # Down
    invoke_task(env_info["client_type"], project_tmpl_dev, "down")

def test_task_click_odoo_update(project_tmpl_ci, env_info):
    result = invoke_task(env_info["client_type"], project_tmpl_ci, "click-odoo-update")
    assert "starting..." in result['stdout'].lower()

def test_task_build(project_tmpl_ci, env_info):
    image_tag = "test-isodoo-dummy"
    # Build
    invoke_task(env_info["client_type"], project_tmpl_ci, "build", image_tag=image_tag)
    # Verify exists
    result = subprocess.run(
        [env_info["client_type"], "images", "-q", image_tag],
        capture_output=True, text=True
    )
    assert result.stdout.strip(), f"The image {image_tag} was not created"
    # Clean
    subprocess.run([env_info["client_type"], "rmi", "-f", image_tag], check=True)
