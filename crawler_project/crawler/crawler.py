import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

class WebCrawler:
    def __init__(self, domains, patterns=["/product/", "/item/", "/p/"], max_depth=3):
        self.domains = domains
        self.patterns = patterns
        self.max_depth = max_depth
        self.visited = {domain: set() for domain in domains}
        self.results = {domain: [] for domain in domains}
    
    async def fetch(self, session, url):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
        return None

    def is_product_url(self, url):
        return any(pattern in url for pattern in self.patterns)

    def get_domain(self, url):
        return urlparse(url).netloc

    def get_links(self, base_url, html):
        soup = BeautifulSoup(html, 'lxml')
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = urljoin(base_url, a_tag['href'])
            if self.get_domain(href) == self.get_domain(base_url):
                links.add(href)
        return links

    async def crawl(self, domain, session, url, depth):
        if depth > self.max_depth or url in self.visited[domain]:
            return

        self.visited[domain].add(url)
        html = await self.fetch(session, url)
        if not html:
            return

        links = self.get_links(url, html)
        for link in links:
            if self.is_product_url(link):
                self.results[domain].append(link)
            await self.crawl(domain, session, link, depth + 1)

    async def start(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for domain in self.domains:
                tasks.append(self.crawl(domain, session, f"http://{domain}", 0))
            await asyncio.gather(*tasks)

    def save_results(self, filepath):
        for domain in self.results:
            self.results[domain] = list(set(self.results[domain]))  # Deduplicate URLs
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=4)

if __name__ == "__main__":
    domains = ["example1.com", "example2.com", "example3.com"]
    crawler = WebCrawler(domains)
    asyncio.run(crawler.start())
    crawler.save_results("crawler/output/product_urls.json")
