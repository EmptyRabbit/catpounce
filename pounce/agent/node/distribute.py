from langchain_core.messages import HumanMessage
from langgraph.runtime import Runtime

from pounce.agent.schema.agent_schema import PounceContext, PounceState, AssertionOutput
from pounce.model.base import BaseLLMModel


class DistributeNode():

    def __init__(self, model: BaseLLMModel):
        self.model = model

    def is_init(self, step_id):
        return step_id <= 0

    async def distribute(self, state: PounceState):
        if self.is_init(state.step_id):
            subtasks = [
                '访问 http://localhost:3000/360-profile',
                '输入 ID值 在ID输入框中（例如：输入测试用户的ID值:_TIHK1s65mzzap2s6）',
                '点击 查询按钮',
                '滚动 页面到行程可视化组件区域',
                '点击 行程可视化图表中的航班点'
            ]
            next_task = subtasks.pop(0)
            return {
                'subtasks': subtasks,
                'user_message': next_task
            }

        next_task = state.subtasks.pop(0)
        state.finished_subtasks.append(state.user_message)

        return {
            'finished_subtasks': state.finished_subtasks,
            'subtasks': state.subtasks,
            'user_message': next_task
        }
