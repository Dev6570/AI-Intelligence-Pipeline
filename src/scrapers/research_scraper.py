import asyncio
import aiohttp
import xml.etree.ElementTree as ET
import json
import re
import logging
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse
from src.scrapers.github_client import enrich_github_metrics
BASE_URL = "https://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def clean_text(value):
    return " ".join((value or "").split())
def extract_github_url(text):
    """Extract an explicitly mentioned GitHub repository URL."""
    urls = re.findall(
        r"https?://github\.com/[\w.-]+/[\w.-]+",
        text or "",
        flags=re.IGNORECASE
    )
    for url in urls:
        parsed = urlparse(url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2:
            owner, repo = parts[0], parts[1]
            if repo.lower() not in {
                "issues", "pulls", "topics", "settings"
            }:
                return f"https://github.com/{owner}/{repo}"
    return None
def parse_paper(entry):
    """Convert one arXiv XML entry into a structured record."""
    title = clean_text(
        entry.findtext(f"{ATOM}title")
    )
    abstract = clean_text(
        entry.findtext(f"{ATOM}summary")
    )
    paper_url = clean_text(
        entry.findtext(f"{ATOM}id")
    )
    published = clean_text(
        entry.findtext(f"{ATOM}published")
    )
    authors = [
        clean_text(author.findtext(f"{ATOM}name"))
        for author in entry.findall(f"{ATOM}author")
    ]
    comment = clean_text(
        entry.findtext(f"{ARXIV}comment")
    )
    github_url = extract_github_url(
        comment + " " + abstract
    )
    return {
        "schemaVersion": "1.0",
        "recordType": "RESEARCH_PAPER",
        "source": {
            "name": "arXiv",
            "url": paper_url
        },
        "content": {
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "paper_url": paper_url,
            "github_url": github_url,
            "github_stars": None,
            "published_date": published
        },
        "collectedAt": datetime.now(
            timezone.utc
        ).isoformat()
    }
async def fetch_arxiv_page(
    session,
    start,
    page_size=100
):
    """Fetch one page of arXiv results."""
    params = {
        "search_query": (
            "cat:cs.AI OR cat:cs.LG OR "
            "cat:cs.CL OR cat:cs.CV"
        ),
        "start": start,
        "max_results": page_size,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    async with session.get(
        BASE_URL,
        params=params,
        timeout=aiohttp.ClientTimeout(total=90)
    ) as response:
        response.raise_for_status()
        xml_data = await response.text()
        root = ET.fromstring(xml_data)
        entries = root.findall(f"{ATOM}entry")
        papers = []
        for entry in entries:
            paper = parse_paper(entry)
            if (
                paper["content"]["title"]
                and paper["content"]["paper_url"]
            ):
                papers.append(paper)
        return papers
async def scrape_research_papers(
    target=1000,
    page_size=100
):
    """Collect research papers with safe pagination."""
    papers = {}
    start = 0
    connector = aiohttp.TCPConnector(limit=1)
    async with aiohttp.ClientSession(
        connector=connector,
        headers={
            "User-Agent": "AIIntelligencePipeline/1.0"
        }
    ) as session:
        while len(papers) < target:
            logger.info(
                "Fetching arXiv page. Start=%s",
                start
            )
            try:
                batch = await fetch_arxiv_page(
                    session,
                    start,
                    page_size
                )
            except Exception as error:
                logger.exception(
                    "arXiv request failed: %s",
                    error
                )
                break
            if not batch:
                logger.info("No more records available.")
                break
            for paper in batch:
                url = paper["content"]["paper_url"]
                papers[url] = paper
            logger.info(
                "Unique papers collected: %s",
                len(papers)
            )
            start += len(batch)
            if len(papers) >= target:
                break
            await asyncio.sleep(3)
    return list(papers.values())[:target]
def save_research_data(papers):
    """Save collected papers as JSON and CSV."""
    json_path = OUTPUT_DIR / "research_papers.json"
    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            papers,
            file,
            indent=4,
            ensure_ascii=False
        )
    import pandas as pd
    csv_path = OUTPUT_DIR / "research_papers.csv"
    rows = []
    for paper in papers:
        content = paper["content"]
        rows.append({
            "title": content["title"],
            "authors": ", ".join(content["authors"]),
            "paper_url": content["paper_url"],
            "github_url": content["github_url"],
            "github_stars": content["github_stars"],
            "published_date": content["published_date"],
            "collectedAt": paper["collectedAt"]
        })
    pd.DataFrame(rows).to_csv(
        csv_path,
        index=False
    )
    logger.info("JSON saved: %s", json_path)
    logger.info("CSV saved: %s", csv_path)
async def main():
    papers = await scrape_research_papers(
        target=1000,
        page_size=100
    )
    print("Papers collected:", len(papers))
    papers = await enrich_github_metrics(papers)
    save_research_data(papers)
    linked = sum(
        1 for paper in papers
        if paper["content"]["github_url"]
    )
    enriched = sum(
        1 for paper in papers
        if paper["content"]["github_stars"] is not None
    )
    print("\nResearch Scraping Completed")
    print("Total papers:", len(papers))
    print("Papers with repository links:", linked)
    print("Papers with verified star counts:", enriched)
if __name__ == "__main__":
    asyncio.run(main())