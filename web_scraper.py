import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re
import json
from weaviate_setup import initialize_products_collection, populate_collection
import time
import random


def get_item_urls(url):
    HEADERS={'User-Agent': 'my-clothes-scraper/1.0'}
    r =requests.get(url, headers=HEADERS, timeout=5)
    html=r.text
    soup=BeautifulSoup(html,'lxml')
    item_urls=[]
    for item in soup.select('a.block.h-full.w-full'):
        if item['href'].startswith('/product/'):
            href=item['href']
            item_url=urljoin(url, href)
            item_urls.append(item_url)
    return item_urls

def get_id(item_url):
    HEADERS={'User-Agent': 'my-clothes-scraper/1.0'}
    r =requests.get(item_url, headers=HEADERS, timeout=5)
    html=r.text
    soup=BeautifulSoup(html,'lxml')
    for script in soup.select('script'):
        if 'regular_price' in script.text:
            match=re.search(r'"id":"([A-Za-z0-9]{24})"', script.text.replace('\\',""))
    print(match.group(1))
    return match.group(1)
        
    



def get_item_info(product_id):
    url = f"https://www.coolmate.me/api/proxy/products?ids={product_id}"
    product = requests.get(url).json()["data"][0]
    with open('json.json', 'w', encoding='utf-8') as f:
        json.dump(product, f, ensure_ascii=False, indent=2)
    product_id=product['id']
    try:
        product_code=product['spu']
    except:
        product_code=""
    name=product['title']
    short_desc=product['short_desc']
    price=product['regular_price']
    gender=product['gender_type']
    try:
        highlights=", ".join([dict_['title'] for dict_ in product['extra']["p_extra_attributes"]])
    except:
        highlights=""
    try:
        technology=product['extra']['p_extra_features'][0]['value'][0]['title']
    except:
        technology=""
    try:
        material=product['extra']['p_extra_features'][1]['value'][0]['title']
    except:
        material=""
    try:
        style=product['extra']['p_extra_features'][2]['value'][0]['title']
    except:
        style=""
    try:   
        usage=product['extra']['p_extra_features'][3]['value'][0]['title']
    except:
        usage=""
    try:
        features=product['extra']['p_extra_features'][4]['value'][0]['title']
    except:
        features=""
    try:
        care=", ".join([dict_['title'] for dict_ in product['extra']['p_extra_features'][5]['value']])
    except:
        care=""
    images=['https://n7media.coolmate.me/uploads/'+dict_['src'][7:] for dict_ in product['images']]
    storage={}
    for variant in product['variants']:
        if variant['quantity']>0:
            color=variant['option1']
            size=variant['option2']
            quantity=variant['quantity']
            storage[size+" "+color]=quantity
    product_url='https://www.coolmate.me/product/'+ product['seo_alias']

    return {'product_id':product_id,
            'product_code':product_code,
            'name':name,
            'short_desc':short_desc,
            'price':price,
            'gender':gender,
            'highlights':highlights,
            'technology':technology,
            'material':material,
            'style':style,
            'usage':usage,
            'features':features,
            'care':care,
            'images':str(images),
            'storage':str(storage),
            'product_url':product_url
            }
def get_items_data(url):    
    list_=[]
    urls=get_item_urls(url)
    for url in urls:
        time.sleep(random.uniform(1,2))
        id=get_id(url)
        dict_=get_item_info(id)
        list_.append(dict_)
    return list_



            
