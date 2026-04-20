import requests

with open("test_dummy.pdf", "w") as f:
    f.write("dummy PDF content")

files = {'file': ('test_dummy.pdf', open('test_dummy.pdf', 'rb'))}
response = requests.post("http://localhost:8000/api/chat/upload", files=files)
print("Status:", response.status_code)
print("Response:", response.json())
