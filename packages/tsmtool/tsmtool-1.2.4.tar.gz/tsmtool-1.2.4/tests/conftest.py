import os

import pytest


@pytest.fixture(scope="session")
def test_environment():
    assert "TEST_TSMTOOL_ACCOUNT" in os.environ
    assert "TEST_TSMTOOL_EMAIL" in os.environ
    assert "TEST_TSMTOOL_PASSWORD" in os.environ


@pytest.fixture
def config_file(shared_datadir):
    config = shared_datadir / "tsmtool.cfg"
    account = os.environ["TEST_TSMTOOL_ACCOUNT"]
    email = os.environ["TEST_TSMTOOL_EMAIL"]
    password = os.environ["TEST_TSMTOOL_PASSWORD"]
    config.write_text(f"{account}\t{email}\t{password}\n")
    return config
