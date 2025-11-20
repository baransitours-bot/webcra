"""
Matcher Service Page
Match user profiles to eligible visas
"""

import streamlit as st
import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

st.set_page_config(page_title="Matcher Service", page_icon="🔍", layout="wide")

st.title("🔍 Matcher Service")
st.markdown("Match your profile to eligible visas based on your qualifications")

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["👤 Profile", "▶️ Run", "📊 Results"])

with tab1:
    st.subheader("👤 User Profile")
    st.markdown("Enter your information to find matching visas")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📋 Basic Information")

        age = st.number_input(
            "Age",
            min_value=18,
            max_value=100,
            value=30,
            help="Your current age"
        )

        nationality = st.text_input(
            "Nationality",
            value="",
            placeholder="e.g., Indian, Chinese, Brazilian",
            help="Your country of citizenship"
        )

        marital_status = st.selectbox(
            "Marital Status",
            ["single", "married", "divorced", "widowed"],
            help="Your marital status"
        )

        st.markdown("#### 🎓 Education")

        education = st.selectbox(
            "Highest Education Level",
            ["secondary", "diploma", "bachelors", "masters", "phd"],
            index=2,
            help="Your highest completed education"
        )

        field_of_study = st.text_input(
            "Field of Study",
            value="",
            placeholder="e.g., Computer Science, Engineering",
            help="Your major or specialization"
        )

    with col2:
        st.markdown("#### 💼 Work Experience")

        work_experience = st.number_input(
            "Years of Work Experience",
            min_value=0,
            max_value=50,
            value=5,
            help="Total years of professional experience"
        )

        occupation = st.text_input(
            "Current Occupation",
            value="",
            placeholder="e.g., Software Engineer, Teacher",
            help="Your current job title"
        )

        industry = st.text_input(
            "Industry",
            value="",
            placeholder="e.g., IT, Healthcare, Education",
            help="Your industry sector"
        )

        st.markdown("#### 🌐 Languages")

        english_proficiency = st.selectbox(
            "English Proficiency",
            ["none", "basic", "intermediate", "advanced", "native"],
            index=3,
            help="Your English language level"
        )

        other_languages = st.text_input(
            "Other Languages",
            value="",
            placeholder="e.g., French, Spanish, Mandarin",
            help="Other languages you speak (comma-separated)"
        )

    st.markdown("---")

    # Additional preferences
    with st.expander("⚙️ Additional Preferences"):
        col1, col2 = st.columns(2)

        with col1:
            country_preference = st.multiselect(
                "Preferred Countries",
                ["australia", "canada", "uk", "germany", "usa", "uae"],
                default=[],
                help="Filter matches by country"
            )

            visa_categories = st.multiselect(
                "Visa Categories",
                ["work", "student", "business", "family", "skilled"],
                default=["work", "skilled"],
                help="Types of visas to consider"
            )

        with col2:
            budget = st.number_input(
                "Budget (USD)",
                min_value=0,
                max_value=100000,
                value=5000,
                step=500,
                help="Maximum visa application budget"
            )

            timeline = st.selectbox(
                "Desired Timeline",
                ["urgent (< 3 months)", "soon (3-6 months)", "flexible (6+ months)"],
                index=1,
                help="When you want to apply"
            )

    # Build profile object
    user_profile = {
        'age': age,
        'nationality': nationality,
        'marital_status': marital_status,
        'education': education,
        'field_of_study': field_of_study,
        'work_experience': work_experience,
        'occupation': occupation,
        'industry': industry,
        'english_proficiency': english_proficiency,
        'other_languages': other_languages.split(',') if other_languages else [],
        'country_preference': country_preference,
        'visa_categories': visa_categories,
        'budget': budget,
        'timeline': timeline
    }

    # Save to session
    st.session_state['user_profile'] = user_profile

    st.success("✅ Profile saved to session")

    # Profile actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Export Profile as JSON"):
            profile_json = json.dumps(user_profile, indent=2)
            st.download_button(
                "📥 Download",
                data=profile_json,
                file_name="my_profile.json",
                mime="application/json"
            )

    with col2:
        uploaded_file = st.file_uploader(
            "📤 Import Profile from JSON",
            type=['json'],
            help="Upload a previously saved profile"
        )
        if uploaded_file:
            try:
                loaded_profile = json.load(uploaded_file)
                st.session_state['user_profile'] = loaded_profile
                st.success("✅ Profile loaded! Please refresh to see values.")
            except Exception as e:
                st.error(f"❌ Failed to load profile: {str(e)}")

