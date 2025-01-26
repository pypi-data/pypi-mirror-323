"""Command line interface for PHART."""

import sys
import argparse
import importlib.util
from pathlib import Path
from typing import Optional, Any

from .renderer import ASCIIRenderer
from .styles import NodeStyle, LayoutOptions


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PHART: Python Hierarchical ASCII Rendering Tool"
    )
    parser.add_argument("input", type=Path, help="Input file (.dot, .graphml, or .py format)")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file (if not specified, prints to stdout)",
    )
    parser.add_argument(
        "--style",
        choices=[s.name.lower() for s in NodeStyle],
        default="square",
        help="Node style (default: square)",
    )
    parser.add_argument(
        "--ascii",
        action="store_true",
        help="Force ASCII output (no Unicode box characters)",
    )
    parser.add_argument(
        "--node-spacing",
        type=int,
        default=4,
        help="Horizontal space between nodes (default: 4)",
    )
    parser.add_argument(
        "--layer-spacing",
        type=int,
        default=2,
        help="Vertical space between layers (default: 2)",
    )
    return parser.parse_args()


def load_python_module(file_path: Path) -> Any:
    """
    Dynamically load a Python file as a module.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        Loaded module object
    """
    spec = importlib.util.spec_from_file_location("dynamic_module", file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {file_path}")
        
    module = importlib.util.module_from_spec(spec)
    sys.modules["dynamic_module"] = module
    spec.loader.exec_module(module)
    return module


def create_layout_options(args: argparse.Namespace) -> LayoutOptions:
    """Create LayoutOptions from CLI arguments."""
    return LayoutOptions(
        node_style=NodeStyle[args.style.upper()],
        node_spacing=args.node_spacing,
        layer_spacing=args.layer_spacing,
        use_ascii=args.ascii
    )


def main() -> Optional[int]:
    """CLI entry point for PHART."""
    args = parse_args()

    try:
        if args.input.suffix == '.py':
            # Handle Python file
            module = load_python_module(args.input)
            
            # Create default layout options from CLI args
            options = create_layout_options(args)
            
            # Modify global renderer settings to match CLI args
            ASCIIRenderer.default_options = options
            
            # Execute the module (which will use the configured renderer)
            return 0
            
        else:
            # Existing .dot and .graphml handling
            with open(args.input, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                if content.strip().startswith("<?xml") or content.strip().startswith("<graphml"):
                    renderer = ASCIIRenderer.from_graphml(str(args.input))
                else:
                    renderer = ASCIIRenderer.from_dot(content)
            except Exception as format_error:
                print(
                    f"Error: Could not parse file as GraphML or DOT format: {format_error}",
                    file=sys.stderr,
                )
                return 1

            # Apply CLI options
            renderer.options.node_style = NodeStyle[args.style.upper()]
            renderer.options.use_ascii = args.ascii
            renderer.options.node_spacing = args.node_spacing
            renderer.options.layer_spacing = args.layer_spacing

            # Handle output
            if args.output:
                renderer.write_to_file(str(args.output))
            else:
                print(renderer.render())
            return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())