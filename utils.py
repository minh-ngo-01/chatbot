import os
import re
import json
import joblib

from google import genai
from google.genai import types
from weaviate.classes.query import Filter
from dotenv import load_dotenv

load_dotenv()

llm_client=genai.Client(api_key=os.getenv('GOOGLE_STUDIO_API_KEY'))

def get_prev_chat():
    chat_history=joblib.load('chat_history.joblib')
    prev_chat='\n'.join(map(str,chat_history))
    return prev_chat

def call_llm(prompt, system_instruction, temperature=0, model='gemini-2.5-flash-lite', include_thoughts=False):
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
               Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
               Tin nhắn hiện tại: {query}"""
    # print(prompt)
    system_instruction='Chỉ trả về một chữ FAQ hoặc Product hoặc Other'    
    response=call_llm(prompt, system_instruction, temperature=1)
    return response.strip().replace("'", "")

def query_faq(client, query, prev_chat):
    faqs=client.collections.get('faqs')
    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng lịch sử trò chuyện.
              Hãy trả về đoạn văn bản tối ưu nhất để thực hiện semantic search trong bộ các câu hỏi faqs.
              Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
              Tin nhắn hiện tại: {query}"""
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
                      Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
                      Tin nhắn hiện tại: {query}
                      Thông tin: {context}"""
    system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến Coolmate. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                                  Giữ câu trả lời ngắn gọn và hữu ích."""
    response=call_llm(prompt, system_instruction, temperature=1)
    # print(prompt)
    return response

def get_metadata(query, prev_chat):
    prompt=f"""Đây là tin nhắn hiện tại của khách hàng cùng với lịch sử trò chuyện. 
            Hãy lọc ra các meta data hữu ích liên quan tới giá, giới tính, 
            và các mã sản phẩm đã được gợi ý trước đó (đã hiển thị cho khách hàng), 
            **nhưng chỉ đối với loại sản phẩm mà khách hàng hiện đang muốn xem thêm.**

            Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
            Tin nhắn hiện tại: {query}

            Trả về kết quả theo mẫu:
            {{
            'price': {{'min': 0, 'max': "inf"}},     # 'max': "inf" nếu khách hàng không đề cập đến giá
            'gender': ['MALE', 'UNISEX'],          # list, possible values: ['MALE', 'FEMALE', 'UNISEX'], hoặc null nếu không nhắc đến
            'shown_product_codes': ['JKZ400', 'TT009', 'SOA102']  # list, trả về null nếu không có
            }}



            **Chú ý:**
            - 'shown_product_codes' là danh sách **các mã sản phẩm đã từng được gợi ý hoặc hiển thị cho khách hàng**, 
            **và thuộc cùng loại sản phẩm mà khách hàng hiện đang muốn xem thêm**.
            - Mục đích là để **loại trừ các sản phẩm này khỏi danh sách gợi ý tiếp theo**, 
            tránh gợi lại các mẫu đã từng hiển thị.
            - Không bao gồm các mã sản phẩm khác loại hoặc chưa từng được gợi ý.
            - Nếu không xác định được loại sản phẩm mà khách hàng muốn xem thêm, hoặc không có sản phẩm trùng loại, trả về null.
""" 
    system_instruction='Chỉ trả về JSON, không gì khác!'
    meta_data=call_llm(prompt, system_instruction, model='gemini-2.5-flash')
    match=re.search(r'{.*}', meta_data, re.DOTALL)
    meta_data=match.group(0)

    # print(meta_data)
    meta_data=json.loads(meta_data)
    return meta_data

def build_filters(meta_data):
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
               Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
               Tin nhắn hiện tại: {query}.
               Hãy trả về đặc điểm của sản phẩm khách hàng đang tìm.
               Ví dụ:
                    Khách hàng: Tôi sắp đi đám cưới, cho tôi bộ quần áo phù hợp.
                    Trả về: Quần áo nam lịch sự, trang trọng để dự tiệc.

                    Khách hàng: Quần áo mặc cho mùa hè.
                    Trả về: Quần áo nam mặc hằng ngày, thấm hút nhanh khô, phù hợp cho các hoạt động ngoài trời.

                    Khách hàng: Áo đi làm.
                    Trả về: Áo nam lịch sự, thoải mái để mặc cả ngày, phù hợp để đi làm văn phòng.
               Hỏi khách hàng thêm thông tin nếu cần thiết.
               """
    # print(prompt)
    system_instruction='Chỉ trả về đoạn văn bản dùng để tìm kiếm hoặc câu hỏi thêm thông tin khách hàng, không gì khác!'
    augmented_query=call_llm(prompt, system_instruction, temperature=1)
    if '?' in augmented_query:
        return augmented_query
    print(augmented_query)
    
    meta_data=get_metadata(query, prev_chat)
    print(meta_data)

    filters=build_filters(meta_data)
    # filters=[]
    # limit=get_litmit(query, prev_chat)
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
    # print(context)

    prompt=f""" Bạn sẽ nhận tin nhắn hiện tại và lịch sử trò chuyện cùng với thông tin chi tiết các sản phẩm liên quan.
                Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
                Tin nhắn hiện tại: {query}
                Thông tin sản phẩm: {context}
                Không đề cấp đến số lượng hàng tồn.
                Gắn hình ảnh bằng tag <img src="http:\\ ..." width=300>.
                Đính kèm mã sản phẩm.
                Nếu vẫn đang trong một cuộc trò chuyện thì chỉ trả lời, không chào lại."""
    system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến Coolmate. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                                  Giữ câu trả lời ngắn gọn và hữu ích."""

    response=call_llm(prompt, system_instruction, temperature=1)
    return response


def query_other(query, prev_chat):
    prompt=f"""Bạn sẽ nhận tin nhắn hiện tại và lịch sử trò chuyện.
              Các tin nhắn trước đó từ cũ tới mới nhất: {prev_chat}
              Tin nhắn hiện tại: {query}"""
    
    system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến Coolmate. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                          Giữ câu trả lời ngắn gọn và hữu ích."""
    # print(prompt)
    response=call_llm(prompt, system_instruction)
    return response
