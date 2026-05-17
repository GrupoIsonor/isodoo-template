<h1 align="center">
  <div>isOdoo - Template</div>

[![Tests](https://github.com/GrupoIsonor/isodoo-template/actions/workflows/isodoo-template.yml/badge.svg)](https://github.com/GrupoIsonor/isodoo-template/actions/workflows/isodoo-template.yml)

</h1>

<p align="center">
*** PROJECT UNDER DEVELOPMENT. NOT READY FOR PRODUCTION ***

[Cookiecutter](https://www.cookiecutter.io/) template for <a href="https://github.com/GrupoIsonor/isodoo">isOdoo</a>
</p>
<p align="center">
-- <a href="https://www.grupoisonor.es/">Grupo Isonor</a> --
</p>

---

## Features

- Development and CI environments
- Predefined tasks (using invoke)
- Support podman and docker workflows
- AI-Ready (comes with documentation for AI agents)
- [Squid](https://www.squid-cache.org/) - Traffic filter [all envs]
- [pgWeb](https://sosedoff.github.io/pgweb/) - PostgreSQL client [dev env]
- [GreenMail](https://greenmail-mail-test.github.io/greenmail) - Sand-boxed email servers [dev env]
- [Roundcube](https://roundcube.net/) - Webmail [dev env]

## System Requirements

- [Docker](https://www.docker.com/) + Compose **or** [Podman](https://podman.io/) + Compose
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Necessary Tools

- [cruft](https://cruft.github.io/cruft/):
  ```sh
  uv tool install cruft --with jinja2-ansible-filters
  ```

- [pre-commit](https://pre-commit.com/):
  ```sh
  uv tool install pre-commit --with pre-commit-uv
  ```

- [invoke](https://www.pyinvoke.org/):
  ```sh
  uv tool install invoke
  ```

## Basic Documentation

**This template is not meant for direct production use.**

It serves as a starting point for development teams to build, test, and customize their isOdoo-based applications. It facilitates local development, testing environments, and the creation of optimized container images ready for production deployment.

## Environment Variables (dev mode)

| Name | Description | Default |
| ---- | ----------- | ------- |
| DEBUGPY_ENABLED | Enable debugpy | false |
| ODOO_DEV_MODES | Development modes | all |

** Check available "dev modes" here: https://www.odoo.com/documentation/19.0/developer/reference/cli.html#cmdoption-odoo-bin-dev

## Simple Usage

```sh
cruft create https://github.com/GrupoIsonor/isodoo-template.git
cd <project_folder>
inv db init
docker compose up
```

## Advance Usage

The best way to have full control is to fork this project and customize it (Don't forget to share anything you find interesting!)

To avoid issues with template updates, its best to always use the "merge feature" provided by "compose": https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/
