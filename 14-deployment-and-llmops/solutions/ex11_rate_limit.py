"""
Exercise 11 solution - a per-user sliding-window rate limiter as a FastAPI dependency.
Run:  python ex11_rate_limit.py
"""
import time
from collections import defaultdict, deque

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

MAX_REQUESTS = 5          # allowed requests ...
WINDOW_SECONDS = 10       # ... per this many seconds
_hits: dict[str, deque] = defaultdict(deque)   # user id -> timestamps of recent requests


def rate_limit(x_user_id: str = Header(default="anonymous")):
    """Dependency: runs before the route. Raises 429 if this user is over the limit."""
    now = time.monotonic()                      # a clock that never jumps backwards
    q = _hits[x_user_id]
    while q and now - q[0] > WINDOW_SECONDS:    # forget requests older than the window
        q.popleft()
    if len(q) >= MAX_REQUESTS:
        retry_after = int(WINDOW_SECONDS - (now - q[0])) + 1
        raise HTTPException(status_code=429, detail="rate limit exceeded",
                            headers={"Retry-After": str(retry_after)})   # tell the client when to come back
    q.append(now)


app = FastAPI()


@app.post("/chat", dependencies=[Depends(rate_limit)])
def chat(body: dict):
    return {"reply": f"echo: {body.get('message', '')}"}


if __name__ == "__main__":
    client = TestClient(app)
    codes = [client.post("/chat", json={"message": "hi"}, headers={"X-User-Id": "asha"}).status_code
             for _ in range(6)]
    print("asha:", codes)                                    # [200, 200, 200, 200, 200, 429]
    assert codes == [200] * 5 + [429]
    other = client.post("/chat", json={"message": "hi"}, headers={"X-User-Id": "ravi"}).status_code
    print("ravi:", other)                                    # 200 - separate bucket
    assert other == 200
    print("all checks passed")
