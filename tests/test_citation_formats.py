"""Citation-format regression coverage for APA, IEEE and GB/T 7714.

Every fixture below is synthetic. No real manuscript, author, or personal data
appears here; surnames are placeholders and the DOI prefix 10.1000 is the
IANA-reserved example prefix.

Why these tests exist in this shape
-----------------------------------
`audit()` calls `without_citations()` *before* it counts numbers. That ordering
means a citation the patterns fail to match is never stripped, and its page and
year numbers are then counted as **content** numbers. A missed citation is
therefore not a silent gap -- it actively misfiles a citation edit as a data
error, which is the one confusion this tool exists to prevent.

So the negative tests here assert both halves: that an altered citation is
reported under `citations`, *and* that it is not reported under `numbers`.
"""

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "skills"
    / "academic-integrity-rewrite"
    / "scripts"
    / "audit_revision.py"
)
SPEC = importlib.util.spec_from_file_location("audit_revision", MODULE_PATH)
audit_revision = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(audit_revision)


# (label, text, expected number of citations recognised)
BRACKETED_FIXTURES = [
    ("ieee single", "The effect is well established [1].", 1),
    ("ieee multiple separate", "Three studies agree [1], [2], [5].", 3),
    ("ieee grouped", "Three studies agree [1, 2, 5].", 1),
    ("ieee semicolon group", "Two studies agree [1; 2].", 1),
    ("ieee en dash range", "A range of work [1–3] applies.", 1),
    ("ieee hyphen range", "A range of work [4-6] applies.", 1),
    ("ieee letter suffix", "A revised entry [7a] applies.", 1),
    ("gbt chinese sentence", "研究表明[1]，该方法有效。", 1),
    ("gbt chinese range", "多项研究[1-3]支持这一结论。", 1),
    ("gbt chinese list", "参见[1,5,7]。", 1),
    ("gbt mixed language", "As 张 notes [2], the trend holds 。", 1),
]

AUTHOR_YEAR_FIXTURES = [
    ("apa basic", "The trend holds (Placeholder, 2020).", 1),
    ("apa ampersand", "The trend holds (Placeholder & Example, 2020).", 1),
    ("apa et al", "The trend holds (Placeholder et al., 2020).", 1),
    ("apa year letter", "The trend holds (Placeholder, 2020a).", 1),
    ("apa two citations", "The trend holds (Placeholder, 2020; Example, 2019).", 1),
    ("apa page locator", "The trend holds (Placeholder, 2020, p. 15).", 1),
    ("apa page range locator", "The trend holds (Placeholder, 2020, pp. 15-17).", 1),
    ("apa en dash page range", "The trend holds (Placeholder, 2020, pp. 15–17).", 1),
    ("apa german locator", "The trend holds (Placeholder, 2020, S. 20).", 1),
    ("gbt cjk surname", "趋势成立 (张, 2020)。", 1),
    ("gbt cjk surname locator", "趋势成立 (张伟, 2020, 第15页)。", 1),
    ("gbt full-width punctuation", "趋势成立（张伟，2020，第15页）。", 1),
    ("mixed-language full-width citation", "As Zhang notes（张伟，2020；Example, 2019），the trend holds.", 1),
]

# Parenthesised text that must NOT be read as a citation. A pattern loose
# enough to catch narrative citations would swallow most of these.
NON_CITATION_FIXTURES = [
    ("bare year in prose", "The reactor (2020) was recommissioned."),
    ("cross reference", "The results are shown (see Table 2)."),
    ("parenthetical aside", "The yield (measured twice) was stable."),
    ("units in parentheses", "The mass (in kg) was recorded."),
]


class BracketedCitationTests(unittest.TestCase):
    """IEEE and GB/T 7714 numeric citations, in English and Chinese text."""

    def test_bracketed_forms_are_recognised(self):
        for label, text, expected in BRACKETED_FIXTURES:
            with self.subTest(label):
                found = audit_revision.BRACKET_CITATION_RE.findall(text)
                self.assertEqual(len(found), expected, f"{label}: got {found}")


