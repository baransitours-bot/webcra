"""
Classifier Service Page - Fixed Version
Extract structured visa data using LLM with full customization
"""

import streamlit as st
import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.service_config import get_service_config

st.set_page_config(page_title="Classifier Service", page_icon="📊", layout="wide")

st.title("📊 Classifier Service")
st.markdown("Extract structured visa data from crawled pages using LLM")

# Load defaults from Global Config
config_loader = get_service_config()
global_llm_config = config_loader.get_classifier_config()['llm']

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["⚙️ Configuration", "▶️ Run", "📊 Results"])

with tab1:
    st.subheader("⚙️ LLM Configuration")

    # Show global config defaults
    st.info(f"""
    **Global Config Defaults:**
    - Provider: {global_llm_config.get('provider', 'openrouter').upper()}
    - Model: {global_llm_config.get('model', 'google/gemini-2.0-flash-001:free')}

    You can override these settings below, or use them as-is.
    To change defaults permanently, go to 🌐 Global Config page.
    """)

    col1, col2 = st.columns([1, 1])

    with col1:
        # Provider - default from Global Config
        default_provider = global_llm_config.get('provider', 'openrouter')
        provider_options = ["openrouter", "openai"]
        provider_index = provider_options.index(default_provider) if default_provider in provider_options else 0

        llm_provider = st.selectbox(
            "LLM Provider",
            provider_options,
            index=provider_index,
            help="OpenRouter offers FREE models. Default from Global Config."
        )

        # Custom model checkbox
        use_custom_model = st.checkbox(
            "🎯 Use Custom Model",
            value=False,
            help="Enter any model name from your provider"
        )

    with col2:
        if use_custom_model:
            # Custom model input - default from Global Config
            default_model = global_llm_config.get('model', 'google/gemini-2.0-flash-001:free')
            model = st.text_input(
                "Custom Model Name",
                value=default_model,
                placeholder="e.g., google/gemini-pro, anthropic/claude-3.5-sonnet",
                help="Enter the FULL model name from your provider. Default from Global Config."
            )

            st.info(f"""
            **Common {llm_provider.upper()} models:**
            - OpenRouter: `google/gemini-2.0-flash-001:free`, `anthropic/claude-3.5-sonnet`, `openai/gpt-4o`
            - OpenAI: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`

            Get model names from:
            - OpenRouter: https://openrouter.ai/models
            - OpenAI: https://platform.openai.com/docs/models
            """)
        else:
            # Predefined models
            default_model = global_llm_config.get('model', 'google/gemini-2.0-flash-001:free')

            if llm_provider == "openrouter":
                model_options = [
                    "google/gemini-2.0-flash-001:free",
                    "meta-llama/llama-3.2-3b-instruct:free",
                    "anthropic/claude-3.5-sonnet",
                    "google/gemini-pro",
                    "openai/gpt-4o-mini",
                    "x-ai/grok-2-1212",
                    "x-ai/grok-vision-beta"
                ]
            else:
                model_options = [
                    "gpt-4o-mini",
                    "gpt-4o",
                    "gpt-4-turbo",
                    "gpt-3.5-turbo"
                ]

            # Find default model index
            try:
                default_index = model_options.index(default_model)
            except ValueError:
                # If global config model not in list, add it and select it
                model_options.insert(0, default_model)
                default_index = 0

            model = st.selectbox(
                "Model",
                model_options,
                index=default_index,
                help="Select a predefined model. Default from Global Config."
            )

    st.markdown("---")

    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        col1, col2 = st.columns(2)

        with col1:
            batch_size = st.number_input(
                "Batch Size",
                min_value=1,
                max_value=50,
                value=5,
                help="Pages to process before saving"
            )

            show_llm_response = st.checkbox(
                "Show LLM Responses",
                value=False,
                help="Display raw LLM output for debugging"
            )

        with col2:
            # Country filter
            countries_filter = st.multiselect(
                "Filter by Countries",
                ["australia", "canada", "uk", "germany", "usa", "uae", "china", "japan"],
                default=[],
                help="Leave empty to process all countries"
            )

    # API Key
    st.markdown("---")
    st.markdown("### 🔑 API Key (Optional)")
    api_key_input = st.text_input(
        f"{llm_provider.upper()} API Key",
        type="password",
        help="Leave empty to use .env file",
        placeholder="sk-... (optional if already in .env)"
    )

    # Save config to session
    st.session_state['classifier_config'] = {
        'llm_provider': llm_provider,
        'model': model,
        'batch_size': batch_size,
        'countries_filter': countries_filter,
        'api_key': api_key_input,
        'show_llm_response': show_llm_response
    }

    st.success("✅ Configuration saved to session")

