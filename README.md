# Blockchain Mining Simulation

A simulation of a blockchain-inspired system where miners perform computational tasks, validate results, and receive rewards based on performance, renewable energy usage, and verification contributions.

## Features

- Multiple types of computational tasks (addition, multiplication, sorting, searching)
- Score-based miner selection
- Renewable energy usage bonuses
- Consensus-based validation system
- Token rewards distribution
- Real-time visualization of system metrics

## Requirements

- Python 3.7+
- matplotlib
- numpy

## Installation

1. Clone the repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the simulation:
```bash
python main.py
```

The simulation will:
1. Create miners with random renewable energy proportions
2. Generate and distribute computational tasks
3. Execute tasks and validate solutions
4. Distribute rewards based on performance
5. Generate visualizations of system metrics

## Visualization

The simulation generates four plots:
1. Miner scores over time
2. Average renewable energy usage
3. Task success rate
4. Final token distribution

Plots are saved as 'simulation_results.png' in the project directory.

## Components

- `task.py`: Defines computational tasks and their execution
- `miner.py`: Implements miner behavior and scoring
- `distribution.py`: Handles task distribution logic
- `validation.py`: Manages solution validation and rewards
- `visualization.py`: Creates system metrics visualizations
- `main.py`: Orchestrates the simulation

## Configuration

You can modify the simulation parameters in `main.py`:
- Number of miners
- Number of tasks
- Reward multiplier (k)
- Task input sizes 