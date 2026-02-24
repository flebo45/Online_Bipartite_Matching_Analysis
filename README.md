# Online Bipartite Matching: An Algorithm Engineering Study

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Algorithm Engineering](https://img.shields.io/badge/Course-Algorithm%20Engineering-orange.svg)]()

A rigorous empirical evaluation of online matching algorithms, implementing the **Algorithm Engineering methodology** to bridge theoretical guarantees with practical performance. This project compares two online heuristics against an offline optimal baseline across synthetic and real-world datasets.

---

## Table of Contents

- Problem Statement
- Algorithms Implemented
- Features
- Installation
- Usage
- Experimental Design
- Project Structure
- Results & Analysis
- References

---

## Problem Statement

The **Online Bipartite Matching** problem is a fundamental challenge in combinatorial optimization with applications in ad allocation, job scheduling, and recommendation systems. Given a bipartite graph $G = (U, V, E)$:

- **Offline vertices** $V$ are known in advance
- **Online vertices** $U$ arrive sequentially in an adversarial or stochastic order
- Upon arrival, each online vertex $u \in U$ must be **irrevocably** matched to an available neighbor $v \in V$, or left unmatched

The objective is to maximize the matching size. Performance is measured via the **Competitive Ratio**:

$$CR = \frac{|M_{ALG}|}{|M_{OPT}|}$$

where $M_{OPT}$ is the maximum matching computed offline.

---

## Algorithms Implemented

| Algorithm                | Type    | Time Complexity | Theoretical CR                  |
| ------------------------ | ------- | --------------- | ------------------------------- |
| **Deterministic Greedy** | Online  | $O(E)$          | $0.5$ (worst-case)              |
| **Ranking (KVV)**        | Online  | $O(E)$          | $1 - \frac{1}{e} \approx 0.632$ |
| **Hopcroft-Karp**        | Offline | $O(E\sqrt{V})$  | $1.0$ (optimal)                 |

### Algorithm Details

- **Deterministic Greedy**: Matches arriving vertices to the first available neighbor using fixed tie-breaking (lowest index). Simple but vulnerable to adversarial inputs.

- **Ranking (Karp-Vazirani-Vazirani)**: Assigns random priorities to offline vertices at initialization. Arriving online vertices match to their highest-priority available neighbor. Achieves the optimal competitive ratio for the adversarial model.

- **Hopcroft-Karp**: Computes the maximum cardinality matching offline via alternating BFS/DFS phases. Implementation uses **iterative DFS** to circumvent Python's recursion limits on large graphs.

---

## Features

- **Strict Reproducibility**: RNG state snapshotting and `--seed` flag ensure identical results across runs
- **High-Performance Data Structures**: Custom [`FastBipartite`](src/workhorse/src/datastructures.py) graph using `__slots__` for minimal memory overhead
- **Independent Validation**: Every matching is certified by [`validate_matching()`](src/workhorse/src/validation.py) to ensure structural feasibility
- **Precise Benchmarking**: Uses `time.process_time_ns()` with GC disabled during measurement
- **Configurable Experiments**: JSON-driven experimental design with CLI overrides
- **Real-World Testing**: MovieLens dataset loader with chronological arrival ordering

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/flebo45/Online_Bipartite_Matching_Analysis.git
cd OnlineBipartiteMatching

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

```
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
seaborn>=0.11.0
networkx>=2.6.0  # For pilot phase validation
```

---

## Usage

### Basic Execution

```bash
# Navigate to the workhorse implementation
cd src/workhorse

# Run an experiment with a configuration file
python src/main.py --config /configs/scalability_study.json
```

### Command-Line Interface

| Argument      | Description                                              |
| ------------- | -------------------------------------------------------- |
| `--config`    | Path to JSON configuration file (required)               |
| `--algorithm` | Override algorithm: `greedy`, `ranking`, `hopcroft_karp` |
| `--n`         | Override input size $N$                                  |
| `--trials`    | Override number of trials per design point               |
| `--seed`      | Fixed seed for reproducibility (sets trials to 1)        |

### Configuration Format

```json
{
  "experiment_name": "Scalability Study",
  "experiment_type": "standard",
  "n_list": [1024, 2048, 4096, 8192, 16384, 32768],
  "densities": ["sparse", "medium"],
  "orders": ["random"],
  "algorithms": ["greedy", "ranking", "hopcroft_karp"],
  "trials": 30
}
```

### Reproducible Single Run

```bash
python src/main.py --config /configs/test_config.json --seed 42
```

---

## Experimental Design

The project implements four distinct experiments following Algorithm Engineering principles:

### 1. Scalability Study (Doubling Experiment)

Tests algorithmic complexity by doubling input size $N \in \{1024, 2048, ..., 32768\}$.

**Expected Doubling Ratios:**

- Greedy: $\approx 2.0$ (linear)
- Hopcroft-Karp: $\approx 2.83$ ($O(E\sqrt{V})$)
- Ranking: $\approx 2.0$ (linear)

```bash
python main.py --config ../configs/scalability_study.json
```

### 2. Robustness Study (Factorial Design)

Full factorial experiment crossing:

- **Graph Density**: `sparse` ($p = \frac{\log n}{n}$), `medium` ($p = \frac{1}{\sqrt{n}}$), `dense` ($p = 0.5$)
- **Arrival Order**: `random`, `adversarial` (greedy starvation heuristic)

```bash
python main.py --config ../configs/horserace_study.json
```

### 3. Real-World Analysis

Evaluates algorithms on the **MovieLens 100K** dataset:

- Users as online vertices (sorted by first interaction timestamp)
- Movies as offline vertices
- Edges represent ratings $\geq 4.0$

```bash
python main.py --config ../configs/movie_real.json
```

### 4. Stress Testing

Deterministic verification on edge cases:

- Empty graphs
- Single-edge graphs
- Disconnected components
- Adversarial Z-trap structures

```bash
python main.py --config ../configs/stress_study.json
```

---

## Project Structure

```
OnlineBipartiteMatching/
├── README.md
├── requirements.txt
│
└── src/
    ├── pilot/                          # Prototyping & validation phase
    │   ├── BipartitePilot.py           # NetworkX-backed graph wrapper
    │   ├── algorithms.py               # Reference implementations
    │   ├── generator.py                # Simple graph generators
    │   ├── pilot_test.py               # Smoke tests & validation
    │   └── pilot_vis.py                # Visualization utilities
    │
    └── workhorse/                      # Production implementation
        ├── configs/                    # JSON experiment configurations
        │   ├── scalability_study.json
        │   ├── horserace_study.json
        │   ├── movie_real.json
        │   ├── stress_study.json
        │   └── test_config.json
        │
        ├── data/                       # Dataset storage (e.g., MovieLens)
        │
        ├── results/                    # CSV output from experiments
        │   ├── Scalability_Study_*.csv
        │   ├── Robustness_Horse_Race_*.csv
        │   └── Real_World_-_MovieLens_*.csv
        │
        ├── analysis_plots/             # Generated visualizations
        │
        └── src/
            ├── main.py                 # Entry point
            ├── runner.py               # Experiment execution engine
            ├── utils.py                # CLI parsing & config loading
            ├── datastructures.py       # FastBipartite graph class
            ├── algorithms.py           # Core algorithm implementations
            ├── generators.py           # Synthetic graph generation
            ├── loaders.py              # Real-world dataset parsing
            ├── validation.py           # Matching certifier
            └── analysis.py             # Post-processing & plotting
```

---

## Results & Analysis

After running experiments, generate visualizations using the analysis module:

```bash
cd src/workhorse/src
python analysis.py
```

### Generated Plots

| Plot                              | Description                          |
| --------------------------------- | ------------------------------------ |
| `scalability_loglog_plot.png`     | Log-log time complexity verification |
| `robustness_boxplot.png`          | CR distribution by arrival order     |
| `robustness_interaction_plot.png` | Factorial interaction effects        |
| `realworld_cr_barplot.png`        | MovieLens performance comparison     |

## References

1. Karp, R. M., Vazirani, U. V., & Vazirani, V. V. (1990). _An optimal algorithm for on-line bipartite matching_. STOC '90.

2. Hopcroft, J. E., & Karp, R. M. (1973). _An $n^{5/2}$ algorithm for maximum matchings in bipartite graphs_. SIAM Journal on Computing.

3. Mehta, A. (2013). _Online Matching and Ad Allocation_. Foundations and Trends in Theoretical Computer Science.

4. Sanders, P. (2009). _Algorithm Engineering – An Attempt at a Definition_. Efficient Algorithms, LNCS 5760.

---

## License

This project is licensed under the MIT License. See LICENSE for details.

---

<p align="center">
  <i>Developed as part of the Algorithm Engineering course curriculum</i>
</p>
