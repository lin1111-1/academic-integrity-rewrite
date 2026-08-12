---
name: academic-integrity-rewrite
description: Revise Chinese or English academic writing for lower unnecessary textual overlap while preserving meaning, evidence, numbers, equations, terminology, and citations. Use for 学术论文降重、查重后修改、重复段落重写、paraphrasing, similarity-report remediation, abstracts, literature reviews, methods, results, discussions, theses, and manuscripts in DOCX, Markdown, or plain text. Do not use to disguise plagiarism, fabricate sources, or evade academic-integrity review.
---

# Academic Integrity Rewrite

Rewrite from the research logic and evidence, not by replacing words sentence by sentence. Treat originality as clearer authorship and synthesis, never as detector gaming.

## Establish the task

1. Identify the target language, field, venue or style guide, editable sections, and any similarity report.
2. Distinguish the author's findings from cited ideas, standard definitions, methods that require precise wording, and text that must remain verbatim.
3. If the source or citation evidence is unavailable, mark claims for verification instead of inventing details.
4. State that no exact similarity score can be guaranteed because databases and algorithms differ.

## Triage before rewriting

Classify each flagged passage:

- **P0 — integrity or technical risk:** missing attribution, changed data, equations, labels, units, citations, or unsupported claims. Resolve first.
- **P1 — reasoning risk:** source-by-source summary, weak synthesis, duplicated logic, overclaiming, or a mechanism not supported by the model or data.
- **P2 — expression risk:** formulaic phrasing, noun stacking, repeated sentence frames, vague subjects, or unnecessary metadiscourse.
- **P3 — presentation risk:** inconsistent terms, symbols, figure/table references, citation format, or typography.

Read [references/rewrite-methods.md](references/rewrite-methods.md) for section-specific strategies. Read [references/quality-gates.md](references/quality-gates.md) before final review.

## Build a protected fact ledger

Record, before drafting:

- every number, sign, range, unit, symbol, equation, boundary condition, and named method;
- every citation marker and the claim it supports;
- approved terminology, abbreviations, figure/table/equation numbers, and causal qualifiers;
- direct quotations or legally/academically fixed language that must not be paraphrased.

Never silently change an item in this ledger. Flag contradictions or likely source errors for the author.

## Reconstruct the passage

1. Reduce the passage to an evidence map: purpose → method/evidence → result → interpretation → limitation.
2. Close the source text where practical and draft from that map.
3. Reorder claims by logic, combine redundant sentences, split overloaded sentences, and make the actor or evidence explicit.
4. Synthesize multiple sources by theme, agreement, disagreement, method, chronology, or research gap. Preserve attribution at claim level.
5. Prefer precise verbs and quantified statements. Remove empty frames such as “it is obvious,” “it can be seen,” and repeated announcements of what follows.
6. Preserve necessary technical terms. Do not force synonyms for established concepts.

## Validate

Run the deterministic audit when both original and revision are available:

```bash
python scripts/audit_revision.py ORIGINAL REVISED
```

Use `--json PATH` for a machine-readable report. Treat its warnings as review prompts, not proof of plagiarism or correctness.

Then verify manually:

1. Compare the protected fact ledger against the revision.
2. Check every citation against its supported claim and, when possible, the primary source.
3. Check equations, terminology, abbreviations, units, and cross-references globally.
4. Confirm that interpretations do not exceed the method, model, or data.
5. Read the revision for natural academic flow and field-appropriate tone.

## Deliver

Return:

- the revised passage;
- a concise change rationale grouped by logic, evidence, and expression;
- a verification list for any unresolved facts, citations, or labels;
- an audit summary stating whether numbers and citation markers were preserved and which long shared spans remain.

Do not claim guaranteed acceptance, guaranteed originality, or a guaranteed similarity percentage.
