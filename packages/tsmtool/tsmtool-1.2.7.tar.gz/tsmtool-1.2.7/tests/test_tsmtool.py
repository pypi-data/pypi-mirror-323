import pytest

from tsmtool import Tarsnap


@pytest.fixture
def default_account(config_file):
    text = config_file.read_text()
    line = text.split("\n")[0]
    account = line.split()[0]
    return account


def test_tsmtool_report(config_file, default_account):
    t = Tarsnap(config_file, default_account)
    rows = True
    balance = True
    payments = True
    raw = False
    report = t.get_status(rows, balance, payments, raw)
    assert report
    assert isinstance(report, dict)


def test_tsmtool_bad_email():
    t = Tarsnap(None, None, email="user@example.com", password="1337_d00d")
    with pytest.raises(RuntimeError) as exc_info:
        t.get_status()
    print(exc_info)


def test_tsmtool_bad_password(config_file, default_account):
    t = Tarsnap(config_file, default_account, password="1337_d00d")
    with pytest.raises(RuntimeError) as exc_info:
        t.get_status()
    print(exc_info)
