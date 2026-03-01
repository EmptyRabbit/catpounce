from langchain_core.messages import HumanMessage
from langgraph.runtime import Runtime

from pounce.agent.schema.agent_schema import PounceContext, PounceState, AssertionOutput
from pounce.agent.trajectory import LogTrajectory
from pounce.model.base import BaseLLMModel


class ActionCheckNode():

    def __init__(self, model: BaseLLMModel):
        self.model = model

    async def check(self, state: PounceState, runtime: Runtime[PounceContext]):
        if not state.planning_screenshot:
            state.history_items[-1].action_result = state.action_result
            return {'history_items': state.history_items}

        current_screenshot = await runtime.context.browser.page.screenshot()
        content = [
            {
                "type": "text",
                "text": f"Please understand the goal of the operation: '{state.output.action_prompt}', and use the screenshots before and after the operation to determine whether the operation was successful."
                        f"The following is a screenshot before the operation. If there is a red box, the area circled in the red box represents the planned operation area."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{state.planning_screenshot}"
                }
            },
            {
                "type": "text",
                "text": "The following is a current screenshot after the operation:"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{current_screenshot}"
                }
            },
            {
                "type": "text",
                "text": """
                    You must ALWAYS respond with a valid JSON in this exact format:
                    {{
                        "passed": "Whether the check passes (true/false)",
                        "thinking": "The basis for your judgment and analysis process",
                        "confidence": "Confidence level (0–1) float number",
                        "message": "If the check fails, explain the specific reason"
                    }}
                """
            },
        ]
        messages = [HumanMessage(content=content)]
        model = self.model.with_structured_output(AssertionOutput)
        output: AssertionOutput = await model.ainvoke(messages)

        if output.passed:
            action_result = f'Action executed successful. Please continue plan next action.'
        else:
            action_result = f'Not complete action, detail is {output.message}. Please consider the reasons and make corrections in the next plan.'

        state.history_items[-1].action_result = action_result
        LogTrajectory.action_log(state)
        return {
            'history_items': state.history_items,
            'action_result': action_result
        }
