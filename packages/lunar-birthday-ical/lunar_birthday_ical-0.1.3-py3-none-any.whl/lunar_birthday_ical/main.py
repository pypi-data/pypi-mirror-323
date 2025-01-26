#!/usr/bin/env python3
# author: ak1ra
# date: 2025-01-24
# python3 -m pip install PyYAML icalendar lunar_python
# https://github.com/collective/icalendar
# https://github.com/6tail/lunar-python

import argparse
import time
from pathlib import Path

import yaml

from lunar_birthday_ical.ical import create_calendar
from lunar_birthday_ical.utils import get_logger

logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate iCal events for lunar birthday and cycle days."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="input config.yaml, check config/example-lunar-birthday.yaml for example.",
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="Path to save the generated iCal file."
    )

    args = parser.parse_args()
    config_file = Path(args.input)
    if not args.output:
        output = config_file.with_suffix(".ics")
    else:
        output = Path(args.output)

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    start = time.perf_counter()
    create_calendar(config, output)
    elapsed = time.perf_counter() - start
    logger.debug("iCal generation elapsed at %.6fs", elapsed)


if __name__ == "__main__":
    main()
