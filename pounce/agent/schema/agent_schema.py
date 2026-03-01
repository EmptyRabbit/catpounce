from typing import List

from pydantic import BaseModel, Field, ConfigDict

from pounce.agent.schema.action_type import Action
from pounce.browser.browser import Browser


class PounceContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    browser: Browser = Field(default=None)


class PounceOutput(BaseModel):
    thinking: str = Field(default='')
    action_prompt: str = Field(default='')
    action: Action = Field(default=None)


class PounceInputState(BaseModel):
    task_id: str = Field(default='')
    user_message: str = Field(default='')
    max_history_item: int = Field(default=0)
    report_path: str = Field(default='')


class AssertionOutput(BaseModel):
    passed: bool = Field(default=False)
    thinking: str = Field(default='')
    confidence: float = Field(default=0)
    message: str = Field(default='')


class PounceHistoryItem(PounceOutput):
    action_result: str = Field(default='')


class PounceState(PounceInputState):
    step_id: int = Field(default=0)
    subtasks: List[str] = Field(default=[])
    finished_subtasks: List[str] = Field(default=[])

    output: PounceOutput = Field(default_factory=PounceOutput)
    assert_output: AssertionOutput = Field(default_factory=AssertionOutput)

    planning_screenshot: str = Field(default='')
    action_result: str = Field(default='')
    history_items: List[PounceHistoryItem] = Field(default_factory=list)

    def is_planning_continue(self):
        if self.output.action:
            if self.output.action.type == 'done':
                return False
            if self.output.action.type == 'Assert' and self.assert_output.passed is False:
                return False

        return True

    def is_task_finish(self):
        if not self.subtasks and self.finished_subtasks:
            return True

        if self.output.action:
            if self.output.action.type == 'done' and not self.output.action.param.get('success', False):
                return True
            if self.output.action.type == 'Assert' and self.assert_output.passed is False:
                return True

        return False
