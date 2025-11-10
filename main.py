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

from utils import classify_query, query_faq, query_product, query_other, get_prev_chat

load_dotenv()
app=FastAPI()

origins = [
    "https://chatbot-qhxh.onrender.com",  # <-- your deployed frontend
    "http://localhost:3000",                   # for local testing
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


class Question(BaseModel):
    query: str
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
def answer(question: Question):
    weaviate_url=os.getenv('WEAVIATE_URL')
    weaviate_api_key=os.getenv('WEAVIATE_API_KEY')
    try:
        chat_history=joblib.load('chat_history.joblib')
    except:
        chat_history=[]
        joblib.dump(chat_history, 'chat_history.joblib')
    prev_chat=get_prev_chat()
    # print(prev_chat)
    with weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key)
    ) as client:
        query=question.query
        query_type=classify_query(query, prev_chat)
        print(query_type)
        if query_type=='FAQ':
            res=query_faq(client, query, prev_chat)
        elif query_type=='Product':
            res=query_product(client, query, prev_chat)
        else:
            res=query_other(query, prev_chat)
        # with open('text.txt', 'w', encoding='utf-8') as f:
        #     f.write(res)
        chat_history.append({'time': time.asctime(), 'customer':query, 'bot':res})
        joblib.dump(chat_history, 'chat_history.joblib')
        return {'message':res}
    
@app.get('/')
def root():
    return {'message':'FastAPI chatbot backend running!'}

        
# @app.post('/chat')
# def answer():
#     res="""Okie bạn! Mình gợi ý thêm mẫu Áo Thun Chạy Bộ Graphic Special nhé, đây là dòng sản phẩm chuyên chạy bộ cho nam, mang lại sự thoải mái, thoáng mát với chất liệu vải nhẹ, được xử lý hoàn thiện vải Quick-Dry thoát mồ hôi nhanh giúp bạn luôn khô ráo trên đường chạy. Giá chỉ 159.000đ thôi nè.
# <img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-chay-bo-nam-graphic-special-den-2_50.jpg", width=300>
# Mã sản phẩm: TSZ878

# Hoặc bạn có thể tham khảo Combo 3 Áo Thun Nam Thể Thao Coolmate Basics, giá 259.000đ, siêu nhẹ mỏng mát, năng động và thanh lịch, không nhăn nhàu khi giặt.
# <br><img src="https://n7media.coolmate.me/uploads/September2025/combo-03-ao-the-thao-nam-coolmate-basics-mau-1-1.jpg", width=300><br>

# Bạn thích mẫu nào hay muốn mình tìm kiếm theo tiêu chí nào không?"""
#     return {'message':res}        