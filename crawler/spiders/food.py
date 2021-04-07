# -*- coding: utf-8 -*-

from scrapy import Request, Spider
from scrapy.http.response import Response
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest, SplashResponse

from crawler.items import Recipe, User
from .food_const import *

PAGES = 2000
RECIPE_URL = 'https://www.food.com/recipe/all/popular?pn={}'
MOST_TWEAK_URL = 'https://www.food.com/ideas/most-tweaked-recipes-6655'
FOLLOW_URL = 'https://api.food.com/external/v1/members/{0}/feed/{1}?pn={2}&size=1'
REVIEW_URL = 'https://api.food.com/external/v1/recipes/{0}/feed/?pn={1}&size=1'
USER_URL = 'https://www.food.com/user/{}'
OWN_RECIPE_URL = 'https://api.food.com/external/v1/members/{0}/feed/recipes?pn={1}&size=1'
POPULAR_URL = 'https://api.food.com/services/mobile/fdc/search/sectionfront?pn={}&recordType=Recipe&sortBy=mostPopular&collectionId=17'

# wait_recipe = """
# function main(splash)
#   assert(splash:go(splash.args.url))

#   -- requires Splash 2.3
#   while not splash:select('.fd-inner-tile') do
#     splash:wait(0.1)
#   end
#   return {html=splash:html()}
# end
# """


def handle_follow(x):
    return int(x['memberId']), int(x['followedId'])


def handle_review(x):
    return {
        REVIEW_ID: int(x['id']),
        RECIPE_ID: int(x['recipeId']),
        USER_ID: int(x['memberId']),
        RATING: int(x['rating']),
        COMMENT: x['text']
    }


