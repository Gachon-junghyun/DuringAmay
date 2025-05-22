import requests

BASE = "http://127.0.0.1:5000"

# 1. Register
print("Register:")
res = requests.post(f"{BASE}/register", json={
    "username": "testuser",
    "password": "securepass"
})
print(res.json())

# 2. Login
print("Login:")
res = requests.post(f"{BASE}/login", json={
    "username": "testuser",
    "password": "securepass"
})
print(res.json())

# 3. Create Debate
print("Create Debate:")
res = requests.post(f"{BASE}/debates", json={"topic": "junghyun_seeing2"})
debate_id = res.json().get("debate_id")
print(res.json())

# 4. Add Message
print("Add Message:")
res = requests.post(f"{BASE}/debates/{debate_id}/messages", json={
    "sender_name": "Alice",
    "content": "AI will never feel love like humans do."
})
print(res.json())

# 4. Add Message
print("Add Message:")
res = requests.post(f"{BASE}/debates/{debate_id}/messages", json={
    "sender_name": "Hanjeonghyun",
    "content": "i love yoonjung"
})
print(res.json())

# 4. Add Message
print("Add Message:")
res = requests.post(f"{BASE}/debates/{debate_id}/messages", json={
    "sender_name": "wls",
    "content": "you can not see her"
})
print(res.json())


# 5. Get Messages
print("Get Messages:")
res = requests.get(f"{BASE}/debates/{debate_id}/messages")
print(res.json())
