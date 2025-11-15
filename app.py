"""
Immigration Platform - Home Page
Multi-page Streamlit application
"""

import streamlit as st
from shared.config_manager import get_config
from shared.database import Database

st.set_page_config(
    page_title="Immigration Platform",
    page_icon="🌍",
    layout="wide"
)

# ============ APP INITIALIZATION ============
# Load configuration and initialize database at startup
@st.cache_resource
def init_app():
    """Initialize app - runs once at startup"""
    # Initialize database (creates tables including settings)
    db = Database()

    # Load configuration from .env > Database > YAML
    config = get_config()

    return {"db": db, "config": config}

# Initialize
app_state = init_app()
config = app_state["config"]

# Check if API key is configured
api_key_configured = config.get_api_key() is not None

# Home page
st.title("🌍 Immigration Platform")
st.markdown("### Multi-source visa data collection and analysis system")

# Configuration status banner
if not api_key_configured:
    st.warning("""
    ⚠️ **API Key Not Configured** - LLM features are disabled

    **To enable AI-powered features:**
    1. Go to ⚙️ Settings page (in sidebar)
    2. Tab 3 → API Key Quick Setup
    3. Paste your API key and save

    **Get FREE OpenRouter key:** https://openrouter.ai/keys
    """)
else:
    provider = config.get('llm.provider', 'openrouter')
    model = config.get('llm.model', 'unknown')
    st.success(f"✅ **System Ready** - Using {provider.title()} ({model})")

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
