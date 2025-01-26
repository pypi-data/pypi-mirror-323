# neuraparse/universal_scraper/scraper.py

import re
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import SessionNotCreatedException
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import logging
import json
from urllib.parse import urljoin, urlparse
from typing import List, Set, Optional, Dict, Callable
from dataclasses import dataclass, asdict
import subprocess
import sys
import threading
import queue
import time
import random
import warnings

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Suppress specific BeautifulSoup warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


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
        proxies: Optional[Dict[str, str]] = None,
    ):
        """
        :param base_url: Tarama başlangıç URL'i
        :param max_depth: Derinlik (None ise, link bitene kadar devam)
        :param data_queue: Scraped verilerin gönderileceği kuyruk
        :param proxies: Kullanılacak proxy sunucuları
        """
        super().__init__()
        self.base_url = base_url
        self.allowed_domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.visited_urls: Set[str] = set()
        self.all_links: Set[str] = set()
        self.page_contents: List[PageContent] = []

        self.links_output_file = f"collected_links_{self._sanitize_url(base_url)}.json"
        self.articles_output_file = f"collected_articles_{self._sanitize_url(base_url)}.json"

        self.pages_scraped = 0
        self.data_queue = data_queue
        self.proxies = proxies

        self.lock = threading.Lock()

        # Retry stratejisini ayarla
        self.session = self._get_session()

        # Tarayıcı seçeneklerini oluştur
        chrome_options = self._create_options()

        # Chrome sürümünü tespit et
        chrome_version = self._get_chrome_version()
        if chrome_version:
            logging.info(f"[{self.base_url}] Detected Chrome version: {chrome_version}")
        else:
            logging.warning(f"[{self.base_url}] Could not detect Chrome version. Assuming Chrome 108 or higher.")
            chrome_version = 108  # Varsayılan sürüm

        try:
            self.driver = uc.Chrome(options=chrome_options, version_main=chrome_version)
        except SessionNotCreatedException as e:
            msg = str(e)
            version_match = re.search(r'Current browser version is (\d+)', msg)
            if version_match:
                version = int(version_match.group(1))
                logging.info(f"[{self.base_url}] Uyumsuz sürüm tespit edildi. Kullanılan Chrome versiyonu: {version}.")
                new_options = self._create_options()
                self.driver = uc.Chrome(options=new_options, version_main=version)
            else:
                raise e

        # Logger yapılandırması
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('universal_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _sanitize_url(self, url: str) -> str:
        # URL'yi dosya ismi için uygun hale getir
        return re.sub(r'[^a-zA-Z0-9]', '_', url)

    def _get_chrome_version(self) -> Optional[int]:
        """
        Sisteminizde yüklü olan Chrome tarayıcı sürümünü tespit eder.
        :return: Chrome'un ana sürüm numarası (örn: 108) veya None
        """
        try:
            if sys.platform.startswith('win'):
                # Windows için Chrome sürümünü tespit et
                process = subprocess.Popen(
                    ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
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
                # Mac için Chrome sürümünü tespit et
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
            else:
                # Linux için Chrome sürümünü tespit et
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

    def _create_options(self) -> Options:
        """
        Selenium için Chrome seçeneklerini oluşturur.
        """
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--ignore-certificate-errors')
        opts.add_argument('--disable-blink-features=AutomationControlled')
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        # Rastgele bir kullanıcı ajanı seç
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Chrome/115.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)'
            ' Version/14.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Chrome/115.0.0.0 Safari/537.36',
            # Daha fazla kullanıcı ajanı ekleyebilirsiniz
        ]
        opts.add_argument(f'user-agent={random.choice(user_agents)}')
        return opts

    def _get_session(self) -> requests.Session:
        """
        Requests için bir oturum oluşturur ve retry mekanizmasını ekler.
        """
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _is_valid_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            return (
                bool(parsed.netloc) and
                parsed.netloc == self.allowed_domain and
                not any(ext in url.lower() for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.gif'])
            )
        except Exception:
            return False

    def _extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/'):
                href = urljoin(current_url, href)
            elif not href.startswith('http'):
                href = urljoin(current_url, href)
            if self._is_valid_url(href):
                links.append(href)
        return links

    def _find_title(self, soup: BeautifulSoup) -> Optional[str]:
        title_tag = soup.find('title')
        if title_tag and title_tag.get_text(strip=True):
            return title_tag.get_text(strip=True)

        possible_title_id = soup.find(id='title')
        if possible_title_id and possible_title_id.get_text(strip=True):
            return possible_title_id.get_text(strip=True)

        possible_title_class = soup.find(class_='title')
        if possible_title_class and possible_title_class.get_text(strip=True):
            return possible_title_class.get_text(strip=True)

        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.get_text(strip=True):
            return h1_tag.get_text(strip=True)

        return None

    def _find_content(self, soup: BeautifulSoup) -> Optional[str]:
        content_id = soup.find(id='content')
        if content_id and content_id.get_text(strip=True):
            return content_id.get_text(strip=True)

        content_class = soup.find(class_='content')
        if content_class and content_class.get_text(strip=True):
            return content_class.get_text(strip=True)

        p_tags = soup.find_all('p')
        paragraphs = [p.get_text(strip=True) for p in p_tags if p.get_text(strip=True)]
        combined_text = ' '.join(paragraphs)

        if len(combined_text) > 50:
            return combined_text

        return None

    def _save_links(self):
        with self.lock:
            with open(self.links_output_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.all_links), f, ensure_ascii=False, indent=2)
        self.logger.info(f"[{self.base_url}] Links saved to {self.links_output_file}")

    def _save_articles(self):
        with self.lock:
            data = [asdict(pc) for pc in self.page_contents]
            with open(self.articles_output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"[{self.base_url}] Articles saved to {self.articles_output_file}")

    def _fetch_content(self, url: str) -> Optional[BeautifulSoup]:
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        try:
            response = self.session.get(
                url,
                headers=headers,
                verify=True,  # Sertifika doğrulamasını etkinleştir
                timeout=10,
                proxies=self.proxies
            )
            if response.status_code == 403:
                self.logger.error(f"[{self.base_url}] 403 Forbidden for {url}")
                return None
            if response.status_code == 404:
                self.logger.error(f"[{self.base_url}] 404 Not Found for {url}")
                return None
            if response.status_code != 200:
                self.logger.error(f"[{self.base_url}] Failed to fetch {url}: {response.status_code}")
                return None
            return BeautifulSoup(response.text, 'lxml')  # veya 'xml'
        except requests.exceptions.SSLError as ssl_err:
            self.logger.error(f"[{self.base_url}] SSL Error for {url}: {ssl_err}")
            return None
        except requests.exceptions.ConnectionError as conn_err:
            self.logger.error(f"[{self.base_url}] Connection Error for {url}: {conn_err}")
            return None
        except requests.exceptions.Timeout as timeout_err:
            self.logger.error(f"[{self.base_url}] Timeout Error for {url}: {timeout_err}")
            return None
        except Exception as e:
            self.logger.error(f"[{self.base_url}] Unexpected Error for {url}: {e}")
            return None

    def _get_random_user_agent(self) -> str:
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Chrome/115.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)'
            ' Version/14.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Chrome/115.0.0.0 Safari/537.36',
            # Daha fazla kullanıcı ajanı ekleyebilirsiniz
        ]
        return random.choice(user_agents)

    def _dfs(self, url: str, current_depth: int, max_pages: Optional[int] = None):
        if url in self.visited_urls:
            return
        if self.max_depth is not None and current_depth > self.max_depth:
            return
        if max_pages is not None and self.pages_scraped >= max_pages:
            return

        self.visited_urls.add(url)
        self.logger.info(f"[{self.base_url}] Visiting (Depth={current_depth}): {url}")

        soup = self._fetch_content(url)
        if not soup:
            return

        links = self._extract_links(soup, url)
        unique_new_links = set(links) - self.all_links
        self.all_links.update(unique_new_links)

        page_title = self._find_title(soup)
        page_content = self._find_content(soup)

        if page_title and page_content:
            page = PageContent(url=url, title=page_title, content=page_content)
            self.page_contents.append(page)
            if self.data_queue:
                self.data_queue.put(('article', page))

        self.pages_scraped += 1
        self._save_links()
        self._save_articles()

        if max_pages is not None and self.pages_scraped >= max_pages:
            return

        for new_link in unique_new_links:
            # Aralıklı bekleme (rate limiting) ekleyin
            time.sleep(random.uniform(1, 3))
            self._dfs(new_link, current_depth + 1, max_pages)

    def scrape_links_dfs(self, max_pages: Optional[int] = None):
        self.logger.info(f"[{self.base_url}] Starting DFS")
        self._dfs(self.base_url, 0, max_pages=max_pages)
        self.logger.info(
            f"[{self.base_url}] DFS completed. Total unique links: {len(self.all_links)} | Pages with content: {len(self.page_contents)}"
        )

    def run(self):
        self.scrape_links_dfs()

    def close(self):
        self.driver.quit()


