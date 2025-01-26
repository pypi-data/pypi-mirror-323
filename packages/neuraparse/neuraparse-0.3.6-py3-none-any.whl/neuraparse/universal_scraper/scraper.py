import os
import re
import hashlib
import undetected_chromedriver as uc

from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import SessionNotCreatedException

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from bs4 import BeautifulSoup
import logging
import json
from urllib.parse import urljoin, urlparse
from typing import List, Set, Optional, Dict, Callable, Union
from dataclasses import dataclass, asdict
import subprocess
import sys
import threading
import queue
import time
import warnings

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from bs4 import XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

###########################
# Readability (opsiyonel)
###########################
try:
    from readability import Document
    USE_READABILITY = True
except ImportError:
    USE_READABILITY = False

from collections import defaultdict

domain_line_frequency = defaultdict(lambda: defaultdict(int))

OUTPUTS_DIR = "outputs"
os.makedirs(OUTPUTS_DIR, exist_ok=True)

@dataclass
class PageContent:
    url: str
    title: str
    content: str

class UniversalScraper(threading.Thread):
    def __init__(
        self, 
        base_url: str, 
        max_depth: Optional[int] = None, 
        data_queue: Optional[queue.Queue] = None,
        save_links: bool = True,       # <-- Eklenen bayrak
        save_articles: bool = True     # <-- Eklenen bayrak
    ):
        super().__init__()
        self.base_url = base_url
        self.allowed_domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.visited_urls: Set[str] = set()
        self.all_links: Set[str] = set()
        self.page_contents: List[PageContent] = []

        # Duplicate engelleme
        self.content_hashes: Set[str] = set()

        self.save_links_flag = save_links       # <--
        self.save_articles_flag = save_articles # <--

        sanitized = self._sanitize_url(base_url)
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

        # Chrome options
        def create_options():
            opts = Options()
            opts.add_argument('--headless')
            opts.add_argument('--no-sandbox')
            opts.add_argument('--disable-dev-shm-usage')
            opts.add_argument('--ignore-certificate-errors')
            return opts

        chrome_options = create_options()

        # Chrome sürüm
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

    def _sanitize_url(self, url: str) -> str:
        return re.sub(r'[^a-zA-Z0-9]', '_', url)

    def _get_chrome_version(self) -> Optional[int]:
        try:
            if sys.platform.startswith('win'):
                # Windows
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
                # Mac OS
                try:
                    process = subprocess.Popen(
                        ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    stdout, stderr = process.communicate()
                    version_match = re.search(r'\d+\.\d+\.\d+\.\d+', stdout.decode())
                    if version_match:
                        version_str = version_match.group()
                        return int(version_str.split('.')[0])
                except FileNotFoundError:
                    # fallback path'ler
                    self.logger.warning("[macOS] /Applications/Google Chrome.app/... not found, trying other paths...")
                    paths_to_try = [
                        "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
                        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                        "/usr/local/bin/google-chrome",
                        "/usr/bin/google-chrome"
                    ]
                    for p in paths_to_try:
                        if os.path.isfile(p):
                            self.logger.info(f"[macOS] Trying Chrome path: {p}")
                            proc = subprocess.Popen([p, '--version'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            out, err = proc.communicate()
                            ver_match = re.search(r'\d+\.\d+\.\d+\.\d+', out.decode())
                            if ver_match:
                                ver_str = ver_match.group()
                                return int(ver_str.split('.')[0])

            else:
                # Linux
                process = subprocess.Popen(
                    ['google-chrome', '--version'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate()
                version_match = re.search(r'\d+\.\d+\.\d+\.\d+', stdout.decode())
                if version_match:
                    version_str = version_match.group()
                    return int(version_str.split('.')[0])

        except Exception as e:
            self.logger.error(f"[{self.base_url}] Failed to detect Chrome version: {e}")
            return None
        return None

    ########################
    # Link Extraction
    ########################
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

    ########################
    # Title
    ########################
    def _find_title(self, html_text: str, soup: BeautifulSoup) -> Optional[str]:
        if USE_READABILITY:
            try:
                doc = Document(html_text)
                rd_title = doc.short_title()
                if rd_title and len(rd_title.strip()) > 5:
                    return rd_title.strip()
            except Exception as e:
                self.logger.warning(f"[{self.allowed_domain}] Readability title error: {e}")

        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            candidate = og_title["content"].strip()
            if len(candidate) > 5:
                return candidate

        tw_title = soup.find("meta", attrs={"name": "twitter:title"})
        if tw_title and tw_title.get("content"):
            candidate = tw_title["content"].strip()
            if len(candidate) > 5:
                return candidate

        if soup.title and soup.title.get_text(strip=True):
            candidate = soup.title.get_text(strip=True)
            if len(candidate) > 5:
                return candidate

        h1_tags = soup.find_all("h1")
        for h1 in h1_tags:
            txt = h1.get_text(strip=True)
            if len(txt) > 5:
                return txt
        return None

    ########################
    # Content 
    ########################
    def _find_content(self, html_text: str, domain: str) -> Optional[str]:
        # Basit: sadece fallback
        # (isteyenler yukarıda gösterilen paragraf/blog container approach'ları ekleyebilir)
        soup = BeautifulSoup(html_text, "lxml")

        for bad_tag in ["script","style","nav","header","footer","aside","form","code"]:
            for t in soup.find_all(bad_tag):
                t.decompose()

        text = soup.get_text(separator="\n")
        lines = text.splitlines()
        clean_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if len(line) < 20:
                continue
            lower_line = line.lower()
            if any(kw in lower_line for kw in ["cookie","policy","privacy","terms",
                                               "copyright","all rights reserved"]):
                continue
            if re.match(r'^\d{1,4}[-/\.]\d{1,2}[-/\.]\d{1,4}', line):
                continue
            if re.match(r'^[0-9\s\-]+$', line):
                continue

            domain_line_frequency[domain][line] += 1
            if domain_line_frequency[domain][line] > 3:
                continue

            clean_lines.append(line)
        final_text = " ".join(clean_lines)
        if len(final_text) < 50:
            return None
        return final_text

    ########################
    # Save (Opsiyonel)
    ########################
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

    ########################
    # DFS
    ########################
    def _dfs(self, url: str, current_depth: int, max_pages: Optional[int] = None):
        if url in self.visited_urls:
            return
        if self.max_depth is not None and current_depth > self.max_depth:
            return
        if max_pages is not None and self.pages_scraped >= max_pages:
            return

        self.visited_urls.add(url)
        self.logger.info(f"[{self.base_url}] Visiting (Depth={current_depth}): {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }

        try:
            session = requests.Session()
            retry = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[500,502,503,504],
                allowed_methods=["GET","POST"]
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            response = session.get(url, headers=headers, verify=True, timeout=10)
            if response.status_code == 403:
                self.logger.error(f"[{self.base_url}] 403 Forbidden for {url}")
                return
            if response.status_code == 404:
                self.logger.error(f"[{self.base_url}] 404 Not Found for {url}")
                return
            if response.status_code != 200:
                self.logger.error(f"[{self.base_url}] Failed to fetch {url}: {response.status_code}")
                return

        except requests.exceptions.SSLError as ssl_err:
            self.logger.error(f"[{self.base_url}] SSL Error for {url}: {ssl_err}")
            return
        except requests.exceptions.ConnectionError as conn_err:
            self.logger.error(f"[{self.base_url}] Connection Error for {url}: {conn_err}")
            return
        except requests.exceptions.Timeout as timeout_err:
            self.logger.error(f"[{self.base_url}] Timeout Error for {url}: {timeout_err}")
            return
        except Exception as e:
            self.logger.error(f"[{self.base_url}] Unexpected Error for {url}: {e}")
            return

        html_text = response.text
        soup = BeautifulSoup(html_text, 'lxml')

        # Linkleri çıkar
        links = self._extract_links(soup, url)
        unique_new_links = set(links) - self.all_links
        self.all_links.update(unique_new_links)

        # ANLIK haber verme (new_link)
        if self.data_queue:
            for lnk in unique_new_links:
                self.data_queue.put(('new_link', lnk))

        # Title + Content
        page_title = self._find_title(html_text, soup)
        page_content = self._find_content(html_text, self.allowed_domain)

        # Anlık article
        if page_title and page_content:
            combined_text = page_title.strip() + "\n" + page_content.strip()
            content_hash = hashlib.sha256(combined_text.encode("utf-8")).hexdigest()

            if content_hash not in self.content_hashes:
                self.content_hashes.add(content_hash)
                page = PageContent(url=url, title=page_title, content=page_content)
                self.page_contents.append(page)

                # Kuyruğa da atıyoruz (real-time izleme)
                if self.data_queue:
                    self.data_queue.put(('article', page))

        self.pages_scraped += 1

        # Opsiyonel kaydetmeler
        self._save_links()
        self._save_articles()

        if max_pages is not None and self.pages_scraped >= max_pages:
            return

        # Derinlikli devam
        for new_link in unique_new_links:
            self._dfs(new_link, current_depth + 1, max_pages)

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


######################################
# MultiUniversalScraper
######################################
class MultiUniversalScraper:
    def __init__(
        self,
        base_urls: List[str],
        max_depth: Optional[int] = None,
        on_new_article: Optional[Callable[[PageContent], None]] = None,
        save_pool_links: bool = True,     # <-- ek
        save_pool_articles: bool = True,  # <-- ek
    ):
        self.base_urls = base_urls
        self.max_depth = max_depth
        self.scrapers: Dict[str, UniversalScraper] = {}
        self.all_links: Set[str] = set()
        self.all_page_contents: List[PageContent] = []
        self.data_queue = queue.Queue()
        self.lock = threading.Lock()
        self.on_new_article = on_new_article

        self.save_pool_links = save_pool_links           # <-- ek
        self.save_pool_articles = save_pool_articles     # <-- ek

        self.pool_links_output_file = os.path.join(OUTPUTS_DIR, "all_collected_links.json")
        self.pool_articles_output_file = os.path.join(OUTPUTS_DIR, "all_collected_articles.json")

        self.stop_event = threading.Event()
        self.listener_thread = threading.Thread(target=self._listen_data)
        self.listener_thread.start()

        # Örnek: Tüm scrapers aynı parametrelerle kuruyoruz (isterseniz her URL için farklı da yapabilirsiniz)
        for url in base_urls:
            scraper = UniversalScraper(
                url,
                max_depth=max_depth,
                data_queue=self.data_queue,
                save_links=save_pool_links,      # <- link kaydı opsiyon
                save_articles=save_pool_articles # <- article kaydı opsiyon
            )
            self.scrapers[url] = scraper

    def _listen_data(self):
        """
        data_queue -> ('new_link', link) veya ('article', PageContent)
        """
        while not self.stop_event.is_set() or not self.data_queue.empty():
            try:
                data_type, data = self.data_queue.get(timeout=1)

                if data_type == 'new_link':
                    # Anlık linkleri de buradan izleyebilirsiniz
                    # if you want to do something:
                    with self.lock:
                        self.all_links.add(data)  # data -> link (str)

                elif data_type == 'article':
                    with self.lock:
                        self.all_page_contents.append(data)
                        self.all_links.add(data.url)

                    if self.on_new_article:
                        self.on_new_article(data)

            except queue.Empty:
                continue

    def scrape_all(self, max_pages: Optional[int] = None):
        threads = []
        for scraper in self.scrapers.values():
            scraper.start()
            threads.append(scraper)

        for thread in threads:
            thread.join()

        time.sleep(1)
        self.stop_event.set()
        self.listener_thread.join()

        # multi-level kaydetme (opsiyonel)
        self._save_pool_links()
        self._save_pool_articles()

    def _save_pool_links(self):
        # Eğer global link kaydı istenmezse atla
        if not self.save_pool_links:
            return
        with self.lock:
            all_links = list(self.all_links)
        with open(self.pool_links_output_file, 'w', encoding='utf-8') as f:
            json.dump(all_links, f, ensure_ascii=False, indent=2)
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


##############################
# Örnek kullanım / main
##############################
def on_new_article(article: PageContent):
    print(f"Yeni makale bulundu: {article.title} - {article.url}")

def main():
    base_urls = [
        "https://www.defense.gov",
        "https://www.msb.gov.tr",
        # ...
    ]

    # Örneğin link kaydını devre dışı, article kaydını aktif yapmak:
    multi_scraper = MultiUniversalScraper(
        base_urls,
        max_depth=2,
        on_new_article=on_new_article,
        save_pool_links=False,      # <-- link kaydı kapalı
        save_pool_articles=True     # <-- article kaydı açık
    )
    multi_scraper.scrape_all(max_pages=10)
    multi_scraper.close_all()

    print(f"Toplam link sayısı: {len(multi_scraper.all_links)}")
    print(f"Toplanan içerik sayısı: {len(multi_scraper.all_page_contents)}")

if __name__ == "__main__":
    main()
