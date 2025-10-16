"""
Graph builder using NetworkX for entity relationship mapping
"""

import networkx as nx
from typing import List, Dict, Any
import json


class GraphBuilder:
    """Build network graphs from entities and relationships"""
    
    # Color palette for different entity types
    COLORS = {
        'email': '#FF6B6B',           # Red
        'ipv4': '#4ECDC4',            # Teal
        'ipv6': '#45B7D1',            # Blue
        'url': '#FFA07A',             # Light Salmon
        'domain': '#98D8C8',          # Mint
        'md5': '#F7DC6F',             # Yellow
        'sha1': '#F8B739',            # Orange
        'sha256': '#E67E22',          # Dark Orange
        'sha512': '#D35400',          # Darker Orange
        'bitcoin_wallet': '#F39C12',  # Bitcoin Gold
        'ethereum_wallet': '#8E44AD', # Ethereum Purple
        'phone': '#3498DB',           # Blue
        'credential': '#E74C3C',      # Red
        'api_key': '#9B59B6',         # Purple
        'jwt_token': '#1ABC9C',       # Turquoise
    }
    
    def __init__(self):
        self.graph = nx.Graph()
        self.entities = []
        self.relationships = []
        
    def build_graph(self, classified_data: Dict[str, Any]) -> nx.Graph:
        """
        Build a NetworkX graph from classified data
        
        Args:
            classified_data: Output from EntityClassifier
            
        Returns:
            NetworkX graph object
        """
        self.entities = classified_data.get('entities', [])
        self.relationships = classified_data.get('relationships', [])
        
        # Clear existing graph
        self.graph.clear()
        
        # Add nodes for all entities
        self._add_entity_nodes()
        
        # Add nodes for domains (extracted from relationships)
        self._add_domain_nodes()
        
        # Add edges for relationships
        self._add_relationship_edges()
        
        # Calculate node metrics
        self._calculate_metrics()
        
        return self.graph
    
    def _add_entity_nodes(self):
        """Add nodes for all entities"""
        for entity in self.entities:
            node_id = entity['value']
            node_type = entity['type']
            
            self.graph.add_node(
                node_id,
                type=node_type,
                label=node_id,
                confidence=entity['confidence'],
                line=entity['line'],
                context=entity['context'],
                color=self.COLORS.get(node_type, '#95A5A6'),
                metadata=entity.get('metadata', {})
            )
    
    def _add_domain_nodes(self):
        """Add domain nodes from entity metadata"""
        domain_nodes = set()
        
        # Collect domains from emails
        for entity in self.entities:
            if entity['type'] == 'email':
                domain = entity['metadata'].get('domain')
                if domain and domain not in self.graph:
                    domain_nodes.add(domain)
            
            elif entity['type'] == 'url':
                domain = entity['metadata'].get('domain')
                if domain and domain not in self.graph:
                    domain_nodes.add(domain)
        
        # Add domain nodes
        for domain in domain_nodes:
            self.graph.add_node(
                domain,
                type='domain',
                label=domain,
                confidence=0.9,
                color=self.COLORS.get('domain', '#95A5A6'),
                metadata={'is_domain_node': True}
            )
    
    def _add_relationship_edges(self):
        """Add edges for all relationships"""
        for rel in self.relationships:
            source = rel['source']
            target = rel['target']
            rel_type = rel['type']
            confidence = rel.get('confidence', 0.9)
            
            # Ensure both nodes exist
            if source in self.graph and target in self.graph:
                self.graph.add_edge(
                    source,
                    target,
                    relationship=rel_type,
                    confidence=confidence,
                    weight=confidence,
                    metadata=rel.get('metadata', {})
                )
    
    def _calculate_metrics(self):
        """Calculate graph metrics for nodes"""
        if len(self.graph.nodes()) == 0:
            return
        
        # Degree centrality
        degree_centrality = nx.degree_centrality(self.graph)
        
        # Betweenness centrality (if graph is connected enough)
        try:
            betweenness_centrality = nx.betweenness_centrality(self.graph)
        except:
            betweenness_centrality = {node: 0 for node in self.graph.nodes()}
        
        # Add metrics to nodes
        for node in self.graph.nodes():
            self.graph.nodes[node]['degree_centrality'] = degree_centrality.get(node, 0)
            self.graph.nodes[node]['betweenness_centrality'] = betweenness_centrality.get(node, 0)
            self.graph.nodes[node]['degree'] = self.graph.degree(node)
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the graph"""
        if len(self.graph.nodes()) == 0:
            return {
                'nodes': 0,
                'edges': 0,
                'density': 0,
                'components': 0
            }
        
        stats = {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'components': nx.number_connected_components(self.graph),
            'avg_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes()
        }
        
        # Find most connected nodes
        degree_dict = dict(self.graph.degree())
        if degree_dict:
            top_nodes = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)[:5]
            stats['top_connected_nodes'] = [
                {'node': node, 'degree': degree} for node, degree in top_nodes
            ]
        
        return stats
    
    def export_graphml(self, filepath: str):
        """Export graph in GraphML format"""
        nx.write_graphml(self.graph, filepath)
    
    def export_json(self, filepath: str):
        """Export graph in JSON format"""
        data = nx.node_link_data(self.graph)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def get_subgraph(self, node_id: str, depth: int = 1) -> nx.Graph:
        """
        Get subgraph around a specific node
        
        Args:
            node_id: Central node ID
            depth: How many hops to include
            
        Returns:
            Subgraph
        """
        if node_id not in self.graph:
            return nx.Graph()
        
        # Get nodes within depth
        nodes = {node_id}
        current_layer = {node_id}
        
        for _ in range(depth):
            next_layer = set()
            for node in current_layer:
                next_layer.update(self.graph.neighbors(node))
            nodes.update(next_layer)
            current_layer = next_layer
        
        return self.graph.subgraph(nodes).copy()
    
    def find_paths(self, source: str, target: str, cutoff: int = 5) -> List[List[str]]:
        """
        Find all simple paths between two nodes
        
        Args:
            source: Source node
            target: Target node
            cutoff: Maximum path length
            
        Returns:
            List of paths
        """
        if source not in self.graph or target not in self.graph:
            return []
        
        try:
            paths = list(nx.all_simple_paths(self.graph, source, target, cutoff=cutoff))
            return paths
        except nx.NetworkXNoPath:
            return []
    
    def get_communities(self) -> Dict[int, List[str]]:
        """Detect communities in the graph using Louvain method"""
        if len(self.graph.nodes()) == 0:
            return {}
        
        try:
            # Use greedy modularity communities
            communities = nx.community.greedy_modularity_communities(self.graph)
            
            result = {}
            for i, community in enumerate(communities):
                result[i] = list(community)
            
            return result
        except:
            return {}