class MultiUniversalScraper:
    def __init__(
        self,
        base_urls: List[str],
        max_depth: Optional[int] = None,
        on_new_article: Optional[Callable[[PageContent], None]] = None,
        proxies: Optional[Dict[str, str]] = None,
    ):
        """
        :param base_urls: Tarama başlangıç URL'lerinin listesi
        :param max_depth: Derinlik (None ise, link bitene kadar devam)
        :param on_new_article: Yeni makale bulunduğunda çağrılacak callback fonksiyonu
        :param proxies: Kullanılacak proxy sunucuları
        """
        self.base_urls = base_urls
        self.max_depth = max_depth
        self.scrapers: Dict[str, UniversalScraper] = {}
        self.all_links: Set[str] = set()
        self.all_page_contents: List[PageContent] = []
        self.data_queue = queue.Queue()
        self.lock = threading.Lock()
        self.on_new_article = on_new_article
        self.proxies = proxies

        # Output files
        self.pool_links_output_file = "all_collected_links.json"
        self.pool_articles_output_file = "all_collected_articles.json"

        # Event to stop listening
        self.stop_event = threading.Event()

        # Listener thread
        self.listener_thread = threading.Thread(target=self._listen_data, daemon=True)
        self.listener_thread.start()

        # Initialize individual scrapers
        for url in base_urls:
            scraper = UniversalScraper(url, max_depth=max_depth, data_queue=self.data_queue, proxies=self.proxies)
            self.scrapers[url] = scraper

    def _listen_data(self):
        """
        Anlık dinleme işlemi için veri kuyruğunu dinler.
        """
        while not self.stop_event.is_set() or not self.data_queue.empty():
            try:
                data_type, data = self.data_queue.get(timeout=1)
                if data_type == 'article':
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

        # Bekletmek için küçük bir süre
        time.sleep(2)

        # Stop the listener thread
        self.stop_event.set()
        self.listener_thread.join()

        # Save pool outputs
        self._save_pool_links()
        self._save_pool_articles()

    def _save_pool_links(self):
        with self.lock:
            all_links = list(self.all_links)
        with open(self.pool_links_output_file, 'w', encoding='utf-8') as f:
            json.dump(all_links, f, ensure_ascii=False, indent=2)
        logging.info(f"All links saved to {self.pool_links_output_file}")

    def _save_pool_articles(self):
        with self.lock:
            data = [asdict(pc) for pc in self.all_page_contents]
        with open(self.pool_articles_output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"All articles saved to {self.pool_articles_output_file}")

    def close_all(self):
        for scraper in self.scrapers.values():
            scraper.close()




