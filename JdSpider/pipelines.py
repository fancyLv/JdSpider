# -*- coding: utf-8 -*-
import pymongo
from datetime import datetime


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class JdspiderPipeline(object):
    def process_item(self, item, spider):
        item["downloadTime"] = datetime.datetime.now()
        return item


class MongoDBPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client['Jd']
        self.JdItem = db['JdItem']

    def process_item(self, item, spider):
        self.JdItem.insert(item)
