import graphviz

from mgraph_ai_serverless.graph_engines.graphviz.models.Model__Graphviz__Render_Dot import Model__Graphviz__Render_Dot
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe


class Graphviz__Render(Type_Safe):

    def render_dot(self, render_config: Model__Graphviz__Render_Dot)-> bytes:
        dot_source    = render_config.dot_source
        output_format = render_config.output_format
        dot           = graphviz.Source(dot_source)
        return dot.pipe(format=output_format)