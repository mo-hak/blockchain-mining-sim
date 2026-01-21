# Complete Documentation

This file consolidates all documentation for the blockchain mining simulation project.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Overview](#project-overview)
3. [Running Simulations](#running-simulations)
4. [Analysis Features](#analysis-features)
5. [Thesis Integration](#thesis-integration)
6. [Web Interface](#web-interface)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Basic Usage
```bash
# Single simulation
python3 main.py

# Multiple runs with statistics
python3 main.py multi-run 10

# Sensitivity analysis
python3 main.py sensitivity-error
python3 main.py sensitivity-verifiers

# Ablation study
python3 main.py ablation
```

### Generate Thesis Results
```bash
# Generate all results and plots
python3 generate_thesis_results.py all
python3 generate_thesis_plots.py
```

---

## Project Overview

This project implements a Computation-as-a-Service (CaaS) blockchain consensus model that replaces wasteful Proof-of-Work with useful computational tasks. The simulation models:

- **Miner Selection**: Score-based probabilistic selection with Byzantine fault tolerance
- **Task Execution**: Four task types (Addition, Multiplication, Sorting, Searching)
- **Validation**: Majority-based consensus with configurable verifier count
- **Rewards**: Base rewards + renewable energy bonuses
- **Byzantine Detection**: Continuous error rate monitoring with adaptive down-weighting

### Key Features

- Configurable parameters (17+ settings)
- Multiple-run statistical analysis with confidence intervals
- Sensitivity analysis across parameter ranges
- Ablation studies for component evaluation
- Web interface for interactive exploration
- Publication-quality plot generation

---

## Running Simulations

### Command-Line Interface

#### Single Simulation
```bash
python3 main.py
```

#### Multiple Runs (Statistical Analysis)
```bash
python3 main.py multi-run 10
```
Output: Mean ± 95% confidence intervals

#### Sensitivity Analysis

**Byzantine Error Rate:**
```bash
python3 main.py sensitivity-error
```
Tests error rates: 0.1, 0.2, 0.3, 0.4, 0.5

**Number of Verifiers:**
```bash
python3 main.py sensitivity-verifiers
```
Tests verifier counts: 1, 3, 5, 7, 9

#### Ablation Study
```bash
python3 main.py ablation
```
Tests: Full model, No renewable bonus, No fault tolerance

### Programmatic Usage

```python
from main import BlockchainSimulation

sim = BlockchainSimulation(
    num_miners=20,
    num_tasks=2000,
    max_byzantine=3,
    byzantine_error_rate=0.3,
    num_verifiers=3,
    fault_tolerance_enabled=True,
    seed=42  # For reproducibility
)

results = sim.run_simulation(verbose=False)
print(f"Success rate: {results['success_rate']:.2%}")
```

---

## Analysis Features

### Configurable Parameters

| Parameter | Default | Description |
|----------|---------|-------------|
| `num_miners` | 20 | Total number of miners |
| `num_tasks` | 1000 | Number of tasks to process |
| `max_byzantine` | 3 | Number of Byzantine miners |
| `byzantine_error_rate` | 0.3 | Error probability for Byzantine miners |
| `byzantine_threshold` | 0.2 | Error rate threshold for detection |
| `num_verifiers` | 3 | Number of verifiers per task |
| `fault_tolerance_enabled` | True | Enable Byzantine down-weighting |
| `reward_multiplier` | 1.0 | Base reward multiplier (k) |
| `renewable_energy_alpha` | None | Renewable proportion (None = random) |
| `seed` | None | Random seed for reproducibility |

### Key Metrics

- **Success Rate**: Percentage of tasks passing validation
- **Useful Work Efficiency (η)**: U/(U+W) where U=useful work, W=wasted work
- **Byzantine Marginalization**: Tasks and tokens received by Byzantine vs. honest miners
- **Selection Counts**: How many times each miner was selected

---

## Thesis Integration

### Generated Files

**Results:** `results_thesis/`
- `baseline_new.txt` - Baseline statistics (20 runs)
- `sensitivity_error_new.txt` - Error rate sensitivity
- `sensitivity_verifiers_new.txt` - Verifier count sensitivity
- `ablation_new.txt` - Ablation study results

**Plots:** `results_thesis/images/`
- `baseline_performance_summary.png`
- `sensitivity_error_rate.png`
- `sensitivity_verifiers.png`
- `ablation_study.png`
- `roc_curve_byzantine_detection.png`
- `pow_vs_caas_comparison.png`

**Thesis Files:** `docs/`
- `thesis_formmulation.tex` - Mathematical formulation
- `thesis_results.tex` - Experimental results (updated with real data)


### Key Results for Thesis

- **Baseline Success Rate**: 97.54% ± 0.14%
- **Useful Work Efficiency**: 75.03% ± 0.11%
- **Fault Tolerance Impact**: 7.36% improvement (97.52% vs. 90.17%)
- **Byzantine Marginalization**: 6.7× fewer tasks, 6.7% of tokens
- **ROC AUC**: > 0.95 (excellent detection)

---

## Web Interface

### Starting the Web Server

```bash
# Linux/Mac
./start_web.sh

# Windows
start_web.bat

# Or directly
python3 app.py
```

Server runs on `http://localhost:5001`

### API Endpoints

- `GET /` - Main interface
- `POST /api/simulate` - Run simulation (streaming)
- `POST /api/simulate/sync` - Run simulation (synchronous)
- `GET /api/config/default` - Get default configuration

### Web Interface Features

- Interactive parameter configuration
- Real-time simulation progress
- Visualizations (scores, tokens, success rate)
- Results export
- All protocol-level features from command-line

---

## Troubleshooting

### Common Issues

**"No module named 'numpy'"**
```bash
pip install -r requirements.txt
```

**"Figure not found" (in thesis)**
- Ensure images are in `Images/` folder (capital I) in Overleaf
- Check image paths in LaTeX match actual filenames

**"Results don't show expected trends"**
- Use `generate_thesis_results.py` for properly parameterized results
- See `RESULTS_EXPLANATION.md` for why results are what they are

**"Simulation too slow"**
- Reduce `num_tasks` (e.g., 500 instead of 2000)
- Reduce `num_miners` (e.g., 10 instead of 20)
- Use `verbose=False` for batch runs

### Performance Tips

- Single run: ~10 seconds (1000 tasks, 20 miners)
- 10 runs: ~2 minutes
- Full sensitivity analysis: ~15-20 minutes
- Use `seed` parameter for reproducible results

---

## File Structure

```
blockchain-mining-sim/
├── main.py                    # Core simulation engine
├── app.py                     # Web interface
├── miner.py                   # Miner implementation
├── task.py                    # Task types
├── distribution.py            # Task distribution
├── validation.py              # Validation manager
├── visualization.py           # Plotting utilities
├── generate_thesis_results.py # Generate thesis data
├── generate_thesis_plots.py   # Generate thesis plots
├── docs/
│   ├── thesis_formmulation.tex
│   └── thesis_results.tex
├── results/
│   └── *_new.txt             # Generated results
├── results_thesis/
│   └── images/               # Publication plots
├── static/                    # Web interface assets
├── templates/                 # Web interface templates
└── requirements.txt           # Dependencies
```

---


---

## Support

For detailed explanations:
- **Reviewer Responses**: See how all reviewer comments were addressed
- **Results Explanation**: Why results show specific trends
- **Analysis Guide**: Detailed usage of analysis features

All documentation has been consolidated into this file for easy reference.
