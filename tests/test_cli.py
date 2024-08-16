import pytest
from click.testing import CliRunner

from fail2ban_rpc import __version__
from fail2ban_rpc import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_no_args(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip().startswith('Usage: ')


def test_cli_usage(runner):
    result = runner.invoke(cli.main, ['--f2brpc-help'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip().startswith('Usage: ')


def test_cli_version(runner):
    result = runner.invoke(cli.main, ['--f2brpc-version'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == f'f2brpc client, version {__version__}'
