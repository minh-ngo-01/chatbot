from weaviate_setup import initialize_products_collection, populate_products_collection
from web_scraper import get_items_data, get_faqs_data
from weaviate_setup import initialize_faqs_collection, populate_faqs_collection
from google import genai
from google.genai import types
import joblib
import tqdm



def classify_query(query):
    chat_history=joblib.load('chat_history.joblib')
    prev_chat=""
    for chat in chat_history[-5:]:
        prev_chat+=str(chat)
        prev_chat+='\n'

    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện.
              Hãy tóm tắt ý định hiện tại của khách hàng.
              Tóm tắt này sẽ được sử dụng thực hiện việc phân loại ý định là về FAQs, sản phẩm hoặc chủ đề khác.
              Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
              Tin nhắn hiện tại: {query}"""
    # print(prompt)
    client=genai.Client(api_key='AIzaSyAYioiyAlQFNZih4qJZdaM6N1xnkF5yj2A')
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)),
        contents=prompt)
    augmented_query=response.text
    # print(augmented_query)

    response=client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""Phân loại ý định sau của khách hàng là FAQ, Product hoặc Others.
                   Trả về FAQ nếu ý định đó liên quan đến các câu hỏi FAQs.
                   Trả về Product nếu ý định đó liên quan đến sản phẩm.
                   Trả về Other nếu không phải về FAQ hay Product.
                   Chỉ trả về 'FAQ, 'Product' hoặc 'Other'. Không gì khác!
                   Ý định:{augmented_query}""",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ))
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
              Hãy trả về đoạn văn bản tối ưu nhất để thực hiện sematic search trong bộ các câu hỏi faqs.
              Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
              Tin nhắn hiện tại: {query}"""
    # print(prompt)

    response=client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                                  Chỉ chào người dùng một lần, ở đầu cuộc trò chuyện.
                                  Giữ câu trả lời ngắn gọn và hữu ích.
                                  Nếu người dùng đặt câu hỏi tiếp theo, hãy tiếp tục cuộc trò chuyện mà không lặp lại lời chào hay phần giới thiệu."""),
        contents=prompt)
    augmented_query=response.text
    # print(augmented_query)
    
    
    
    response=faqs.query.near_text(query, limit=3)

    context=""
    for res in response.objects:
        context+=f"Question: {res.properties['question']} Answer: {res.properties['answer']}\n"
    
    client=genai.Client(api_key='AIzaSyAYioiyAlQFNZih4qJZdaM6N1xnkF5yj2A')
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                                  Chỉ chào người dùng một lần, ở đầu cuộc trò chuyện.
                                  Giữ câu trả lời ngắn gọn và hữu ích.
                                  Nếu người dùng đặt câu hỏi tiếp theo, hãy tiếp tục cuộc trò chuyện mà không lặp lại lời chào hay phần giới thiệu."""),
        
        
        
        contents=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện.
                      Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
                      Tin nhắn hiện tại: {query}
                      Thông tin: {context}"""
                    )
    return response.text


    
def query_product(client, query):
    if not client.collections.exists('products'):
        products=initialize_products_collection(client)
        urls=['https://www.coolmate.me/collection/ao-ba-lo-tank-top-nam',
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
    
    chat_history=joblib.load('chat_history.joblib')

    prev_chat=""
    for chat in chat_history[-5:]:
        prev_chat+=str(chat)
        prev_chat+='\n'

    prompt=fprompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện. 
                       Hãy trả về đoạn văn bản tối ưu nhất để thực hiện sematic search trong bộ dự liệu thông tin sản phẩm.
                       Bạn có thể tự nghĩ ra văn bản mới để tìm cho ra sản phẩm phù hợp nhất.
                       Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
                       Tin nhắn hiện tại: {query}"""
    print(prompt)

    response=client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            system_instruction='Nhiệm vụ của bạn liên quan đến một cửa hàng thời trang online'),
        contents=prompt)
    augmented_query=response.text
    print(augmented_query)

    response=products.query.near_text(query=augmented_query, limit=5)
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
                Phản hồi hình ảnh bằng tag img. Điều chỉnh kích thước ảnh sao cho nội dung được hiển thị đẹp nhất."""
    
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                                  Chỉ chào người dùng một lần, ở đầu cuộc trò chuyện.
                                  Giữ câu trả lời ngắn gọn và hữu ích.
                                  Nếu người dùng đặt câu hỏi tiếp theo, hãy tiếp tục cuộc trò chuyện mà không lặp lại lời chào hay phần giới thiệu."""),
        contents=prompt)
    # print(response.text)
    return response.text


def query_other(query):
    chat_history=joblib.load('chat_history.joblib')

    prev_chat=""
    for chat in chat_history[-5:]:
        prev_chat+=str(chat)
        prev_chat+='\n'
    
    client=genai.Client(api_key='AIzaSyAYioiyAlQFNZih4qJZdaM6N1xnkF5yj2A')
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                                  Chỉ chào người dùng một lần, ở đầu cuộc trò chuyện.
                                  Giữ câu trả lời ngắn gọn và hữu ích.
                                  Nếu người dùng đặt câu hỏi tiếp theo, hãy tiếp tục cuộc trò chuyện mà không lặp lại lời chào hay phần giới thiệu."""),
        contents=f""" Bạn sẽ nhận tin nhắn hiện tại và lịch sử trò chuyện.
                      Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
                      Tin nhắn hiện tại: {query}""")
    return response.text