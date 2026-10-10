#!/usr/bin/env python3
"""Build downloadable Teacher Document Studio skill and plugin ZIP files."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "teacher-doc-studio"
SKILL = PLUGIN / "skills" / "teacher-doc-studio"
DIST = ROOT / "dist"


def add_tree(archive: ZipFile, source: Path, prefix: Path = Path()) -> None:
    for path in sorted(source.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        archive.write(path, (prefix / path.relative_to(source)).as_posix())


def main() -> None:
    if not (PLUGIN / "plugin.json").is_file():
        raise SystemExit(f"Plugin manifest not found: {PLUGIN / 'plugin.json'}")
    if not (SKILL / "SKILL.md").is_file():
        raise SystemExit(f"Skill instructions not found: {SKILL / 'SKILL.md'}")

    DIST.mkdir(parents=True, exist_ok=True)
    packages = [
        (DIST / "teacher-doc-studio-skill.zip", SKILL, Path()),
        (DIST / "teacher-doc-studio-plugin.zip", PLUGIN, Path()),
    ]
    for target, source, prefix in packages:
        with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
            add_tree(archive, source, prefix)
        print(f"Created {target.relative_to(ROOT)} ({target.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
