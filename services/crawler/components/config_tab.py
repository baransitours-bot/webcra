"""
Crawler Configuration Tab Component
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import shared modules
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from shared.config_manager import get_config

class ConfigTab:
    """Handles crawler configuration UI"""

    @staticmethod
    def render():
        """Render configuration tab and return config dict"""
        st.subheader("⚙️ Crawler Configuration")

        # Get config manager
        config_mgr = get_config()

        # Load countries from config manager (DB > YAML)
        countries_data = config_mgr.get_countries()
        available_countries = list(countries_data.keys())

        # Config mode selection
        config_mode = st.radio(
            "Configuration Mode",
            ["Quick Start (Default)", "Custom Configuration"],
            help="Use default settings or customize"
        )

        if config_mode == "Custom Configuration":
            config = ConfigTab._render_custom_config(available_countries)
        else:
            config = ConfigTab._render_default_config(available_countries)

        # Save to session
        st.session_state['crawler_config'] = config

        return config

    @staticmethod
    def _render_default_config(available_countries):
        """Render default configuration"""
        # Get config manager for defaults
        config_mgr = get_config()

        max_pages_default = config_mgr.get('crawler.max_pages', 50)
        max_depth_default = config_mgr.get('crawler.max_depth', 3)
        delay_default = config_mgr.get('crawler.delay', 2.0)

        st.info(f"""
        **Default Settings (from Global Config):**
        - Max Pages: {max_pages_default} per country
        - Max Depth: {max_depth_default} levels
        - Delay: {delay_default} seconds between requests
        - Saves to database with versioning
        """)

        # Just select countries
        default_country = ['canada'] if 'canada' in available_countries else (
            [available_countries[0]] if available_countries else []
        )

        countries = st.multiselect(
            "Select Countries to Crawl",
            available_countries,
            default=default_country,
            help="Choose which countries to crawl"
        )

        return {
            'countries': countries,
            'max_pages': max_pages_default,
            'max_depth': max_depth_default,
            'request_delay': delay_default,
            'mode': 'default'
        }

    @staticmethod
    def _render_custom_config(available_countries):
        """Render custom configuration"""
        col1, col2 = st.columns(2)

        with col1:
            countries = st.multiselect(
                "Select Countries",
                available_countries,
                default=['canada'],
                help="Countries to crawl"
            )

            max_pages = st.number_input(
                "Max Pages per Country",
                min_value=10,
                max_value=500,
                value=50,
                step=10,
                help="Maximum number of pages to crawl per country"
            )

        with col2:
            max_depth = st.slider(
                "Max Crawl Depth",
                min_value=1,
                max_value=5,
                value=3,
                help="How deep to follow links (1 = seed URLs only)"
            )

            request_delay = st.number_input(
                "Request Delay (seconds)",
                min_value=0.5,
                max_value=10.0,
                value=2.0,
                step=0.5,
                help="Delay between requests to avoid rate limiting"
            )

        return {
            'countries': countries,
            'max_pages': max_pages,
            'max_depth': max_depth,
            'request_delay': request_delay,
            'mode': 'custom'
        }
