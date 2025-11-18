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

def get_prev_chat(n=5):
    try:
        chat_history=joblib.load('chat_history.joblib')
    except:
        chat_history=[]        
    prev_chat='\n'.join(map(str,chat_history[-5:]))
    return prev_chat


def call_llm(prompt, system_instruction, temperature=0, model='gemini-2.5-flash-lite', include_thoughts=False, stream=False):
    response=llm_client.models.generate_content(
        model=model,
        config=types.GenerateContentConfig(system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(include_thoughts=include_thoughts),
            temperature=temperature),
        contents=prompt)
    return response.text


def classify_query(query, prev_chat, previous_intent):
    prompt=f"""Bạn sẽ nhận:
            - lịch sử trò chuyện giữa bạn và khách hàng.
            - ý định trước đó của khách hàng
            - tin nhắn hiện tại.

            Nhiệm vụ:
            - mô tả chi tiết ý định của khách hàng, cụ thể về mẫu sản phẩm, loại sản phẩm và đặc điểm sản phẩm nếu có.
            - phân loại ý định đó theo 3 chủ đề gồm: Product(sản phẩm)/Delivery(giao hàng)/Other(chủ đề khác)
            Trả vê một JSON.

            Ví dụ: 
              Lịch sử trò chuyện: {{'time': 'Sun Nov 16 07:52:30 2025', 'customer': 'các mẫu áo thun nam', 'bot': 'Tuyệt vời! Bạn đang tìm áo thun nam đúng không? Coolmate có mấy mẫu này rất được ưa chuộng nè:\n\n**1. Áo Thun Nam Cotton 220GSM Basics (TSZ959)**\n<img src="https://n7media.coolmate.me/uploads/February2025/ao-thun-nam-cotton-220gsm-mau-nau-cappuccino_(7).jpg" width=300>\nChất liệu 100% Cotton Úc dày dặn, mềm mịn, thấm hút tốt. Form Regular Fit mặc lên cực thoải mái, có đến 12 màu tha hồ lựa chọn nha. Giá chỉ 159.000đ.\n\n**2. Áo Thun Nam Chạy Bộ Graphic Heartbeat (TSZ877)**\n<img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-hong-5.jpg" width=300>\nSiêu nhẹ, nhanh khô và co giãn 4 chiều, cực hợp cho những ai mê vận động. Đặc biệt có logo phản quang giúp an toàn hơn khi tập luyện buổi tối. Giá cũng là 159.000đ.\n\n**3. Áo Thun Nam Thể Thao Coolmate Basics (TSZ916)**\n<img src="https://n7media.coolmate.me/uploads/September2025/ao-the-thao-nam-promax-recycle-basics1-hong-marsala-1_10.jpg" width=300>\nĐây là dòng sản phẩm Recycle Basics, vừa thân thiện môi trường, vừa siêu nhẹ, thấm hút và khô nhanh. Giá mềm hơn, chỉ 99.000đ.\n\nBạn ưng mẫu nào hay muốn xem thêm màu sắc của mẫu nào không?'}}
              Tin nhắn hiện tại: mẫu thứ 2 có những màu nào?
              Trả về:
              {{"intent":" cần thêm thông tin về màu sắc Áo Thun Nam Chạy Bộ Graphic Heartbeat (TSZ877)",
               "topic": "Product"}}

              Lịch sử trò chuyện: {{'time': 'Sun Nov 16 16:00:00 2025', 'customer': 'mẫu áo thun cho nam, dưới 200k', 'bot': 'Ok bạn ơi, đây là mẫu Áo Thun Nam Cotton 220GSM này, giá chỉ 159k thôi nè. Chất cotton dày dặn, mặc thoải mái lắm nha. Bạn xem thử có ưng màu nào không nè:\n\n<img src="https://n7media.coolmate.me/uploads/February2025/ao-thun-nam-cotton-220gsm-mau-nau-cappuccino_(7).jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/February2025/ao-thun-nam-cotton-220gsm-mau-xam-castlerock_(8).jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/February2025/ao-thun-nam-cotton-220gsm-mau-hong-peach-whip_(7).jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/October2024/AT.220_-_Do_1.1.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.den6.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.xd.3.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.be.1.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.den14.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.NAU.1.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/June2025/ao-thun-nam-cotton-220gsm-xanh-reu-1111.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.mint1.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.xam1.jpg" width=300>\n\nMã sản phẩm: TSZ959'}}
                                  {{'time': 'Sun Nov 16 16:00:20 2025', 'customer': 'mẫu khác nha', 'bot': 'Ok bạn ơi, mình có mẫu Áo Thun Chạy Bộ Graphic Heartbeat này, giá cũng 159k nè, có nhiều màu xinh lắm:\n<img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-hong-5.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-tim-2.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-den-3.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-xanh-reu-3_60.jpg" width=300>\n\nMã sản phẩm: TSZ877\n\nNgoài ra còn có Áo singlet chạy bộ nam "Việt Nam tiến bước" giá 109k, siêu nhẹ và thoáng mát nè:\n<img src="https://n7media.coolmate.me/uploads/August2025/ao-singlet-chay-bo-nam-viet-nam-tien-buoc-18-do_76.jpg" width=300>\nMã sản phẩm: 25CM.MAWRU.TTA484\n\nBạn thích mẫu nào hơn nè?'}}
              Tin nhắn hiện tại: mẫu khác
              Trả về:
               {{"intent":"tìm mẫu áo thun nam khác dưới 200k",
               "topic": "Poroduct"}}

              Lịch sử trò chuyện: ""
              Tin nhắn hiện tại: Khi nào cửa hàng mình mở cửa?
              Trả về:
               {{"intent":"hỏi về thời gian mở cửa cửa hàng",
               "topic": "Other"}}
            
            Lịch sử trò chuyện: {prev_chat}
            Ý định trước đó: {previous_intent}
            Tin nhắn hiện tại: {query} """
   
    print(previous_intent)
    system_instruction="""Nhiệm vụ của bạn là xác định và phân loại ý định của khách hàng.
                        Chỉ trả về JSON."""
    response=call_llm(prompt, system_instruction, temperature=0)
    match=re.search(r'{.*}', response, re.DOTALL)
    meta_data=match.group(0)
    meta_data=json.loads(meta_data)
    return meta_data



