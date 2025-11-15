"""
Crawler Service Page - Refactored with Components
Collect visa data from government websites
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import crawler components
from services.crawler.components import ConfigTab, RunTab, ResultsTab

st.set_page_config(
    page_title="Crawler Service",
    page_icon="🕷️",
    layout="wide"
)

st.title("🕷️ Crawler Service")
st.markdown("Collect visa and immigration data from government websites")

st.markdown("---")

# Create tabs
tab1, tab2, tab3 = st.tabs(["⚙️ Configuration", "▶️ Run", "📊 Results"])

# Render each tab using components
with tab1:
    config = ConfigTab.render()

with tab2:
    # Get config from session or use default
    if 'crawler_config' in st.session_state:
        config = st.session_state['crawler_config']
    else:
        config = {
            'countries': ['canada'],
            'max_pages': 50,
            'max_depth': 3,
            'request_delay': 2.0,
            'mode': 'default'
        }

    RunTab.render(config)

with tab3:
    ResultsTab.render()
