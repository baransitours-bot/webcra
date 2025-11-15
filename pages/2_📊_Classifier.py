"""
Classifier Service Page
Extract structured visa data from crawled pages
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

st.set_page_config(page_title="Classifier Service", page_icon="📊", layout="wide")

st.title("📊 Classifier Service")
st.markdown("Extract structured visa data from crawled pages using LLM")

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["⚙️ Configuration", "▶️ Run", "📊 Results"])

with tab1:
    st.subheader("⚙️ Configuration")

    # Config mode
    config_mode = st.radio(
        "Configuration Mode",
        ["Use Default Config", "Custom Configuration"],
        help="Choose how to configure the classifier"
    )

    if config_mode == "Custom Configuration":
        st.markdown("### Custom Settings")

        col1, col2 = st.columns(2)

        with col1:
            # LLM Provider
            llm_provider = st.selectbox(
                "LLM Provider",
                ["openrouter", "openai"],
                index=0,
                help="OpenRouter is FREE with some models"
            )

            # Model selection
            if llm_provider == "openrouter":
                model_options = [
                    "google/gemini-2.0-flash-001:free",
                    "meta-llama/llama-3.2-3b-instruct:free",
                    "microsoft/phi-3-mini-128k-instruct:free"
                ]
                default_model = "google/gemini-2.0-flash-001:free"
            else:
                model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
                default_model = "gpt-4o-mini"

            model = st.selectbox(
                "Model",
                model_options,
                index=0
            )

        with col2:
            # Batch size
            batch_size = st.number_input(
                "Batch Size",
                min_value=1,
                max_value=50,
                value=5,
                help="Number of pages to process at once"
            )

            # Country filter
            countries_filter = st.multiselect(
                "Process Only These Countries",
                ["australia", "canada", "uk", "germany", "usa", "uae"],
                default=[],
                help="Leave empty to process all"
            )

        # API Key
        st.markdown("### API Key")
        api_key_input = st.text_input(
            f"{llm_provider.upper()} API Key",
            type="password",
            help="Enter your API key or leave empty to use environment variable"
        )

        # Save config
        st.session_state['classifier_config'] = {
            'llm_provider': llm_provider,
            'model': model,
            'batch_size': batch_size,
            'countries_filter': countries_filter,
            'api_key': api_key_input
        }

        st.success("✅ Custom configuration saved")

    else:
        st.info("""
        **Default Configuration:**
        - LLM Provider: OpenRouter (FREE)
        - Model: google/gemini-2.0-flash-001:free
        - Batch Size: 5 pages
        - Countries: All

        **Note:** Set OPENROUTER_API_KEY environment variable
        """)

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
            'api_key': ''
        }

    # Show current config
    st.markdown("#### Current Configuration:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Provider", config['llm_provider'].upper())
    with col2:
        st.metric("Model", config['model'].split('/')[-1][:20])
    with col3:
        st.metric("Batch Size", config['batch_size'])

    # Check data source
    st.markdown("---")
    st.markdown("#### Data Source:")

    data_source = st.radio(
        "Source",
        ["Database (Crawled Pages)", "Files (data/raw/)"],
        help="Choose where to load crawled pages from"
    )

    # Show available data
    if data_source == "Database (Crawled Pages)":
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
                for country, count in by_country.items():
                    st.write(f"- {country.title()}: {count} pages")
            else:
                st.warning("⚠️ No crawled pages found in database. Run Crawler first!")
                st.stop()

        except Exception as e:
            st.error(f"❌ Error loading from database: {str(e)}")
            st.stop()

    else:
        raw_dir = Path("data/raw")
        if not raw_dir.exists():
            st.error("❌ data/raw directory not found!")
            st.stop()

        files = list(raw_dir.rglob("*.json"))
        if files:
            st.success(f"✅ Found {len(files)} JSON files")
        else:
            st.warning("⚠️ No files found in data/raw/. Run Crawler first!")
            st.stop()

    st.markdown("---")

    # Run button
    if st.button("▶️ Start Classification", type="primary", use_container_width=True):

        progress_container = st.container()

        with progress_container:
            st.markdown("### 🔄 Classification in Progress...")

            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Log area
            log_container = st.expander("📋 Live Logs", expanded=True)

            with log_container:
                log_area = st.empty()

                import time
                logs = []

                try:
                    from shared.database import Database
                    import yaml
                    import os

                    # Load classifier config
                    with open('services/classifier/config.yaml', 'r') as f:
                        classifier_config = yaml.safe_load(f)

                    # Override with user settings
                    classifier_config['llm']['provider'] = config['llm_provider']

                    if config['llm_provider'] == 'openrouter':
                        classifier_config['llm']['openrouter']['model'] = config['model']
                        if config['api_key']:
                            os.environ['OPENROUTER_API_KEY'] = config['api_key']
                    else:
                        classifier_config['llm']['openai']['model'] = config['model']
                        if config['api_key']:
                            os.environ['OPENAI_API_KEY'] = config['api_key']

                    logs.append(f"[INFO] Starting classification...")
                    logs.append(f"[INFO] Provider: {config['llm_provider']}")
                    logs.append(f"[INFO] Model: {config['model']}")
                    log_area.code('\n'.join(logs))

                    # Load pages from database
                    db = Database()
                    pages = db.get_latest_pages()

                    # Filter by country if needed
                    if config['countries_filter']:
                        pages = [p for p in pages if p['country'] in config['countries_filter']]

                    total_pages = len(pages)
                    logs.append(f"[INFO] Processing {total_pages} pages...")
                    log_area.code('\n'.join(logs))

                    # Process in batches
                    from services.classifier.visa_extractor import VisaExtractor

                    extractor = VisaExtractor(classifier_config)
                    all_visas = []
                    pages_processed = 0

                    status_text.text(f"Processing... (0/{total_pages} pages)")
                    progress_bar.progress(0.1)

                    for i, page in enumerate(pages):
                        try:
                            logs.append(f"\n[INFO] Processing: {page['title'][:60]}...")
                            log_area.code('\n'.join(logs[-20:]))

                            # Extract visa from page content
                            visa_data = extractor.extract_visa_from_text(
                                page['content'],
                                page['country']
                            )

                            if visa_data:
                                # Save to database
                                db.save_visa(
                                    visa_type=visa_data.get('visa_type', 'Unknown'),
                                    country=page['country'],
                                    category=visa_data.get('category', 'unknown'),
                                    requirements=visa_data.get('requirements', {}),
                                    fees=visa_data.get('fees', {}),
                                    processing_time=visa_data.get('processing_time', 'Not specified'),
                                    documents_required=visa_data.get('documents_required', []),
                                    timeline_stages=visa_data.get('timeline_stages', {}),
                                    cost_breakdown=visa_data.get('cost_breakdown', {}),
                                    source_urls=[page['url']]
                                )

                                all_visas.append(visa_data)
                                logs.append(f"[SUCCESS] Extracted: {visa_data.get('visa_type', 'Unknown')}")
                            else:
                                logs.append(f"[WARNING] No visa data found in page")

                            pages_processed += 1
                            progress = pages_processed / total_pages
                            progress_bar.progress(progress)
                            status_text.text(f"Processing... ({pages_processed}/{total_pages} pages)")
                            log_area.code('\n'.join(logs[-20:]))

                            # Small delay to avoid rate limiting
                            time.sleep(0.5)

                        except Exception as e:
                            logs.append(f"[ERROR] Failed to process page: {str(e)}")
                            log_area.code('\n'.join(logs[-20:]))
                            continue

                    # Completion
                    progress_bar.progress(1.0)
                    status_text.text(f"✅ Completed! Processed {pages_processed} pages, extracted {len(all_visas)} visas")

                    logs.append(f"\n[SUCCESS] Classification completed!")
                    logs.append(f"[INFO] Total pages processed: {pages_processed}")
                    logs.append(f"[INFO] Total visas extracted: {len(all_visas)}")
                    logs.append(f"[INFO] Data saved to database with versioning")
                    log_area.code('\n'.join(logs))

                    # Save results to session
                    st.session_state['classifier_results'] = {
                        'pages_processed': pages_processed,
                        'visas_extracted': len(all_visas),
                        'visas': all_visas,
                        'status': 'completed'
                    }

                    st.success(f"✅ Classification completed! Extracted {len(all_visas)} visas")
                    st.info("📂 View results in the **Results** tab")

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

        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pages Processed", results['pages_processed'])
        with col2:
            st.metric("Visas Extracted", results['visas_extracted'])
        with col3:
            st.metric("Status", results['status'].upper())

        st.markdown("---")

        # Visas preview
        if results['visas']:
            st.markdown("#### Extracted Visas:")

            for i, visa in enumerate(results['visas'][:10], 1):
                with st.expander(f"{i}. {visa.get('visa_type', 'Unknown')} ({visa.get('country', 'Unknown')})"):
                    st.json(visa)

            if len(results['visas']) > 10:
                st.info(f"... and {len(results['visas']) - 10} more visas")

        st.markdown("---")

        # Database stats
        st.markdown("#### Database Statistics:")

        try:
            from shared.database import Database
            db = Database()
            stats = db.get_stats()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Pages", stats['pages_crawled'])
            with col2:
                st.metric("Total Visas", stats['visas_total'])
            with col3:
                st.metric("Countries", stats['countries'])
            with col4:
                st.metric("Checks", stats['checks_performed'])

        except Exception as e:
            st.error(f"Error loading stats: {str(e)}")

        st.markdown("---")

        st.info("""
        **Next Step:**
        Go to the **Matcher Service** to check client eligibility against extracted visas
        """)

    else:
        st.info("No classification results yet. Run the classifier from the **Run** tab.")

st.markdown("---")
st.caption("Classifier Service - Part of Immigration Platform")
