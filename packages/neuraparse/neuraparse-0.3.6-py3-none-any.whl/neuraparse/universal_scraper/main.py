# main.py

from .models import PageContent
from .multi_scraper import MultiUniversalScraper

def on_new_article(article: PageContent):
    print(f"Yeni makale bulundu: {article.title} - {article.url}")

def main():
    base_urls = [
        "https://www.defense.gov",
        "https://www.msb.gov.tr",
        # ...
    ]
    multi = MultiUniversalScraper(
        base_urls,
        max_depth=2,
        on_new_article=on_new_article,
        save_pool_links=False,
        save_pool_articles=True
    )
    multi.scrape_all(max_pages=10)
    multi.close_all()

    print(f"Toplam link sayısı: {len(multi.all_links)}")
    print(f"Toplanan içerik sayısı: {len(multi.all_page_contents)}")

if __name__ == "__main__":
    main()
