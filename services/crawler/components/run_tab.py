"""
Crawler Run Tab Component - Updated to use Controller
"""

import streamlit as st
import yaml
from shared.components import ProgressDisplay, LogViewer
from services.crawler.interface import CrawlerController


class RunTab:
    """Handles crawler execution UI"""

    @staticmethod
    def render(config: dict):
        """Render run tab"""
        st.subheader("▶️ Run Crawler")

        # Show current config
        st.markdown("#### 📋 Current Configuration")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Countries", len(config['countries']))
        with col2:
            st.metric("Max Pages", config['max_pages'])
        with col3:
            st.metric("Max Depth", config['max_depth'])
        with col4:
            st.metric("Delay", f"{config['request_delay']}s")

        st.markdown("**Selected Countries:**")
        st.write(", ".join([c.title() for c in config['countries']]))

        st.markdown("---")

        # Run button
        if st.button("▶️ Start Crawling", type="primary", use_container_width=True):
            RunTab._execute_crawl(config)

    @staticmethod
    def _execute_crawl(config: dict):
        """Execute the crawling process using Controller"""
        progress = ProgressDisplay()
        logger = LogViewer(max_lines=30, expanded=True)

        try:
            logger.add_info("Initializing crawler controller...")

            # Initialize controller
            controller = CrawlerController()
            logger.add_success("Controller initialized")

            # Update config
            crawler_config = controller.get_config()
            crawler_config['crawling']['max_pages_per_country'] = config['max_pages']
            crawler_config['crawling']['max_depth'] = config['max_depth']
            crawler_config['crawling']['delay_between_requests'] = config['request_delay']

            logger.add_info(f"Max pages: {config['max_pages']}")
            logger.add_info(f"Max depth: {config['max_depth']}")
            logger.add_info(f"Request delay: {config['request_delay']}s")

            # Load global config to get country URLs
            with open('config.yaml', 'r') as f:
                global_config = yaml.safe_load(f)

            # Prepare countries to crawl
            countries_to_crawl = []
            for country_name in config['countries']:
                if country_name in global_config['countries']:
                    country_info = global_config['countries'][country_name]
                    countries_to_crawl.append({
                        'name': country_info['name'],
                        'seed_urls': country_info['seed_urls']
                    })

            if not countries_to_crawl:
                logger.add_error("No valid countries found")
                return

            logger.add_info(f"Crawling {len(countries_to_crawl)} countries...")

            # Tracking
            total_countries = len(countries_to_crawl)
            current_country_idx = [0]  # Use list for mutable closure
            total_pages = [0]

            # Define callbacks
            def on_start(country):
                current_country_idx[0] += 1
                logger.add_info(f"\n{'='*50}")
                logger.add_info(f"Crawling {country}...")
                progress.update(
                    current_country_idx[0] - 1,
                    total_countries,
                    f"Crawling {country}"
                )

            def on_complete(country, result):
                pages = result.get('pages_saved', 0)
                total_pages[0] += pages
                logger.add_success(f"✓ {country}: {pages} pages saved")
                progress.update(
                    current_country_idx[0],
                    total_countries,
                    f"Completed {country}"
                )

            def on_error(country, error):
                logger.add_error(f"✗ {country}: {error}")

            # Crawl with progress
            results = controller.crawl_with_progress(
                countries_to_crawl,
                on_start=on_start,
                on_complete=on_complete,
                on_error=on_error
            )

            # Final summary
            logger.add_info(f"\n{'='*50}")
            logger.add_success(f"✅ Crawling complete!")
            logger.add_info(f"Total pages saved: {total_pages[0]}")
            logger.add_info(f"Countries crawled: {len(results)}")

            st.success(f"✅ Crawled {len(results)} countries, saved {total_pages[0]} pages")

        except Exception as e:
            logger.add_error(f"Crawling failed: {str(e)}")
            st.error(f"Error: {str(e)}")
