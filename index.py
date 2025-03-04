from opensearchpy import OpenSearch

OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200

client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
    use_ssl=False,
)

INDEX_NAME = "documents"

index_body = {
    "settings": {
        "analysis": {
            "filter": {
                "synonym_filter": {
                    "type": "synonym",
                    "synonyms": [
                        "AI, artificial intelligence",
                        "ML, machine learning",
                        "NLP, natural language processing"
                    ]
                }
            },
            "analyzer": {
                "synonym_analyzer": {
                    "tokenizer": "standard",
                    "filter": ["lowercase", "synonym_filter"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "filename": {"type": "text"},
            "content": {"type": "text", "analyzer": "synonym_analyzer"},
            "upload_date": {"type": "date"}
        }
    }
}

# Delete existing index if it exists
if client.indices.exists(INDEX_NAME):
    client.indices.delete(index=INDEX_NAME)

# Create a new index
client.indices.create(index=INDEX_NAME, body=index_body)
print("Index created successfully!")
