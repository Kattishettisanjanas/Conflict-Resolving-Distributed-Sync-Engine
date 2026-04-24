from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class Item(BaseModel):
    id: str
    value: str
    updated_at: datetime
    vector_clock: Dict[str, int] = {}

class PushRequest(BaseModel):
    site_id: str
    changes: List[Item]

class PullRequest(BaseModel):
    since: datetime
