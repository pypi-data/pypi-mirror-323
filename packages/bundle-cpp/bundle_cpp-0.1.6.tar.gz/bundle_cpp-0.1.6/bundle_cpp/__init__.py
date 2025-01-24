import os
import re
from pathlib import Path
from typing import List
from typing import Optional as Opt

WD = Path(os.getcwd())


def _read(p: Path) -> List[str]:
    with p.open() as f:
        return f.readlines()


def bundle(
    src: Path,
    include_paths: List[Path] = None,
    without_empty_line=False,
) -> str:
    if include_paths is None:
        include_paths = []

    is_once = set()
    edges = set()

    def expand(file: Path) -> str:
        file = file.resolve()
        dir = file.parent

        def find_file(header: str) -> Opt[Path]:
            file = dir / header
            file = file.resolve()
            if file.exists():
                return file
            for d in include_paths:
                file = d / header
                file = file.resolve()
                if file.exists():
                    return file
            return None

        def included_file(line: str) -> Opt[str]:
            ptn = r"^\s*#\s*include\s*\"(.+)\"\s*\n$"
            m = re.match(ptn, line)
            if m is not None:
                header = m.groups()[0]
                return find_file(header)

        def is_pragma_once(line: str) -> bool:
            ptn = r"^\s*#\s*pragma\s+once\s*\n$"
            return re.match(ptn, line) is not None

        def remove_comment(line: str) -> str | None:
            if line == '\n': return '\n'
            i = line.find('//')
            if i != -1: line = line[:i]
            line = line.rstrip()
            if line == '': return None
            return line + '\n'

        lines = _read(file)
        result_lines = []
        for line in lines:
            line = remove_comment(line)
            if line is None: continue
            if is_pragma_once(line):
                is_once.add(file)
                continue
            dep = included_file(line)
            if dep is None:
                result_lines.append(line)
                continue
            if dep in is_once: continue
            e = (file, dep)
            if e in edges: raise "circular includes"
            edges.add(e)
            result_lines.append(expand(dep))
            edges.remove(e)

        res = "".join(result_lines)
        if res == "\n": res = ""
        return res

    res = expand(src)
    if without_empty_line:
        res = '\n'.join(res.rstrip().split('\n'))
    return res
