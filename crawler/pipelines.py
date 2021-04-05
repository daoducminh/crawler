# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import json
from itemadapter import ItemAdapter
from pathlib import Path
import pickle
import datetime
import shutil

from crawler.constants.food import *

FOOD_DATA = 'food/'
FOOD_DATA_FILE = FOOD_DATA+'{}.pkl'
DEST_FOLDER = '/content/drive/MyDrive/Projects/it5230/'
DEST = Path(DEST_FOLDER)


class ChessPipeline:
    def open_spider(self, spider):
        self.file = open('links.out', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        self.file.write(f"{item['file_urls']}\n")
        return item


class FoodPipeline:
    def open_spider(self, spider):
        Path(FOOD_DATA).mkdir(parents=True, exist_ok=True)
        self.recipe = open(FOOD_DATA+'recipe.jsonl', 'w')
        self.user = open(FOOD_DATA+'user.dat', 'w')
        self.review = open(FOOD_DATA+'review.dat', 'w')
        self.follow = open(FOOD_DATA+'follow.dat', 'w')

    def close_spider(self, spider):
        self.recipe.close()
        self.user.close()
        self.review.close()
        self.follow.close()

    def process_item(self, item, spider):
        if item[TYPE] == RECIPE:
            line = json.dumps(ItemAdapter(item).asdict()) + '\n'
            self.recipe.write(line)
        if item[TYPE] == USER:
            line = f'{item[USER_ID]},{item[USERNAME]},{item[FULL_NAME]}\n'
            self.user.write(line)
        if item[TYPE] == REVIEW:
            review = item[REVIEW]
            line = f'{review[REVIEW_ID]},{review[RECIPE_ID]},{review[USER_ID]},{review[RATING]},{review[COMMENT]}\n'
            self.review.write(line)
        if item[TYPE] == FOLLOWER or item[TYPE] == FOLLOWING:
            a = ItemAdapter(item).asdict()
            line = f'{a[FOLLOW][0]},{a[FOLLOW][1]}\n'
            self.follow.write(line)
        return item


class FoodPicklePipeline:
    def open_spider(self, spider):
        self.data = {
            RECIPE: [],
            USER: [],
            REVIEW: [],
            FOLLOW: set(),
            ERROR: []
        }

    def close_spider(self, spider):
        Path(FOOD_DATA).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = FOOD_DATA_FILE.format(timestamp)
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)
        src = Path(filename)
        shutil.copy(src, DEST)

    def process_item(self, item, spider):
        if item[TYPE] == FOLLOWER or item[TYPE] == FOLLOWING:
            a = ItemAdapter(item).asdict()
            self.data[FOLLOW].add(a[FOLLOW])
        else:
            t = item[TYPE]
            del item[TYPE]
            self.data[t].append(item)
        return item
