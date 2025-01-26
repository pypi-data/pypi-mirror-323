# neuraparse/universal_scraper/scraper.py

import re
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import SessionNotCreatedException
import requests
from bs4 import BeautifulSoup
import logging
import json
from urllib.parse import urljoin, urlparse
from typing import List, Set, Optional, Dict
from dataclasses import dataclass, asdict

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class PageContent:
    url: str
    title: str
    content: str


class UniversalScraper:
    def __init__(self, base_url: str, max_depth: Optional[int] = None):
        """
        :param base_url: Tarama başlangıç URL'i
        :param max_depth: Derinlik (None ise, link bitene kadar devam)
        """
        self.base_url = base_url
        self.allowed_domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.visited_urls: Set[str] = set()
        self.all_links: Set[str] = set()
        self.page_contents: List[PageContent] = []

        self.links_output_file = f"collected_links_{self._sanitize_url(base_url)}.json"
        self.articles_output_file = f"collected_articles_{self._sanitize_url(base_url)}.json"

        self.pages_scraped = 0

        def create_options():
            opts = Options()
            opts.add_argument('--headless')
            opts.add_argument('--no-sandbox')
            opts.add_argument('--disable-dev-shm-usage')
            opts.add_argument('--ignore-certificate-errors')
            return opts

        chrome_options = create_options()

        try:
            self.driver = uc.Chrome(options=chrome_options)
        except SessionNotCreatedException as e:
            msg = str(e)
            version_match = re.search(r'Current browser version is (\d+)', msg)
            if version_match:
                version = int(version_match.group(1))
                logging.info(f"Uyumsuz sürüm tespit edildi. Kullanılan Chrome versiyonu: {version}.")
                new_options = create_options()
                self.driver = uc.Chrome(options=new_options, version_main=version)
            else:
                raise e

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
        with open(self.links_output_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.all_links), f, ensure_ascii=False, indent=2)
        self.logger.info(f"Links saved to {self.links_output_file}")

    def _save_articles(self):
        data = [asdict(pc) for pc in self.page_contents]
        with open(self.articles_output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Articles saved to {self.articles_output_file}")

    def _dfs(self, url: str, current_depth: int, max_pages: Optional[int] = None):
        if url in self.visited_urls:
            return
        if self.max_depth is not None and current_depth > self.max_depth:
            return
        if max_pages is not None and self.pages_scraped >= max_pages:
            return

        self.visited_urls.add(url)
        self.logger.info(f"Visiting (Depth={current_depth}): {url}")

        try:
            response = requests.get(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                verify=False,
                timeout=10
            )
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch {url}: {response.status_code}")
                return
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return

        soup = BeautifulSoup(response.text, 'lxml')

        links = self._extract_links(soup, url)
        unique_new_links = set(links) - self.all_links
        self.all_links.update(unique_new_links)

        page_title = self._find_title(soup)
        page_content = self._find_content(soup)

        if page_title and page_content:
            self.page_contents.append(
                PageContent(url=url, title=page_title, content=page_content)
            )

        self.pages_scraped += 1
        self._save_links()
        self._save_articles()

        if max_pages is not None and self.pages_scraped >= max_pages:
            return

        for new_link in unique_new_links:
            self._dfs(new_link, current_depth + 1, max_pages)

    def scrape_links_dfs(self, max_pages: Optional[int] = None):
        self.logger.info(f"Starting DFS from {self.base_url}")
        self._dfs(self.base_url, 0, max_pages=max_pages)
        self.logger.info(
            f"DFS completed. Total unique links: {len(self.all_links)} | Pages with content: {len(self.page_contents)}"
        )

    def close(self):
        self.driver.quit()


class MultiUniversalScraper:
    def __init__(self, base_urls: List[str], max_depth: Optional[int] = None):
        """
        :param base_urls: Tarama başlangıç URL'lerinin listesi
        :param max_depth: Derinlik (None ise, link bitene kadar devam)
        """
        self.base_urls = base_urls
        self.max_depth = max_depth
        self.scrapers: Dict[str, UniversalScraper] = {}
        self.all_links: Set[str] = set()
        self.all_page_contents: List[PageContent] = []

        # Initialize individual scrapers
        for url in base_urls:
            scraper = UniversalScraper(url, max_depth=max_depth)
            self.scrapers[url] = scraper

        # Output files
        self.pool_links_output_file = "all_collected_links.json"
        self.pool_articles_output_file = "all_collected_articles.json"

    def scrape_all(self, max_pages: Optional[int] = None):
        for url, scraper in self.scrapers.items():
            scraper.scrape_links_dfs(max_pages=max_pages)
            # Aggregate links and contents
            self.all_links.update(scraper.all_links)
            self.all_page_contents.extend(scraper.page_contents)

        # Save pool outputs
        self._save_pool_links()
        self._save_pool_articles()

    def _save_pool_links(self):
        with open(self.pool_links_output_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.all_links), f, ensure_ascii=False, indent=2)
        logging.info(f"All links saved to {self.pool_links_output_file}")

    def _save_pool_articles(self):
        with open(self.pool_articles_output_file, 'w', encoding='utf-8') as f:
            data = [asdict(pc) for pc in self.all_page_contents]
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"All articles saved to {self.pool_articles_output_file}")

    def close_all(self):
        for scraper in self.scrapers.values():
            scraper.close()


def main():
    # Örnek bir ana fonksiyon
    base_urls = [
        "https://www.defense.gov",  # ABD Savunma Bakanlığı
        "https://www.msb.gov.tr",  # Türkiye Milli Savunma Bakanlığı
        "https://www.gov.uk/government/organisations/ministry-of-defence",  # Birleşik Krallık Savunma Bakanlığı
        "https://eng.mil.ru",  # Rusya Savunma Bakanlığı
        "https://www.defenseone.com",  # ABD savunma haber platformu
        "https://www.defence.gov.au",  # Avustralya Savunma Bakanlığı
        "https://www.mod.go.jp",  # Japonya Savunma Bakanlığı
        "https://www.mod.gov.in",  # Hindistan Savunma Bakanlığı
        "https://www.bundeswehr.de",  # Almanya Silahlı Kuvvetleri
        "https://www.canada.ca/en/department-national-defence.html",  # Kanada Savunma Bakanlığı
        "https://www.pla.gov.cn",  # Çin Halk Kurtuluş Ordusu
    ]

    multi_scraper = MultiUniversalScraper(base_urls, max_depth=2)
    multi_scraper.scrape_all(max_pages=10)
    multi_scraper.close_all()

    # Tüm linklere ve içeriklere erişim
    print(f"Toplam link sayısı: {len(multi_scraper.all_links)}")
    print(f"Toplanan içerik sayısı: {len(multi_scraper.all_page_contents)}")
