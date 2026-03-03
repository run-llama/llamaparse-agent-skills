#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
import argparse
import json
import sys
from pathlib import Path

METADATA_FILE = Path("../metadata.json")


def add_skill(skill: str, version: str, author: str) -> None:
    with open(METADATA_FILE, "r") as f:
        data = json.load(f)
    if skill not in data:
        data[skill] = {"version": version, "author": author}
        with open(METADATA_FILE, "w") as f:
            content = json.dumps(data, indent=2) + "\n"
            f.write(content)
        sys.exit(0)
    else:
        print(f"Skill {skill} already in metadata.json")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill", help="Name of the skill to add", type=str)
    parser.add_argument(
        "-a",
        "--author",
        help="Author of the skill. Defaults to LlamaIndex",
        type=str,
        required=False,
        default="LlamaIndex",
    )
    parser.add_argument(
        "-v",
        "--version",
        help="Version of the skill. Defaults to 0.1.0",
        type=str,
        required=False,
        default="0.1.0",
    )
    args = parser.parse_args()
    add_skill(args.skill, author=args.author, version=args.version)


if __name__ == "__main__":
    main()
