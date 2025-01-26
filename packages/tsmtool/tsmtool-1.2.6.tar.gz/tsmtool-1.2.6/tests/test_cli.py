#!/usr/bin/env python

"""Tests for `tsmtool` package."""

from click.testing import CliRunner

import tsmtool


def test_cli_version():
    """Test reading version and module name"""
    assert tsmtool.__name__ == "tsmtool"
    assert tsmtool.__version__
    assert isinstance(tsmtool.__version__, str)


def test_cli_help():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(tsmtool.cli, ["--help"])
    assert result.exit_code == 0, result
    assert "Show this message and exit." in result.output
