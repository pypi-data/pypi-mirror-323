from dataclasses                                                                        import dataclass
from osbot_utils.helpers.Safe_Id                                                        import Safe_Id
from mgraph_ai_serverless.graph_engines.graphviz.models.Model__Graphviz__Output_Format  import Model__Graphviz__Output_Format

GRAPHVIZ__DOT__SAMPLE_GRAPH_1 = """\
digraph NodeAttributes {
    A [shape=box, color=blue];
    B [shape=ellipse, color=green];
    C [shape=diamond, color=red];
    A -> B;
    B -> C;
    C -> A;
}"""


@dataclass
class Model__Graphviz__Render_Dot:
    dot_source     : str                            = GRAPHVIZ__DOT__SAMPLE_GRAPH_1
    #output_file_name: Safe_Id                        = Safe_Id('graphviz_render_dot')
    #output_file_name : str                          = 'graphviz_render_dot'
    output_format  : Model__Graphviz__Output_Format = Model__Graphviz__Output_Format.png
