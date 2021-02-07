from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=['localhost'])
class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word", filter = ["lowercase"])
class ArticleType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    author_name = Text(analyzer="ik_max_word")
    time = Date()
    url = Keyword()
    url_object_id = Keyword()
    author_img_url = Keyword()
    author_img_path = Keyword()
    content = Text(analyzer="ik_max_word")



    class Meta:
        index = "segmentfault"
        doc_type = "article"

if __name__ == "__main__":
    ArticleType.init()