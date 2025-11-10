from weaviate.classes.config import Configure
from weaviate.classes.config import Property
from weaviate.classes.config import DataType

def initialize_faqs_collection(client):
    if not client.collections.exists('faqs'):
        faqs=client.collections.create(
            name='faqs',
            vector_config=Configure.Vectors.text2vec_weaviate(
                name='vector',
                source_properties=['question', 'answer']),
            properties=[
                Property(name='question', vectorize_property_name=False, data_type=DataType.TEXT),
                Property(name='answer', vectorize_property_name=False, data_type=DataType.TEXT)
            ]   
        )
    return faqs

def populate_faqs_collection(collection, list_):
    for dict_ in list_:
        with collection.batch.fixed_size(batch_size=100) as batch:
            batch.add_object(
            properties= (
                    {'question': dict_['question'],
                    'answer': dict_['answer'],
                    }))
            if batch.number_errors >10:
                print('Batch import stopped due to too many errors.')
                break    
    return collection

def initialize_products_collection(client):
    if not client.collections.exists('products'):
        products=client.collections.create(
            name='products',
            vector_config=Configure.Vectors.text2vec_weaviate(
                name='vector',
                source_properties=['product_code', 'name', 'desc',
                                'price', 'gender', 'highlights','usage',
                                'features']),
            properties=[
                Property(name='product_id', vectorize_property_name=False, data_type=DataType.TEXT),
                Property(name='product_code', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='name', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='desc', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='price', vectorize_property_name=True, data_type=DataType.INT),
                Property(name='gender', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='highlights', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='technology', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='material', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='style', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='usage', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='features', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='care', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='video', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='images', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='storage', vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name='product_url', vectorize_property_name=True, data_type=DataType.TEXT),
            ]
                        
        )
    return products

def populate_products_collection(collection, list_):
    for dict_ in list_:
        with collection.batch.fixed_size(batch_size=100) as batch:
            batch.add_object(
                properties= {'product_id':dict_['product_id'],
            'product_code':dict_['product_code'],
            'name':dict_['name'],
            'desc':dict_['desc'],
            'price':dict_['price'],
            'gender':dict_['gender'],
            'highlights':dict_['highlights'],
            'technology':dict_['technology'],
            'material':dict_['material'],
            'style':dict_['style'],
            'usage':dict_['usage'],
            'features':dict_['features'],
            'care':dict_['care'],
            'video':dict_['video'],
            'images':dict_['images'],
            'storage':dict_['storage'],
            'product_url':dict_['product_url']})
            if batch.number_errors >10:
                print('Batch import stopped due to too many errors.')
                break    
    return collection


urls=[         
              'https://www.coolmate.me/collection/ao-ba-lo-tank-top-nam',
              'https://www.coolmate.me/collection/ao-thun-nam',
              'https://www.coolmate.me/collection/ao-nam-choi-the-thao',
              'https://www.coolmate.me/collection/ao-polo-nam',
              'https://www.coolmate.me/collection/ao-so-mi-nam',
              'https://www.coolmate.me/collection/ao-nam-dai-tay',
              'https://www.coolmate.me/collection/ao-sweater-len-ni-nam',
              'https://www.coolmate.me/collection/ao-khoac-nam',
              'https://www.coolmate.me/collection/quan-short-nam',
              'https://www.coolmate.me/collection/quan-jogger-nam',
              'https://www.coolmate.me/collection/quan-nam-choi-the-thao',
              'https://www.coolmate.me/collection/quan-dai-nam',
              'https://www.coolmate.me/collection/quan-pants-nam',
              'https://www.coolmate.me/collection/quan-jeans-nam',
              'https://www.coolmate.me/collection/quan-kaki-nam',
              'https://www.coolmate.me/collection/do-boi-nam',
              'https://www.coolmate.me/collection/quan-tam-giac-brief',
              'https://www.coolmate.me/collection/quan-boxer-trunk',
              'https://www.coolmate.me/collection/quan-boxer-brief-dang-dai',
              'https://www.coolmate.me/collection/quan-long-leg',
              'https://www.coolmate.me/collection/quan-boxer-shorts',
              'https://www.coolmate.me/collection/phu-kien-nam'] 

# import os
# from weaviate.classes.init import Auth
# import weaviate
# from web_scraper import get_items_data
# from dotenv import load_dotenv
# import tqdm
# load_dotenv()
# weaviate_url=os.getenv('WEAVIATE_URL')
# weaviate_api_key=os.getenv('WEAVIATE_API_KEY')
# with weaviate.connect_to_weaviate_cloud(
#     cluster_url=weaviate_url,
#     auth_credentials=Auth.api_key(weaviate_api_key)
#     ) as client:
#     client.collections.delete('products')
#     products=initialize_products_collection(client)
#     # products=client.collections.get('products')
#     for url in tqdm.tqdm(urls):
#         product_data=get_items_data(url)
#         products=populate_products_collection(products, product_data)

# # if not client.collections.exists('faqs'):
# #     faqs=initialize_faqs_collection(client)
# #     faqs_data=get_faqs_data()
# #     faqs=populate_faqs_collection(faqs, faqs_data)
# # else:

# import weaviate
# from weaviate.classes.init import Auth
# import os
# from weaviate.classes.query import Filter
# from dotenv import load_dotenv
# load_dotenv()
# weaviate_url=os.getenv('WEAVIATE_URL')
# weaviate_api_key=os.getenv('WEAVIATE_API_KEY')
# filter=Filter.by_property('product_code').equal('SM006')
# with weaviate.connect_to_weaviate_cloud(
# cluster_url=weaviate_url,
# auth_credentials=Auth.api_key(weaviate_api_key)
# ) as client:
#     products=client.collections.get('products')
#     print(products.query.fetch_objects(filters=filter))
    

