import networkx as nx
from phart import LayoutOptions, ASCIIRenderer, NodeStyle

G = nx.DiGraph(
            [
                ("A", "B"),
                ("A", "C"),
                ("B", "D"),
                ("C", "D"),
                ("D", "E"),
                ("B", "C"),
                ("E", "F"),
                ("F", "D"), 
            ]
        )
ASCIIRenderer(G).draw()
options = LayoutOptions(
    node_style=NodeStyle.MINIMAL, node_spacing=6, layer_spacing=4
)
ASCIIRenderer(G, options=options).draw()

