from playwright.async_api import PlaywrightContextManager

from pounce.browser.action import PageAction


class Browser(PlaywrightContextManager):
    def __init__(self, headless: bool=False, viewport_width=1920, viewport_height=1080):
        super().__init__()
        self.headless = headless
        self._browser = None
        self._context = None
        self._page = None

    @property
    def instance(self):
        return self._browser

    @property
    def page(self):
        page_action = PageAction(self._page)
        return page_action

    @page.setter
    def page(self, value):
        self._page = value

    async def __aenter__(self) -> "Browser":
        playwright = await super().__aenter__()
        self._browser = await playwright.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False
        )
        self._page = await self._context.new_page()
        await self._page.evaluate("document.body.style.zoom = '100%'")
        return self
