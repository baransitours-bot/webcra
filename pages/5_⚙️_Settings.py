"""
Settings Page - Centralized Configuration Management
View and edit all system settings
"""

import streamlit as st
import os
from pathlib import Path
from shared.config_manager import get_config


st.set_page_config(
    page_title="Settings - Immigration Platform",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ System Settings")
st.markdown("Centralized configuration management. Priority: `.env` > Database > YAML")

# Initialize config manager
config = get_config()

# Create tabs
tab1, tab2, tab3 = st.tabs([
    "📋 Current Settings",
    "🔧 Edit Settings",
    "📝 Environment (.env)"
])

# ============ TAB 1: Current Settings ============
with tab1:
    st.markdown("### Current Configuration")
    st.markdown("Shows active values from all sources (`.env`, Database, YAML)")

    # Check .env file
    env_file = Path('.env')
    env_exists = env_file.exists()

    col1, col2, col3 = st.columns(3)
    with col1:
        if env_exists:
            st.success("✅ .env file found")
        else:
            st.warning("⚠️ No .env file (using Database/YAML)")

    with col2:
        # Check API key
        api_key = config.get_api_key()
        if api_key:
            st.success(f"✅ API Key configured ({api_key[:8]}...)")
        else:
            st.error("❌ No API key set")

    with col3:
        provider = config.get('llm.provider', 'openrouter')
        st.info(f"🤖 Provider: {provider}")

    st.markdown("---")

    # Display settings by category
    categories = {
        'llm': '🤖 LLM Configuration',
        'crawler': '🕷️ Crawler Settings',
        'embeddings': '🔍 Embeddings',
        'app': '📱 Application'
    }

    for category, title in categories.items():
        st.markdown(f"#### {title}")

        settings = config.get_all(category)

        if settings:
            # Create a nice table
            data = []
            for key, value in settings.items():
                # Check source
                env_key = key.upper().replace('.', '_')
                if os.getenv(env_key):
                    source = "🌍 .env"
                elif config._get_from_db(key) is not None:
                    source = "💾 Database"
                else:
                    source = "📄 YAML"

                data.append({
                    "Setting": key,
                    "Value": str(value),
                    "Source": source
                })

            st.dataframe(data, use_container_width=True, hide_index=True)
        else:
            # Show defaults from YAML
            st.info(f"No {category} settings in database. Using YAML defaults.")

        st.markdown("")

# ============ TAB 2: Edit Settings ============
with tab2:
    st.markdown("### Edit Settings")
    st.markdown("Changes are saved to **Database**. `.env` values always take priority.")

    # LLM Settings
    st.markdown("#### 🤖 LLM Configuration")

    col1, col2 = st.columns(2)

    with col1:
        llm_provider = st.selectbox(
            "Provider",
            options=["openrouter", "openai"],
            index=0 if config.get('llm.provider', 'openrouter') == 'openrouter' else 1,
            help="LLM provider to use"
        )

        llm_temp = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=float(config.get('llm.temperature', 0.3)),
            step=0.1,
            help="Higher = more creative, Lower = more focused"
        )

    with col2:
        # Model options based on provider
        if llm_provider == 'openrouter':
            model_options = [
                "google/gemini-2.0-flash-001:free",
                "meta-llama/llama-3.2-3b-instruct:free",
                "google/gemini-flash-1.5",
            ]
        else:
            model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

        current_model = config.get('llm.model', model_options[0])
        if current_model not in model_options:
            model_options.insert(0, current_model)

        llm_model = st.selectbox(
            "Model",
            options=model_options,
            index=model_options.index(current_model) if current_model in model_options else 0,
            help="Model to use for extraction and chat"
        )

        llm_max_tokens = st.number_input(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=int(config.get('llm.max_tokens', 2000)),
            step=100,
            help="Maximum tokens per request"
        )

    if st.button("💾 Save LLM Settings", type="primary"):
        config.set('llm.provider', llm_provider)
        config.set('llm.model', llm_model)
        config.set('llm.temperature', llm_temp)
        config.set('llm.max_tokens', llm_max_tokens)
        st.success("✅ LLM settings saved to database!")
        st.rerun()

    st.markdown("---")

    # Crawler Settings
    st.markdown("#### 🕷️ Crawler Settings")

    col1, col2, col3 = st.columns(3)

    with col1:
        crawler_delay = st.number_input(
            "Request Delay (seconds)",
            min_value=0.5,
            max_value=10.0,
            value=float(config.get('crawler.delay', 2.0)),
            step=0.5,
            help="Delay between requests to avoid rate limiting"
        )

    with col2:
        crawler_max_pages = st.number_input(
            "Max Pages per Country",
            min_value=10,
            max_value=500,
            value=int(config.get('crawler.max_pages', 50)),
            step=10,
            help="Maximum pages to crawl per country"
        )

    with col3:
        crawler_max_depth = st.number_input(
            "Max Depth",
            min_value=1,
            max_value=5,
            value=int(config.get('crawler.max_depth', 3)),
            step=1,
            help="Maximum crawl depth"
        )

    if st.button("💾 Save Crawler Settings", type="primary"):
        config.set('crawler.delay', crawler_delay)
        config.set('crawler.max_pages', crawler_max_pages)
        config.set('crawler.max_depth', crawler_max_depth)
        st.success("✅ Crawler settings saved to database!")
        st.rerun()

    st.markdown("---")

    # Application Settings
    st.markdown("#### 📱 Application Settings")

    col1, col2 = st.columns(2)

    with col1:
        log_level = st.selectbox(
            "Log Level",
            options=["DEBUG", "INFO", "WARNING", "ERROR"],
            index=["DEBUG", "INFO", "WARNING", "ERROR"].index(
                config.get('app.log_level', 'INFO')
            ),
            help="Logging verbosity"
        )

    with col2:
        default_country = st.text_input(
            "Default Country",
            value=config.get('app.default_country', 'australia'),
            help="Default country in UI dropdowns"
        )

    if st.button("💾 Save App Settings", type="primary"):
        config.set('app.log_level', log_level)
        config.set('app.default_country', default_country)
        st.success("✅ App settings saved to database!")
        st.rerun()

