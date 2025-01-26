# base_scraper.py

import os
import re
import hashlib
import undetected_chromedriver as uc
import logging
import json
import subprocess
import sys
import threading
import queue
import time
import warnings

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from bs4 import BeautifulSoup

from urllib.parse import urljoin, urlparse
from typing import List, Set, Optional
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import SessionNotCreatedException

# İsteğe bağlı: readability-lxml
try:
    from readability import Document
    USE_READABILITY = True
except ImportError:
    USE_READABILITY = False

# Domain line frequency (opsiyonel)
from collections import defaultdict
domain_line_frequency = defaultdict(lambda: defaultdict(int))

# Projeden import
from .models import PageContent   # Aynı package içindeki models.py

OUTPUTS_DIR = "outputs"
os.makedirs(OUTPUTS_DIR, exist_ok=True)


class UniversalScraper(threading.Thread):
    def __init__(
        self, 
        base_url: str, 
        max_depth: Optional[int] = None, 
        data_queue: Optional[queue.Queue] = None,
        save_links: bool = True,
        save_articles: bool = True
    ):
        super().__init__()
        self.base_url = base_url
        self.allowed_domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.visited_urls: Set[str] = set()
        self.all_links: Set[str] = set()
        self.page_contents: List[PageContent] = []

        self.save_links_flag = save_links
        self.save_articles_flag = save_articles

        self.content_hashes: Set[str] = set()

        sanitized = re.sub(r'[^a-zA-Z0-9]', '_', base_url)
        self.links_output_file = os.path.join(OUTPUTS_DIR, f"collected_links_{sanitized}.json")
        self.articles_output_file = os.path.join(OUTPUTS_DIR, f"collected_articles_{sanitized}.json")

        self.pages_scraped = 0
        self.data_queue = data_queue
        self.lock = threading.Lock()

        # Logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('universal_scraper.log', mode='a', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Chrome driver options
        def create_options():
            opts = Options()
            opts.add_argument('--headless')
            opts.add_argument('--no-sandbox')
            opts.add_argument('--disable-dev-shm-usage')
            opts.add_argument('--ignore-certificate-errors')
            return opts

        chrome_options = create_options()

        # Detect Chrome version
        chrome_version = self._get_chrome_version()
        if not chrome_version:
            self.logger.warning(f"[{self.base_url}] Could not detect Chrome version. Fallback to 108.")
            chrome_version = 108

        try:
            self.driver = uc.Chrome(options=chrome_options, version_main=chrome_version)
        except SessionNotCreatedException as e:
            msg = str(e)
            version_match = re.search(r'Current browser version is (\d+)', msg)
            if version_match:
                version = int(version_match.group(1))
                self.logger.info(f"[{self.base_url}] Re-trying with Chrome version: {version}.")
                new_options = create_options()
                self.driver = uc.Chrome(options=new_options, version_main=version)
            else:
                raise e

    def _get_chrome_version(self) -> Optional[int]:
        # Mevcut yapıyı bozmadan
        try:
            if sys.platform.startswith('win'):
                process = subprocess.Popen(
                    ['reg', 'query',
                     'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon',
                     '/v', 'version'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
                stdout, stderr = process.communicate()
                version_match = re.search(r'\d+\.\d+\.\d+\.\d+', stdout.decode())
                if version_match:
                    version_str = version_match.group()
                    return int(version_str.split('.')[0])
            elif sys.platform.startswith('darwin'):
                try:
                    process = subprocess.Popen(
                        ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    stdout, stderr = process.communicate()
                    version_match = re.search(r'\d+\.\d+\.\d+\.\d+', stdout.decode())
                    if version_match:
                        return int(version_match.group().split('.')[0])
                except FileNotFoundError:
                    # Ek path fallback
                    ...
            else:
                process = subprocess.Popen(
                    ['google-chrome', '--version'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate()
                version_match = re.search(r'\d+\.\d+\.\d+\.\d+', stdout.decode())
                if version_match:
                    return int(version_match.group().split('.')[0])

        except Exception as e:
            self.logger.error(f"[{self.base_url}] Failed to detect Chrome version: {e}")
            return None
        return None

    def _is_valid_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            return (
                bool(parsed.netloc) and
                parsed.netloc == self.allowed_domain and
                not any(ext in url.lower() for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.gif'])
            )
        except:
            return False

    def _extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/'):
                href = urljoin(current_url, href)
            if self._is_valid_url(href):
                links.append(href)
        return links

    def _find_title(self, html_text: str, soup: BeautifulSoup) -> Optional[str]:
        # (Klasik title bulma mantığı)
        # ...
        return "title"

    def _find_content(self, html_text: str, domain: str) -> Optional[str]:
        # ...
        return "content"

    def _save_links(self):
        if not self.save_links_flag:
            return
        with self.lock:
            with open(self.links_output_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.all_links), f, ensure_ascii=False, indent=2)
        self.logger.info(f"[{self.base_url}] Links saved to {self.links_output_file}")

    def _save_articles(self):
        if not self.save_articles_flag:
            return
        with self.lock:
            data = [asdict(pc) for pc in self.page_contents]
            with open(self.articles_output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"[{self.base_url}] Articles saved to {self.articles_output_file}")

    def _dfs(self, url: str, current_depth: int, max_pages: Optional[int] = None):
        # DFS mantığı
        # ...
        pass

    def scrape_links_dfs(self, max_pages: Optional[int] = None):
        self.logger.info(f"[{self.base_url}] Starting DFS")
        self._dfs(self.base_url, 0, max_pages=max_pages)
        self.logger.info(
            f"[{self.base_url}] DFS completed. "
            f"Total unique links: {len(self.all_links)} | Pages with content: {len(self.page_contents)}"
        )

    def run(self):
        self.scrape_links_dfs()

    def close(self):
        self.driver.quit()
