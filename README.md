<h1 align="center">
  <div>isOdoo - Template</div>

[![Tests](https://github.com/GrupoIsonor/isodoo-template/actions/workflows/isodoo.yml/badge.svg)](https://github.com/GrupoIsonor/isodoo-template/actions/workflows/isodoo.yml)

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

- Developer and CI environments
- Predefined tasks for working with the environment and building the production image 
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

This project is not intended for use as-is in production. It is intended for development and the creation of images for production.

## Simple Usage

```sh
cruft create https://github.com/GrupoIsonor/isodoo-template.git
```

Due to security policies, this template does not prompt for passwords. Default values are used. The best way to control these values is through the python API or by forcing the values in the Cookiecutter configuration file.

Default values:
- Postgres Superuser Password: postgres
- Odoo Admin Password: odoo

Cookiecutter keys:
- Postgres Superuser Password: _default_postgres_superuser_password
- Odoo Admin Password: _default_odoo_database_password

## Advance Usage

The best way to have full control is to fork this project and customize it (Don't forget to share anything you find interesting!)

To avoid issues with template updates, its best to always use the "merge feature" provided by "compose": https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/
