from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class CrawlingStatus(str, Enum):
    Success = "Success"
    Failed = "Failed"
    UnknownError = "UnknownError"
    DNSLookupError = "DNSLookupError"

class CrawlResponse(BaseModel):
    URL: str
    phone_numbers: Optional[List[str]] = None
    social_media_links: Optional[List[str]] = None
    addresses: Optional[List[str]] = None
    company_commercial_name: Optional[str] = None
    company_legal_name: Optional[str] = None
    company_all_available_names: Optional[str] = None
    Status: CrawlingStatus