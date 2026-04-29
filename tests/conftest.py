#!/usr/bin/env python3
# Copyright Grupo Isonor - Alexandre D. <dev@redneboa.es>
from cookiecutter.main import cookiecutter


def pytest_addoption(parser):
    parser.addoption("--no-cache", action="store_true", default=False)
    parser.addoption("--odoo-version", action="store", default="6.0")
    parser.addoption("--client-type", action="store", default=None)

@pytest.fixture
def custom_template(tmp_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        result_dir = cookiecutter(
            template=".",
            output_dir=tmpdir,
            no_input=True,
            extra_context={"project_name": "test-proj"}
        )
        project_path = Path(result_dir)
        yield project_path
