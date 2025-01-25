"""DoHome CLI entrypoint"""
import logging
from arrrgs import arg, command, global_args, run

from .light import turn_on, turn_off, set_color, set_white
from .describe import describe
from .discover import discover

global_args(
    arg('--hosts', '-d',
        default="all", help="Device hosts separated by comma. Default: all"),
    arg("--timeout", "-t",
        type=float, default=0.3, help="Discovery timeout in seconds"),
    arg("--debug", "-D",
        action="store_true", help="Enable debug logging")
)

def _prepare(args):
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    return args, None


def start():
    """Application entrypoint"""
    run(prepare=_prepare)
