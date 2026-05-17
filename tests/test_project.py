#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>

import time
import socket
import json
import pytest
from conftest import invoke_task, switch_project_mode


def test_project_structure(project_tmpl):
    assert (project_tmpl / "addons" / "git").is_dir()
    assert (project_tmpl / "compose.yaml").is_file()
    assert not (project_tmpl / "macros").exists()
    assert not (project_tmpl / "recipes").exists()
    assert not (project_tmpl / "_helpers.jinja").exists()

def test_debugpy(project_tmpl, env_info):
    switch_project_mode(env_info["client_type"], project_tmpl, "dev")
    invoke_task(env_info["client_type"], project_tmpl, "build", mode="dev")
    # Up
    invoke_task(env_info["client_type"], project_tmpl, "up", detach=True, invoke_env={'DEBUGPY_ENABLED': 'true'})
    # Test Basic Connection
    host = env_info['ip']
    port = int(env_info['ports']['debugpy'])
    for _ in range(30):
        try:
            with socket.create_connection((host, port), timeout=3) as s:
                req = {
                    "seq": 1,
                    "type": "request",
                    "command": "initialize",
                    "arguments": {"adapterID": "python"}
                }
                msg = json.dumps(req)
                s.sendall(f"Content-Length: {len(msg)}\r\n\r\n{msg}".encode())
                response = s.recv(8192).decode(errors='ignore')
                if any(x in response for x in ["debugpySockets", "success", "output"]):
                    break
        except:
            time.sleep(2)
    else:
        pytest.fail("debugpy is not working")
    # Down
    invoke_task(env_info["client_type"], project_tmpl, "down")
    # Restore Image
    switch_project_mode(env_info["client_type"], project_tmpl, "ci")
    invoke_task(env_info["client_type"], project_tmpl, "build")

def test_squid(project_tmpl, env_info):
    switch_project_mode(env_info["client_type"], project_tmpl, "dev")
    result = invoke_task(env_info["client_type"], project_tmpl, "check-connection-code", dst="http://www.amazon.com")
    assert "403" in result["return"]
    result = invoke_task(env_info["client_type"], project_tmpl, "check-connection-code", dst="http://www.google.com")
    assert "200" in result["return"]
