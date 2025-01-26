"""Console script for tsmtool."""

import json
import os
import sys
from pathlib import Path

import click
from tabulate import tabulate

from .tarsnap import Tarsnap
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"

DEFAULT_CONFIG = Path(os.environ["HOME"]) / ".tsmtool"


@click.command("tsmtool")
@click.version_option(message=header)
@click.option(
    "-c",
    "--config-file",
    type=click.Path(dir_okay=False),
    default=DEFAULT_CONFIG,
    envvar="TSMTOOL_CONFIG",
    help="config file for tsmtool",
)
@click.option("-e", "--email", envvar="TSMTOOL_EMAIL", help="email address website login")
@click.option(
    "-p",
    "--password",
    envvar="TSMTOOL_PASSWORD",
    help="password for website login",
)
@click.option("--rows", is_flag=True, help="include all row data")
@click.option("--balances", is_flag=True, help="include daily balances")
@click.option("--payments", is_flag=True, help="include payments")
@click.option("--last-payment", is_flag=True, help="include last payment")
@click.option("--raw", is_flag=True, help="raw data only (skip calculated fields)")
@click.option("--list", "_list", is_flag=True, help="list accounts in config file")
@click.option(
    "--all",
    "_all",
    is_flag=True,
    help="generate report for all accounts in config file",
)
@click.option("-f", "--table", "fmt", flag_value="table", default="table", help="output table format")
@click.option("-j", "--json", "fmt", flag_value="json", help="output json")
@click.option("--tablefmt", default="simple_outline")
@click.option("-d", "--debug", is_flag=True, help="debug mode")
@click.argument("account", type=str, required=False, default=None)
def cli(
    config_file,
    email,
    password,
    rows,
    balances,
    payments,
    raw,
    _list,
    _all,
    debug,
    account,
    fmt,
    tablefmt,
    last_payment,
):
    """login to tarsnap.com and output account status as JSON data

    config file: ~/.tsmtool
    format: whitespace-delimited ASCII file; one line per account
    example:
    account     email_address   password
    """

    def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):

        if debug:
            debug_hook(exception_type, exception, traceback)
        else:
            click.echo(f"{exception_type.__name__}: {exception}", err=True)

    sys.excepthook = exception_handler

    tarsnap = Tarsnap(config_file, account, email, password)

    output = {}

    if _list:
        output["accounts"] = [_account for _account in tarsnap.config]
    elif _all:
        for _account in tarsnap.config:
            tarsnap = Tarsnap(config_file, _account)
            output[_account] = tarsnap.get_status(rows, balances, payments, raw, last_payment=last_payment)
    else:
        output[tarsnap.account] = tarsnap.get_status(rows, balances, payments, raw, last_payment=last_payment)

    if fmt == "table":
        output = [dict(name=k, **v) for k, v in output.items()]
        output = tabulate(output, headers="keys", tablefmt=tablefmt, floatfmt=".2f")
    else:
        output = json.dumps(output, indent=2)

    click.echo(output)

    return 0
