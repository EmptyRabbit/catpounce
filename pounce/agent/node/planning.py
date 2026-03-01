from typing import List, Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime

from pounce.agent.schema.agent_schema import PounceContext, PounceState, PounceHistoryItem, PounceOutput
from pounce.agent.trajectory import ReportTrajectory
from pounce.model.base import BaseLLMModel


class PlanningNode():

    def __init__(self, model: BaseLLMModel, system_message: str):
        self.model = model
        self.system_message = system_message

    @staticmethod
    def get_agent_history(history_items: List[PounceHistoryItem]) -> str:
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

    async def get_next_action(self, state: PounceState, runtime: Runtime[PounceContext]) -> Dict[str, Any]:
        state.step_id += 1
        agent_history = self.get_agent_history(state.history_items)
        step_content = self.get_step_content(state.user_message, agent_history)

        content = [{"type": "text", "text": step_content}]
        if state.planning_screenshot:
            content.extend(
                [
                    {
                        "type": "text",
                        "text": "The screenshot of the last planning result:"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{state.planning_screenshot}"
                        }
                    }
                ]
            )
        if not runtime.context.browser.page.is_blank():
            screenshot_base64 = await ReportTrajectory.screenshot(state, runtime, image_name='planning')
            content.extend(
                [
                    {
                        "type": "text",
                        "text": "The current screenshot:"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{screenshot_base64}"
                        }
                    }
                ]
            )

        messages = [SystemMessage(content=self.system_message), HumanMessage(content=content)]
        model = self.model.with_structured_output(PounceOutput)
        output: PounceOutput = await model.ainvoke(messages)

        history = PounceHistoryItem(
            thinking=output.thinking,
            action_prompt=output.action_prompt,
            action=output.action.model_dump()
        )
        return {
            'output': output,
            'history_items': [*state.history_items[-state.max_history_item:], history],
            'step_id': state.step_id
        }
