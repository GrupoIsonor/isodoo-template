#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

NO_PRECOMMIT_ODOO_VERSIONS = ("6.0", "6.1", "7.0", "8.0", "9.0", "10.0")

project_root = Path.cwd()
project_mode = "{{ cookiecutter.project_mode }}"
odoo_version = "{{ cookiecutter.odoo_version }}"

### Create compose.yml symlink
if project_mode == "dev":
    git_dir = project_root / "addons" / "git"
    git_dir.mkdir(parents=True, exist_ok=True)
os.symlink(f'compose/{project_mode}.yaml', 'compose.yml')

### Move recipes
recipes_dir = source_dir = project_root / "recipes"
if odoo_version not in NO_PRECOMMIT_ODOO_VERSIONS:
    source_dir = recipes_dir / odoo_version
    shutil.copytree(source_dir, project_root, dirs_exist_ok=True)
shutil.rmtree(recipes_dir)

### Clean project folder
if odoo_version not in NO_PRECOMMIT_ODOO_VERSIONS:
    precommit_files_to_remove = [
        ".pre-commit-config.yaml",
        "eslint.config.cjs",
        ".ruff.toml",
    ]
    for file in precommit_files_to_remove:
        os.remove(project_root / file)
files_to_remove = [
    "_helpers.jinja",
]
for file in files_to_remove:
    os.remove(project_root / file)
shutil.rmtree(project_root / "macros")