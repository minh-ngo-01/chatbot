from weaviate_setup import initialize_products_collection, populate_collection
from web_scraper import get_items_data
from weaviate_setup import get_faqs_collection
from google import genai
from google.genai import types

def classify_query(query):
    client=genai.Client(api_key='AIzaSyAPKfxC3j_VP-uVkCp-LONlNGsnNbn_RAA')
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""Phân loại yêu cầu/câu hỏi sau của khách hàng là FAQ hoặc Product.
                   Trả về FAQ nếu yêu cầu/câu hỏi đó liên quan đến các câu hỏi FAQ.
                   Trả về Product nếu yêu cầu/câu hỏi đó liên quan đến sản phẩm.
                Chỉ trả về 'FAQ' hoặc 'Product'. Không gì khác!
                Yêu cầu/câu hỏi:{query}""",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ))
    return response.text.strip().replace("'", "")



def query_faq(client, query):

    faqs=get_faqs_collection(client)
    response=faqs.query.near_text(query, limit=3)

    context=""
    for res in response.objects:
        context+=f"Question: {res.properties['question']} Answer: {res.properties['answer']}\n"
    
    client=genai.Client(api_key='AIzaSyAPKfxC3j_VP-uVkCp-LONlNGsnNbn_RAA')
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            system_instruction='Bạn là nhân viên của cửa hàng quần áo'),
        contents=""" Trả lời câu hỏi sau bằng cách chỉ sử dụng thông tin được cung cấp:
                    Câu hỏi: {query}
                    Thông tin: {context}""")
    return response.text


    
def query_product(client, query):

    if not client.collections.exists('products'):
        products=initialize_products_collection(client)
        url='https://www.coolmate.me/collection/do-nam'
        product_data=get_items_data(url)
        products=populate_collection(collection, product_data)
    else:
        products=client.collections.get('products')

    client=genai.Client(api_key='AIzaSyAPKfxC3j_VP-uVkCp-LONlNGsnNbn_RAA')

    # prompt=f""" Base on the query given, extract the useful metadata to search relevat clothing items.
    #         the metadata includes 'gender', 'colour' and 'price'.
    #         Just return JSON object, nothing else.
    #         {{
    #         'gender': ['Men'] (possible values in:['Men', 'Women'])
    #         'baseColour': ['Black'] (possible values in: [{" , ".join([color for color in possible_color if type(color)==str])}] if not mentioned, leave None
    #         'price': {{'min': 0, 'max': 1000}} if not mentioned, leave None
    #         }} 
    #         Here is the query: {query}.

    #         """
    # completion=client.chat.completions.create(
    #         model='openai/gpt-oss-20b:groq',
    #         messages=[{'role':'user',"content":prompt}])
    # meta_data= completion.choices[0].message.content

    # print(meta_data)
    # import json
    # meta_data=json.loads(meta_data)
    # from weaviate.classes.query import Filter
    # filters=[]
    # for key, value in meta_data.items():
    #     if value==None:
    #         continue
    #     elif key=='price':
    #         if value['min']<0:
    #             continue        
            
    #         filters.append(Filter.by_property(key).greater_than(value['min']))
    #         filters.append(Filter.by_property(key).less_than(value['max']))
    #     else:
    #         filters.append(Filter.by_property(key).contains_any(value))
    # response=products.query.near_text(query=query,filters=Filter.all_of(filters) if len(filters) != 0 else None, limit=5)
    response=products.query.near_text(query=query, limit=5)
    context=""
    for res in response.objects:
        context+=f"""mã sản phẩm: {res.properties['product_code']},
                     tên sản phẩm:{res.properties['name']},
                     mô tả ngắn: {res.properties['short_desc']},
                     giá: {res.properties['price']},
                     giới tính: {res.properties['gender']},
                     nổi bât: {res.properties['highlights']},
                     công nghệ: {res.properties['technology']},
                     vật liệu: {res.properties['material']},
                     kiểu dáng: {res.properties['style']},
                     phù hợp: {res.properties['usage']},
                     tính năng: {res.properties['features']},
                     bảo quản: {res.properties['care']},
                     hình ảnh: {res.properties['images']},
                     tồn kho theo kích thường và màu: {res.properties['storage']},
                     link sản phẩm:{res.properties['product_url']}/n"""
    
    prompt=f""" Bạn sẽ nhận yêu cầu hoặc câu hỏi từ khác hàng cũng với thông tin chi tiết các sản phẩm liên quan, trả lời như là một nhân viên cửa hàng.
                yêu cầu/ câu hỏi: {query}.
                thông tin sản phẩm: {context}.
                Phản hồi hình ảnh theo mẫu sau: <img src= alt=" width="200">."""
    
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            system_instruction='Bạn là nhân viên của một cửa hàng quần áo'),
        contents=prompt)
    return response.text