"""
Database Viewer - Comprehensive database exploration
View all data with pagination, filtering, and export
"""

import streamlit as st
import pandas as pd
from shared.database import Database
from shared.config_manager import get_config
import json

st.set_page_config(
    page_title="Database Viewer",
    page_icon="💾",
    layout="wide"
)

st.title("💾 Database Viewer")
st.markdown("Comprehensive view of all data in the system")

# Initialize
db = Database()
config = get_config()

# Create tabs for different data types
tabs = st.tabs([
    "📊 Overview",
    "🕷️ Crawled Pages",
    "📋 Visas",
    "👤 Clients",
    "✅ Eligibility Checks",
    "⚙️ Settings",
    "🔍 Embeddings"
])

# ============ TAB 1: Overview ============
with tabs[0]:
    st.markdown("### Database Statistics")

    stats = db.get_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Pages Crawled", stats.get('Pages Crawled', 0))
        st.metric("Countries (Pages)", stats.get('Countries', 0))

    with col2:
        st.metric("Visas Total", stats.get('Visas Total', 0))
        st.metric("Countries (Visas)", len(stats.get('Countries (Visas)', [])))

    with col3:
        st.metric("Clients", stats.get('Clients', 0))
        st.metric("Eligibility Checks", stats.get('Checks Performed', 0))

    with col4:
        st.metric("Embeddings", stats.get('Embeddings', 0))

        # Get settings count
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM settings")
            settings_count = cursor.fetchone()['count']
        st.metric("Settings", settings_count)

    st.markdown("---")

    # Database file info
    import os
    db_path = "data/immigration.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        st.info(f"📁 **Database File:** `{db_path}` ({size:,} bytes / {size/1024:.1f} KB)")

    # Table structure
    st.markdown("### Database Tables")

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, sql FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)
        tables = cursor.fetchall()

    for table in tables:
        with st.expander(f"📋 {table['name']}"):
            st.code(table['sql'], language='sql')

# ============ TAB 2: Crawled Pages ============
with tabs[1]:
    st.markdown("### Crawled Pages")

    pages = db.get_latest_pages()

    if not pages:
        st.warning("⚠️ No pages crawled yet. Run the Crawler service first.")
    else:
        # Filter by country
        countries = sorted(list(set(p['country'] for p in pages)))
        selected_country = st.selectbox(
            "Filter by Country",
            options=['All'] + countries,
            key='pages_country'
        )

        if selected_country != 'All':
            pages = [p for p in pages if p['country'] == selected_country]

        st.info(f"Showing {len(pages)} pages")

        # Pagination
        items_per_page = st.slider("Items per page", 5, 50, 10, key='pages_per_page')
        total_pages = (len(pages) - 1) // items_per_page + 1

        if total_pages > 1:
            page_num = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=1,
                key='pages_page_num'
            )
        else:
            page_num = 1

        start_idx = (page_num - 1) * items_per_page
        end_idx = start_idx + items_per_page
        pages_to_show = pages[start_idx:end_idx]

        # Display as table
        for i, page in enumerate(pages_to_show, start=start_idx + 1):
            with st.expander(f"{i}. {page['country']} - {page['title'][:80]}"):
                col1, col2 = st.columns([1, 3])

                with col1:
                    st.markdown(f"**ID:** {page['id']}")
                    st.markdown(f"**Country:** {page['country']}")
                    st.markdown(f"**Version:** {page['version']}")
                    st.markdown(f"**Latest:** {'✅' if page['is_latest'] else '❌'}")
                    st.markdown(f"**Crawled:** {page['crawled_at']}")

                with col2:
                    st.markdown(f"**Title:** {page['title']}")
                    st.markdown(f"**URL:** {page['url']}")

                    # Show content preview
                    content = page['content'][:500]
                    st.text_area("Content Preview", content, height=100, key=f"page_content_{page['id']}")

                    # Metadata
                    if page['metadata']:
                        metadata = json.loads(page['metadata'])
                        st.json(metadata)

