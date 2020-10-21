# -*- coding: utf-8 -*-

from scrapy import Request, Spider
from scrapy.http.response import Response

BASE_PIECE_XPATH = '/html/body/div[3]/div[3]/div[5]/div[1]/div/div[2]/ul/li/table[1]/tbody/tr[{0}]/td[{1}]/a/@href'


class ChessSpider(Spider):
    name = 'chess'
    start_urls = ['https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces']
    custom_settings = {
        'ITEM_PIPELINES': {
            'crawler.pipelines.ChessPipeline': 1
        }
    }

    def parse(self, response: Response):
        for i in range(3, 9):
            for j in range(1, 3):
                piece_url = response.xpath(BASE_PIECE_XPATH.format(i, j)).get()
                yield Request(
                    url=response.urljoin(piece_url),
                    callback=self.parse_chess_piece
                )

    def parse_chess_piece(self, response: Response):
        yield {
            'file_urls': response.xpath('/html/body/div[3]/div[3]/div[5]/div[2]/p[1]/a/@href').get()
        }
