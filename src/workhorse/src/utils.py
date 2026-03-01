import json
import argparse
import sys

def load_config():
    """
    Loads parameters from a JSON file and overrides them with command-line arguments if provided

    Returns:
        dict: A dictionary containing the configuration parameters
    """
    # CLI Arguments
    parser = argparse.ArgumentParser(description="Workhorse Implementation")
    
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration JSON file")
    parser.add_argument("--algorithm", type=str, help="Override algorithm name from config")
    parser.add_argument("--n", type=int, help="Override input size N")
    parser.add_argument("--trials", type=int, help="Override number of trials")
    parser.add_argument("--seed", type=int, help="Fixed seed for reproducibility")
    parser.add_argument("--densities", type=str, help="Comma-separated list of densities (e.g., 'sparse, medium, dense')")

    args = parser.parse_args()

    # Load config from JSON
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{args.config}' not found.")
        sys.exit(1)

    # Override with CLI arguments if provided
    if args.algorithm:
        config['algorithm'] = args.algorithm
    if args.n:
        config['n_list'] = [args.n]
    if args.trials:
        config['trials'] = args.trials
    if args.densities:
        config['densities'] = [d.strip() for d in args.densities.split(',')]
    if args.seed is not None:
        config['fixed_seed'] = args.seed
        config['trials'] = 1  # If a fixed seed is provided, we only need one trial
        print(f"[INFO] Fixed seed provided: {args.seed}. Setting trials to 1 for reproducibility.")
    print(f"[INFO] Loaded Config: {config['experiment_name']}")
    return config