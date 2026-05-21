"""Modern scrape_all implementation using JobSpy.

This module provides a replacement for the legacy scrape_all function,
using the modern JobService and JobSpy integration for job scraping.
"""

import asyncio
import logging

from src.services.job_service import job_service

logger = logging.getLogger(__name__)


async def scrape_all() -> dict[str, int]:
    """Scrape jobs from all major job sites and return statistics.

    This function replaces the legacy scrape_all implementation with
    a modern JobSpy-based approach that scrapes from multiple job sites
    and provides statistics about the results.

    Returns:
        dict[str, int]: Statistics about the scraping operation:
            - 'inserted': Number of new jobs added
            - 'updated': Number of existing jobs updated
            - 'skipped': Number of jobs skipped (duplicates)
    """
    logger.info("Starting modern scrape_all using JobSpy integration")

    total_stats = {"inserted": 0, "updated": 0, "skipped": 0}

    try:
        # Custom queries targeting FAANG, YC, and Remote roles for India-based candidates
        search_queries = [
            # 1. FAANG / Big Tech in India
            {"term": "software engineer google", "location": "India"},
            {"term": "software engineer meta", "location": "India"},
            {"term": "software engineer microsoft", "location": "India"},
            {"term": "software engineer amazon", "location": "India"},
            
            # 2. YC / Startups / Remote
            {"term": "software engineer y combinator", "location": "India"},
            {"term": "software engineer remote", "location": "India"},
            {"term": "machine learning engineer remote", "location": "India"},
            
            # 3. Core Software Engineering / AI
            {"term": "software engineer", "location": "India"},
            {"term": "backend engineer", "location": "India"},
            {"term": "frontend engineer", "location": "India"},
            {"term": "machine learning engineer", "location": "India"},
            {"term": "ai engineer", "location": "India"},
            {"term": "data engineer", "location": "India"},
            {"term": "SDE", "location": "India"},
            {"term": "full stack developer", "location": "India"},
        ]

        # Focus on LinkedIn to avoid Datacenter IP blocks/hangs from Indeed/Glassdoor
        sites = ["linkedin"]

        for query in search_queries:
            search_term = query["term"]
            location = query["location"]
            try:
                logger.info("Scraping jobs for: %s in %s", search_term, location)

                # Use JobService to scrape and save jobs
                result = await job_service.search_and_save_jobs(
                    search_term=search_term,
                    location=location,
                    sites=sites,
                    results_wanted=8,  # Smaller batch per query for rapid scraping
                    save_to_db=True,
                )

                # Count new jobs as "inserted"
                jobs_found = len(result.jobs)
                total_stats["inserted"] += jobs_found

                logger.info("Found %d jobs for '%s' in %s", jobs_found, search_term, location)

            except Exception as e:
                logger.warning("Failed to scrape jobs for '%s': %s", search_term, e)
                # Continue with other search terms
                continue
    except Exception:
        logger.exception("Critical error in scrape_all")
        # Return empty stats on total failure
        return {"inserted": 0, "updated": 0, "skipped": 0}
    else:
        logger.info("Scrape_all completed successfully. Stats: %s", total_stats)
        return total_stats


def scrape_all_sync() -> dict[str, int]:
    """Synchronous wrapper for scrape_all function.

    Provides a synchronous interface for cases where async/await cannot be used.
    This is the function that should be used by Streamlit UI components.

    Returns:
        dict[str, int]: Statistics from async scrape_all().
    """
    try:
        return asyncio.run(scrape_all())
    except Exception:
        logger.exception("Failed to run scrape_all_sync")
        return {"inserted": 0, "updated": 0, "skipped": 0}
