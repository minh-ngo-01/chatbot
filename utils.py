from weaviate_setup import get_faqs_collection
from weaviate_setup import get_products_collection
import re

import os
from openai import OpenAI
import joblib

def classify_query(query):
    client=OpenAI(
        base_url='https://router.huggingface.co/v1',
        api_key='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')
    completion=client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct:novita",
        messages=[{'role':'user',"content":f"""Label the following instruction as an FAQ-related query or a produt-related query.
                return either 'FAQ' or 'Product'. Nothing else!
                'Query':{query}"""}])
    return completion.choices[0].message.content.strip().replace("'", "")



def query_faq(client, query):

    faqs=get_faqs_collection(client)
    response=faqs.query.near_text(query, limit=3)

    context=""
    for res in response.objects:
        context+=f"Question: {res.properties['question']} Answer: {res.properties['answer']}\n"
    
    client=OpenAI(
        base_url='https://router.huggingface.co/v1',
        api_key='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')
    
    completion=client.chat.completions.create(
        model="MiniMaxAI/MiniMax-M2:novita",
        messages=[{'role':'system',"content":'You are a helpful assistant of an online clothing store'},
            {'role':'user',"content":f""" Answer the faq question {query} just using the information bellow:
                    {context}.
                    Respond as you are a representative of the clothing store."""}])
    return completion.choices[0].message.content

def query_product(client, query):
    products=get_products_collection(client)
    product_data=joblib.load('clothes_json.joblib')
    possible_color=set()
    for product in product_data:
        for key in product.keys():
            if key=='baseColour':
                possible_color.add(product[key])

    client=OpenAI(
        base_url='https://router.huggingface.co/v1',
        api_key='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')

    prompt=f""" Base on the query given, extract the useful metadata to search relevat clothing items.
            the metadata includes 'gender', 'colour' and 'price'.
            Just return JSON object, nothing else.
            {{
            'gender': ['Men'] (possible values in:['Men', 'Women'])
            'baseColour': ['Black'] (possible values in: [{" , ".join([color for color in possible_color if type(color)==str])}] if not mentioned, leave None
            'price': {{'min': 0, 'max': 1000}} if not mentioned, leave None
            }} 
            Here is the query: {query}.

            """
    completion=client.chat.completions.create(
            model='openai/gpt-oss-20b:groq',
            messages=[{'role':'user',"content":prompt}])
    meta_data= completion.choices[0].message.content

    print(meta_data)
    import json
    meta_data=json.loads(meta_data)
    from weaviate.classes.query import Filter
    filters=[]
    for key, value in meta_data.items():
        if value==None:
            continue
        elif key=='price':
            if value['min']<0:
                continue        
            
            filters.append(Filter.by_property(key).greater_than(value['min']))
            filters.append(Filter.by_property(key).less_than(value['max']))
        else:
            filters.append(Filter.by_property(key).contains_any(value))

    response=products.query.near_text(query=f'{query}',filters=Filter.all_of(filters) if len(filters) != 0 else None, limit=5)
    
    context=""
    for res in response.objects:
        context+=f"""product_id: {res.properties['product_id']},
                     product display name:{res.properties['productDisplayName']},
                     baseColour: {res.properties['baseColour']},
                     usage: {res.properties['usage']},
                     price: {res.properties['price']},
                     image_url: {res.properties['image_url']}/n"""
    
    prompt=f""" You will be given a query from customer and the retrieved product detail information, answer the query like a store representitive.
                query: {query}.
                products: {context}.
                Format the image_url to Markdown text."""
    completion=client.chat.completions.create(
        model="MiniMaxAI/MiniMax-M2:novita",
        messages=[{'role':'system',"content":"""act as a sale representative in a cloth store"""},
            {'role':'user',"content":prompt}])
    print(completion.choices[0].message.content)
    # with open('text.txt', 'w', encoding='utf-8') as f:
    #     f.write(re.sub(r'<think>.*?</think>',"",completion.choices[0].message.content, flags=re.DOTALL).strip())
    return re.sub(r'<think>.*?</think>',"",completion.choices[0].message.content, flags=re.DOTALL).strip()
    
    

        

