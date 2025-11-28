import re
import json
text="""{"reasoning": "Khách hàng đang tìm kiếm"}"""
print(re.search(r'{\"(.+)\"}',text))
print(re.search(r'{\"(.+)\"}',text).group(1))
# match=re.search(r'\"reasoning\":\\s\"(.+)\", \"response\"', text,flags=re.DOTALL)
# print(match.group(0))
