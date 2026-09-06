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
MC_NS = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"
DOCX_TEXT_PARTS = (
    "word/document.xml",
    "word/footnotes.xml",
    "word/endnotes.xml",
)
NUMBER_RE = re.compile(r"(?<![\w.])[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:\s*[–—-]\s*[+-]?\d+(?:\.\d+)?)?\s*%?")
MEASUREMENT_RE = re.compile(
    r"(?<![\w.])[+-]?(?:\d+(?:\.\d+)?|\.\d+)"
    r"(?:\s*[–—-]\s*[+-]?(?:\d+(?:\.\d+)?|\.\d+))?"
    r"\s*(?:%|°\s*[CF]|℃|℉|[kMGTcmµμnp]?"
    r"(?:m|g|s|A|K|mol|cd|Hz|Pa|J|W|V|F|Ω|S|T|H|L|l)"
    r"(?:\s*(?:[·⋅*/]|\s)\s*[kMGTcmµμnp]?"
    r"(?:m|g|s|A|K|mol|cd|Hz|Pa|J|W|V|F|Ω|S|T|H|L|l))?"
    r"(?:\s*(?:\^\s*)?[−-]?\d+)?)(?![\w])",
)
BRACKET_CITATION_RE = re.compile(r"\[(?:\d+[a-z]?\s*(?:[-–,;]\s*\d+[a-z]?\s*)*)\]", re.I)
# An author-year citation, optionally with a locator after the year.
#
# The locator tail matters more than it looks: `audit()` strips citations
# before counting numbers, so a citation this pattern misses leaks its page
# numbers into the *content* number audit. Before the tail was allowed,
# `(Smith, 2020, p. 15)` -> `(Smith, 2020, pp. 15-16)` reported nothing under
# citations and `15 -> 15-16` under numbers -- a citation edit misfiled as a
# data error, which is the one confusion this tool exists to prevent.
#
# The surname alternative accepts a CJK character as well as a capital, for
# GB/T 7714 documents that use author-year with Chinese surnames. The
# delimiters and separators also accept their full-width Chinese equivalents:
# Word documents and Chinese-language manuscripts commonly use `（张伟，2020）`.
#
# Narrative citations (`Smith (2020) showed ...`) are deliberately NOT matched.
# Recognising them means matching a bare `(2020)` and deciding from the
# preceding token whether it is an author, which false-positives on ordinary
# prose such as "the reactor (2020)". A documented miss is safer here than a
# noisy detector: see test_narrative_citation_is_a_documented_limitation.
AUTHOR_YEAR_RE = re.compile(
    r"[（(](?:(?:[A-Z][A-Za-z'’-]+|[㐀-鿿]{1,4})(?:\s+et\s+al\.)?"
    r"[^()（）]{0,60}?(?:19|20)\d{2}[a-z]?)"
    # Locator: `, p. 15`, `, pp. 15-17`, `, 第15页`, `, S. 20`.
    r"(?:\s*[,，]\s*(?:pp?\.|S\.|第)?\s*\d+(?:\s*[-–—]\s*\d+)?\s*页?)?"
    r"(?:\s*[;；][^()（）]+)?[)）]"
)
TOKEN_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*|\d+(?:\.\d+)?|[\u3400-\u9fff]")


def iter_paragraphs(root: ET.Element):
    if root.tag == MC_NS + "AlternateContent":
        choices = [child for child in root if child.tag == MC_NS + "Choice"]
        fallbacks = [child for child in root if child.tag == MC_NS + "Fallback"]
        branches = choices + fallbacks
        if branches:
            branch = next(
                (
                    item
                    for item in branches
                    if any((text.text or "").strip() for text in item.iter(WORD_NS + "t"))
                ),
                branches[0],
            )
            yield from iter_paragraphs(branch)
        return
    if root.tag == WORD_NS + "p":
        yield root
    for child in root:
        yield from iter_paragraphs(child)


def paragraph_text(paragraph: ET.Element) -> str:
    pieces: list[str] = []

    def collect(node: ET.Element) -> None:
        for child in node:
            if child.tag == WORD_NS + "p":
                continue
            if child.tag == WORD_NS + "t":
                pieces.append(child.text or "")
            else:
                collect(child)

    collect(paragraph)
    return "".join(pieces)


def read_text(path: Path) -> str:
    if path.suffix.lower() != ".docx":
        return path.read_text(encoding="utf-8")
    with zipfile.ZipFile(path) as archive:
        available_parts = set(archive.namelist())
        parts = [ET.fromstring(archive.read(DOCX_TEXT_PARTS[0]))]
        parts.extend(
            ET.fromstring(archive.read(name))
            for name in DOCX_TEXT_PARTS[1:]
            if name in available_parts
        )
    paragraphs = []
    for root in parts:
        for paragraph in iter_paragraphs(root):
            text = paragraph_text(paragraph)
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
    original_without_citations = without_citations(original)
    revised_without_citations = without_citations(revised)
    original_numbers = normalized_items(NUMBER_RE, original_without_citations)
    revised_numbers = normalized_items(NUMBER_RE, revised_without_citations)
    original_measurements = normalized_items(MEASUREMENT_RE, original_without_citations)
    revised_measurements = normalized_items(MEASUREMENT_RE, revised_without_citations)
    original_citations = normalized_items(BRACKET_CITATION_RE, original) + normalized_items(AUTHOR_YEAR_RE, original)
    revised_citations = normalized_items(BRACKET_CITATION_RE, revised) + normalized_items(AUTHOR_YEAR_RE, revised)
    spans = shared_spans(original, revised, ngram, limit)
    return {
        "numbers": {
            "missing_or_reduced": counter_diff(original_numbers, revised_numbers),
            "added_or_increased": counter_diff(revised_numbers, original_numbers),
        },
        "measurements": {
            "missing_or_reduced": counter_diff(original_measurements, revised_measurements),
            "added_or_increased": counter_diff(revised_measurements, original_measurements),
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
    has_fidelity_warning = any(
        report[key][kind]
        for key in ("numbers", "measurements", "citations")
        for kind in ("missing_or_reduced", "added_or_increased")
    )
    return 1 if has_fidelity_warning else 0


if __name__ == "__main__":
    sys.exit(main())
