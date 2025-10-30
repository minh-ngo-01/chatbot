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

if not weaviate_client.collections.exists('faqs'):
    faqs=weaviate_client.collections.create(
        name='faqs',
        vector_config=Configure.Vectors.text2vec_weaviate(
            name='vector',
            source_properties=['question', 'answer', 'type']),
        properties=[
            Property(name='question', vectorize_property_name=False, data_type=DataType.TEXT),
            Property(name='answer', vectorize_property_name=False, data_type=DataType.TEXT),
            Property(name='type', vectorize_property_name=False, data_type=DataType.TEXT)
            ]
                    
    )
    import joblib
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
    faqs=weaviate_client.collections.get('faqs')

query='how can i pay'

import os
from openai import OpenAI
client=OpenAI(
    base_url='https://router.huggingface.co/v1',
    api_key='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')
completion=client.chat.completions.create(
    model="MiniMaxAI/MiniMax-M2:novita",
    messages=[{'role':'user',"content":f"""Label the following instruction as an FAQ-related query or a produt-related query.
               Return only 'FAQ' or 'Product'.
               'Query':{query}"""}])
question_type=completion.choices[0].message.content

response=faqs.query.near_text(query, limit=3)

context=""
for res in response.objects:
    context+=f"Question: {res.properties['question']} Answer: {res.properties['answer']}\n"
print(context)

completion=client.chat.completions.create(
    model="MiniMaxAI/MiniMax-M2:novita",
    messages=[{'role':'system',"content":'You are a helpful assistant of an online clothing store'},
        {'role':'user',"content":f""" Answer the faq question {query} just using the information bellow:
                {context}.
                Respond as you are a representative of the clothing store."""}])
print(completion.choices[0].message.content)

completion=client.chat.completions.create(
    model="MiniMaxAI/MiniMax-M2:novita",
    messages=[{'role':'system',"content":'You are a helpful assistant of an online clothing store'},
        {'role':'user',"content":f""""""}])
print(completion.choices[0].message.content)




weaviate_client.close()