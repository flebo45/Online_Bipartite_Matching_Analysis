# Online vs Offline Bipartite Matching

Algorithm Engineering study analyzing the empirical performance gap between online and offline algorithms for bipartite matching.

## Project Structure

```
OnlineBipartiteMatching/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── config.py             # Experimental configuration
│   ├── algorithms.py         # Matching algorithms (HK, Greedy, Ranking)
│   ├── generators.py         # Graph generators (Erdős-Rényi, Z-Graph)
│   ├── validation.py         # Certifying checker for correctness
│   ├── runner.py             # Experimental harness
│   └── main.py               # CLI entry point
├── results/                  # Output directory (auto-created)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Algorithms

| Algorithm                       | Type    | Deterministic | Competitive Ratio  |
| ------------------------------- | ------- | ------------- | ------------------ |
| **Hopcroft-Karp**               | Offline | Yes           | Optimal (1.0)      |
| **Greedy (Fixed Tie-Breaking)** | Online  | Yes           | ≥ 0.5 (worst case) |
| **Ranking (KVV)**               | Online  | No            | ≥ 1 - 1/e ≈ 0.632  |

## Quick Start

```bash
# Run validation tests
python -m src.main validate

# View algorithm information
python -m src.main info

# Run scalability study (small)
python -m src.main scalability --sizes 10,11,12 --reps 5 --summary

# Run horse race comparison
python -m src.main horserace --size 2048 --reps 20 --summary

# Run adversarial analysis (Z-Graph)
python -m src.main adversarial --sizes 8,10,12 --reps 10
```

## Experimental Design

### Factors

- **Input Size (N)**: 2^10 to 2^15 (1,024 to 32,768 vertices per side)
- **Graph Density**: Sparse (~log n), Medium (~√n), Dense (~n/2)
- **Arrival Order**: Random, Adversarial (sorted)

### Metrics

- **CPU Time**: Measured using `time.process_time()` (excludes I/O)
- **Competitive Ratio**: |M_online| / |M_offline|

### Design Principles

- **Warm-up Runs**: Dummy executions to stabilize JIT/interpreter
- **Repetitions**: Multiple runs per design point for statistical significance
- **Validation**: Certifying checker verifies all matchings

## Output Format

Results are saved in both CSV and JSON formats:

```
results/
├── scalability_study_20260210_143052.csv
├── scalability_study_20260210_143052.json
├── horse_race_20260210_144123.csv
└── horse_race_20260210_144123.json
```

### CSV Schema

```csv
input_size,density,arrival_order,repetition,seed,num_edges,algorithm,matching_size,cpu_time_seconds,wall_time_seconds,competitive_ratio,is_valid
```

### JSON Schema

```json
{
  "experiment_name": "scalability_study",
  "timestamp": "20260210_143052",
  "num_results": 150,
  "results": [
    {
      "design_point": {...},
      "graph_metadata": {...},
      "algorithm_results": {...}
    }
  ]
}
```

## API Usage

```python
from src.algorithms import hopcroft_karp, greedy_matching, ranking_algorithm
from src.generators import generate_erdos_renyi_bipartite, generate_adversarial_z_graph
from src.validation import validate_matching
from src.runner import ExperimentRunner

# Generate a random bipartite graph
graph = generate_erdos_renyi_bipartite(n_left=1000, n_right=1000, edge_prob=0.1)

# Run Hopcroft-Karp (optimal)
matching, size = hopcroft_karp(graph.adj, graph.left_vertices, graph.right_vertices)

# Validate the result
result = validate_matching(matching, graph.adj, graph.left_vertices, graph.right_vertices)
print(result.summary())

# Run a complete experiment
runner = ExperimentRunner(output_dir="results", warmup_runs=2)
design_points = runner.generate_design_points(
    input_sizes=[1024, 2048],
    densities=["sparse", "medium"],
    arrival_orders=["random"],
    repetitions=5
)
results = runner.run_experiment(design_points, experiment_name="my_experiment")
```

## Z-Graph (Adversarial Construction)

The Z-Graph forces Greedy to achieve exactly 0.5 competitive ratio:

```
u_1 ─── v_1
    ╲
     ╲── v_2
u_2 ────╱
    ╲
     ╲── v_3
u_3 ────╱
    ⋮
```

With adversarial arrival (u_1, u_2, ..., u_n):

- Greedy matches: u_1→v_1, u_3→v_3, u_5→v_5, ... (~n/2 matches)
- Optimal matches: u_1→v_2, u_2→v_3, ..., u_n→v_1 (n matches)

## License

MIT License - For academic and research purposes.
