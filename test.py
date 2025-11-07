import re


meta_data="""```json
{"price": {
"min": 0,
"max": 200000
},
"gender": [
"Men"
],
"shown_product_codes": []}
```"""
import re
import json
match=re.search(r'{.*}', meta_data, re.DOTALL)
meta_data=match.group(0)

meta_data=json.loads(meta_data)
print(meta_data)