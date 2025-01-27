import argparse
import logging
import sys
from pathlib import Path

import tosholi

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

try:
    sys.path.remove(str(parent))
except ValueError:
    pass

from bibli_ls.bibli_config import BibliTomlConfig
from bibli_ls.server import SERVER
from bibli_ls import __version__


def cli() -> None:
    """bibli language server cli entrypoint."""
    parser = argparse.ArgumentParser(
        prog="bibli_ls",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Bibli language server.",
        epilog="""\
Examples:

    Run over stdio     : bibli_ls
    Run over tcp       : bibli_ls --tcp
    Run over websockets:
        # only need to pip install once per env
        pip install pygls[ws]
        bibli_ls --ws

Notes:

    For use with web sockets, user must first run
    'pip install pygls[ws]' to install the correct
    version of the websockets library.
""",
    )
    parser.add_argument(
        "--version",
        help="display version information and exit",
        action="store_true",
    )

    parser.add_argument(
        "--default-config",
        help="display the default TOML config",
        action="store_true",
    )

    parser.add_argument(
        "--tcp",
        help="use TCP web server instead of stdio",
        action="store_true",
    )
    parser.add_argument(
        "--ws",
        help="use web socket server instead of stdio",
        action="store_true",
    )
    parser.add_argument(
        "--host",
        help="host for web server (default 127.0.0.1)",
        type=str,
        default="127.0.0.1",
    )
    parser.add_argument(
        "--port",
        help="port for web server (default 2087)",
        type=int,
        default=2087,
    )
    parser.add_argument(
        "--log-file",
        help="redirect logs to file specified",
        type=str,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase verbosity of log output",
        action="count",
        default=0,
    )
    args = parser.parse_args()
    if args.version:
        print(__version__)
        return

    if args.default_config:
        default_config = BibliTomlConfig()
        print(tosholi.dumps(default_config))  # type: ignore
        return

    if args.tcp and args.ws:
        print(
            "Error: --tcp and --ws cannot both be specified",
            file=sys.stderr,
        )
        sys.exit(1)
    log_level = {0: logging.WARN, 1: logging.INFO, 2: logging.DEBUG}.get(
        args.verbose,
        logging.DEBUG,
    )

    if args.log_file:
        logging.basicConfig(
            filename=args.log_file,
            filemode="a",
            level=log_level,
        )
    else:
        logging.basicConfig(stream=sys.stderr, level=log_level)

    if args.tcp:
        SERVER.start_tcp(host=args.host, port=args.port)
    elif args.ws:
        SERVER.start_ws(host=args.host, port=args.port)
    else:
        SERVER.start_io()


if __name__ == "__main__":
    cli()
