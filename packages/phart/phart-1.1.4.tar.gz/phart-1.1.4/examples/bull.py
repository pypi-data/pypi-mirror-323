import networkx as nx
import phart

print("Bull Graph:")
G = nx.bull_graph()
options = phart.LayoutOptions(node_style=phart.NodeStyle.MINIMAL, node_spacing=6, layer_spacing=4)
phart.ASCIIRenderer(G, options=options).draw()
print(G.edges())

print("Converted to digraph:")
G = nx.DiGraph(G)  # Convert to directed
phart.ASCIIRenderer(G, options=options).draw()
print(G.edges())

###
(.venv-win) C:\Users\scott\source\phart> python examples\bull.py
Bull Graph:
      +----- 1
      |      |
      |      |
      |      |
      0------2----- 3
             |
             |
             |
             4


[(0, 1), (0, 2), (1, 2), (1, 3), (2, 4)]
Converted to digraph:
      +----- 1 -----+
      |      |      |
      |      |      |
      |      |      |
      0------2----- 3
             |
             |
             |
             4

