"""
Database Query Utility
Run queries on your SQLite database
"""

from shared.database import Database
import json


def query_pages(country=None, limit=10):
    """Query crawled pages"""
    print(f"\n📄 CRAWLED PAGES {f'(Country: {country})' if country else '(All)'}:")
    print("-" * 80)

    db = Database()
    pages = db.get_latest_pages(country=country)

    if not pages:
        print("No pages found")
        return

    for i, page in enumerate(pages[:limit], 1):
        print(f"\n{i}. {page['title']}")
        print(f"   URL: {page['url']}")
        print(f"   Country: {page['country']}, Version: {page['version']}")
        print(f"   Crawled: {page['crawled_at']}")
        print(f"   Content preview: {page['content'][:100]}...")

    if len(pages) > limit:
        print(f"\n... and {len(pages) - limit} more pages")


def query_visas(country=None, limit=10):
    """Query visas"""
    print(f"\n🎫 VISAS {f'(Country: {country})' if country else '(All)'}:")
    print("-" * 80)

    db = Database()
    visas = db.get_latest_visas(country=country)

    if not visas:
        print("No visas found")
        return

    for i, visa in enumerate(visas[:limit], 1):
        print(f"\n{i}. {visa['visa_type']}")
        print(f"   Country: {visa['country']}, Category: {visa['category']}")
        print(f"   Processing time: {visa['processing_time']}")
        print(f"   Version: {visa['version']}, Created: {visa['created_at']}")

        # Show requirements
        if visa['requirements']:
            print(f"   Requirements:")
            req = visa['requirements']
            if req.get('age'):
                print(f"     - Age: {req['age']}")
            if req.get('education'):
                print(f"     - Education: {req['education']}")
            if req.get('experience_years'):
                print(f"     - Experience: {req['experience_years']} years")

    if len(visas) > limit:
        print(f"\n... and {len(visas) - limit} more visas")


def query_visa_history(visa_type, country):
    """Get all versions of a visa"""
    print(f"\n📜 VISA HISTORY: {visa_type} ({country})")
    print("-" * 80)

    db = Database()
    history = db.get_visa_history(visa_type, country)

    if not history:
        print("No history found")
        return

    for i, version in enumerate(history, 1):
        print(f"\nVersion {version['version']}:")
        print(f"  Valid from: {version['valid_from']}")
        print(f"  Valid to: {version.get('valid_to', 'Current')}")
        print(f"  Is latest: {version['is_latest']}")
        print(f"  Processing time: {version['processing_time']}")


def custom_query(sql):
    """Run custom SQL query"""
    print(f"\n🔍 CUSTOM QUERY:")
    print("-" * 80)
    print(f"SQL: {sql}\n")

    db = Database()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

        if not rows:
            print("No results")
            return

        # Print results
        for i, row in enumerate(rows[:20], 1):
            print(f"{i}. {dict(row)}")

        if len(rows) > 20:
            print(f"\n... and {len(rows) - 20} more rows")


def main():
    """Interactive query tool"""
    print("=" * 80)
    print("🗄️  DATABASE QUERY TOOL")
    print("=" * 80)

    while True:
        print("\n\nChoose an option:")
        print("  1. View all crawled pages")
        print("  2. View pages by country")
        print("  3. View all visas")
        print("  4. View visas by country")
        print("  5. View visa version history")
        print("  6. Run custom SQL query")
        print("  7. Database statistics")
        print("  0. Exit")

        choice = input("\nEnter choice: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            query_pages()

        elif choice == "2":
            country = input("Enter country name: ").strip()
            query_pages(country=country)

        elif choice == "3":
            query_visas()

        elif choice == "4":
            country = input("Enter country name: ").strip()
            query_visas(country=country)

        elif choice == "5":
            visa_type = input("Enter visa type: ").strip()
            country = input("Enter country: ").strip()
            query_visa_history(visa_type, country)

        elif choice == "6":
            print("\nEnter SQL query (or 'examples' for examples):")
            sql = input().strip()

            if sql.lower() == 'examples':
                print("\nExample queries:")
                print("  SELECT * FROM crawled_pages WHERE country = 'australia' LIMIT 5")
                print("  SELECT visa_type, country, version FROM visas WHERE is_latest = 1")
                print("  SELECT country, COUNT(*) as count FROM visas GROUP BY country")
                continue

            if sql:
                custom_query(sql)

        elif choice == "7":
            db = Database()
            stats = db.get_stats()
            print("\n📊 DATABASE STATISTICS:")
            print("-" * 80)
            for key, value in stats.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
