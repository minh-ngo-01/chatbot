import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re
import json
import time
import random


def get_item_urls(url):
    print(url)
    HEADERS={'User-Agent': 'my-clothes-scraper/1.0'}
    r =requests.get(url, headers=HEADERS, timeout=5)
    html=r.text
    soup=BeautifulSoup(html,'lxml')
    item_urls=[]
    seen=[]
    for item in soup.select('a.block.h-full.w-full'):
        if item['href'].startswith('/product/') and (item['href'] not in seen):
            href=item['href']
            seen.append(href)
            item_url=urljoin(url, href)
            item_urls.append(item_url)
    return item_urls

def get_id(item_url):
    print(item_url)
    HEADERS={'User-Agent': 'my-clothes-scraper/1.0'}
    r =requests.get(item_url, headers=HEADERS, timeout=5)
    html=r.text
    soup=BeautifulSoup(html,'lxml')
    for script in soup.select('script'):
        if 'regular_price' in script.text:
            match=re.search(r'"id":"([A-Za-z0-9]{24})"', script.text.replace('\\',""))
    # print(match.group(1))
    return match.group(1)
        
def get_item_info(product_id):
    print(product_id)
    HEADERS={'User-Agent': 'my-clothes-scraper/1.0'}
    url = f"https://www.coolmate.me/api/proxy/products?ids={product_id}"
    product = requests.get(url, headers=HEADERS, timeout=5).json()["data"][0]
    # with open('json.json', 'w', encoding='utf-8') as f:
    #     json.dump(product, f, ensure_ascii=False, indent=2)
    product_id=product['id']
    try:
        product_code=product['spu']
    except:
        product_code=""
    name=product['title']

    soup=BeautifulSoup(product['body_html'], 'html.parser')
    raw_text=soup.get_text()
    text=re.sub(r'(.*Xem thêm:.*)',"", raw_text)
    desc=re.sub(r'\n+',"\n", text).strip()

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
    video=product['youtube_video']
    images={}
    for dict_0 in product['options_value'][0]['options']:
        urls=[]
        for dict_1 in dict_0['image'][:3]:
            url='https://n7media.coolmate.me/uploads/'+dict_1['src'][7:]
            urls.append(url)
            images[dict_0['title']]=urls
    colorBySize=[]
    for variant in product['variants']:
        if variant['quantity']>0:
            color=variant['option1']
            size=variant['option2']
            colorBySize.append[size+" "+color]
    product_url='https://www.coolmate.me/product/'+ product['seo_alias']

    return {'product_id':product_id,
            'product_code':product_code,
            'name':name,
            'desc':desc,
            'price':price,
            'gender':gender,
            'highlights':highlights,
            'technology':technology,
            'material':material,
            'style':style,
            'usage':usage,
            'features':features,
            'care':care,
            'video':video,
            'images':str(images),
            'colorBySize':str(colorBySize),
            'product_url':product_url
            }
def get_items_data(url):    
    list_=[]
    urls=get_item_urls(url)
    for url in set(urls):
        id=get_id(url)
        dict_=get_item_info(id)
        if dict_["product_code"] != "" :
            list_.append(dict_)
    return list_

def get_faqs_data():
    url='https://www.coolmate.me/page/faqs'
    HEADERS={'User-Agent': 'my-clothes-scraper/1.0'}
    response=requests.get(url,headers=HEADERS, timeout=5)
    soup=BeautifulSoup(response.text, 'lxml')

    list_=[]
    for h3 in soup.find_all('h3'):
        question=h3.get_text(strip=True)

        answers=[]

        for sibling in h3.find_next_siblings():
            if sibling.name in ['h3', 'h2']:
                break
            for a in sibling.find_all('a'):
                a.replace_with(f"{a.get_text(strip=True)} ({a['href']})")
            answer=sibling.get_text(strip=False)
            if 'Covid' in answer:
                continue
            answers.append(answer)
        answers=" ".join(answers)
        list_.append({'question': question, 'answer': answers})
    return list_



# url = f"https://www.coolmate.me/api/proxy/products?ids=6593ee1f9e830a519420fbe4"
# product = requests.get(url).json()["data"][0]
# with open('json.json', 'w', encoding='utf-8') as f:
#     json.dump(product, f, ensure_ascii=False, indent=2)
# images={}
# for dict_0 in product['options_value'][0]['options']:
#     urls=[]
#     for dict_1 in dict_0['image']:
#         url='https://n7media.coolmate.me/uploads/'+dict_1['src'][7:]
#         urls.append(url)
#     images[dict_0['title']]=urls
# print(images)

# HEADERS={'User-Agent': 'my-clothes-scraper/1.0'}
# url = f"https://www.coolmate.me/api/proxy/products?ids=664340520764e2769f636943"
# product = requests.get(url, headers=HEADERS, timeout=5).json()["data"][0]
# with open('json.json', 'w', encoding='utf-8') as f:
#     json.dump(product, f, ensure_ascii=False, indent=2)