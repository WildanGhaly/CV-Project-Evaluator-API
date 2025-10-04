from pydantic import BaseModel
from typing import Optional, Dict, Any

class ResultResponse(BaseModel):
    id: str
    status: str
    result: Optional[Dict[str, Any]] = None
