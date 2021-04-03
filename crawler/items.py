# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import jsbeautifier
import re
from itemloaders.processors import Join, MapCompose
from scrapy import Item, Field
from w3lib.html import remove_tags


def get_review_count(x):
    return x[1:-1]


def decode_escape_unicode(x):
    a = bytes(x, 'utf-8')
    return a.decode('unicode_escape')


def get_photo_url(x):
    return re.search(r'photoUrl: "https://img.sndimg.com/food/image/upload/.+"', x)


def extract_js(x):
    opts = jsbeautifier.default_options()
    opts.indent_size = 0
    opts.space_in_empty_paren = False
    a = jsbeautifier.beautify(x, opts=opts)
    b = a.split('\n')
    return list(filter(get_photo_url, b))


class Recipe(Item):
    ingredients = Field(
        input_processor=MapCompose(remove_tags)
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
        input_processor=MapCompose(remove_tags),
        output_processor=Join()
    )
    following = Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join()
    )
