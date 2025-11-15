"""
Database Checker Utility
View what's in your SQLite database
"""

from shared.database import Database
from datetime import datetime


def check_database():
    """Check database contents"""
    print("=" * 60)
    print("🗄️  DATABASE CHECKER")
    print("=" * 60)

    db = Database()

    # Overall stats
    print("\n📊 OVERALL STATISTICS:")
    print("-" * 60)
    stats = db.get_stats()

    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

    # Crawled pages
    print("\n📄 CRAWLED PAGES:")
    print("-" * 60)
    pages = db.get_latest_pages()

    if pages:
        print(f"Total: {len(pages)} pages\n")

        # Group by country
        by_country = {}
        for page in pages:
            country = page['country']
            by_country[country] = by_country.get(country, 0) + 1

        print("By country:")
        for country, count in sorted(by_country.items()):
            print(f"  - {country.title()}: {count} pages")

        # Show sample
        print("\nSample pages:")
        for page in pages[:3]:
            print(f"  • {page['title'][:60]}")
            print(f"    URL: {page['url'][:70]}")
            print(f"    Version: {page['version']}, Crawled: {page['crawled_at']}")
    else:
        print("  No pages found")

    # Visas
    print("\n🎫 VISAS:")
    print("-" * 60)
    visas = db.get_latest_visas()

    if visas:
        print(f"Total: {len(visas)} visas\n")

        # Group by country
        by_country = {}
        for visa in visas:
            country = visa['country']
            by_country[country] = by_country.get(country, 0) + 1

        print("By country:")
        for country, count in sorted(by_country.items()):
            print(f"  - {country.title()}: {count} visas")

        # Show sample
        print("\nSample visas:")
        for visa in visas[:5]:
            print(f"  • {visa['visa_type']}")
            print(f"    Country: {visa['country'].title()}, Category: {visa['category']}")
            print(f"    Version: {visa['version']}, Created: {visa['created_at']}")
    else:
        print("  No visas found")

    # Check for versioning
    print("\n📝 VERSIONING CHECK:")
    print("-" * 60)

    # Check if any pages have multiple versions
    all_pages = []
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT url, COUNT(*) as version_count
            FROM crawled_pages
            GROUP BY url
            HAVING version_count > 1
        """)
        multi_version_pages = cursor.fetchall()

    if multi_version_pages:
        print(f"Pages with multiple versions: {len(multi_version_pages)}")
        for row in multi_version_pages[:3]:
            print(f"  • {row['url'][:70]} - {row['version_count']} versions")
    else:
        print("No pages with multiple versions yet")

    # Check if any visas have multiple versions
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT visa_type, country, COUNT(*) as version_count
            FROM visas
            GROUP BY visa_type, country
            HAVING version_count > 1
        """)
        multi_version_visas = cursor.fetchall()

    if multi_version_visas:
        print(f"Visas with multiple versions: {len(multi_version_visas)}")
        for row in multi_version_visas[:3]:
            print(f"  • {row['visa_type']} ({row['country']}) - {row['version_count']} versions")
    else:
        print("No visas with multiple versions yet")

    print("\n" + "=" * 60)
    print("Database location: data/immigration.db")
    print("=" * 60)


if __name__ == "__main__":
    check_database()
