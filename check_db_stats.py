#!/usr/bin/env python3
"""Check database statistics"""

import sqlite3
import os

db_path = "/home/user/webcra/data/immigration.db"

print(f"Database file: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")
print(f"File size: {os.path.getsize(db_path) if os.path.exists(db_path) else 0} bytes")
print()

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 60)
    print("CRAWLED_PAGES TABLE")
    print("=" * 60)

    # Total pages
    cursor.execute("SELECT COUNT(*) as count FROM crawled_pages")
    total_pages = cursor.fetchone()['count']
    print(f"Total pages (all versions): {total_pages}")

    # Latest pages
    cursor.execute("SELECT COUNT(*) as count FROM crawled_pages WHERE is_latest = 1")
    latest_pages = cursor.fetchone()['count']
    print(f"Latest pages (is_latest=1): {latest_pages}")

    # Check is_latest values
    cursor.execute("SELECT is_latest, COUNT(*) as count FROM crawled_pages GROUP BY is_latest")
    print("\nPages by is_latest value:")
    for row in cursor.fetchall():
        print(f"  is_latest={row['is_latest']}: {row['count']} pages")

    # Sample pages
    cursor.execute("SELECT id, country, title, is_latest FROM crawled_pages LIMIT 5")
    print("\nSample pages:")
    for row in cursor.fetchall():
        print(f"  ID={row['id']}, Country={row['country']}, is_latest={row['is_latest']}, Title={row['title'][:50]}")

    print()
    print("=" * 60)
    print("VISAS TABLE")
    print("=" * 60)

    # Total visas
    cursor.execute("SELECT COUNT(*) as count FROM visas")
    total_visas = cursor.fetchone()['count']
    print(f"Total visas (all versions): {total_visas}")

    # Latest visas
    cursor.execute("SELECT COUNT(*) as count FROM visas WHERE is_latest = 1")
    latest_visas = cursor.fetchone()['count']
    print(f"Latest visas (is_latest=1): {latest_visas}")

    # Check is_latest values
    cursor.execute("SELECT is_latest, COUNT(*) as count FROM visas GROUP BY is_latest")
    print("\nVisas by is_latest value:")
    for row in cursor.fetchall():
        print(f"  is_latest={row['is_latest']}: {row['count']} visas")

    # Sample visas
    cursor.execute("SELECT id, country, visa_type, is_latest FROM visas LIMIT 5")
    print("\nSample visas:")
    for row in cursor.fetchall():
        print(f"  ID={row['id']}, Country={row['country']}, is_latest={row['is_latest']}, Visa={row['visa_type'][:50]}")

    print()
    print("=" * 60)
    print("SETTINGS TABLE")
    print("=" * 60)

    cursor.execute("SELECT COUNT(*) as count FROM settings")
    settings_count = cursor.fetchone()['count']
    print(f"Total settings: {settings_count}")

    cursor.execute("SELECT key FROM settings")
    print("\nSettings keys:")
    for row in cursor.fetchall():
        print(f"  - {row['key']}")

    conn.close()
