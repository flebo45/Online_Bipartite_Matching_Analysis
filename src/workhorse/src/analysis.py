import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import logging
import argparse
from datetime import datetime

# Visualization style
sns.set_theme(style="whitegrid")

def setup_logger(experiment_name):
    """Sets up a file-only logger for the given experiment."""
    os.makedirs('analysis_logs', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"analysis_logs/{experiment_name}_{timestamp}.log"

    logger = logging.getLogger(experiment_name)
    logger.setLevel(logging.INFO)

    # Clear existing handlers if any
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler
    fh = logging.FileHandler(log_file, mode='w')
    fh.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(fh)
    
    print(f"[{experiment_name.upper()}] Running analysis... Logs are being saved to: {log_file}")
    return logger, timestamp

# Data Post-Processing
def load_and_clean_data(file_pattern, logger):
    logger.info(f"Loading file(s) matching pattern: {file_pattern}")
    # Load all csv files matching the pattern
    all_files = glob.glob(file_pattern)
    if not all_files:
        logger.error(f"No files found matching pattern: {file_pattern}")
        raise FileNotFoundError(f"No files found matching pattern: {file_pattern}")

    logger.info(f"Files loaded:\n" + "\n".join([f"- {f}" for f in all_files]))    

    # Concatenate all dataframes into one
    df = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)

    # Filter out invalid runs
    initial_count = len(df)
    df = df[df['is_valid'] == True]
    dropped = initial_count - len(df)
    if dropped > 0:
        logger.info(f"Dropped {dropped} invalid runs from the dataset.")

    # Convert time in milliseconds for esier reading
    df['time_ms'] = df['time_ns'] / 1_000_000.0
    logger.info(f"Total valid rows after cleaning: {len(df)}\n")

    return df

