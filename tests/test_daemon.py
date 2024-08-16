import signal

import click
import pytest
from click.testing import CliRunner

from fail2ban_rpc import __version__
from fail2ban_rpc import daemon


class MockTimeoutPIDLockFile:
    def __init__(self, pid_file: str):
        self.pid_file = pid_file


class MockDaemonContext:
    def __init__(self, **kwargs):
        MockDaemonContext.kwargs = kwargs

    def __enter__(self):
        self.entered = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exited = True


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_no_args(runner):
    result = runner.invoke(daemon.daemon_cli)
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip().startswith('Usage: ')


def test_cli_usage(runner):
    result = runner.invoke(daemon.daemon_cli, ['--help'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip().startswith('Usage: ')


def test_cli_version(runner):
    result = runner.invoke(daemon.daemon_cli, ['--version'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == f'f2brpc server, version {__version__}'


@pytest.mark.parametrize('retval', [True, False])
def test_cli_daemon_reload(runner, mocker, retval):
    expected_pid_file = '/path/to/pid_file'

    # replace the real _daemon_signal with a mock
    mocked_daemon_signal = mocker.patch.object(daemon, '_daemon_signal')
    mocked_daemon_signal.return_value = retval

    result = runner.invoke(daemon.daemon_cli, ['reload','--pid-file',expected_pid_file])
    assert result.exit_code == (not retval)
    assert retval or result.exception

    mocked_daemon_signal.assert_called_with("Reloading the daemon...", expected_pid_file, signal.SIGHUP)


def test_cli_daemon_restart(runner, mocker, monkeypatch):
    expected_pid_file = '/path/to/pid_file'
    expected_log_file = '/path/to/log_file'

    # replace the real _daemon_loop with a mock
    mocked_daemon_start = mocker.patch.object(daemon,'daemon_start')
    mocked_daemon_stop = mocker.patch.object(daemon,'daemon_stop')

    result = runner.invoke(daemon.daemon_cli, ['restart','--pid-file',expected_pid_file,'--log-file',expected_log_file,'--verbose'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip().startswith('Restarting the daemon...')

    mocked_daemon_stop.assert_called_with(expected_pid_file)
    mocked_daemon_start.assert_called_with(expected_pid_file, expected_log_file, 1)


def test_cli_daemon_start(runner, mocker, monkeypatch):
    expected_keys = ['stdout', 'stderr', 'working_directory', 'umask', 'pidfile', 'signal_map']
    expected_working_directory = '/var/lib/f2brpc'
    expected_umask = 2
    expected_pid_file = '/path/to/pid_file'
    expected_log_file = '/path/to/log_file'

    # replace the real daemon.DaemonContext with MockDaemonContext
    monkeypatch.setattr(daemon.pidfile, "TimeoutPIDLockFile", MockTimeoutPIDLockFile)

    # replace the real daemon.DaemonContext with MockDaemonContext
    monkeypatch.setattr(daemon.daemon, "DaemonContext", MockDaemonContext)

    # replace the real _daemon_loop with a mock
    def mock_daemon_loop(log_file: str, verbose: int) -> None:
        daemon.DaemonStatus.daemon_command = daemon.DaemonCommand.STOP
    mocked_daemon_loop = mocker.patch.object(daemon, '_daemon_loop')
    mocked_daemon_loop.side_effect = mock_daemon_loop

    result = runner.invoke(daemon.daemon_cli, ['start','--pid-file',expected_pid_file,'--log-file',expected_log_file,'--verbose'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip().startswith('Starting the daemon...')

    assert sorted(expected_keys) == sorted(MockDaemonContext.kwargs.keys())
    assert MockDaemonContext.kwargs['working_directory'] == expected_working_directory
    assert MockDaemonContext.kwargs['umask'] == expected_umask
    assert MockDaemonContext.kwargs['pidfile'].pid_file == expected_pid_file
    mocked_daemon_loop.assert_called_with(expected_log_file, 1)


@pytest.mark.parametrize('exists_retval', [True, False])
def test_cli_daemon_status(runner, mocker, exists_retval):
    expected_pid_file = '/path/to/pid_file'

    # replace the real os.path.exists with a mock
    mocked_exists = mocker.patch('os.path.exists')
    mocked_exists.return_value = exists_retval

    result = runner.invoke(daemon.daemon_cli, ['status','--pid-file',expected_pid_file])

    if exists_retval:
        assert "Daemon instance is running" == result.stdout.strip()
        assert result.exit_code == 0
        assert not result.exception
    else:
        assert "No active daemon instance was found" == result.stdout.strip()
        assert result.exit_code == 1
        assert result.exception


@pytest.mark.parametrize('exists_retval', [True, False])
def test_cli_daemon_stop(runner, mocker, exists_retval):
    expected_pid_file = '/path/to/pid_file'

    # replace the real _daemon_signal with a mock
    mocked_daemon_signal = mocker.patch.object(daemon, '_daemon_signal')
    mocked_daemon_signal.return_value = exists_retval

    result = runner.invoke(daemon.daemon_cli, ['stop','--pid-file',expected_pid_file])
    assert result.exit_code == (not exists_retval)
    assert (exists_retval and not result.exception) or (not exists_retval and result.exception)

    mocked_daemon_signal.assert_called_with("Stoping the daemon...", expected_pid_file, signal.SIGINT)


@pytest.mark.parametrize('exists_retval, kill_side_effect', [(True, None), (True, ProcessLookupError("test error")), (False, None)])
def test_daemon_signal(capsys, mocker, exists_retval, kill_side_effect):
    expected_pid_file = '/path/to/pid_file'
    expected_pid = '0'

    # replace the real os.kill with a mock
    mocked_kill = mocker.patch('os.kill')
    mocked_kill.side_effect = kill_side_effect

    # replace the real os.path.exists with a mock
    mocked_exists = mocker.patch('os.path.exists')
    mocked_exists.return_value = exists_retval

    # replace the real os.remove with a mock
    mocked_remove = mocker.patch('os.remove')

    # replace the real os.path.exists with a mock
    mocked_open = mocker.patch.object(daemon, 'open', mocker.mock_open(read_data=expected_pid))

    result = daemon._daemon_signal("test message", expected_pid_file, signal.SIGCONT)
    stdout, stderr = capsys.readouterr()

    if exists_retval:
        mocked_open.assert_called_with(expected_pid_file)
        mocked_kill.assert_called_with(int(expected_pid), signal.SIGCONT)
        if kill_side_effect:
            mocked_remove.assert_called_with(expected_pid_file)
            assert "test message\ntest error" == stdout.strip()
            assert result is False
        else:
            assert "test message" == stdout.strip()
            assert result is True
    else:
        assert "No active daemon instance was found" == stdout.strip()
        assert result is False

    mocked_exists.assert_called_with(expected_pid_file)


def test_daemon_loop(caplog, mocker, monkeypatch):
    expected_log_file = '/path/to/log_file'

    # replace the real time.sleep with a mock
    mocked_sleep = mocker.patch.object(daemon.time, 'sleep')
    mocked_sleep.side_effect = KeyboardInterrupt()

    daemon._daemon_loop(expected_log_file)
