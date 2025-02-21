from elasticsearch_async import AsyncElasticsearch
from app.core.config import settings

es_client = AsyncElasticsearch([settings.ELASTICSEARCH_URL])

product_index = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "name": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword"},
                    "suggest": {"type": "completion"}
                }
            },
            "vendor_id": {"type": "keyword"},
            "vendor_name": {"type": "text"},
            "category": {"type": "keyword"},
            "type": {"type": "keyword"},
            "description": {"type": "text"},
            "base_price": {"type": "float"},
            "measurement_unit": {"type": "keyword"},
            "delivery_options": {"type": "keyword"},
            "country": {"type": "keyword"},
            "city": {"type": "keyword"},
            "location": {"type": "geo_point"},
            "is_active": {"type": "boolean"}
        }
    }
}

async def init_elasticsearch():
    """Initialize Elasticsearch indices"""
    if not await es_client.indices.exists(index="products"):
        await es_client.indices.create(index="products", body=product_index)

async def index_product(product_data):
    """Index a product in Elasticsearch"""
    await es_client.index(
        index="products",
        id=product_data["id"],
        body=product_data,
        refresh=True
    )

async def search_products(query, filters=None, location=None):
    """
    Search products with advanced filtering
    
    Args:
        query (str): Search query
        filters (dict): Filter parameters (category, type, delivery_method, etc.)
        location (dict): Location data for geo-based search
    """
    must = []
    if query:
        must.append({
            "multi_match": {
                "query": query,
                "fields": ["name^3", "description", "vendor_name"]
            }
        })
    
    if filters:
        for key, value in filters.items():
            if value:
                must.append({"term": {key: value}})
    
    if location and location.get("lat") and location.get("lon"):
        must.append({
            "geo_distance": {
                "distance": f"{location.get('radius', '10')}km",
                "location": {
                    "lat": location["lat"],
                    "lon": location["lon"]
                }
            }
        })
    
    body = {
        "query": {"bool": {"must": must}},
        "sort": [{"_score": "desc"}]
    }
    
    result = await es_client.search(
        index="products",
        body=body
    )
    return result["hits"]["hits"]
