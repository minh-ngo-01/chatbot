import re

text="""(Phân tích ý định của khách hàng: Khách hàng đang tìm kiếm "áo thun nam". Phân tích các sản phẩm tìm được:

Sản phẩm 1: "Áo singlet chạy bộ nam 'Việt Nam tiến bước'" - Đây là áo tanktop, không phải áo thun thông thường.
Sản phẩm 2: "Áo Thun Nam Thể Thao Coolmate Basics" - Đây là áo thun nam.
Sản phẩm 3: "Tshirt chạy bộ nam Airflow Luman Line" - Đây là áo thun nam.
Xác định sản phẩm khách hàng tìm: Có sản phẩm áo thun nam. Lập danh sách các sản phẩm áo thun nam tìm được. Định dạng câu trả lời theo yêu cầu.) Dưới đây là các mẫu áo thun nam, bạn xem thử nhé:"""

print(re.sub(r"\(.+\) ", "", text, flags=re.DOTALL))