from typing import Optional
from pydantic import BaseModel, ConfigDict


class DocumentPackResponse(BaseModel):
    id: str
    title: str
    desc: str
    tag: str
    level: str
    pages: str
    is_premium: bool
    can_access: bool = False
    download_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

