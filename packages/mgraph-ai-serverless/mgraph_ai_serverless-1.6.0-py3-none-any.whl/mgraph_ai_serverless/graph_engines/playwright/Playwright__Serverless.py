from osbot_utils.type_safe.Type_Safe                import Type_Safe
from osbot_playwright.playwright.api.Playwright_CLI import Playwright_CLI
from playwright.async_api                           import async_playwright, Playwright, Browser, Page, Response
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self


class Playwright__Serverless(Type_Safe):
    browser        : Browser             = None
    page           : Page                = None
    playwright     : Playwright          = None
    playwright_cli : Playwright_CLI
    response       : Response            = None
    screenshot     : bytes               = None

    async def new_page(self):
        browser   = await self.launch()
        self.page = await browser.new_page()
        return self.page

    async def goto(self, url) -> Response:
        self.response = await self.page.goto(url)
        return self.response

    async def launch(self):
        if self.browser is None:
            playwright   = await self.start()
            self.browser = await playwright.chromium.launch(**self.browser__launch_kwargs())
        return self.browser

    async def start(self) -> Playwright:
        if self.playwright is None:
            self.playwright = await async_playwright().start()
        return self.playwright

    async def stop(self):
        if self.playwright:
            await self.playwright.stop()

    async def screenshot_bytes(self, full_page=False, path=None, **kwargs):
        self.screenshot = await self.page.screenshot(full_page=full_page, path=path, **kwargs)
        return self.screenshot

    # sync methods

    def browser__exists(self):
        return self.playwright_cli.browser_installed__chrome()

    def browser__install(self):                                     # todo: see if we use the version that was downloaded during the docker image install
        if self.browser__exists() is False:                         #       which is downloaded to: /root/.cache/ms-playwright/chromium-1134
            return self.playwright_cli.install__chrome()            #       and                   : /root/.cache/ms-playwright/ffmpeg-1010
        return True

    def browser__launch_kwargs(self):
        return dict(args=["--disable-gpu", "--single-process"],
                    executable_path=self.chrome_path())

    @cache_on_self
    def chrome_path(self):
        return self.playwright_cli.executable_path__chrome()