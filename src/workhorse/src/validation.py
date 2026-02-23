def validate_matching(graph, matching_list):
    """
    Indipendent validator fo Bipartite Matching

    Checks:
    1. Existence: Every matched edge must exist in the graph
    2. Disjointness: No two matched edges can share a vertex
    3. Correctness: All matched vertices must be valid (exist in the graph)

    Args:
        graph: FastBipartite instance representing the original graph
        matching_list: List of tuples (u, v) representing the matching
    
    Returns:
        bool: True if valid, raises ValueError with details if invalid
    """
    # Check Theoretical Bounds
    max_possible = min(graph.n_left, graph.n_right)
    if len(matching_list) > max_possible:
        raise ValueError(f"Invalid matching: Size {len(matching_list)} exceeds theoretical maximum {max_possible}")

    matched_u = set()
    matched_v = set()

    for u, v in matching_list:
        # Check vertext indexes are in valid range
        if not (0 <= u < graph.n_left) or not (0 <= v < graph.n_right):
            raise ValueError(f"Invalid matching: Vertex index out of bounds (u={u}, v={v})")

        # Check 1: Edge existence
        if v not in graph.get_neighbors(u):
            raise ValueError(f"Invalid matching: Edge ({u}, {v}) does not exist in the graph")

        # Check 2: Disjointness
        if u in matched_u:
            raise ValueError(f"Invalid matching: Online vertex {u} is matched more than once")
        matched_u.add(u)
        if v in matched_v:
            raise ValueError(f"Invalid matching: Offline vertex {v} is matched more than once")
        matched_v.add(v)

    return True