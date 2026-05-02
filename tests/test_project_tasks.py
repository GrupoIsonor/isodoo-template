#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>

import os
import requests
import time
import pytest
from pathlib import Path
from conftest import invoke_task, switch_project_mode

def _wait_for_odoo(ip_address, port):
    from requests.exceptions import RequestException

    url = f"http://{ip_address}:{port}"
    for _ in range(60):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                break
        except RequestException:
            pass
        time.sleep(2)
    else:
        raise TimeoutError("Odoo did not start on time")


def test_task_mode(project_tmpl, env_info):
    project_tmpl = Path(project_tmpl)
    # Dev Mode
    result = switch_project_mode(env_info["client_type"], project_tmpl, "dev")
    assert "mode changed to dev" in result['stdout'].lower()
    compose_link = project_tmpl / "compose.yml"
    assert compose_link.exists() and compose_link.is_symlink(), "Symlink compose.yml not found"
    assert compose_link.resolve().name == "dev.yml"
    # CI Mode
    switch_project_mode(env_info["client_type"], project_tmpl, "ci")
    assert (project_tmpl / "compose.yml").resolve().name == "ci.yml"

def test_task_git_aggregate(project_tmpl, env_info):
    # Ensure CI Mode
    switch_project_mode(env_info["client_type"], project_tmpl, "ci")
    result = invoke_task(env_info["client_type"], project_tmpl, "git-aggregate")
    assert "addons updated!" in result['stdout'].lower()

def test_task_up_stop_start_down(project_tmpl, env_info):
    switch_project_mode(env_info["client_type"], project_tmpl, "ci")
    # Up
    invoke_task(env_info["client_type"], project_tmpl, "up", detach=True)
    _wait_for_odoo(env_info["ip"], env_info["ports"]["odoo"])
    # Stop
    invoke_task(env_info["client_type"], project_tmpl, "stop")
    url = f"http://{env_info['ip']}:{env_info['ports']['odoo']}"
    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(url, timeout=5)
    # Start
    invoke_task(env_info["client_type"], project_tmpl, "start")
    _wait_for_odoo(env_info["ip"], env_info["ports"]["odoo"])
    # Down
    invoke_task(env_info["client_type"], project_tmpl, "down")

def test_click_odoo_update(project_tmpl, env_info):
    switch_project_mode(env_info["client_type"], project_tmpl, "ci")
    result = invoke_task(env_info["client_type"], project_tmpl, "click-odoo-update")
    assert "starting..." in result['stdout'].lower()
