import networkx as nx
import matplotlib.pyplot as plt
from io import StringIO

def create_test_svg():
    """Create a very simple test SVG with explicit node IDs and a clear path."""
    return """<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <!-- Input node -->
    <circle cx="20" cy="20" r="5" id="input_node"/>
    
    <!-- Hidden layer node -->
    <circle cx="50" cy="50" r="5" id="hidden_node"/>
    
    <!-- Output node -->
    <circle cx="80" cy="80" r="5" id="output_node"/>
    
    <!-- Edges -->
    <path d="M 20 20 L 50 50" id="edge1"/>
    <path d="M 50 50 L 80 80" id="edge2"/>
</svg>
"""

def test_svg_parsing():
    """Test SVG parsing and rendering with debug output."""
    from phart.svg import SVGRenderer, SVGParser
    
    # Create test SVG
    svg_content = create_test_svg()
    
    # Debug: Print the SVG content
    print("Original SVG content:")
    print(svg_content)
    
    # Create parser and graph for debugging
    parser = SVGParser()
    graph, options = parser.parse_svg(svg_content)
    
    # Debug: Print graph information
    print("\nGraph information:")
    print(f"Nodes: {list(graph.nodes())}")
    print(f"Edges: {list(graph.edges())}")
    
    print("\nRendered ASCII:")
    renderer = SVGRenderer.from_svg(svg_content, node_spacing=4, layer_spacing=2)
    print(renderer.render())

if __name__ == "__main__":
    test_svg_parsing()
