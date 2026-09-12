FROM ghcr.io/grupoisonor/isodoo:{{ cookiecutter.odoo_version }} AS isodoo-runtime
FROM isodoo-runtime AS isodoo-runtime-private
COPY --from=addons --chown=odoo:odoo /private/ /var/lib/odoo/private
COPY --from=addons --chown=odoo:odoo /addons.yaml /repos.yaml /opt/odoo/
ENV OCONF__options__addons_path="/var/lib/odoo/private,${OCONF__options__addons_path}"

FROM isodoo-runtime-private AS isodoo-runtime-private-dev
ARG PUID=10000
ARG PGID=10001
USER root
RUN set -eux; \
    if [ "${PGID}" != "$(id -g odoo)" ]; then \
        groupmod -g "${PGID}" odoo 2>/dev/null || groupadd -g "${PGID}" odoo; \
    fi; \
    if [ "${PUID}" != "$(id -u odoo)" ]; then \
        usermod -u "${PUID}" -g "${PGID}" odoo; \
    fi; \
    chown -R odoo:odoo /home/odoo /opt/odoo /etc/odoo /var/lib/odoo; \
    apt-get update && apt-get install -y --no-install-recommends \
        htop \
        vim \
        nano \
        less \
        curl \
        procps \
        net-tools \
        iputils-ping; \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*;
USER odoo
# Install extra tools
COPY --chown=odoo:odoo start_dev.sh /usr/local/bin/start_dev
ENV DEBUGPY_LISTEN_ADDRESS="0.0.0.0:5678" \
    DEBUGPY_ENABLED=false \
    ODOO_DEV_MODES="all" \
    GEVENT_SUPPORT=false
ARG DEVEL_EXTRA_PIP_PKGS="debugpy ipdb pudb wdb"
RUN set -eux; \
    chmod +x /usr/local/bin/start_dev; \
    . .venv/bin/activate; \
    if command -v uv >/dev/null 2>&1; then \
        uv pip install --no-cache-dir ${DEVEL_EXTRA_PIP_PKGS}; \
    else \
        pip install --no-cache-dir ${DEVEL_EXTRA_PIP_PKGS}; \
    fi; \
    deactivate;

CMD ["/usr/local/bin/start_dev"]
