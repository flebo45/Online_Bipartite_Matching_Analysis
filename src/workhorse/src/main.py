from utils import load_config
from datastructures import FastBipartite
from generators import generate_random_bipartite, generate_adversarial_z_trap, generate_arrival_order
from algorithms import online_greedy, online_ranking, hopcroft_karp
from runner import run_experiment, run_stress_tests

def main():
    # Load config from JSON + CLI
    config = load_config()
    
    # Validation check: ensure 'results' directory exists
    if not os.path.exists('results'):
        os.makedirs('results')

    try:
        if config.get('experiment_type') == 'stress_test':
            run_stress_tests(config)
        else:
            run_experiment(config)
    except KeyboardInterrupt:
        print("\n[STOP] Experiment interrupted by user.")
        sys.exit(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import os
    import sys
    main()