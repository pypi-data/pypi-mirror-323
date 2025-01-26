import networkx as nx
from phart import ASCIIRenderer

G = nx.DiGraph()

G.add_edges((1, 2), (2,3), (3,1))

print("circular triangle DAG")
ASCIIRenderer(G).draw()

print("use as undirected. see your doctor if you experience any side effects")
ASCIIRenderer(G.to_undirected()).draw()
