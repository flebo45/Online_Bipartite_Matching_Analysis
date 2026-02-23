import sys

class FastBipartite:
    """
    Optimized Memory and traversal speed for Bipartite Graphs

    Structure:
    - Vertices are integers from 0 to N-1
    - Adjacency list is a lists of lists: adj[u] -> [v1, v2, ...]
    """

    __slots__ = ['n_left', 'n_right', 'adj'] # Use __slots__ to reduce memory overhead

    def __init__(self, n_left: int, n_right: int):
        self.n_left = n_left
        self.n_right = n_right
        self.adj = [[] for _ in range(n_left)]

    def add_edge(self, u: int, v: int):
        """
        Add a directed edge from Online node u to Offline node v
        """
        self.adj[u].append(v)

    def get_neighbors(self, u: int):
        """
        Get neighbors of Online node u
        """
        return self.adj[u]
    
    def count_edges(self) -> int:
        """
        Count total number of edges in the graph
        """
        return sum(len(neighbors) for neighbors in self.adj)

    def __repr__(self):
        return f"<FastBipartite U={self.n_left}, V={self.n_right}, E={self.count_edges()}>"