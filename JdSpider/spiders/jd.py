# -*- coding: utf-8 -*-
import datetime
import json
import re
import time
import sys

from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from JdSpider.items import JdspiderItem
reload(sys)
sys.setdefaultencoding('utf-8')

class JdSpider(CrawlSpider):
    name = "jd"
    allowed_domains = ["jd.com", "p.3.cn"]
    start_urls = ['https://www.jd.com/allSort.aspx']
    rules = (Rule(LinkExtractor(allow='item.jd.com/\d+', deny=('club.jd.com/(?!comment).+')), follow=True,
                  callback='parse_item'),
             Rule(LinkExtractor(allow='jd.com', deny=('club.jd.com/(?!comment).+'),
                                restrict_xpaths=('//div[@class="items"]//a')), follow=True),
             )

    def parse_item(self, response):
        skuId = re.findall(r'https://item.jd.com/(\d+).html', response.url)
        if not skuId:
            return
        item = JdspiderItem()
        item['url'] = response.url
        item['sku'] = skuId[0]
        item['name'] = response.css('.sku-name,#name > h1').xpath("string(.)").extract_first().strip()
        item['shopName'] = response.css(
            '.contact .name a::attr(title),#extInfo .seller-infor .name::attr(title)').extract_first()
        html = response.text
        item['shopId'] = re.findall(r"shopId:'?(\d+)'?", html)[0]
        item['cat'] = re.findall(r"cat: \[(\d+),(\d+),(\d+)\]", html)[0]
        tag = response.css('.u-jd,.i-ziying').xpath("string(.)").extract_first()
        item['isJD'] = 1 if tag and u'自营' in tag else 0
        item['category'] = response.css('.crumb-wrap .crumb .item > a::text,#root-nav .breadcrumb a::text').extract()
        item['brand'] = response.css('#parameter-brand li::text').extract_first()
        item['parameter'] = response.css('.parameter2 li::text,#parameter2 li::text').extract()

        price_url = r'https://p.3.cn/prices/mgets?type=1&area=1_72_2799_0&pdtk=&pduid=&pdpin=&pdbp=0&skuIds=J_{}&source=item-pc'.format(
            item['sku'])
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'p.3.cn',
            'Referer': response.url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        }
        yield Request(url=price_url, headers=headers, meta={'item': item}, callback=self.parse_price)

    def parse_price(self, response):
        item = response.meta['item']
        jsonresponse = json.loads(response.body_as_unicode())
        item['price'] = jsonresponse[0].get('p')
        promotion_url = r'https://cd.jd.com/promotion/v2?skuId={}&area=1_72_2799_0&shopId={}&venderId={}&cat={}%2C{}%2C{}&isCanUseDQ=isCanUseDQ-1&isCanUseJQ=isCanUseJQ-1'.format(
            item['sku'], item['shopId'], item['shopId'], item['cat'][0], item['cat'][1], item['cat'][2])
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': '__jda=122270672.14955178194161933167621.1495517819.1495517819.1495517819.1; __jdb=122270672.1.14955178194161933167621|1.1495517819; __jdc=122270672; __jdv=122270672|direct|-|none|-|1495517819419; __jdu=14955178194161933167621',
            'Host': 'cd.jd.com',
            'Referer': 'https://item.jd.com/{}.html'.format(item['sku']),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        yield Request(url=promotion_url, headers=headers, meta={'item': item}, callback=self.parse_promotion)

    def parse_promotion(self, response):
        item = response.meta['item']
        jsonresponse = json.loads(response.body_as_unicode())
        promotion = jsonresponse.get("prom")
        promotion_dict = {}
        tags = promotion.get("pickOneTag", []) + promotion.get("tags", [])
        for tag in tags:
            name = tag.get("name")
            print name
            content = tag.get("content").replace("&nbsp;<a href='javascript:login();'>", " ").replace("</a>&nbsp;", " ")
            promotion_dict[name] = content
        item['promotion'] = promotion_dict
        comment_url = r'http://club.jd.com/comment/productCommentSummaries.action?referenceIds={}'.format(item['sku'])
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': '__jda=122270672.150175594619176500199.1501755946.1501755946.1501755946.1; __jdb=122270672.1.150175594619176500199|1.1501755946; __jdc=122270672; __jdv=122270672|controller.bdatahub.com|-|referral|-|1501755946192; __jdu=150175594619176500199',
            'Host': 'club.jd.com',
            'Referer': 'http://item.jd.com/{}.html'.format(item['sku']),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        }
        yield Request(url=comment_url, headers=headers, meta={'item': item}, callback=self.parse_comment)

    def parse_comment(self, response):
        item = response.meta['item']
        try:
            data = json.loads(response.body_as_unicode())
            item['commentsCount'] = data['CommentsCount'][0]['CommentCountStr']
        except Exception, e:
            pass
        item['downloadTime'] = datetime.datetime.now()
        yield item
