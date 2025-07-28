from elasticsearch import Elasticsearch
import os

es_host = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
es_port = os.getenv("ELASTICSEARCH_PORT", "9200")

es_url = f"http://{es_host}:{es_port}"
es = Elasticsearch(es_url)

def get_es_info():
    try:
        return es.info()
    except Exception as e:
        print(f"Elasticsearch not available: {e}")
        return None
