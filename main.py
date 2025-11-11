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

from utils import classify_query, query_faq, query_product, query_other, get_prev_chat

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
    gender: str
    masterCategory: str
    subCategory: str
    articleType: str
    baseColour: str
    season: str
    year: int
    usage: str
    productDisplayName: str
    price: int
    product_id: int

@app.post('/add_product')
def add_product(product: Product):
    load_dotenv()
    weaviate_url=os.getenv('WEAVIATE_URL')
    weaviate_api_key=os.getenv('WEAVIATE_API_KEY')
    with weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key)
    ) as client:

        collection=get_products_collection(client)
        try:
            collection.data.insert(
                properties={
                'gender': product.gender,
                'masterCategory': product.masterCategory,
                'subCategory': product.subCategory,
                'articleType': product.articleType,
                'baseColour': product.baseColour,
                'season': product.season,
                'year': product.year,
                'usage': product.usage,
                'productDisplayName': product.productDisplayName,
                'price': product.price,
                'product_id': product.product_id 
                })
            return {'message': f'Product {product.product_id} added'}
        except Exception as e:
            return {'error': str(e)}
        
@app.post('/chat')
def answer(chatRequest: chatRequest):
    weaviate_url=os.getenv('WEAVIATE_URL')
    weaviate_api_key=os.getenv('WEAVIATE_API_KEY')

    prev_chat='\n'.join(map(str,chatRequest.chat_history))
    print(prev_chat)
    with weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key)
    ) as client:
        query=chatRequest.query
        query_type=classify_query(query, prev_chat)
        print(query_type)
        if query_type=='FAQ':
            res=query_faq(client, query, prev_chat)
        elif query_type=='Product':
            res=query_product(client, query, prev_chat)
        else:
            res=query_other(query, prev_chat)
        with open('text.txt', 'w', encoding='utf-8') as f:
            f.write(res)
        # chat_history.append({'time': time.asctime(), 'customer':query, 'bot':res})
        # joblib.dump(chat_history, 'chat_history.joblib')
        return {'message':res}
    
# @app.post('/chat')
# def answer(chatRequest: chatRequest):
#         return {'message':"""Ok bạn, mình có thêm mẫu Quần Jogger Nam Daily Wear này nha, giá 179.000đ. Chất liệu Polyester thoáng mát, co giãn 4 chiều, kháng khuẩn và còn chống nước, chống tia UV nữa đó.
# <img src="https://n7media.coolmate.me/uploads/December2024/quan-joggers-the-thao-daily-wear-den-1.jpg" width=300>
# <img src="https://n7media.coolmate.me/uploads/December2024/quan-joggers-the-thao-daily-wear-den-2.jpg" width=300>
# <img src="https://n7media.coolmate.me/uploads/December2024/quan-joggers-the-thao-daily-wear-den-3.jpg" width=300>

# Mã sản phẩm: JGZ865

# Bạn xem thử nha!"""}

        

