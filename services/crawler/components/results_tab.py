"""
Crawler Results Tab Component
"""

import streamlit as st
import json
from shared.database import Database

class ResultsTab:
    """Handles results display"""

    @staticmethod
    def render():
        """Render results tab"""
        st.subheader("📊 Crawling Results")

        if 'crawler_results' not in st.session_state:
            st.info("ℹ️ No results yet. Run the crawler in the **Run** tab first.")
            return

        results = st.session_state['crawler_results']

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Pages Crawled", results.get('pages_crawled', 0))

        with col2:
            st.metric("Countries", len(results.get('countries', [])))

        with col3:
            st.metric("Status", results.get('status', 'unknown').title())

        with col4:
            # Get database stats
            db = Database()
            stats = db.get_stats()
            st.metric("Total in DB", stats.get('Pages Crawled', 0))

        st.markdown("---")

        # Countries processed
        st.markdown("### Countries Processed")
        st.write(", ".join(results.get('countries', [])))

        st.markdown("---")

        # Pages by country
        st.markdown("### Pages by Country")

        db = Database()
        pages = db.get_latest_pages()

        if pages:
            # Count by country
            by_country = {}
            for page in pages:
                country = page['country']
                by_country[country] = by_country.get(country, 0) + 1

            # Display as metrics
            cols = st.columns(len(by_country))
            for i, (country, count) in enumerate(sorted(by_country.items())):
                with cols[i]:
                    st.metric(country.title(), count)

            st.markdown("---")

            # Show sample pages
            st.markdown("### Recent Pages (Last 10)")

            for i, page in enumerate(pages[:10], 1):
                with st.expander(f"{i}. {page['country'].title()} - {page['title'][:60]}"):
                    st.markdown(f"**URL:** {page['url']}")
                    st.markdown(f"**Crawled:** {page['crawled_at']}")
                    st.markdown(f"**Version:** {page['version']}")

                    # Show content preview
                    content_preview = page['content'][:300] + "..." if len(page['content']) > 300 else page['content']
                    st.text_area("Content Preview", content_preview, height=100, key=f"preview_{i}")

        else:
            st.warning("⚠️ No pages in database yet.")

        st.markdown("---")

        # Export
        st.markdown("### 📥 Export Data")

        if pages:
            export_data = json.dumps(results.get('results', []), indent=2)

            st.download_button(
                "📥 Download Results as JSON",
                data=export_data,
                file_name="crawler_results.json",
                mime="application/json"
            )

        st.markdown("---")

        # Next steps
        st.info("""
        **Next Steps:**
        1. View all pages in 💾 **Database** page
        2. Run **Classifier** to extract visa data
        3. Create embeddings for semantic search
        """)
