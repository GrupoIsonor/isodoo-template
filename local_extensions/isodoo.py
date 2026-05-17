#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>
import locale
from jinja2.ext import Extension

PG_VERSIONS = {
    "6.0": "9.6",
    "6.1": "9.6",
    "7.0": "9.6",
    "8.0": "9.6",
    "9.0": "11",
    "10.0": "12",
    "11.0": "13",
    "12.0": "14",
    "13.0": "15",
    "14.0": "16",
    "15.0": "16",
    "16.0": "16",
    "17.0": "17",
    "18.0": "17",
    "19.0": "18",
}

class isOdooAutoConfig(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.globals.update(
            get_odoo_pg_version=self.getPGVersion,
            get_odoo_lang=self.getLang,
        )

    def getPGVersion(self, odoo_version):
        return PG_VERSIONS.get(odoo_version)

    def getLang(self, default_lang):
        return locale.getlocale()[0] or default_lang
