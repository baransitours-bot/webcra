"""
Assistant Service Page
Q&A about visa requirements using AI
"""

import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

st.set_page_config(page_title="Assistant Service", page_icon="💬", layout="wide")

st.title("💬 Assistant Service")
st.markdown("Ask questions about visa requirements and immigration processes")

st.markdown("---")

# Initialize session state for conversation
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Tabs
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📜 History", "⚙️ Settings"])

with tab1:
    st.subheader("💬 Chat with Assistant")

    # Validate setup
    from services.assistant.interface import AssistantController
    controller = AssistantController()

    validation = controller.validate_setup()

    if not validation['ready']:
        st.error("❌ Assistant is not ready:")
        for error in validation['errors']:
            st.error(f"  - {error}")
        st.info("""
        **To use the Assistant:**
        1. Set LLM API key in Settings (page 5)
        2. Run Crawler to collect data (page 1)
        3. Run Classifier to extract visas (page 2)
        """)
        st.stop()

    # Show readiness
    stats = validation['stats']
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Status", "✅ Ready" if validation['ready'] else "⚠️ Not Ready")
    with col2:
        st.metric("Visa Data", stats['total_visas'])
    with col3:
        st.metric("General Content", stats.get('total_general_content', 0))
    with col4:
        st.metric("LLM", "✅ Available" if stats['llm_available'] else "❌ Not Set")

    st.markdown("---")

    # Load user profile if available
    user_profile = st.session_state.get('user_profile', None)

    if user_profile:
        st.info(f"ℹ️ Using profile: {user_profile.get('nationality', 'N/A')}, {user_profile.get('education', 'N/A')}, {user_profile.get('work_experience', 0)} yrs exp")
        if st.button("🔄 Clear Profile"):
            st.session_state['user_profile'] = None
            st.rerun()
    else:
        st.info("ℹ️ No profile loaded. Answers will be general. Create a profile in the Matcher page for personalized answers.")

    # Suggested questions
    with st.expander("💡 Example Questions"):
        st.markdown("""
        **General Questions:**
        - What are the requirements for a work visa in Canada?
        - How long does it take to process an Australian skilled visa?
        - What are the fees for UK student visas?

        **Specific Questions:**
        - Can I apply for a German work visa with a bachelor's degree?
        - What documents do I need for a UAE business visa?
        - What is the age limit for Canadian Express Entry?

        **Comparison Questions:**
        - Compare work visas between Australia and Canada
        - Which country has the fastest visa processing?
        - What are the cheapest visa options?
        """)

    st.markdown("---")

    # Chat interface
    st.markdown("### 💬 Conversation")

    # Display chat history
    if st.session_state['chat_history']:
        for i, message in enumerate(st.session_state['chat_history']):
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.markdown(message['content'])
            else:  # assistant
                with st.chat_message("assistant"):
                    st.markdown(message['content'])

                    # Show sources if available
                    if 'sources' in message and message['sources']:
                        with st.expander(f"📚 Sources ({len(message['sources'])})"):
                            for j, source in enumerate(message['sources'], 1):
                                source_type = source.get('type', 'unknown')
                                badge = "🎫 Visa" if source_type == 'visa' else "📄 Guide"
                                st.markdown(f"**{j}. {badge}:** {source.get('title', 'Unknown')} ({source.get('country', 'Unknown')})")
                                if 'url' in source:
                                    st.markdown(f"   [Source]({source['url']})")
    else:
        st.info("👋 No messages yet. Ask a question below to get started!")

    # Chat input
    st.markdown("---")

    question = st.text_area(
        "Your Question:",
        placeholder="e.g., What are the requirements for a Canadian work visa?",
        height=100,
        key="question_input"
    )

    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("📤 Send", type="primary", disabled=not question):

            # Add user message to history
            st.session_state['chat_history'].append({
                'role': 'user',
                'content': question,
                'timestamp': datetime.now().isoformat()
            })

            # Create response area
            with st.spinner("🤔 Thinking..."):

                try:
                    # Define callbacks
                    def on_start():
                        pass  # Can show a spinner or status

                    def on_complete(result):
                        # Add assistant response to history
                        st.session_state['chat_history'].append({
                            'role': 'assistant',
                            'content': result.get('answer', 'No answer generated.'),
                            'sources': result.get('sources', []),
                            'timestamp': datetime.now().isoformat()
                        })

                    def on_error(error_msg):
                        st.error(f"❌ Error: {error_msg}")

                    # Get answer
                    result = controller.chat(
                        question=question,
                        user_profile=user_profile,
                        on_start=on_start,
                        on_complete=on_complete,
                        on_error=on_error
                    )

                    # Clear input and rerun to show new message
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    with col2:
        if st.button("🗑️ Clear Conversation"):
            st.session_state['chat_history'] = []
            controller.reset_conversation()
            st.rerun()