with tab2:
    st.subheader("▶️ Run Matcher")

    # Check if profile exists
    if 'user_profile' not in st.session_state:
        st.warning("⚠️ Please create a profile in the **Profile** tab first!")
        st.stop()

    profile = st.session_state['user_profile']

    # Validate profile
    from services.matcher.interface import MatcherController
    controller = MatcherController()

    validation = controller.validate_profile(profile)

    if not validation['valid']:
        st.error("❌ Profile validation failed:")
        for error in validation['errors']:
            st.error(f"  - {error}")
        st.info("👈 Go back to the **Profile** tab to fix these issues")
        st.stop()

    # Show profile summary
    st.markdown("#### 📋 Profile Summary:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Age", profile['age'])
    with col2:
        st.metric("Education", profile['education'].title())
    with col3:
        st.metric("Experience", f"{profile['work_experience']} years")
    with col4:
        st.metric("English", profile['english_proficiency'].title())

    # Check data availability
    st.markdown("---")
    st.markdown("#### 📊 Data Availability:")

    try:
        stats = controller.get_statistics()

        if stats['total_visas'] > 0:
            st.success(f"✅ Found {stats['total_visas']} visas in database")
        else:
            st.warning("⚠️ No visas found in database. Run Crawler and Classifier first!")
            st.stop()

    except Exception as e:
        st.error(f"❌ Error checking data: {str(e)}")
        st.stop()

    st.markdown("---")

    # Country filter
    country_filter = st.selectbox(
        "Filter by Country (Optional)",
        ["All Countries"] + (profile.get('country_preference', [])),
        help="Narrow matches to specific country"
    )

    selected_country = None if country_filter == "All Countries" else country_filter

    # Run button
    if st.button("▶️ Start Matching", type="primary"):

        progress_container = st.container()

        with progress_container:
            st.markdown("### 🔄 Matching in Progress...")

            # Progress indicators
            status_text = st.empty()
            progress_bar = st.progress(0)

            # Log area
            log_container = st.expander("📋 Live Logs", expanded=True)

            with log_container:
                log_area = st.empty()
                logs = []

                # Results area
                matches_area = st.empty()
                all_matches = []

                try:
                    # Define callbacks
                    def on_start(total_visas):
                        logs.append(f"[INFO] Starting matching against {total_visas} visas...")
                        logs.append(f"[INFO] Profile: {profile['education']}, {profile['work_experience']} yrs exp")
                        if selected_country:
                            logs.append(f"[INFO] Filtering to country: {selected_country}")
                        log_area.code('\n'.join(logs))
                        status_text.text(f"Matching against {total_visas} visas...")
                        progress_bar.progress(0.1)

                    def on_match(match):
                        all_matches.append(match)
                        visa_type = match.get('visa_type', 'Unknown')
                        score = match.get('match_score', 0)

                        logs.append(f"[MATCH] ✅ {visa_type}: {score:.1f}% match")
                        log_area.code('\n'.join(logs[-20:]))

                        status_text.text(f"Found {len(all_matches)} matches...")

                        # Update progress
                        progress_bar.progress(min(0.9, 0.1 + (len(all_matches) / 100)))

                    def on_complete(matches):
                        progress_bar.progress(1.0)

                        # Categorize matches
                        high_matches = [m for m in matches if m.get('match_score', 0) >= 80]
                        medium_matches = [m for m in matches if 60 <= m.get('match_score', 0) < 80]
                        low_matches = [m for m in matches if m.get('match_score', 0) < 60]

                        logs.append(f"\n[SUCCESS] ==================== COMPLETED ====================")
                        logs.append(f"[INFO] Total matches: {len(matches)}")
                        logs.append(f"[INFO] High matches (80%+): {len(high_matches)}")
                        logs.append(f"[INFO] Medium matches (60-79%): {len(medium_matches)}")
                        logs.append(f"[INFO] Low matches (<60%): {len(low_matches)}")
                        log_area.code('\n'.join(logs))

                        status_text.text(f"✅ Completed! Found {len(matches)} matches")

                    def on_error(error_msg):
                        logs.append(f"[ERROR] ❌ {error_msg}")
                        log_area.code('\n'.join(logs))

                    # Run matching
                    matches = controller.match_with_progress(
                        user_profile=profile,
                        country=selected_country,
                        on_start=on_start,
                        on_match=on_match,
                        on_complete=on_complete,
                        on_error=on_error
                    )

                    # Save to session
                    st.session_state['matcher_results'] = {
                        'matches': matches,
                        'profile': profile,
                        'timestamp': str(Path(__file__).stat().st_mtime),
                        'country_filter': selected_country
                    }

                    st.success(f"✅ Matching completed! Found {len(matches)} matches")
                    st.info("📊 View results in the **Results** tab →")

                except Exception as e:
                    st.error(f"❌ Error during matching: {str(e)}")
                    logs.append(f"[ERROR] {str(e)}")
                    log_area.code('\n'.join(logs))
                    import traceback
                    st.code(traceback.format_exc())

