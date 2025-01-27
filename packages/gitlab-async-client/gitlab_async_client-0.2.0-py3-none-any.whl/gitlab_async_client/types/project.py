from pydantic import RootModel, HttpUrl
from .base import ExtendBaseModel
from .extend import ArrowPydanticV2


class Project(ExtendBaseModel):
    id: int
    description: str | None
    name: str
    name_with_namespace: str
    created_at: ArrowPydanticV2
    last_activity_at: ArrowPydanticV2
    web_url: HttpUrl

    class Config:
        extra = 'ignore'


class ProjectList(RootModel[list[Project]]):
    pass
