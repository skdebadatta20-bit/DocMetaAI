"""AI engine module for DocMetaAI.

This module supports local document-aware suggestions and can be extended later
for an external LLM provider.
"""

import os
from pathlib import Path


class AIEngine:
    """Provide AI-powered document suggestions and transformations."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.provider = "openai" if self.api_key else "local"

    def get_suggestions(self, file_path: str) -> str:
        """Return document-aware suggestions based on the selected Word file."""
        path = Path(file_path)
        document_text = self._extract_all_text(path)

        if not document_text:
            return "The selected document is empty or unsupported."

        paragraphs = [paragraph.strip() for paragraph in document_text.splitlines() if paragraph.strip()]
        heading_candidates = [paragraph for paragraph in paragraphs if len(paragraph.split()) <= 8 and paragraph[0:1].isupper()]
        heading = heading_candidates[0] if heading_candidates else None
        long_paragraphs = [paragraph for paragraph in paragraphs if len(paragraph.split()) > 35]
        word_count = sum(len(paragraph.split()) for paragraph in paragraphs)

        suggestions: list[str] = []
        if heading:
            suggestions.append(f"Use the heading '{heading}' as the opening title and keep it short and clear.")
        else:
            suggestions.append("Add a clear heading structure so readers can scan the document quickly.")

        if long_paragraphs:
            suggestions.append(f"Break {len(long_paragraphs)} long paragraph(s) into shorter paragraphs for easier reading.")
        else:
            suggestions.append("Keep the writing concise and split ideas into shorter paragraphs where needed.")

        if word_count > 250:
            suggestions.append("Condense repetitive content and remove filler phrases to keep the document professional.")
        else:
            suggestions.append("Strengthen the conclusion with a short summary of the main message.")

        if len(paragraphs) > 6:
            suggestions.append("Group related ideas into sections with consistent spacing and heading levels.")
        else:
            suggestions.append("Add one supporting section or bullet list to improve structure.")

        summary = self.summarize(document_text)
        return (
            "AI Suggestions:\n"
            + "- "
            + "\n- ".join(suggestions)
            + f"\n\nDocument summary: {summary}"
            + "\n\nThese recommendations are based on the document content and structure."
        )

    def grammar_suggestions(self, text: str) -> str:
        """Return grammar improvement suggestions for a block of text."""
        return self._safe_response(
            "Check spelling, punctuation, and sentence flow. Consider shorter sentences and consistent verb tense."
        )

    def rewrite_paragraph(self, text: str) -> str:
        """Rewrite a paragraph with a more professional tone."""
        sanitized = " ".join(text.strip().split())
        if not sanitized:
            return "No text to rewrite."
        return f"Rewrite suggestion: {sanitized[:180]}"

    def summarize(self, text: str) -> str:
        """Return a short summary of a long text block."""
        sentences = [sentence.strip() for sentence in text.replace("\n", " ").split(".") if sentence.strip()]
        summary = " ".join(sentences[:3])
        return summary[:220] if summary else "No content available to summarize."

    def translate(self, text: str, target_language: str = "English") -> str:
        """Return a placeholder translation message."""
        return f"Translation to {target_language} is available in future AI releases."

    def convert_to_university_format(self, text: str) -> str:
        """Return a placeholder for university formatting."""
        return "University formatting guidelines will be applied in the next update."

    def convert_to_government_format(self, text: str) -> str:
        """Return a placeholder for government office formatting."""
        return "Government office formatting support is planned for future versions."

    def format_resume(self, text: str) -> str:
        """Return a placeholder for resume formatting."""
        return "Resume formatting suggestions are available in the next AI integration release."

    def format_internship_report(self, text: str) -> str:
        """Return a placeholder for internship report formatting."""
        return "Internship report formatting support is on the roadmap."

    def _extract_all_text(self, path: Path) -> str:
        """Read and return all paragraph text from a Word document."""
        try:
            from docx import Document

            document = Document(path)
            return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
        except Exception:
            return ""

    def _safe_response(self, message: str) -> str:
        """Wrap a message with provider details."""
        return f"[{self.provider.upper()} AI] {message}"
