# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import re
from itemloaders.processors import Join, MapCompose
from scrapy import Item, Field
from w3lib.html import remove_tags


class Recipe(Item):
    ingredients = Field(
        input_processor=MapCompose(remove_tags, str.strip)
    )
    directions = Field(
        input_processor=MapCompose(remove_tags, str.strip)
    )


def get_username(x):
    return x[1:]


class User(Item):
    full_name = Field(
        input_processor=MapCompose(remove_tags, str.strip),
        output_processor=Join()
    )
    username = Field(
        input_processor=MapCompose(remove_tags, get_username, str.strip),
        output_processor=Join()
    )
    follower = Field(
        input_processor=MapCompose(remove_tags, str.strip),
        output_processor=Join()
    )
    following = Field(
        input_processor=MapCompose(remove_tags, str.strip),
        output_processor=Join()
    )
