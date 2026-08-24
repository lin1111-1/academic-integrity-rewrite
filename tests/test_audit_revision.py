import importlib.util
import io
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).parents[1] / "skills" / "academic-integrity-rewrite" / "scripts" / "audit_revision.py"
SPEC = importlib.util.spec_from_file_location("audit_revision", MODULE_PATH)
audit_revision = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(audit_revision)


class AuditRevisionTests(unittest.TestCase):
    def write_docx(self, path, document_xml, **additional_parts):
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", document_xml)
            for name, content in additional_parts.items():
                archive.writestr(f"word/{name}.xml", content)

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

    def test_changed_unit_is_reported(self):
        result = audit_revision.audit("The specimen was heated to 450 K.", "The specimen was heated to 450 °C.", 4, 10)
        self.assertIn("450K", result["measurements"]["missing_or_reduced"])
        self.assertIn("450°C", result["measurements"]["added_or_increased"])

    def test_equivalent_unit_spacing_is_ignored(self):
        result = audit_revision.audit("The speed was 12 m s−1.", "A speed of 12 m s−1 was measured.", 4, 10)
        self.assertEqual(result["measurements"]["missing_or_reduced"], {})
        self.assertEqual(result["measurements"]["added_or_increased"], {})

    def test_symbol_unit_is_reported(self):
        result = audit_revision.audit("温度为 37 ℃。", "温度为 37 ℉。", 4, 10)
        self.assertIn("37℃", result["measurements"]["missing_or_reduced"])
        self.assertIn("37℉", result["measurements"]["added_or_increased"])

    def test_cli_returns_warning_for_changed_unit(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "original.txt"
            revised = Path(directory) / "revised.txt"
            original.write_text("The specimen was heated to 450 K.", encoding="utf-8")
            revised.write_text("The specimen was heated to 450 °C.", encoding="utf-8")
            with mock.patch("sys.argv", ["audit_revision.py", str(original), str(revised)]):
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(audit_revision.main(), 1)

    def test_citation_number_is_not_double_counted(self):
        result = audit_revision.audit("Prior work [12] agrees.", "Prior work agrees.", 4, 10)
        self.assertEqual(result["numbers"]["missing_or_reduced"], {})
        self.assertIn("[12]", result["citations"]["missing_or_reduced"])

    def test_citation_with_unit_like_text_is_not_a_measurement(self):
        result = audit_revision.audit("Prior work [12] agrees.", "Prior work agrees.", 4, 10)
        self.assertEqual(result["measurements"]["missing_or_reduced"], {})

    def test_reads_docx_without_third_party_packages(self):
        document_xml = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>Preserved 1.41 [3].</w:t></w:r></w:p></w:body>
</w:document>'''
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.docx"
            self.write_docx(path, document_xml)
            self.assertEqual(audit_revision.read_text(path), "Preserved 1.41 [3].")

    def test_reads_docx_tables_text_boxes_footnotes_and_endnotes(self):
        document_xml = b'''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">
  <w:body>
    <w:tbl><w:tr><w:tc><w:p><w:r><w:t>Table value 42 kg [7].</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
    <w:p><w:r><mc:AlternateContent>
      <mc:Choice Requires="wps"><w:drawing><w:txbxContent><w:p><w:r><w:t>Text box 12.5% [8].</w:t></w:r></w:p></w:txbxContent></w:drawing></mc:Choice>
      <mc:Fallback><w:pict><w:txbxContent><w:p><w:r><w:t>Text box 12.5% [8].</w:t></w:r></w:p></w:txbxContent></w:pict></mc:Fallback>
    </mc:AlternateContent></w:r></w:p>
  </w:body>
</w:document>'''
        footnotes_xml = b'''<?xml version="1.0" encoding="UTF-8"?>
<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:footnote w:id="1"><w:p><w:r><w:t>Footnote 450 K [9].</w:t></w:r></w:p></w:footnote>
</w:footnotes>'''
        endnotes_xml = b'''<?xml version="1.0" encoding="UTF-8"?>
<w:endnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:endnote w:id="1"><w:p><w:r><w:t>Endnote 3.2 m [10].</w:t></w:r></w:p></w:endnote>
</w:endnotes>'''
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "structures.docx"
            self.write_docx(
                path,
                document_xml,
                footnotes=footnotes_xml,
                endnotes=endnotes_xml,
            )
            text = audit_revision.read_text(path)
            self.assertIn("Table value 42 kg [7].", text)
            self.assertIn("Text box 12.5% [8].", text)
            self.assertEqual(text.count("Text box 12.5% [8]."), 1)
            self.assertIn("Footnote 450 K [9].", text)
            self.assertIn("Endnote 3.2 m [10].", text)

    def test_audits_changes_in_docx_structures(self):
        original_document = b'''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:tbl><w:tr><w:tc><w:p><w:r><w:t>Table value 42 kg [7].</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
    <w:p><w:r><w:drawing><w:txbxContent><w:p><w:r><w:t>Text box 12.5% [8].</w:t></w:r></w:p></w:txbxContent></w:drawing></w:r></w:p>
  </w:body>
</w:document>'''
        revised_document = original_document.replace(b"42 kg", b"47 kg")
        original_footnotes = b'''<?xml version="1.0" encoding="UTF-8"?>
<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:footnote w:id="1"><w:p><w:r><w:t>Footnote 450 K [9].</w:t></w:r></w:p></w:footnote>
</w:footnotes>'''
        revised_footnotes = original_footnotes.replace(b"[9]", b"[10]")
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "original.docx"
            revised = Path(directory) / "revised.docx"
            self.write_docx(original, original_document, footnotes=original_footnotes)
            self.write_docx(revised, revised_document, footnotes=revised_footnotes)
            result = audit_revision.audit(
                audit_revision.read_text(original),
                audit_revision.read_text(revised),
                4,
                10,
            )
            self.assertIn("42kg", result["measurements"]["missing_or_reduced"])
            self.assertIn("47kg", result["measurements"]["added_or_increased"])
            self.assertIn("[9]", result["citations"]["missing_or_reduced"])
            self.assertIn("[10]", result["citations"]["added_or_increased"])

    def test_preserved_docx_structures_have_no_fidelity_warning(self):
        original_document = b'''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:tbl><w:tr><w:tc><w:p><w:r><w:t>Table value 42 kg [7].</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
    <w:p><w:r><w:drawing><w:txbxContent><w:p><w:r><w:t>Text box 12.5% [8].</w:t></w:r></w:p></w:txbxContent></w:drawing></w:r></w:p>
  </w:body>
</w:document>'''
        revised_document = original_document.replace(b"Table value", b"Measured value")
        footnotes = b'''<?xml version="1.0" encoding="UTF-8"?>
<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:footnote w:id="1"><w:p><w:r><w:t>Footnote 450 K [9].</w:t></w:r></w:p></w:footnote>
</w:footnotes>'''
        revised_footnotes = footnotes.replace(b"Footnote", b"Supporting note")
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "original.docx"
            revised = Path(directory) / "revised.docx"
            self.write_docx(original, original_document, footnotes=footnotes)
            self.write_docx(revised, revised_document, footnotes=revised_footnotes)
            result = audit_revision.audit(
                audit_revision.read_text(original),
                audit_revision.read_text(revised),
                4,
                10,
            )
            for category in ("numbers", "measurements", "citations"):
                self.assertEqual(result[category]["missing_or_reduced"], {})
                self.assertEqual(result[category]["added_or_increased"], {})


if __name__ == "__main__":
    unittest.main()