# Analyze Scalability
def analyze_scalability(file_pattern):
    logger, timestamp = setup_logger("scalability")
    df = load_and_clean_data(file_pattern, logger)

    logger.info(f"\nExperiment 1: Scalability Analysis")

    # Data Aggregation
    # Meam for time (to ignore OS spikes), mean for competitive ratio
    agg_df = df.groupby(['n', 'algorithm']).agg(
        mean_time_ms=('time_ms', 'mean'),
        std_time_ms=('time_ms', 'std'),
        mean_cr=('cr', 'mean'),
    ).reset_index()

    # Pivot table for better plotting
    time_pivot = agg_df.pivot(index='n', columns='algorithm', values='mean_time_ms')

    # Calculate Doubling ratios
    doubling_ratios = time_pivot / time_pivot.shift(1)

    # Logging
    logger.info(f"\nMean Execution Time (ms):")
    logger.info(time_pivot.round(2))

    logger.info(f"\nDoubling Ratios:")
    logger.info(doubling_ratios.iloc[1:].round(2).to_string())
    logger.info(f"\nExpectations:")
    logger.info(f"- Greedy: O(E) -> Doubling ratio ~2")
    logger.info(f"- Hopcroft-Karp: O(E * sqrt(V)) -> Doubling ratio ~2 * sqrt(2) ≈ 2.83")
    logger.info(f"- Ranking: O(E) -> Doubling ratio ~2")

    # Visualization Log-Log plot
    plt.figure(figsize=(10, 6))

    algorithms = df['algorithm'].unique()
    markers = {'greedy': 'o', 'ranking': 's', 'hopcroft_karp': '^'}

    for algo in algorithms:
        subset = agg_df[agg_df['algorithm'] == algo]
        plt.plot(subset['n'], subset['mean_time_ms'], marker=markers.get(algo, 'o'), linewidth=2, label=algo.upper())
    
    # Axes in log scale (base 2 for N, base 10 for time)
    plt.xscale('log', base=2)
    plt.yscale('log', base=10)

    plt.title('Algorithm Scalability (Log-Log Plot)', fontsize=16, fontweight='bold')
    plt.xlabel('Input Size N (Log Scale)', fontsize=14)
    plt.ylabel('Median Time in ms (Log Scale)', fontsize=14)
    plt.legend(title='Algorithm', fontsize=12)
    plt.grid(True, which="both", ls="--", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(f'analysis_plots/scalability_loglog_plot_{timestamp}.pdf', format='pdf', dpi=300)
    logger.info(f"\nSaved plot to 'scalability_loglog_plot_{timestamp}.pdf'")

def analyze_robustness(file_pattern):
    logger, timestamp = setup_logger("robustness")
    df = load_and_clean_data(file_pattern, logger)

    logger.info(f"\nExperiment 2: Robustness Analysis")

    # Remove H-K cause it's ratio is always 1
    df_online = df[df['algorithm'].isin(['greedy', 'ranking'])].copy()

     # Summary Table
    summary = df_online.groupby(['algorithm', 'density', 'order'])['cr'].agg(
        ['mean', 'std', 'min', 'max']
    ).round(3)
    logger.info("\nCompetitive Ratio Summary by Algorithm, Density, and Order:")
    logger.info(summary.to_string())

    # Boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df_online, x='algorithm', y='cr', hue='order', palette='Set2')
    plt.title('Distribution of Competitive Ratios by Arrival Order', fontsize=16, fontweight='bold')
    plt.ylabel('Competitive Ratio (ALG / OPT)', fontsize=14)
    plt.xlabel('Algorithm', fontsize=14)
    plt.legend(title='Arrival Order', loc='lower right')
    plt.tight_layout()
    plt.savefig(f'analysis_plots/robustness_boxplot_{timestamp}.pdf', format='pdf', dpi=300)
    logger.info(f"\nSaved plot to 'robustness_boxplot_{timestamp}.pdf'")

    # Interaction Plot
    g = sns.catplot(
        data=df_online,
        x='density', y='cr', hue='order', col='algorithm',
        kind='point', markers=['o', 's'], linestyles=['-', '--'],
        palette='Dark2', height=5, aspect=1.2, errorbar='sd'
    )

    g.fig.suptitle('Factorial Interaction Effects: Density vs. Arrival Order', fontsize=16, fontweight='bold', y=1.05)
    g.set_axis_labels("Graph Density", "Mean Competitive Ratio")
    g.set_titles("Algorithm: {col_name}")

    g.set(ylim=(0.45, 1.05))
    
    plt.savefig(f'analysis_plots/robustness_interaction_plot_{timestamp}.pdf', format='pdf', dpi=300, bbox_inches='tight')
    logger.info(f"Saved plot to 'robustness_interaction_plot_{timestamp}.pdf'")

def analyze_real_world(file_pattern):
    logger, timestamp = setup_logger("realworld")
    df = load_and_clean_data(file_pattern, logger)
    logger.info(f"\nExperiment 3: Real-World Performance Analysis")

    # Remove H-K cause it's ratio is always 1
    df_online = df[df['algorithm'].isin(['greedy', 'ranking'])].copy()

     # Summary Table
    summary = df_online.groupby(['algorithm','order'])['cr'].agg(
        ['mean', 'std', 'min', 'max']
    ).round(4)
    logger.info("\nCompetitive Ratio Summary by Algorithm and Order:")
    logger.info(summary.to_string())

    # Bar Chart
    plt.figure(figsize=(9, 6))

    # bar plot to show average performance diffrences
    ax = sns.barplot(
        data=df_online, 
        x='algorithm', 
        y='cr', 
        hue='order', 
        palette='viridis',
        capsize=0.05,
        err_kws={'linewidth': 1.5}
    )

    plt.title('Real-World Performance', fontsize=16, fontweight='bold')
    plt.ylabel('Mean Competitive Ratio (ALG / OPT)', fontsize=14)
    plt.xlabel('Algorithm', fontsize=14)

    plt.ylim(0.5, 1.0)
    plt.legend(title='Arrival Order', loc='lower right')

    for p in ax.patches:
        ax.annotate(format(p.get_height(), '.3f'), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    xytext = (0, 9), 
                    textcoords = 'offset points')

    plt.tight_layout()
    plt.savefig(f'analysis_plots/realworld_cr_barplot_{timestamp}.pdf', format='pdf', dpi=300)
    logger.info(f"\nSaved plot to 'realworld_cr_barplot_{timestamp}.pdf'")

def analyze_stress_test(file_pattern):
    logger, timestamp = setup_logger("stress_test")

    all_files = glob.glob(file_pattern)
    if not all_files:
        logger.error(f"No files found matching pattern: {file_pattern}")
        raise FileNotFoundError(f"No files found matching pattern: {file_pattern}")

    # Load the most recent stress test file
    latest_file = max(all_files, key=lambda x: x)
    logger.info(f"Loading latest stress test report: {latest_file}")
    df = pd.read_csv(latest_file)

    logger.info(f"\nExperiment 4: Stress Test Analysis")

    # 1. Quick sanity check: Did anything crash?
    total_tests = len(df)
    passed_tests = len(df[df['status'] == 'PASS'])
    failed_tests = total_tests - passed_tests
    
    logger.info(f"Total Test Executions: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed/Crashed: {failed_tests}\n")
    
    if failed_tests > 0:
        logger.warning("You have failing edge cases! See details below:")
        logger.info(df[df['status'] != 'PASS'][['id', 'type', 'algorithm', 'status', 'message']].to_string(index=False))
        logger.info("\n")

    # 2. Build the Verification Matrix
    # We want rows to be the Test Cases, and columns to be the Algorithms, showing the Status
    matrix = df.pivot(index=['id', 'type'], columns='algorithm', values='status')
    
    logger.info("Verification Matrix:")
    logger.info(matrix.to_string())
    
    # 3. Show the actual match sizes for the Z-Trap (DP-V5) to prove the adversary worked
    logger.info("\nDeep Dive: The Z-Trap Adversarial Edge Case (DP-V5)")
    z_trap_data = df[df['type'] == 'z_trap'][['algorithm', 'match_size', 'expected']]
    logger.info(z_trap_data.to_string(index=False))
    


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Analyze experimental results and generate PDF plots.")
    parser.add_argument(
        "--analysis", 
        type=str, 
        choices=['scalability', 'robustness', 'real_world', 'stress', 'all'], 
        default='all', 
        help="Specify which analysis to run (default: all)"
    )
    args = parser.parse_args()

    PATTERN_SCALABILITY = 'results/Scalability_Study*.csv'
    PATTERN_ROBUSTNESS  = 'results/Robustness_Horse_Race*.csv'
    PATTERN_REAL_WORLD  = 'results/Real_World_*.csv'
    PATTERN_STRESS      = 'results/Stress_study_*.csv'

    # Execute based on arguments
    if args.analysis in ['scalability', 'all']:
        analyze_scalability(PATTERN_SCALABILITY)
        
    if args.analysis in ['robustness', 'all']:
        analyze_robustness(PATTERN_ROBUSTNESS)
        
    if args.analysis in ['real_world', 'all']:
        analyze_real_world(PATTERN_REAL_WORLD)
        
    if args.analysis in ['stress', 'all']:
        analyze_stress_test(PATTERN_STRESS)
        
    print("\n[DONE] Requested analyses completed. Check the 'analysis_plots/' and 'analysis_logs/' directories.")