import re
from typing import Optional

def validate_email(email: str) -> bool:
    """이메일 형식을 검증합니다."""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False
    
    parts = email.split('@')
    if len(parts) != 2:
        return False
    
    local_part, domain = parts
    
    if len(local_part) == 0 or len(local_part) > 64:
        return False
    
    if len(domain) == 0 or len(domain) > 255:
        return False
    
    if '.' not in domain:
        return False
    
    return True

def sanitize_email(email: str) -> Optional[str]:
    """이메일을 정리하고 검증합니다."""
    if not email:
        return None
    
    cleaned_email = email.strip().lower()
    
    if validate_email(cleaned_email):
        return cleaned_email
    
    return None 