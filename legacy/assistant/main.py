"""
Assistant Service - Entry Point
"""

import yaml
import json
import os
from services.assistant.llm_client import LLMClient

# Try to use enhanced retriever, fallback to original if not available
try:
    from services.assistant.enhanced_retriever import EnhancedRetriever as ContextRetriever
except ImportError:
    from services.assistant.retriever import ContextRetriever

from services.assistant.prompts import (
    SYSTEM_PROMPT,
    ELIGIBILITY_PROMPT_TEMPLATE,
    GENERAL_QUERY_PROMPT_TEMPLATE,
    CHAT_SYSTEM_PROMPT
)
from shared.logger import setup_logger

def parse_arguments(args):
    """Parse command line arguments"""
    options = {
        'query': None,
        'profile': None,
        'chat': False
    }

    i = 0
    while i < len(args):
        if args[i] == '--query' and i + 1 < len(args):
            options['query'] = args[i + 1]
            i += 2
        elif args[i] == '--profile' and i + 1 < len(args):
            options['profile'] = args[i + 1]
            i += 2
        elif args[i] == '--chat':
            options['chat'] = True
            i += 1
        else:
            i += 1

    return options

def run_chat_mode(llm_client, retriever):
    """Run interactive chat mode"""
    print("\n🤖 AI Immigration Assistant")
    print("Ask me anything about immigration visas. Type 'exit' to quit.\n")

    while True:
        try:
            query = input("You: ").strip()

            if query.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye! Good luck with your immigration journey! 🌍")
                break

            if not query:
                continue

            # Retrieve context
            print("🔍 Searching visa information...")
            relevant_visas = retriever.retrieve_relevant_visas(query)

            if not relevant_visas:
                print("\nAssistant: I couldn't find specific visa information related to your query. Could you be more specific about which country or visa type you're interested in?\n")
                continue

            context = retriever.format_context_for_llm(relevant_visas)

            # Generate answer
            print("💭 Thinking...")
            user_prompt = GENERAL_QUERY_PROMPT_TEMPLATE.format(
                context=context,
                query=query
            )

            answer = llm_client.generate_answer(CHAT_SYSTEM_PROMPT, user_prompt)

            print(f"\nAssistant: {answer}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye! Good luck with your immigration journey! 🌍")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            continue

def run_assistant(args):
    """
    Run the assistant service

    Usage:
      python main.py assist --query "Am I eligible for Canada?"
      python main.py assist --query "..." --profile user.json
      python main.py assist --chat
    """
    logger = setup_logger('assistant', 'assistant.log')
    logger.info("🤖 Starting AI Assistant Service...")

    # Load config first to check provider
    with open('services/assistant/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Check if appropriate API key is set based on provider
    provider = config['llm'].get('provider', 'openai')

    if provider == 'openrouter':
        api_key_env = config['llm']['openrouter']['api_key_env']
        # Skip check if API key is directly in config (starts with 'sk-')
        if not api_key_env.startswith('sk-') and not os.getenv(api_key_env):
            print(f"\n❌ Error: {api_key_env} environment variable not set!")
            print(f"\nPlease set your OpenRouter API key:")
            print(f"  Windows PowerShell: $env:{api_key_env}='your-api-key-here'")
            print(f"  Linux/Mac: export {api_key_env}='your-api-key-here'")
            print("\nOr put the key directly in config.yaml under api_key_env")
            print("\nGet your FREE API key from: https://openrouter.ai/keys")
            print("\nNote: OpenRouter offers free models for testing!\n")
            return
    else:
        api_key_env = config['llm']['openai']['api_key_env']
        # Skip check if API key is directly in config (starts with 'sk-')
        if not api_key_env.startswith('sk-') and not os.getenv(api_key_env):
            print(f"\n❌ Error: {api_key_env} environment variable not set!")
            print(f"\nPlease set your OpenAI API key:")
            print(f"  Windows PowerShell: $env:{api_key_env}='your-api-key-here'")
            print(f"  Linux/Mac: export {api_key_env}='your-api-key-here'")
            print("\nOr put the key directly in config.yaml under api_key_env")
            print("\nGet your API key from: https://platform.openai.com/api-keys")
            print("\nNote: This requires an OpenAI account with API credits.")
            print("\nAlternatively, set provider to 'openrouter' in config.yaml for free models.\n")
            return

    # Parse arguments
    options = parse_arguments(args)

    try:
        # Initialize components
        llm_client = LLMClient(config)
        retriever = ContextRetriever(config)

        # Chat mode
        if options['chat']:
            run_chat_mode(llm_client, retriever)
            return

        # Single query mode
        if not options['query']:
            logger.error("No query specified. Use --query or --chat")
            print("\n❌ No query specified. Use --query or --chat")
            print("Example: python main.py assist --query 'What visas are available in Canada?'")
            print("Or: python main.py assist --chat\n")
            return

        query = options['query']

        # Load user profile if provided
        user_profile = None
        if options['profile']:
            with open(options['profile'], 'r') as f:
                user_profile = json.load(f)

        # Retrieve relevant context
        logger.info("Retrieving relevant visa information...")
        relevant_visas = retriever.retrieve_relevant_visas(query, user_profile)

        if not relevant_visas:
            print("\n❌ No relevant visa information found for your query.")
            print("Try running the classifier first: python main.py classify --all\n")
            return

        context = retriever.format_context_for_llm(relevant_visas)

        # Generate answer
        logger.info("Generating answer...")

        if user_profile:
            user_prompt = ELIGIBILITY_PROMPT_TEMPLATE.format(
                user_profile=json.dumps(user_profile, indent=2),
                context=context,
                query=query
            )
        else:
            user_prompt = GENERAL_QUERY_PROMPT_TEMPLATE.format(
                context=context,
                query=query
            )

        answer = llm_client.generate_answer(SYSTEM_PROMPT, user_prompt)

        # Display answer
        print("\n" + "=" * 80)
        print(f"💬 {answer}")
        print("=" * 80 + "\n")

        logger.info("✅ Answer generated successfully!")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {str(e)}\n")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"\n❌ Error: {str(e)}\n")
