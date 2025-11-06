import weaviate
from weaviate.classes.init import Auth
from utils import classify_query
from utils import query_faq
from utils import query_product
from utils import query_other
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv
import joblib
import time

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
    load_dotenv()
    weaviate_url=os.getenv('WEAVIATE_URL')
    weaviate_api_key=os.getenv('WEAVIATE_API_KEY')
    try:
        chat_history=joblib.load('chat_history.joblib')
    except:
        chat_history=[]
        joblib.dump(chat_history, 'chat_history.joblib')
    with weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key)
    ) as client:
        
        query=question.query
        query_type=classify_query(query)
        if query_type=='FAQ':
            res=query_faq(client, query)
        elif query_type=='Product':
            res=query_product(client, query)
        else:
            res=query_other(query)

        print(query_type)
        print(query_type=='Product')
        # with open('text.txt', 'w') as f:
        #     f.write(res)
        chat_history.append({'time': time.asctime(), 'customer':query, 'bot':res})
        joblib.dump(chat_history, 'chat_history.joblib')
        return {'message':res}

@app.get('/')
def root():
    return {'message':'FastAPI chatbot backend running!'}