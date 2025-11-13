"""
Immigration Platform - Web UI
Streamlit-based web interface for local use
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="Immigration Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        text-align: center;
        margin-bottom: 3rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #F5F5F5;
        margin: 1rem 0;
    }
    .stat-box {
        padding: 1rem;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #E8F5E9;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar navigation
    st.sidebar.title("🌍 Immigration Platform")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "👤 Build Profile", "🔍 Find Visas", "💬 AI Assistant", "📊 Admin Tools"]
    )

    # Main content
    if page == "🏠 Home":
        show_home_page()
    elif page == "👤 Build Profile":
        show_profile_builder()
    elif page == "🔍 Find Visas":
        show_visa_matcher()
    elif page == "💬 AI Assistant":
        show_ai_assistant()
    elif page == "📊 Admin Tools":
        show_admin_tools()

def show_home_page():
    """Home page with overview"""
    st.markdown('<div class="main-header">🌍 Immigration Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Find Your Perfect Visa Match Across Multiple Countries</div>', unsafe_allow_html=True)

    # Statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="stat-box">
            <h2>5</h2>
            <p>Countries</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stat-box">
            <h2>100+</h2>
            <p>Visa Types</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="stat-box">
            <h2>AI</h2>
            <p>Powered</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="stat-box">
            <h2>FREE</h2>
            <p>Forever</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Features
    st.subheader("✨ Key Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-box">
            <h3>🔍 Smart Matching</h3>
            <p>Advanced algorithm matches your profile to eligible visas across multiple countries with detailed eligibility scoring.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-box">
            <h3>💬 AI Assistant</h3>
            <p>Chat with our AI-powered assistant to get instant answers about visa requirements, application processes, and more.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-box">
            <h3>📊 Multiple Countries</h3>
            <p>Compare visa options across Australia, Canada, UK, Germany, and UAE all in one place.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-box">
            <h3>🎯 Gap Analysis</h3>
            <p>Know exactly what you're missing for each visa and get recommendations on how to improve your profile.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick start
    st.subheader("🚀 Quick Start")

    st.markdown("""
    1. **Build Your Profile** - Tell us about your age, education, experience
    2. **Find Visas** - Get matched to eligible visas with scores
    3. **Ask Questions** - Chat with AI assistant for detailed information
    4. **Apply** - Get direct links to official application pages
    """)

    # Call to action
    st.markdown("---")
    st.markdown("""
    <div class="success-box">
        <h3>👉 Ready to get started?</h3>
        <p>Use the sidebar to navigate to <b>Build Profile</b> and create your immigration profile in just 2 minutes!</p>
    </div>
    """, unsafe_allow_html=True)

def show_profile_builder():
    """Profile builder page"""
    st.title("👤 Build Your Profile")
    st.markdown("Complete your profile to find matching visas")

    # Profile form
    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input("Age", min_value=18, max_value=100, value=28)

            education = st.selectbox(
                "Highest Education Level",
                ["High School", "Diploma", "Bachelor's Degree", "Master's Degree", "PhD/Doctorate"],
                index=2
            )

            work_experience = st.number_input(
                "Years of Work Experience",
                min_value=0,
                max_value=50,
                value=5
            )

        with col2:
            occupation = st.text_input("Occupation", value="Software Engineer")

            ielts_score = st.number_input(
                "IELTS Score (if taken)",
                min_value=0.0,
                max_value=9.0,
                value=7.5,
                step=0.5
            )

            countries = st.multiselect(
                "Countries of Interest",
                ["Australia", "Canada", "UK", "Germany", "UAE"],
                default=["Australia", "Canada"]
            )

        submit = st.form_submit_button("💾 Save Profile & Find Visas")

        if submit:
            # Map education
            edu_map = {
                "High School": "secondary",
                "Diploma": "diploma",
                "Bachelor's Degree": "bachelor",
                "Master's Degree": "master",
                "PhD/Doctorate": "phd"
            }

            # Create profile
            profile = {
                "age": age,
                "education": edu_map[education],
                "work_experience": work_experience,
                "occupation": occupation.lower(),
                "language": {
                    "english": {
                        "ielts": ielts_score
                    }
                },
                "countries_of_interest": [c.lower() for c in countries]
            }

            # Save to session state
            st.session_state['user_profile'] = profile

            st.success("✅ Profile saved! Go to 'Find Visas' to see your matches.")

            # Show profile summary
            with st.expander("📋 Profile Summary"):
                st.json(profile)

def show_visa_matcher():
    """Visa matching page"""
    st.title("🔍 Find Your Matching Visas")

    # Check if profile exists
    if 'user_profile' not in st.session_state:
        st.warning("⚠️ Please build your profile first!")
        st.info("👈 Go to 'Build Profile' in the sidebar")
        return

    profile = st.session_state['user_profile']

    # Display profile summary
    with st.expander("👤 Your Profile"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Age", profile['age'])
            st.metric("Education", profile['education'].title())
        with col2:
            st.metric("Experience", f"{profile['work_experience']} years")
            st.metric("IELTS", profile['language']['english']['ielts'])
        with col3:
            st.write("**Occupation:**", profile['occupation'].title())
            st.write("**Countries:**", ", ".join([c.title() for c in profile['countries_of_interest']]))

    # Match visas button
    if st.button("🎯 Find Matching Visas", type="primary"):
        with st.spinner("🔄 Analyzing your profile and matching visas..."):
            try:
                import yaml
                from services.matcher.ranker import VisaRanker
                from shared.database import DataStore

                # Load config
                with open('services/matcher/config.yaml', 'r') as f:
                    config = yaml.safe_load(f)

                # Get all visas
                db = DataStore()
                all_visas = db.load_structured_visas()

                if not all_visas:
                    st.error("❌ No visa data found. Please run the classifier first.")
                    st.code("python main.py classify --all")
                    return

                # Rank visas
                ranker = VisaRanker(config)
                matches = ranker.rank_all_visas(profile, all_visas)

                # Filter eligible (score >= 50%)
                eligible = [m for m in matches if m['eligibility_score'] >= 50]

                st.success(f"✅ Found {len(eligible)} eligible visas!")

                # Save to session
                st.session_state['matches'] = eligible

                # Display results
                if eligible:
                    st.markdown("---")
                    st.subheader("🎯 Top Matches")

                    for i, match in enumerate(eligible[:10], 1):
                        with st.container():
                            # Header
                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.markdown(f"### {i}. {match['visa_type']}")
                            with col2:
                                st.metric("Score", f"{match['eligibility_score']:.1f}%")
                            with col3:
                                st.metric("Category", match['category'].title())

                            # Details
                            col1, col2 = st.columns(2)

                            with col1:
                                st.markdown("**🌍 Country:**", )
                                st.write(match['country'].title())

                                # Requirements
                                st.markdown("**📋 Requirements:**")
                                reqs = match.get('requirements', {})
                                if reqs.get('age'):
                                    age_req = reqs['age']
                                    if age_req.get('min') and age_req.get('max'):
                                        st.write(f"- Age: {age_req['min']}-{age_req['max']} years")
                                if reqs.get('education'):
                                    st.write(f"- Education: {reqs['education']}")
                                if reqs.get('work_experience'):
                                    st.write(f"- Experience: {reqs['work_experience'].get('years', 'N/A')} years")

                            with col2:
                                # Strengths
                                if match.get('strengths'):
                                    st.markdown("**✅ Your Strengths:**")
                                    for strength in match['strengths']:
                                        st.write(f"- {strength}")

                                # Gaps
                                if match.get('gaps'):
                                    st.markdown("**❌ Gaps:**")
                                    for gap in match['gaps']:
                                        st.write(f"- {gap}")

                            st.markdown("---")
                else:
                    st.warning("No visas found with 50%+ eligibility. Try broadening your search or improving your profile.")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)

def show_ai_assistant():
    """AI assistant chat page"""
    st.title("💬 AI Immigration Assistant")
    st.markdown("Ask me anything about immigration visas!")

    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    # Display chat history
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about visas, requirements, processes..."):
        # Add user message
        st.session_state['messages'].append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    import yaml
                    import os

                    # Check API key
                    with open('services/assistant/config.yaml', 'r') as f:
                        config = yaml.safe_load(f)

                    provider = config['llm'].get('provider', 'openrouter')

                    if provider == 'openrouter':
                        api_key_env = config['llm']['openrouter']['api_key_env']
                    else:
                        api_key_env = config['llm']['openai']['api_key_env']

                    # Check if key is set
                    if not api_key_env.startswith('sk-') and not os.getenv(api_key_env):
                        st.error(f"❌ {api_key_env} not set!")
                        st.info("Set your API key in the config or environment variable.")
                        st.stop()

                    # Import services
                    try:
                        from services.assistant.enhanced_retriever import EnhancedRetriever as Retriever
                    except ImportError:
                        from services.assistant.retriever import ContextRetriever as Retriever

                    from services.assistant.llm_client import LLMClient
                    from services.assistant.prompts import CHAT_SYSTEM_PROMPT, GENERAL_QUERY_PROMPT_TEMPLATE

                    # Initialize
                    retriever = Retriever(config)
                    llm_client = LLMClient(config)

                    # Retrieve context
                    user_profile = st.session_state.get('user_profile', None)
                    relevant_visas = retriever.retrieve_relevant_visas(prompt, user_profile)

                    if not relevant_visas:
                        response = "I couldn't find specific visa information for your query. Could you be more specific about which country or visa type you're interested in?"
                    else:
                        context = retriever.format_context_for_llm(relevant_visas)
                        user_prompt = GENERAL_QUERY_PROMPT_TEMPLATE.format(
                            context=context,
                            query=prompt
                        )
                        response = llm_client.generate_answer(CHAT_SYSTEM_PROMPT, user_prompt)

                    st.markdown(response)

                    # Save assistant response
                    st.session_state['messages'].append({"role": "assistant", "content": response})

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)

    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state['messages'] = []
        st.rerun()

def show_admin_tools():
    """Admin tools page"""
    st.title("📊 Admin Tools")
    st.markdown("Manage data and system operations")

    tab1, tab2, tab3 = st.tabs(["📥 Data Collection", "🔧 System Status", "📈 Statistics"])

    with tab1:
        st.subheader("Data Collection")

        # Crawler
        st.markdown("### 🕷️ Crawler")
        col1, col2 = st.columns(2)

        with col1:
            countries = st.multiselect(
                "Select Countries to Crawl",
                ["Australia", "Canada", "UK", "Germany", "UAE"],
                default=[]
            )

        with col2:
            max_pages = st.number_input("Max Pages per Country", min_value=10, max_value=500, value=100)

        if st.button("🚀 Start Crawling"):
            st.warning("⚠️ This will take several minutes. Use CLI for better control: `python main.py crawl --countries ...`")

        # Classifier
        st.markdown("### 📊 Classifier")
        if st.button("🔄 Extract & Structure Data"):
            st.warning("⚠️ Run via CLI: `python main.py classify --all`")

    with tab2:
        st.subheader("System Status")

        # Check data directories
        from pathlib import Path

        raw_data = Path('data/raw')
        structured_data = Path('data/structured')

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Raw Data Files", len(list(raw_data.rglob('*.json'))) if raw_data.exists() else 0)

        with col2:
            st.metric("Structured Data Files", len(list(structured_data.glob('*.json'))) if structured_data.exists() else 0)

        # Service status
        st.markdown("### 🔧 Services")

        services = {
            "Crawler": "services/crawler/main.py",
            "Classifier": "services/classifier/main.py",
            "Matcher": "services/matcher/main.py",
            "Assistant": "services/assistant/main.py"
        }

        for name, path in services.items():
            if Path(path).exists():
                st.success(f"✅ {name} - Ready")
            else:
                st.error(f"❌ {name} - Not Found")

    with tab3:
        st.subheader("Statistics")

        try:
            from shared.database import DataStore
            db = DataStore()
            all_visas = db.load_structured_visas()

            if all_visas:
                # Count by country
                by_country = {}
                by_category = {}

                for visa in all_visas:
                    country = visa.get('country', 'unknown')
                    category = visa.get('category', 'other')

                    by_country[country] = by_country.get(country, 0) + 1
                    by_category[category] = by_category.get(category, 0) + 1

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Visas by Country:**")
                    for country, count in sorted(by_country.items()):
                        st.write(f"- {country.title()}: {count}")

                with col2:
                    st.markdown("**Visas by Category:**")
                    for category, count in sorted(by_category.items()):
                        st.write(f"- {category.title()}: {count}")

                st.metric("Total Visas", len(all_visas))
            else:
                st.info("No visa data available. Run classifier to populate data.")

        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")

if __name__ == "__main__":
    main()