class FoodSpider(Spider):
    name = 'food'
    allowed_domains = ['food.com']
    custom_settings = {
        # 'SPIDER_MIDDLEWARES': {
        #     'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
        # },
        # 'DOWNLOADER_MIDDLEWARES': {
        #     'scrapy_splash.SplashCookiesMiddleware': 723,
        #     'scrapy_splash.SplashMiddleware': 725,
        #     'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        # },
        # 'SPLASH_URL': 'http://127.0.0.1:8050',
        # 'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
        # 'ITEM_PIPELINES': {
        #     'crawler.pipelines.FoodPicklePipeline': 100
        # },
        'RETRY_TIMES': 20
    }

    def __init__(self, number=PAGES, *args, **kwargs):
        super(FoodSpider, self).__init__(*args, **kwargs)
        self.number = number

    def start_requests(self):
        try:
            n = int(self.number)
            for i in range(1, 1+n):
                yield Request(
                    url=POPULAR_URL.format(i),
                    callback=self.parse_search_recipes,
                    headers={
                        'Accept': 'application/json'
                    }
                )
        except Exception as e:
            print(e)

    def parse_search_recipes(self, response):
        body = response.json()
        items = body['response']['results']
        if items:
            for i in items:
                data = {
                    DESCRIPTION: i.get(DESCRIPTION, ''),
                    IMAGE_URL: i.get('recipe_photo_url', ''),
                    REVIEW_COUNT: i.get('main_num_ratings', 0),
                    CATEGORY: i.get('primary_category_name'),
                    FACTS_TIME: i.get('recipe_totaltime', 0),
                    RECIPE_ID: i[RECIPE_ID],
                    AUTHOR_ID: i['main_userid'],
                    AUTHOR_URL: i['recipe_user_url'],
                    FULL_NAME: i['main_title'],
                    USER_AVATAR_URL: i.get(USER_AVATAR_URL)
                }
                yield Request(
                    url=i['record_url'],
                    callback=self.parse_recipe,
                    cb_kwargs=dict(
                        data=data,
                        get_author=True
                    )
                )

    # def parse(self, response):
    #     selectors = response.xpath(
    #         "//a[contains(@href,'/recipe/')]/@href"
    #     )
    #     links = [i.get() for i in selectors]
    #     for i in links:
    #         # yield SplashRequest(
    #         #     url=i,
    #         #     callback=self.parse_recipe
    #         # )
    #         yield Request(
    #             url=i,
    #             callback=self.parse_recipe,
    #             cb_kwargs=dict(get_author=True)
    #         )

    def parse_recipe(self, response, data, get_author=False):
        item = ItemLoader(item=Recipe(), response=response)
        item.add_css(INGREDIENTS, '.recipe-ingredients__ingredient')
        item.add_css(DIRECTIONS, 'li.recipe-directions__step')
        recipe = dict(item.load_item())
        try:
            recipe_id = int(data[RECIPE_ID])
            author_id = int(data[AUTHOR_ID])
            review_count = int(data[REVIEW_COUNT])
            facts_time = int(data[FACTS_TIME])
            # Append additional information
            recipe = {**recipe, **data}
            recipe[RECIPE_ID] = recipe_id
            recipe[AUTHOR_ID] = author_id
            recipe[REVIEW_COUNT] = review_count
            recipe[FACTS_TIME] = facts_time
            recipe[TYPE] = RECIPE
            del recipe[USER_AVATAR_URL]
            del recipe[AUTHOR_URL]

            yield recipe
            if get_author:
                yield Request(
                    url=data[AUTHOR_URL],
                    callback=self.parse_user,
                    cb_kwargs=dict(
                        user_avatar_url=data.get(USER_AVATAR_URL)
                    )
                )
            if review_count:
                for i in range(1, 1+review_count):
                    yield Request(
                        url=REVIEW_URL.format(recipe_id, i),
                        callback=self.parse_review
                    )
        except Exception as e:
            yield {
                TYPE: ERROR,
                URL: response.url,
                ERROR: str(e)
            }

    def parse_user(self, response, user_avatar_url=''):
        item = ItemLoader(item=User(), response=response)
        item.add_css(FULL_NAME, '.name-bio-message h3')
        item.add_css(USERNAME, '.profileusername')
        item.add_css(FOLLOWER, '.user-followers span')
        item.add_css(FOLLOWING, '.user-following span')

        user = dict(item.load_item())
        try:
            user[USER_ID] = int(response.url.split('/')[-1])
            user[FOLLOWER] = int(user[FOLLOWER])
            user[FOLLOWING] = int(user[FOLLOWING])
            user[TYPE] = USER
            user[USER_AVATAR_URL] = user_avatar_url
            yield user
            # yield Request(
            #     url=OWN_RECIPE_URL.format(user[USER_ID], 1),
            #     callback=self.parse_first_own_recipe
            # )
            # Followers
            if user[FOLLOWER]:
                for i in range(1, 1+user[FOLLOWER]):
                    yield Request(
                        url=FOLLOW_URL.format(user[USER_ID], 'followers', i),
                        callback=self.parse_follow,
                        cb_kwargs=dict(
                            user=user,
                            f_type=FOLLOWER
                        )
                    )
            # Followings
            if user[FOLLOWING]:
                for i in range(1, 1+user[FOLLOWING]):
                    yield Request(
                        url=FOLLOW_URL.format(user[USER_ID], 'follows', i),
                        callback=self.parse_follow,
                        cb_kwargs=dict(
                            user=user,
                            f_type=FOLLOWING
                        )
                    )
        except Exception as e:
            yield {
                TYPE: ERROR,
                URL: response.url,
                ERROR: str(e)
            }

    def parse_first_own_recipe(self, response):
        body = response.json()
        item = body['data']['items']
        if item:
            recipe = item[0]
            yield Request(
                url=recipe['recipeUrl'],
                callback=self.parse_recipe
            )
            if body['total'] > 1:
                for i in range(2, 1+body['total']):
                    yield Request(
                        url=OWN_RECIPE_URL.format(recipe['memberId'], i),
                        callback=self.parse_own_recipe
                    )

    def parse_own_recipe(self, response):
        body = response.json()
        items = body['data']['items']
        if items:
            for i in items:
                yield Request(
                    url=i['recipeUrl'],
                    callback=self.parse_recipe
                )

    def parse_follow(self, response, user, f_type):
        body = response.json()
        item = body['data']['items'][0]
        if item:
            yield {
                TYPE: f_type,
                FOLLOW: handle_follow(item)
            }

    def parse_review(self, response):
        body = response.json()
        item = body['data']['items'][0]
        if item:
            if item[TYPE] == REVIEW:
                review = handle_review(item)
                review[TYPE] = REVIEW
                yield review
                yield Request(
                    url=USER_URL.format(review[USER_ID]),
                    callback=self.parse_user
                )

    # def parse_own_recipe(self, response):
    #     pass

    # def parse_review(self, response):
    #     pass

    # def start_requests(self):
    #     for i in range(1, 1+PAGES):
    #         yield Request(
    #             url=RECIPE_URL.format(i),
    #             callback=self.parse_recipe_list
    #         )

    # def parse_all_list(self, response):
    #     selectors = response.xpath(
    #         "//a[contains(@href,'food.com/recipe')]/@href"
    #     )
    #     a = [i.get() for i in selectors]
    #     links = list(filter(lambda x: '#' not in x, a))
    #     all_links = list(filter(lambda x: '/all/' in x, links))
    #     all_links.append(RECIPE_URL)
    #     all_links = list(map(lambda x: x+'?pn={}', all_links))

    #     for link in all_links:
    #         for i in range(1, 2):
    #             yield SplashRequest(
    #                 url=link.format(i),
    #                 callback=self.parse_recipe_list,
    #                 endpoint='execute',
    #                 args={
    #                     'lua_source': wait_recipe
    #                 }
    #             )

    # def parse_recipe_list(self, response):
    #     selectors = response.xpath(
    #         "//div[contains(@class,'fdStream')]//a[contains(@href,'/recipe/')]/@href"
    #     )
    #     links = [i.get() for i in selectors]
    #     links = list(set(links))

    #     for i in links:
    #         yield Request(
    #             url=i,
    #             callback=self.parse_recipe
    #         )

    # def parse_recipe_list(self, response):
    #     selectors = response.xpath(
    #         "//a[contains(@href,'/recipe/')]/@href"
    #     )
    #     links = [i.get() for i in selectors]
    #     for i in links:
    #         yield SplashRequest(
    #             url=i,
    #             callback=self.parse_recipe
    #         )
