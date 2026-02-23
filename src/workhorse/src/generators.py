import random
import math
from datastructures import FastBipartite

def generate_random_bipartite(n, density_type):
    """
    Generate a Random Bipartite Graph G(n, n, p)
    Optimized for speed: uses random.sample() for sparse graph to avoid O(n^2) checks

    Args:
        n: Number of vertices on each side (U and V)
        density_type: 'sparse', 'medium', 'dense', or 'extremely_sparse' to control edge probability
    """
    graph = FastBipartite(n, n)

    # Determine Probability p based on density_type
    if density_type == 'sparse':
        # E[degree] = O(log n) => p = log(n)/n
        p = math.log(n + 1) / n

    elif density_type == 'extremely_sparse':
        # E[degree] = 2 => p = 1/n
        p = 2.0 / n

    elif density_type == 'medium':
        #E[degree] = O(sqrt(n)) => p = 1/sqrt(n)
        p = 1.0 / math.sqrt(n)

    elif density_type == 'dense':
        # E[degree] = O(n) => p = 0.5
        p = 0.5
    
    else:
        raise ValueError(f"Invalid density_type: {density_type}. Choose from 'sparse', 'medium', 'dense', 'extremely_sparse'")

    # Optimization Strategy selection
    # For sparse graphs, we can directly sample edges without checking every possible pair
    if p < 0.1:
        for u in range(n):
            # Binomial Distribution approx: Number of neighbors for u
            # For very small p, this is roughly Poisson, but random.sample handles the selection
            # Calculate expected neighbors: k ~ Binomial(n, p)
            # Optimization: Just use the mean for speed in "generation", 
            # or use numpy.random.binomial if strict correctness is needed.
            # Here we use a fast approximation:
            
            # Fast way: iterate and skip? No, random.sample is faster for sparse.
            # Let's use the geometric skipping method if we want to be pure, 
            # but random.sample(range(n), k) is standard pythonic optimization.
            
            # Determine k (degree of u)
            # For strict G(n,p), degree varies. For AE 'random', fixed degree is sometimes preferred.
            # Let's stick to true G(n,p) simulation:
            
            # In standard python random, there isn't a fast "jump" for p.
            # We will use the 'random.random() < p' check but only for the expected number of edges.
            
            # ACTUAL FAST METHOD FOR G(n,p) in Python:
            # Iterating N*N is too slow.
            # We will use 'random.sample' for fixed degree approximation 
            # OR just iterate if N is small.
            
            # Correct Efficient Approach for AE:

            target_degree = int(p * n)

            if target_degree == 0 and p > 0:
                target_degree = 1
            
            targets = random.sample(range(n), target_degree)
            for v in targets:
                graph.add_edge(u, v)

    # For dense graph, checking every pair is more efficient than sampling
    else:
        for u in range(n):
            for v in range(n):
                if random.random() < p:
                    graph.add_edge(u, v)

    return graph

def generate_adversarial_z_trap(n_pairs):
    """
    Generate  a z-graph to force greedy 0.5 competitive ratio

    Logic:
    - n_pairs unit. Total N = 2*n_pairs
    - Structure:
        u_top (i) -> [v_trap(i), v_safe(i+1)]
        u_bottom (i+1) -> [v_trap(i)]
    """
    n = 2 * n_pairs
    graph = FastBipartite(n, n)

    for i in range(0, n, 2):
        u_top = i
        u_bottom = i + 1

        v_trap = i
        v_safe = (i + 1)

        if v_safe < n:  # Ensure we don't go out of bounds
            graph.add_edge(u_top, v_trap)  # Online vertex connects to trap
            graph.add_edge(u_top, v_safe)  # Online vertex connects to safe

            graph.add_edge(u_bottom, v_trap)  # Online vertex connects to trap

    return graph

def generate_adversarial_arrival_order(graph):
    """
    Generate adversarial order for online vertices in every graph.
    Strategy: Sort online vertices by degree ascending (lowest degree first)
    """
    n_left = graph.n_left

    scoring = []
    for u in range(n_left):
        neighbors_list = graph.get_neighbors(u)
        if neighbors_list:
            scoring.append((u, len(neighbors_list)))
        else:
            scoring.append((u, float('inf')))  # No neighbors, worst case

    scoring.sort(key=lambda x: x[1])  # Sort by degree (ascending)
    return [item[0] for item in scoring]

def generate_arrival_order(graph, order_type):
    """
    Return a list of online vertex representing arrival sequence

    Args:
        n: Number of online vertices
        order_type: 'random', 'sorted', 'adversarial'
    """
    n = graph.n_left

    if order_type == 'sorted':
        return list(range(n))  # Already sorted

    elif order_type == 'random':
        order = list(range(n))
        random.shuffle(order) # In-place shuffle
        return order

    elif order_type == 'adversarial':
        return generate_adversarial_arrival_order(graph)

    else:
        raise ValueError(f"Invalid order_type: {order_type}. Choose from 'random', 'sorted', 'adversarial'")

def generate_stress_test(n, test_type):
    """
    Generate specific graph structures to stress test algorithms

    Args:
        n: Number of vertices on each side
        test_type: 'empty', 'single_edge, 'complete', 'disconected', 'z_trap'
    """
    if test_type == 'z_trap':
        # existing logic for z-graph
        return generate_adversarial_z_trap(n // 2)
    
    graph = FastBipartite(n, n)

    if test_type == 'empty':
        pass  # No edges

    elif test_type == 'single_edge':
        graph.add_edge(0, 0)  # Just one edge
    
    elif test_type == 'complete':
        for u in range(n):
            for v in range(n):
                graph.add_edge(u, v)
    
    elif test_type == 'disconnected':
        # Two disjoint K_2,2 components
        if n < 4:
            raise ValueError("n must be at least 4 for disconnected test")
        
        for u in [0, 1]:
            for v in [0, 1]:
                graph.add_edge(u, v)
        for u in [2, 3]:
            for v in [2, 3]:
                graph.add_edge(u, v)

    else:
        raise ValueError(f"Invalid test_type: {test_type}. Choose from 'empty', 'single_edge', 'complete', 'disconnected', 'z_trap'")

    return graph
   
