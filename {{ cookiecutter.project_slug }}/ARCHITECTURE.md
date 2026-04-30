# Architecture

## Overview

Cookiecutter template for isOdoo environments (Docker/Podman). Generates complete setups: Build, Dev and CI.

## Project Structure

.
├── .skills/              # AI-first documentation
│   └── project/          # Core project rules
├── addons/               # Odoo Core + modules
│   ├── git/              # Core + OCA modules
│   └── private/          # Custom modules
├── compose/              # Docker Compose project files
├── deps/                 # Odoo dependencies (pip, npm and apt)
├── .devcontainer/        # VS Code + AI ready
├── tasks.py              # Invoke tasks
└── README.md

## Key Components

- **Containers**: Odoo + Postgres + Squid + pgWeb + GreenMail
- **Environments**: build / dev / ci (separate compose files)
- **AI Support**: Optimized for agents (Claude, Cursor, Copilot, etc.)

## Using with AI
1. Read `.skills/project/` first
2. Follow SKILL.md files per folder
3. Use `.devcontainer` for full context

## Technical Decisions
- Full Docker/Podman compatibility
- uv + pre-commit + ruff
- Cruft for template updates