def main():
    """
    Paketinizin komut satırı giriş noktası.
    """
    import argparse

    # Komut satırı argümanlarını tanımlayın
    parser = argparse.ArgumentParser(description='Neuraparse Universal Web Scraper')
    parser.add_argument(
        '--urls',
        nargs='+',
        required=True,
        help='Başlangıç URL\'lerini boşluklarla ayrılmış şekilde belirtin.'
    )
    parser.add_argument(
        '--max-depth',
        type=int,
        default=2,
        help='Tarama derinliği (varsayılan: 2)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Her bir scraper için maksimum sayfa sayısı (varsayılan: 10)'
    )
    parser.add_argument(
        '--proxies',
        type=str,
        nargs='*',
        help='Kullanılacak proxy sunucuları (örn: http://proxy1, http://proxy2)'
    )

    args = parser.parse_args()

    # Proxy'leri sözlüğe dönüştürün
    proxies = None
    if args.proxies:
        proxies = {}
        for proxy in args.proxies:
            if proxy.startswith('http://') or proxy.startswith('https://'):
                proxies['http'] = proxy
                proxies['https'] = proxy

    def on_new_article(article: PageContent):
        print(f"Yeni makale bulundu: {article.title} - {article.url}")

    multi_scraper = MultiUniversalScraper(
        base_urls=args.urls,
        max_depth=args.max_depth,
        on_new_article=on_new_article,
        proxies=proxies
    )
    multi_scraper.scrape_all(max_pages=args.max_pages)
    multi_scraper.close_all()

    # Tüm linklere ve içeriklere erişim
    print(f"Toplam link sayısı: {len(multi_scraper.all_links)}")
    print(f"Toplanan içerik sayısı: {len(multi_scraper.all_page_contents)}")
