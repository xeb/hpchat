from pydantic import BaseModel
from typing import List

class ParsedSermon(BaseModel):
    url_slug: str = None
    title: str = None
    one_sentence_summary: str = None
    announcements: List[str] = None
    biblical_references: List[str] = None