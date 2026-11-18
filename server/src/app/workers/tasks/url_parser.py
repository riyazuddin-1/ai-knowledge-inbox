from bs4 import BeautifulSoup
import requests

from app.core.database import SessionLocal
from app.models.content import ContentStatus
from app.repositories.content import add_title, update_status
from app.workers.tasks.embedding import run_embedding_task

def run_url_parser_task(content_id: int, url: str):
    """Background task that manages its own independent database session for URL parsing."""
    db = SessionLocal()
    try:
        update_status(db, content_id, ContentStatus.PROCESSING)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        page_title = soup.title.string.strip() if soup.title and soup.title.string else url

        for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
            script_or_style.decompose()

        raw_text = soup.get_text(separator=" ", strip=True)
        if not raw_text:
            raise ValueError("Extracted page content is empty.")

        add_title(db, content_id, page_title)
        
        # Forwarding text to generate embeddings
        run_embedding_task(content_id=content_id, raw_text=raw_text)

    except Exception as e:
        update_status(db, content_id, ContentStatus.FAILED)
        print(f"Error parsing URL {url} for content ID {content_id}: {e}")
        raise e
    finally:
        db.close()