# ============ TAB 3: Environment File ============
with tab3:
    st.markdown("### .env File Management")

    env_file = Path('.env')
    env_example = Path('.env.example')

    if not env_file.exists():
        st.warning("⚠️ No `.env` file found")

        if env_example.exists():
            st.markdown("**Quick Setup:**")
            if st.button("📋 Create .env from .env.example"):
                env_example_content = env_example.read_text()
                env_file.write_text(env_example_content)
                st.success("✅ Created .env file! Edit it below.")
                st.rerun()
        else:
            st.error("❌ No .env.example template found")

    else:
        st.success("✅ .env file exists")

        # Show current content (hide API keys)
        st.markdown("**Current .env file** (API keys hidden):")

        env_content = env_file.read_text()
        lines = env_content.split('\n')

        # Mask API keys for display
        display_lines = []
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                if 'API_KEY' in key and value.strip():
                    display_lines.append(f"{key}=********")
                else:
                    display_lines.append(line)
            else:
                display_lines.append(line)

        st.code('\n'.join(display_lines), language='bash')

        st.markdown("---")

        # Edit mode
        st.markdown("#### Edit .env File")
        st.warning("⚠️ Be careful editing directly. Invalid syntax will break config loading.")

        with st.expander("✏️ Click to Edit"):
            edited_content = st.text_area(
                "Edit .env content",
                value=env_content,
                height=400,
                help="Edit carefully. Save when done."
            )

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("💾 Save .env", type="primary"):
                    env_file.write_text(edited_content)
                    st.success("✅ .env file saved!")
                    st.info("🔄 Restart the app to apply changes")

    st.markdown("---")
    st.markdown("### API Key Quick Setup")

    api_key_provider = st.radio(
        "Choose Provider",
        options=["OpenRouter (FREE)", "OpenAI (Paid)"],
        horizontal=True
    )

    if api_key_provider == "OpenRouter (FREE)":
        st.markdown("**Get FREE OpenRouter API Key:**")
        st.markdown("1. Go to [OpenRouter.ai](https://openrouter.ai)")
        st.markdown("2. Sign up / Login")
        st.markdown("3. Get your API key from dashboard")

        or_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            placeholder="sk-or-...",
            help="Paste your OpenRouter API key"
        )

        if st.button("💾 Save OpenRouter Key"):
            if or_key:
                # Update or create .env
                lines = env_file.read_text().split('\n') if env_file.exists() else []
                new_lines = []
                key_found = False

                for line in lines:
                    if line.startswith('OPENROUTER_API_KEY='):
                        new_lines.append(f'OPENROUTER_API_KEY={or_key}')
                        key_found = True
                    else:
                        new_lines.append(line)

                if not key_found:
                    new_lines.append(f'OPENROUTER_API_KEY={or_key}')

                env_file.write_text('\n'.join(new_lines))
                st.success("✅ OpenRouter API key saved to .env!")
                st.info("🔄 Restart the app to apply")

    else:
        st.markdown("**Get OpenAI API Key:**")
        st.markdown("1. Go to [platform.openai.com](https://platform.openai.com)")
        st.markdown("2. Create account / Login")
        st.markdown("3. Go to API Keys section")

        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Paste your OpenAI API key"
        )

        if st.button("💾 Save OpenAI Key"):
            if openai_key:
                lines = env_file.read_text().split('\n') if env_file.exists() else []
                new_lines = []
                key_found = False

                for line in lines:
                    if line.startswith('OPENAI_API_KEY='):
                        new_lines.append(f'OPENAI_API_KEY={openai_key}')
                        key_found = True
                    else:
                        new_lines.append(line)

                if not key_found:
                    new_lines.append(f'OPENAI_API_KEY={openai_key}')

                env_file.write_text('\n'.join(new_lines))
                st.success("✅ OpenAI API key saved to .env!")
                st.info("🔄 Restart the app to apply")

    st.markdown("---")
    st.markdown("""
    ### Configuration Priority

    Settings are loaded in this order (highest to lowest priority):

    1. **🌍 .env file** - Environment variables (HIGHEST)
    2. **💾 Database** - Settings saved via this UI
    3. **📄 YAML files** - Default configs in services/ (LOWEST)

    **Tip:** Use `.env` for API keys and secrets, use Database for user preferences.
    """)
