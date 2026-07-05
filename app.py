import tempfile
from pathlib import Path

import streamlit as st

from ai_engine import AIEngine
from fixer import DocumentFixer
from report import DocumentReport
from scanner import DocumentScanner

st.set_page_config(page_title="DocMetaAI", page_icon="📄", layout="wide")
st.title("DocMetaAI")
st.caption("Upload a Word document and use the web version of the assistant.")

scanner = DocumentScanner()
report = DocumentReport()
fixer = DocumentFixer()
ai_engine = AIEngine()

uploaded_file = st.file_uploader("Upload a DOCX file", type=["docx"])

if uploaded_file is not None:
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / uploaded_file.name
        input_path.write_bytes(uploaded_file.getvalue())

        if st.button("Analyze document"):
            with st.spinner("Scanning document..."):
                metrics = scanner.scan(str(input_path))
                health_score, health_label = report.compute_health(metrics)
                summary = report.format_document_summary(str(input_path), metrics, health_score, health_label)

            st.session_state["metrics"] = metrics
            st.session_state["health_score"] = health_score
            st.session_state["health_label"] = health_label
            st.session_state["summary"] = summary
            st.session_state["input_path"] = str(input_path)

        if "summary" in st.session_state:
            st.subheader("Health report")
            st.success(f"Health Score: {st.session_state['health_score']} / 100 ({st.session_state['health_label']})")
            st.code(st.session_state["summary"], language="text")

        if st.button("Apply fixes") and "input_path" in st.session_state:
            with st.spinner("Improving document..."):
                output_path = fixer.improve(st.session_state["input_path"])
            st.success(f"Improved file saved as {output_path}")
            with open(output_path, "rb") as handle:
                st.download_button(
                    label="Download improved DOCX",
                    data=handle.read(),
                    file_name=Path(output_path).name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

        if st.button("Get AI suggestions") and "input_path" in st.session_state:
            with st.spinner("Preparing suggestions..."):
                suggestions = ai_engine.get_suggestions(st.session_state["input_path"])
            st.subheader("AI suggestions")
            st.write(suggestions)

        if st.button("Export PDF") and "input_path" in st.session_state:
            with st.spinner("Exporting PDF..."):
                output_path = report.export_pdf(st.session_state["input_path"])
            st.success(f"PDF saved as {output_path}")
            with open(output_path, "rb") as handle:
                st.download_button(
                    label="Download PDF",
                    data=handle.read(),
                    file_name=Path(output_path).name,
                    mime="application/pdf",
                )
else:
    st.info("Upload a DOCX file to begin.")
