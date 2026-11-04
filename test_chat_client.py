import requests

URL = "http://127.0.0.1:8000/chat"

request = {
    "messages": [{"role": "user", "content": "What is NIST SP 800 publications?"}],
    "model": "gemini-3.8-flash",
}

print("=================================")
print("Testing ControlMap /chat")
print("=================================")

print("\nSending request...")
# print(json.dumps(request, indent=2))

try:
    response = requests.post(URL, json=request, timeout=120)

    print("\nStatus Code:", response.status_code)
    print("Headers:", dict(response.headers))

    print("\nResponse:")
    print(response.text)

except requests.exceptions.ConnectionError as e:
    print("\nCONNECTION ERROR")
    print(e)

except requests.exceptions.Timeout:
    print("\nTIMEOUT")

except Exception as e:
    print("\nERROR")
    print(type(e).__name__, e)
