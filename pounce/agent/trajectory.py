import logging
from typing import List

from langgraph.runtime import Runtime

from pounce.agent.schema.agent_schema import PounceContext, PounceState
from pounce.utils.image_util import ImageUtil

logger = logging.getLogger(__name__)


class LogTrajectory():

    @staticmethod
    def action_log(state: PounceState):
        logger.info(f'------------ [Step {state.step_id}] Action ------------')
        logger.info(f'thinking: {state.output.thinking}')
        logger.info(f'action_prompt: {state.output.action_prompt}')
        logger.info(f'action: {state.output.action}')
        logger.info(f'action_result: {state.action_result} \n')

        if not state.output.action or state.output.action.type != 'Assert':
            return {}

        logger.info(f'------------ [Step {state.step_id}] Assertion ------------')
        logger.info(f'thinking: {state.assert_output.thinking}')
        logger.info(f'passed: {state.assert_output.passed}')
        logger.info(f'message: {state.assert_output.message}')
        logger.info(f'confidence: {state.assert_output.confidence} \n')

        return {}


class ReportTrajectory():
    @staticmethod
    async def screenshot(
            state: PounceState,
            runtime: Runtime[PounceContext],
            image_name: str = '',
            bbox_list: List[List[int]] = None,
            is_draw_box: bool = False
    ):
        try:
            if is_draw_box:
                for bbox in bbox_list:
                    await runtime.context.browser.page.drawing.draw_box(bbox)

            base64_str = await runtime.context.browser.page.screenshot()
            ImageUtil.save_png(base64_str, state.report_path, f'step_{state.step_id}_{image_name}.png')

            return base64_str
        finally:
            if is_draw_box:
                await runtime.context.browser.page.drawing.clear_box()
