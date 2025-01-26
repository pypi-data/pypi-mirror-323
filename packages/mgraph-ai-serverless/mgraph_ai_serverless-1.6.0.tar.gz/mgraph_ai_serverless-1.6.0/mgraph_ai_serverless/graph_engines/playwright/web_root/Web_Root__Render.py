from mgraph_ai_serverless.graph_engines.playwright.flows.Flow__Playwright__Get_Page_Screenshot  import Flow__Playwright__Get_Page_Screenshot
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe


class Web_Root__Render(Type_Safe):


    def render_page(self, target_url, js_code=None):
        with Flow__Playwright__Get_Page_Screenshot() as _:
            _.url     = target_url
            _.js_code = js_code
            run_data = _.run()
            return run_data

