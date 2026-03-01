from typing import Dict, Any

from pounce.agents.trajectory import ReportTrajectory


class ScreenshotNode():

    def __init__(self, browser):
        self.browser = browser

    async def screenshot(self, _) -> Dict[str, Any]:
        screenshot_base64 = ''
        if not self.browser.page.is_blank():
            screenshot_base64 = await ReportTrajectory.screenshot(self.browser, image_name='planning')

        return {'screenshot': screenshot_base64}
