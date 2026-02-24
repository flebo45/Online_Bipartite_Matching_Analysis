import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob

# Visualization style
sns.set_theme(style="whitegrid")

# Data Post-Processing
def load_and_clean_data(file_pattern):
    print(f"Loading file matching: {file_pattern}")
    # Load all csv files matching the pattern
    all_files = glob.glob(file_pattern)
    if not all_files:
        raise FileNotFoundError(f"No files found matching pattern: {file_pattern}")

    # Concatenate all dataframes into one
    df = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)

    # Filter out invalid runs
    initial_count = len(df)
    df = df[df['is_valid'] == True]
    dropped = initial_count - len(df)
    if dropped > 0:
        print(f"Dropped {dropped} invalid runs from the dataset.")

    # Convert time in milliseconds for esier reading
    df['time_ms'] = df['time_ns'] / 1_000_000.0

    return df

# Analyze Scalability
def analyze_scalability(df):
    print(f"\nExperiment 1: Scalability Analysis")

    # Data Aggregation
    # Median for time (to ignore OS spikes), mean for competitive ratio
    agg_df = df.groupby(['n', 'algorithm']).agg(
        median_time_ms=('time_ms', 'median'),
        std_time_ms=('time_ms', 'std'),
        mean_cr=('cr', 'mean'),
    ).reset_index()

    # Pivot table for better plotting
    time_pivot = agg_df.pivot(index='n', columns='algorithm', values='median_time_ms')

    # Calculate Doubling ratios
    doubling_ratios = time_pivot / time_pivot.shift(1)

    # Logging
    print(f"\nMedian Execution Time (ms):")
    print(time_pivot.round(2))

    print(f"\nDoubling Ratios:")
    print(doubling_ratios.iloc[1:].round(2).to_string())
    print(f"\nExpectations:")
    print(f"- Greedy: O(E) -> Doubling ratio ~2 to 2.2")
    print(f"- Hopcroft-Karp: O(E * sqrt(V)) -> Doubling ratio ~2 * sqrt(2) ≈ 2.83 to 3.1")
    print(f"- Ranking: O(E * log(V)) -> Doubling ratio ~2 * log(2) ≈ 2.77 to 3.0")

    # Visualization Log-Log plot
    plt.figure(figsize=(10, 6))

    algorithms = df['algorithm'].unique()
    markers = {'greedy': 'o', 'ranking': 's', 'hopcroft_karp': '^'}

    for algo in algorithms:
        subset = agg_df[agg_df['algorithm'] == algo]
        plt.plot(subset['n'], subset['median_time_ms'], marker=markers.get(algo, 'o'), linewidth=2, label=algo.upper())
    
    # Axes in log scale (base 2 for N, base 10 for time)
    plt.xscale('log', base=2)
    plt.yscale('log', base=10)

    plt.title('Algorithm Scalability (Log-Log Plot)', fontsize=16, fontweight='bold')
    plt.xlabel('Input Size N (Log Scale)', fontsize=14)
    plt.ylabel('Median Time in ms (Log Scale)', fontsize=14)
    plt.legend(title='Algorithm', fontsize=12)
    plt.grid(True, which="both", ls="--", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('scalability_loglog_plot.png', dpi=300)
    print("\nSaved plot to 'scalability_loglog_plot.png'")
    plt.show()

def analyze_robustness(df):
    print(f"\nExperiment 2: Robustness Analysis")

    # Remove H-K cause it's ratio is always 1
    df_online = df[df['algorithm'].isin(['greedy', 'ranking'])].copy()

     # Summary Table
    summary = df_online.groupby(['algorithm', 'density', 'order'])['cr'].agg(
        ['mean', 'std', 'min', 'max']
    ).round(3)
    print("\nCompetitive Ratio Summary by Algorithm, Density, and Order:")
    print(summary.to_string())

    # Boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df_online, x='algorithm', y='cr', hue='order', palette='Set2')
    plt.title('Distribution of Competitive Ratios by Arrival Order', fontsize=16, fontweight='bold')
    plt.ylabel('Competitive Ratio (ALG / OPT)', fontsize=14)
    plt.xlabel('Algorithm', fontsize=14)
    plt.legend(title='Arrival Order', loc='lower right')
    plt.tight_layout()
    plt.savefig('../../analysis_plots/robustness_boxplot.png', dpi=300)
    print("\nSaved plot to 'robustness_boxplot.png'")
    plt.show()

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
    
    plt.savefig('../../analysis_plots/robustness_interaction_plot.png', dpi=300, bbox_inches='tight')
    print("Saved plot to 'robustness_interaction_plot.png'")
    plt.show()


if __name__ == "__main__":
    dataset = load_and_clean_data('../../results/Robustness_Horse_Race*.csv')

    print(f"Rows after loading and cleaning: {len(dataset)}")

    # 2. Check what unique values actually exist in your CSV
    if len(dataset) > 0:
        print("Unique densities found:", dataset['density'].unique())
        print("Unique orders found:", dataset['order'].unique())

    analyze_robustness(dataset)