import io

from mgraph_ai_serverless.graph_engines.playwright.Playwright__Serverless                       import Playwright__Serverless
from mgraph_ai_serverless.graph_engines.playwright.steps.Flow__Playwright__Get_Page_Html        import Flow__Playwright__Get_Page_Html
from mgraph_ai_serverless.graph_engines.playwright.steps.Flow__Playwright__Get_Page_Pdf         import Flow__Playwright__Get_Page_Pdf
from mgraph_ai_serverless.graph_engines.playwright.steps.Flow__Playwright__Get_Page_Screenshot  import Flow__Playwright__Get_Page_Screenshot
from osbot_fast_api.api.Fast_API_Routes                                                         import Fast_API_Routes
from starlette.responses                                                                        import StreamingResponse

ROUTES__EXPECTED_PATHS__BROWSER = ['/browser/install-browser' ,
                                   '/browser/url-html'        ,
                                   '/browser/url-pdf'         ,
                                   '/browser/url-screenshot'  ]

class Routes__Browser(Fast_API_Routes):
    tag : str = 'browser'


    def install_browser(self):
        playwright_browser = Playwright__Serverless()
        result             = playwright_browser.browser__install()
        return dict(status=result)

    def url_html(self, url="https://httpbin.org/get"):
        self.install_browser()                                              # todo: BUG: for now, put the check there to make sure the browser is installed
        with Flow__Playwright__Get_Page_Html() as _:
            _.url = url
            result = _.run()
            return result

    def url_pdf(self, url="https://httpbin.org/get", return_file:bool=False):           # todo: refactor with url_screenshot
        self.install_browser()                                                          # todo:  BUG: for now, put the check there to make sure the browser is installed
        with Flow__Playwright__Get_Page_Pdf() as _:
            _.url = url
            run_data   =_.run()
            pdf_bytes  = run_data.get('pdf_bytes' )
            pdf_base64 = run_data.get('pdf_base64')

            if return_file is True:
                pdf_stream = io.BytesIO(pdf_bytes)
                response = StreamingResponse( pdf_stream,
                                              media_type = "application/pdf",
                                              headers    = {"Content-Disposition": "attachment; filename=document.pdf"})
            else:
                response = {'pdf_base64': pdf_base64}

            return response

    def url_screenshot(self, url="https://httpbin.org/get", return_file:bool=False):
        self.install_browser()                                                           # todo:  BUG: for now, put the check there to make sure the browser is installed
        with Flow__Playwright__Get_Page_Screenshot() as _:
            _.url = url
            run_data = _.run()
            screenshot_base64 = run_data.get('screenshot_base64')
            screenshot_bytes  = run_data.get('screenshot_bytes')
            if return_file:
                screenshot_stream = io.BytesIO(screenshot_bytes)
                response = StreamingResponse(screenshot_stream,
                                             media_type = "image/png",
                                             headers    = {"Content-Disposition": "attachment; filename=screenshot.png"})
            else:
                response = {'screenshot_base64': screenshot_base64}

            return response

    def setup_routes(self):
        self.add_route_get(self.url_html        )
        self.add_route_get(self.url_pdf         )
        self.add_route_get(self.url_screenshot  )
        self.add_route_get(self.install_browser )

        # self.add_route_get(self.launch_browser)
        # self.add_route_get(self.new_page      )

        # self.add_route_get(self.html_2        )
        # self.add_route_get(self.html_async    )