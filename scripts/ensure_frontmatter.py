#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#    "python-frontmatter>=1.1.0",
# ]
# ///

import os
import sys
from pathlib import Path

import frontmatter

SKILLS_DIR = Path("../skills/")
FRONTMATTER_KEYS = ("name", "description", "compatibility", "license", "metadata")
METADATA_MINIMUM_KEYS = ("author", "version")


def ensure_frontmatter() -> None:
    skill_files = [
        SKILLS_DIR / d / "SKILL.md"
        for d in os.listdir(SKILLS_DIR)
        if (SKILLS_DIR / d).is_dir() and (SKILLS_DIR / d / "SKILL.md").is_file()
    ]
    for skill_file in skill_files:
        with open(skill_file, "r") as f:
            content = f.read()
            data = frontmatter.loads(content)
            for key in FRONTMATTER_KEYS:
                if data.get(key) is None:
                    print(f"Invalid frontmatter: {key} is missing")
                    sys.exit(1)
                if key == "metadata" and not isinstance(data.get(key), dict):
                    meta = data.get(key)
                    if not isinstance(meta, dict):
                        print("Metadata expected to be a dictionary, but it is not")
                        sys.exit(2)
                    for mk in METADATA_MINIMUM_KEYS:
                        if mk not in meta:
                            print(f"Invalid metada: missing {mk}")
                            sys.exit(3)
    print("All files include the correct frontmatter")
    sys.exit(0)


if __name__ == "__main__":
    ensure_frontmatter()
