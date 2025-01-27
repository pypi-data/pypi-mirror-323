from enum import Enum

from gitlab_async_client.types.base import ExtendBaseModel
from pydantic import RootModel, HttpUrl

from gitlab_async_client.types.extend import ArrowPydanticV2


class MRState(str, Enum):
    opened = 'opened'
    closed = 'closed'
    locked = 'locked'
    merged = 'merged'
    all = 'all'


class MRScopeState(str, Enum):
    all = 'all'
    created_by_me = 'created_by_me'
    assigned_to_me = 'assigned_to_me'


class MergeRequestAuthor(ExtendBaseModel):
    id: int
    username: str
    name: str
    web_url: HttpUrl

    class Config:
        extra = 'ignore'


class MergeRequest(ExtendBaseModel):
    id: int
    iid: int
    project_id: int
    title: str
    description: str | None
    state: MRState
    created_at: ArrowPydanticV2
    updated_at: ArrowPydanticV2
    merged_by: str | None
    merge_user: str | None
    merged_at: ArrowPydanticV2 | None
    author: MergeRequestAuthor
    closed_by: str | None
    closed_at: str | None
    target_branch: str
    source_branch: str
    merge_status: str
    has_conflicts: bool

    class Config:
        extra = 'ignore'


class MergeRequestDiff(ExtendBaseModel):
    deleted_file: bool
    diff: str
    generated_file: bool
    new_file: bool
    new_path: str
    old_path: str
    renamed_file: bool


class MergeRequestNotes(ExtendBaseModel):
    id: int
    attachment: str | None
    author: MergeRequestAuthor
    created_at: ArrowPydanticV2
    noteable_id: int
    noteable_iid: int
    project_id: int
    resolvable: bool
    system: bool
    type: str | None
    updated_at: ArrowPydanticV2
    body: str
    noteable_type: str

    class Config:
        extra = 'ignore'


class MergeRequestNotesList(RootModel[list[MergeRequestNotes]]):
    pass


class MergeRequestDiffList(RootModel[list[MergeRequestDiff]]):
    pass


class MergeRequestsList(RootModel[list[MergeRequest]]):
    pass
