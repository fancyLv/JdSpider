# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdspiderItem(scrapy.Item):
    # define the fields for your item here like:
    sku = scrapy.Field()
    name = scrapy.Field()
    shopId = scrapy.Field()
    shopName = scrapy.Field()
    cat = scrapy.Field()
    category = scrapy.Field()
    isJD = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    promotion = scrapy.Field()
    commentsCount = scrapy.Field()
    parameter = scrapy.Field()
    url = scrapy.Field()
    downloadTime = scrapy.Field()
