"""
Global Configuration Manager
Manage countries, seed URLs, keywords, and system settings
"""

import streamlit as st
import yaml
from pathlib import Path
import json

st.set_page_config(
    page_title="Global Config",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Global Configuration")
st.markdown("Manage countries, seed URLs, keywords, and system settings")

# Load global config
config_path = Path('config.yaml')

def load_config():
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def save_config(config_data):
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

config = load_config()

# Tabs
tabs = st.tabs(["🌍 Countries", "🔑 Keywords", "📁 Paths", "💾 Save"])

# ============ TAB 1: Countries ============
with tabs[0]:
    st.markdown("### Manage Countries")

    # Add new country
    with st.expander("➕ Add New Country", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            new_country_key = st.text_input("Country Key (lowercase)", placeholder="japan")
            new_country_name = st.text_input("Country Name", placeholder="Japan")

        with col2:
            new_country_code = st.text_input("Country Code", placeholder="JP")
            new_base_url = st.text_input("Base URL", placeholder="https://www.mofa.go.jp")

        with col3:
            st.markdown("**Seed URLs** (one per line)")
            new_seed_urls = st.text_area(
                "Seed URLs",
                placeholder="https://www.mofa.go.jp/j_info/visit/visa/\nhttps://...",
                height=100,
                label_visibility="collapsed"
            )

        if st.button("➕ Add Country", type="primary"):
            if new_country_key and new_country_name:
                seed_urls_list = [url.strip() for url in new_seed_urls.split('\n') if url.strip()]

                config['countries'][new_country_key] = {
                    'name': new_country_name,
                    'code': new_country_code,
                    'base_url': new_base_url,
                    'seed_urls': seed_urls_list
                }

                save_config(config)
                st.success(f"✅ Added {new_country_name}")
                st.rerun()
            else:
                st.error("Country key and name are required")

    st.markdown("---")
    st.markdown("### Current Countries")

    # Display existing countries
    for country_key, country_data in config.get('countries', {}).items():
        with st.expander(f"🌍 {country_data.get('name', country_key)} ({country_key})", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                # Editable fields
                name = st.text_input(
                    "Name",
                    value=country_data.get('name', ''),
                    key=f"name_{country_key}"
                )

                code = st.text_input(
                    "Code",
                    value=country_data.get('code', ''),
                    key=f"code_{country_key}"
                )

                base_url = st.text_input(
                    "Base URL",
                    value=country_data.get('base_url', ''),
                    key=f"base_{country_key}"
                )

                # Seed URLs
                current_seeds = '\n'.join(country_data.get('seed_urls', []))
                seed_urls = st.text_area(
                    "Seed URLs (one per line)",
                    value=current_seeds,
                    height=100,
                    key=f"seeds_{country_key}"
                )

                # Update button
                if st.button(f"💾 Save Changes", key=f"save_{country_key}"):
                    seed_urls_list = [url.strip() for url in seed_urls.split('\n') if url.strip()]

                    config['countries'][country_key] = {
                        'name': name,
                        'code': code,
                        'base_url': base_url,
                        'seed_urls': seed_urls_list
                    }

                    save_config(config)
                    st.success(f"✅ Updated {name}")
                    st.rerun()

            with col2:
                st.markdown("**Actions**")

                # Delete button
                if st.button(f"🗑️ Delete", key=f"del_{country_key}", type="secondary"):
                    del config['countries'][country_key]
                    save_config(config)
                    st.success(f"Deleted {country_key}")
                    st.rerun()

                # Stats
                st.metric("Seed URLs", len(country_data.get('seed_urls', [])))

# ============ TAB 2: Keywords ============
with tabs[1]:
    st.markdown("### Manage Keywords")
    st.info("Keywords used for filtering relevant pages during crawling")

    # Current keywords
    current_keywords = config.get('keywords', [])

    # Edit keywords
    keywords_text = st.text_area(
        "Keywords (one per line)",
        value='\n'.join(current_keywords),
        height=300,
        help="Add keywords that indicate visa/immigration content"
    )

    if st.button("💾 Save Keywords", type="primary"):
        keywords_list = [kw.strip() for kw in keywords_text.split('\n') if kw.strip()]
        config['keywords'] = keywords_list
        save_config(config)
        st.success(f"✅ Saved {len(keywords_list)} keywords")
        st.rerun()

    st.markdown("---")
    st.markdown("### Suggested Keywords")

    suggested = [
        "visa", "immigration", "permit", "residence", "eligibility",
        "requirements", "application", "citizenship", "work permit",
        "study permit", "tourist visa", "business visa", "family visa",
        "skilled worker", "express entry", "permanent residence"
    ]

    cols = st.columns(4)
    for i, kw in enumerate(suggested):
        with cols[i % 4]:
            if st.button(f"➕ {kw}", key=f"add_kw_{i}"):
                if kw not in current_keywords:
                    config['keywords'].append(kw)
                    save_config(config)
                    st.rerun()

# ============ TAB 3: Paths ============
with tabs[2]:
    st.markdown("### Storage Paths")

    storage = config.get('storage', {})

    raw_path = st.text_input(
        "Raw Data Path",
        value=storage.get('raw_data_path', 'data/raw'),
        help="Where to store raw crawled pages"
    )

    processed_path = st.text_input(
        "Processed Data Path",
        value=storage.get('processed_data_path', 'data/processed'),
        help="Where to store processed/classified data"
    )

    db_path = st.text_input(
        "Database Path",
        value=storage.get('database_path', 'data/database'),
        help="Where to store database files"
    )

    if st.button("💾 Save Paths", type="primary"):
        config['storage'] = {
            'raw_data_path': raw_path,
            'processed_data_path': processed_path,
            'database_path': db_path
        }
        save_config(config)
        st.success("✅ Paths updated")
        st.rerun()

    st.markdown("---")
    st.markdown("### Project Info")

    project = config.get('project', {})

    project_name = st.text_input(
        "Project Name",
        value=project.get('name', 'Immigration Platform')
    )

    project_version = st.text_input(
        "Version",
        value=project.get('version', '0.1.0')
    )

    if st.button("💾 Save Project Info", type="primary"):
        config['project'] = {
            'name': project_name,
            'version': project_version
        }
        save_config(config)
        st.success("✅ Project info updated")
        st.rerun()

# ============ TAB 4: Save/Export ============
with tabs[3]:
    st.markdown("### Current Configuration")

    st.code(yaml.dump(config, default_flow_style=False, sort_keys=False), language='yaml')

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "📥 Download YAML",
            data=yaml.dump(config, default_flow_style=False, sort_keys=False),
            file_name="config.yaml",
            mime="text/yaml"
        )

    with col2:
        st.download_button(
            "📥 Download JSON",
            data=json.dumps(config, indent=2),
            file_name="config.json",
            mime="application/json"
        )

    with col3:
        if st.button("🔄 Reload from File"):
            config = load_config()
            st.success("✅ Reloaded")
            st.rerun()

    st.markdown("---")
    st.markdown("### Import Configuration")

    uploaded_file = st.file_uploader("Upload config.yaml", type=['yaml', 'yml'])

    if uploaded_file:
        try:
            new_config = yaml.safe_load(uploaded_file)

            st.success("✅ File loaded successfully")
            st.json(new_config)

            if st.button("💾 Apply This Configuration", type="primary"):
                save_config(new_config)
                st.success("✅ Configuration updated!")
                st.rerun()
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")

st.markdown("---")

# Quick stats
st.markdown("### 📊 Quick Stats")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Countries", len(config.get('countries', {})))

with col2:
    total_seeds = sum(len(c.get('seed_urls', [])) for c in config.get('countries', {}).values())
    st.metric("Total Seed URLs", total_seeds)

with col3:
    st.metric("Keywords", len(config.get('keywords', [])))

with col4:
    st.metric("Version", config.get('project', {}).get('version', 'N/A'))
