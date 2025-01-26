# __init__.py

from .models import PageContent
from .base_scraper import UniversalScraper
from .multi_scraper import MultiUniversalScraper

__all__ = [
    "PageContent",
    "UniversalScraper",
    "MultiUniversalScraper"
]
