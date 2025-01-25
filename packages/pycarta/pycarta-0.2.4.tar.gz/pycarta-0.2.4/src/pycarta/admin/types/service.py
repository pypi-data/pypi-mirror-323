from pydantic import Field
from .document_history import TrackedItem


class Service(TrackedItem):
    name: str
    base_url: str = Field(alias='baseUrl', default=None)

