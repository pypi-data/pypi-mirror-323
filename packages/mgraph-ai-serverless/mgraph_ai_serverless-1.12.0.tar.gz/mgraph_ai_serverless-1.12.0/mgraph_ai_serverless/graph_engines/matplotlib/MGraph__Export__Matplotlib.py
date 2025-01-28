import matplotlib
matplotlib.use('Agg')

import networkx          as nx
import matplotlib.pyplot as plt
from typing                                                     import Dict, Any, Optional
from mgraph_ai.mgraph.actions.exporters.MGraph__Export__Base    import MGraph__Export__Base
from io                                                         import BytesIO

class MGraph__Export__Matplotlib(MGraph__Export__Base):

    def create_node_data(self, node) -> Dict[str, Any]:
        return { 'id'    : str(node.node_id)                ,
                 'type'  : node.node.data.node_type.__name__,
                 'label' : self.get_node_label(node)        }

    def create_edge_data(self, edge) -> Dict[str, Any]:
        return { 'id'     : str(edge.edge_id       )        ,
                 'source' : str(edge.from_node_id())        ,
                 'target' : str(edge.to_node_id  ())        ,
                 'type'   : edge.edge.data.edge_type.__name__}

    def get_node_label(self, node) -> str:
        for attr in ('label', 'name', 'value'):
            node_label = getattr(node.node_data, attr, None)
            if node_label:
                return str(node_label)
        return node.node.data.node_type.__name__

    def to_networkx(self) -> nx.Graph:
        """Convert the graph to a NetworkX graph object"""
        G = nx.Graph()

        # Process all nodes first
        for node in self.graph.nodes():
            node_data = self.create_node_data(node)
            G.add_node(node_data['id'], **node_data)

        # Then process all edges
        for edge in self.graph.edges():
            edge_data = self.create_edge_data(edge)
            G.add_edge(edge_data['source'],
                      edge_data['target'],
                      **edge_data)

        return G

    def to_image(self,
                 layout      : str           = 'spring'    ,
                 figsize    : tuple         = (10, 10)    ,
                 node_size  : int           = 1000        ,
                 node_color : str           = 'lightblue' ,
                 format     : str           = 'png'       ,
                 dpi        : int           = 300         ,
                 **kwargs) -> Optional[str]:
        G = self.to_networkx()


        layouts = { 'spring'   : nx.spring_layout    ,                  # Select layout algorithm
                    'circular' : nx.circular_layout  ,
                    'random'   : nx.random_layout    ,
                    'shell'    : nx.shell_layout     ,
                    'spectral' : nx.spectral_layout  }
        layout_func = layouts.get(layout, nx.spring_layout)
        pos = layout_func(G)

        plt.figure(figsize=figsize)                                     # Create figure

        # Draw the graph
        nx.draw(G,
                pos         = pos       ,
                with_labels = True      ,
                node_color  = node_color,
                node_size   = node_size ,
                labels      = {node: G.nodes[node]['label'] for node in G.nodes()},
                **kwargs)


        buffer = BytesIO()                                                          # Save to bytes buffer
        plt.savefig(buffer, format=format, dpi=dpi, bbox_inches='tight')
        plt.close()

        buffer.seek(0)
        return buffer.getvalue()                                                    # return bytes

    def format_output(self) -> Dict[str, Any]:                  # Format the processed data including positions for visualization

        base_output = super().format_output()                   # Get base output from parent class

        G = self.to_networkx()                                  # Calculate positions using NetworkX
        pos = nx.spring_layout(G)                               # Calculate positions


        pos_dict = {str(node): { 'x': float(coords[0]),         # Convert positions to serializable format
                                 'y': float(coords[1])}
                    for node, coords in pos.items()}


        nodes_with_positions = []                               # Add positions to the existing node data
        for node in base_output['nodes']:
            node_data             = node.copy()                 # Make a copy to avoid modifying original
            node_data['position'] = pos_dict[node['id']]
            nodes_with_positions.append(node_data)

        return { 'nodes': nodes_with_positions,
                 'edges': base_output['edges']}