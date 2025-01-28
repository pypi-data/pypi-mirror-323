from osbot_utils.utils.Objects                                                        import type_full_name
from mgraph_ai.mgraph.domain.Domain__MGraph__Graph                                    import Domain__MGraph__Graph
from mgraph_ai.providers.json.domain.Domain__MGraph__Json__Graph                      import Domain__MGraph__Json__Graph
from mgraph_ai.providers.simple.domain.Domain__Simple__Graph                          import Domain__Simple__Graph
from mgraph_ai_serverless.graph_engines.matplotlib.models.Model__Matplotlib__Render   import Model__Matplotlib__Render
from mgraph_ai_serverless.graph_engines.matplotlib.MGraph__Export__Matplotlib         import MGraph__Export__Matplotlib
from osbot_utils.type_safe.Type_Safe                                                  import Type_Safe

DOMAIN_TYPES = { type_full_name(Domain__MGraph__Graph      ) : Domain__MGraph__Graph       ,        # todo: see if there is a better way to do this (that is safe and doesn't allow any type of class from being created)
                 type_full_name(Domain__Simple__Graph      ) : Domain__Simple__Graph       ,                           # allow-list of supported domain types
                 type_full_name(Domain__MGraph__Json__Graph) : Domain__MGraph__Json__Graph }

class Matplotlib__Render(Type_Safe):


    def create_graph_from_graph_data(self, graph_data):
        if not graph_data:
            raise ValueError("No graph provided for rendering")

        graph_type  = graph_data.get('graph_type')
        domain_type = DOMAIN_TYPES.get(graph_type)                    # Get the domain type class that match the supplied graph_data
        if not domain_type:
            raise ValueError(f"Unsupported domain type: {graph_type}")
        return domain_type.from_json(graph_data)                      # Reconstruct the graph from JSON

    def render_graph(self, matplotlib_render: Model__Matplotlib__Render) -> bytes:         # Main render method
        graph_data       = matplotlib_render.graph_data
        graph            = self.create_graph_from_graph_data(graph_data=graph_data)
        screenshot_bytes = self.create_image(matplotlib_render=matplotlib_render, graph=graph)
        return screenshot_bytes

    def create_image(self, matplotlib_render: Model__Matplotlib__Render, graph: Domain__MGraph__Graph) -> bytes:
        with MGraph__Export__Matplotlib(graph=graph) as _:
            _.process_graph()

            render_params = { 'layout'     : matplotlib_render.layout         ,                 # Extract render parameters
                              'figsize'    : matplotlib_render.figsize        ,
                              'node_size'  : matplotlib_render.node_size      ,
                              'node_color' : matplotlib_render.node_color     ,
                              'format'     : matplotlib_render.output_format  ,
                              'dpi'        : matplotlib_render.dpi            }

            return _.to_image(**render_params)                                           # Generate the image

    # def process_graph(self) -> Dict[str, Any]:                                              # Process graph to data format
    #     if not self.graph:
    #         raise ValueError("No graph provided for processing")
    #
    #     exporter = self.create_exporter()
    #     return exporter.process_graph()                                                    # Use the existing format_output method