import argparse
import dataclasses
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List
from typing import Optional as Opt

from . import bundle

WD = Path(os.getcwd())


@dataclass
class CLIParam:
    src: Path
    include_paths: List[Path] = dataclasses.field(
        default_factory=list
    )
    without_empty_line: bool = False


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-I",
        type=str,
        action="append",
        metavar="include_path",
        default=[WD],
        dest="include_paths",
        help="can be set multiple times.",
    )
    parser.add_argument('--without-empty-line', action='store_true')
    g = parser.add_argument_group("required positional")
    g.add_argument(
        "src_file",
        type=str,
        help="e.g. main.cpp",
    )

    args = parser.parse_args()
    include_paths = [
        Path(p).resolve() for p in args.include_paths
    ]
    args = CLIParam(
        Path(args.src_file).resolve(),
        include_paths,
        args.without_empty_line,
    )
    res = bundle(args.src, args.include_paths, args.without_empty_line)
    print(res)



if __name__ == "__main__":
    cli()
