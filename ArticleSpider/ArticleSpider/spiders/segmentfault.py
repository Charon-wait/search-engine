# -*- coding: utf-8 -*-
import scrapy
from ..items import AritcleItem
from ..utils.common import get_md5
from datetime import datetime, timedelta
import re
from scrapy.http import Request
from urllib import parse
import datetime
from scrapy.loader import ItemLoader
import requests
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
class SegmentfaultSpider(scrapy.Spider):
    name = 'segmentfault'
    allowed_domains = ['segmentfault.com']
    start_urls = ['https://segmentfault.com/blogs']
    custom_settings = {
        "COOKIES_ENABLED": True,

    }
    #动态网页
    # def __init__(self):
    #     self.browser = webdriver.Chrome()
    #     super(SegmentfaultSpider,self).__init__()
    #     dispatcher.connect(self.spider_close,signals.spider_closed)
    # def spider_close(self,spider):
    #     print("spider closed")
    #     self.browser.quit()
    # 2、获取文章列表的文章url交给解析函数
    def parse(self, response):
        #print(response.request.headers["User-Agent"])
        post_nodes = response.css('div.summary  a')
        # print(post_nodes)
        for post_node in post_nodes:
            #post_url = 'https://segmentfault.com'+ post_url

            post_url = post_node.css("[href^='/a/']::attr(href)").extract_first("")
            #print(post_url)
            post_url=post_url = 'https://segmentfault.com' + post_url
            yield Request(url=post_url, callback=self.parse_detail)

        # 1、获取下一页的url并交给scrapy下载解析
        next_urls = response.css(".next.page-item a::attr(href)").extract_first("")
        #print(next_urls)

        if next_urls:
            #print('----------------------------------------------------------------------------------------------')
            next_urls = 'https://segmentfault.com' + next_urls
            yield Request(url=next_urls, callback=self.parse)
            #print(post_url)
    #解析
    def parse_detail(self, response):


        article_item = AritcleItem()
        # 作者头像
        #image_url = post_node.css('img::attr(src)').extract_first("").strip()
        #root div.d-flex.align-items-center.mb-4 a picture img
        author_img_url = response.css('#root div.d-flex.align-items-center.mb-4 a picture img::attr(src) ').extract()
        print('******************************************************************************************************')

        #print(author_img_url)
        print('******************************************************************************************************')

        title = response.xpath('//div/h1/a/text()').extract()[0]
        time = response.css("div.font-size-14 time::attr(datetime)").extract()[0]
        time = time.replace('T', ' ').replace('+', ' ')
        content = response.xpath('//div/article').extract()[0]
        author_name = response.xpath('//*[@id="root"]/div[4]/div[1]/div[1]/div[2]/div/div[1]/a/strong/text()').extract_first()
        #print('******************************************************************************************************')

        article_item["url_object_id"] = get_md5(response.url)
        article_item["title"] = title
        article_item["url"] = response.url
        article_item["author_img_url"] = author_img_url
        try:
            time = datetime.datetime.strptime(time, "%Y/%m/%d").date()

        except Exception as e:
            time = datetime.datetime.now().date()

        article_item["time"] = time
        article_item["author_name"] = author_name
        article_item["content"] = content



        #通过item_loader加载item
        # item_loader = ItemLoader(item =AritcleItem(),response=response)
        # item_loader.add_css("author_img_url", "#root div.d-flex.align-items-center.mb-4 a picture img::attr(src)")
        # item_loader.add_css("time", "div.font-size-14 time::attr(datetime)")
        # item_loader.add_xpath("title", "//div/h1/a/text()")
        # item_loader.add_value("url",response.url)
        # item_loader.add_value("url_object_id", get_md5(response.url))
        # item_loader.add_xpath("content", "//div/article")
        # item_loader.add_xpath("author_name", "//*[@id='root']/div[4]/div[1]/div[1]/div[2]/div/div[1]/a/strong/text()")

        yield article_item

