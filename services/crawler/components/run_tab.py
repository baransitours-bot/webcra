"""
Crawler Run Tab Component
"""

import streamlit as st
import yaml
from shared.components import ProgressDisplay, LogViewer
from shared.database import Database

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
        """Execute the crawling process"""
        progress = ProgressDisplay()
        logger = LogViewer(max_lines=30, expanded=True)

        try:
            logger.add_info("Initializing crawler...")

            # Load global config
            with open('config.yaml', 'r') as f:
                global_config = yaml.safe_load(f)

            # Load crawler config
            with open('services/crawler/config.yaml', 'r') as f:
                crawler_config = yaml.safe_load(f)

            # Override with user settings
            crawler_config['max_pages'] = config['max_pages']
            crawler_config['max_depth'] = config['max_depth']
            crawler_config['request_delay'] = config['request_delay']

            logger.add_info(f"Max pages: {config['max_pages']}")
            logger.add_info(f"Max depth: {config['max_depth']}")
            logger.add_info(f"Request delay: {config['request_delay']}s")

            # Initialize database and crawler
            from services.crawler.spider import ImmigrationCrawler

            db = Database()
            logger.add_success("Database initialized")

            # Get country configurations
            countries_to_crawl = [
                global_config['countries'][country]
                for country in config['countries']
                if country in global_config['countries']
            ]

            logger.add_info(f"Crawling {len(countries_to_crawl)} countries...")

            total_countries = len(countries_to_crawl)
            progress.update(0, total_countries, "Starting...")

            # Crawl each country
            all_results = []

            for i, country_config in enumerate(countries_to_crawl):
                country_name = country_config['name']
                logger.add_info(f"\n{'='*50}")
                logger.add_info(f"Crawling {country_name}...")

                progress.update(i, total_countries, f"Crawling {country_name}")

                # Create crawler for this country
                crawler = ImmigrationCrawler([country_config], crawler_config)

                # Crawl
                country_results = crawler.crawl_all()
                all_results.extend(country_results)

                logger.add_success(f"Completed {country_name}: {len(country_results)} pages")

                progress.update(i + 1, total_countries, f"Completed {country_name}")

            # Final summary
            progress.complete(f"✅ Crawling complete! {len(all_results)} pages total")

            logger.add_info(f"\n{'='*50}")
            logger.add_success(f"CRAWLING COMPLETED")
            logger.add_info(f"Total pages crawled: {len(all_results)}")
            logger.add_info(f"Countries processed: {total_countries}")
            logger.add_info("Data saved to database with versioning")

            # Save to session
            st.session_state['crawler_results'] = {
                'pages_crawled': len(all_results),
                'countries': [c['name'] for c in countries_to_crawl],
                'status': 'completed',
                'results': all_results
            }

            st.success(f"✅ Crawling completed! {len(all_results)} pages saved to database")
            st.info("📊 View results in the **Results** tab →")

        except Exception as e:
            logger.add_error(f"Crawling failed: {str(e)}")
            progress.error("❌ Crawling failed")
            st.error(f"❌ Error: {str(e)}")

            import traceback
            st.code(traceback.format_exc())