with tab2:
    st.subheader("▶️ Run Classifier")

    # Get config
    if 'classifier_config' in st.session_state:
        config = st.session_state['classifier_config']
    else:
        config = {
            'llm_provider': 'openrouter',
            'model': 'google/gemini-2.0-flash-001:free',
            'batch_size': 5,
            'countries_filter': [],
            'api_key': '',
            'show_llm_response': False
        }

    # Show current config
    st.markdown("#### 📋 Current Configuration:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Provider", config['llm_provider'].upper())
    with col2:
        # Show full model name (may be long)
        model_name = config['model']
        if len(model_name) > 25:
            model_display = model_name[:22] + "..."
        else:
            model_display = model_name
        st.metric("Model", model_display)
    with col3:
        st.metric("Batch Size", config['batch_size'])
    with col4:
        api_status = "✅ Set" if config['api_key'] else "🌍 From .env"
        st.metric("API Key", api_status)

    # Show full model name
    st.caption(f"Full model: `{config['model']}`")

    # Check data source
    st.markdown("---")
    st.markdown("#### 📂 Data Source:")

    try:
        from shared.database import Database
        db = Database()
        pages = db.get_latest_pages()

        if pages:
            st.success(f"✅ Found {len(pages)} crawled pages in database")

            # Group by country
            by_country = {}
            for page in pages:
                country = page['country']
                by_country[country] = by_country.get(country, 0) + 1

            st.write("**Pages by country:**")
            for country, count in sorted(by_country.items()):
                st.write(f"- {country.title()}: {count} pages")
        else:
            st.warning("⚠️ No crawled pages found in database. Run Crawler first!")
            st.stop()

    except Exception as e:
        st.error(f"❌ Error loading from database: {str(e)}")
        st.stop()

    st.markdown("---")

    # Run button
    if st.button("▶️ Start Classification", type="primary"):

        progress_container = st.container()

        with progress_container:
            st.markdown("### 🔄 Classification in Progress...")

            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Log area
            log_container = st.expander("📋 Live Logs", expanded=True)

            # LLM response area (if enabled)
            if config['show_llm_response']:
                llm_response_container = st.expander("🤖 LLM Responses (Debug)", expanded=False)

            with log_container:
                log_area = st.empty()

                import time
                import os
                logs = []
                all_visas = []
                # Use dict for mutable state tracking
                state = {'total_pages': 0, 'pages_processed': 0}

                try:
                    # Set API key in environment if provided
                    if config['api_key']:
                        if config['llm_provider'] == 'openrouter':
                            os.environ['OPENROUTER_API_KEY'] = config['api_key']
                        else:
                            os.environ['OPENAI_API_KEY'] = config['api_key']

                    # Override ConfigManager settings
                    from shared.config_manager import get_config
                    cfg_manager = get_config()
                    cfg_manager.set('llm.provider', config['llm_provider'])
                    cfg_manager.set('llm.model', config['model'])

                    logs.append(f"[INFO] Starting classification...")
                    logs.append(f"[INFO] Provider: {config['llm_provider']}")
                    logs.append(f"[INFO] Model: {config['model']}")
                    logs.append(f"[INFO] Debug mode: {'ON' if config['show_llm_response'] else 'OFF'}")
                    log_area.code('\n'.join(logs))

                    # Use ClassifierController
                    from services.classifier.interface import ClassifierController
                    controller = ClassifierController()

                    # Determine country filter
                    country_filter = config['countries_filter'][0] if config['countries_filter'] else None

                    # Define callbacks
                    def on_start(total):
                        state['total_pages'] = total
                        logs.append(f"[INFO] Classification started...")
                        logs.append(f"[INFO] Found {total} pages to process")
                        log_area.code('\n'.join(logs))

                    def on_page(current, total, page_title):
                        state['total_pages'] = total
                        state['pages_processed'] = current

                        logs.append(f"\n[{current}/{total}] Processing: {page_title[:60]}...")
                        log_area.code('\n'.join(logs[-25:]))

                        progress = current / total if total > 0 else 0
                        progress_bar.progress(max(0.05, progress))
                        status_text.text(f"Processing... ({current}/{total} pages)")

                    def on_visa_found(visa_data):
                        all_visas.append(visa_data)
                        logs.append(f"[SUCCESS] ✅ Extracted: {visa_data.get('visa_type', 'Unknown')}")
                        log_area.code('\n'.join(logs[-25:]))

                        # Show LLM response if debug mode
                        if config['show_llm_response']:
                            with llm_response_container:
                                st.markdown(f"**Visa {len(all_visas)}: {visa_data.get('visa_type', 'Unknown')}**")
                                st.json(visa_data)
                                st.markdown("---")

                        status_text.text(f"Processing... ({state['pages_processed']}/{state['total_pages']} pages, {len(all_visas)} visas found)")

                    def on_complete(result):
                        progress_bar.progress(1.0)

                        visas_count = result.get('visas_extracted', len(all_visas))
                        pages_count = result.get('pages_processed', state['pages_processed'])

                        logs.append(f"\n[SUCCESS] ==================== COMPLETED ====================")
                        logs.append(f"[INFO] Pages processed: {pages_count}")
                        logs.append(f"[INFO] Visas extracted: {visas_count}")
                        if pages_count > 0:
                            logs.append(f"[INFO] Success rate: {(visas_count/pages_count*100):.1f}%")
                        logs.append(f"[INFO] Data saved to database with versioning")
                        log_area.code('\n'.join(logs))

                        status_text.text(f"✅ Completed! Processed {pages_count} pages, extracted {visas_count} visas")

                    def on_error(error_msg):
                        logs.append(f"[ERROR] ❌ {error_msg[:100]}")
                        log_area.code('\n'.join(logs[-25:]))

                    # Run classification with callbacks
                    result = controller.classify_with_progress(
                        country=country_filter,
                        on_start=on_start,
                        on_page=on_page,
                        on_visa_found=on_visa_found,
                        on_complete=on_complete,
                        on_error=on_error
                    )

                    # Save results to session
                    st.session_state['classifier_results'] = {
                        'pages_processed': result.get('pages_processed', state['pages_processed']),
                        'visas_extracted': result.get('visas_extracted', len(all_visas)),
                        'visas': all_visas,
                        'status': 'completed',
                        'model_used': config['model']
                    }

                    st.success(f"✅ Classification completed! Extracted {len(all_visas)} visas from {result.get('pages_processed', 0)} pages")
                    st.info("📊 View results in the **Results** tab →")

                except Exception as e:
                    st.error(f"❌ Error during classification: {str(e)}")
                    logs.append(f"[ERROR] {str(e)}")
                    log_area.code('\n'.join(logs))
                    import traceback
                    st.code(traceback.format_exc())

