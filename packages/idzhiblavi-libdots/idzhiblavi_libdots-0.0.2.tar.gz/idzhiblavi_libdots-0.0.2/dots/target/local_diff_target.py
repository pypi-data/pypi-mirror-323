import os
import re
import filecmp
import difflib

import aiofile
from loguru import logger

from dots.operation.target import Target
from dots.target import util
from dots.target import log
from dots.util.read_file import read_file


def _make_checker_for_patterns(patterns):
    matchers = [re.compile(p) for p in patterns]

    def matcher(s):
        return any(map(lambda m: bool(m.match(s)), matchers))

    return matcher


async def _print_files_diff(a, b):
    c_a = await read_file(a)
    c_b = await read_file(b)
    return _print_lines_diff(c_a.splitlines(), c_b.splitlines(), a, b)


def _print_lines_diff(a, b, path_a, path_b):
    diff = list(difflib.unified_diff(a, b, path_a, path_b))
    if not diff:
        return

    logger.info(f"files {path_a} and {path_b} differ:")
    print("\n".join(diff))


class LocalDiffTarget(Target):
    async def write_file(self, content: str, path: str):
        util.check_can_put_file(path)

        if not os.path.exists(path):
            path_content = []
        else:
            path_content = await read_file(path)

        _print_lines_diff(
            path_content.splitlines(),
            content.splitlines(),
            path,
            "<generated>",
        )

    async def create_softlink(self, source: str, destination: str):
        if util.softlink_exists(source, destination):
            return

        if os.path.exists(destination):
            logger.info(f"--- remove {destination}")

        logger.info(f"+++ softlink {destination} -> {source}")

    async def copy_file(self, source: str, destination: str):
        util.check_can_put_file(destination)
        _print_files_diff(destination, source)

    async def copy_directory(self, source: str, destination: str, ignore: list[str]):
        util.check_can_put_directory(destination)
        ignored = _make_checker_for_patterns(patterns=ignore)
        not_ignored = lambda p: not ignored(p)
        cmp = filecmp.dircmp(source, destination, shallow=False)

        for p in filter(not_ignored, cmp.diff_files):
            await _print_files_diff(f"{destination}/{p}", f"{source}/{p}")

        for p in filter(not_ignored, cmp.funny_files):
            logger.warning(f"unknown file state, skip: {destination}/{source}")

        for p in filter(not_ignored, cmp.left_only):
            logger.info(f"file will be added: {destination}/{p}")

        for p in filter(not_ignored, cmp.right_only):
            logger.info(f"file will be removed: {destination}/{p}")
