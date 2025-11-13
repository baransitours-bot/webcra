"""
Database utilities
Handles data storage and retrieval
"""

import json
import os
from typing import List, Dict
from pathlib import Path

class DataStore:
    """Simple JSON-based data store for MVP"""

    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "raw"
        self.processed_path = self.base_path / "processed"

        # Create directories
        self.raw_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)

    def save_raw_page(self, country: str, page_data: dict):
        """Save raw crawled page"""
        country_dir = self.raw_path / country
        country_dir.mkdir(exist_ok=True)

        filename = f"{hash(page_data['url'])}.json"
        filepath = country_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)

    def load_raw_pages(self, country: str) -> List[dict]:
        """Load all raw pages for a country"""
        country_dir = self.raw_path / country
        if not country_dir.exists():
            return []

        pages = []
        for filepath in country_dir.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                pages.append(json.load(f))

        return pages

    def save_structured_visas(self, visas: List[dict]):
        """Save structured visa data"""
        filepath = self.processed_path / "visas.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(visas, f, indent=2, ensure_ascii=False)

    def load_structured_visas(self) -> List[dict]:
        """Load all structured visa data"""
        filepath = self.processed_path / "visas.json"
        if not filepath.exists():
            return []

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
