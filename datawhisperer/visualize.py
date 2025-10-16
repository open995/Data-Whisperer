"""
Network visualization using PyVis
"""

from pyvis.network import Network
import networkx as nx
from pathlib import Path
from typing import Dict, Any


class NetworkVisualizer:
    """Create interactive network visualizations"""
    
    def __init__(self, width: str = "100%", height: str = "800px"):
        self.width = width
        self.height = height
        self.net = None
        
    def visualize(self, graph: nx.Graph, output_file: str = "network.html",
                 title: str = "Data Whisperer - OSINT Map") -> str:
        """
        Create interactive visualization from NetworkX graph
        
        Args:
            graph: NetworkX graph object
            output_file: Output HTML file path
            title: Title for the visualization
            
        Returns:
            Path to generated HTML file
        """
        # Create PyVis network
        self.net = Network(
            width=self.width,
            height=self.height,
            bgcolor="#1a1a1a",
            font_color="#ffffff",
            notebook=False,
            directed=False
        )
        
        # Configure physics for better layout
        self.net.set_options("""
        {
            "physics": {
                "enabled": true,
                "barnesHut": {
                    "gravitationalConstant": -30000,
                    "centralGravity": 0.3,
                    "springLength": 200,
                    "springConstant": 0.04,
                    "damping": 0.09,
                    "avoidOverlap": 0.5
                },
                "maxVelocity": 50,
                "minVelocity": 0.1,
                "solver": "barnesHut",
                "timestep": 0.5,
                "stabilization": {
                    "enabled": true,
                    "iterations": 1000,
                    "updateInterval": 25
                }
            },
            "nodes": {
                "borderWidth": 2,
                "borderWidthSelected": 4,
                "font": {
                    "size": 14,
                    "face": "arial"
                }
            },
            "edges": {
                "color": {
                    "inherit": false,
                    "color": "#848484",
                    "highlight": "#00ff00",
                    "hover": "#00ff00"
                },
                "smooth": {
                    "enabled": true,
                    "type": "continuous"
                }
            },
            "interaction": {
                "hover": true,
                "tooltipDelay": 100,
                "hideEdgesOnDrag": true,
                "keyboard": {
                    "enabled": true
                }
            }
        }
        """)
        
        # Add nodes
        self._add_nodes(graph)
        
        # Add edges
        self._add_edges(graph)
        
        # Generate HTML
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add custom title and styling
        html_content = self._generate_custom_html(title)
        
        self.net.save_graph(str(output_path))
        
        # Inject custom HTML
        self._inject_custom_html(str(output_path), html_content)
        
        return str(output_path)
    
    def _add_nodes(self, graph: nx.Graph):
        """Add nodes to PyVis network"""
        for node in graph.nodes():
            node_data = graph.nodes[node]
            
            # Get node attributes
            label = node_data.get('label', node)
            node_type = node_data.get('type', 'unknown')
            color = node_data.get('color', '#95A5A6')
            confidence = node_data.get('confidence', 0)
            
            # Size based on degree centrality or degree
            degree = node_data.get('degree', 1)
            size = 10 + (degree * 5)  # Scale size by connections
            
            # Create hover tooltip
            tooltip = self._create_node_tooltip(node, node_data)
            
            # Add node
            self.net.add_node(
                node,
                label=self._truncate_label(label),
                title=tooltip,
                color=color,
                size=size,
                borderWidth=2,
                borderWidthSelected=4
            )
    
    def _add_edges(self, graph: nx.Graph):
        """Add edges to PyVis network"""
        for source, target, edge_data in graph.edges(data=True):
            relationship = edge_data.get('relationship', 'connected')
            confidence = edge_data.get('confidence', 0.5)
            
            # Edge width based on confidence
            width = 1 + (confidence * 3)
            
            # Create edge tooltip
            tooltip = f"{relationship} (confidence: {confidence})"
            
            self.net.add_edge(
                source,
                target,
                title=tooltip,
                width=width,
                label=relationship[:15] if len(relationship) > 15 else relationship
            )
    
    def _truncate_label(self, label: str, max_length: int = 30) -> str:
        """Truncate long labels"""
        if len(label) > max_length:
            return label[:max_length-3] + "..."
        return label
    
    def _create_node_tooltip(self, node_id: str, node_data: Dict[str, Any]) -> str:
        """Create HTML tooltip for node"""
        tooltip_parts = []
        
        # Node type
        node_type = node_data.get('type', 'unknown').replace('_', ' ').title()
        tooltip_parts.append(f"<b>Type:</b> {node_type}")
        
        # Value
        tooltip_parts.append(f"<b>Value:</b> {node_id}")
        
        # Confidence
        confidence = node_data.get('confidence', 0)
        tooltip_parts.append(f"<b>Confidence:</b> {confidence}")
        
        # Degree
        degree = node_data.get('degree', 0)
        if degree > 0:
            tooltip_parts.append(f"<b>Connections:</b> {degree}")
        
        # Centrality metrics
        degree_cent = node_data.get('degree_centrality', 0)
        if degree_cent > 0:
            tooltip_parts.append(f"<b>Centrality:</b> {degree_cent:.3f}")
        
        # Context (for original entities)
        context = node_data.get('context')
        if context:
            truncated_context = context[:100] + "..." if len(context) > 100 else context
            tooltip_parts.append(f"<b>Context:</b> {truncated_context}")
        
        # Line number
        line = node_data.get('line')
        if line:
            tooltip_parts.append(f"<b>Line:</b> {line}")
        
        return "<br>".join(tooltip_parts)
    
    def _generate_custom_html(self, title: str) -> str:
        """Generate custom HTML header"""
        return f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; margin: -8px -8px 20px -8px;">
            <h1 style="color: white; margin: 0; font-family: 'Segoe UI', Tahoma, sans-serif;">
                🔍 {title}
            </h1>
            <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-family: 'Segoe UI', Tahoma, sans-serif;">
                Interactive Entity Relationship Network
            </p>
        </div>
        <div style="padding: 10px; background: #2a2a2a; margin: -8px -8px 10px -8px; font-family: 'Segoe UI', Tahoma, sans-serif; color: #ccc;">
            <b>Controls:</b> Drag to pan | Scroll to zoom | Click nodes for details | Hover for information
        </div>
        """
    
    def _inject_custom_html(self, filepath: str, custom_html: str):
        """Inject custom HTML into generated file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Inject after body tag
        content = content.replace(
            '<body>',
            f'<body style="margin: 0; padding: 0; background: #1a1a1a;">{custom_html}'
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def create_legend(self, entity_types: set) -> str:
        """Create a legend HTML for entity types"""
        from datawhisperer.mapbuilder import GraphBuilder
        
        legend_html = '<div style="position: absolute; top: 150px; left: 20px; background: rgba(40,40,40,0.9); padding: 15px; border-radius: 8px; color: white; font-family: Arial;">'
        legend_html += '<h3 style="margin-top: 0;">Legend</h3>'
        
        for entity_type in sorted(entity_types):
            color = GraphBuilder.COLORS.get(entity_type, '#95A5A6')
            label = entity_type.replace('_', ' ').title()
            legend_html += f'<div style="margin: 5px 0;"><span style="display: inline-block; width: 15px; height: 15px; background: {color}; border-radius: 50%; margin-right: 8px;"></span>{label}</div>'
        
        legend_html += '</div>'
        return legend_html
    
    def visualize_with_filters(self, graph: nx.Graph, output_file: str = "network_filtered.html",
                               entity_types: list = None) -> str:
        """
        Create visualization with entity type filters
        
        Args:
            graph: NetworkX graph
            output_file: Output file path
            entity_types: List of entity types to include (None = all)
            
        Returns:
            Path to generated file
        """
        if entity_types:
            # Filter nodes by type
            nodes_to_include = [
                n for n, d in graph.nodes(data=True)
                if d.get('type') in entity_types
            ]
            filtered_graph = graph.subgraph(nodes_to_include).copy()
        else:
            filtered_graph = graph
        
        return self.visualize(filtered_graph, output_file)

