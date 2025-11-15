"""
Database Migration Utility
Migrates existing JSON data to SQLite database
"""

import json
from pathlib import Path
from shared.database import Database
from datetime import datetime


def migrate_crawled_pages():
    """Migrate crawled pages from data/raw/ to database"""
    print("\n🔄 Migrating crawled pages...")

    db = Database()
    raw_dir = Path("data/raw")

    if not raw_dir.exists():
        print("⚠️  No data/raw directory found. Skipping pages migration.")
        return 0

    total_migrated = 0

    # Get all JSON files
    json_files = list(raw_dir.rglob("*.json"))

    if not json_files:
        print("⚠️  No JSON files found in data/raw/")
        return 0

    print(f"Found {len(json_files)} files to migrate...")

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                page_data = json.load(f)

            # Extract country from path (data/raw/country/file.json)
            country = file_path.parent.name

            # Save to database
            db.save_crawled_page(
                url=page_data.get('url', str(file_path)),
                country=country,
                title=page_data.get('title', 'No Title'),
                content=page_data.get('content_text', page_data.get('content_html', '')),
                metadata={
                    'breadcrumbs': page_data.get('breadcrumbs', []),
                    'links': page_data.get('links', []),
                    'attachments': page_data.get('attachments', []),
                    'depth': page_data.get('depth', 0),
                    'crawled_date': page_data.get('crawled_date', datetime.now().isoformat())
                }
            )

            total_migrated += 1

            if total_migrated % 10 == 0:
                print(f"  Migrated {total_migrated}/{len(json_files)} pages...")

        except Exception as e:
            print(f"  ❌ Error migrating {file_path}: {str(e)}")
            continue

    print(f"✅ Migrated {total_migrated} crawled pages")
    return total_migrated


def migrate_visas():
    """Migrate structured visas from data/processed/visas.json to database"""
    print("\n🔄 Migrating structured visas...")

    db = Database()
    visas_file = Path("data/processed/visas.json")

    if not visas_file.exists():
        print("⚠️  No data/processed/visas.json found. Skipping visas migration.")
        return 0

    try:
        with open(visas_file, 'r', encoding='utf-8') as f:
            visas = json.load(f)

        if not visas:
            print("⚠️  visas.json is empty")
            return 0

        print(f"Found {len(visas)} visas to migrate...")

        migrated = 0

        for visa in visas:
            try:
                db.save_visa(
                    visa_type=visa.get('visa_type', 'Unknown Visa'),
                    country=visa.get('country', 'Unknown'),
                    category=visa.get('category', 'unknown'),
                    requirements=visa.get('requirements', {}),
                    fees=visa.get('fees', {}),
                    processing_time=visa.get('processing_time', 'Not specified'),
                    documents_required=visa.get('documents_required', []),
                    timeline_stages=visa.get('timeline_stages', {}),
                    cost_breakdown=visa.get('cost_breakdown', {}),
                    source_urls=visa.get('source_urls', [])
                )

                migrated += 1

                if migrated % 5 == 0:
                    print(f"  Migrated {migrated}/{len(visas)} visas...")

            except Exception as e:
                print(f"  ❌ Error migrating visa {visa.get('visa_type', 'Unknown')}: {str(e)}")
                continue

        print(f"✅ Migrated {migrated} visas")
        return migrated

    except Exception as e:
        print(f"❌ Error loading visas.json: {str(e)}")
        return 0


def show_database_stats():
    """Show database statistics after migration"""
    print("\n📊 Database Statistics:")

    db = Database()
    stats = db.get_stats()

    print(f"  Pages crawled: {stats['pages_crawled']}")
    print(f"  Visas: {stats['visas_total']}")
    print(f"  Countries: {stats['countries']}")
    print(f"  Clients: {stats['clients']}")
    print(f"  Eligibility checks: {stats['checks_performed']}")


def main():
    """Run migration"""
    print("=" * 60)
    print("🗄️  DATABASE MIGRATION UTILITY")
    print("=" * 60)
    print("\nThis will migrate your existing JSON data to SQLite database.")
    print("Your original files will NOT be modified or deleted.")
    print("\nDatabase location: data/immigration.db")

    input("\nPress ENTER to continue or Ctrl+C to cancel...")

    # Migrate pages
    pages_migrated = migrate_crawled_pages()

    # Migrate visas
    visas_migrated = migrate_visas()

    # Show stats
    show_database_stats()

    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 60)
    print(f"\nMigrated:")
    print(f"  - {pages_migrated} crawled pages")
    print(f"  - {visas_migrated} visas")
    print("\nYour original JSON files are still in:")
    print("  - data/raw/ (crawled pages)")
    print("  - data/processed/visas.json (structured visas)")
    print("\nNew database:")
    print("  - data/immigration.db (SQLite with versioning)")
    print("\nNext steps:")
    print("  1. Services now use database by default")
    print("  2. Old JSON files kept as backup")
    print("  3. Run Crawler/Classifier UI to add more data")
    print()


if __name__ == "__main__":
    main()
