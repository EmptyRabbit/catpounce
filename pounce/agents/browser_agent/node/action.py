import asyncio
import json

from langgraph.runtime import Runtime

from pounce.agent.trajectory import ReportTrajectory
from pounce.agent.schema.agent_schema import PounceContext, PounceState
from pounce.model.base import BaseLLMModel


class ActionExecutorNode():
    def __init__(self, model: BaseLLMModel):
        self.model = model

    async def route(self, state: PounceState, runtime: Runtime[PounceContext]):
        action_type = state.output.action.type
        match action_type:
            case 'Wait':
                result = await self.execute_wait(state)
            case 'Mock':
                result = await self.execute_mock(state, runtime)
            case 'Assert':
                result = await  self.execute_assert(state, runtime)
            case _:
                result = await self.execute_action(state, runtime)

        return result

    async def execute_wait(self, state):
        action_param = state.output.action.param.value
        await asyncio.sleep(action_param)
        return {'action_result': f'Successful wait {action_param} seconds'}

    async def execute_action(self, state: PounceState, runtime: Runtime[PounceContext]):
        browser = runtime.context.browser
        action = state.output.action
        width, height = browser.page.viewport_size['width'], browser.page.viewport_size['height']
        action_type, param = action.type, action.param

        planning_screenshot = ''
        result = ''
        match action_type:
            case 'Navigate':
                await browser.page.navigate(param.url)
                await asyncio.sleep(1)
                result = 'Successful navigate to url'

            case 'Click':
                bbox, x, y = self.model.normalization(param.locate.bbox, width, height)
                planning_screenshot = await ReportTrajectory.screenshot(
                    state=state,
                    runtime=runtime,
                    image_name='action',
                    bbox_list=[bbox],
                    is_draw_box=True
                )

                await browser.page.click(x, y)
                await asyncio.sleep(1)
                result = f'Successful click on "{param.locate.prompt}"'

            case 'Input':
                bbox, x, y = self.model.normalization(param.locate.bbox, width, height)
                planning_screenshot = await ReportTrajectory.screenshot(
                    state=state,
                    runtime=runtime,
                    image_name='action',
                    bbox_list=[bbox],
                    is_draw_box=True
                )

                await browser.page.input_text(x, y, param.value)
                await asyncio.sleep(1)
                result = f'Successful input text "{param.value}"'

            case 'Scroll':
                planning_screenshot = await browser.page.screenshot()

                await browser.page.scroll(param.direction, param.distance)
                await asyncio.sleep(2)
                result = f'Successful scroll {param.direction}'

        return {
            'action_result': result,
            'planning_screenshot': planning_screenshot
        }

    async def execute_mock(self, state: PounceState, runtime: Runtime[PounceContext]):
        browser = runtime.context.browser
        param = state.output.action.param

        await browser.page.mock.mock_api(param.api, json.loads(param.mock_data))
        return {'action_result': f'Successful mock api {param.api}'}