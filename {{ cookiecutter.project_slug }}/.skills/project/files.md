# Key Files & Folders

### Addons & Modules
- `addons/addons.yaml` — List of Odoo modules to install
- `addons/repos.yaml` — Sources of modules (OCA repos don't need full URL, custom/PR repos do)
- `private/` — Folder for private/custom Odoo modules

### Dependencies
- `deps/apt.txt` — System packages (apt)
- `deps/pip.txt` — Python packages for the Odoo user
- `deps/npm.txt` — Node.js packages for the Odoo user

### Compose (docker and podman) & Configuration
- `compose/.secrets/` — Secret files used by services
- `compose/config/` — Configuration files for services
- `compose/env/` — Environment variables (per environment)
- `compose/common.yml` — Common services for all environments
- `compose/build.yml` — Build definition
- `compose/dev.yml` — Development services
- `compose/ci.yml` — CI services
- `compose/Dockerfile` — Final build stage (isOdoo onbuild image)

---

**These files define the structure and behavior of the rendered project.**
