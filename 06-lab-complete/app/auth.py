from fastapi import Header, HTTPException, Security
from .config import settings

def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """
    Xác thực API Key từ Header `X-API-Key`.
    Trả về 'user_id' giả lập dựa trên API key hợp lệ, hoặc raise 401.
    """
    if x_api_key != settings.agent_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key"
        )
    # Trả về một user_id dựa trên key (trong thực tế sẽ tra DB)
    return f"user_{x_api_key[:5]}"
