from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

ActionT = TypeVar('ActionT')


class VisualPlanOutput(BaseModel, Generic[ActionT]):
    thinking: str = Field(default='')
    action_prompt: str = Field(default='')
    action: ActionT | None = Field(default=None)


class VisualPlanHistoryItem(VisualPlanOutput[ActionT]):  # type: ignore[misc]
    action_result: str = Field(default='')


class VisualPlanInputState(BaseModel, Generic[ActionT]):
    user_message: str = Field(default='')
    history_items: List[VisualPlanHistoryItem[ActionT]] = Field(default_factory=list)


class VisualPlanState(VisualPlanInputState[ActionT]):  # type: ignore[misc]
    screenshot: str = Field(default='')
    output: VisualPlanOutput[ActionT] = Field(default_factory=VisualPlanOutput[ActionT])  # type: ignore[misc]
