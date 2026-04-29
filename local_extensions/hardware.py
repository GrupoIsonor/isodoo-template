#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>
import os
from jinja2.ext import Extension


class CPUExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.globals.update(cpu_count=os.cpu_count)
