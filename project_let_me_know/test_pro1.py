import requests

BASE = "http://127.0.0.1:5000"



# 5. Get Messages
print("Get Messages:")
res = requests.get(f"{BASE}/debates/514ebd76-7157-482b-9ac7-da8318d9c768/messages")
print(res.json())
