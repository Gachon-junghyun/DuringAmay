import scrapy, json, datetime as dt

class NewsSpider(scrapy.Spider):
    name = "news"
    start_urls = [
        "https://techcrunch.com", "https://arstechnica.com"   # swap for your domains
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "ROBOTSTXT_OBEY": True,
        "FEEDS": {"pages.jsonl": {"format": "jsonlines"}},
    }

    def parse(self, response):
        title = response.css('title::text').get()
        text  = ' '.join(response.css('p::text').getall())
        yield {
            "url":   response.url,
            "title": title,
            "text":  text,
            "ts":    dt.datetime.utcnow().isoformat()
        }
        # follow internal links (1 depth)
        for href in response.css('a::attr(href)').getall():
            if href.startswith("http"):          # naive filter
                yield response.follow(href, self.parse, dont_filter=True)