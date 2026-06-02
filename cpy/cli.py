"""
Command-line interface.

    cpy format [paths...]     reformat in place (or stdin -> stdout when given '-')
    cpy check  [paths...]     exit 1 if any file would change; never writes
    cpy diff   [paths...]     print a unified diff of the changes

The stdin/stdout path (``cpy format -``) is the contract the VS Code extension depends on: it reads
the whole buffer from stdin, formats it, and writes the result to stdout without touching disk.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cpy.config import Config, load_config
from cpy.engine.diff import make_diff
from cpy.engine.formatter import format_paths, format_text

#######################################################################################################
# Argument parsing
#

def _build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(prog="cpy", description="CPy — a non-PEP8 personal-style Python formatter.")
    sub    = parser.add_subparsers(dest="command", required=True)

    for name in ("format", "check", "diff"):

        sp = sub.add_parser(name, help=f"{name} Python source")
        sp.add_argument("paths", nargs="*", help="files / directories, or '-' for stdin")
        sp.add_argument("--config", help="path to a pyproject.toml to read configuration from")
        sp.add_argument("--stdin-filename", help="virtual filename used for config discovery when reading stdin")
    #

    return (parser)
#

def _load(args) -> Config:

    if (args.config):

        return (load_config(args.config))
    #
    if (getattr(args, "stdin_filename", None)):

        return (load_config(args.stdin_filename))
    #

    return (load_config(Path.cwd()))
#

def _is_stdin(paths: list[str]) -> bool:

    return (len(paths) == 0  or  paths == ["-"])
#

#######################################################################################################
# Commands
#

def _cmd_stdin(command: str, config: Config) -> int:

    original  = sys.stdin.read()
    formatted = format_text(original, config)

    if (command == "format"):

        sys.stdout.write(formatted)

        return (0)
    #
    if (command == "diff"):

        sys.stdout.write(make_diff(original, formatted))

        return (1 if formatted != original else 0)
    #

    # check
    return (1 if formatted != original else 0)
#

def _cmd_paths(command: str, paths: list[str], config: Config) -> int:

    write   = (command == "format")
    results = format_paths(paths, config, write=write)
    changed = [r for r in results if r.changed]

    if (command == "format"):

        for r in changed:

            print(f"reformatted {r.path}")
        #
        print(f"{len(changed)} file(s) reformatted, {len(results) - len(changed)} unchanged")

        return (0)
    #
    if (command == "diff"):

        for r in changed:

            sys.stdout.write(make_diff(r.original, r.formatted, str(r.path)))
        #

        return (1 if changed else 0)
    #

    # check
    for r in changed:

        print(f"would reformat {r.path}")
    #
    print(f"{len(changed)} file(s) would be reformatted, {len(results) - len(changed)} already clean")

    return (1 if changed else 0)
#

#######################################################################################################
# main
#

def main(argv: list[str] | None = None) -> int:

    args   = _build_parser().parse_args(argv)
    config = _load(args)

    if (_is_stdin(args.paths)):

        return (_cmd_stdin(args.command, config))
    #

    return (_cmd_paths(args.command, args.paths, config))
#

if (__name__ == "__main__"):

    raise SystemExit(main())
#
