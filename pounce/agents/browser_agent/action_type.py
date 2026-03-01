from typing import List, Union, Literal

from pydantic import BaseModel, Field


class LocateParam(BaseModel):
    prompt: str = ''
    bbox: List[int] = Field(
        default=[0, 0, 0, 0],
        min_length=4,
        max_length=4
    )


class MockParam(BaseModel):
    api: str
    mock_data: str


class WaitParam(BaseModel):
    value: int


class ClickParam(BaseModel):
    locate: LocateParam


class HoverParam(BaseModel):
    locate: LocateParam


class AssertParam(BaseModel):
    desc: str
    locate_list: List[LocateParam] = None


class NavigateParam(BaseModel):
    url: str


class InputParam(BaseModel):
    locate: LocateParam
    value: str
    mode: Literal['replace', 'clear'] = 'replace'


class ScrollParam(BaseModel):
    direction: Literal['down', 'up'] = 'down'
    distance: int = 0
    scroll_type: Literal['singleAction'] = 'singleAction'


class MockAction(BaseModel):
    type: Literal['Mock'] = 'Mock'
    param: MockParam


class WaitAction(BaseModel):
    type: Literal['Wait'] = 'Wait'
    param: WaitParam


class AssertAction(BaseModel):
    type: Literal['Assert'] = 'Assert'
    param: AssertParam


class NavigateAction(BaseModel):
    type: Literal['Navigate'] = 'Navigate'
    param: NavigateParam


class ClickAction(BaseModel):
    type: Literal['Click'] = 'Click'
    param: ClickParam


class HoverAction(BaseModel):
    type: Literal['Hover'] = 'Hover'
    param: HoverParam


class InputAction(BaseModel):
    type: Literal['Input'] = 'Input'
    param: InputParam


class ScrollAction(BaseModel):
    type: Literal['Scroll'] = 'Scroll'
    param: ScrollParam


class DoneAction(BaseModel):
    type: Literal['done'] = 'Done'
    param: dict


Action = Union[
    MockAction,
    WaitAction,
    AssertAction,
    NavigateAction,
    ClickAction,
    HoverAction,
    InputAction,
    ScrollAction,
    DoneAction
]
