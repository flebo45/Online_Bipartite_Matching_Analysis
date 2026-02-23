import random
from collections import deque

def online_greedy(graph, arrival_order, return_pairs=False):
    """
    Optimized Deterministic greedy with fixed Tie-Breaking
    Logic: Match u to first available neighbor in the adjacency list
    ( Assumes neighbors are ordered by index)
    """
    assert graph is not None, "Graph cannot be None"
    assert len(arrival_order) == graph.n_left, "Arrival order length must match number of online vertices"

    n_right = graph.n_right
    match_v = [-1] * n_right  # match_v[v] = u if v is matched to u, else -1
    matching_size = 0

    for u in arrival_order:
        for v in graph.get_neighbors(u):
            if match_v[v] == -1:
                match_v[v] = u
                matching_size += 1
                break

    assert matching_size <= min(graph.n_left, graph.n_right), "Matching size cannot exceed number of vertices on either side"
    
    if  not return_pairs:
        return None, matching_size
    
    pairs = []
    for v, u in enumerate(match_v):
        if u != -1:
            pairs.append((u, v))
    return pairs, matching_size

def online_ranking(graph, arrival_order, return_pairs=False):
    """
    Karp-Vazirani-Vazirani (KVV) Ranking Algorithm
    Assigns random ranks to offline vertices
    Match arriving online vertices to their highest-priority unmached neighbor
    """
    assert graph is not None, "Graph cannot be None"
    assert len(arrival_order) == graph.n_left, "Arrival order length must match number of online vertices"

    n_right = graph.n_right
    match_v = [-1] * n_right
    matching_size = 0

    # Random Ranks: lower value = higher priority
    ranks = [random.random() for _ in range(n_right)]

    for u in arrival_order:
        best_v = -1
        min_rank = 2.0

        for v in graph.get_neighbors(u):
            if match_v[v] == -1:
                if ranks[v] < min_rank:
                    min_rank = ranks[v]
                    best_v = v
                
        if best_v != -1:
            match_v[best_v] = u
            matching_size += 1

    assert matching_size <= min(graph.n_left, graph.n_right), "Matching size cannot exceed number of vertices on either side"
    
    if not return_pairs:
        return None, matching_size
    
    pairs = []
    for v, u in enumerate(match_v):
        if u != -1:
            pairs.append((u, v))
    return pairs, matching_size

def hopcroft_karp(graph, return_pairs=False):
    """
    Optimized Hopcroft-Karp Algorithm for Maximum Bipartite Matching
    Use Iterative DFS to handle large N on python
    Returns the size of the maximum matching
    """
    assert graph is not None, "Graph cannot be None"
    assert graph.n_left > 0 and graph.n_right > 0, "Graph must have positive number of vertices"

    u_left = graph.n_left
    v_right = graph.n_right
    
    pair_u = [-1] * u_left # Matching for U
    pair_v = [-1] * v_right # Matching for V
    dist = [0] * (u_left + 1) # Layer levels (+1 for dummy NIL node)
    
    NIL = u_left # Dummy node index

    def bfs():
        queue = deque()
        for u in range(u_left):
            if pair_u[u] == -1:
                dist[u] = 0
                queue.append(u)
            else:
                dist[u] = float('inf')
        dist[NIL] = float('inf')
        
        while queue:
            u = queue.popleft()
            if dist[u] < dist[NIL]:
                for v in graph.get_neighbors(u):
                    next_u = pair_v[v]
                    if next_u == -1: # Representing NIL
                        next_u = NIL
                    
                    if dist[next_u] == float('inf'):
                        dist[next_u] = dist[u] + 1
                        queue.append(next_u)
        return dist[NIL] != float('inf')

    def dfs_iterative(start_u):
        """Iterative DFS to avoid recursion depth issues."""
        stack = [(start_u, 0)] # (current_u, neighbor_index)
        
        path = []
        while stack:
            u, idx = stack.pop()
            
            # Find the next available neighbor in the layered graph
            neighbors = graph.get_neighbors(u)
            found = False
            for i in range(idx, len(neighbors)):
                v = neighbors[i]
                next_u = pair_v[v]
                if next_u == -1: next_u = NIL
                
                if dist[next_u] == dist[u] + 1:
                    # Potential path found
                    path.append((u, v))
                    if next_u == NIL:
                        # Found an augmenting path!
                        # Backtrack and update matching
                        for up, vp in path:
                            pair_u[up] = vp
                            pair_v[vp] = up
                        return True
                    else:
                        # Continue DFS
                        stack.append((u, i + 1)) # Save state
                        stack.append((next_u, 0)) # Move to next node
                        found = True
                        break
            
            if not found:
                dist[u] = float('inf') # Dead end
                if path: path.pop()
        return False

    matching_size = 0
    while bfs():
        for u in range(u_left):
            if pair_u[u] == -1:
                if dfs_iterative(u):
                    matching_size += 1

    assert matching_size <= min(graph.n_left, graph.n_right), "Matching size cannot exceed number of vertices on either side"

    if return_pairs:
        pairs = []
        for u, v in enumerate(pair_u):
            if v != -1:
                pairs.append((u, v))
        return pairs, matching_size
    
    return None, matching_size
    