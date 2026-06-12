import redis
from datetime import datetime
from fastapi import HTTPException
from .config import settings
from .rate_limiter import r  # Sử dụng chung Redis instance

def check_budget(user_id: str, estimated_cost: float = 0.05):
    """
    Kiểm tra xem user có còn ngân sách trong tháng không.
    Mặc định giả lập mỗi request tốn $0.05.
    Trong thực tế, bạn sẽ tính cost thật dựa trên số lượng tokens input/output.
    """
    if not settings.redis_url:
        return
        
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    try:
        current_spent = float(r.get(key) or 0.0)
        
        if current_spent + estimated_cost > settings.daily_budget_usd:
            raise HTTPException(
                status_code=402,
                detail=f"Payment Required. Monthly budget of ${settings.daily_budget_usd} exceeded."
            )
            
    except redis.ConnectionError:
        pass

def add_cost(user_id: str, actual_cost: float):
    """
    Hàm này được gọi SAU khi LLM xử lý xong để cộng dồn chi phí thật vào Redis.
    """
    if not settings.redis_url:
        return
        
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    try:
        r.incrbyfloat(key, actual_cost)
        r.expire(key, 32 * 24 * 3600)  # Giữ data 32 ngày
    except redis.ConnectionError:
        pass