with tab3:
    st.subheader("📊 Classification Results")

    if 'classifier_results' in st.session_state:
        results = st.session_state['classifier_results']

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pages Processed", results['pages_processed'])
        with col2:
            st.metric("Visas Extracted", results['visas_extracted'])
        with col3:
            success_rate = (results['visas_extracted'] / results['pages_processed'] * 100) if results['pages_processed'] > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with col4:
            st.metric("Model Used", results['model_used'].split('/')[-1][:15])

        st.markdown("---")

        # Show visas
        if results['visas']:
            st.markdown(f"### Extracted Visas ({len(results['visas'])})")

            for i, visa in enumerate(results['visas'], 1):
                with st.expander(f"{i}. {visa.get('visa_type', 'Unknown')} ({visa.get('category', 'unknown')})"):
                    st.json(visa)

            # Export button
            st.markdown("---")
            export_data = json.dumps(results['visas'], indent=2)
            st.download_button(
                "📥 Download Results as JSON",
                data=export_data,
                file_name=f"classified_visas_{results['model_used'].replace('/', '_')}.json",
                mime="application/json"
            )
        else:
            st.warning("⚠️ No visas were extracted. Check the logs for details.")

        st.markdown("---")
        st.info("""
        **Next Steps:**
        1. View data in 💾 **Database** page
        2. Create embeddings: `python scripts/index_embeddings.py`
        3. Test semantic search: `python scripts/search_semantic.py`
        """)

    else:
        st.info("ℹ️ No results yet. Run the classifier in the **Run** tab first.")
