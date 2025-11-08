from weaviate_setup import initialize_products_collection, populate_products_collection
from web_scraper import get_items_data, get_faqs_data
from weaviate_setup import initialize_faqs_collection, populate_faqs_collection
from google import genai
from google.genai import types
import joblib
import tqdm
import json
from weaviate.classes.query import Filter
import re



def classify_query(query):
    chat_history=joblib.load('chat_history.joblib')
    prev_chat=""
    for chat in chat_history[-5:]:
        prev_chat+=str(chat)
        prev_chat+='\n'

    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện.
               Phân loại tin nhắn hiện tại của khách hàng liên quan tới FAQs, sản phẩm hoặc gì khác.
               Trả về FAQ nếu ý định đó liên quan đến các câu hỏi FAQs.
               Trả về Product nếu ý định đó liên quan đến sản phẩm.
               Trả về Other nếu không phải về FAQ hay Product.
               Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
               Tin nhắn hiện tại: {query}"""
    # print(prompt)
    client=genai.Client(api_key='AIzaSyAYioiyAlQFNZih4qJZdaM6N1xnkF5yj2A')
    response=client.models.generate_content(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(system_instruction='Chỉ trả về một chữ FAQ hoặc Product hoặc Other',
            thinking_config=types.ThinkingConfig(include_thoughts=False),
            temperature=0),
        contents=prompt)
    return response.text.strip().replace("'", "")

def query_faq(client, query):
    if not client.collections.exists('faqs'):
        faqs=initialize_faqs_collection(client)
        faqs_data=get_faqs_data()
        faqs=populate_faqs_collection(faqs, faqs_data)
    else:
        faqs=client.collections.get('faqs')
    
    chat_history=joblib.load('chat_history.joblib')

    prev_chat=""
    for chat in chat_history[-5:]:
        prev_chat+=str(chat)
        prev_chat+='\n'

    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng lịch sử trò chuyện.
              Hãy trả về đoạn văn bản tối ưu nhất để thực hiện semantic search trong bộ các câu hỏi faqs.
              Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
              Tin nhắn hiện tại: {query}"""
    # print(prompt)
    client=genai.Client(api_key='AIzaSyAYioiyAlQFNZih4qJZdaM6N1xnkF5yj2A')
    response=client.models.generate_content(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(include_thoughts=False),
            temperature=0,
            system_instruction="""Bạn là một trợ lý ảo trò chuyện của cửa hàng quần áo trực tuyến Coolmate. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                                  Giữ câu trả lời ngắn gọn và hữu ích."""),
        contents=prompt)
    augmented_query=response.text
    # print(augmented_query)

    
    response=faqs.query.near_text(query, limit=3)

    context=""
    for res in response.objects:
        context+=f"Question: {res.properties['question']} Answer: {res.properties['answer']}\n"
    
    client=genai.Client(api_key='AIzaSyAYioiyAlQFNZih4qJZdaM6N1xnkF5yj2A')
    response=client.models.generate_content(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            temperature=0,
            system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến Coolmate. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                                  Giữ câu trả lời ngắn gọn và hữu ích."""),
        contents=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện.
                      Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
                      Tin nhắn hiện tại: {query}
                      Thông tin: {context}"""
                    )
    return response.text


    
