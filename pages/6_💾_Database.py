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
    "🔍 Embeddings",
    "🗑️ Data Management"
])

# ============ TAB 1: Overview ============
with tabs[0]:
    st.markdown("### Database Statistics")

    stats = db.get_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Pages Crawled", stats.get('pages_crawled', 0))
        st.metric("Countries (Pages)", stats.get('countries', 0))

    with col2:
        st.metric("Visas Total", stats.get('visas_total', 0))
        # For countries from visas, we need a separate query or use the same 'countries' value
        st.metric("Countries (Visas)", stats.get('countries', 0))

    with col3:
        st.metric("Clients", stats.get('clients', 0))
        st.metric("Eligibility Checks", stats.get('checks_performed', 0))

    with col4:
        st.metric("Embeddings", stats.get('embeddings', 0))

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
        selected_country = st.selectbox("Filter by Country", ["All"] + countries)

        if selected_country != "All":
            pages = [p for p in pages if p['country'] == selected_country]

        st.write(f"**Showing {len(pages)} pages**")

        # Display as table
        if pages:
            df_data = []
            for p in pages:
                df_data.append({
                    'Country': p['country'],
                    'Title': p['title'][:50] + '...' if len(p['title']) > 50 else p['title'],
                    'URL': p['url'][:60] + '...' if len(p['url']) > 60 else p['url'],
                    'Content Size': f"{len(p.get('content_text', ''))} chars",
                    'Crawled': p.get('crawled_at', 'N/A')[:10]
                })

            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)

            # Export
            st.markdown("---")
            st.download_button(
                "📥 Download as CSV",
                data=df.to_csv(index=False),
                file_name="crawled_pages.csv",
                mime="text/csv"
            )

# ============ TAB 3: Visas ============
with tabs[2]:
    st.markdown("### Classified Visas")

    visas = db.get_latest_visas()

    if not visas:
        st.warning("⚠️ No visas classified yet. Run the Classifier service first.")
    else:
        # Filter by country
        countries = sorted(list(set(v['country'] for v in visas)))
        selected_country = st.selectbox("Filter by Country", ["All"] + countries, key="visa_country")

        if selected_country != "All":
            visas = [v for v in visas if v['country'] == selected_country]

        st.write(f"**Showing {len(visas)} visas**")

        # Display as table
        if visas:
            for visa in visas[:20]:  # Show first 20
                with st.expander(f"🎫 {visa['visa_type']} ({visa['country']})"):
                    st.json(visa)

            if len(visas) > 20:
                st.info(f"ℹ️ Showing first 20 of {len(visas)} visas")

# ============ TAB 4: Clients ============
with tabs[3]:
    st.markdown("### Client Profiles")

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients")
        clients = [dict(row) for row in cursor.fetchall()]

    if not clients:
        st.info("No client profiles yet")
    else:
        for client in clients:
            with st.expander(f"👤 {client['name']} ({client['email']})"):
                st.write(f"**Nationality:** {client['nationality']}")
                st.json(json.loads(client['profile']) if isinstance(client['profile'], str) else client['profile'])

# ============ TAB 5: Eligibility Checks ============
with tabs[4]:
    st.markdown("### Eligibility Checks History")

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ec.*, c.name as client_name
            FROM eligibility_checks ec
            LEFT JOIN clients c ON ec.client_id = c.id
            ORDER BY ec.created_at DESC
            LIMIT 50
        """)
        checks = [dict(row) for row in cursor.fetchall()]

    if not checks:
        st.info("No eligibility checks yet")
    else:
        st.write(f"**Showing {len(checks)} most recent checks**")

        for check in checks:
            with st.expander(f"✅ {check['client_name']} - {check['visa_type']} ({check['created_at'][:10]})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Score:** {check['score']}")
                    st.write(f"**Result:** {check['result']}")
                with col2:
                    st.write(f"**Country:** {check['country']}")
                st.json(json.loads(check['details']) if isinstance(check['details'], str) else check['details'])

# ============ TAB 6: Settings ============
with tabs[5]:
    st.markdown("### System Settings")

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM settings ORDER BY key")
        settings = [dict(row) for row in cursor.fetchall()]

    if settings:
        # Group by service
        by_service = {}
        for setting in settings:
            service = setting.get('service', 'system')
            if service not in by_service:
                by_service[service] = []
            by_service[service].append(setting)

        for service, service_settings in by_service.items():
            with st.expander(f"⚙️ {service.upper()}"):
                for s in service_settings:
                    st.write(f"**{s['key']}:** `{s['value'][:100]}`")

# ============ TAB 7: Embeddings ============
with tabs[6]:
    st.markdown("### Embeddings")

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.visa_id, e.model_name, v.visa_type, v.country
            FROM embeddings e
            JOIN visas v ON e.visa_id = v.id
            WHERE v.is_latest = 1
        """)
        embeddings = [dict(row) for row in cursor.fetchall()]

    if not embeddings:
        st.info("No embeddings yet. Run embedding generation script.")
    else:
        st.write(f"**Total embeddings:** {len(embeddings)}")

        # Group by model
        models = {}
        for emb in embeddings:
            model = emb['model_name']
            if model not in models:
                models[model] = []
            models[model].append(emb)

        for model, model_embs in models.items():
            st.write(f"**Model:** {model} - {len(model_embs)} embeddings")

