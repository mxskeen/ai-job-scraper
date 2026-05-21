#!/usr/bin/env python
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from src.db.migrations import run_migrations
    from src.scraping.scrape_all import scrape_all_sync
except ImportError as e:
    print(f"Error importing scraper modules: {e}")
    print("Make sure you are running this from the ai-job-scraper directory inside your virtual environment.")
    sys.exit(1)

if __name__ == "__main__":
    print("Initializing database...")
    run_migrations()
    print("Starting job scraping...")
    stats = scrape_all_sync()
    print(f"Scraping completed! Stats: {stats}")
