#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#    "python-frontmatter>=1.1.0",
# ]
# ///
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Literal, NamedTuple

import frontmatter

SKILLS_DIR = Path("../skills/")
METADATA_FILE = Path("../metadata.json")

BumpType = Literal["patch", "minor", "major"]


class Version(NamedTuple):
    major: int
    minor: int
    patch: int


def _load_version_from_json(skill: str) -> tuple[str, dict[str, Any]]:
    with open(METADATA_FILE, "r") as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert skill in data
    assert "version" in data[skill]
    assert isinstance(data[skill]["version"], str)
    return data[skill]["version"], data


def _load_version_from_frontmatter(skill_file: str) -> tuple[str, str]:
    with open(skill_file, "r") as f:
        content = f.read()
        data = frontmatter.loads(content)
        meta = data.get("metadata")
        assert isinstance(meta, dict)
        assert "version" in meta
        assert isinstance(meta["version"], str)
        return meta["version"], content


def _parse_semver(version: str) -> Version:
    sep = version.split(".")
    assert len(sep) == 3
    assert all(s.isdigit() for s in sep)
    return Version(major=int(sep[0]), minor=int(sep[1]), patch=int(sep[2]))


def _compare_semver(v1: Version, v2: Version) -> bool:
    return v1.major == v2.major and v1.minor == v2.minor and v1.patch == v2.patch


def _semver_to_str(v: Version) -> str:
    return f"{v.major}.{v.minor}.{v.patch}"


def _bump_semver(version: Version, bump_type: BumpType) -> str:
    major = version.major
    minor = version.minor
    patch = version.patch
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    return _semver_to_str(Version(major=major, minor=minor, patch=patch))


def bump_version(skill: str, bump_type: BumpType) -> None:
    if not (SKILLS_DIR / skill / "SKILL.md").is_file():
        print(f"No such file: {str((SKILLS_DIR / skill / 'SKILL.md'))}")
        sys.exit(1)

    frontmatter_ver, content = _load_version_from_frontmatter(
        str(SKILLS_DIR / skill / "SKILL.md")
    )
    json_ver, data = _load_version_from_json(skill)

    frontmatter_semver = _parse_semver(frontmatter_ver)
    json_semver = _parse_semver(json_ver)

    if not _compare_semver(frontmatter_semver, json_semver):
        print(
            f"Version from metadata.json and frontmatter do not match: {json_ver} VS {frontmatter_ver}"
        )
        sys.exit(2)

    new_ver = _bump_semver(json_semver, bump_type)
    data[skill]["version"] = new_ver

    with open(METADATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    new_content = content.replace(
        f'version: "{frontmatter_ver}"', f'version: "{new_ver}"'
    )
    with open(SKILLS_DIR / skill / "SKILL.md", "w") as f:
        f.write(new_content)

    print(f"Bumped version: {json_ver} -> {new_ver}")


def get_version(skill: str) -> None:
    if not (SKILLS_DIR / skill / "SKILL.md").is_file():
        print(f"No such file: {str((SKILLS_DIR / skill / 'SKILL.md'))}")
        sys.exit(1)

    frontmatter_ver, _ = _load_version_from_frontmatter(
        str(SKILLS_DIR / skill / "SKILL.md")
    )
    json_ver, _ = _load_version_from_json(skill)

    frontmatter_semver = _parse_semver(frontmatter_ver)
    json_semver = _parse_semver(json_ver)

    if not _compare_semver(frontmatter_semver, json_semver):
        print(
            f"Version mismatch! metadata.json: {json_ver}, frontmatter: {frontmatter_ver}"
        )
        sys.exit(2)

    print(json_ver)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage skill versions across metadata.json and SKILL.md frontmatter.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # bump subcommand
    bump_parser = subparsers.add_parser(
        "bump",
        help="Bump the version of a skill.",
    )
    bump_parser.add_argument(
        "skill",
        type=str,
        help="Name of the skill to bump (must exist under ../skills/<skill>/SKILL.md).",
    )
    bump_parser.add_argument(
        "bump_type",
        choices=["patch", "minor", "major"],
        help="Type of version bump to perform.",
    )

    # get subcommand
    get_parser = subparsers.add_parser(
        "get",
        help="Print the current version of a skill.",
    )
    get_parser.add_argument(
        "skill",
        type=str,
        help="Name of the skill to query.",
    )

    args = parser.parse_args()

    if args.command == "bump":
        bump_version(args.skill, args.bump_type)
    elif args.command == "get":
        get_version(args.skill)


if __name__ == "__main__":
    main()