# ============ TAB 3: Visas ============
with tabs[2]:
    st.markdown("### Visas")

    visas = db.get_latest_visas()

    if not visas:
        st.warning("⚠️ No visas extracted yet. Run the Classifier service first.")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            countries = sorted(list(set(v['country'] for v in visas)))
            selected_country = st.selectbox(
                "Filter by Country",
                options=['All'] + countries,
                key='visas_country'
            )

        with col2:
            categories = sorted(list(set(v['category'] for v in visas if v['category'])))
            selected_category = st.selectbox(
                "Filter by Category",
                options=['All'] + categories,
                key='visas_category'
            )

        with col3:
            search = st.text_input("Search visa type", key='visas_search')

        # Apply filters
        filtered_visas = visas
        if selected_country != 'All':
            filtered_visas = [v for v in filtered_visas if v['country'] == selected_country]
        if selected_category != 'All':
            filtered_visas = [v for v in filtered_visas if v['category'] == selected_category]
        if search:
            filtered_visas = [v for v in filtered_visas if search.lower() in v['visa_type'].lower()]

        st.info(f"Showing {len(filtered_visas)} of {len(visas)} visas")

        # Pagination
        items_per_page = st.slider("Items per page", 5, 50, 10, key='visas_per_page')
        total_pages = (len(filtered_visas) - 1) // items_per_page + 1

        if total_pages > 1:
            page_num = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=1,
                key='visas_page_num'
            )
        else:
            page_num = 1

        start_idx = (page_num - 1) * items_per_page
        end_idx = start_idx + items_per_page
        visas_to_show = filtered_visas[start_idx:end_idx]

        # Display
        for i, visa in enumerate(visas_to_show, start=start_idx + 1):
            with st.expander(f"{i}. {visa['visa_type']} ({visa['country']})"):
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.markdown(f"**ID:** {visa['id']}")
                    st.markdown(f"**Country:** {visa['country']}")
                    st.markdown(f"**Category:** {visa['category']}")
                    st.markdown(f"**Version:** {visa['version']}")
                    st.markdown(f"**Latest:** {'✅' if visa['is_latest'] else '❌'}")
                    st.markdown(f"**Created:** {visa['created_at']}")

                with col2:
                    st.markdown(f"**Visa Type:** {visa['visa_type']}")

                    if visa['requirements']:
                        st.markdown("**Requirements:**")
                        try:
                            reqs = json.loads(visa['requirements']) if isinstance(visa['requirements'], str) else visa['requirements']
                            st.json(reqs)
                        except:
                            st.text(visa['requirements'])

                    if visa['fees']:
                        st.markdown("**Fees:**")
                        try:
                            fees = json.loads(visa['fees']) if isinstance(visa['fees'], str) else visa['fees']
                            st.json(fees)
                        except:
                            st.text(visa['fees'])

                    if visa['processing_time']:
                        st.markdown(f"**Processing Time:** {visa['processing_time']}")

# ============ TAB 4: Clients ============
with tabs[3]:
    st.markdown("### Clients")

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients ORDER BY created_at DESC")
        clients = cursor.fetchall()

    if not clients:
        st.info("ℹ️ No clients in database yet.")
    else:
        st.info(f"Total clients: {len(clients)}")

        for client in clients:
            with st.expander(f"{client['name']} ({client['email']})"):
                st.markdown(f"**ID:** {client['id']}")
                st.markdown(f"**Nationality:** {client['nationality']}")
                st.markdown(f"**Created:** {client['created_at']}")

                if client['profile']:
                    st.markdown("**Profile:**")
                    try:
                        profile = json.loads(client['profile'])
                        st.json(profile)
                    except:
                        st.text(client['profile'])

