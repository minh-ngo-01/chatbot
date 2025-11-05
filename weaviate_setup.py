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

def initialize_products_collection(client):
    if not client.collections.exists('products'):
        products=client.collections.create(
            name='products',
            vector_config=Configure.Vectors.text2vec_weaviate(
                name='vector',
                source_properties=['product_code', 'name', 'short_desc',
                                'price', 'gender', 'highlights','usage',
                                'features', 'care']),
            properties=[
                Property(name='product_id', vectorize_property_name=False, data_type=DataType.TEXT),
                Property(name='product_code', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='name', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='short_desc', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='price', vectorize_property_name=True, data_type=DataType.INT),
                Property(name='gender', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='highlights', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='technology', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='material', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='style', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='usage', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='features', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='care', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='images', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='storage', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='product_url', vectorize_property_name=True, data_type=DataType.TEXT),
            ]
                        
        )
    return products

def populate_collection(collection, list_):
    for dict_ in list_:
        with collection.batch.fixed_size(batch_size=100) as batch:
            batch.add_object(
                properties= {'product_id':dict_['product_id'],
            'product_code':dict_['product_code'],
            'name':dict_['name'],
            'short_desc':dict_['short_desc'],
            'price':dict_['price'],
            'gender':dict_['gender'],
            'highlights':dict_['highlights'],
            'technology':dict_['technology'],
            'material':dict_['material'],
            'style':dict_['style'],
            'usage':dict_['usage'],
            'features':dict_['features'],
            'care':dict_['care'],
            'images':dict_['images'],
            'storage':dict_['storage'],
            'product_url':dict_['product_url']})
            if batch.number_errors >10:
                print('Batch import stopped due to too many errors.')
                break    
    return collection






