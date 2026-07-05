"""User interface module for DocMetaAI.

This module provides a modern CustomTkinter dashboard and preserves the
existing document workflow through scanner.py and fixer.py.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox

from ai_engine import AIEngine
from fixer import DocumentFixer
from report import DocumentReport
from scanner import DocumentScanner
from utils import normalize_path, safe_execute


APP_TITLE = "DocMetaAI"
APP_SIZE = "1080x720"
SIDEBAR_COLOR = "#111827"
CONTENT_COLOR = "#181f2b"
CARD_COLOR = "#0f172a"
BUTTON_PRIMARY = "#2563eb"
BUTTON_HOVER = "#1d4ed8"
TEXT_SECONDARY = "#94a3b8"


class DocMetaAIApp:
    """Main application class for the DocMetaAI desktop app."""

    def __init__(self) -> None:
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title(APP_TITLE)
        self.root.geometry(APP_SIZE)
        self.root.minsize(1040, 720)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.file_path = ""
        self.scanner = DocumentScanner()
        self.fixer = DocumentFixer()
        self.report = DocumentReport()
        self.ai_engine = AIEngine()

        self._build_interface()

    def _build_interface(self) -> None:
        """Create the main UI layout."""
        sidebar = ctk.CTkFrame(self.root, width=280, fg_color=SIDEBAR_COLOR, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(10, weight=1)

        content = ctk.CTkFrame(self.root, fg_color=CONTENT_COLOR)
        content.grid(row=0, column=1, sticky="nsew", padx=(12, 16), pady=12)
        content.grid_rowconfigure(2, weight=1)
        content.grid_columnconfigure(0, weight=1)

        self._build_sidebar(sidebar)
        self._build_header(content)
        self._build_results_panel(content)

    def _build_sidebar(self, parent: ctk.CTkFrame) -> None:
        """Build the left navigation sidebar."""
        ctk.CTkLabel(
            parent,
            text=APP_TITLE,
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=24, pady=(24, 4), sticky="w")

        ctk.CTkLabel(
            parent,
            text="Modern document assistant for Word cleanup, formatting, and quality scoring.",
            wraplength=220,
            justify="left",
            text_color=TEXT_SECONDARY,
        ).grid(row=1, column=0, padx=24, pady=(0, 24), sticky="w")

        actions = [
            ("📂 Open Document", self.open_document),
            ("🔍 Scan", self.scan_document),
            ("🧹 Fix Document", self.fix_document),
            ("🤖 AI Assistant", self.show_ai_suggestions),
            ("📤 Export PDF", self.export_pdf),
        ]

        for index, (label, command) in enumerate(actions, start=2):
            ctk.CTkButton(
                parent,
                text=label,
                command=command,
                width=220,
                height=50,
                corner_radius=14,
                fg_color=BUTTON_PRIMARY,
                hover_color=BUTTON_HOVER,
                font=ctk.CTkFont(size=14, weight="bold"),
            ).grid(row=index, column=0, padx=24, pady=(0, 10))

        theme_frame = ctk.CTkFrame(parent, fg_color=SIDEBAR_COLOR, border_width=1, border_color="#334155")
        theme_frame.grid(row=8, column=0, padx=24, pady=(24, 16), sticky="ew")
        theme_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(theme_frame, text="Theme", text_color=TEXT_SECONDARY).grid(row=0, column=0, padx=(16, 8), pady=14, sticky="w")
        self.theme_switch = ctk.CTkSwitch(theme_frame, text="", command=self._toggle_theme)
        self.theme_switch.grid(row=0, column=1, padx=16, pady=14, sticky="e")

        ctk.CTkLabel(
            parent,
            text="Version 1.0",
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(size=12),
        ).grid(row=9, column=0, padx=24, pady=(0, 16), sticky="w")

        ctk.CTkButton(
            parent,
            text="Exit",
            command=self.exit_application,
            width=220,
            height=44,
            fg_color="#dc2626",
            hover_color="#ef4444",
            corner_radius=14,
        ).grid(row=10, column=0, padx=24, pady=(0, 24))

    def _build_header(self, parent: ctk.CTkFrame) -> None:
        """Build the top header section and score card."""
        header = ctk.CTkFrame(parent, fg_color=CONTENT_COLOR, corner_radius=20)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12), padx=4)
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=1)

        info_panel = ctk.CTkFrame(header, fg_color=CARD_COLOR, corner_radius=18)
        info_panel.grid(row=0, column=0, sticky="nsew", padx=(16, 12), pady=16)
        info_panel.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            info_panel,
            text="Document Health Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=20, pady=(20, 8), sticky="w")

        self.file_label = ctk.CTkLabel(
            info_panel,
            text="No document loaded.",
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.file_label.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="w")

        self.status_label = ctk.CTkLabel(
            info_panel,
            text="Open a Word document to display health and scan details.",
            wraplength=420,
            justify="left",
            text_color=TEXT_SECONDARY,
        )
        self.status_label.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")

        score_card = ctk.CTkFrame(header, fg_color=CARD_COLOR, corner_radius=18)
        score_card.grid(row=0, column=1, sticky="nsew", padx=(12, 16), pady=16)
        score_card.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            score_card,
            text="Health Score",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).grid(row=0, column=0, padx=20, pady=(20, 8), sticky="w")

        self.health_value = ctk.CTkLabel(
            score_card,
            text="N/A",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#f8fafc",
        )
        self.health_value.grid(row=1, column=0, padx=20, pady=(0, 4), sticky="w")

        self.health_detail = ctk.CTkLabel(
            score_card,
            text="No scan performed yet.",
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.health_detail.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")

    def _build_results_panel(self, parent: ctk.CTkFrame) -> None:
        """Build the scan results card panel."""
        results_card = ctk.CTkFrame(parent, fg_color=CARD_COLOR, corner_radius=20)
        results_card.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 12))
        results_card.grid_rowconfigure(1, weight=1)
        results_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            results_card,
            text="Scan Results",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=24, pady=(24, 12), sticky="w")

        self.results_box = ctk.CTkTextbox(
            results_card,
            width=760,
            height=440,
            fg_color="#0f172a",
            text_color="#e2e8f0",
            corner_radius=16,
            font=ctk.CTkFont(size=14),
        )
        self.results_box.grid(row=1, column=0, padx=24, pady=(0, 24), sticky="nsew")
        self.results_box.insert(
            "0.0",
            "No scan results yet. Open a document and click Scan to analyze document health.",
        )
        self.results_box.configure(state="disabled")

    def _toggle_theme(self) -> None:
        """Toggle between dark and light mode."""
        current_mode = ctk.get_appearance_mode()
        next_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(next_mode)

    def _set_scan_results(self, message: str) -> None:
        """Update the scan results panel."""
        self.results_box.configure(state="normal")
        self.results_box.delete("0.0", "end")
        self.results_box.insert("0.0", message)
        self.results_box.configure(state="disabled")

    def _set_header_status(self, message: str) -> None:
        """Update the header status text."""
        self.status_label.configure(text=message)

    def _set_health_score(self, score: int, label: str) -> None:
        """Update the displayed health score and caption."""
        self.health_value.configure(text=f"{score} / 100")
        self.health_detail.configure(text=label)
        score_color = "#34d399" if score >= 90 else "#60a5fa" if score >= 70 else "#facc15" if score >= 50 else "#f87171"
        self.health_value.configure(text_color=score_color)

    def open_document(self) -> None:
        """Open and scan a document immediately."""

        def action() -> None:
            selected = filedialog.askopenfilename(
                filetypes=[("Word Documents", "*.docx")],
                title="Open Word Document",
            )
            if not selected:
                return

            self.file_path = normalize_path(selected)
            self._set_header_status("Document loaded. Scanning document now...")
            self._set_document_path(self.file_path)

            report_data = self.scanner.scan(self.file_path)
            health_score, health_label = self.report.compute_health(report_data)
            scan_summary = self.report.format_document_summary(
                self.file_path, report_data, health_score, health_label
            )

            self._set_health_score(health_score, health_label)
            self._set_scan_results(scan_summary)
            self._set_header_status("Document loaded and scanned successfully.")

        safe_execute(action, "Unable to open or scan the document.")

    def _set_document_path(self, path: str) -> None:
        """Update the file path label in the header."""
        self.file_label.configure(text=path)

    def scan_document(self) -> None:
        """Scan the currently loaded document and update health details."""

        def action() -> None:
            if not self.file_path:
                messagebox.showwarning("No document", "Please open a Word document first.")
                return

            report_data = self.scanner.scan(self.file_path)
            health_score, health_label = self.report.compute_health(report_data)
            scan_summary = self.report.format_document_summary(
                self.file_path, report_data, health_score, health_label
            )

            self._set_health_score(health_score, health_label)
            self._set_scan_results(scan_summary)
            self._set_header_status("Scan complete. Review the document health report.")

        safe_execute(action, "Unable to scan the document.")

    def fix_document(self) -> None:
        """Fix the current document using fixer.py."""

        def action() -> None:
            if not self.file_path:
                messagebox.showwarning("No document", "Please open a Word document first.")
                return

            output_path = self.fixer.improve(self.file_path)
            messagebox.showinfo("Document Fixed", f"Fixed document saved as:\n{output_path}")
            self._set_header_status("Document fixed and saved. Scan again to refresh the score.")
            self._set_scan_results(f"Document fixed successfully.\nSaved as: {output_path}")

        safe_execute(action, "Unable to fix the document.")

    def show_ai_suggestions(self) -> None:
        """Show AI assistant suggestions for the current document."""

        def action() -> None:
            if not self.file_path:
                messagebox.showwarning("No document", "Please open a Word document first.")
                return

            suggestions = self.ai_engine.get_suggestions(self.file_path)
            self._set_scan_results(suggestions)
            self._set_header_status("AI assistant suggestions are displayed.")

        safe_execute(action, "Unable to retrieve AI suggestions.")

    def export_pdf(self) -> None:
        """Export the currently loaded document to PDF."""

        def action() -> None:
            if not self.file_path:
                messagebox.showwarning("No document", "Please open a Word document first.")
                return

            target_path = self.report.export_pdf(self.file_path)
            messagebox.showinfo("Export Complete", f"PDF exported successfully:\n{target_path}")
            self._set_header_status("PDF export completed successfully.")
            self._set_scan_results(f"PDF exported successfully.\nSaved as: {target_path}")

        safe_execute(action, "Unable to export PDF.")

    def exit_application(self) -> None:
        """Exit the application cleanly."""
        self.root.quit()

    def run(self) -> None:
        """Start the application's main event loop."""
        self.root.mainloop()
