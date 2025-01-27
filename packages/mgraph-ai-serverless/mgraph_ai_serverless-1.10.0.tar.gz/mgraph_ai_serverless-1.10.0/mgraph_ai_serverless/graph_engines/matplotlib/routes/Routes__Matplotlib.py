from fastapi                                                                          import Response, HTTPException
from starlette.status                                                                 import HTTP_400_BAD_REQUEST
from mgraph_ai.providers.simple.domain.Domain__Simple__Graph                          import Domain__Simple__Graph
from mgraph_ai_serverless.graph_engines.matplotlib.models.Model__Matplotlib__Render   import Model__Matplotlib__Render
from mgraph_ai_serverless.graph_engines.matplotlib.Matplotlib__Render                 import Matplotlib__Render
from osbot_fast_api.api.Fast_API_Routes                                               import Fast_API_Routes

ROUTES__MATPLOTLIB__RENDER = ['/render-graph']

DOMAIN_TYPES = {
    'Domain__Simple__Graph': Domain__Simple__Graph,
    # Add other domain types here as needed
}

class Routes__Matplotlib(Fast_API_Routes):
    tag: str = 'matplotlib'

    def render_graph(self, matplotlib_render: Model__Matplotlib__Render) -> Response:
        if not matplotlib_render.graph_data:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                                detail="No graph data provided for rendering" )
        if not matplotlib_render.domain_type_name:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                                detail="No domain type specified")

        domain_type = DOMAIN_TYPES.get(matplotlib_render.domain_type_name)                          # Get the correct domain type class
        if not domain_type:
            raise HTTPException(status_code = HTTP_400_BAD_REQUEST,
                                detail      = f"Unsupported domain type: {matplotlib_render.domain_type_name}")

        graph      = domain_type.from_json(matplotlib_render.graph_data)                                # Reconstruct the graph from JSON
        renderer   = Matplotlib__Render(graph=graph)                                                    # Create a new renderer for this request
        bytes_data = renderer.render_graph(matplotlib_render)                                           # Generate the image
        if type(matplotlib_render.output_format) is str:
            format_type = matplotlib_render.output_format
        else:
            format_type = matplotlib_render.output_format.value
        return Response(content=bytes_data,
                       media_type=f"image/{format_type}")

    def setup_routes(self):
        self.add_route(self.render_graph, methods=['POST'])