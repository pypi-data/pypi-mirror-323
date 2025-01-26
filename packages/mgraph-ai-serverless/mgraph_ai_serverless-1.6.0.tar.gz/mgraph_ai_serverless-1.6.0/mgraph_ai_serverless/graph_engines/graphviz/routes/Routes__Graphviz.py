from fastapi                                                                        import Response
from mgraph_ai_serverless.graph_engines.graphviz.models.Model__Graphviz__Render_Dot import Model__Graphviz__Render_Dot
from mgraph_ai_serverless.graph_engines.graphviz.Graphviz__Render                   import Graphviz__Render
from osbot_fast_api.api.Fast_API_Routes                                             import Fast_API_Routes

ROUTES__GRAPHVIZ__RENDER = ['/render-dot']

class Routes__Graphviz(Fast_API_Routes):
    graphviz_render : Graphviz__Render
    tag             : str = 'graphviz'

    def render_dot(self, graphviz_render_dot: Model__Graphviz__Render_Dot) -> Response:
        bytes_data = self.graphviz_render.render_dot(graphviz_render_dot)
        output_format = graphviz_render_dot.output_format
        return Response(content=bytes_data, media_type=f"image/{output_format.value}")


    def setup_routes(self):
        self.add_route(self.render_dot, methods=['POST'])