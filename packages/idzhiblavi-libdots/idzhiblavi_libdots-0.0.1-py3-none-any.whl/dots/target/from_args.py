import argparse

from dots.operation.target import Target

from dots.target.local_target import LocalTarget
from dots.target.noop_target import NoopTarget


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry-run",
        "-D",
        action=argparse.BooleanOptionalAction,
    )

    return parser.parse_args()


def target_from_args() -> Target:
    args = _parse_args()

    if args.dry_run:
        return NoopTarget()

    else:
        return LocalTarget()
