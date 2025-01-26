from mgraph_ai_serverless.graph_engines.playwright.Playwright__Serverless import Playwright__Serverless
from osbot_utils.type_safe.Type_Safe                import Type_Safe
from osbot_utils.helpers.flows.decorators.task      import task
from playwright.async_api                           import Browser
from osbot_utils.helpers.flows.Flow                 import Flow
from osbot_utils.helpers.flows.decorators.flow      import flow

class Flow__Playwright__Get_Page_Html(Type_Safe):

    playwright_serverless : Playwright__Serverless
    url                   : str = 'https://www.google.com'

    @task()
    def check_config(self) -> Browser:
        print('checking config')

    @task()
    async def launch_browser(self) -> Browser:
        await self.playwright_serverless.launch()
        print('launched playwright')

    @task()
    async def new_page(self) -> Browser:
        await self.playwright_serverless.new_page()

    @task()
    async def open_url(self) -> Browser:
        print(f"opening url: {self.url}")
        await self.playwright_serverless.goto(self.url)

    @task()
    async def print_html(self, flow_data: dict) -> Browser:
        page_content = await self.playwright_serverless.page.content()
        flow_data['page_content'] = page_content
        print(f"got page content with size: {len(page_content)}")

    @flow()
    async def flow_playwright__get_page_html(self) -> Flow:
        self.check_config()
        await self.launch_browser()
        await self.new_page      ()
        await self.open_url      ()
        await self.print_html    ()
        return 'all done'

    def run(self):
        with self.flow_playwright__get_page_html() as _:
            _.execute_flow()
            return _.data