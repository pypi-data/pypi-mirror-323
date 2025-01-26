import io

from starlette.responses                                                         import StreamingResponse, Response
from mgraph_ai_serverless.graph_engines.playwright.models.Model__Render__Mermaid import Model__Render__Mermaid
from osbot_utils.utils.Http                                                      import url_join_safe
from mgraph_ai_serverless.graph_engines.playwright.web_root.Web_Root__Render     import Web_Root__Render
from osbot_fast_api.api.Fast_API_Routes                                          import Fast_API_Routes

URL__LOCAL_SERVER = 'http://localhost:8080/static'
#URL__LOCAL_SERVER = 'http://localhost:7770/static'

class Routes__Web_Root(Fast_API_Routes):
    tag            : str = 'web_root'
    web_root_render: Web_Root__Render

    def render_file(self, target_page = 'examples/hello-world.html'):
        target_url = self.target_url(target_page=target_page)
        run_data   = self.web_root_render.render_page(target_url)
        screenshot_bytes = run_data.get('screenshot_bytes')

        screenshot_stream = io.BytesIO(screenshot_bytes)
        response          = StreamingResponse(screenshot_stream,
                                              media_type = "image/png",
                                              headers    = {"Content-Disposition": "attachment; filename=screenshot.png"})
        return response

    def render_mermaid(self, render_mermaid: Model__Render__Mermaid) -> Response:

        js_code = f"""
                    new_graph = `{render_mermaid.mermaid_code}`
                    document.querySelector('.mermaid').innerHTML = new_graph
                        document.querySelector('.mermaid').removeAttribute('data-processed');
                    
                    mermaid.init(undefined, ".mermaid");
                    """

        target_url = self.target_url('mermaid/index.html')
        run_data = self.web_root_render.render_page(target_url, js_code=js_code)
        screenshot_bytes = run_data.get('screenshot_bytes')

        screenshot_stream = io.BytesIO(screenshot_bytes)
        response = StreamingResponse(screenshot_stream,
                                     media_type="image/png",
                                     headers={"Content-Disposition": "attachment; filename=screenshot.png"})
        return response

    def render_js(self, target_page = 'examples/hello-world.html'):
        js_code = """
                        document.body.style.backgroundColor = "black";
                        document.body.style.color           = "white";
                        document.body.innerHTML = '<h1>Dynamic JS</h1>';
                   """

        target_url = self.target_url(target_page=target_page)
        run_data   = self.web_root_render.render_page(target_url, js_code=js_code)
        screenshot_bytes = run_data.get('screenshot_bytes')

        screenshot_stream = io.BytesIO(screenshot_bytes)
        response          = StreamingResponse(screenshot_stream,
                                              media_type = "image/png",
                                              headers    = {"Content-Disposition": "attachment; filename=screenshot.png"})
        return response

    def target_url(self, target_page='examples/hello-world.html'):
        return url_join_safe(URL__LOCAL_SERVER, target_page)

    def setup_routes(self):
        self.add_route_get (self.render_file   )
        self.add_route_get (self.target_url    )
        self.add_route_get (self.render_js     )
        self.add_route_post(self.render_mermaid)