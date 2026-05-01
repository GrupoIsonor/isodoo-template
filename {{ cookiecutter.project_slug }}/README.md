# {{ cookiecutter.project_name }}

## Documentation

If you're using Podman, you'll likely need to build the image before running “compose up”:
```sh
inv build --image-tag `basename $(pwd)`_odoo
```

### Invoke

When a task is invoked, the “container engine” is selected automatically. If you want to force the use of a specific engine, use the `INVOKE_ISODOO_CLIENT_TYPE` environment variable. Example:
```sh
INVOKE_ISODOO_CLIENT_TYPE=docker inv module install -m base
```

## For AIs / LLMs

Read `.skills/project/` first (fixed project rules).  
Then read `.skills/user/` if it exists (custom skills).

Project maintained by {{ cookiecutter.project_owner }}
