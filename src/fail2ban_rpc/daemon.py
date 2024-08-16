#!/usr/bin/env python3
from enum import Enum
import logging
import os
import signal
import sys
import time

import daemon
from daemon import pidfile
import click

from . import __version__


class DaemonCommand(Enum):
    RUNNING = "running"
    RESTART = "restart"
    RELOAD = "reload"
    STOP = "stop"


PROG_NAME = "f2brpc"
DEFAULT_PID_PATH = f"/var/run/{PROG_NAME}.pid"
DEFAULT_LOG_PATH = f"/var/log/{PROG_NAME}.log"


class DaemonStatus:
    daemon_command = DaemonCommand.RUNNING
    pid_file = None


def _daemon_stop_sighandler(signum, frame):
    DaemonStatus.daemon_command = DaemonCommand.STOP


def _daemon_reload_sighandler(signum, frame):
    DaemonStatus.daemon_command = DaemonCommand.RELOAD


def _daemon_loop(log_file: str, verbose: int = 0) -> None:
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        filename=log_file,
                        # filemode='w',
                        level=logging.DEBUG if verbose > 0 else logging.INFO)

    logger = logging.getLogger('f2brpc')

    # load server configuration
    logger.debug("stub: load server configuration")

    # create server instance
    logger.debug("stub: create server instance")

    # run the event loop
    logger.debug("stub: run the event loop")
    DaemonStatus.daemon_command = DaemonCommand.RUNNING
    try:
        while DaemonStatus.daemon_command == DaemonCommand.RUNNING:
            logger.info("Heartbeat")
            time.sleep(5)
    except KeyboardInterrupt:
        logger.warning("Keyboard Interrupt...")
    logger.info("Exiting...")


def _daemon_signal(message: str, pid_file: str, sig: signal.Signals) -> bool:
    if os.path.exists(pid_file):
        click.echo(message)
        with open(pid_file) as pid:
            try:
                os.kill(int(pid.readline()), sig)
            except ProcessLookupError as ple:
                os.remove(pid_file)
                click.echo(ple)
                return False
            return True
    else:
        click.echo("No active daemon instance was found")
        return False


@click.group()
@click.help_option('-h', '--help', help='Show help message for the RPC server and exit')
@click.version_option(__version__,
                      "-V", "--version", help="Print RPC server version and exit",
                      prog_name=f'{PROG_NAME} server')
def daemon_cli() -> None:
    """RPC server for calling the local fail2ban-client with arguments passed remotely via an RPC call.
    """  # noqa: E501, B950


@daemon_cli.command(name="reload", add_help_option=False)
@click.option('-p', '--pid-file', type=click.Path(dir_okay=False, writable=True, readable=True, resolve_path=True),
              help="Path to PID file", default=DEFAULT_PID_PATH)
def daemon_reload(pid_file: str):
    sys.exit(not _daemon_signal("Reloading the daemon...", pid_file, signal.SIGHUP))


@daemon_cli.command(name="restart", add_help_option=False)
@click.option('-p', '--pid-file', type=click.Path(dir_okay=False, writable=True, readable=True, resolve_path=True),
              help="Path to PID file", default=DEFAULT_PID_PATH)
@click.option('-l', '--log-file', type=click.Path(dir_okay=False, writable=True, readable=False, resolve_path=True),
              help="Path to log file", default=DEFAULT_LOG_PATH)
@click.option("-v", "--verbose", count=True, help="Increase output verbosity for RPC server")
def daemon_restart(pid_file: str, log_file: str, verbose: int) -> None:
    click.echo("Restarting the daemon...")
    daemon_stop(pid_file)
    time.sleep(1)
    daemon_start(pid_file, log_file, verbose)


@daemon_cli.command(name="start", add_help_option=False)
@click.option('-p', '--pid-file', type=click.Path(dir_okay=False, writable=True, readable=True, resolve_path=True),
              help="Path to PID file", default=DEFAULT_PID_PATH)
@click.option('-l', '--log-file', type=click.Path(dir_okay=False, writable=True, readable=False, resolve_path=True),
              help="Path to log file", default=DEFAULT_LOG_PATH)
@click.option("-v", "--verbose", count=True, help="Increase output verbosity for RPC server")
def daemon_start(pid_file: str, log_file: str, verbose: int) -> None:
    click.echo("Starting the daemon...")
    with daemon.DaemonContext(
        stdout=sys.stdout,
        stderr=sys.stderr,
        working_directory=f'/var/lib/{PROG_NAME}',
        umask=0o002,
        pidfile=pidfile.TimeoutPIDLockFile(pid_file),
        signal_map={
            # signal.SIGKILL: daemon_reload,  # SIGKILL is an Invalid argument
            signal.SIGTERM: _daemon_stop_sighandler,
            signal.SIGTSTP: _daemon_stop_sighandler,
            signal.SIGHUP: _daemon_reload_sighandler,
        }
    ) as context:
        while DaemonStatus.daemon_command != DaemonCommand.STOP:
            _daemon_loop(log_file, verbose)
    sys.exit(0)


@daemon_cli.command(name="status", add_help_option=False)
@click.option('-p', '--pid-file', type=click.Path(dir_okay=False, writable=True, readable=True, resolve_path=True),
              help="Path to PID file", default=DEFAULT_PID_PATH)
def daemon_status(pid_file: str):
    if os.path.exists(pid_file):
        click.echo("Daemon instance is running")
        sys.exit(0)
    else:
        click.echo("No active daemon instance was found")
        sys.exit(1)


@daemon_cli.command(name="stop", add_help_option=False)
@click.option('-p', '--pid-file', type=click.Path(dir_okay=False, writable=True, readable=True, resolve_path=True),
              help="Path to PID file", default=DEFAULT_PID_PATH)
def daemon_stop(pid_file: str):
    sys.exit(not _daemon_signal("Stoping the daemon...", pid_file, signal.SIGINT))


if __name__ == "__main__":
    daemon_cli()
