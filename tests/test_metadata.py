"""
Unit Tests: Metadata Parsing and Utilities
"""

from src.fetcher import ArxivFetcher
from src.utils import (
    clean_text,
    count_words,
    extract_base_arxiv_id,
    format_display_date,
    parse_datetime,
)


def test_extract_base_arxiv_id():
    assert extract_base_arxiv_id("http://arxiv.org/abs/2403.00101v2") == "2403.00101"
    assert extract_base_arxiv_id("2403.00101v1") == "2403.00101"
    assert extract_base_arxiv_id("https://arxiv.org/pdf/2403.00101.pdf") == "2403.00101"
    assert extract_base_arxiv_id("cs/0102034v1") == "cs/0102034"


def test_clean_text():
    raw = "  This   is a \n test with $O(N)$  complexity.  "
    cleaned = clean_text(raw)
    assert cleaned == "This is a test with O(N) complexity."


def test_date_parsing_and_formatting():
    dt = parse_datetime("2026-10-08T06:30:00Z")
    formatted = format_display_date(dt)
    assert "08 October 2026" in formatted


def test_arxiv_atom_feed_parsing(test_config):
    xml_sample = """<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/2403.99999v1</id>
        <title> Breakthrough in Edge AI Computing </title>
        <summary> High efficiency inference on microcontrollers. </summary>
        <published>2026-10-08T00:00:00Z</published>
        <updated>2026-10-08T00:00:00Z</updated>
        <author><name>Dr. Scientist</name></author>
        <category term="cs.AI"/>
        <link rel="alternate" type="text/html" href="http://arxiv.org/abs/2403.99999v1"/>
      </entry>
    </feed>
    """
    fetcher = ArxivFetcher(test_config)
    parsed = fetcher._parse_atom_feed(xml_sample)
    assert len(parsed) == 1
    assert parsed[0].arxiv_id == "2403.99999"
    assert parsed[0].title == "Breakthrough in Edge AI Computing"
    assert parsed[0].authors == ["Dr. Scientist"]
    assert "cs.AI" in parsed[0].categories
