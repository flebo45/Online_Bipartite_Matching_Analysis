from BipartitePilot import BipartitePilot
import random

def generate_z_graph(n_pairs):
    """
    Generate a Z-shaped bipartite graph
    Designed to force Greedy into a 0.5 Competitive ratio

    Structure per pair:
    - Online vertex 0 connects to Offline vertex 0 and 1
    - Online vertex 1 connects only to Offline vertex 1

    If greedy picks vertex 0 first, it will match with Offline vertex 0, leaving vertex 1 unmatched
    """

    n_left = 2 * n_pairs
    n_right = 2 * n_pairs
    pilot_graph = BipartitePilot(n_left, n_right)

    for i in range(0, n_left, 2):
        left_top = i
        left_bottom = i + 1
        right_trap = i
        right_safe = i + 1

        pilot_graph.add_edge(left_top, right_trap)  # Online vertex connects to trap
        pilot_graph.add_edge(left_top, right_safe)  # Online vertex connects to safe

        pilot_graph.add_edge(left_bottom, right_trap)  # Online vertex connects to trap

    return pilot_graph

def generate_random_bipartite(n, p):
    """
    Generate a Random bipartite graph with n online and n offline vertices
    Each edge is included with probability p
    """
    graph = BipartitePilot(n, n)
    for i in range(n):
        for j in range(n):
            if random.random() < p:
                graph.add_edge(i, j)
    return graph