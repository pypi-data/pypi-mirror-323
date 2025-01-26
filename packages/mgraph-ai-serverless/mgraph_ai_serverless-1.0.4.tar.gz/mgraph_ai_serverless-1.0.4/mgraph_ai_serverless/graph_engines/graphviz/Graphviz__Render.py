import graphviz
from osbot_utils.type_safe.Type_Safe import Type_Safe


class Graphviz__Render(Type_Safe):

    def render_dot(self, dot_source: str, directory='/tmp', filename='dot-render', output_format="png") -> bytes   :# Create a Digraph from the source
        dot = graphviz.Source(dot_source)
        kwargs = dict(directory = directory     ,
                      filename  = filename      ,
                      format    = output_format)

        return dot.render(**kwargs)