# ============ TAB 5: Eligibility Checks ============
with tabs[4]:
    st.markdown("### Eligibility Checks")

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ec.*, c.name as client_name, v.visa_type
            FROM eligibility_checks ec
            LEFT JOIN clients c ON ec.client_id = c.id
            LEFT JOIN visas v ON ec.visa_id = v.id
            ORDER BY ec.check_date DESC
        """)
        checks = cursor.fetchall()

    if not checks:
        st.info("ℹ️ No eligibility checks performed yet.")
    else:
        st.info(f"Total checks: {len(checks)}")

        for check in checks:
            eligible_text = "✅ Eligible" if check['eligible'] else "❌ Not Eligible"
            with st.expander(f"{check['client_name']} → {check['visa_type']} - {eligible_text}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Date:** {check['check_date']}")
                    st.markdown(f"**Score:** {check['score']}")
                    st.markdown(f"**Eligible:** {eligible_text}")

                with col2:
                    if check['gaps']:
                        st.markdown("**Gaps:**")
                        try:
                            gaps = json.loads(check['gaps'])
                            st.json(gaps)
                        except:
                            st.text(check['gaps'])

                    if check['strengths']:
                        st.markdown("**Strengths:**")
                        try:
                            strengths = json.loads(check['strengths'])
                            st.json(strengths)
                        except:
                            st.text(check['strengths'])

# ============ TAB 6: Settings ============
with tabs[5]:
    st.markdown("### System Settings")

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM settings
            ORDER BY category, key
        """)
        settings = cursor.fetchall()

    if not settings:
        st.warning("⚠️ No settings in database. Run app initialization.")
    else:
        # Group by category
        categories = {}
        for setting in settings:
            cat = setting['category'] or 'other'
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(setting)

        for category, cat_settings in sorted(categories.items()):
            st.markdown(f"#### {category.upper()}")

            # Create DataFrame
            data = []
            for s in cat_settings:
                # Check if overridden by .env
                import os
                env_key = s['key'].upper().replace('.', '_')
                env_value = os.getenv(env_key)

                if env_value:
                    source = "🌍 .env"
                    actual_value = env_value
                else:
                    source = "💾 Database"
                    actual_value = s['value']

                data.append({
                    "Key": s['key'],
                    "Value": actual_value,
                    "Type": s['type'],
                    "Source": source,
                    "Updated": s['updated_at']
                })

            df = pd.DataFrame(data)
            st.dataframe(df, hide_index=True, width=1200)
            st.markdown("")

# ============ TAB 7: Embeddings ============
with tabs[6]:
    st.markdown("### Embeddings")

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, v.visa_type, v.country
            FROM embeddings e
            JOIN visas v ON e.visa_id = v.id
            ORDER BY e.indexed_at DESC
        """)
        embeddings = cursor.fetchall()

    if not embeddings:
        st.warning("⚠️ No embeddings indexed yet. Run: `python scripts/index_embeddings.py`")
    else:
        st.info(f"Total embeddings: {len(embeddings)}")

        # Show sample
        st.markdown("#### Recent Embeddings")

        for emb in embeddings[:20]:
            with st.expander(f"{emb['visa_type']} ({emb['country']})"):
                st.markdown(f"**Visa ID:** {emb['visa_id']}")
                st.markdown(f"**Model:** {emb['model_name']}")
                st.markdown(f"**Indexed:** {emb['indexed_at']}")

                # Show embedding dimension
                import struct
                embedding_bytes = emb['embedding']
                embedding_size = len(embedding_bytes) // 4  # float32
                st.markdown(f"**Dimensions:** {embedding_size}")

st.markdown("---")

# Export functionality
st.markdown("### 📥 Export Data")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Export Pages as JSON"):
        pages = db.get_latest_pages()
        if pages:
            st.download_button(
                "⬇️ Download pages.json",
                data=json.dumps(pages, indent=2),
                file_name="pages.json",
                mime="application/json"
            )

with col2:
    if st.button("Export Visas as JSON"):
        visas = db.get_latest_visas()
        if visas:
            # Convert to serializable format
            visas_export = []
            for v in visas:
                visa_dict = dict(v)
                visas_export.append(visa_dict)

            st.download_button(
                "⬇️ Download visas.json",
                data=json.dumps(visas_export, indent=2, default=str),
                file_name="visas.json",
                mime="application/json"
            )

with col3:
    if st.button("Export Settings as JSON"):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM settings")
            settings = [dict(row) for row in cursor.fetchall()]

        st.download_button(
            "⬇️ Download settings.json",
            data=json.dumps(settings, indent=2),
            file_name="settings.json",
            mime="application/json"
        )
