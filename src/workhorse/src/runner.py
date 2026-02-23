import time
import datetime
import gc
import csv
import os
import sys
import random
from algorithms import online_greedy, online_ranking, hopcroft_karp
from generators import generate_random_bipartite, generate_adversarial_z_trap, generate_arrival_order, generate_stress_test
from validation import validate_matching
from loaders import load_movies_graph

def run_experiment(config):
    """
    Main execution loop for a set of Desing Points
    Handle both Syntehtic and Real-World experiments based on config
    """
    exp_name = config['experiment_name']
    dataset_path = config.get('dataset_path')

    if dataset_path:
        # Real-World Dataset: Load graph from file
        n_values = [0]  # Placeholder, we will override n and m after loading the graph
        densities = ['real']
        print(f"[RUNNER] Running real-world dataset from {dataset_path}...")

    else:
        # Synthetic Dataset: Generate graphs based on config parameters
        n_values = config.get('n_list')
        densities = config.get('densities', 'sparse')
        print(f"[RUNNER] Running synthetic experiments with N={n_values} and densities={densities}...")

    order_type = config.get('orders', 'random')


    trials = config.get('trials', 5)
    algorithms = config.get('algorithms', ['greedy', 'ranking', 'hopcroft_karp'])
    fixed_seed = config.get('fixed_seed', None)

    # Prepare results file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = os.path.join('results', f"{exp_name.replace(' ', '_')}_{timestamp}.csv")
    file_exists = os.path.isfile(results_path)

    fieldnames = ['n', 'm', 'algorithm', 'density', 'order', 'trial', 'match_size', 'opt_size', 'cr', 'time_ns', 'is_valid', 'seed']

    with open(results_path, mode='a', newline='') as csvfile:
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        for n in n_values:
            for density in densities:
                for order in order_type:

                    if not dataset_path:
                        print(f"\n[RUNNER] Starting experiment with N={n}, density={density}, order={order}...")
                    else:
                        print(f"\n[RUNNER] Starting experiment with real-world dataset from {dataset_path}...")

                    for t in range(trials):
                        if fixed_seed is not None:
                            current_seed = fixed_seed
                        else:
                            # Automatic seeding for reproducibility
                            current_seed = random.randint(0, 2**32 - 1)
                        
                        random.seed(current_seed)

                        graph = None
                        arrival_order = []
                        current_n = 0

                        if dataset_path:
                            # Real World Branch
                            graph, file_order_list = load_movies_graph(dataset_path)
                            current_n = graph.n_left

                            if order == 'real':
                                arrival_order = list(file_order_list)
                            elif order == 'random':
                                arrival_order = list(file_order_list)
                                random.shuffle(arrival_order)
                            elif order == 'adversarial':
                                arrival_order = generate_adversarial_arrival_order(graph)
                            else:
                                print(f"[ERROR] Unknown order type '{order}' for real-world dataset. Defaulting to file order.")
                                arrival_order = list(file_order_list)

                        else:
                            # Synthetic Branch
                            current_n = n

                            # Graph Generation
                            if density == 'adversarial':
                                graph = generate_adversarial_z_trap(n // 2)
                            else:
                                graph = generate_random_bipartite(n, density)

                            # Arrival Order Generation
                            arrival_order = generate_arrival_order(graph, order)

                        edges_count = graph.count_edges()

                        # Optimal Baseline (Offline)
                        _, opt_size = hopcroft_karp(graph)

                        # Snapshot Rng state
                        rng_state = random.getstate()

                        for algo_name in algorithms:
                            random.setstate(rng_state)  # Reset RNG to ensure same conditions for each algorithm

                            # Measurement
                            gc.collect() # Clean up before timing
                            gc.disable() # Prevent GC during the run

                            # Warm-up and Validation Run
                            if algo_name == 'greedy':
                                pairs_v, _ = online_greedy(graph, arrival_order, return_pairs=True)
                            elif algo_name == 'ranking':
                                pairs_v, _ = online_ranking(graph, arrival_order, return_pairs=True)
                            elif algo_name == 'hopcroft_karp':
                                pairs_v, _ = hopcroft_karp(graph, return_pairs=True)

                            isValid = True
                            try:
                                validate_matching(graph, pairs_v)
                            except ValueError as ve:
                                print(f"[VALIDATION ERROR] {ve}")
                                isValid = False
                                sys.exit(1)

                            # Timed Run
                            random.setstate(rng_state)  # Reset RNG again for timed run

                            start_t = time.process_time_ns()
                            if algo_name == 'greedy':
                                _, m_size = online_greedy(graph, arrival_order)
                            elif algo_name == 'ranking':
                                _, m_size = online_ranking(graph, arrival_order)
                            elif algo_name == 'hopcroft_karp':
                                _, m_size = hopcroft_karp(graph)
                            end_t = time.process_time_ns()

                            gc.enable()

                            duration = end_t - start_t
                            cr = m_size / opt_size if opt_size > 0 else 0

                            # Logging
                            writer.writerow({
                                'n': current_n,
                                'm': edges_count,
                                'algorithm': algo_name,
                                'density': density,
                                'order': order,
                                'trial': t,
                                'match_size': m_size,
                                'opt_size': opt_size,
                                'cr': cr,
                                'time_ns': duration,
                                'is_valid': isValid,
                                'seed': current_seed
                            })
                        csvfile.flush()
    
    print(f"[RUNNER] Experiment complete. Results saved to {results_path}")

def run_stress_tests(config):
    """
    Run specific stress tests on algorithms
    Read test cases from Json config
    """
    print(f"\n=== STARTING {config['experiment_name']} ===\n")

    # Load test cases from config
    test_cases = config.get('test_cases', [])
    if not test_cases:
        print("[STRESS TEST] No test cases defined in config.")
        return

    algorithms = config.get('algorithms', ['greedy', 'ranking', 'hopcroft_karp'])

    # Prepare results file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = os.path.join('results', f"Stress_study_{timestamp}.csv")
    os.makedirs('results', exist_ok=True)

    fields = ['id', 'type', 'n', 'm', 'algorithm', 'status', 'match_size', 'expected', 'message']

    with open(results_path, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()

        for case in test_cases:
            print(f"[STRESS TEST] Running test case: {case['id']} - {case['type']}")

            # Graph Generation
            try:
                graph = generate_stress_test(case['n'], case['type'])
            except Exception as e:
                print(f"[ERROR] Failed to generate graph for test case {case['id']}: {e}")
                continue

            arrival_order = list(range(graph.n_left))  # Default order for stress tests

            for algo in algorithms:
                try:
                    if algo == 'greedy':
                        pairs_v, size = online_greedy(graph, arrival_order, return_pairs=True)
                    elif algo == 'ranking':
                        pairs_v, size = online_ranking(graph, arrival_order, return_pairs=True)
                    elif algo == 'hopcroft_karp':
                        pairs_v, size = hopcroft_karp(graph, return_pairs=True)
                    validate_matching(graph, pairs_v)
                    status = 'PASS'
                    message = ''
                    expected = case.get('expected_size')

                    # Handle z-trap case
                    if case['type'] == 'z_trap':
                        if algo == 'greedy':
                            expected = case.get('expected_greedy')
                        elif algo == 'hopcroft_karp':
                            expected = case.get('expected_opt')
                        else:
                            expected = None  # Not defined for ranking

                    if expected is not None:
                        if size != expected:
                            status = 'FAIL'
                            message = f"Expected matching size {expected}, got {size}"
                    
                    elif algo == 'ranking' and case['type'] == 'z_trap':
                        if size < case.get('expected_greedy', 0):
                            status = 'FAIL'
                            message = f"Expected ranking to perform at least as well as greedy ({case.get('expected_greedy')}), got {size}"
                    
                    print(f"[{status}] {algo:<15} Size={size} {message}")
                
                    writer.writerow({
                    'id': case['id'],
                    'type': case['type'],
                    'n': graph.n_left,
                    'm': graph.count_edges(),
                    'algorithm': algo,
                    'status': status,
                    'match_size': size if status == 'PASS' else 0,
                    'expected': expected if expected is not None else 'N/A',
                    'message': message
                    })
            
                except Exception as e:
                    print(f"[ERROR] {algo} failed on test case {case['id']}: {e}")
                    writer.writerow({
                        'id': case['id'],
                        'type': case['type'],
                        'n': graph.n_left,
                        'm': graph.count_edges(),
                        'algorithm': algo,
                        'status': 'ERROR',
                        'match_size': 0,
                        'expected': case.get('expected_size', 'N/A'),
                        'message': str(e)
                    })
            
    print(f"\n[STRESS TEST] All tests completed. Results saved to {results_path}")  
