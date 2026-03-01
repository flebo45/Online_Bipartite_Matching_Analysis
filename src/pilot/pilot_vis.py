import matplotlib.pyplot as plt
import numpy as np
import random
from algorithms import pilot_online_greedy, pilot_ranking_algorithm, pilot_hopcroft_karp
from generator import generate_z_graph, generate_random_bipartite
from BipartitePilot import BipartitePilot 

def run_mini_horse_race():
    # Parameters
    n_pairs = 4096
    trials_ranking = 50

    # Graphs Generation
    random_graph = generate_random_bipartite(n_pairs, 1) 
    z_graph = generate_z_graph(n_pairs)

    datsets = {"Random Graph": random_graph, "Z-Graph": z_graph}
    results = {"Greedy": [], "KVV Ranking": [], "Hopcroft-Karp(Optimal)": []}

    for name, graph in datsets.items():
        print(f"\n--- Testing on {name} ---")

        # Optimal Matching
        _, optimal_size = pilot_hopcroft_karp(graph)
        results["Hopcroft-Karp(Optimal)"].append(optimal_size/optimal_size)

        # Greedy Matching
        greedy_res = pilot_online_greedy(graph)
        greedy_size = len(greedy_res)
        results["Greedy"].append(greedy_size/optimal_size)

        # KVV Ranking Algorithm
        kvv_sizes = []
        for _ in range(trials_ranking):
            res = pilot_ranking_algorithm(graph)
            kvv_sizes.append(len(res))
        kvv_avg_size = sum(kvv_sizes) / len(kvv_sizes)
        results["KVV Ranking"].append(kvv_avg_size/optimal_size)

        print(f" Greedy Competitive Ratio: {results['Greedy'][-1]:.2f}")
        print(f" KVV Ranking Competitive Ratio: {results['KVV Ranking'][-1]:.2f}")

    return results, datsets.keys()


def plot_results(results, labels):
    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))

    # Create the bars
    ax.bar(x - width, results["Greedy"], width, label='Simple Greedy', color='#e74c3c')
    ax.bar(x, results["KVV Ranking"], width, label='Ranking (KVV)', color='#3498db')
    ax.bar(x + width, results["Hopcroft-Karp(Optimal)"], width, label='Hopcroft-Karp (OPT)', color='#2ecc71')
    
    # Add labels and formatting
    ax.set_ylabel('Competitive Ratio (Size / OPT)')
    ax.set_title('Pilot Phase: Online vs Offline Performance Gap')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.2) # Give some space for labels
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(y=0.632, color='blue', linestyle=':', label='1 - 1/e limit')
    ax.axhline(y=0.5, color='red', linestyle=':', label='0.5 limit')
    
    ax.legend()
    
    plt.tight_layout()
    plt.savefig("pilot_results.png")
    print("\n[SUCCESS] Plot saved as 'pilot_results.png'")
    print(results)
    plt.show()

if __name__ == "__main__":
    results, labels = run_mini_horse_race()
    plot_results(results, labels)