class LatexCitationTests(unittest.TestCase):
    """Natbib-style LaTeX citations are audited as protected citations."""

    def test_latex_commands_are_recognised(self):
        text = r"See \citep{Placeholder2020} and \citet[see][p. 15]{Example2021}."
        self.assertEqual(
            audit_revision.LATEX_CITATION_RE.findall(text),
            [r"\citep{Placeholder2020}", r"\citet[see][p. 15]{Example2021}"],
        )

    def test_changed_latex_key_is_a_citation_change_not_a_number_change(self):
        result = audit_revision.audit(
            r"The result was retained in \citep{Placeholder2020}.",
            r"The result was retained in \citep{Example2021}.",
            4,
            10,
        )
        self.assertIn(r"\citep{Placeholder2020}", result["citations"]["missing_or_reduced"])
        self.assertIn(r"\citep{Example2021}", result["citations"]["added_or_increased"])
        self.assertEqual(result["numbers"]["missing_or_reduced"], {})
        self.assertEqual(result["numbers"]["added_or_increased"], {})

    def test_latex_citation_notes_and_multiple_keys_are_preserved(self):
        result = audit_revision.audit(
            r"The result was retained in \citep[see][p. 15]{Placeholder2020,Other2019}.",
            r"The retained result is reported in \citep[see][p. 15]{Placeholder2020,Other2019}.",
            4,
            10,
        )
        self.assertEqual(result["citations"]["missing_or_reduced"], {})
        self.assertEqual(result["citations"]["added_or_increased"], {})
        self.assertEqual(result["numbers"]["missing_or_reduced"], {})
        self.assertEqual(result["numbers"]["added_or_increased"], {})


class AuthorYearCitationTests(unittest.TestCase):
    """APA author-year citations, including locators and CJK surnames."""

    def test_author_year_forms_are_recognised(self):
        for label, text, expected in AUTHOR_YEAR_FIXTURES:
            with self.subTest(label):
                found = audit_revision.AUTHOR_YEAR_RE.findall(text)
                self.assertEqual(len(found), expected, f"{label}: got {found}")

    def test_ordinary_parentheses_are_not_citations(self):
        for label, text in NON_CITATION_FIXTURES:
            with self.subTest(label):
                self.assertEqual(audit_revision.AUTHOR_YEAR_RE.findall(text), [])

    def test_narrative_citation_is_a_documented_limitation(self):
        """`Placeholder (2020) showed ...` is knowingly not matched.

        Recognising it means matching a bare `(2020)` and deciding from the
        preceding token whether it is an author, which false-positives on
        prose like "the reactor (2020)" above. This test records the
        limitation rather than hiding it: if narrative support is added
        later, this test is the one that should change, deliberately.
        """
        text = "Placeholder (2020) showed the same effect."
        self.assertEqual(audit_revision.AUTHOR_YEAR_RE.findall(text), [])


class PreservedCitationTests(unittest.TestCase):
    """Positive cases: a faithful rewrite must raise nothing."""

    def _assert_clean(self, original, revised):
        result = audit_revision.audit(original, revised, 4, 10)
        self.assertEqual(result["citations"]["missing_or_reduced"], {})
        self.assertEqual(result["citations"]["added_or_increased"], {})
        self.assertEqual(result["numbers"]["missing_or_reduced"], {})
        self.assertEqual(result["numbers"]["added_or_increased"], {})

    def test_reordered_sentence_preserves_bracketed_citation(self):
        self._assert_clean(
            "At 450 K the yield reached 1.41 [12].",
            "A yield of 1.41 was reached at 450 K [12].",
        )

    def test_reordered_sentence_preserves_apa_locator_citation(self):
        # The case that used to leak `15` into the number audit.
        self._assert_clean(
            "The catalyst yielded 42 units (Placeholder, 2020, p. 15).",
            "Yields of 42 units were observed (Placeholder, 2020, p. 15).",
        )

    def test_reordered_sentence_preserves_chinese_citation(self):
        self._assert_clean(
            "在450 K下，产率为1.41[12]。",
            "产率为1.41，温度为450 K[12]。",
        )

    def test_multiple_citations_survive_reordering(self):
        self._assert_clean(
            "Both results agree [1], [2] and so does the model (Placeholder, 2019).",
            "The model agrees (Placeholder, 2019), as do both results [1], [2].",
        )

    def test_doi_is_not_counted_as_content_numbers(self):
        # A DOI is not a citation pattern, but it must survive unchanged and
        # must not produce a spurious number diff when the sentence moves.
        original = "Data are archived at 10.1000/182 and were checked twice."
        revised = "Checked twice, the data are archived at 10.1000/182."
        result = audit_revision.audit(original, revised, 4, 10)
        self.assertEqual(result["numbers"]["missing_or_reduced"], {})
        self.assertEqual(result["numbers"]["added_or_increased"], {})


