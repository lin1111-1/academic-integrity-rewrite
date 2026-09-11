# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2026-09-11

### Fixed

- LaTeX `\\cite`, `\\citep`, `\\citet`, and related natbib-style commands are now audited as citations, including optional pre/post notes and year-like citation keys.
- Citation key changes in `.tex` input no longer disappear from the citation report or leak into the content-number audit.

### Added

- Regression coverage for LaTeX citation commands, optional locators, and multiple citation keys.

## [0.2.0] - 2026-09-06

### Added

- Citation audit support for full-width Chinese parentheses, commas, and semicolons in author-year citations, including CJK surnames and page locators.
- Regression coverage for mixed-language and full-width GB/T 7714 author-year citations, including a guard that classifies changed page locators as citation changes rather than numeric-data changes.

### Changed

- Documented the supported mixed-language citation forms and the deliberate limitation for narrative author-year citations, which remain manual-review items to avoid noisy false positives.

## [0.1.1] - 2026-08-28

### Added

- Structured bug report and feature request forms with privacy and academic-integrity safeguards.
- Public roadmap, version targets, and release gates.
- Cross-platform installation instructions and runnable audit examples.
- CI, release, license, and test-status badges in the README.
- Reproducible preserved-fact and changed-number audit examples.
- Anonymous, privacy-safe usage feedback form.
- Transparent adoption evidence and a documented Codex maintenance plan.
- DOCX audit coverage for tables, inline text boxes, footnotes, and endnotes, with documented format limitations.

### Fixed

- Citation auditing now covers APA, IEEE, and GB/T 7714 forms, including page locators and CJK surnames.
- Citation locator changes are reported as citation changes instead of content-number changes.

## [0.1.0] - 2026-08-17

### Added

- Initial release of the bilingual Academic Integrity Rewrite skill for Codex.
- Evidence-preserving rewriting workflow for abstracts, literature reviews, methods, results, discussions, and conclusions.
- Protected-fact ledger for citations, quantitative claims, measurements, formulas, terminology, and document labels.
- Local audit support for TXT, Markdown, and DOCX files.
- Detection of changed numbers, unit-bearing measurements, citation markers, and long overlapping spans.
- Command-line JSON audit report support.
- Regression test suite covering citations, temperature symbols, compound units, and CLI exit behavior.
- GitHub Actions validation across Python 3.10–3.13.
- Contributor, maintainer, security, citation, and code-of-conduct documentation.

### Security

- The audit workflow runs locally and does not transmit manuscript contents.
- Added guidance for handling unpublished manuscripts, similarity reports, personal data, and sensitive security reports.

[Unreleased]: https://github.com/lin1111-1/academic-integrity-rewrite/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/lin1111-1/academic-integrity-rewrite/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/lin1111-1/academic-integrity-rewrite/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/lin1111-1/academic-integrity-rewrite/releases/tag/v0.1.1
[0.1.0]: https://github.com/lin1111-1/academic-integrity-rewrite/releases/tag/v0.1.0
