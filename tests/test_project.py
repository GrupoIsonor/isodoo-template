#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>

import time
import socket
import pytest
import os
from conftest import invoke_task, switch_project_mode, wait_for_odoo


def test_project_structure(project_tmpl):
    assert (project_tmpl / "addons" / "git").is_dir()
    assert (project_tmpl / "compose.yaml").is_file()
    assert not (project_tmpl / "macros").exists()
    assert not (project_tmpl / "recipes").exists()
    assert not (project_tmpl / "_helpers.jinja").exists()

def test_debugpy(project_tmpl, env_info):
    switch_project_mode(env_info["client_type"], project_tmpl, "dev")
    invoke_task(env_info["client_type"], project_tmpl, "build", mode="dev", invoke_env={'UID': os.getuid(), 'GID': os.getgid()})
    try:
        invoke_task(env_info["client_type"], project_tmpl, "up", services="odoo", force_recreate=True, detach=True, invoke_env={'DEBUGPY_ENABLED': 'true'})
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
        invoke_task(env_info["client_type"], project_tmpl, "down")
        switch_project_mode(env_info["client_type"], project_tmpl, "ci")
        invoke_task(env_info["client_type"], project_tmpl, "build")

def test_squid(project_tmpl, env_info):
    switch_project_mode(env_info["client_type"], project_tmpl, "dev")
    invoke_task(env_info["client_type"], project_tmpl, "build", mode="dev", invoke_env={'UID': os.getuid(), 'GID': os.getgid()})
    invoke_task(env_info["client_type"], project_tmpl, "up", services="odoo", force_recreate=True, detach=True)
    wait_for_odoo(env_info["ip"], env_info["ports"]["odoo"])
    result = invoke_task(env_info["client_type"], project_tmpl, "check-connection-code", dst="http://www.amazon.com")
    assert result["return"].strip() == "403"
    result = invoke_task(env_info["client_type"], project_tmpl, "check-connection-code", dst="https://www.google.com/generate_204")
    assert result["return"].strip() == "204"
