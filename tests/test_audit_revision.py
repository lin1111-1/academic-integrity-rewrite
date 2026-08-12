import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "skills" / "academic-integrity-rewrite" / "scripts" / "audit_revision.py"
SPEC = importlib.util.spec_from_file_location("audit_revision", MODULE_PATH)
audit_revision = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(audit_revision)


class AuditRevisionTests(unittest.TestCase):
    def test_preserved_numbers_and_citations(self):
        original = "At Re = 450, efficiency was 1.41 [12]."
        revised = "The measured efficiency reached 1.41 when Re = 450 [12]."
        result = audit_revision.audit(original, revised, 4, 10)
        self.assertEqual(result["numbers"]["missing_or_reduced"], {})
        self.assertEqual(result["numbers"]["added_or_increased"], {})
        self.assertEqual(result["citations"]["missing_or_reduced"], {})

    def test_changed_number_is_reported(self):
        result = audit_revision.audit("The gain was 4.43% [2].", "The gain was 4.34% [2].", 4, 10)
        self.assertIn("4.43%", result["numbers"]["missing_or_reduced"])
        self.assertIn("4.34%", result["numbers"]["added_or_increased"])

    def test_citation_number_is_not_double_counted(self):
        result = audit_revision.audit("Prior work [12] agrees.", "Prior work agrees.", 4, 10)
        self.assertEqual(result["numbers"]["missing_or_reduced"], {})
        self.assertIn("[12]", result["citations"]["missing_or_reduced"])

    def test_reads_docx_without_third_party_packages(self):
        document_xml = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>Preserved 1.41 [3].</w:t></w:r></w:p></w:body>
</w:document>'''
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", document_xml)
            self.assertEqual(audit_revision.read_text(path), "Preserved 1.41 [3].")


if __name__ == "__main__":
    unittest.main()
