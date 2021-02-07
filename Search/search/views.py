import json
from django.shortcuts import render
from django.views.generic.base import View
from search.models import ArticleType
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from datetime import datetime
import redis

client = Elasticsearch(hosts=["127.0.0.1"])

redis_cli = redis.StrictRedis()
class IndexView(View):
    def get(self,request):
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)

        return render(request,"index.html",{"topn_search": topn_search})

# Create your views here.
class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s', '')
        re_datas = []
        if key_words:
            s = ArticleType.search()
            s = s.suggest('my_suggest', key_words, completion={
                "field":"suggest","fuzzy": {
                    "fuzziness": 2
                },
                "size": 10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["title"]) # 获取查询结果title值
        return HttpResponse(json.dumps(re_datas),content_type="application/json")





class SearchView(View):
    def get(self,request):
        key_words = request.GET.get("q","")
        #s_type = request.GET.get("s_type","article")
        # 热门搜索设置和排序
        redis_cli.zincrby("search_keywords_set", 1, key_words)  # redis最新版本参数坑
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        page = request.GET.get("p","1") # 获取分页数据
        try:
            page = int(page) # 进行转换
        except:
            page = 1
        pm_count = redis_cli.get("pm_count")  # 获取爬虫数量
        start_time = datetime.now() # 获取查询开始时time
        response = client.search( # 允许我们编写kibana查询语句
            index = "segmentfault",
            body = {
                "query":{
                    "bool":{
                        "should": [
                          {"multi_match": {
                            "query": key_words,
                            "fields": ["title", "content"]
                          }},
                          {"fuzzy": {
                            "title": {
                                "value": key_words,
                                "fuzziness": 2
                            }
                          }}
                        ]
                    }
                },
                "from":(page-1)*10,
                "size":10,
                "highlight":{
                    "pre_tags":["<span class='keyWord'>"], #可以指定关键词使用的html标签
                    "post_tags":["</span>"],
                    "fields":{
                        "title":{},
                        "content":{},
                    }
                }
            }
        )

        end_time = datetime.now()
        last_seconds = (end_time - start_time) # 获取查询时间
        total_nums = response["hits"]["total"] # 获取查询到的值
        if (page%10) > 0: # 计算页码
            page_nums = int(total_nums/10) +1
        else:
            page_nums = int(total_nums/10)

        hit_list = []
        for hit in response["hits"]["hits"]: # 对查询的数据进行处理
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"]) # 获取title
            else:
                hit_dict["title"] = hit["_source"]["title"]
            if "content" in hit["highlight"]:
                #texts = hit["highlight"]["content"]
                #t1=texts[:500]
                #print(t1)

                hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]# 获取内容,取前500个
            else:
                hit_dict["content"] = hit["_source"]["content"][:500]

            hit_dict["time"] = hit["_source"]["time"] # 获取发布时间
            hit_dict["url"] = hit["_source"]["url"] # 获取跳转链接
            hit_dict["score"] = hit["_score"] # 获取分数

            hit_list.append(hit_dict)

        return render(request,"result.html",{"page":page,
                                            "all_hits":hit_list,
                                            "key_words":key_words,
                                            "total_nums":total_nums,
                                            "page_nums":page_nums,
                                            "last_seconds":last_seconds,
                                            "pm_count": pm_count,
                                            "topn_search": topn_search}) # 将后端获取的数据传递给前端页面
