from fastapi                                                                          import Response, HTTPException
from starlette.status                                                                 import HTTP_400_BAD_REQUEST
from mgraph_ai.providers.json.domain.Domain__MGraph__Json__Graph                      import Domain__MGraph__Json__Graph
from mgraph_ai.providers.simple.domain.Domain__Simple__Graph                          import Domain__Simple__Graph
from mgraph_ai_serverless.graph_engines.matplotlib.models.Model__Matplotlib__Render   import Model__Matplotlib__Render
from mgraph_ai_serverless.graph_engines.matplotlib.Matplotlib__Render                 import Matplotlib__Render
from osbot_fast_api.api.Fast_API_Routes                                               import Fast_API_Routes

ROUTES__MATPLOTLIB__RENDER = ['/render-graph']

DOMAIN_TYPES = { 'Domain__Simple__Graph'      : Domain__Simple__Graph       ,                           # allow-list of supported domain types
                 'Domain__MGraph__Json__Graph': Domain__MGraph__Json__Graph }

class Routes__Matplotlib(Fast_API_Routes):
    tag                : str = 'matplotlib'
    matplotlib__render : Matplotlib__Render

    def render_graph(self, matplotlib_render: Model__Matplotlib__Render) -> Response:
        try:
            bytes_data = self.matplotlib__render.render_graph(matplotlib_render)                                           # Generate the image
        except ValueError as value_error:
            raise HTTPException(status_code = HTTP_400_BAD_REQUEST,
                                detail      = value_error.args[0]        )

        if type(matplotlib_render.output_format) is str:
            format_type = matplotlib_render.output_format
        else:
            format_type = matplotlib_render.output_format.value
        return Response(content=bytes_data,
                       media_type=f"image/{format_type}")

    def setup_routes(self):
        self.add_route(self.render_graph, methods=['POST'])