def get_metadata(intent, prev_chat):
    prompt=f"""Bạn sẽ nhận:
            - lịch sử trò chuyện giữa bạn và khách hàng.
            - mô tả chi tiết về ý định hiện tại của khách hàng.
            
              Nhiệm vụ:
              1. Xác định khách hàng đang tìm gì?.
                 Thực hiện theo các bước sau:
                 - trong lịch sử trò chuyện, xác định sản phẩm được đề cập gần nhất.  vd áo thun/quần tây/tất/áo khoác,...
                 - trong ý định hiện tại, khách hàng có hỏi thêm, yêu cầu cung cấp thêm thông tin gì về sản phẩm được đề cập gần nhất không? có -> see_more:false, product_codes=[""]
                 - trong ý định hiện tại, khách hàng có tìm mẫu, kiểu khác của sản phẩm được đề cập gần nhất không? có -> see_more: True, product_codes: <tất cả các mã sản phẩm của sản phẩm trước đó trong lịch sử trò chuyện>
                 - trong ý định hiện tại, khách hàng tìm sản phẩm khác với sản phẩm được đề cập gần nhất không? có -> see_more: false, product_codes=[""]

            2. Xác định các meta_data trong ý định của khách hàng.
                 - lọc ra các thông tin về giá và giới tính
                 - nếu khách hàng chưa cung cấp thông tin về giới tính, hỏi lại khách hàng
            
            Trả vê một JSON hoặc câu hỏi theo mẫu:
                    {{
                    "previous_product": str           # sản phẩm được đề cập trong tin nhắn trước dó.
                    "see_more": Boolean           
                    "product_codes": List[str]        # mã sản phẩm của sản phẩm được đề cập trong tin nhắn gần nhất trong lịch sử trò chuyện.
                    "price": {{"min": int, "max": int}},     # "max": "inf" nếu không có thông tin về giá
                    "gender": List[str],          # possible values in ['MALE', 'FEMALE', 'UNISEX'], hỏi lại khách hàng nếu chưa được đề cập.
                    }}            
            
            Ví dụ: 
              Lịch sử trò chuyện: {{'time': 'Sun Nov 16 16:00:00 2025', 'customer': 'mẫu áo thun cho nam size XL, dưới 200k', 'bot': 'Ok bạn ơi, đây là mẫu Áo Thun Nam Cotton 220GSM này, giá chỉ 159k thôi nè. Chất cotton dày dặn, mặc thoải mái lắm nha. Bạn xem thử có ưng màu nào không nè:\n\n<img src="https://n7media.coolmate.me/uploads/February2025/ao-thun-nam-cotton-220gsm-mau-nau-cappuccino_(7).jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/February2025/ao-thun-nam-cotton-220gsm-mau-xam-castlerock_(8).jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/February2025/ao-thun-nam-cotton-220gsm-mau-hong-peach-whip_(7).jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/October2024/AT.220_-_Do_1.1.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.den6.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.xd.3.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.be.1.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.den14.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.NAU.1.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/June2025/ao-thun-nam-cotton-220gsm-xanh-reu-1111.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.mint1.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/January2024/AT.220.xam1.jpg" width=300>\n\nMã sản phẩm: TSZ959'}}
                                  {{'time': 'Sun Nov 16 16:00:20 2025', 'customer': 'mẫu khác nha', 'bot': 'Ok bạn ơi, mình có mẫu Áo Thun Chạy Bộ Graphic Heartbeat này, giá cũng 159k nè, có nhiều màu xinh lắm:\n<img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-hong-5.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-tim-2.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-den-3.jpg" width=300>\n<img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-xanh-reu-3_60.jpg" width=300>\n\nMã sản phẩm: TSZ877\n\nNgoài ra còn có Áo singlet chạy bộ nam "Việt Nam tiến bước" giá 109k, siêu nhẹ và thoáng mát nè:\n<img src="https://n7media.coolmate.me/uploads/August2025/ao-singlet-chay-bo-nam-viet-nam-tien-buoc-18-do_76.jpg" width=300>\nMã sản phẩm: MUW\n\nBạn thích mẫu nào hơn nè?'}}
              Ý định khách hàng: tìm mẫu áo thun nam khác dưới 200k
              Trả về:
              {{
                    "previous_product": áo thun
                    "see_more": true           
                    "product_codes": ['TSZ959', 'TSZ877', 'MUW']  
                    "price": {{"min": 0, "max": 200000}},     
                    "gender": ['MALE'],          
              }}

              
              Lịch sử trò chuyện: {{'time': 'Sun Nov 16 07:52:30 2025', 'customer': 'các mẫu áo thun nam', 'bot': 'Tuyệt vời! Bạn đang tìm áo thun nam đúng không? Coolmate có mấy mẫu này rất được ưa chuộng nè:\n\n**1. Áo Thun Nam Cotton 220GSM Basics (TSZ959)**\n<img src="https://n7media.coolmate.me/uploads/February2025/ao-thun-nam-cotton-220gsm-mau-nau-cappuccino_(7).jpg" width=300>\nChất liệu 100% Cotton Úc dày dặn, mềm mịn, thấm hút tốt. Form Regular Fit mặc lên cực thoải mái, có đến 12 màu tha hồ lựa chọn nha. Giá chỉ 159.000đ.\n\n**2. Áo Thun Nam Chạy Bộ Graphic Heartbeat (TSZ877)**\n<img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-hong-5.jpg" width=300>\nSiêu nhẹ, nhanh khô và co giãn 4 chiều, cực hợp cho những ai mê vận động. Đặc biệt có logo phản quang giúp an toàn hơn khi tập luyện buổi tối. Giá cũng là 159.000đ.\n\n**3. Áo Thun Nam Thể Thao Coolmate Basics (TSZ916)**\n<img src="https://n7media.coolmate.me/uploads/September2025/ao-the-thao-nam-promax-recycle-basics1-hong-marsala-1_10.jpg" width=300>\nĐây là dòng sản phẩm Recycle Basics, vừa thân thiện môi trường, vừa siêu nhẹ, thấm hút và khô nhanh. Giá mềm hơn, chỉ 99.000đ.\n\nBạn ưng mẫu nào hay muốn xem thêm màu sắc của mẫu nào không?'}},
                                  {{'time': 'Sun Nov 16 07:52:46 2025', 'customer': 'mẫu khác', 'bot': 'Oke, bạn muốn xem thêm áo thun nam đúng không? Coolmate có mấy mẫu này nè:\n\n**1. Áo thun dài tay 100% Cotton Relax fit (LSZ711)**\n<img src="https://n7media.coolmate.me/uploads/September2025/ao-dai-tay-100-cotton-relax-fit-reu-1.jpg" width=300>\nÁo này làm từ 100% cotton mềm mại, thấm hút tốt, form Relax fit mặc thoải mái lắm. Có màu Rêu, Trắng, Đen. Giá 219.000đ.\n\n**2. Áo dài tay thể thao 1699 (LSZ681)**\n<img src="https://n7media.coolmate.me/uploads/December2024/ao-dai-tay-the-thao-1699-trang_(3).jpg" width=300>\nÁo này chất polyester thoáng khí, nhanh khô, hợp cho người hay vận động nè. Form Slim fit tôn dáng. Có các màu Trắng, Be Trench Coat, Be, Đen, Navy, Xanh bóng đêm. Giá 199.000đ.\n\n**3. Áo thun nam Cotton Compact (TSZ923)**\n<img src="https://n7media.coolmate.me/uploads/September2025/ao-thun-nam-cotton-compact-chong-nhan-den-1.jpg" width=300>\nChất cotton compact siêu mềm mịn, ít nhăn, có thêm chút spandex co giãn thoải mái. Form Regular fit. Có nhiều màu lắm: Đen, Xám, Xanh Navy, Trắng, Xanh rêu, Đỏ, Be, Xanh Pastel. Giá 229.000đ.\n\nBạn thấy mẫu nào ưng ý hay muốn xem thêm chi tiết gì không?'}}
              Ý định khách hàng: quần kaki để đi làm
              Trả về:
               {{
                    "previous_product": áo thun         
                    "see_more": false
                    "product_codes":[""]      
                    "price": {{"min": 0, "max": "inf"}},    
                    "gender": ['MALE']
              }}

              Lịch sử trò chuyện: {{'time': 'Sun Nov 16 17:05:40 2025', 'customer': 'mẫu áo thun nam dưới 200k', 'bot': 'Chào bạn, dưới đây là một số mẫu áo thun nam dưới 200k mà bạn có thể tham khảo nè:\n\n1.  **Áo Thun Nam Cotton 220GSM Basics**\n    *   Giá: 159.000đ\n    *   Chất liệu: 100% Cotton\n    *   Đặc điểm nổi bật: Thấm hút tốt, chống xù lông, bề mặt vải mềm mịn, giữ form dáng tốt.\n    *   Mô tả: Đây là mẫu áo thun basic, là item nền tảng cho mọi tủ đồ. Vải dày dặn nhưng vẫn thoáng khí, rất phù hợp để mặc hàng ngày.\n    *   Có nhiều màu sắc đa dạng: Nâu Cappuccino, Xám Castlerock, Hồng Peach Whip, Đỏ Zifandel, Trắng, Xanh biển, Be, Đen, Nâu, Xanh rêu, Xanh mint, Xám Melange.\n    *   Link sản phẩm: https://www.coolmate.me/product/ao-thun-100-cotton-220gsm/n\n    *   Mã sản phẩm: TSZ959\n    *   Hình ảnh:\n        <img src="https://n7media.coolmate.me/uploads/February2025/ao-thun-nam-cotton-220gsm-mau-nau-cappuccino_(7).jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/February2025/ao-thun-nam-cotton-220gsm-mau-xam-castlerock_(8).jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/February2025/ao-thun-nam-cotton-220gsm-mau-hong-peach-whip_(7).jpg" width=300>\n\n2.  **Áo Thun Nam Thể Thao Coolmate Basics**\n    *   Giá: 99.000đ\n    *   Chất liệu: 51% Poly Recycled và 49% Poly\n    *   Đặc điểm nổi bật: Siêu nhẹ, thấm hút tốt, nhanh khô, thoáng mát.\n    *   Mô tả: Phù hợp cho các hoạt động thể thao, tập gym, chạy bộ nhờ công nghệ thấm hút và khô nhanh. Chất liệu tái chế thân thiện với môi trường.\n    *   Có nhiều màu sắc: Hồng Marsala, Xanh dương, Đen logo mới, Đen, Navy logo mới, Xanh da trời, Xanh bóng đêm, Xám nhạt, Xám nhạt logo mới, Xám đậm logo mới, Xám đậm, Xanh Cool, Xanh Cobalt, Xanh Forever Blue, Xanh Pacific, Nâu Iron, Xanh bạc hà, Xanh Navy.\n    *   Link sản phẩm: https://www.coolmate.me/product/ao-the-thao-nam-promax-recycle-basics1/n\n    *   Mã sản phẩm: TSZ916\n    *   Hình ảnh:\n        <img src="https://n7media.coolmate.me/uploads/September2025/ao-the-thao-nam-promax-recycle-basics1-hong-marsala-1_10.jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/September2025/ao-the-thao-nam-promax-recycle-basics1-xanh-duong-1_54.jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/September2025/ao-the-thao-nam-promax-recycle-basics1-den-logo-moi-1_82.jpg" width=300>\n\n3.  **Áo singlet chạy bộ nam "Việt Nam tiến bước"**\n    *   Giá: 109.000đ\n    *   Chất liệu: 100% Polyester\n    *   Đặc điểm nổi bật: Siêu nhẹ, thấm hút, thoáng mát, công nghệ Ex-Dry, kiểu dáng tanktop.\n    *   Mô tả: Đây là áo tanktop chuyên dụng cho chạy bộ, leo núi, với thiết kế lưng chữ Y giúp tối ưu chuyển động. Họa tiết Cờ đỏ sao vàng thể hiện niềm tự hào dân tộc.\n    *   Màu sắc: Đỏ.\n    *   Link sản phẩm: https://www.coolmate.me/product/singlet-chay-bo-nam-viet-nam-tien-buoc/n\n    *   Mã sản phẩm: 25CM.MAWRU.TTA484\n    *   Hình ảnh:\n        <img src="https://n7media.coolmate.me/uploads/August2025/ao-singlet-chay-bo-nam-viet-nam-tien-buoc-18-do_76.jpg" width=300>\n\nBạn thích mẫu nào hơn, hay muốn xem thêm những lựa chọn nào khác không?'}},
                                  {{'time': 'Sun Nov 16 17:05:55 2025', 'customer': 'mẫu khác nha', 'bot': 'Mình có vài mẫu áo thun thể thao và áo giữ nhiệt đây, bạn xem có ưng không nhé:\n\n1.  **Áo Thun Nam Chạy Bộ Graphic Heartbeat**\n    *   Giá: 159.000đ\n    *   Đặc điểm nổi bật: Siêu nhẹ, nhanh khô, thấm hút tốt, co giãn.\n    *   Mô tả: Phù hợp cho chạy bộ và tập luyện đa môn, có logo phản quang tăng an toàn.\n    *   Màu sắc: Hồng, Tím, Đen, Xanh rêu.\n    *   Link sản phẩm: https://www.coolmate.me/product/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-sieu-nhe-thoang-mat/n\n    *   Mã sản phẩm: TSZ877\n    *   Hình ảnh:\n        <img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-hong-5.jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-tim-2.jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-den-3.jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/July2025/ao-thun-nam-chay-bo-hoat-tiet-graphic-heartbeat-xanh-reu-3_60.jpg" width=300>\n\n2.  **Áo dài tay thể thao 1699**\n    *   Giá: 199.000đ\n    *   Mô tả: Áo dài tay thể thao, thấm hút mồ hôi nhanh và thoát ẩm tốt, giữ ấm hiệu quả.\n    *   Màu sắc: Trắng, Be Trench Coat, Be, Đen, Navy, Xanh bóng đêm.\n    *   Link sản phẩm: https://www.coolmate.me/product/ao-dai-tay-the-thao-1699/n\n    *   Mã sản phẩm: LSZ681\n    *   Hình ảnh:\n        <img src="https://n7media.coolmate.me/uploads/December2024/ao-dai-tay-the-thao-1699-trang_(3).jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/December2024/ao-dai-tay-the-thao-1699-den_(1).jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/December2024/ao-dai-tay-the-thao-1699-navy_(1).jpg" width=300>\n\n3.  **Áo Giữ Nhiệt Modal Ultra**\n    *   Giá: 149.000đ\n    *   Mô tả: Áo giữ nhiệt mềm mại, thoáng khí, giữ ấm tốt nhờ chất liệu Modal và Cotton.\n    *   Màu sắc: Trắng, Xám, Đen.\n    *   Link sản phẩm: https://www.coolmate.me/product/ao-giu-nhiet-nam-modal-ultra-warm-mac-la-am-thoang-khi/n\n    *   Mã sản phẩm: MUW\n    *   Hình ảnh:\n        <img src="https://n7media.coolmate.me/uploads/October2023/sao_giu_nhiet_trang_6.jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/October2023/modal-ultra-warm-3_75.jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/October2023/modal-ultra-warm-den-1-1.jpg" width=300>\n\nBạn thấy mẫu nào hợp ý hơn không?'}},
                                  {{'time': 'Sun Nov 16 17:06:21 2025', 'customer': 'mẫu quần short nam', 'bot': 'Dưới đây là một vài mẫu quần short nam Coolmate gợi ý cho bạn nha:\n\n1.  **Quần Shorts Nam Mặc Nhà Cotton kháng khuẩn**\n    *   Giá: 99.000đ\n    *   Chất liệu: 74% Cotton, 22% Polyester, 4% Spandex\n    *   Đặc điểm nổi bật: Thấm hút tốt, thoáng mát, kháng khuẩn, mềm mại.\n    *   Mô tả: Quần short dáng rộng rãi, lưng thun dệt êm ái, rất lý tưởng để mặc ở nhà hoặc đi ngủ.\n    *   Có nhiều màu sắc và họa tiết: Xanh dương, Xám đen, Trắng kẻ đen, Đỏ xanh, Đen xám, Rêu, Xanh lá...\n    *   Mã sản phẩm: SOZ890\n    *   Link sản phẩm: https://www.coolmate.me/product/quan-short-nam-mac-nha-thoang-mat/n\n    *   Hình ảnh:\n        <img src="https://n7media.coolmate.me/uploads/July2025/quan-short-nam-mac-nha-4-xanh-duong-7.jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/July2025/quan-short-nam-mac-nha-2-xam-den-3.jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/July2025/quan-short-nam-mac-nha-2-trang-ke-den.jpg" width=300>\n\n2.  **Quần Short Nam Thể Thao Promax-S1**\n    *   Giá: 169.000đ\n    *   Chất liệu: 100% Polyester\n    *   Đặc điểm nổi bật: Nhanh khô, thấm hút tốt, co giãn.\n    *   Mô tả: Phù hợp cho tập thể thao hoặc mặc hàng ngày, chất vải nhẹ, thoáng khí, thấm hút mồ hôi hiệu quả.\n    *   Có nhiều màu sắc: Đen, Xanh Navy, Xanh bóng đêm, Xanh Aqua, Xám đen.\n    *   Mã sản phẩm: SOZ890\n    *   Link sản phẩm: https://www.coolmate.me/product/quan-the-thao-nam-promax-s1/n\n    *   Hình ảnh:\n        <img src="https://n7media.coolmate.me/uploads/September2025/quan-the-thao-nam-promax-s1-den-1.jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/September2025/quan-the-thao-nam-promax-s1-xanh-navy-1.jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/September2025/quan-the-thao-nam-promax-s1-xam-den-1.jpg" width=300>\n\n3.  **Quần Thể Thao Nam 7" Ultra Shorts**\n    *   Giá: 159.000đ\n    *   Chất liệu: 100% Polyester\n    *   Đặc điểm nổi bật: Co giãn, thoáng mát, thoải mái, thấm hút và nhanh khô.\n    *   Mô tả: Thiết kế tối ưu cho vận động, phù hợp tập gym, chạy bộ hoặc các môn thể thao khác.\n    *   Có nhiều màu sắc: Xanh Forest Night, Nâu Iron, Xanh Hunter Green, Cam Hot Sauce, Nâu Chocolate Chip, Đen, Xám,...\n    *   Mã sản phẩm: SOZ893\n    *   Link sản phẩm: https://www.coolmate.me/product/quan-the-thao-nam-7-ultra-short/n\n    *   Hình ảnh:\n        <img src="https://n7media.coolmate.me/uploads/September2025/quan-the-thao-nam-7-ultra-short-den-1.jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/September2025/quan-the-thao-nam-7-ultra-short-xanh-navy-1.jpg" width=300>\n        <img src="https://n7media.coolmate.me/uploads/September2025/quan-the-thao-nam-7-ultra-short-reu-1.jpg" width=300>\n\nBạn thích mẫu nào hơn, hay muốn mình tìm thêm những kiểu quần short nào khác không?'}},                                 
              Ý định khách hàng: tìm mẫu quần short khác cho nam
              Trả về:
               {{
                    "previous_product": quần short        
                    "see_more": true
                    "product_codes": ["SOZ890", "SOZ890", "SOZ893"]       
                    "price": {{"min": 0, "max": "inf"}}, 
                    "gender": ['MALE']
              }}

              Lịch sử trò chuyện: {{'time': 'Mon Nov 17 15:18:54 2025', 'customer': 'xin chào', 'bot': 'Chào bạn, mình có thể giúp gì cho bạn nè?'}}
              Ý định khách hàng: tìm quần kaki để đi làm
              Trả về: Bạn mua quần kaki cho nam hay nữ vậy ạ?

              Lịch sử trò chuyện: 
              Ý định khách hàng: tìm áo thun
              Trả về: Bạn mua áo thun cho nam hay nữ vậy ạ?

            
            Lịch sử trò chuyện: {prev_chat}
            Ý định hiện tại của khách hàng: {intent}"""
    print(f"""Lịch sử trò chuyện: {prev_chat}
              Ý định hiện tại của khách hàng: {intent}""")

    system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến Coolmate.
                          Trả về một JSON hoặc câu hỏi, chỉ một trong hai"""
    response=call_llm(prompt, system_instruction, temperature=0)
    if "?" in response:
        return response
    match=re.search(r'{.*}', response, re.DOTALL)
    meta_data=match.group(0)
    meta_data=json.loads(meta_data)
    return meta_data

def build_filters(meta_data):
    filters=[]
    for key, value in meta_data.items():
        if value==[]:
            continue
        elif key=='price' and value['max'] != 'inf':                          
            filters.append(Filter.by_property(key).greater_than(value['min']))
            filters.append(Filter.by_property(key).less_than(value['max']))
        elif key=='gender':
            filters.append(Filter.by_property('gender').contains_any(value))
        elif key=="product_codes" and meta_data["see_more"] ==True:
            filters.append(Filter.by_property('product_code').contains_none(value))
    return filters
    
def query_product(client, query, prev_chat, intent):   
    
    # client.collections.delete('products')
    products=client.collections.get('products')

    # print(prompt)
    meta_data=get_metadata(intent, prev_chat)
    if "?" in meta_data:
        return meta_data

    # if '?' in augmented_query:
    #     return augmented_query
    # print(augmented_query)
    context=""
    print(meta_data)
    filters=build_filters(meta_data)
    response=products.query.near_text(query=intent, filters=Filter.all_of(filters) if len(filters) != 0 else None, limit=3)
    context=""
    check_context=""
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
                    size theo màu có sẵn: {res.properties['colorBySize']},
                    link sản phẩm:{res.properties['product_url']}/n"""
        

        check_context+=f"""mã sản phẩm: {res.properties['product_code']},
                    tên sản phẩm:{res.properties['name']},                     
                    giá: {res.properties['price']}
                        """
                    
    
    
    print(check_context)

    prompt=f""" Bạn sẽ nhận:
                - ý định hiện tại của khách hàng
                - thông tin các sản phẩm phù hợp

                Nhiệm vụ: 
                trả lời đúng vào sản phẩm khách hàng đang tìm dựa theo thông tin sản phẩm được cung cấp.
                

                Yêu cầu:
                - Báo hết sản phẩm nếu trong sản phẩm phù hợp không có sản phẩm khách hàng muốn tìm, gợi ý sản phẩm khác.
                - tránh trả lời không liên quan đến câu hỏi hay yêu cầu của khách hàng.
                - liệt kê sản phẩm theo số thứ tự.
                - Không đề cấp đến số lượng hàng tồn.
                - Gắn hình ảnh bằng tag <img src="http:\\ ..." width=300>.
                - Đính kèm mã sản phẩm.
                
                ý định hiện tại của khách hàng: {intent}
                sản phẩm phù hợp: {context}"""
                
    system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến Coolmate. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                            Giữ câu trả lời ngắn gọn và hữu ích.
                            Không chào lại nếu đã trong một cuộc trò chuyện."""

    response=call_llm(prompt, system_instruction)
    
    
    
    return response


def query_other(client, query, prev_chat, intent):
    context=""
    faqs=client.collections.get('faqs')
    response=faqs.query.near_text(intent, limit=3)
    for res in response.objects:
        context+=f"Question: {res.properties['question']} Answer: {res.properties['answer']}\n"

    prompt=f""" Bạn sẽ nhận:
                - lịch sử trò chuyện giữa bạn và khách hàng
                - tin nhắn hiện tại của khách
                - thông tin sản phẩm

                Nhiệm vụ: 
                - trả lời tin nhắn khách hàng dựa theo các thông tin được cung cấp
                
                Lịch sử trò chuyện:{prev_chat}
                Tin nhắn hiện tại: '{query}'.
                Thông tin: {context}"""
    
    system_instruction="""Bạn là một trợ lý ảo trò chuyện cho cửa hàng quần áo trực tuyến Coolmate. Hãy nói chuyện một cách tự nhiên, như đang trò chuyện với một người bạn.
                          Giữ câu trả lời ngắn gọn và hữu ích.
                          Nếu vẫn đang trong một cuộc trò chuyện thì chỉ trả lời, không chào lại."""
    response=call_llm(prompt, system_instruction)
    return response

 
