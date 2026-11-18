import logging

from bs4 import BeautifulSoup
import httpx

from app.core.database import SessionLocal
from app.models.content import ContentStatus
from app.repositories.content import add_title, update_status
from app.workers.tasks.embedding import run_embedding_task

logger = logging.getLogger(__name__)
MAX_PARSED_URL_CONTENT_CHARS = 5000


def run_url_parser_task(content_id: int, url: str):
    """Background task that manages its own independent database session for URL parsing."""
    db = None
    try:
        db = SessionLocal()
        if update_status(db, content_id, ContentStatus.PROCESSING) is None:
            logger.error("Cannot parse URL for content ID %s because it no longer exists.", content_id)
            return

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        page_title = soup.title.string.strip() if soup.title and soup.title.string else url

        for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
            script_or_style.decompose()

        raw_text = soup.get_text(separator=" ", strip=True)[:MAX_PARSED_URL_CONTENT_CHARS]
        if not raw_text:
            raise ValueError("The requested page contained no extractable text.")

        if add_title(db, content_id, page_title) is None:
            raise RuntimeError(f"Content ID {content_id} disappeared during URL parsing.")
        
        run_embedding_task(content_id=content_id, raw_text=raw_text)

    except Exception:
        logger.exception("URL parsing task failed for content ID %s.", content_id)
        if db is not None:
            try:
                db.rollback()
                if update_status(db, content_id, ContentStatus.FAILED) is None:
                    logger.error("Could not mark missing content ID %s as failed.", content_id)
            except Exception:
                logger.exception("Could not mark content ID %s as failed.", content_id)
    finally:
        if db is not None:
            try:
                db.close()
            except Exception:
                logger.exception("Could not close the URL parsing DB session for content ID %s.", content_id)
