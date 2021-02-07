# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import LagouJobItemLoader,LagouJobItem
from ..utils.common import get_md5
from scrapy.loader import ItemLoader
from datetime import datetime
#body div.position-head div div.position-content-l div::attr(title)
class LaogouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=r'zhaopin/.*'), follow=True),
        Rule(LinkExtractor(allow=r'gongsi/v1/.*'), follow=True),

        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )


    def parse_job(self, response):
        #解析职位
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)

        item_loader.add_css("title", ".job-name::attr(title)")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("salary", ".job_request .salary::text")
        item_loader.add_xpath("job_city", "//dd[@class='job_request']/h3/span[2]/text()")
        item_loader.add_xpath("work_years", "//dd[@class='job_request']/h3/span[3]/text()")
        item_loader.add_xpath("degree_need", "//dd[@class='job_request']/h3/span[4]/text()")
        item_loader.add_xpath("job_type", "//dd[@class='job_request']/h3/span[5]/text()")
        item_loader.add_css("tags",".position-label li::text")
        item_loader.add_css("publish_time", ".publish_time::text")
        item_loader.add_css("job_advantage",".job-advantage p::text")
        item_loader.add_css("job_desc",".job_bt div")
        item_loader.add_css("job_addr", ".work_addr")
        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
        job_item = item_loader.load_item()

        return item_loader.load_item()
