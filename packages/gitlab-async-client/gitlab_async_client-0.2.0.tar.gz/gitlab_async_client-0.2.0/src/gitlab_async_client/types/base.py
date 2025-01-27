

from pydantic import (
    BaseModel,
)


class ExtendBaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        extra = 'allow'