with tab3:
    st.subheader("📊 Matching Results")

    if 'matcher_results' not in st.session_state:
        st.info("ℹ️ No results yet. Run the matcher in the **Run** tab first.")
        st.stop()

    results = st.session_state['matcher_results']
    matches = results['matches']
    profile = results['profile']

    if not matches:
        st.warning("⚠️ No matches found for your profile.")
        st.info("""
        **Tips to improve your matches:**
        - Update your profile with more details
        - Try different countries
        - Run Classifier to get more visa data
        """)
        st.stop()

    # Summary metrics
    st.markdown("### 📈 Summary")

    high_matches = [m for m in matches if m.get('match_score', 0) >= 80]
    medium_matches = [m for m in matches if 60 <= m.get('match_score', 0) < 80]
    low_matches = [m for m in matches if m.get('match_score', 0) < 60]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Matches", len(matches))
    with col2:
        st.metric("High (80%+)", len(high_matches), delta="Best fit")
    with col3:
        st.metric("Medium (60-79%)", len(medium_matches))
    with col4:
        st.metric("Low (<60%)", len(low_matches))

    st.markdown("---")

    # Filter results
    score_filter = st.selectbox(
        "Filter by Match Score",
        ["All Matches", "High (80%+)", "Medium (60-79%)", "Low (<60%)"],
        index=0
    )

    if score_filter == "High (80%+)":
        display_matches = high_matches
    elif score_filter == "Medium (60-79%)":
        display_matches = medium_matches
    elif score_filter == "Low (<60%)":
        display_matches = low_matches
    else:
        display_matches = matches

    # Sort by score
    display_matches = sorted(display_matches, key=lambda m: m.get('match_score', 0), reverse=True)

    st.markdown(f"### 🎯 Matches ({len(display_matches)})")

    for i, match in enumerate(display_matches, 1):
        score = match.get('match_score', 0)
        visa_type = match.get('visa_type', 'Unknown')
        country = match.get('country', 'Unknown')
        category = match.get('category', 'unknown')

        # Score color
        if score >= 80:
            score_color = "🟢"
        elif score >= 60:
            score_color = "🟡"
        else:
            score_color = "🔴"

        with st.expander(f"{i}. {score_color} **{visa_type}** ({country.title()}) - {score:.1f}%"):

            # Match details
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Visa Type:** {visa_type}")
                st.markdown(f"**Country:** {country.title()}")
                st.markdown(f"**Category:** {category.title()}")
                st.markdown(f"**Match Score:** {score:.1f}%")

                # Requirements
                if 'requirements' in match and match['requirements']:
                    st.markdown("**Requirements:**")
                    reqs = match['requirements']
                    if isinstance(reqs, dict):
                        for key, value in reqs.items():
                            st.markdown(f"  - {key}: {value}")
                    else:
                        st.markdown(f"  {reqs}")

                # Fees
                if 'fees' in match and match['fees']:
                    st.markdown("**Fees:**")
                    fees = match['fees']
                    if isinstance(fees, dict):
                        for key, value in fees.items():
                            st.markdown(f"  - {key}: {value}")
                    else:
                        st.markdown(f"  {fees}")

                # Processing time
                if 'processing_time' in match:
                    st.markdown(f"**Processing Time:** {match['processing_time']}")

            with col2:
                # Gap analysis
                if 'gaps' in match and match['gaps']:
                    st.markdown("**⚠️ Gaps:**")
                    for gap in match['gaps']:
                        st.markdown(f"  - {gap}")
                else:
                    st.success("✅ No gaps detected")

                # Source
                if 'source_urls' in match and match['source_urls']:
                    st.markdown("**🔗 Source:**")
                    for url in match['source_urls'][:1]:  # Show first URL
                        st.markdown(f"[Link]({url})")

            # Full match data
            with st.expander("🔍 View Full Match Data"):
                st.json(match)

    # Export results
    st.markdown("---")
    st.markdown("### 💾 Export Results")

    col1, col2 = st.columns(2)

    with col1:
        export_data = json.dumps(display_matches, indent=2)
        st.download_button(
            "📥 Download Matches as JSON",
            data=export_data,
            file_name=f"visa_matches_{profile.get('nationality', 'user')}.json",
            mime="application/json"
        )

    with col2:
        # Summary report
        report = f"""# Visa Matching Report

## Profile Summary
- Age: {profile.get('age', 'N/A')}
- Education: {profile.get('education', 'N/A')}
- Experience: {profile.get('work_experience', 'N/A')} years
- Nationality: {profile.get('nationality', 'N/A')}

## Results
- Total Matches: {len(matches)}
- High Matches (80%+): {len(high_matches)}
- Medium Matches (60-79%): {len(medium_matches)}
- Low Matches (<60%): {len(low_matches)}

## Top Recommendations
"""
        for i, match in enumerate(display_matches[:5], 1):
            report += f"\n{i}. {match.get('visa_type', 'Unknown')} ({match.get('country', 'Unknown')}) - {match.get('match_score', 0):.1f}%"

        st.download_button(
            "📄 Download Summary Report",
            data=report,
            file_name=f"visa_report_{profile.get('nationality', 'user')}.md",
            mime="text/markdown"
        )

    st.markdown("---")
    st.info("""
    **Next Steps:**
    1. Review high-match visas (80%+)
    2. Check requirements and gaps
    3. Visit official source URLs
    4. Consult with immigration advisor
    """)
