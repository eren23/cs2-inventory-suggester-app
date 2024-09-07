from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict

# Settings
REQUEST_LIMIT_PER_USER = 5
REQUEST_LIMIT_PER_IP = 5
TIME_FRAME = timedelta(minutes=1)

# Stores
user_requests = defaultdict(lambda: {"count": 0, "time": datetime.now()})
ip_requests = defaultdict(lambda: {"count": 0, "time": datetime.now()})


async def rate_limit_user(request: Request, username: str = None):
    now = datetime.now()
    ip = request.client.host

    # Rate limit by IP
    ip_data = ip_requests[ip]
    if now - ip_data["time"] > TIME_FRAME:
        ip_data["count"] = 1
        ip_data["time"] = now
    else:
        ip_data["count"] += 1
        if ip_data["count"] > REQUEST_LIMIT_PER_IP:
            raise HTTPException(status_code=429, detail="Rate limit exceeded for IP")

    # If user is authenticated, rate limit by user
    if username:
        user_data = user_requests[username]
        if now - user_data["time"] > TIME_FRAME:
            user_data["count"] = 1
            user_data["time"] = now
        else:
            user_data["count"] += 1
            if user_data["count"] > REQUEST_LIMIT_PER_USER:
                raise HTTPException(status_code=429, detail="Rate limit exceeded for user")
