"""
Classifier Service Page
Extract structured data from crawled pages
"""

import streamlit as st

st.set_page_config(page_title="Classifier Service", page_icon="📊", layout="wide")

st.title("📊 Classifier Service")
st.markdown("Extract structured visa data from raw crawled content")

st.markdown("---")

st.info("""
### ⏳ Coming Soon

This service will:
- Extract visa requirements from crawled pages
- Structure data using LLM
- Save to `data/processed/visas.json`

**Status:** Under development
""")

st.markdown("---")
st.caption("Classifier Service - Part of Immigration Platform")
