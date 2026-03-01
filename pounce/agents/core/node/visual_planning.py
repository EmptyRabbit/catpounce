from typing import Any, List, Dict, Generic

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime

from pounce.agents.trajectory import ReportTrajectory
from pounce.agents.core.state import ActionT, VisualPlanState, VisualPlanHistoryItem, VisualPlanOutput
from pounce.model.base import BaseLLMModel


class VisualPlanningNode(Generic[ActionT]):

    def __init__(self, model: BaseLLMModel):
        self.model = model

    @staticmethod
    def get_agent_history(history_items: List[VisualPlanHistoryItem[ActionT]]) -> str:
        if not history_items:
            return 'Agent initialized'

        result = ''
        for index, item in enumerate(history_items, 1):
            result += f"""
            <step_{index}>
            Thinking: {item.thinking}
            Action Description: {item.action_prompt}
            Action Result: {item.action_result}
            </step_{index}>
            """
        return result

    @staticmethod
    def get_step_content(user_message: str, agent_history: str) -> str:
        result = f"""
        <agent_history>
        {agent_history}
        </agent_history>
        <user_request>
        {user_message}
        </user_request>
        """
        return result

    async def get_next_action(self, state: VisualPlanState[ActionT]) -> Dict[str, Any]:
        state.step_id += 1
        agent_history = self.get_agent_history(state.history_items)
        step_content = self.get_step_content(state.user_message, agent_history)

        content = [{"type": "text", "text": step_content}]
        if state.screenshot:
            content.extend(
                [
                    {
                        "type": "text",
                        "text": "The current screenshot:"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{state.screenshot}"
                        }
                    }
                ]
            )

        messages = [SystemMessage(content=self.system_message), HumanMessage(content=content)]
        model = self.model.with_structured_output(VisualPlanOutput[ActionT])  # type: ignore[misc]
        output: VisualPlanOutput = await model.ainvoke(messages)

        history = VisualPlanHistoryItem(
            thinking=output.thinking,
            action_prompt=output.action_prompt,
            action=output.action.model_dump()
        )
        return {
            'output': output,
            'history_items': [*state.history_items, history]
        }
