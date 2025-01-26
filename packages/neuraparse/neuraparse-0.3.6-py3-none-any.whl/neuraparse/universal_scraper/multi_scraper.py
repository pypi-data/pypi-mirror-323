# multi_scraper.py

import os
import json
import logging
import time
import queue
from dataclasses import asdict
from typing import List, Dict, Set, Optional, Callable
import threading

# Projeden import
from .base_scraper import UniversalScraper
from .models import PageContent

OUTPUTS_DIR = "outputs"
os.makedirs(OUTPUTS_DIR, exist_ok=True)

class MultiUniversalScraper:
    def __init__(
        self,
        base_urls: List[str],
        max_depth: Optional[int] = None,
        on_new_article: Optional[Callable[[PageContent], None]] = None,
        save_pool_links: bool = True,
        save_pool_articles: bool = True
    ):
        self.base_urls = base_urls
        self.max_depth = max_depth
        self.scrapers: Dict[str, UniversalScraper] = {}
        self.all_links: Set[str] = set()
        self.all_page_contents: List[PageContent] = []
        self.data_queue = queue.Queue()
        self.lock = threading.Lock()
        self.on_new_article = on_new_article

        self.save_pool_links = save_pool_links
        self.save_pool_articles = save_pool_articles

        self.pool_links_output_file = os.path.join(OUTPUTS_DIR, "all_collected_links.json")
        self.pool_articles_output_file = os.path.join(OUTPUTS_DIR, "all_collected_articles.json")

        self.stop_event = threading.Event()
        self.listener_thread = threading.Thread(target=self._listen_data)
        self.listener_thread.start()

        # Her URL için bir UniversalScraper
        for url in base_urls:
            scraper = UniversalScraper(
                url,
                max_depth=max_depth,
                data_queue=self.data_queue,
                save_links=save_pool_links,
                save_articles=save_pool_articles
            )
            self.scrapers[url] = scraper

    def _listen_data(self):
        while not self.stop_event.is_set() or not self.data_queue.empty():
            try:
                data_type, data = self.data_queue.get(timeout=1)
                if data_type == 'article':
                    with self.lock:
                        self.all_page_contents.append(data)
                        self.all_links.add(data.url)
                    if self.on_new_article:
                        self.on_new_article(data)

                elif data_type == 'new_link':
                    with self.lock:
                        self.all_links.add(data)
            except queue.Empty:
                continue

    def scrape_all(self, max_pages: Optional[int] = None):
        threads = []
        for scraper in self.scrapers.values():
            scraper.start()
            threads.append(scraper)

        for t in threads:
            t.join()

        time.sleep(1)
        self.stop_event.set()
        self.listener_thread.join()

        self._save_pool_links()
        self._save_pool_articles()

    def _save_pool_links(self):
        if not self.save_pool_links:
            return
        with self.lock:
            links_list = list(self.all_links)
        with open(self.pool_links_output_file, 'w', encoding='utf-8') as f:
            json.dump(links_list, f, ensure_ascii=False, indent=2)
        logging.info(f"All links saved to {self.pool_links_output_file}")

    def _save_pool_articles(self):
        if not self.save_pool_articles:
            return
        with self.lock:
            data = [asdict(pc) for pc in self.all_page_contents]
        with open(self.pool_articles_output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"All articles saved to {self.pool_articles_output_file}")

    def close_all(self):
        for scraper in self.scrapers.values():
            scraper.close()
