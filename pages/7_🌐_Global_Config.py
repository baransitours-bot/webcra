"""
Global Configuration Manager
Manage countries, seed URLs, keywords, and system settings

Uses ConfigManager for centralized configuration with priority:
.env > Database > YAML defaults
"""

import streamlit as st
import yaml
from pathlib import Path
import json
import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.config_manager import get_config

st.set_page_config(
    page_title="Global Config",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Global Configuration")
st.markdown("""
**Centralized Configuration Management**
- Changes are saved to database
- Database overrides YAML defaults
- Reset button restores YAML defaults
""")

# Get config manager
config_mgr = get_config()

# Tabs
tabs = st.tabs(["🌍 Countries", "🔑 Keywords", "🏷️ Visa Categories", "📊 Extraction Schema", "⚙️ System", "🔄 Reset"])

# ============ TAB 1: Countries ============
with tabs[0]:
    st.markdown("### Manage Countries")
    st.info("Configure countries for crawling. Changes are saved to database and override YAML defaults.")

    # Add new country
    with st.expander("➕ Add New Country", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            new_country_key = st.text_input("Country Key (lowercase)", placeholder="japan", key="new_key")
            new_country_name = st.text_input("Country Name", placeholder="Japan", key="new_name")

        with col2:
            new_country_code = st.text_input("Country Code", placeholder="JP", key="new_code")
            new_base_url = st.text_input("Base URL", placeholder="https://www.mofa.go.jp", key="new_base")

        with col3:
            st.markdown("**Seed URLs** (one per line)")
            new_seed_urls = st.text_area(
                "Seed URLs",
                placeholder="https://www.mofa.go.jp/j_info/visit/visa/\nhttps://...",
                height=100,
                label_visibility="collapsed",
                key="new_seeds"
            )

        if st.button("➕ Add Country", type="primary"):
            if new_country_key and new_country_name:
                seed_urls_list = [url.strip() for url in new_seed_urls.split('\n') if url.strip()]

                success = config_mgr.add_country(
                    code=new_country_key,
                    name=new_country_name,
                    base_url=new_base_url,
                    seed_urls=seed_urls_list
                )

                if success:
                    st.success(f"✅ Added {new_country_name}")
                    st.rerun()
                else:
                    st.error("❌ Failed to add country")
            else:
                st.error("Country key and name are required")

    st.markdown("---")
    st.markdown("### Current Countries")

    # Get current countries
    countries = config_mgr.get_countries()

    if not countries:
        st.warning("No countries configured. Add one above to get started.")
    else:
        # Display existing countries
        for country_key, country_data in countries.items():
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

                        success = config_mgr.add_country(
                            code=country_key,
                            name=name,
                            base_url=base_url,
                            seed_urls=seed_urls_list
                        )

                        if success:
                            st.success(f"✅ Updated {name}")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update country")

                with col2:
                    st.markdown("**Actions**")

                    # Delete button
                    if st.button(f"🗑️ Delete", key=f"del_{country_key}", type="secondary"):
                        success = config_mgr.remove_country(country_key)
                        if success:
                            st.success(f"Deleted {country_key}")
                            st.rerun()
                        else:
                            st.error("Failed to delete")

                    # Stats
                    st.metric("Seed URLs", len(country_data.get('seed_urls', [])))

# ============ TAB 2: Keywords ============
with tabs[1]:
    st.markdown("### Manage Keywords")
    st.info("Keywords used for filtering relevant pages during crawling. Saved to database.")

    # Current keywords
    current_keywords = config_mgr.get_list_config('keywords', [])

    # Edit keywords
    keywords_text = st.text_area(
        "Keywords (one per line)",
        value='\n'.join(current_keywords),
        height=300,
        help="Add keywords that indicate visa/immigration content"
    )

    if st.button("💾 Save Keywords", type="primary"):
        keywords_list = [kw.strip() for kw in keywords_text.split('\n') if kw.strip()]
        success = config_mgr.set_list_config('keywords', keywords_list)

        if success:
            st.success(f"✅ Saved {len(keywords_list)} keywords")
            st.rerun()
        else:
            st.error("❌ Failed to save keywords")

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
                    current_keywords.append(kw)
                    config_mgr.set_list_config('keywords', current_keywords)
                    st.rerun()

# ============ TAB 3: Visa Categories ============
with tabs[2]:
    st.markdown("### Manage Visa Categories")
    st.info("Categories used by the classifier to categorize visas. Saved to database.")

    # Current categories
    current_categories = config_mgr.get_list_config('visa_categories', [])

    # Edit categories
    categories_text = st.text_area(
        "Visa Categories (one per line)",
        value='\n'.join(current_categories),
        height=200,
        help="Add visa categories for classification"
    )

    if st.button("💾 Save Categories", type="primary"):
        categories_list = [cat.strip() for cat in categories_text.split('\n') if cat.strip()]
        success = config_mgr.set_list_config('visa_categories', categories_list)

        if success:
            st.success(f"✅ Saved {len(categories_list)} categories")
            st.rerun()
        else:
            st.error("❌ Failed to save categories")

    st.markdown("---")
    st.markdown("### Category Keywords")
    st.info("Configure keywords for each visa category to improve classification accuracy.")

    # Get current keyword mappings
    visa_keywords = config_mgr.get_dict_config('visa_type_keywords', 'classifier', {})

    # Allow editing for each category
    for category in current_categories:
        with st.expander(f"🏷️ {category.title()}", expanded=False):
            current_kw = visa_keywords.get(category, [])
            kw_text = st.text_area(
                f"Keywords for {category} (one per line)",
                value='\n'.join(current_kw) if current_kw else '',
                height=150,
                key=f"cat_kw_{category}"
            )

            if st.button(f"💾 Save {category} keywords", key=f"save_cat_{category}"):
                kw_list = [k.strip() for k in kw_text.split('\n') if k.strip()]
                visa_keywords[category] = kw_list
                success = config_mgr.set_dict_config('visa_type_keywords', visa_keywords)

                if success:
                    st.success(f"✅ Updated {category} keywords")
                    st.rerun()
                else:
                    st.error("❌ Failed to update keywords")

# ============ TAB 4: Extraction Schema ============
with tabs[3]:
    st.markdown("### Extraction Schema Configuration")
    st.info("Configure which fields the Classifier extracts from visa pages. More fields = more comprehensive data but slower processing and higher LLM costs.")

    # Import schema presets
    from shared.extraction_schema import SCHEMA_PRESETS, get_default_schema, validate_schema

    # Get current schema
    current_schema = config_mgr.get_extraction_schema()

    # Determine current preset (if any)
    current_preset = None
    for preset_name, preset_config in SCHEMA_PRESETS.items():
        if preset_config.get('fields') == current_schema.get('fields'):
            current_preset = preset_name
            break

    st.markdown("#### Quick Presets")

    # Display preset options
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🎯 Basic**")
        st.caption(SCHEMA_PRESETS['basic']['description'])
        st.write("**Extracts:**")
        st.write("• Visa type & category")
        st.write("• Basic requirements")
        st.write("• Application fee")
        st.write("• Processing time")

        if st.button("📥 Load Basic", type="secondary" if current_preset != 'basic' else "primary", key="load_basic"):
            success = config_mgr.load_schema_preset('basic')
            if success:
                st.success("✅ Loaded Basic schema")
                st.rerun()
            else:
                st.error("❌ Failed to load preset")

    with col2:
        st.markdown("**⚖️ Standard** (Recommended)")
        st.caption(SCHEMA_PRESETS['standard']['description'])
        st.write("**Extracts:**")
        st.write("• All Basic fields")
        st.write("• Detailed requirements")
        st.write("• Full fee breakdown")
        st.write("• Documents & eligibility")
        st.write("• Benefits & rights")

        if st.button("📥 Load Standard", type="secondary" if current_preset != 'standard' else "primary", key="load_standard"):
            success = config_mgr.load_schema_preset('standard')
            if success:
                st.success("✅ Loaded Standard schema")
                st.rerun()
            else:
                st.error("❌ Failed to load preset")

    with col3:
        st.markdown("**🔬 Comprehensive**")
        st.caption(SCHEMA_PRESETS['comprehensive']['description'])
        st.write("**Extracts:**")
        st.write("• All Standard fields")
        st.write("• Cost breakdown")
        st.write("• Timeline stages")
        st.write("• Renewal information")
        st.write("• Restrictions & conditions")
        st.write("• Appeal process")

        if st.button("📥 Load Comprehensive", type="secondary" if current_preset != 'comprehensive' else "primary", key="load_comprehensive"):
            success = config_mgr.load_schema_preset('comprehensive')
            if success:
                st.success("✅ Loaded Comprehensive schema")
                st.rerun()
            else:
                st.error("❌ Failed to load preset")

    st.markdown("---")
    st.markdown("#### Current Schema")

    # Show current preset or custom
    if current_preset:
        st.success(f"**Active Preset:** {SCHEMA_PRESETS[current_preset]['name']} - {SCHEMA_PRESETS[current_preset]['description']}")
    else:
        st.info("**Active Schema:** Custom configuration")

    # Count enabled fields
    enabled_fields = [f for f, cfg in current_schema.get('fields', {}).items() if cfg.get('enabled', False)]
    st.metric("Enabled Fields", len(enabled_fields))

    # Show enabled fields
    with st.expander("📋 View Enabled Fields", expanded=False):
        for field_name in enabled_fields:
            field_config = current_schema['fields'][field_name]

            # Show field name
            st.markdown(f"**{field_name.replace('_', ' ').title()}**")

            # Show subfields if any
            if 'subfields' in field_config:
                enabled_subfields = [sf for sf, enabled in field_config['subfields'].items() if enabled]
                st.caption(f"  └─ Subfields: {', '.join(enabled_subfields)}")

            st.markdown("")

    st.markdown("---")
    st.markdown("#### Advanced: Custom Configuration")

    with st.expander("⚙️ Customize Schema (Advanced)", expanded=False):
        st.warning("⚠️ Custom configurations will override preset selections. Only modify if you need specific field combinations.")

        # Show all available fields with toggles
        st.markdown("**Enable/Disable Fields:**")

        custom_config = current_schema.copy()
        fields = custom_config.get('fields', {})

        # Group fields by category
        st.markdown("**Core Fields** (Required)")
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("Visa Type", value=True, disabled=True, help="Required field")
        with col2:
            st.checkbox("Country", value=True, disabled=True, help="Required field")

        st.markdown("**Basic Information**")
        for field_name in ['category', 'processing_time', 'documents_required']:
            if field_name in fields:
                fields[field_name]['enabled'] = st.checkbox(
                    field_name.replace('_', ' ').title(),
                    value=fields[field_name].get('enabled', False),
                    key=f"toggle_{field_name}"
                )

        st.markdown("**Requirements & Eligibility**")
        for field_name in ['requirements', 'eligibility']:
            if field_name in fields:
                fields[field_name]['enabled'] = st.checkbox(
                    field_name.replace('_', ' ').title(),
                    value=fields[field_name].get('enabled', False),
                    key=f"toggle_{field_name}"
                )

        st.markdown("**Costs & Fees**")
        for field_name in ['fees', 'cost_breakdown']:
            if field_name in fields:
                fields[field_name]['enabled'] = st.checkbox(
                    field_name.replace('_', ' ').title(),
                    value=fields[field_name].get('enabled', False),
                    key=f"toggle_{field_name}"
                )

        st.markdown("**Timeline & Processing**")
        for field_name in ['timeline_stages']:
            if field_name in fields:
                fields[field_name]['enabled'] = st.checkbox(
                    field_name.replace('_', ' ').title(),
                    value=fields[field_name].get('enabled', False),
                    key=f"toggle_{field_name}"
                )

        st.markdown("**Benefits & Rights**")
        for field_name in ['benefits']:
            if field_name in fields:
                fields[field_name]['enabled'] = st.checkbox(
                    field_name.replace('_', ' ').title(),
                    value=fields[field_name].get('enabled', False),
                    key=f"toggle_{field_name}"
                )

        st.markdown("**Restrictions & Conditions**")
        for field_name in ['restrictions', 'conditions', 'renewal', 'appeal_process']:
            if field_name in fields:
                fields[field_name]['enabled'] = st.checkbox(
                    field_name.replace('_', ' ').title(),
                    value=fields[field_name].get('enabled', False),
                    key=f"toggle_{field_name}"
                )

        # Save custom configuration
        if st.button("💾 Save Custom Configuration", type="primary"):
            custom_config['fields'] = fields
            is_valid, errors = validate_schema(custom_config)

            if not is_valid:
                st.error(f"❌ Invalid schema: {', '.join(errors)}")
            else:
                success = config_mgr.set_extraction_schema(custom_config)
                if success:
                    st.success("✅ Custom schema saved")
                    st.rerun()
                else:
                    st.error("❌ Failed to save schema")

    st.markdown("---")
    st.markdown("#### Schema Preview")

    with st.expander("🔍 View JSON Schema", expanded=False):
        st.json(current_schema)

    # Performance impact info
    st.markdown("---")
    st.markdown("### 📊 Performance Impact")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Basic", "~500 tokens", "Fast & Cheap")
        st.caption("✅ Best for quick classification")

    with col2:
        st.metric("Standard", "~1000 tokens", "Balanced")
        st.caption("✅ Recommended for most use cases")

    with col3:
        st.metric("Comprehensive", "~2000 tokens", "Detailed")
        st.caption("⚠️ Higher cost, slower processing")

# ============ TAB 5: System Settings ============
with tabs[4]:
    st.markdown("### System Settings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Crawler Settings")

        delay = st.number_input(
            "Delay between requests (seconds)",
            min_value=0.5,
            max_value=10.0,
            value=config_mgr.get('crawler.delay', 2.0),
            step=0.5,
            help="Rate limiting delay"
        )

        max_pages = st.number_input(
            "Max pages per country",
            min_value=10,
            max_value=1000,
            value=config_mgr.get('crawler.max_pages', 50),
            step=10
        )

        max_depth = st.slider(
            "Max crawl depth",
            min_value=1,
            max_value=5,
            value=config_mgr.get('crawler.max_depth', 3),
            help="How deep to follow links"
        )

        if st.button("💾 Save Crawler Settings", type="primary"):
            config_mgr.set('crawler.delay', delay)
            config_mgr.set('crawler.max_pages', max_pages)
            config_mgr.set('crawler.max_depth', max_depth)
            st.success("✅ Crawler settings saved")
            st.rerun()

    with col2:
        st.markdown("#### LLM Settings")

        provider = st.selectbox(
            "LLM Provider",
            ["openrouter", "openai"],
            index=0 if config_mgr.get('llm.provider', 'openrouter') == 'openrouter' else 1
        )

        model = st.text_input(
            "Model",
            value=config_mgr.get('llm.model', 'google/gemini-2.0-flash-001:free'),
            help="Model identifier"
        )

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=config_mgr.get('llm.temperature', 0.3),
            step=0.1
        )

        max_tokens = st.number_input(
            "Max tokens",
            min_value=100,
            max_value=8000,
            value=config_mgr.get('llm.max_tokens', 2000),
            step=100
        )

        if st.button("💾 Save LLM Settings", type="primary"):
            config_mgr.set('llm.provider', provider)
            config_mgr.set('llm.model', model)
            config_mgr.set('llm.temperature', temperature)
            config_mgr.set('llm.max_tokens', max_tokens)
            st.success("✅ LLM settings saved")
            st.rerun()

    st.markdown("---")
    st.markdown("### Current Configuration (Database + YAML)")

    # Show effective config
    effective_config = {
        'countries': config_mgr.get_countries(),
        'keywords': config_mgr.get_list_config('keywords'),
        'visa_categories': config_mgr.get_list_config('visa_categories'),
        'crawler': {
            'delay': config_mgr.get('crawler.delay', 2.0),
            'max_pages': config_mgr.get('crawler.max_pages', 50),
            'max_depth': config_mgr.get('crawler.max_depth', 3)
        },
        'llm': config_mgr.get_llm_config()
    }

    st.code(yaml.dump(effective_config, default_flow_style=False, sort_keys=False), language='yaml')

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "📥 Download Current Config",
            data=yaml.dump(effective_config, default_flow_style=False, sort_keys=False),
            file_name="current_config.yaml",
            mime="text/yaml"
        )

    with col2:
        st.download_button(
            "📥 Download as JSON",
            data=json.dumps(effective_config, indent=2),
            file_name="current_config.json",
            mime="application/json"
        )

# ============ TAB 6: Reset ============
with tabs[5]:
    st.markdown("### Reset Configuration")

    st.warning("""
    **⚠️ Warning: This will reset ALL database settings to YAML defaults**

    This action will:
    - Delete all custom countries from database
    - Delete all custom keywords from database
    - Delete all custom visa categories from database
    - Delete all system settings from database
    - Revert to YAML file defaults

    YAML files will NOT be modified.
    """)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("🔄 Reset to YAML Defaults", type="secondary"):
            success = config_mgr.reset_to_defaults()

            if success:
                st.success("✅ Configuration reset to YAML defaults!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Failed to reset configuration")

st.markdown("---")

# Quick stats
st.markdown("### 📊 Quick Stats")

col1, col2, col3, col4 = st.columns(4)

countries = config_mgr.get_countries()
keywords = config_mgr.get_list_config('keywords')
visa_cats = config_mgr.get_list_config('visa_categories')

with col1:
    st.metric("Countries", len(countries))

with col2:
    total_seeds = sum(len(c.get('seed_urls', [])) for c in countries.values())
    st.metric("Total Seed URLs", total_seeds)

with col3:
    st.metric("Keywords", len(keywords))

with col4:
    st.metric("Visa Categories", len(visa_cats))
