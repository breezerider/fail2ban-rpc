#!/usr/bin/env python3
import logging
import sys

import click

from . import __version__


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('f2brpc-client')


@click.command(add_help_option=False, no_args_is_help=True)
@click.help_option('--f2brpc-help', help='Show help message for the RPC client and exit')
@click.version_option(__version__,
                      "--f2brpc-version", help="Print RPC client version and exit",
                      prog_name='f2brpc client',
)
@click.option("--f2brpc-dry-run",
              is_flag=True,
              help="Perform a connection test without running fail2ban-client remotely",
)
@click.option("--f2brpc-verbose", count=True, help="Increase output verbosity for RPC client")
@click.argument("arguments", nargs=-1)
def main(f2brpc_dry_run, f2brpc_verbose, arguments):
    """CLI client for calling fail2ban-client remotely via an RPC call.
    """  # noqa: E501, B950
    sys.exit(0)


if __name__ == "__main__":
    main()
