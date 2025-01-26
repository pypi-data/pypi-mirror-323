import networkx as nx
from phart import ASCIIRenderer

G = nx.DiGraph()
G.add_edges_from([("Alice","Bob"), ("Bob", "Alice"), ("Bob", "Charlie"), ("Charlie", "Bob"), ("David","Alice"), ("David", "Bob")])
G.add_edges_from([("1","2"), ("2", "1"), ("2", "3"), ("3", "2"), ("4", "3"), ("5", "4"), ("1", "5")])

# Render it in ASCII
renderer = ASCIIRenderer(G)
print(renderer.render())

## test new .draw() method
renderer.draw()

# Bug: this is not bidirectional :(
#
#   [1]
#    ↑
#   [2]
#    ↑
#   [3]
