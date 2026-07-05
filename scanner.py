"""Document scanning and health analysis for DocMetaAI."""

from collections import Counter
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


class DocumentScanner:
    """Scan a Word document and extract health metrics."""

    def scan(self, file_path: str) -> dict[str, Any]:
        """Return a structured health report for a DOCX file."""
        path = Path(file_path)
        document = Document(path)
        paragraphs = list(document.paragraphs)

        word_count = 0
        empty_paragraphs = 0
        extra_spaces = 0
        missing_headings = 0
        page_break_issues = 0
        wrong_alignment = 0

        font_names: set[str] = set()
        font_sizes: set[float] = set()
        heading_styles: Counter[str] = Counter()

        for paragraph in paragraphs:
            text = paragraph.text or ""
            stripped = text.strip()
            if not stripped:
                empty_paragraphs += 1

            words = stripped.split()
            word_count += len(words)
            extra_spaces += max(0, text.count("  "))

            style_name = paragraph.style.name if paragraph.style else "Normal"
            if style_name.lower().startswith("heading"):
                heading_styles[style_name] += 1

            # Some python-docx versions don't expose a page_break_before
            # attribute on the paragraph object. Use getattr to safely
            # detect this property without raising an AttributeError.
            if getattr(paragraph, "page_break_before", False):
                page_break_issues += 1

            if paragraph.alignment not in {
                WD_PARAGRAPH_ALIGNMENT.LEFT,
                WD_PARAGRAPH_ALIGNMENT.CENTER,
                WD_PARAGRAPH_ALIGNMENT.RIGHT,
                WD_PARAGRAPH_ALIGNMENT.JUSTIFY,
                None,
            }:
                wrong_alignment += 1

            for run in paragraph.runs:
                font_name = run.font.name
                if font_name:
                    font_names.add(font_name)

                font_size = getattr(run.font.size, "pt", None)
                if font_size:
                    font_sizes.add(round(font_size, 2))

                # Runs may carry a page break flag — guard access safely.
                if getattr(run, "page_break", False):
                    page_break_issues += 1

        if len(heading_styles) == 0 and paragraphs:
            missing_headings = 1
        elif paragraphs and sum(heading_styles.values()) < max(1, len(paragraphs) // 8):
            missing_headings = 1

        return {
            "paragraphs": len(paragraphs),
            "words": word_count,
            "empty_paragraphs": empty_paragraphs,
            "extra_spaces": extra_spaces,
            "different_fonts": len(font_names),
            "different_font_sizes": len(font_sizes),
            "wrong_alignment": wrong_alignment,
            "missing_headings": missing_headings,
            "page_break_issues": page_break_issues,
            "fonts": sorted(font_names),
            "font_sizes": sorted(font_sizes),
        }
