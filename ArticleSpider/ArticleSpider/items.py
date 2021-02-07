# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
import scrapy
from scrapy.loader import ItemLoader
from .settings import  SQL_DATETIME_FORMAT,SQL_DATE_FORMAT
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags
from .models.es_types import ArticleType
from elasticsearch_dsl.connections import connections
import redis
redis_cli = redis.StrictRedis()
es = connections.create_connection(ArticleType._doc_type.using)
class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
def gen_suggests(index,info_tuple):
    #根据字符串生成搜索建议词
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests

class AritcleItem(scrapy.Item):
    title = scrapy.Field()
    author_name = scrapy.Field()
    time = scrapy.Field()
    url = scrapy.Field()
    author_img_url = scrapy.Field()
    content = scrapy.Field()
    url_object_id = scrapy.Field()
    author_img_path = scrapy.Field()
    def get_insert_sql(self):
        index_sql = """
               insert into sifou_aritcle(title,author_name,time,url,url_object_id,author_img_url,author_img_path,content)
               VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
               """
        params = (
            self["title"],self["author_name"],self["time"],
            self["url"],self["url_object_id"],self["author_img_url"],
            self["author_img_path"],self["content"],
        )
        return index_sql, params
    def save_to_es(self):
        article = ArticleType()
        article.title = self['title']
        article.author_name = self['author_name']
        article.time = self['time']
        article.url = self['url']
        article.meta.id = self['url_object_id']
        article.author_img_url = self['author_img_url']
        if "author_img_path" in self:
            article.author_img_path = self['author_img_path']
        article.content = remove_tags(self['content'])
        article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title,10),(article.content,7)))

        article.save()
        redis_cli.incr("pm_count")  # redis存储爬虫数量
        return

def remove_splash(value):
    return value.replace("/", "")

def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip()!="查看地图" ]
    return "".join(addr_list)
class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

class LagouJobItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years = scrapy.Field(
       input_processor= MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=MapCompose(remove_tags)
    )
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr)
    )
    company_name = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",",)
    )
    company_url = scrapy.Field()
    def get_insert_sql(self):
        index_sql = """
                    insert into lagou_job(title,url,salary,job_city,work_years,degree_need,job_type,publish_time,job_advantage,job_desc,job_addr,company_name,company_url,job_addr)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        # create_time = datetime.datetime.fromtimestamp(self["create_time"])
        # update_time = datetime.datetime.fromtimestamp(self["update_time"])
        params = (
            self["title"],self["url"],self["salary"],
            self["job_city"],self["work_years"],self["degree_need"],
            self["job_type"],self["publish_time"],self["job_advantage"],self["job_desc"],self["job_addr"],self["company_name"],self["company_url"],self["job_addr"],
        )

        return index_sql, params