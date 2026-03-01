import asyncio
import base64
import json

from pounce.browser.drawing import PageDrawing


class PageMock():
    def __init__(self, page):
        self._page = page

    async def mock_api(self, api_path, mock_data, status=200):
        await self._page.route(
            f'**{api_path}*',
            lambda route: route.fulfill(
                status=status,
                content_type='application/json',
                body=json.dumps(mock_data)
            )
        )


class PageAction():

    def __init__(self, page):
        self._page = page
        self.drawing = PageDrawing(page)
        self.mock = PageMock(page)

    @property
    def url(self):
        return self._page.url

    @property
    def viewport_size(self):
        return self._page.viewport_size

    def is_blank(self):
        return self._page.url == 'about:blank'

    async def navigate(self, url: str):
        await self._page.goto(url, timeout=50000)

    async def click(self, x: int, y: int):
        await self._page.mouse.click(x, y)

    async def input_text(self, x: int, y: int, text: str, wait_time: float = 0.2):
        await self._page.mouse.click(x, y)
        await asyncio.sleep(wait_time)
        await self._page.keyboard.press('Control+A')
        await self._page.keyboard.press('Delete')
        await self._page.keyboard.type(text)

    async def scroll(self, direction: str, distance: int):
        if direction == 'down':
            await self._page.mouse.wheel(0, distance)
        if direction == 'up':
            await self._page.mouse.wheel(0, 0 - distance)

    async def screenshot(self, timeout: int = 30000, full_page: bool = False) -> str:
        content = await self._page.screenshot(timeout=timeout, full_page=full_page)
        result = base64.b64encode(content).decode('utf-8')
        return result
