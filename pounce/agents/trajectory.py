import logging
from typing import List

from pounce.browser.browser import Browser
from pounce.utils.image_util import ImageUtil

logger = logging.getLogger(__name__)


class ReportTrajectory():
    @staticmethod
    async def screenshot(
            browser: Browser,
            report_path: str = '',
            image_name: str = '',
            bbox_list: List[List[int]] = None,
            is_draw_box: bool = False
    ):
        try:
            if is_draw_box:
                for bbox in bbox_list:
                    await browser.page.drawing.draw_box(bbox)

            base64_str = await browser.page.screenshot()
            ImageUtil.save_png(base64_str, report_path, f'{image_name}.png')

            return base64_str
        finally:
            if is_draw_box:
                await browser.page.drawing.clear_box()
