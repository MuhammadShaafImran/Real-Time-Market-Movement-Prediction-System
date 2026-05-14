import requests

API_URL = "https://api-inference.huggingface.co/models/mabdullahali/market-mind-lstm"

headers = {
    "Authorization": "Bearer YOUR_TOKEN"
}

payload = {
    "inputs": [[0.1] * 17] * 30
}

response = requests.post(
    API_URL,
    headers=headers,
    json=payload
)

print(response.status_code)
print(response.json())