# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
from .models.es_types import ArticleType
import pymysql
import pymysql.cursors
import codecs
import json
from w3lib.html import remove_tags
class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

#自定义
class JsonWithPipeline(object):
    def __init__(self):
        self.file = codecs.open('aritcle.json', 'wb', encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()

#scrapy 自带
class JsonExporterPipeline(object):
    def __init__(self):
        self.file = open("articleexport.json", "wb")
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value["path"]

        item["author_img_path"] = [image_file_path]

        return item
#mysql  同步
class ArticleMysqlPipeline(object):
        def __init__(self):
            self.connect = pymysql.connect(
                host="127.0.0.1",
                db="aritcle_spider",
                user="root",
                passwd="root",
                charset='utf8',
                use_unicode=True,
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.connect.cursor()

        def process_item(self, item, spider):
            index_sql = """
            insert into sifou_aritcle(title,author_name,time,url,url_object_id,author_img_url,author_img_path,content)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
            """
            self.cursor.execute(index_sql, (item['title'], item['author_name'], item['time'], item['url'], item['url_object_id'], item['author_img_url'], item['author_img_path'], item['content']))
            self.connect.commit()
            return item

#异步化
class MyTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
        host=settings["MYSQL_HOST"],
        db=settings["MYSQL_DBNAME"],
        user=settings["MYSQL_USER"],
        passwd=settings["MYSQL_PASSWORD"],
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor,
        use_unicode=True,
        )

        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
      #将插入变成异步
        query = self.dbpool.runInteraction(self.do_insert, item)
        #错误处理
        query.addErrback(self.handle_error,item,spider)

    def handle_error(self, failure, item, spider):
        print(failure)


    def do_insert(self,cursor,item):
        index_sql, params = item.get_insert_sql()

        cursor.execute(index_sql, params)

class ElasticsearchPipeline(object):
    # 将数据插入es
    def process_item(self, item, spider):
      #将item转换成es的数据
        item.save_to_es()
        return item

#
# class LagouJobTwistedPipeline(object):
#     def __init__(self, dbpool):
#         self.dbpool = dbpool
#     @classmethod
#     def from_settings(cls, settings):
#         dbparms = dict(
#         host=settings["MYSQL_HOST"],
#         db=settings["MYSQL_DBNAME"],
#         user=settings["MYSQL_USER"],
#         passwd=settings["MYSQL_PASSWORD"],
#         charset='utf8',
#         cursorclass=pymysql.cursors.DictCursor,
#         use_unicode=True,
#         )
#
#         dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
#         return cls(dbpool)
#
#     def process_item(self, item, spider):
#       #将插入变成异步
#         query = self.dbpool.runInteraction(self.do_insert, item)
#         #错误处理
#         query.addErrback(self.handle_error)
#
#     def handle_error(self, failure):
#         print(failure)
#
#
#     def do_insert(self,cursor,item):
#         index_sql = """
#                             insert into lagou_job(title,url,salary,job_city,work_years,degree_need,job_type,publish_time,job_advantage,job_desc,job_addr,company_name,company_url,job_addr)
#                             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#                 """
#         cursor.execute(index_sql, (
#             item["title"], item["url"], item["salary"],
#             item["job_city"], item["work_years"], item["degree_need"],
#             item["job_type"], item["publish_time"], item["job_advantage"], item["job_desc"], item["job_addr"],
#             item["company_name"], item["company_url"], item["job_addr"]))
