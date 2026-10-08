"""
Main Pipeline Orchestrator
==========================
Coordinates the entire daily research intelligence cycle:
Fetch -> Filter -> Deduplicate -> Score & Rank -> Concepts -> Summary ->
Insights -> Infographic -> Daily Report -> Ledger & Archive -> README & Site.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from src.analyzer import analyze_paper
from src.archive import (
    generate_daily_markdown_report,
    sync_site_data,
    update_archives,
    update_papers_ledger,
    update_statistics,
)
from src.concepts import extract_key_concepts
from src.config import AppConfig, get_repo_root, load_config
from src.fetcher import ArxivFetcher, Paper
from src.filter import filter_and_deduplicate, load_existing_arxiv_ids
from src.infographic import generate_daily_infographic
from src.readme import update_readme
from src.scorer import RelevanceScorer
from src.summarizer import generate_summary
from src.utils import format_display_date, format_path_date, safe_read_json, setup_logger

logger = setup_logger("main")


def run_pipeline(
    config: AppConfig,
    run_date: datetime,
    force: bool = False
) -> int:
    """
    Executes the end-to-end Daily Tech Intelligence pipeline.
    Returns 0 on success, non-zero on fatal failure.
    """
    logger.info("=" * 70)
    logger.info("STARTING DAILY TECH INTELLIGENCE PIPELINE")
    logger.info(f"Execution Date : {run_date.strftime('%Y-%m-%d')} ({format_display_date(run_date)})")
    logger.info(f"Target Papers  : {config.papers_per_day}")
    logger.info(f"Dry Run Mode   : {config.dry_run}")
    logger.info("=" * 70)

    # 1. Deduplication Ledger
    existing_ids = set() if force else load_existing_arxiv_ids(config.data_file)
    logger.info(f"Tracking {len(existing_ids)} previously processed papers.")

    # 2. Fetch Candidates
    fetcher = ArxivFetcher(config)
    raw_candidates = fetcher.fetch_papers(limit=config.fetch_limit)
    if not raw_candidates:
        logger.warning("No papers retrieved from arXiv. Pipeline terminating gracefully.")
        return 0

    # 3. Filter & Deduplicate
    filtered_candidates = filter_and_deduplicate(raw_candidates, existing_ids)
    if not filtered_candidates:
        logger.info("All retrieved papers have already been processed or filtered out. No new updates today.")
        return 0

    # 4. Score and Rank
    scorer = RelevanceScorer(config)
    selected_papers = scorer.rank_and_select(filtered_candidates)
    if not selected_papers:
        logger.info(f"No papers met the minimum relevance threshold ({config.minimum_relevance_score}).")
        return 0

    # 5. Process Each Selected Paper (Isolated error boundaries)
    processed_date_str = run_date.strftime("%Y-%m-%d")
    final_papers: List[Paper] = []

    for idx, paper in enumerate(selected_papers, start=1):
        try:
            paper.processed_date = processed_date_str
            # Key Concepts
            extract_key_concepts(paper, max_concepts=config.max_key_concepts)
            # 100-200 word summary
            generate_summary(paper, target_min=config.summary_word_min, target_max=config.summary_word_max)
            # Technical insights (Problem, Approach, Innovation, Results, Applications, Limitations)
            analyze_paper(paper)

            final_papers.append(paper)
            logger.info(
                f"[{idx}/{len(selected_papers)}] Processed: '{paper.title[:55]}...' "
                f"(Score: {paper.relevance_score:.2f}, Topic: {paper.primary_topic})"
            )
        except Exception as p_err:
            logger.error(f"Error processing paper {paper.arxiv_id}; continuing with others: {p_err}", exc_info=True)

    if not final_papers:
        logger.error("No papers were successfully processed. Terminating.")
        return 1

    # 6. Determine Paths for Today
    year, month, day = format_path_date(run_date)
    today_report_dir = config.reports_dir / year / month / day
    report_file = today_report_dir / "report.md"
    infographic_file = today_report_dir / "infographic.png"

    # 7. Generate Infographic
    has_infographic = False
    try:
        has_infographic = generate_daily_infographic(
            papers=final_papers,
            display_date=format_display_date(run_date),
            output_path=infographic_file
        )
    except Exception as info_err:
        logger.error(f"Infographic generation encountered an error: {info_err}. Continuing with report generation.")

    # 8. Generate Daily Markdown Report
    try:
        generate_daily_markdown_report(
            papers=final_papers,
            run_date=run_date,
            report_path=report_file,
            has_infographic=has_infographic
        )
    except Exception as rep_err:
        logger.error(f"Error generating daily Markdown report: {rep_err}", exc_info=True)
        return 1

    # 9. Persistence, Archives, README, and Site Sync
    if config.dry_run:
        logger.info("[DRY RUN] Skipping persistent ledger, archive commit, and README update.")
        logger.info(f"[DRY RUN] Generated preview report at: {report_file}")
        if has_infographic:
            logger.info(f"[DRY RUN] Generated preview infographic at: {infographic_file}")
    else:
        logger.info("Persisting paper records to ledger...")
        all_papers = update_papers_ledger(final_papers, config.data_file)

        logger.info("Updating aggregate project statistics...")
        stats = update_statistics(final_papers, run_date, config.statistics_file, all_papers)

        logger.info("Updating archive indices...")
        update_archives(all_papers, config.archive_dir)

        logger.info("Synchronizing data to GitHub Pages site...")
        sync_site_data(config.site_dir, config.reports_dir, all_papers, stats)

        logger.info("Updating README.md with latest metrics...")
        update_readme(final_papers, all_papers, stats, run_date, config.repo_root)

    logger.info("=" * 70)
    logger.info("DAILY TECH INTELLIGENCE PIPELINE COMPLETED SUCCESSFULLY")
    logger.info(f"Processed & Published: {len(final_papers)} research breakthroughs")
    logger.info("=" * 70)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily Tech Intelligence Automation CLI")
    parser.add_argument("--dry-run", action="store_true", help="Run without writing persistent updates or Git commits")
    parser.add_argument("--max-papers", type=int, default=None, help="Override number of papers to select (default: 10)")
    parser.add_argument("--force", action="store_true", help="Bypass deduplication filter for testing")
    parser.add_argument("--date", type=str, default=None, help="Execution date override in YYYY-MM-DD format")
    args = parser.parse_args()

    repo_root = get_repo_root()
    overrides = {}
    if args.dry_run:
        overrides["dry_run"] = True
    if args.max_papers:
        overrides["papers_per_day"] = args.max_papers

    config = load_config(repo_root=repo_root, overrides=overrides)

    if args.date:
        try:
            run_date = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            logger.error("Invalid date format. Expected YYYY-MM-DD.")
            sys.exit(1)
    else:
        run_date = datetime.now(timezone.utc)

    exit_code = run_pipeline(config=config, run_date=run_date, force=args.force)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
