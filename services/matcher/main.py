"""
Matcher Service - Entry Point
"""

import yaml
import json
from services.matcher.ranker import VisaRanker
from shared.database import DataStore
from shared.logger import setup_logger

def parse_arguments(args):
    """Parse command line arguments"""
    options = {
        'profile': None,
        'interactive': False
    }

    i = 0
    while i < len(args):
        if args[i] == '--profile' and i + 1 < len(args):
            options['profile'] = args[i + 1]
            i += 2
        elif args[i] == '--interactive':
            options['interactive'] = True
            i += 1
        else:
            i += 1

    return options

def get_user_profile_interactive():
    """Get user profile via interactive prompts"""
    print("\n👤 Let's build your profile:\n")

    profile = {
        'age': int(input("Age: ")),
        'nationality': input("Nationality: "),
        'education': input("Education (secondary/diploma/bachelors/masters/phd): "),
        'profession': input("Profession: "),
        'experience_years': int(input("Years of work experience: ")),
        'target_countries': input("Target countries (comma-separated): ").split(',')
    }

    profile['target_countries'] = [c.strip() for c in profile['target_countries']]

    return profile

def display_matches(matches: list):
    """Display match results in a user-friendly format"""
    if not matches:
        print("\n❌ No matching visas found.")
        return

    print(f"\n✅ Found {len(matches)} matching visa options:\n")
    print("=" * 80)

    for i, match in enumerate(matches[:10], 1):  # Show top 10
        print(f"\n{i}. {match['visa_type']}")
        print(f"   Country: {match['country']}")
        print(f"   Category: {match['category']}")
        print(f"   Eligibility Score: {match['eligibility_score']}% {'⭐' * int(match['eligibility_score'] // 20)}")
        print(f"   Match Level: {match['match_level'].upper()}")
        print(f"   Status: {'✅ Eligible' if match['eligible'] else '⚠️  Not Eligible'}")

        if match['gaps']:
            print(f"   Gaps:")
            for gap in match['gaps']:
                print(f"      - {gap}")

        if match.get('language'):
            print(f"   Language: {match['language']}")

        if match['fees']:
            print(f"   Fees: {match['fees']}")

        if match['processing_time']:
            print(f"   Processing Time: {match['processing_time']}")

        print(f"   Source: {match['source_urls'][0] if match['source_urls'] else 'N/A'}")

    print("\n" + "=" * 80)

def run_matcher(args):
    """
    Run the matcher service

    Usage:
      python main.py match --profile user_profile.json
      python main.py match --interactive
    """
    logger = setup_logger('matcher', 'matcher.log')
    logger.info("🎯 Starting Matcher Service...")

    # Load config
    with open('services/matcher/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Parse arguments
    options = parse_arguments(args)

    # Get user profile
    if options['interactive']:
        user_profile = get_user_profile_interactive()
    elif options['profile']:
        with open(options['profile'], 'r') as f:
            user_profile = json.load(f)
    else:
        logger.error("No profile specified. Use --profile or --interactive")
        return

    # Load structured visa data
    data_store = DataStore()
    all_visas = data_store.load_structured_visas()

    if not all_visas:
        logger.error("No structured visa data found. Run 'python main.py classify' first")
        return

    logger.info(f"Loaded {len(all_visas)} structured visas")

    # Rank visas for user
    ranker = VisaRanker(config)
    matches = ranker.rank_all_visas(user_profile, all_visas)

    # Display results
    display_matches(matches)

    logger.info("✅ Matching complete!")
