from pydantic import BaseModel
from typing import List

class ParsedSermon(BaseModel):
    url_slug: str 
    title: str 
    one_sentence_summary: str 
    announcements: List[str] 
    biblical_references: List[str] 
    speaker_name: str 
