from osbot_utils.type_safe.Type_Safe import Type_Safe

from mgraph_ai_serverless.graph_engines.playwright.Playwright__Serverless import Playwright__Serverless
from osbot_utils.utils.Misc                                     import bytes_to_base64
from osbot_utils.helpers.flows.decorators.task                  import task
from playwright.async_api                                       import Browser
from osbot_utils.helpers.flows.Flow                             import Flow
from osbot_utils.helpers.flows.decorators.flow                  import flow

class Flow__Playwright__Get_Page_Pdf(Type_Safe):             # refactor with Flow__Playwright__Get_Page_Html since 90% of the code is the same

    playwright_serverless : Playwright__Serverless
    url                   : str = 'https://httpbin.org/get'

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
        import asyncio
        await asyncio.sleep(1)

    @task()
    async def capture_pdf(self, flow_data: dict) -> Browser:
        pdf_bytes = await self.playwright_serverless.page.pdf(print_background=True)
        flow_data['pdf_bytes'] = pdf_bytes
        print(f"got pdf_bytes with size: {len(pdf_bytes)}")

    @task()
    def convert_to_base64(self, flow_data: dict) -> Browser:
        pdf_bytes               = flow_data['pdf_bytes']
        pdf_base64              = bytes_to_base64(pdf_bytes)
        flow_data['pdf_base64'] = pdf_base64
        print(f"converted to base64 with size: {len(pdf_base64)}")

    @flow()
    async def flow_playwright__get_page_pdf(self) -> Flow:
        self.check_config()
        await self.launch_browser()
        await self.new_page      ()
        await self.open_url      ()
        await self.capture_pdf   ()
        self.convert_to_base64   ()
        return 'all done'

    def run(self):
        with self.flow_playwright__get_page_pdf() as _:
            _.execute_flow()
            return _.data