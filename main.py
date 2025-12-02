import os
import time
import joblib

import weaviate
from weaviate.classes.init import Auth
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List

from utils import classify_query, query_product, get_prev_chat, query_other

load_dotenv()
app=FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount("/static", StaticFiles(directory='frontend'), name='static')

@app.get('/')
def serve_index():
    return FileResponse(os.path.join('frontend', 'index.html'))

@app.get('/add_product_page')
def serve_add_product_page():
    return FileResponse(os.path.join('frontend', 'input.html'))


class Message(BaseModel):
    time: str
    user: str
    bot: str

class chatRequest(BaseModel):
    query: str
    chat_history: List[Message]

class Product(BaseModel):
    product_id: str
    product_code: str
    name: str
    desc: str
    price: int
    gender: str
    highlight: str
    technology: str
    material: str
    style: str
    usage: str
    feature: str
    care: str
    video: str
    image: str
    available_color: str
    available_size: str
    colorBySize: str

@app.post('/add_product')
def add_product(product: Product):
    load_dotenv()
    weaviate_url=os.getenv('WEAVIATE_URL')
    weaviate_api_key=os.getenv('WEAVIATE_API_KEY')
    with weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key)
    ) as client:
        collection=client.collections.get('products')
        try:
            collection.data.insert(
                properties={
                'product_id': product.product_id ,
                'product_code': product.product_code ,
                'name': product.name ,
                'desc': product.desc ,
                'price': product.price ,
                'gender': product.gender ,
                'highlight': product.highlight ,
                'technology': product.technology ,
                'material': product.material ,
                'style': product.style,
                'usage': product.usage,
                'feature': product.feature,
                'care': product.care,
                'video': product.video ,
                'image': product.image,
                'available_color': list(product.available_color),
                'available_size': list(product.available_size),
                'colorBySize': list(product.colorBySize),
                })
            return {'message': f'Product {product.product_id} added'}
        except Exception as e:
            return {'error': str(e)}

@app.post('/chat')
def answer(chat_request: chatRequest):
    weaviate_url=os.getenv('WEAVIATE_URL')
    weaviate_api_key=os.getenv('WEAVIATE_API_KEY')    
    prev_chat="/n".join(map(str,chat_request.chat_history))
    with weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key)
    ) as client:
        query=chat_request.query
        response=classify_query(query, prev_chat)
        if response['topic']=='Product':
            res=query_product(client, query, prev_chat, response['intent'])
        if response['topic']=='Delivery':
            res="Vấn đề giao hàng chưa được hỗ trợ"
        if response['topic']=='Other':
            res=query_other(client, query, prev_chat, response['intent'])
        return {'intent':response['intent'],'message':res}

# @app.post('/chat')
# def answer(chatRequest: chatRequest):
#         return {'message':"""Ok bạn, mình có thêm mẫu Quần Jogger Nam Daily Wear này nha, giá 179.000đ. Chất liệu Polyester thoáng mát, co giãn 4 chiều, kháng khuẩn và còn chống nước, chống tia UV nữa đó.
# <img src="https://n7media.coolmate.me/uploads/December2024/quan-joggers-the-thao-daily-wear-den-1.jpg" width=300>
# <img src="https://n7media.coolmate.me/uploads/December2024/quan-joggers-the-thao-daily-wear-den-2.jpg" width=300>
# <img src="https://n7media.coolmate.me/uploads/December2024/quan-joggers-the-thao-daily-wear-den-3.jpg" width=300>

# Mã sản phẩm: JGZ865

# Bạn xem thử nha!"""}

# load_dotenv()
# weaviate_url=os.getenv('WEAVIATE_URL')
# weaviate_api_key=os.getenv('WEAVIATE_API_KEY')
# with weaviate.connect_to_weaviate_cloud(
# cluster_url=weaviate_url,
# auth_credentials=Auth.api_key(weaviate_api_key)
# ) as client:
#     collection=client.collections.get('products')
#     try:
#         collection.data.insert(
#             properties={
#             'product_id': "123abc",
#             'product_code': "123abc",
#             'name': "abc",
#             'desc': "abc",
#             'price': 123,
#             'gender': "MALE",
#             'highlight': "abc",
#             'technology': "abc",
#             'material': "abc",
#             'style': "abc",
#             'usage': "abc",
#             'feature': "abc",
#             'care': "abc",
#             'video': "abc",
#             'image': "abc",
#             'available_color': ["abc"],
#             'available_size': ["abc"],
#             'colorBySize': ["abc"],
#             })
#         print( {'message': f'Product "123abc" added'})
#     except Exception as e:
#         print( {'error': str(e)})
