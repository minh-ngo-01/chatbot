import os
import re
import json
import joblib

from google import genai
from google.genai import types
from weaviate.classes.query import Filter
from dotenv import load_dotenv


# import phoenix as px
# from phoenix.otel import register
# from opentelemetry.trace import Status, StatusCode
# px.launch_app(use_temp_dir=False)
# phoenix_name= "chatbot"
# endpoint="http://127.0.0.1:6006/v1/traces"
# tracer_provider_phoenix=register(project_name=phoenix_name, endpoint=endpoint)
# tracer=tracer_provider_phoenix.get_tracer(__name__)



load_dotenv()

llm_client=genai.Client(api_key=os.getenv('GOOGLE_STUDIO_API_KEY'))

def get_prev_chat(chat_history,n=5):
    try:
        recent_message=str(chat_history[-1])
    except:
        recent_message=""
    old_messages='\n'.join(map(str,chat_history[-n:-1]))
    return [old_messages, recent_message]

def call_llm(prompt, system_instruction, temperature=0, model='gemini-2.5-flash-lite', include_thoughts=False, stream=False):
    # if stream==True:
    #     response=llm_client.models.generate_content_stream(
    #     model=model,
    #     config=types.GenerateContentConfig(system_instruction=system_instruction,
    #         thinking_config=types.ThinkingConfig(include_thoughts=include_thoughts),
    #         temperature=temperature),
    #     contents=prompt)
    #     return response
    #     for chunk in response:
    #         yield chunk.text



    response=llm_client.models.generate_content(
        model=model,
        config=types.GenerateContentConfig(system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(include_thoughts=include_thoughts),
            temperature=temperature),
        contents=prompt)
    return response.text


def classify_query(query, prev_chat):
    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện.
               Xem xét lịch sử trò chuyên cùng tin nhắn hiện tại để xác định ý định của khách hàng.
               Trả về FAQ nếu ý định đó liên quan đến các câu hỏi FAQs.
               Trả về Product nếu ý định đó liên quan đến sản phẩm.
               Trả về Other nếu không phải về FAQ hay Product.
               Tin nhắn trước đó:{prev_chat[-2]}.
               Tin nhắn ngay trước đó: {prev_chat[-1]}.
               Tin nhắn hiện tại: '{query}'"""
    print(prompt)
   
    system_instruction='Chỉ trả về một chữ FAQ hoặc Product hoặc Other'    
    response=call_llm(prompt, system_instruction, temperature=1)
    return response.strip().replace("'", "")

def query_faq(client, query, prev_chat):
    faqs=client.collections.get('faqs')
    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng lịch sử trò chuyện.
              Hãy trả về đoạn văn bản tối ưu nhất để thực hiện semantic search trong bộ các câu hỏi faqs.
              Tin nhắn trước đó:{prev_chat[-2]}.
              Tin nhắn ngay trước đó: {prev_chat[-1]}.
              Tin nhắn hiện tại: '{query}'"""
    system_instruction="""Bạn là một trợ lý ảo trò chuyện của cửa hàng quần áo trực tuyến Coolmate. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                                  Giữ câu trả lời ngắn gọn và hữu ích."""
    # print(prompt)
    
    response=call_llm(prompt, system_instruction)
    augmented_query=response
    # print(augmented_query)

    
    response=faqs.query.near_text(augmented_query, limit=3)

    context=""
    for res in response.objects:
        context+=f"Question: {res.properties['question']} Answer: {res.properties['answer']}\n"

    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện.
                      Tin nhắn trước đó:{prev_chat[-2]}.
                      Tin nhắn ngay trước đó: {prev_chat[-1]}.
                      Tin nhắn hiện tại: '{query}'.
                      Thông tin: {context}"""
    system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến Coolmate. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                                  Giữ câu trả lời ngắn gọn và hữu ích."""
    response=call_llm(prompt, system_instruction, temperature=1)
    # print(prompt)
    return response
### if the customer want to see more samples of the recommended

def get_shown_codes(query, prev_chat):
    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện. 
    Tin nhắn trước đó:{prev_chat[-2]}.
    Tin nhắn ngay trước đó: {prev_chat[-1]}.
    Tin nhắn hiện tại: '{query}'.
    Nếu khách hàng muốn xem thêm mẫu khác của loại sản phẩm trước đó, trả về True.
    Nếu khách hàng muốn xem loại sản phẩm khác, trả về False.
    Trả về sản phẩm khách hàng muốn xem thêm.
    Trả về file JSON theo mẫu sau:
    Mẫu: 
    {{ 'see_more': true
       'product': "Áo khoác" 
    }}
    """  
    # print(prompt)
    system_instruction='Chỉ trả về JSON, không gì khác!'
    response=call_llm(prompt, system_instruction)
    # print(response)
    match=re.search(r'{.*}', response, re.DOTALL)
    meta_data=match.group(0)
    meta_data=json.loads(meta_data)
    print(meta_data)
    if meta_data['see_more']==True:

        prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện. 
        Tin nhắn trước đó:{prev_chat[-2]}.
        Tin nhắn ngay trước đó: {prev_chat[-1]}.
        Tin nhắn hiện tại: '{query}'.
        Trả về một list tất cả mã sản phẩm {meta_data['product']} đã gửi cho khách hàng.
        Mẫu: [JKZ400,TT009,SOA102]
        """  
        system_instruction='Chỉ trả về một list, không gì khác!'
        response=call_llm(prompt, system_instruction)
        # print(response)
        return [char.strip().strip("\"").strip("\'") for char in response.strip("[]").split(',')]
    return False


