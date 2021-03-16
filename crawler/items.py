# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from itemloaders.processors import Join, MapCompose
from scrapy import Item, Field
from w3lib.html import remove_tags


def get_review_count(x):
    return x[1:-1]


class Recipe(Item):
    full_name = Field(
        input_processor=MapCompose(remove_tags, str.strip),
        output_processor=Join()
    )
    # ingredients = Field(
    #     input_processor=MapCompose(remove_tags),
    #     output_processor=Join()
    # )
    directions = Field(
        input_processor=MapCompose(remove_tags, str.strip)
    )
    facts_time = Field(
        input_processor=MapCompose(remove_tags, str.strip),
        output_processor=Join()
    )
    review_count = Field(
        input_processor=MapCompose(remove_tags, str.strip, get_review_count),
        output_processor=Join()
    )
    # facts_serves = Field(
    #     input_processor=MapCompose(remove_tags),
    #     output_processor=Join()
    # )
    # description = Field(
    #     input_processor=MapCompose(remove_tags),
    #     output_processor=Join()
    # )


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
        input_processor=MapCompose(remove_tags),
        output_processor=Join()
    )
    following = Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join()
    )
