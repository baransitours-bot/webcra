"""
Classifier Service - Entry Point
"""

import yaml
from services.classifier.extractor import RequirementExtractor
from services.classifier.structurer import VisaStructurer
from shared.database import DataStore
from shared.logger import setup_logger
import os

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
    Run the classifier service

    Usage:
      python main.py classify --country australia
      python main.py classify --all
    """
    logger = setup_logger('classifier', 'classifier.log')
    logger.info("🔄 Starting Classifier Service...")

    # Load config
    with open('services/classifier/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Parse arguments
    options = parse_arguments(args)

    # Initialize components
    data_store = DataStore()
    extractor = RequirementExtractor(config)
    structurer = VisaStructurer()

    # Determine which countries to process
    if options['all']:
        # Get all countries from raw data
        countries = [d for d in os.listdir('data/raw') if os.path.isdir(f'data/raw/{d}')]
    elif options['country']:
        countries = [options['country']]
    else:
        logger.error("No country specified. Use --country or --all")
        return

    # Process each country
    all_structured_visas = []

    for country in countries:
        logger.info(f"Processing {country}...")

        # Load raw pages
        raw_pages = data_store.load_raw_pages(country)
        logger.info(f"Loaded {len(raw_pages)} raw pages for {country}")

        if not raw_pages:
            logger.warning(f"No raw data found for {country}")
            continue

        # Extract requirements from each page
        extracted_data = []
        for page in raw_pages:
            requirements = extractor.extract_all_requirements(page)
            extracted_data.append(requirements)

        logger.info(f"Extracted requirements from {len(extracted_data)} pages")

        # Structure into complete visa profiles
        structured_visas = structurer.structure_all_visas(extracted_data)
        all_structured_visas.extend(structured_visas)

        logger.info(f"Created {len(structured_visas)} structured visa profiles for {country}")

    # Save all structured data
    data_store.save_structured_visas(all_structured_visas)

    logger.info(f"✅ Classification complete! {len(all_structured_visas)} total visa types structured")
    logger.info("Data saved to data/processed/visas.json")
