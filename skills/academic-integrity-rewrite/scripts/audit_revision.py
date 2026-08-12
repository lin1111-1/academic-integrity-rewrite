#!/usr/bin/env python3
"""Audit factual tokens and long shared spans between an original and a revision."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
NUMBER_RE = re.compile(r"(?<![\w.])[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:\s*[–—-]\s*[+-]?\d+(?:\.\d+)?)?\s*%?")
BRACKET_CITATION_RE = re.compile(r"\[(?:\d+[a-z]?\s*(?:[-–,;]\s*\d+[a-z]?\s*)*)\]", re.I)
AUTHOR_YEAR_RE = re.compile(r"\((?:[A-Z][A-Za-z'’-]+(?:\s+et\s+al\.)?[^()]{0,60}?\b(?:19|20)\d{2}[a-z]?)(?:\s*;[^()]+)?\)")
TOKEN_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*|\d+(?:\.\d+)?|[\u3400-\u9fff]")


def read_text(path: Path) -> str:
    if path.suffix.lower() != ".docx":
        return path.read_text(encoding="utf-8")
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    paragraphs = []
    for paragraph in root.iter(WORD_NS + "p"):
        text = "".join(node.text or "" for node in paragraph.iter(WORD_NS + "t"))
        if text.strip():
            paragraphs.append(text)
    return "\n".join(paragraphs)


def normalized_items(pattern: re.Pattern[str], text: str) -> Counter[str]:
    return Counter(re.sub(r"\s+", "", item) for item in pattern.findall(text))


def tokenise(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def without_citations(text: str) -> str:
    for pattern in (BRACKET_CITATION_RE, AUTHOR_YEAR_RE):
        text = pattern.sub(" ", text)
    return text


def shared_spans(original: str, revised: str, width: int, limit: int) -> list[str]:
    left, right = tokenise(original), tokenise(revised)
    if len(left) < width or len(right) < width:
        return []
    right_grams = {tuple(right[i : i + width]) for i in range(len(right) - width + 1)}
    found: list[str] = []
    seen: set[tuple[str, ...]] = set()
    for index in range(len(left) - width + 1):
        gram = tuple(left[index : index + width])
        if gram in right_grams and gram not in seen:
            seen.add(gram)
            found.append(" ".join(gram))
            if len(found) >= limit:
                break
    return found


def counter_diff(expected: Counter[str], actual: Counter[str]) -> dict[str, int]:
    return dict(sorted((expected - actual).items()))


def audit(original: str, revised: str, ngram: int, limit: int) -> dict[str, object]:
    original_numbers = normalized_items(NUMBER_RE, without_citations(original))
    revised_numbers = normalized_items(NUMBER_RE, without_citations(revised))
    original_citations = normalized_items(BRACKET_CITATION_RE, original) + normalized_items(AUTHOR_YEAR_RE, original)
    revised_citations = normalized_items(BRACKET_CITATION_RE, revised) + normalized_items(AUTHOR_YEAR_RE, revised)
    spans = shared_spans(original, revised, ngram, limit)
    return {
        "numbers": {
            "missing_or_reduced": counter_diff(original_numbers, revised_numbers),
            "added_or_increased": counter_diff(revised_numbers, original_numbers),
        },
        "citations": {
            "missing_or_reduced": counter_diff(original_citations, revised_citations),
            "added_or_increased": counter_diff(revised_citations, original_citations),
        },
        "shared_spans": {"ngram_width": ngram, "count_shown": len(spans), "items": spans},
        "notes": [
            "A warning may be legitimate; review it against the protected fact ledger.",
            "No lexical audit can prove originality, attribution, or scientific correctness.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("revised", type=Path)
    parser.add_argument("--ngram", type=int, default=10, help="Token width for shared-span detection")
    parser.add_argument("--limit", type=int, default=25, help="Maximum shared spans to show")
    parser.add_argument("--json", type=Path, help="Also save the JSON report to this path")
    args = parser.parse_args()
    if args.ngram < 3:
        parser.error("--ngram must be at least 3")
    report = audit(read_text(args.original), read_text(args.revised), args.ngram, args.limit)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json:
        args.json.write_text(rendered + "\n", encoding="utf-8")
    has_fidelity_warning = any(report[key][kind] for key in ("numbers", "citations") for kind in ("missing_or_reduced", "added_or_increased"))
    return 1 if has_fidelity_warning else 0


if __name__ == "__main__":
    sys.exit(main())