# ============ TAB 8: Data Management ============
with tabs[7]:
    st.markdown("### 🗑️ Data Management & Reset")

    st.warning("""
    ⚠️ **Warning: Data deletion is permanent and cannot be undone!**

    Use this page to delete data from the database. This is useful for:
    - Starting fresh with new data
    - Removing data from specific countries
    - Clearing test data
    - Freeing up database space
    """)

    st.markdown("---")

    # Get current stats
    stats = db.get_stats()

    # Section 1: Delete by Country
    st.markdown("### 🌍 Delete by Country")

    # Get list of countries
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT country FROM crawled_pages")
        page_countries = [row['country'] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT country FROM visas")
        visa_countries = [row['country'] for row in cursor.fetchall()]

    all_countries = sorted(list(set(page_countries + visa_countries)))

    if all_countries:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Delete Crawled Pages by Country")
            country_pages = st.selectbox(
                "Select Country",
                all_countries,
                key="delete_pages_country"
            )

            # Show count
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM crawled_pages WHERE country = ?", (country_pages,))
                pages_count = cursor.fetchone()['count']

            st.caption(f"📄 {pages_count} pages from {country_pages}")

            if st.button(f"🗑️ Delete {pages_count} Pages from {country_pages.title()}", type="secondary", key="delete_pages_btn"):
                deleted = db.delete_crawled_pages(country=country_pages)
                st.success(f"✅ Deleted {deleted} crawled pages from {country_pages}")
                st.rerun()

        with col2:
            st.markdown("#### Delete Visas by Country")
            country_visas = st.selectbox(
                "Select Country",
                all_countries,
                key="delete_visas_country"
            )

            # Show count
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM visas WHERE country = ?", (country_visas,))
                visas_count = cursor.fetchone()['count']

            st.caption(f"🎫 {visas_count} visas from {country_visas}")

            if st.button(f"🗑️ Delete {visas_count} Visas from {country_visas.title()}", type="secondary", key="delete_visas_btn"):
                deleted = db.delete_visas(country=country_visas)
                st.success(f"✅ Deleted {deleted} visas from {country_visas}")
                st.rerun()
    else:
        st.info("No countries found in database")

    st.markdown("---")

    # Section 2: Delete Specific Data Types
    st.markdown("### 📊 Delete by Data Type")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🕷️ All Crawled Pages")
        st.metric("Pages", stats.get('pages_crawled', 0))

        if st.button("🗑️ Delete All Pages", type="secondary", key="delete_all_pages"):
            if stats.get('pages_crawled', 0) > 0:
                if st.checkbox("✅ Yes, delete all pages", key="confirm_pages"):
                    deleted = db.delete_crawled_pages()
                    st.success(f"✅ Deleted {deleted} crawled pages")
                    st.rerun()
            else:
                st.info("No pages to delete")

    with col2:
        st.markdown("#### 📋 All Visas")
        st.metric("Visas", stats.get('visas_total', 0))

        if st.button("🗑️ Delete All Visas", type="secondary", key="delete_all_visas"):
            if stats.get('visas_total', 0) > 0:
                if st.checkbox("✅ Yes, delete all visas", key="confirm_visas"):
                    deleted = db.delete_visas()
                    st.success(f"✅ Deleted {deleted} visas")
                    st.rerun()
            else:
                st.info("No visas to delete")

    with col3:
        st.markdown("#### 🔍 All Embeddings")
        st.metric("Embeddings", stats.get('embeddings', 0))

        if st.button("🗑️ Delete All Embeddings", type="secondary", key="delete_all_embeddings"):
            if stats.get('embeddings', 0) > 0:
                if st.checkbox("✅ Yes, delete all embeddings", key="confirm_embeddings"):
                    deleted = db.delete_embeddings()
                    st.success(f"✅ Deleted {deleted} embeddings")
                    st.rerun()
            else:
                st.info("No embeddings to delete")

    st.markdown("---")

    # Section 3: Nuclear Option - Delete Everything
    st.markdown("### 💥 Delete ALL Data")

    st.error("""
    **☢️ DANGER ZONE: This will delete ALL data from the database!**

    This will permanently remove:
    - All crawled pages
    - All classified visas
    - All embeddings
    - All client profiles
    - All eligibility check records

    **Settings will NOT be deleted** - your configuration is safe.
    """)

    total_records = (
        stats.get('pages_crawled', 0) +
        stats.get('visas_total', 0) +
        stats.get('embeddings', 0) +
        stats.get('clients', 0) +
        stats.get('checks_performed', 0)
    )

    st.metric("Total Records to Delete", total_records)

    if total_records > 0:
        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            delete_all_checkbox = st.checkbox(
                "☑️ I understand this cannot be undone",
                key="confirm_delete_all"
            )

            if delete_all_checkbox:
                if st.button("💥 DELETE ALL DATA", type="primary", key="delete_all_data_btn"):
                    result = db.delete_all_data()
                    st.success(f"""
                    ✅ **All data deleted successfully!**

                    Deleted:
                    - {result['pages']} crawled pages
                    - {result['visas']} visas
                    - {result['embeddings']} embeddings
                    - {result['clients']} clients
                    - {result['checks']} eligibility checks

                    **Total:** {sum(result.values())} records deleted
                    """)
                    st.balloons()
                    st.rerun()
    else:
        st.info("✅ Database is already empty")

    st.markdown("---")

    # Quick Export before delete
    st.markdown("### 📥 Export Before Delete (Recommended)")

    st.info("💡 **Tip:** Always export your data before deleting in case you need it later!")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Export Pages as JSON"):
            pages = db.get_latest_pages()
            if pages:
                st.download_button(
                    "⬇️ Download pages.json",
                    data=json.dumps(pages, indent=2, default=str),
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
