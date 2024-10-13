from pydantic import BaseModel
from typing import Optional, List

class TestRequest(BaseModel):
    tags_list: dict


class TestCallback(BaseModel):
    result: dict
    
class CrawlingRequest(BaseModel):
    number_of_domains: Optional[int] = 10
    
class QueryUrl(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    phone_number: Optional[str] = None
    social_media_links: Optional[str] = None
    facebook: Optional[str] = None
    addresses: Optional[str] = None