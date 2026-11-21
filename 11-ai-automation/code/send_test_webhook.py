"""
send_test_webhook.py - plays the role of "the other system" and sends a signed webhook.

Start the receiver first:   uvicorn webhook_receiver:app --port 8000
Then run:                   python send_test_webhook.py
Point it elsewhere with:    TARGET_URL=https://your-n8n/webhook/support-ticket python send_test_webhook.py
"""
import hashlib
import hmac
import json
import os
import uuid

import httpx   # modern HTTP client (like requests, but also supports async)

URL = os.getenv("TARGET_URL", "http://127.0.0.1:8000/webhook/ticket")
SECRET = os.getenv("WEBHOOK_SECRET", "dev-secret-change-me")   # must match the receiver

payload = {
    "event_id": str(uuid.uuid4()),                 # unique id so the receiver can skip duplicates
    "email": "asha@example.com",
    "subject": "Site is down",
    "message": "We get error 500 on checkout, urgent!",
}
body = json.dumps(payload).encode()                # the exact bytes we will send
signature = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()

response = httpx.post(URL, content=body, timeout=10,
                      headers={"Content-Type": "application/json", "X-Signature": signature})
print(response.status_code, response.json())

# Send the same event again: the receiver should answer "duplicate".
again = httpx.post(URL, content=body, timeout=10,
                   headers={"Content-Type": "application/json", "X-Signature": signature})
print(again.status_code, again.json())
