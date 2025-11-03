import weaviate
import joblib
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure
from weaviate.classes.config import Property
from weaviate.classes.config import DataType
import os

def get_faqs_collection(client):
    if not client.collections.exists('faqs'):
        faqs=client.collections.create(
            name='faqs',
            vector_config=Configure.Vectors.text2vec_weaviate(
                name='vector',
                source_properties=['question', 'answer', 'type']),
            properties=[
                Property(name='question', vectorize_property_name=False, data_type=DataType.TEXT),
                Property(name='answer', vectorize_property_name=False, data_type=DataType.TEXT),
                Property(name='type', vectorize_property_name=False, data_type=DataType.TEXT)])
        
        faq_data=joblib.load('faq.joblib')
        with faqs.batch.fixed_size(batch_size=100) as batch:
            for faq in faq_data:
                batch.add_object(
                    {'question': faq['question'],
                    'answer': faq['answer'],
                    'type': faq['type'],
                    })
                if batch.number_errors >10:
                    print('Batch import stopped due to too many errors.')
                    break
    else:
        faqs=client.collections.get('faqs')
    return faqs

def get_products_collection(client):
    if not client.collections.exists('products'):
        products=client.collections.create(
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
                Property(name='baseColour', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='season', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='year', vectorize_property_name=False, data_type=DataType.NUMBER),
                Property(name='usage', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='productDisplayName', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='price', vectorize_property_name=True, data_type=DataType.NUMBER),
                Property(name='product_id', vectorize_property_name=True, data_type=DataType.INT),
                Property(name='image_url', vectorize_property_name=False, data_type=DataType.TEXT)

            ]
                        
        )
        
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
                    'product_id': product['product_id'],
                    'image_url': 'http://127.0.0.1:8000/images/' + str(product['product_id']) + '.jpg'})
                if batch.number_errors >10:
                    print('Batch import stopped due to too many errors.')
                    break
    else:
        products=client.collections.get('products')
    return products