import streamlit as st
from summarizer import extract_text_from_pdf, clean_text, extract_keywords_with_bert, summarize
import json
import tempfile

st.title("PDF Summarizer")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    st.info("Extracting text from PDF")
    raw_text = extract_text_from_pdf(tmp_path)
    cleaned_text = clean_text(raw_text)

    summary_input = cleaned_text[:1000]

    st.info("Generating summary...")
    summary = summarize(summary_input)

    st.info("Extracting keywords...")
    keywords = extract_keywords_with_bert(summary)

    st.subheader("📌 Summary")
    st.write(summary)

    st.subheader("🔑 Keywords")
    st.write(", ".join(keywords))

    result = {
        "summary": summary,
        "keywords": keywords
    }

    st.download_button(
        label="📥 Download Result as JSON",
        data=json.dumps(result, indent=2),
        file_name="summary_output.json",
        mime="application/json"
    )