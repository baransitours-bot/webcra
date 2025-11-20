"""
Crawler Results Tab Component - Enhanced with Database View
"""

import streamlit as st
import json
import pandas as pd
from shared.database import Database

class ResultsTab:
    """Handles results display with database view"""

    @staticmethod
    def render():
        """Render results tab with sub-tabs"""
        st.subheader("📊 Crawling Results")

        # Create sub-tabs for current run vs database view
        results_tab1, results_tab2 = st.tabs(["💾 Database View", "🔄 Current Run"])

        # TAB 1: Database View (All Crawled Pages)
        with results_tab1:
            st.markdown("### All Crawled Pages in Database")

            db = Database()
            pages = db.get_latest_pages()

            if not pages:
                st.warning("⚠️ No pages crawled yet. Run the crawler first.")
            else:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Pages", len(pages))
                with col2:
                    countries = set(p['country'] for p in pages)
                    st.metric("Countries", len(countries))
                with col3:
                    total_content = sum(len(p.get('content', '')) for p in pages)
                    st.metric("Total Content", f"{total_content // 1000}K chars")
                with col4:
                    # Check how many are unclassified
                    unclassified = len(db.get_unclassified_pages())
                    st.metric("Unclassified", unclassified)

                st.markdown("---")

                # Filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    country_filter = st.selectbox(
                        "Filter by Country",
                        ["All"] + sorted(list(countries)),
                        key="db_country_filter_crawler"
                    )
                with col2:
                    search_term = st.text_input("Search Title/URL", "", key="db_search_crawler")
                with col3:
                    classification_filter = st.selectbox(
                        "Classification Status",
                        ["All", "Classified", "Unclassified"],
                        key="classification_filter"
                    )

                # Apply filters
                filtered_pages = pages
                if country_filter != "All":
                    filtered_pages = [p for p in filtered_pages if p['country'] == country_filter]
                if search_term:
                    filtered_pages = [p for p in filtered_pages if
                                     search_term.lower() in p['title'].lower() or
                                     search_term.lower() in p['url'].lower()]

                # Classification filter
                if classification_filter == "Classified":
                    # Get URLs of classified pages
                    visas = db.get_visas()
                    classified_urls = set()
                    for visa in visas:
                        if visa.source_urls:
                            classified_urls.update(visa.source_urls)
                    filtered_pages = [p for p in filtered_pages if p['url'] in classified_urls]
                elif classification_filter == "Unclassified":
                    visas = db.get_visas()
                    classified_urls = set()
                    for visa in visas:
                        if visa.source_urls:
                            classified_urls.update(visa.source_urls)
                    filtered_pages = [p for p in filtered_pages if p['url'] not in classified_urls]

                st.markdown(f"**Showing {len(filtered_pages)} of {len(pages)} pages**")

                # Display options
                view_mode = st.radio("View Mode", ["Table", "Cards"], horizontal=True, key="db_view_mode_crawler")

                if view_mode == "Table":
                    # Create DataFrame for table view
                    table_data = []
                    for page in filtered_pages:
                        table_data.append({
                            'Country': page['country'].title(),
                            'Title': page['title'][:60] + '...' if len(page['title']) > 60 else page['title'],
                            'URL': page['url'][:50] + '...' if len(page['url']) > 50 else page['url'],
                            'Content Size': f"{len(page.get('content', ''))} chars",
                            'Crawled': page.get('crawled_at', 'N/A')[:10],
                            'Version': page.get('version', 1)
                        })

                    if table_data:
                        df = pd.DataFrame(table_data)
                        st.dataframe(df, use_container_width=True, height=400)

                        # Export
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "📥 Download Table as CSV",
                            data=csv,
                            file_name="crawled_pages.csv",
                            mime="text/csv"
                        )

                else:  # Cards view
                    # Card view with pagination
                    items_per_page = 10
                    total_pages_paginated = (len(filtered_pages) + items_per_page - 1) // items_per_page

                    page_num = st.number_input("Page", min_value=1, max_value=max(1, total_pages_paginated), value=1, key="db_page_crawler")
                    start_idx = (page_num - 1) * items_per_page
                    end_idx = start_idx + items_per_page
                    page_items = filtered_pages[start_idx:end_idx]

                    for page in page_items:
                        # Check if classified
                        visas = db.get_visas()
                        is_classified = False
                        for visa in visas:
                            if page['url'] in visa.source_urls:
                                is_classified = True
                                break

                        status_icon = "✅" if is_classified else "⏳"

                        with st.expander(f"{status_icon} {page['country'].title()} - {page['title'][:60]}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**URL:** {page['url']}")
                                st.write(f"**Crawled:** {page.get('crawled_at', 'N/A')[:10]}")
                                st.write(f"**Version:** {page.get('version', 1)}")
                            with col2:
                                st.write(f"**Content Size:** {len(page.get('content', ''))} chars")
                                st.write(f"**Status:** {'Classified' if is_classified else 'Unclassified'}")

                            # Show content preview
                            if st.checkbox(f"Show Content Preview", key=f"preview_{page.get('id', page['url'])}"):
                                content = page.get('content', '')
                                preview = content[:500] + "..." if len(content) > 500 else content
                                st.text_area("Content", preview, height=150, key=f"content_{page.get('id', page['url'])}")

                    st.caption(f"Page {page_num} of {total_pages_paginated}")

                # Export all filtered data
                st.markdown("---")
                export_data = json.dumps(filtered_pages, indent=2, default=str)
                st.download_button(
                    "📥 Download All Filtered Pages as JSON",
                    data=export_data,
                    file_name="crawled_pages_all.json",
                    mime="application/json",
                    key="db_export_json_crawler"
                )

        # TAB 2: Current Run Results
        with results_tab2:
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
                st.metric("Total in DB", stats.get('pages_crawled', 0))

            st.markdown("---")

            # Countries processed
            st.markdown("### Countries Processed This Run")
            st.write(", ".join(results.get('countries', [])))

            st.markdown("---")

            # Export this run
            st.markdown("### 📥 Export This Run")

            export_data = json.dumps(results.get('results', []), indent=2)

            st.download_button(
                "📥 Download This Run as JSON",
                data=export_data,
                file_name="crawler_results_run.json",
                mime="application/json",
                key="run_export_json_crawler"
            )

            st.markdown("---")

            # Next steps
            st.info("""
            **💡 Tip:** Switch to the **Database View** tab to see ALL crawled pages, not just this run.

            **Next Steps:**
            1. Run **Classifier** to extract structured visa data
            2. View results in Classifier → Results → Database View
            """)
