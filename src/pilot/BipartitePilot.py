import networkx as nx
import random

class BipartitePilot:
    """
    A Pilot wrapper for Bipartite Matching experiments
    Use NetworkX for easy visualizaion
    """
    def __init__(self, n_left, n_right):
        self.n_left = n_left
        self.n_right = n_right
        self.adjacency_list = {i: [] for i in range(n_left)}

    def add_edge(self, left_node, right_node):
        """
        Add an edge betwwen Online vertex (left_node) and Offline vertex (right_node)
        """
        if right_node not in self.adjacency_list[left_node]:
            self.adjacency_list[left_node].append(right_node)
    
    def get_neighbors(self, left_node):
        """
        Get the neighbors of an Online vertex (left_node)
        """
        return self.adjacency_list[left_node]

    def to_networkx(self):
        """
        Convert to a NetworkX graph for visualization
        """
        G = nx.Graph()
        G.add_nodes_from(range(self.n_left), bipartite=0)  # Online vertices
        G.add_nodes_from(range(self.n_left, self.n_left + self.n_right), bipartite=1)  # Offline vertices
        for left_node, neighbors in self.adjacency_list.items():
            for right_node in neighbors:
                G.add_edge(left_node, self.n_left + right_node)  # Shift right_node index for bipartite graph
        return G
