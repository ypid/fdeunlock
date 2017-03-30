# -*- coding: utf-8 -*-

"""
Command line interface of fdeunlock
"""

from __future__ import absolute_import, division, print_function

import sys
import logging
import textwrap
import argparse

from ._meta import __version__
from .fdeunlock import FdeUnlock
from .vault import FileVault
from .checker import get_default_checkers, CheckViolation

__all__ = ['main']

LOG = logging.getLogger(__name__)


def get_args_parser():
    args_parser = argparse.ArgumentParser(
        prog='fdeunlock',
        description=textwrap.dedent("""
            Check and unlock full disk encrypted systems via ssh
        """),
        # epilog=__doc__,
    )
    args_parser.add_argument(
        '-V', '--version',
        action='version',
        version=__version__,
    )
    args_parser.add_argument(
        '-d', '--debug',
        help="Write debugging and higher to STDOUT|STDERR.",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
    )
    args_parser.add_argument(
        '-v', '--verbose',
        help="Write information and higher to STDOUT|STDERR.",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )
    args_parser.add_argument(
        '-q', '--quiet', '--silent',
        help="Only write errors and higher to STDOUT|STDERR.",
        action="store_const",
        dest="loglevel",
        const=logging.ERROR,
    )
    args_parser.add_argument(
        '-H', '--host',
        help="Hostname of the remove server",
        required=True,
    )
    args_parser.add_argument(
        '-n',
        '--no-unlock',
        action='store_false',
        default=True,
        dest='unlock',
        help="Don‘t enter passphrases. Start a interactive shell session after checking instead.",
    )

    return args_parser


def main():
    args_parser = get_args_parser()
    args = args_parser.parse_args()
    if args.loglevel is None:
        args.loglevel = logging.INFO
    logging.basicConfig(
        format='%(levelname)s{}, %(asctime)s: %(message)s'.format(
            ' (%(filename)s:%(lineno)s)' if args.loglevel <= logging.DEBUG else '',
        ),
        level=args.loglevel,
    )

    vault = FileVault()

    unlocker = FdeUnlock(
        vault,
        checkers=get_default_checkers(),
    )
    try:
        unlocker.check_and_unlock(
            args.host,
            unlock=args.unlock,
        )
    except CheckViolation as err:
        raise SystemExit(err)
    except SystemExit:
        sys.exit(0)


if __name__ == '__main__':
    main()
