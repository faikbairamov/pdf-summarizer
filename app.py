import streamlit as st
from summarizer import extract_text_from_pdf, improved_extract_title, clean_text, extract_keywords_with_bert, summarize, \
    extract_text_with_font_info, extract_authors
import json
import tempfile

st.set_page_config(page_title="PDF Summarizer for Scientific Papers", layout="centered")
st.title("📄 PDF Summarizer for Scientific Papers")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    st.info("Extracting text from PDF...")
    raw_text = extract_text_from_pdf(tmp_path)

    st.info("Extracting title...")
    # Use the improved title extraction function with font detection
    title = improved_extract_title(raw_text, pdf_path=tmp_path)

    st.info("Extracting authors...")
    authors = extract_authors(raw_text, title=title, pdf_path=tmp_path)

    # Add font-based debugging info
    with st.expander("Debug: Font-Based Title Detection"):
        try:
            text_with_font = extract_text_with_font_info(tmp_path)
            st.text("First 10 text elements with font size:")
            for i, (text, size) in enumerate(text_with_font[:10]):
                if text.strip():
                    st.text(f"Element {i + 1} [Font size: {size:.1f}]: {text}")
            st.text(f"\nExtracted title: {title}")
        except Exception as e:
            st.error(f"Error in font extraction debug: {e}")

    cleaned_text = clean_text(raw_text)

    st.info("Generating summary...")
    # Use a reasonable chunk size to avoid token limits
    summary_text = cleaned_text[:3000]  # Limiting to first 3000 chars for summary
    summary = summarize(summary_text)

    st.info("Extracting keywords...")
    keywords = extract_keywords_with_bert(summary)

    st.subheader("📌 Title")
    st.markdown(f"**{title}**")

    st.subheader("👥 Authors")
    st.write(authors)

    st.subheader("📝 Summary")
    st.write(summary)

    st.subheader("🔑 Keywords")
    st.write(", ".join(keywords))

    result = {
        "title": title,
        "authors": authors,
        "summary": summary,
        "keywords": keywords
    }

    st.download_button(
        label="📥 Download Result as JSON",
        data=json.dumps(result, indent=2),
        file_name="summary_output.json",
        mime="application/json"
    )