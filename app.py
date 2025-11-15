"""
Immigration Platform - Home Page
Multi-page Streamlit application
"""

import streamlit as st

st.set_page_config(
    page_title="Immigration Platform",
    page_icon="🌍",
    layout="wide"
)

# Home page
st.title("🌍 Immigration Platform")
st.markdown("### Multi-source visa data collection and analysis system")

st.markdown("---")

# Services overview
st.subheader("📋 Available Services")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 🕷️ Crawler Service
    Collect visa data from government websites
    - Web scraping
    - Progress tracking
    - Configurable sources

    **Status:** ✅ Ready
    """)

    st.markdown("""
    #### 📊 Classifier Service
    Extract structured data from raw content
    - LLM-powered extraction
    - Visa requirements
    - Fee information

    **Status:** ⏳ Coming soon
    """)

with col2:
    st.markdown("""
    #### 🔍 Matcher Service
    Match visas to user profiles
    - Eligibility scoring
    - Gap analysis
    - Recommendations

    **Status:** ⏳ Coming soon
    """)

    st.markdown("""
    #### 💬 Assistant Service
    Q&A about visa requirements
    - Chat interface
    - Context-aware answers
    - Profile-based queries

    **Status:** ⏳ Coming soon
    """)

st.markdown("---")

# Quick start
st.subheader("🚀 Quick Start")

st.markdown("""
1. **Use the sidebar** to navigate to a service
2. **Configure** the service parameters
3. **Run** and monitor progress
4. **View** results and outputs

**Start with:** 🕷️ Crawler Service to collect data
""")

st.markdown("---")

# System info
st.info("""
**📖 Documentation:** See `SYSTEM.md` for complete system overview

**🔧 Current Data:** `data/processed/visas.json` (13 visas from USA, TestCountry)
""")
