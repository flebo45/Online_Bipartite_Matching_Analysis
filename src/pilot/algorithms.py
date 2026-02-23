import random
from collections import deque

def pilot_online_greedy(graph: BipartitePilot, arrival_order=None):
    """
    Deterministic greedy with fixed Tie-Breaking (lowest index)
    """
    if arrival_order is None:
        arrival_order = list(range(graph.n_left))

    matching = {}
    matched_offline = set()

    for left_node in arrival_order:
        #Tie Breaking
        neighbors = sorted(graph.get_neighbors(left_node))

        for right_node in neighbors:
            if right_node not in matched_offline:
                matching[left_node] = right_node
                matched_offline.add(right_node)
                print(f"[DEBUG] Matched Online vertex {left_node} with Offline vertex {right_node}")
                break

    return matching


def pilot_ranking_algorithm(graph: BipartitePilot, arrival_order=None, rng=None):
    """
    Karp-Vazirani-Vazirani (KVV) Ranking Algorithm
    Assigns random ranks to offline vertices
    Match arriving online vertices to their highest-priority unmached neighbor
    """
    if arrival_order is None:
        arrival_order = list(range(graph.n_left))

    # Initialization
    # Assign random ranks to offline vertices
    offline_vertices = list(range(graph.n_right))
    ranks = {v: random.random() for v in offline_vertices}

    matching = {}
    matched_offline = set()

    print(f"[DEBUG] Offline Ranks Assigned: { {v: round(r, 2) for v, r in ranks.items()} }")

    # Matching
    for left_node in arrival_order:
        neighbors = graph.get_neighbors(left_node)
        # Filter out already matched offline vertices
        available_neighbors = [v for v in neighbors if v not in matched_offline]

        if available_neighbors:
            # Select the neighbor with the highest rank (lowest random value)
            best_neighbor = min(available_neighbors, key=lambda v: ranks[v])

            matching[best_neighbor] = left_node
            matched_offline.add(best_neighbor)
            print(f"[DEBUG] Matched Online vertex {left_node} with Offline vertex {best_neighbor} (Rank: {round(ranks[best_neighbor], 2)})")
        
        else:
            print(f"[DEBUG] Online vertex {left_node} has no available neighbors to match.")
    
    return matching

def pilot_hopcroft_karp(graph: BipartitePilot):
    """
    Offline Maximum Bipartite matching
    Standard Implementation:
    1. BFS to build layered graph (shortest augmenting path)
    2. DFS to find maximal set of disjoint augmenting paths
    """
    # pair_u[u] is the V vertex matched with U, or None if free
    # pair_v[v] is the U vertex matched with V, or None if free
    pair_u = {u: None for u in range(graph.n_left)}
    pair_v = {v: None for v in range(graph.n_right)}
    dist = {} # Stores layers for BFS

    def bfs():
        queue = deque()
        for u in range(graph.n_left):
            if pair_u[u] is None:
                dist[u] = 0
                queue.append(u)
            else:
                dist[u] = float('inf')

        dist[None] = float('inf')

        while queue:
            u = queue.popleft()
            if dist[u] < dist[None]:
                for v in graph.get_neighbors(u):
                    next_u = pair_v[v]
                    if dist.get(next_u, float('inf')) == float('inf'):
                        dist[next_u] = dist[u] + 1
                        queue.append(next_u)
        
        return dist[None] != float('inf')

    def dfs(u):
        if u is not None:
            for v in graph.get_neighbors(u):
                next_u = pair_v[v]
                if dist.get(next_u, float('inf')) == dist[u] + 1:
                    if dfs(next_u):
                        pair_v[v] = u
                        pair_u[u] = v
                        return True
            dist[u] = float('inf')
            return False
        return True

    matching_size = 0
    phase_count = 0
    while bfs():
        phase_count += 1

        for u in range(graph.n_left):
            if pair_u[u] is None:
                if dfs(u):
                    matching_size += 1
    print(f"[DEBUG] Hopcroft-Karp completed in {phase_count} phases with matching size {matching_size}")

    return pair_u, matching_size