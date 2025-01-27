from typing                                                                           import Dict, Any
from mgraph_ai.mgraph.domain.Domain__MGraph__Graph                                    import Domain__MGraph__Graph
from mgraph_ai_serverless.graph_engines.matplotlib.models.Model__Matplotlib__Render   import Model__Matplotlib__Render
from mgraph_ai_serverless.graph_engines.matplotlib.MGraph__Export__Matplotlib         import MGraph__Export__Matplotlib
from osbot_utils.decorators.methods.cache                                             import cache
from osbot_utils.type_safe.Type_Safe                                                  import Type_Safe


class Matplotlib__Render(Type_Safe):
    graph: Domain__MGraph__Graph                                                            # The graph to render

    @cache
    def create_exporter(self) -> MGraph__Export__Matplotlib:                               # Create and cache the exporter
        return MGraph__Export__Matplotlib(graph=self.graph)

    def render_graph(self, matplotlib_render: Model__Matplotlib__Render) -> bytes:         # Main render method
        if not self.graph:
            raise ValueError("No graph provided for rendering")

        exporter = self.create_exporter()


        render_params = { 'layout'     : matplotlib_render.layout         ,                 # Extract render parameters
                          'figsize'    : matplotlib_render.figsize        ,
                          'node_size'  : matplotlib_render.node_size      ,
                          'node_color' : matplotlib_render.node_color     ,
                          'format'     : matplotlib_render.output_format  ,
                          'dpi'        : matplotlib_render.dpi            }

        return exporter.to_image(**render_params)                                           # Generate the image

    def process_graph(self) -> Dict[str, Any]:                                              # Process graph to data format
        if not self.graph:
            raise ValueError("No graph provided for processing")

        exporter = self.create_exporter()
        return exporter.process_graph()                                                    # Use the existing format_output method