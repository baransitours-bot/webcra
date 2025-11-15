"""
Crawler Configuration Tab Component
"""

import streamlit as st
import yaml

class ConfigTab:
    """Handles crawler configuration UI"""

    @staticmethod
    def render():
        """Render configuration tab and return config dict"""
        st.subheader("⚙️ Crawler Configuration")

        # Load global config for countries
        with open('config.yaml', 'r') as f:
            global_config = yaml.safe_load(f)

        available_countries = list(global_config.get('countries', {}).keys())

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
        st.info("""
        **Default Settings:**
        - Max Pages: 50 per country
        - Max Depth: 3 levels
        - Delay: 2 seconds between requests
        - Saves to database with versioning
        """)

        # Just select countries
        countries = st.multiselect(
            "Select Countries to Crawl",
            available_countries,
            default=['canada'],
            help="Choose which countries to crawl"
        )

        return {
            'countries': countries,
            'max_pages': 50,
            'max_depth': 3,
            'request_delay': 2.0,
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
