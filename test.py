
import os
import weaviate
from weaviate.classes.query import Filter
from weaviate.classes.init import Auth
from dotenv import load_dotenv
import json
load_dotenv()

filter=Filter.by_property('product_code').equal('TSZ959')
weaviate_url=os.getenv('WEAVIATE_URL')
weaviate_api_key=os.getenv('WEAVIATE_API_KEY')
with weaviate.connect_to_weaviate_cloud(
cluster_url=weaviate_url,
auth_credentials=Auth.api_key(weaviate_api_key)
) as client:
    products=client.collections.get('products')
    response=products.query.near_text(query='áo thun nam',filters=filter)

print(response.objects[0].properties['images'])
