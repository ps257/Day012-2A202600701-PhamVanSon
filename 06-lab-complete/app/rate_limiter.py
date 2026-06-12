import time
import redis
from fastapi import HTTPException
from .config import settings

# Khởi tạo connection pool tới Redis để tái sử dụng
redis_pool = redis.ConnectionPool.from_url(settings.redis_url, decode_responses=True)
r = redis.Redis(connection_pool=redis_pool)

def check_rate_limit(user_id: str):
    """
    Sử dụng thuật toán Sliding Window hoặc Token Bucket đơn giản với Redis.
    Ở đây dùng cách đếm số request trong 1 phút bằng incr và expire.
    """
    if not settings.redis_url:
        return  # Bỏ qua nếu chưa cấu hình Redis

    current_minute = int(time.time() / 60)
    key = f"rate_limit:{user_id}:{current_minute}"
    
    try:
        current_requests = r.incr(key)
        if current_requests == 1:
            r.expire(key, 60)  # TTL 60 giây
            
        if current_requests > settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Too Many Requests. Limit is {settings.rate_limit_per_minute} per minute."
            )
    except redis.ConnectionError:
        # Trong trường hợp Redis sập, cho phép pass để hệ thống không chết hoàn toàn (Fail Open)
        pass
