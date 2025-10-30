import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure
from weaviate.classes.config import Property
from weaviate.classes.config import DataType
import os
weaviate_url='tokrkalystyjvoxbektmqq.c0.asia-southeast1.gcp.weaviate.cloud'
weaviate_api_key='OWQ5Vm9MUEdSa2VUaUtpL19RcHVUODlkbDF2WjFRWGc3dzFDUy9OWDI4R2RQSWIrUkhFakplTlREQzFRPV92MjAw'
weaviate_client=weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key)
)
print(weaviate_client.is_ready())

if not weaviate_client.collections.exists('products'):
    products=weaviate_client.collections.create(
        name='products',
        vector_config=Configure.Vectors.text2vec_weaviate(
            name='vector',
            source_properties=['gender', 'masterCategory', 'subCategory',
                               'articleType', 'baseColour', 'season','usage',
                               'productDisplayName']),
        properties=[
            Property(name='gender', vectorize_property_name=True, data_type=DataType.TEXT),
            Property(name='masterCategory', vectorize_property_name=True, data_type=DataType.TEXT),
            Property(name='subCategory', vectorize_property_name=True, data_type=DataType.TEXT),
            Property(name='articleType', vectorize_property_name=True, data_type=DataType.TEXT),
            Property(name='baseColor', vectorize_property_name=True, data_type=DataType.TEXT),
            Property(name='season', vectorize_property_name=True, data_type=DataType.TEXT),
            Property(name='year', vectorize_property_name=False, data_type=DataType.NUMBER),
            Property(name='usage', vectorize_property_name=True, data_type=DataType.TEXT),
            Property(name='productDisplayName', vectorize_property_name=True, data_type=DataType.TEXT),
            Property(name='price', vectorize_property_name=True, data_type=DataType.NUMBER),
            Property(name='product_id', vectorize_property_name=True, data_type=DataType.INT)

        ]
                    
    )
    import joblib
    product_data=joblib.load('clothes_json.joblib')
    with products.batch.fixed_size(batch_size=100) as batch:
        for product in product_data:
            batch.add_object(
                {'gender': product['gender'],
                'masterCategory': product['masterCategory'],
                'subCategory': product['subCategory'],
                'articleType': product['articleType'],
                'baseColour': product['baseColour'],
                'season': product['season'],
                'year': product['year'],
                'usage': product['usage'],
                'productDisplayName': product['productDisplayName'],
                'price': product['price'],
                'product_id': product['product_id']})
            if batch.number_errors >10:
                print('Batch import stopped due to too many errors.')
                break
else:
    products=weaviate_client.collections.get('products')

import PIL.Image as Image
response=products.query.near_text("""""", limit=3)
for obj in response.objects:
    print(obj.properties)
    print('images/'+str(obj.properties['product_id'])+'.jpg')
    img=Image.open('images/'+str(obj.properties['product_id'])+'.jpg')
    img.show()
print(type(response.objects))
weaviate_client.close()