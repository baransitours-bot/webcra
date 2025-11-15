"""
Crawler Service Page
Collect visa data from government websites
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

st.set_page_config(page_title="Crawler Service", page_icon="🕷️", layout="wide")

st.title("🕷️ Crawler Service")
st.markdown("Collect visa data from government websites")

st.markdown("---")

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["⚙️ Configuration", "▶️ Run", "📊 Results"])

with tab1:
    st.subheader("⚙️ Configuration")

    # Config mode selection
    config_mode = st.radio(
        "Configuration Mode",
        ["Use Default Config", "Custom Configuration"],
        help="Choose how to configure the crawler"
    )

    if config_mode == "Custom Configuration":
        st.markdown("### Custom Settings")

        col1, col2 = st.columns(2)

        with col1:
            # Countries selection
            countries = st.multiselect(
                "Countries to Crawl",
                ["australia", "canada", "uk", "germany", "usa", "uae"],
                default=["australia"],
                help="Select countries to crawl for visa information"
            )

            # Max pages
            max_pages = st.number_input(
                "Max Pages per Country",
                min_value=1,
                max_value=500,
                value=10,
                help="Maximum number of pages to crawl per country"
            )

        with col2:
            # Max depth
            max_depth = st.number_input(
                "Max Crawl Depth",
                min_value=1,
                max_value=10,
                value=3,
                help="How deep to follow links (1 = only start URLs)"
            )

            # Delay
            delay = st.number_input(
                "Delay Between Requests (seconds)",
                min_value=0.0,
                max_value=10.0,
                value=1.0,
                step=0.5,
                help="Polite crawling delay between requests"
            )

        # Store in session state
        st.session_state['crawler_config'] = {
            'countries': countries,
            'max_pages': max_pages,
            'max_depth': max_depth,
            'delay': delay
        }

        st.success("✅ Custom configuration saved to session")

    else:
        st.info("""
        **Default Configuration:**
        - Countries: Australia
        - Max Pages: 10
        - Max Depth: 3
        - Delay: 1.0 seconds
        """)

with tab2:
    st.subheader("▶️ Run Crawler")

    # Get config
    if 'crawler_config' in st.session_state:
        config = st.session_state['crawler_config']
    else:
        config = {
            'countries': ['australia'],
            'max_pages': 10,
            'max_depth': 3,
            'delay': 1.0
        }

    # Show current config
    st.markdown("#### Current Configuration:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Countries", len(config['countries']))
    with col2:
        st.metric("Max Pages", config['max_pages'])
    with col3:
        st.metric("Max Depth", config['max_depth'])
    with col4:
        st.metric("Delay", f"{config['delay']}s")

    st.markdown("---")

    # Run button
    if st.button("▶️ Start Crawling", type="primary", use_container_width=True):

        # Progress area
        progress_container = st.container()

        with progress_container:
            st.markdown("### 🔄 Crawling in Progress...")

            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Log area
            log_container = st.expander("📋 Live Logs", expanded=True)

            with log_container:
                log_area = st.empty()

                # Simulate crawling (replace with actual crawler call)
                import time
                logs = []

                try:
                    from services.crawler.spider import ImmigrationCrawler
                    import yaml

                    # Load global config (for country definitions)
                    with open('config.yaml', 'r') as f:
                        global_config = yaml.safe_load(f)

                    # Load crawler config
                    with open('services/crawler/config.yaml', 'r') as f:
                        crawler_config = yaml.safe_load(f)

                    # Override max_pages in crawler config
                    crawler_config['crawling']['max_pages_per_domain'] = config['max_pages']

                    # Get country configurations
                    countries_to_crawl = [
                        global_config['countries'][country]
                        for country in config['countries']
                        if country in global_config['countries']
                    ]

                    if not countries_to_crawl:
                        st.error("❌ No valid countries selected")
                        st.stop()

                    logs.append(f"[INFO] Starting crawler for countries: {', '.join(config['countries'])}")
                    logs.append(f"[INFO] Max pages per country: {config['max_pages']}")
                    logs.append(f"[INFO] Max depth: {config['max_depth']}")
                    log_area.code('\n'.join(logs))

                    # Initialize crawler with proper arguments
                    crawler = ImmigrationCrawler(countries_to_crawl, crawler_config)

                    logs.append(f"[INFO] Crawler initialized successfully")
                    log_area.code('\n'.join(logs))

                    # Simulate progress (since actual crawler doesn't have progress callback yet)
                    total_pages = len(config['countries']) * config['max_pages']
                    pages_crawled = 0

                    # Update status
                    status_text.text(f"Starting crawl... (0/{total_pages} pages)")
                    progress_bar.progress(0.1)

                    logs.append(f"[INFO] Beginning crawl process...")
                    log_area.code('\n'.join(logs[-20:]))

                    # Run the actual crawler
                    # Note: This will block until complete - in future we can make it async
                    crawler.crawl_all()

                    # Since we can't track real progress yet, simulate completion
                    logs.append(f"[SUCCESS] Crawling completed!")
                    logs.append(f"[INFO] Pages have been saved to data/raw/")
                    log_area.code('\n'.join(logs))

                    # Completion
                    progress_bar.progress(1.0)
                    status_text.text(f"✅ Completed! Check data/raw/ for results")

                    # Count actual files crawled
                    from pathlib import Path
                    raw_dir = Path("data/raw")
                    actual_files = list(raw_dir.rglob("*.json")) if raw_dir.exists() else []

                    # Save results to session
                    st.session_state['crawler_results'] = {
                        'pages_crawled': len(actual_files),
                        'countries': config['countries'],
                        'status': 'completed'
                    }

                    st.success(f"✅ Crawling completed successfully! Saved {len(actual_files)} pages")
                    st.info("📂 View results in the **Results** tab")

                except Exception as e:
                    st.error(f"❌ Error during crawling: {str(e)}")
                    logs.append(f"[ERROR] {str(e)}")
                    log_area.code('\n'.join(logs))

with tab3:
    st.subheader("📊 Crawling Results")

    if 'crawler_results' in st.session_state:
        results = st.session_state['crawler_results']

        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pages Crawled", results['pages_crawled'])
        with col2:
            st.metric("Countries", len(results['countries']))
        with col3:
            st.metric("Status", results['status'].upper())

        st.markdown("---")

        # Countries list
        st.markdown("#### Countries Processed:")
        for country in results['countries']:
            st.write(f"- {country.title()}")

        st.markdown("---")

        # Data location
        st.info("""
        **📁 Data Location:**
        - Raw data: `data/raw/`
        - Check directory for crawled pages

        **Next Step:**
        Run the **Classifier Service** to extract structured data from crawled pages
        """)

        # View files
        if st.button("📂 Show Crawled Files"):
            from pathlib import Path

            raw_dir = Path("data/raw")
            if raw_dir.exists():
                files = list(raw_dir.rglob("*.json"))
                st.write(f"Found {len(files)} files:")
                for f in files[:20]:  # Show first 20
                    st.code(str(f))
                if len(files) > 20:
                    st.info(f"... and {len(files) - 20} more files")
            else:
                st.warning("No raw data directory found")

    else:
        st.info("No crawling results yet. Run the crawler from the **Run** tab.")

st.markdown("---")
st.caption("Crawler Service - Part of Immigration Platform")
