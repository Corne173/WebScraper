import re

text = "Item: i3 6100 Age: 4 years Price: R 800 neg. Warranty: 7 days on me  Packaging: Original Condition: Good Location: Pretoria Reason: Upgraded Shipping: On you Collection: Yes"

result = re.findall("Location: \w+",text)

print(result)