with tab2:
    st.subheader("📜 Conversation History")

    if not st.session_state['chat_history']:
        st.info("ℹ️ No conversation history yet.")
    else:
        st.markdown(f"**Total Messages:** {len(st.session_state['chat_history'])}")

        st.markdown("---")

        # Display all messages
        for i, message in enumerate(st.session_state['chat_history'], 1):
            role = message['role']
            content = message['content']
            timestamp = message.get('timestamp', 'Unknown')

            if role == 'user':
                st.markdown(f"**{i}. User** ({timestamp})")
                st.info(content)
            else:
                st.markdown(f"**{i}. Assistant** ({timestamp})")
                st.success(content)

                # Show sources
                if 'sources' in message and message['sources']:
                    with st.expander(f"📚 Sources ({len(message['sources'])})"):
                        for j, source in enumerate(message['sources'], 1):
                            st.json(source)

            st.markdown("---")

        # Export options
        st.markdown("### 💾 Export Conversation")

        col1, col2 = st.columns(2)

        with col1:
            # Export as JSON
            history_json = json.dumps(st.session_state['chat_history'], indent=2)
            st.download_button(
                "📥 Download as JSON",
                data=history_json,
                file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

        with col2:
            # Export as Markdown
            markdown_content = f"# Visa Assistant Conversation\n\n"
            markdown_content += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            markdown_content += "---\n\n"

            for i, message in enumerate(st.session_state['chat_history'], 1):
                role = message['role'].upper()
                content = message['content']
                timestamp = message.get('timestamp', 'Unknown')

                markdown_content += f"## {i}. {role}\n"
                markdown_content += f"*{timestamp}*\n\n"
                markdown_content += f"{content}\n\n"

                if message['role'] == 'assistant' and 'sources' in message and message['sources']:
                    markdown_content += "**Sources:**\n"
                    for j, source in enumerate(message['sources'], 1):
                        source_type = source.get('type', 'unknown')
                        type_label = "Visa" if source_type == 'visa' else "Guide"
                        markdown_content += f"{j}. [{type_label}] {source.get('title', 'Unknown')} ({source.get('country', 'Unknown')})\n"
                        if source.get('url'):
                            markdown_content += f"   URL: {source['url']}\n"
                    markdown_content += "\n"

                markdown_content += "---\n\n"

            st.download_button(
                "📄 Download as Markdown",
                data=markdown_content,
                file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )

        # Clear history
        st.markdown("---")
        if st.button("🗑️ Clear All History", type="secondary"):
            st.session_state['chat_history'] = []
            controller.reset_conversation()
            st.success("✅ Conversation history cleared")
            st.rerun()

with tab3:
    st.subheader("⚙️ Assistant Settings")

    # Show current config
    config = controller.get_config()

    st.markdown("### 📋 Current Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Retrieval Settings:**")
        st.write(f"- Enhanced Retrieval: {config.get('use_enhanced_retrieval', True)}")
        st.write(f"- Max Visas per Query: {config.get('context', {}).get('max_visas', 5)}")
        st.write(f"- Max History Items: {config.get('context', {}).get('max_history', 10)}")

    with col2:
        st.markdown("**System Status:**")
        stats = controller.get_statistics()
        st.write(f"- Total Visas: {stats['total_visas']}")
        st.write(f"- LLM Available: {'✅' if stats['llm_available'] else '❌'}")
        st.write(f"- Ready: {'✅' if stats['ready'] else '⚠️'}")

    st.markdown("---")

    # LLM Configuration
    st.markdown("### 🤖 LLM Configuration")

    st.info("""
    **LLM configuration is managed in the Settings page (page 5).**

    The Assistant uses the same LLM settings as the Classifier:
    - Provider: OpenRouter or OpenAI
    - Model: Selected model
    - API Key: From Settings

    Go to Settings to configure your LLM provider and model.
    """)

    st.markdown("---")

    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        st.markdown("**Retrieval Configuration:**")

        new_max_visas = st.number_input(
            "Max Visas per Query",
            min_value=1,
            max_value=20,
            value=config.get('context', {}).get('max_visas', 5),
            help="Maximum number of visas to retrieve for context"
        )

        new_max_history = st.number_input(
            "Max History Items",
            min_value=1,
            max_value=50,
            value=config.get('context', {}).get('max_history', 10),
            help="Maximum conversation history items to keep"
        )

        use_enhanced = st.checkbox(
            "Use Enhanced Retrieval",
            value=config.get('use_enhanced_retrieval', True),
            help="Use semantic search for better context retrieval"
        )

        if st.button("💾 Save Settings"):
            # Update config (in real app, this would save to config file)
            st.success("✅ Settings saved (would update config.yaml in production)")
            st.info("Note: Restart the application for changes to take full effect")

    st.markdown("---")

    # Data management
    st.markdown("### 📊 Data Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Reload Data"):
            try:
                # Reinitialize controller (reloads data)
                controller = AssistantController()
                st.success("✅ Data reloaded successfully")
            except Exception as e:
                st.error(f"❌ Error reloading data: {str(e)}")

    with col2:
        if st.button("🗑️ Clear Conversation"):
            controller.reset_conversation()
            st.session_state['chat_history'] = []
            st.success("✅ Conversation cleared")

    st.markdown("---")

    # Help and tips
    with st.expander("💡 Tips for Better Answers"):
        st.markdown("""
        **Ask Specific Questions:**
        - Instead of "Tell me about visas", ask "What are the requirements for a Canadian work visa?"
        - Include country names, visa types, and specific criteria

        **Provide Context:**
        - Load your profile in the Matcher page for personalized answers
        - Mention your education, experience, nationality in questions

        **Follow Up:**
        - The assistant remembers conversation history
        - You can ask follow-up questions like "What about fees?" or "How long does it take?"

        **Compare Options:**
        - Ask comparative questions like "Compare work visas between Canada and Australia"
        - Request recommendations: "Which visa is best for software engineers?"

        **Data Quality:**
        - More visa data = better answers
        - Run Crawler regularly to keep data updated
        - Use Classifier to extract structured information
        """)

    st.markdown("---")

    # Troubleshooting
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **"LLM not configured" error:**
        - Go to Settings (page 5)
        - Enter your OpenRouter or OpenAI API key
        - Select a model

        **"No visa data found" error:**
        - Run Crawler (page 1) to collect data
        - Run Classifier (page 2) to extract visas
        - Check Database (page 6) to verify data

        **Poor quality answers:**
        - Ensure Classifier has processed pages
        - Check that you have enough visa data
        - Try asking more specific questions
        - Provide user profile for personalized answers

        **Slow responses:**
        - Some LLM models are slower than others
        - Try a faster model like "google/gemini-2.0-flash-001:free"
        - Reduce max_visas in advanced settings
        """)