def query_product(client, query):   
    # client.collections.delete('products')
    
    if not client.collections.exists('products'):
        products=initialize_products_collection(client)
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
        for url in tqdm.tqdm(urls):
            product_data=get_items_data(url)
            products=populate_products_collection(products, product_data)
    else:
        products=client.collections.get('products')

    client=genai.Client(api_key='AIzaSyAYioiyAlQFNZih4qJZdaM6N1xnkF5yj2A')
    
    chat_history=joblib.load('chat_history.joblib')

    prev_chat=""
    for chat in chat_history[-5:]:
        prev_chat+=str(chat)
        prev_chat+='\n'

    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện. 
               Hãy trả về đoạn văn bản tối ưu nhất để thực hiện semantic search trong bộ dữ liệu thông tin sản phẩm.
               Bạn có thể tự nghĩ ra văn bản mới để tìm cho ra sản phẩm phù hợp nhất.
               Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
               Tin nhắn hiện tại: {query}."""
    # print(prompt)

    response=client.models.generate_content(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            temperature=0,
            system_instruction='Chỉ trả về đoạn văn bản dùng để tìm kiếm, không gì khác!'),
        contents=prompt)
    augmented_query=response.text
    print(augmented_query)

    
    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện. 
               Hãy lọc ra các meta data hữu ích liên quan tới giá, giới tính và những mã sản phẩm đã gợi ý cho khách hàng.
               Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
               Tin nhắn hiện tại: {query}
               Mẫu: 
               {{
              'price': {{'min': 0, 'max': "inf"}} 'max':"inf" nếu không đề cập về giá.
              'gender': ['MALE', 'UNISEX'] (possible values in:['MALE', 'FEMALE', 'UNISEX',]) nếu không đề cập đến giới tính, trả về null
              'shown_product_codes': ['JKZ400', 'TT009','SOA102'] trả về null nếu cần.
              }} """

    response=client.models.generate_content(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            temperature=0,
            system_instruction='Chỉ trả về JSON, không gì khác!'),
        contents=prompt)
    
    meta_data= response.text    

    match=re.search(r'{.*}', meta_data, re.DOTALL)
    meta_data=match.group(0)
    # print(meta_data)
    meta_data=json.loads(meta_data)
    print(meta_data)
    
    
    filters=[]
    for key, value in meta_data.items():
        if value==None:
            continue
        elif key=='price' and value['max'] != 'inf':                          
            filters.append(Filter.by_property(key).greater_than(value['min']))
            filters.append(Filter.by_property(key).less_than(value['max']))
            # print(value['max'])
        elif key=='shown_product_codes':
            filters.append(Filter.by_property('product_code').contains_none(value))
        elif key=='gender':
            filters.append(Filter.by_property('gender').contains_any(value))

    # prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng lịch sử trò chuyện.
    #           Bạn hãy trả về số lượng sản phẩm nên được lấy thông tin trong vector databse để trả lời khách hàng.
    #           Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
    #           Tin nhắn hiện tại: {query}"""
    

    # response=client.models.generate_content(
    #     model="gemini-2.5-flash",
    #     config=types.GenerateContentConfig(
    #         thinking_config=types.ThinkingConfig(thinking_budget=0),
    #         system_instruction='Chỉ trả về số tự nhiên trong khoảng từ 1 tới 20'),
    #     contents=prompt)
    # limit=int(response.text)
    # print(limit)
    # filters=[]
    response=products.query.near_text(query=augmented_query, filters=Filter.all_of(filters) if len(filters) != 0 else None, limit=5)
    
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
    # print(context)

    prompt=f""" Bạn sẽ nhận tin nhắn hiện tại và lịch sử trò chuyện cùng với thông tin chi tiết các sản phẩm liên quan.
                Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
                Tin nhắn hiện tại: {query}
                Thông tin sản phẩm: {context}
                Không đề cấp đến số lượng hàng tồn.
                Gắn hình ảnh bằng tag <br><img src="http:\\ ..." width=300><br>.
                Đính kèm mã sản phẩm.
                Nếu vẫn đang trong một cuộc trò chuyện thì chỉ trả lời, không chào lại."""
    
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            temperature=0,
            system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến Coolmate. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                                  Giữ câu trả lời ngắn gọn và hữu ích."""),
        contents=prompt)

    return response.text


def query_other(query):
    chat_history=joblib.load('chat_history.joblib')

    prev_chat=""
    for chat in chat_history[-5:]:
        prev_chat+=str(chat)
        prev_chat+='\n'
    
    client=genai.Client(api_key='AIzaSyAYioiyAlQFNZih4qJZdaM6N1xnkF5yj2A')
    response=client.models.generate_content(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            temperature=0,
            system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến Coolmate. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                                  Giữ câu trả lời ngắn gọn và hữu ích."""),
        contents=f""" Bạn sẽ nhận tin nhắn hiện tại và lịch sử trò chuyện.
                      Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
                      Tin nhắn hiện tại: {query}""")
    return response.text


# urls=[         
#             #   'https://www.coolmate.me/collection/ao-ba-lo-tank-top-nam',
#             #   'https://www.coolmate.me/collection/ao-thun-nam',
#             #   'https://www.coolmate.me/collection/ao-nam-choi-the-thao',
#             #   'https://www.coolmate.me/collection/ao-polo-nam',
#             #   'https://www.coolmate.me/collection/ao-so-mi-nam',
#             #   'https://www.coolmate.me/collection/ao-nam-dai-tay',
#             #   'https://www.coolmate.me/collection/ao-sweater-len-ni-nam',
#             #   'https://www.coolmate.me/collection/ao-khoac-nam',
#             #   'https://www.coolmate.me/collection/quan-short-nam',
#             #   'https://www.coolmate.me/collection/quan-jogger-nam',
#             #   'https://www.coolmate.me/collection/quan-nam-choi-the-thao',
#             #   'https://www.coolmate.me/collection/quan-dai-nam',
#               'https://www.coolmate.me/collection/quan-pants-nam',
#               'https://www.coolmate.me/collection/quan-jeans-nam',
#               'https://www.coolmate.me/collection/quan-kaki-nam',
#               'https://www.coolmate.me/collection/do-boi-nam',
#               'https://www.coolmate.me/collection/quan-tam-giac-brief',
#               'https://www.coolmate.me/collection/quan-boxer-trunk',
#               'https://www.coolmate.me/collection/quan-boxer-brief-dang-dai',
#               'https://www.coolmate.me/collection/quan-long-leg',
#               'https://www.coolmate.me/collection/quan-boxer-shorts',
#               'https://www.coolmate.me/collection/phu-kien-nam'] 

# import os
# from weaviate.classes.init import Auth
# import weaviate
# from web_scraper import get_item_info
# from dotenv import load_dotenv
# load_dotenv()
# weaviate_url=os.getenv('WEAVIATE_URL')
# weaviate_api_key=os.getenv('WEAVIATE_API_KEY')
# with weaviate.connect_to_weaviate_cloud(
#     cluster_url=weaviate_url,
#     auth_credentials=Auth.api_key(weaviate_api_key)
#     ) as client:
#     # client.collections.delete('products')
#     # products=initialize_products_collection(client)
#     products=client.collections.get('products')
#     for url in tqdm.tqdm(urls):
#         product_data=get_items_data(url)
#         products=populate_products_collection(products, product_data)