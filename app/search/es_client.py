from elasticsearch import Elasticsearch

es = Elasticsearch('http://boiler-elasticsearch-1:9200') # http://boiler-elasticsearch-1:9200 - Docker

version_info = es.info()
print(version_info['version']['number']) 

if not es.ping():
    print("Connection to Elasticsearch failed")
else:
    print("Connected to Elasticsearch")