from typing import Optional, List
from fastapi import Query

from app.restschema import QueryUrl

def get_query_params(
    name: Optional[str] = Query(None, alias="name"),
    url: Optional[str] = Query(None, alias="url"),
    phone_number: Optional[str] = Query(None, alias="phone_number"),
    social_media_links: Optional[str] = Query(None, alias="social_media_links"),
    facebook: Optional[str] = Query(None, alias="facebook"),
    addresses: Optional[str] = Query(None, alias="addresses")
):
    return QueryUrl(
        name=name,
        url=url,
        phone_number=phone_number,
        social_media_links=social_media_links,
        facebook=facebook,
        addresses=addresses
    )