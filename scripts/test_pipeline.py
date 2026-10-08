#!/usr/bin/env python3
"""
Safe Pipeline Verification Script
=================================
Runs an end-to-end verification of the Daily Tech Intelligence pipeline
in safe dry-run mode without modifying production databases or committing to Git.

Usage:
    python scripts/test_pipeline.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Add repo root to Python path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import load_config
from src.main import run_pipeline
from src.utils import setup_logger

logger = setup_logger("test_pipeline")


def main():
    logger.info("=" * 60)
    logger.info("DAILY TECH INTELLIGENCE - END-TO-END VERIFICATION")
    logger.info("=" * 60)

    # Force safe dry run and 3 papers for fast verification
    config = load_config(
        repo_root=REPO_ROOT,
        overrides={
            "dry_run": True,
            "papers_per_day": 3,
            "fetch_limit": 15
        }
    )

    run_date = datetime.now(timezone.utc)
    logger.info(f"Target Directory: {REPO_ROOT}")
    logger.info("Running pipeline with --dry-run and max 3 papers...")

    exit_code = run_pipeline(config=config, run_date=run_date, force=True)

    if exit_code == 0:
        logger.info("Verification PASSED: Pipeline ran cleanly without errors!")
        sys.exit(0)
    else:
        logger.error(f"Verification FAILED: Pipeline exited with code {exit_code}")
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
