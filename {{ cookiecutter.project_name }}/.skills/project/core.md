# Project Core Skills

This project builds and runs Odoo {{ cookiecutter.odoo_version }} in Docker containers.

### Base Reference
- Main Dockerfile logic comes from:  
  https://github.com/GrupoIsonor/isodoo/blob/master/{{ cookiecutter.odoo_version }}.Dockerfile

### Available Environments
- **prod**  → Production
- **dev**   → Development
- **demo**  → Demo (volatile/ephemeral data)
- **ci**    → Continuous Integration / Testing

### Task Runner
Use **Invoke** (`inv`) for common tasks.  
Run `inv --list` to see all available tasks or check `tasks.py` directly.

### Addons Path Priority
Odoo module search order is controlled by:  
`OCONF__options__addons_path`

---

**These rules apply to the rendered project.**