class AlteredCitationTests(unittest.TestCase):
    """Negative cases: a changed citation must be detected, and detected
    as a *citation* change rather than a number one."""

    def test_dropped_bracketed_citation_is_reported(self):
        result = audit_revision.audit(
            "The effect is established [1], [2].",
            "The effect is established [1].",
            4,
            10,
        )
        self.assertIn("[2]", result["citations"]["missing_or_reduced"])

    def test_renumbered_citation_is_reported(self):
        result = audit_revision.audit(
            "The effect is established [12].",
            "The effect is established [13].",
            4,
            10,
        )
        self.assertIn("[12]", result["citations"]["missing_or_reduced"])
        self.assertIn("[13]", result["citations"]["added_or_increased"])

    def test_edited_page_locator_is_a_citation_change_not_a_number_change(self):
        """The regression this file was written for.

        Before the locator tail was added to AUTHOR_YEAR_RE, this reported
        `{}` under citations and `15 -> 15-16` under numbers: a citation edit
        arriving as a data error, sending a reviewer looking for the wrong
        kind of problem.
        """
        result = audit_revision.audit(
            "Yield was 42 units (Placeholder, 2020, p. 15).",
            "Yield was 42 units (Placeholder, 2020, pp. 15-16).",
            4,
            10,
        )
        self.assertIn("(Placeholder,2020,p.15)", result["citations"]["missing_or_reduced"])
        self.assertIn(
            "(Placeholder,2020,pp.15-16)", result["citations"]["added_or_increased"]
        )
        self.assertEqual(result["numbers"]["missing_or_reduced"], {})
        self.assertEqual(result["numbers"]["added_or_increased"], {})

    def test_changed_citation_year_is_reported(self):
        result = audit_revision.audit(
            "The trend holds (Placeholder, 2020).",
            "The trend holds (Placeholder, 2021).",
            4,
            10,
        )
        self.assertIn("(Placeholder,2020)", result["citations"]["missing_or_reduced"])
        self.assertIn("(Placeholder,2021)", result["citations"]["added_or_increased"])

    def test_full_width_locator_change_is_a_citation_change_not_a_number_change(self):
        result = audit_revision.audit(
            "该结论与证据一致（张伟，2020，第15页）。",
            "该结论与证据一致（张伟，2020，第16页）。",
            4,
            10,
        )
        self.assertIn("（张伟，2020，第15页）", result["citations"]["missing_or_reduced"])
        self.assertIn("（张伟，2020，第16页）", result["citations"]["added_or_increased"])
        self.assertEqual(result["numbers"]["missing_or_reduced"], {})
        self.assertEqual(result["numbers"]["added_or_increased"], {})

    def test_dropped_chinese_citation_is_reported(self):
        result = audit_revision.audit(
            "多项研究[1-3]支持这一结论。",
            "多项研究支持这一结论。",
            4,
            10,
        )
        self.assertIn("[1-3]", result["citations"]["missing_or_reduced"])

    def test_a_real_number_change_is_still_reported_alongside_citations(self):
        # The two audits must stay independent: fixing the citation leak must
        # not make genuine data changes harder to see.
        result = audit_revision.audit(
            "Yield was 42 units (Placeholder, 2020, p. 15).",
            "Yield was 47 units (Placeholder, 2020, p. 15).",
            4,
            10,
        )
        self.assertIn("42", result["numbers"]["missing_or_reduced"])
        self.assertIn("47", result["numbers"]["added_or_increased"])
        self.assertEqual(result["citations"]["missing_or_reduced"], {})


if __name__ == "__main__":
    unittest.main()
