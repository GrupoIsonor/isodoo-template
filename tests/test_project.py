#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>


def test_project_structure(project_tmpl):
    assert (project_tmpl / "addons" / "git").is_dir()
    assert (project_tmpl / "compose.yaml").is_file()
    assert not (project_tmpl / "macros").exists()
    assert not (project_tmpl / "recipes").exists()
    assert not (project_tmpl / "_helpers.jinja").exists()
