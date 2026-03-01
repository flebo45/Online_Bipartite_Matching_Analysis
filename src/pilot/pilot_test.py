from BipartitePilot import BipartitePilot
from algorithms import pilot_online_greedy, pilot_ranking_algorithm, pilot_hopcroft_karp
from generator import generate_z_graph
import networkx as nx
import random


def run_smoke_test():
    print("Running smoke test...")
    
    # Generate a trap with 5 pairs (10 online and 10 offline vertices)
    n_pairs = 5
    pilot_graph = generate_z_graph(n_pairs)

    # Get Optimal Matching
    nx_graph = pilot_graph.to_networkx()
    opt_matching = nx.bipartite.matching.hopcroft_karp_matching(nx_graph, range(pilot_graph.n_left))
    optimal_size = len(opt_matching) // 2  # Each match is counted twice in the matching dict

    # Greedy Matching
    greedy_matching = pilot_online_greedy(pilot_graph, arrival_order=list(range(pilot_graph.n_left)))
    greedy_size = len(greedy_matching)

    # Calculate Competitive Ratio
    cr = greedy_size / optimal_size if optimal_size > 0 else 0
    #print(pilot_graph.to_networkx())
    print("\n--- RESULTS ---")
    print(f"Optimal Size: {optimal_size}")
    print(f"Greedy Size:  {greedy_size}")
    print(f"Competitive Ratio: {cr:.2f}")

    print("Smoke test completed successfully.")

def run_horse_race_pilot():
    print("Running horse race pilot test...")
    n_pairs = 4096
    graph = generate_z_graph(n_pairs)

    # Optimal Matching
    nx_graph = graph.to_networkx()
    opt_matching = nx.bipartite.matching.hopcroft_karp_matching(nx_graph, range(graph.n_left))
    optimal_size = len(opt_matching) // 2

    # Greedy Matching
    greedy_size = len(pilot_online_greedy(graph))
    greedY_cr = greedy_size / optimal_size if optimal_size > 0 else 0

    # KVV Ranking Algorithm
    # 30 trials to get an average competitive ratio
    kvv_results = []
    for _ in range(30):
        res = pilot_ranking_algorithm(graph)
        kvv_results.append(len(res))
    
    kvv_avg_size = sum(kvv_results) / len(kvv_results)
    kvv_cr = kvv_avg_size / optimal_size if optimal_size > 0 else 0

    print("\n--- RESULTS ---")
    print(f"Optimal Size: {optimal_size}")
    print(f"Greedy Size:  {greedy_size}")
    print(f"Greedy Competitive Ratio: {greedY_cr:.2f}")
    print(f"KVV Average Size: {kvv_avg_size}")
    print(f"KVV Competitive Ratio: {kvv_cr:.2f}")

def valide_hk_implementation():
    print("Validating Hopcroft-Karp implementation...")
    # Use random graph for testing
    n = 20

    graph = BipartitePilot(n, n)
    for u in range(n):
        for v in range(n):
            if random.random() < 0.2:  # 20% chance of edge
                graph.add_edge(u, v)
    
    # NetworkX Optimal Matching
    nx_graph = graph.to_networkx()
    opt_matching = nx.bipartite.matching.hopcroft_karp_matching(nx_graph, range(graph.n_left))
    optimal_size = len(opt_matching) // 2

    # Pilot Hopcroft-Karp Matching
    _, size = pilot_hopcroft_karp(graph)

    print("\n--- RESULTS ---")
    print(f"Optimal Size (NetworkX): {optimal_size}")
    print(f"Pilot HK Size: {size}")

if __name__ == "__main__":
    run_horse_race_pilot()