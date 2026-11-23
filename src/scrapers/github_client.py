import aiohttp
import asyncio
import os
import re
import logging
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)
GITHUB_API = "https://api.github.com"
def parse_repo_url(url):
    """Extract owner and repository from a GitHub URL."""
    if not url:
        return None
    match = re.match(
        r"https?://github\.com/([^/]+)/([^/#?]+)",
        url
    )
    if not match:
        return None
    owner, repo = match.groups()
    repo = repo.removesuffix(".git")
    return owner, repo
async def get_github_stars(session, repo_url):
    """Fetch the current repository star count."""
    parsed = parse_repo_url(repo_url)
    if not parsed:
        return None
    owner, repo = parsed
    url = f"{GITHUB_API}/repos/{owner}/{repo}"
    for attempt in range(4):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("stargazers_count")
                if response.status == 404:
                    logger.warning(
                        "Repository not found: %s",
                        repo_url
                    )
                    return None
                if response.status == 403:
                    logger.warning(
                        "GitHub rate limit or access restriction."
                    )
                    return None
                if response.status == 429 or response.status >= 500:
                    await asyncio.sleep(2 ** attempt)
                    continue
                logger.warning(
                    "GitHub returned status %s",
                    response.status
                )
                return None
        except (
            aiohttp.ClientError,
            asyncio.TimeoutError
        ) as error:
            logger.warning(
                "GitHub request failed: %s",
                error
            )
            await asyncio.sleep(2 ** attempt)
    return None
async def enrich_github_metrics(papers):
    """Add GitHub stars to research paper records."""
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    connector = aiohttp.TCPConnector(limit=5)
    async with aiohttp.ClientSession(
        headers=headers,
        connector=connector,
        timeout=aiohttp.ClientTimeout(total=30)
    ) as session:
        semaphore = asyncio.Semaphore(5)
        async def process(paper):
            content = paper["content"]
            repo_url = content.get("github_url")
            if not repo_url:
                return
            async with semaphore:
                stars = await get_github_stars(
                    session,
                    repo_url
                )
                content["github_stars"] = stars
        await asyncio.gather(
            *(process(paper) for paper in papers)
        )
    return papers