def get_metadata(query, prev_chat):
    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện. 
            Hãy lọc ra các meta data hữu ích liên quan tới giá, giới tính.

            Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
            Tin nhắn hiện tại: {query}

            Trả về kết quả theo mẫu:
            {{
            "price": {{"min": 0, "max": "inf"}},     # "max": "inf" nếu khách hàng không đề cập đến giá
            "gender": ["MALE", "UNISEX"],          # possible values: ['MALE', 'FEMALE', 'UNISEX'], hoặc null nếu không nhắc đến
            }}            
            """ 
    system_instruction='Chỉ trả về JSON, không gì khác!'
    response=call_llm(prompt, system_instruction, model='gemini-2.5-flash')
    # print(response)
    match=re.search(r'{.*}', response, re.DOTALL)
    meta_data=match.group(0)


    # print(meta_data)
    meta_data=json.loads(meta_data)
    return meta_data


def build_filters(meta_data, shown_codes):
    filters=[]
    for key, value in meta_data.items():
        if value==None:
            continue
        elif key=='price' and value['max'] != 'inf':                          
            filters.append(Filter.by_property(key).greater_than(value['min']))
            filters.append(Filter.by_property(key).less_than(value['max']))
        elif key=='gender':
            filters.append(Filter.by_property('gender').contains_any(value))
    if shown_codes:
        filters.append(Filter.by_property('product_code').contains_none(shown_codes))
    return filters


def get_litmit(query, prev_chat):
    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng lịch sử trò chuyện.
            Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
            Tin nhắn hiện tại: {query}
            Bạn hãy trả về số lượng sản phẩm nên được lấy thông tin trong vector databse để trả lời khách hàng.
            Trả về 0 nếu không cần lấy thêm thông tin"""
    system_instruction='Chỉ trả về số tự nhiên trong khoảng từ 0 tới 20'
    response=call_llm(prompt, system_instruction)
    print(response)
    return int(response)

    
def query_product(client, query, prev_chat):   
    
    # client.collections.delete('products')
    products=client.collections.get('products')

    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện. 
            Tin nhắn trước đó:{prev_chat[-2]}.
            Tin nhắn ngay trước đó: {prev_chat[-1]}.
            Tin nhắn hiện tại: '{query}'.
            Hãy trả về đặc điểm của sản phẩm khách hàng đang tìm.
            Ví dụ:
                    Khách hàng: Tôi sắp đi đám cưới, cho tôi bộ quần áo phù hợp.
                    Trả về: Quần áo nam lịch sự, trang trọng để dự tiệc.

                    Khách hàng: Quần áo mặc cho mùa hè.
                    Trả về: Quần áo nam mặc hằng ngày, thấm hút nhanh khô, phù hợp cho các hoạt động ngoài trời.

                    Khách hàng: Áo đi làm.
                    Trả về: Áo nam lịch sự, thoải mái để mặc cả ngày, phù hợp để đi làm văn phòng.
            Hỏi thêm khách hàng nếu cần thiết.
            """
    # print(prompt)
    with open('text.text', 'w', encoding='utf-8') as f:
        f.write(prompt)
    system_instruction='Chỉ trả về đoạn văn bản dùng để tìm kiếm hoặc câu hỏi thêm thông tin khách hàng, không gì khác!'
    augmented_query=call_llm(prompt, system_instruction, temperature=1)

    if '?' in augmented_query:
        return augmented_query
    print(augmented_query)
    
    meta_data=get_metadata(query, prev_chat)
    print(meta_data)
    shown_codes=get_shown_codes(query, prev_chat)
    print(shown_codes)
    filters=build_filters(meta_data, shown_codes)
    # filters=[]
    
    context=""
    
    response=products.query.near_text(query=augmented_query, filters=Filter.all_of(filters) if len(filters) != 0 else None, limit=3)
    context=""
    for res in response.objects:
        context+=f"""mã sản phẩm: {res.properties['product_code']},
                    tên sản phẩm:{res.properties['name']},                     
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
                    mô tả: {res.properties['desc']},
                    tồn kho theo kích thước và màu: {res.properties['storage']},
                    link sản phẩm:{res.properties['product_url']}/n"""
    
    with open('context.txt', 'w', encoding='utf-8') as f:
        f.write(context)

    prompt=f""" Bạn sẽ nhận tin nhắn hiện tại và lịch sử trò chuyện cùng với thông tin chi tiết các sản phẩm liên quan.
                Tin nhắn trước đó:{prev_chat[-2]}.
                Tin nhắn ngay trước đó: {prev_chat[-1]}.
                Tin nhắn hiện tại: '{query}'.
                Thông tin sản phẩm: {context}
                Không đề cấp đến số lượng hàng tồn.
                Gắn hình ảnh bằng tag <img src="http:\\ ..." width=300>.
                Đính kèm mã sản phẩm."""
    system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến Coolmate. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                            Giữ câu trả lời ngắn gọn và hữu ích.
                            Nếu vẫn đang trong một cuộc trò chuyện thì chỉ trả lời, không chào lại."""

    response=call_llm(prompt, system_instruction, temperature=1)
    
    
    
    return response


def query_other(query, prev_chat):
    prompt=f"""Bạn sẽ nhận tin nhắn hiện tại và lịch sử trò chuyện.
              Tin nhắn trước đó:{prev_chat[-2]}.
              Tin nhắn ngay trước đó: {prev_chat[-1]}.
              Tin nhắn hiện tại: '{query}'."""
    
    system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến Coolmate. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                          Giữ câu trả lời ngắn gọn và hữu ích."""
    # print(prompt)
    response=call_llm(prompt, system_instruction)
    return response
