from utils import classify_query
from utils import query_faq
from utils import query_product

query='i want to buy t-shirt for men'
query_type=classify_query(query)
print(query_type)
if query_type=='FAQ':
    res=query_faq(query)
elif query_type=='Product':
    res=query_product(query)
print(res)
