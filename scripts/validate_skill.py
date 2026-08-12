#!/usr/bin/env python3
"""Minimal repository-local validation for the skill package."""

from pathlib import Path
import re
import sys

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parents[1] / "skills" / "academic-integrity-rewrite"
    root = root.resolve()
    skill = root / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        print("SKILL.md: missing YAML frontmatter", file=sys.stderr)
        return 1
    lines = [line for line in match.group(1).splitlines() if line.strip()]
    keys = [line.split(":", 1)[0].strip() for line in lines]
    if keys != ["name", "description"]:
        print("SKILL.md: frontmatter must contain only name and description", file=sys.stderr)
        return 1
    if "name: academic-integrity-rewrite" not in match.group(0):
        print("SKILL.md: unexpected skill name", file=sys.stderr)
        return 1
    required = [
        root / "agents" / "openai.yaml",
        root / "scripts" / "audit_revision.py",
        root / "references" / "rewrite-methods.md",
        root / "references" / "quality-gates.md",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
    if missing:
        print("Missing required files: " + ", ".join(missing), file=sys.stderr)
        return 1
    print("Skill package is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
