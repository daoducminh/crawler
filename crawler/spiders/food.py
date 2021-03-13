# -*- coding: utf-8 -*-

from scrapy import Request, Spider
from scrapy.http.response import Response
from scrapy_splash import SplashRequest, SplashResponse


class FoodSpider(Spider):
    name = 'food'
    allowed_domains = ['food.com']
    custom_settings = {
        'SPIDER_MIDDLEWARES': {
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        },
        'SPLASH_URL': 'http://127.0.0.1:8050',
        'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter'
    }

    def start_requests(self):
        yield SplashRequest(
            url='https://www.food.com/recipe',
            callback=self.parse_list,
            args={
                'wait': 0.5
            }
        )

    def parse_list(self, response):
        selectors = response.xpath(
            "//a[contains(@href,'food.com/recipe')]/@href"
        )
        a = [i.get() for i in selectors]
        links = list(filter(lambda x: '#' not in x, a))
        print(links)

    def parse_food(self, response):
        pass
