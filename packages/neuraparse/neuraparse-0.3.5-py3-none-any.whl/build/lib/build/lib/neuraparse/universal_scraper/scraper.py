# neuraparse/universal_scraper/scraper.py

import re
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
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
import os

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
        output_dir: str = "outputs",
    ):
        """
        :param base_url: Tarama başlangıç URL'i
        :param max_depth: Derinlik (None ise, link bitene kadar devam)
        :param data_queue: Scraped verilerin gönderileceği kuyruk
        :param proxies: Kullanılacak proxy sunucuları
        :param output_dir: Çıktıların kaydedileceği dizin
        """
        # Logger yapılandırmasını en başa taşıyın
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('universal_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        super().__init__()
        self.base_url = base_url
        self.allowed_domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.visited_urls: Set[str] = set()
        self.all_links: Set[str] = set()
        self.page_contents: List[PageContent] = []

        # Çıktı dizinini oluşturun
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Her bir scraper için alt klasör oluşturun
        self.site_output_dir = os.path.join(self.output_dir, self._sanitize_url(base_url))
        os.makedirs(self.site_output_dir, exist_ok=True)

        self.links_output_file = os.path.join(self.site_output_dir, "collected_links.json")
        self.articles_output_file = os.path.join(self.site_output_dir, "collected_articles.json")

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
            self.logger.info(f"[{self.base_url}] Detected Chrome version: {chrome_version}")
        else:
            self.logger.warning(f"[{self.base_url}] Could not detect Chrome version. Assuming Chrome 108 or higher.")
            chrome_version = 108  # Varsayılan sürüm

        try:
            self.driver = uc.Chrome(options=chrome_options, version_main=chrome_version)
        except SessionNotCreatedException as e:
            msg = str(e)
            version_match = re.search(r'Current browser version is (\d+)', msg)
            if version_match:
                version = int(version_match.group(1))
                self.logger.info(f"[{self.base_url}] Uyumsuz sürüm tespit edildi. Kullanılan Chrome versiyonu: {version}.")
                new_options = self._create_options()
                try:
                    self.driver = uc.Chrome(options=new_options, version_main=version)
                except Exception as inner_e:
                    self.logger.error(f"[{self.base_url}] Failed to initialize Chrome driver: {inner_e}")
                    raise inner_e
            else:
                self.logger.error(f"[{self.base_url}] Failed to initialize Chrome driver: {e}")
                raise e
        except WebDriverException as e:
            self.logger.error(f"[{self.base_url}] WebDriver exception: {e}")
            raise e

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
        opts.add_argument('--headless')  # İsteğe bağlı: Tarayıcıyı görünmez modda çalıştırmak için
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--ignore-certificate-errors')
        opts.add_argument('--disable-blink-features=AutomationControlled')
        
        # Aşağıdaki satırları kaldırdık
        # opts.add_experimental_option("excludeSwitches", ["enable-automation"])  # Kaldırıldı
        # opts.add_experimental_option('useAutomationExtension', False)  # Kaldırıldı

        # Rastgele bir kullanıcı ajanı seç
        user_agents = [
            # Chrome User Agents
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            # Firefox User Agents
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:109.0) Gecko/20100101 Firefox/109.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0',
            # Diğer tarayıcılar
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0',
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
        # Daha esnek bir başlık bulma yöntemi
        title_tag = soup.find('title')
        if title_tag and title_tag.get_text(strip=True):
            return title_tag.get_text(strip=True)

        # Farklı başlık etiketlerini kontrol et
        for header_tag in ['h1', 'h2', 'h3']:
            header = soup.find(header_tag)
            if header and header.get_text(strip=True):
                return header.get_text(strip=True)

        return None

    def _find_content(self, soup: BeautifulSoup) -> Optional[str]:
        # Belirli içerik alanlarını kontrol etmek yerine tüm paragraf etiketlerini topla
        p_tags = soup.find_all('p')
        paragraphs = [p.get_text(separator=' ', strip=True) for p in p_tags if p.get_text(strip=True)]
        combined_text = '\n\n'.join(paragraphs)  # Paragraflar arasında çift satır boşluk bırak

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
            self.driver.get(url)
            # Sayfanın belirli bir elementini yüklenene kadar bekleyin
            # Bu örnekte, sayfanın tamamen yüklendiğini varsayıyoruz
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            page_source = self.driver.page_source
            return BeautifulSoup(page_source, 'lxml')  # veya 'html.parser'
        except Exception as e:
            self.logger.error(f"[{self.base_url}] Error loading page {url}: {e}")
            return None

    def _get_random_user_agent(self) -> str:
        user_agents = [
            # Chrome User Agents
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            # Firefox User Agents
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:109.0) Gecko/20100101 Firefox/109.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0',
            # Diğer tarayıcılar
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0',
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
        try:
            self.driver.quit()
        except Exception as e:
            self.logger.error(f"[{self.base_url}] Error quitting driver: {e}")


class MultiUniversalScraper:
    def __init__(
        self,
        base_urls: List[str],
        max_depth: Optional[int] = None,
        on_new_article: Optional[Callable[[PageContent], None]] = None,
        proxies: Optional[Dict[str, str]] = None,
        output_dir: str = "outputs",
    ):
        """
        :param base_urls: Tarama başlangıç URL'lerinin listesi
        :param max_depth: Derinlik (None ise, link bitene kadar devam)
        :param on_new_article: Yeni makale bulunduğunda çağrılacak callback fonksiyonu
        :param proxies: Kullanılacak proxy sunucuları
        :param output_dir: Çıktıların kaydedileceği dizin
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
        self.output_dir = output_dir

        # Output dizinini oluşturun
        os.makedirs(self.output_dir, exist_ok=True)

        # Pool outputs dosyalarını oluşturun
        self.pool_links_output_file = os.path.join(self.output_dir, "all_collected_links.json")
        self.pool_articles_output_file = os.path.join(self.output_dir, "all_collected_articles.json")

        # Event to stop listening
        self.stop_event = threading.Event()

        # Listener thread
        self.listener_thread = threading.Thread(target=self._listen_data, daemon=True)
        self.listener_thread.start()

        # Initialize individual scrapers
        for url in base_urls:
            scraper = UniversalScraper(
                url,
                max_depth=max_depth,
                data_queue=self.data_queue,
                proxies=self.proxies,
                output_dir=self.output_dir
            )
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
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

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
    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs',
        help='Çıktıların kaydedileceği dizin (varsayılan: outputs)'
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
        proxies=proxies,
        output_dir=args.output_dir
    )
    multi_scraper.scrape_all(max_pages=args.max_pages)
    multi_scraper.close_all()

    # Tüm linklere ve içeriklere erişim
    print(f"Toplam link sayısı: {len(multi_scraper.all_links)}")
    print(f"Toplanan içerik sayısı: {len(multi_scraper.all_page_contents)}")


if __name__ == "__main__":
    main()
