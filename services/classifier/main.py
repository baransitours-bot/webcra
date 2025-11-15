"""
Classifier Service - Entry Point (Database Version)
"""

import yaml
from services.classifier.visa_extractor import VisaExtractor
from shared.database import Database
from shared.logger import setup_logger

def parse_arguments(args):
    """Parse command line arguments"""
    options = {
        'country': None,
        'all': False
    }

    i = 0
    while i < len(args):
        if args[i] == '--country' and i + 1 < len(args):
            options['country'] = args[i + 1]
            i += 2
        elif args[i] == '--all':
            options['all'] = True
            i += 1
        else:
            i += 1

    return options

def run_classifier(args):
    """
    Run the classifier service with database storage

    Usage:
      python main.py classify --country canada
      python main.py classify --all
    """
    logger = setup_logger('classifier', 'classifier.log')
    logger.info("🔄 Starting Classifier Service (Database Version)...")

    # Parse arguments
    options = parse_arguments(args)

    # Initialize database and extractor
    db = Database()
    extractor = VisaExtractor()  # Auto-uses ConfigManager

    # Get pages from database
    pages = db.get_latest_pages()

    if not pages:
        logger.error("❌ No pages found in database!")
        logger.info("Run the Crawler service first to collect pages.")
        logger.info("Example: python main.py crawl --all")
        return

    # Filter by country if specified
    if options['country']:
        pages = [p for p in pages if p['country'].lower() == options['country'].lower()]
        if not pages:
            logger.error(f"❌ No pages found for country: {options['country']}")
            logger.info(f"Available countries: {', '.join(set(p['country'] for p in db.get_latest_pages()))}")
            return

    logger.info(f"Processing {len(pages)} pages...")

    # Process each page
    visas_extracted = 0

    for i, page in enumerate(pages, 1):
        logger.info(f"[{i}/{len(pages)}] Processing: {page['title'][:60]}...")

        try:
            # Extract visa from page
            visa_data = extractor.extract_visa_from_text(
                page['content'],
                page['country']
            )

            if visa_data:
                # Save to database
                db.save_visa(
                    visa_type=visa_data.get('visa_type', 'Unknown'),
                    country=page['country'],
                    category=visa_data.get('category', 'unknown'),
                    requirements=visa_data.get('requirements', {}),
                    fees=visa_data.get('fees', {}),
                    processing_time=visa_data.get('processing_time', 'Not specified'),
                    documents_required=visa_data.get('eligibility_criteria', []),
                    timeline_stages=[],
                    cost_breakdown={},
                    source_urls=[page['url']]
                )
                visas_extracted += 1
                logger.info(f"✅ Extracted: {visa_data['visa_type']}")
            else:
                logger.debug(f"⏭️  Skipped (no visa data): {page['title'][:60]}")

        except Exception as e:
            logger.error(f"❌ Error processing {page['title'][:60]}: {str(e)}")

    logger.info(f"✅ Classification complete!")
    logger.info(f"   Pages processed: {len(pages)}")
    logger.info(f"   Visas extracted: {visas_extracted}")
    logger.info(f"   Data saved to database: data/immigration.db")

    if visas_extracted == 0:
        logger.warning("⚠️  No visas were extracted. This might mean:")
        logger.warning("   - Pages don't contain visa information")
        logger.warning("   - LLM extraction failed (check API key)")
        logger.warning("   - Pattern matching didn't find requirements")
