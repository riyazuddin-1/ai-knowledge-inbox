# workers/url-parser/parser.py
from bs4 import BeautifulSoup
import requests
from sqlalchemy.orm import Session

from shared.models.content import ContentStatus
from shared.repositories.content import (
    add_title,
    get_by_id,
    update_status,
)
from workers.chunk_embed.handler import process_content_embedding

def parse_and_process_url(db: Session, content_id: int, url: str):
  """Fetches a URL server-side using BeautifulSoup, extracts title and text,

  updates the database, and passes it along to the chunk-embed handler.
  """
  try:
    # 1. Update status to processing
    update_status(db, content_id, ContentStatus.PROCESSING)

    # 2. Set headers to mimic a real browser and prevent 403 blocks
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    # 3. Parse HTML content with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title (<title> tag or fallback to hostname/URL)
    page_title = soup.title.string.strip() if soup.title and soup.title.string else url

    # Remove unwanted tags that clutter text content
    for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
      script_or_style.decompose()

    # Extract human-readable text from the body
    raw_text = soup.get_text(separator=" ", strip=True)

    if not raw_text:
      raise ValueError("Extracted page content is empty.")

    # 4. Save the extracted title to the content record
    add_title(db, content_id, page_title)

    # 5. Hand off text directly to your chunk & embed worker pipeline
    process_content_embedding(db=db, content_id=content_id, raw_text=raw_text)

  except Exception as e:
    update_status(db, content_id, ContentStatus.FAILED)
    print(f"Error parsing URL {url} for content ID {content_id}: {e}")
    raise e
