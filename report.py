"""Reporting utilities for DocMetaAI."""

import os
from pathlib import Path
from typing import Any


class DocumentReport:
    """Create health summaries and export documents."""

    def compute_health(self, metrics: dict[str, Any]) -> tuple[int, str]:
        """Compute a health score and category based on document metrics."""
        score = 100
        score -= min(metrics.get("extra_spaces", 0) * 2, 20)
        score -= min(metrics.get("empty_paragraphs", 0) * 2, 20)
        score -= min(max(metrics.get("different_fonts", 1) - 1, 0) * 5, 20)
        score -= min(max(metrics.get("different_font_sizes", 1) - 1, 0) * 4, 20)
        score -= min(metrics.get("wrong_alignment", 0) * 3, 15)
        score -= metrics.get("missing_headings", 0) * 10
        score -= min(metrics.get("page_break_issues", 0) * 4, 20)

        score = max(0, min(100, score))
        return score, self._health_label(score)

    def _health_label(self, score: int) -> str:
        """Return a label based on the health score."""
        if score >= 90:
            return "Excellent"
        if score >= 70:
            return "Good"
        if score >= 50:
            return "Warning"
        return "Critical"

    def format_document_summary(
        self,
        file_path: str,
        metrics: dict[str, Any],
        health_score: int,
        health_label: str,
    ) -> str:
        """Format a readable document summary report."""
        lines = [
            f"Document: {file_path}",
            f"Health Score: {health_score} ({health_label})",
            "",
            "Document Health Metrics:",
            f"- Paragraphs: {metrics.get('paragraphs', 0)}",
            f"- Words: {metrics.get('words', 0)}",
            f"- Empty Paragraphs: {metrics.get('empty_paragraphs', 0)}",
            f"- Extra Spaces: {metrics.get('extra_spaces', 0)}",
            f"- Different Fonts: {metrics.get('different_fonts', 0)}",
            f"- Different Font Sizes: {metrics.get('different_font_sizes', 0)}",
            f"- Wrong Alignment: {metrics.get('wrong_alignment', 0)}",
            f"- Missing Headings: {metrics.get('missing_headings', 0)}",
            f"- Page Break Issues: {metrics.get('page_break_issues', 0)}",
            "",
            "Review the health score and apply fix formatting or AI suggestions to improve the document.",
        ]
        return "\n".join(lines)

    def export_pdf(self, file_path: str) -> str:
        """Export a DOCX file to PDF using the installed converter or a built-in fallback."""
        path = Path(file_path)
        target_path = path.with_suffix(".pdf")

        try:
            if os.name == "nt":
                from docx2pdf import convert

                convert(str(path), str(target_path))
                return str(target_path)
        except Exception:
            pass

        self._write_simple_pdf(path, target_path)
        return str(target_path)

    def _write_simple_pdf(self, source_path: Path, target_path: Path) -> None:
        """Create a lightweight PDF file from the document text when no converter is installed."""
        from docx import Document

        document = Document(source_path)
        lines: list[str] = []
        for paragraph in document.paragraphs:
            text = paragraph.text.strip()
            if text:
                lines.append(text)

        if not lines:
            lines = ["No text available for export."]

        title = lines[0] if lines else "Document Export"
        body_lines = self._wrap_text("\n".join(lines[1:20]), 80)
        content_lines = [title, ""] + body_lines
        content_stream = self._build_content_stream(content_lines)
        stream_bytes = content_stream.encode("latin-1", "replace")

        objects: list[bytes] = []
        objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
        objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
        objects.append(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
        )
        objects.append(f"<< /Length {len(stream_bytes)} >>\nstream\n{content_stream}\nendstream".encode("latin-1"))
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

        pdf_bytes = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for index, obj in enumerate(objects, start=1):
            offsets.append(len(pdf_bytes))
            pdf_bytes.extend(f"{index} 0 obj\n".encode("latin-1"))
            pdf_bytes.extend(obj)
            pdf_bytes.extend(b"\nendobj\n")

        xref_offset = len(pdf_bytes)
        pdf_bytes.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
        pdf_bytes.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf_bytes.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
        pdf_bytes.extend(
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin-1")
        )
        target_path.write_bytes(pdf_bytes)

    def _build_content_stream(self, lines: list[str]) -> str:
        """Build the PDF content stream for a list of text lines."""
        commands = ["BT", "/F1 12 Tf", "72 760 Td"]
        for index, line in enumerate(lines):
            if index > 0:
                commands.append("0 -14 Td")
            commands.append(f"({self._escape_pdf_text(line)}) Tj")
        commands.append("ET")
        return "\n".join(commands)

    def _wrap_text(self, text: str, width: int) -> list[str]:
        """Wrap long text into multiple PDF lines."""
        words = text.split()
        wrapped: list[str] = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 <= width:
                current = f"{current} {word}".strip()
            else:
                if current:
                    wrapped.append(current)
                current = word
        if current:
            wrapped.append(current)
        return wrapped if wrapped else [text]

    def _escape_pdf_text(self, text: str) -> str:
        """Escape characters that are not valid inside a PDF string."""
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
