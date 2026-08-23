# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Structured bug report and feature request forms with privacy and academic-integrity safeguards.
- Public roadmap, version targets, and release gates.
- Cross-platform installation instructions and runnable audit examples.
- CI, release, license, and test-status badges in the README.
- Reproducible preserved-fact and changed-number audit examples.
- Anonymous, privacy-safe usage feedback form.
- Transparent adoption evidence and a documented Codex maintenance plan.

## [0.1.0] - 2026-08-17

### Added

- Initial release of the bilingual Academic Integrity Rewrite skill for Codex.
- Evidence-preserving rewriting workflow for abstracts, literature reviews, methods, results, discussions, and conclusions.
- Protected-fact ledger for citations, quantitative claims, measurements, formulas, terminology, and document labels.
- Local audit support for `.txt`, `.md`, and `.docx` files.
- Detection of changed numbers, unit-bearing measurements, citation markers, and long overlapping spans.
- Command-line JSON audit report support.
- Regression test suite covering citations, temperature symbols, compound units, and CLI exit behavior.
- GitHub Actions validation across Python 3.10–3.13.
- Contributor, maintainer, security, citation, and code-of-conduct documentation.

### Security

- The audit workflow runs locally and does not transmit manuscript contents.
- Added guidance for handling unpublished manuscripts, similarity reports, personal data, and sensitive security reports.

[Unreleased]: https://github.com/lin1111-1/academic-integrity-rewrite/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/lin1111-1/academic-integrity-rewrite/releases/tag/v0.1.0
