import random
from typing import List, Dict, Tuple
import time
import numpy as np
from task import Task, TaskType
from miner import Miner
from distribution import TaskDistributor
from validation import ValidationManager
from visualization import Visualizer

class BlockchainSimulation:
    def __init__(self, num_miners: int = 20, num_tasks: int = 1000, 
                 max_byzantine: int = 3, byzantine_error_rate: float = 0.3,
                 reward_multiplier: float = 1.0, renewable_energy_alpha: float = None,
                 num_verifiers: int = 3, byzantine_threshold: float = 0.2,
                 fault_tolerance_enabled: bool = True, seed: int = None):
        """
        Initialize blockchain simulation with configurable parameters.
        
        Args:
            num_miners: Number of miners (thesis default: 20)
            num_tasks: Number of tasks to simulate
            max_byzantine: Number of Byzantine miners (thesis default: up to 3)
            byzantine_error_rate: Error rate for Byzantine miners (thesis Eq.3: 0.3)
            reward_multiplier: k value (thesis Eq.5-8: default 1.0)
            renewable_energy_alpha: α_m value ∈ [0, 0.5] (thesis Eq.6)
                                   If None, random per miner. If set, all miners use this value.
            num_verifiers: Number of verifiers per task V (thesis Eq.11: default 3)
            byzantine_threshold: Threshold for Byzantine detection (thesis Eq.2: 0.2)
            fault_tolerance_enabled: Enable Byzantine fault tolerance (Eq.4 penalties)
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Create miners with deterministic Byzantine selection
        self.miners = Miner.create_miners(
            num_miners=num_miners,
            max_byzantine=max_byzantine,
            byzantine_error_rate=byzantine_error_rate,
            renewable_energy_alpha=renewable_energy_alpha
        )
        self.distributor = TaskDistributor(self.miners, fault_tolerance_enabled=fault_tolerance_enabled)
        self.validator = ValidationManager(k=reward_multiplier)  # Per thesis Equations 5-8
        self.visualizer = Visualizer()
        self.total_tasks = num_tasks
        self.completed_tasks = 0
        self.successful_tasks = 0
        self.byzantine_threshold = byzantine_threshold
        self.actual_byzantine_count = sum(1 for m in self.miners if m.is_byzantine)
        self.num_verifiers = num_verifiers
        self.fault_tolerance_enabled = fault_tolerance_enabled
        
        # Metrics tracking for analysis
        self.task_history = []
        self.success_rate_history = []
        self.miner_selection_count = {m.miner_id: 0 for m in self.miners}

    def generate_random_task(self) -> Task:
        """Generate a random task with random input size."""
        task_type = random.choice(list(TaskType))
        input_size = random.randint(10, 100)
        return Task(task_type, input_size)

    def run_simulation(self, verbose: bool = True):
        """Run the main simulation loop."""
        if verbose:
            print("Starting blockchain mining simulation...")
            print(f"Number of miners: {len(self.miners)}")
            print(f"Number of tasks: {self.total_tasks}")
            print(f"Byzantine miners: {self.actual_byzantine_count}")
            print(f"Number of verifiers per task (V): {self.num_verifiers}")
            print(f"Byzantine fault tolerance: {'Enabled' if self.fault_tolerance_enabled else 'Disabled'}")
            print(f"Byzantine threshold: {self.byzantine_threshold:.2%}")
            print("\nInitial miner states:")
            for miner in self.miners:
                print(miner)
            print("\nStarting tasks...")

        # Generate initial task queue
        for _ in range(self.total_tasks):
            self.distributor.add_task(self.generate_random_task())

        while self.completed_tasks < self.total_tasks:
            # Distribute task with configured number of verifiers
            distribution_result = self.distributor.distribute_task(num_verifiers=self.num_verifiers)
            if not distribution_result:
                break

            task, miner, verifiers = distribution_result
            
            # Track miner selection
            self.miner_selection_count[miner.miner_id] += 1
            
            # Only print every 100th task to avoid console spam
            if verbose and (self.completed_tasks + 1) % 100 == 0:
                print(f"\nTask {self.completed_tasks + 1}/{self.total_tasks}")
                print(f"Assigned to: {miner}")
                print(f"Verifiers: {len(verifiers)}")

            # Execute task
            solution = miner.execute_task(task)

            # Validate and process rewards
            is_valid = self.validator.process_validation(task, solution)
            if is_valid:
                self.successful_tasks += 1
                if verbose and (self.completed_tasks + 1) % 100 == 0:
                    print("Task completed successfully!")
            else:
                if verbose and (self.completed_tasks + 1) % 100 == 0:
                    print("Task failed validation.")
                    if miner.error_rate > self.byzantine_threshold:
                        print(f"WARNING: Miner {miner.miner_id} shows Byzantine behavior! "
                              f"Error rate: {miner.error_rate:.2%}")

            self.completed_tasks += 1
            success_rate = self.successful_tasks / self.completed_tasks
            self.success_rate_history.append(success_rate)
            
            # Store task outcome for analysis
            self.task_history.append({
                'task_id': self.completed_tasks,
                'miner_id': miner.miner_id,
                'is_byzantine': miner.is_byzantine,
                'is_valid': is_valid,
                'num_verifiers': len(verifiers)
            })
            
            if verbose and (self.completed_tasks) % 100 == 0:
                print(f"Current success rate: {success_rate:.2%}")

            # Update visualization (only if verbose)
            if verbose:
                self.visualizer.update_metrics(self.miners, success_rate)
                if self.completed_tasks % 100 == 0:  # Update plot every 100 tasks
                    self.visualizer.plot_metrics()

        # Final visualization
        if verbose:
            self.visualizer.plot_metrics()
            self.print_final_stats()
        
        return self.get_simulation_results()

    def get_simulation_results(self) -> Dict:
        """Get comprehensive simulation results for analysis."""
        byzantine_miners = [m for m in self.miners if m.error_rate > self.byzantine_threshold]
        honest_miners = [m for m in self.miners if m.error_rate <= self.byzantine_threshold]
        
        results = {
            'success_rate': self.successful_tasks / self.completed_tasks if self.completed_tasks > 0 else 0,
            'total_tasks': self.completed_tasks,
            'successful_tasks': self.successful_tasks,
            'byzantine_count': len(byzantine_miners),
            'avg_tasks_honest': np.mean([m.tasks_completed for m in honest_miners]) if honest_miners else 0,
            'avg_tasks_byzantine': np.mean([m.tasks_completed for m in byzantine_miners]) if byzantine_miners else 0,
            'avg_tokens_honest': np.mean([m.tokens for m in honest_miners]) if honest_miners else 0,
            'avg_tokens_byzantine': np.mean([m.tokens for m in byzantine_miners]) if byzantine_miners else 0,
            'task_history': self.task_history,
            'miner_selection_count': self.miner_selection_count,
            'miners': self.miners,
            'success_rate_history': self.success_rate_history,
            'useful_work_efficiency': self.calculate_useful_work_efficiency()
        }
        return results
    
    def calculate_useful_work_efficiency(self) -> float:
        """
        Calculate useful work efficiency η = U/(U+W).
        U = useful work (successful tasks), W = wasted work (failed tasks + verification overhead).
        """
        useful_work = self.successful_tasks
        wasted_work = (self.completed_tasks - self.successful_tasks) + (self.completed_tasks * self.num_verifiers * 0.1)
        return useful_work / (useful_work + wasted_work) if (useful_work + wasted_work) > 0 else 0
    
    def print_final_stats(self):
        """Print final simulation statistics with detailed Byzantine analysis."""
        print("\n=== Final Statistics ===")
        print("\n1. Overall Performance:")
        print(f"   Total tasks completed: {self.completed_tasks}")
        print(f"   Successful tasks: {self.successful_tasks}")
        print(f"   Overall success rate: {(self.successful_tasks / self.completed_tasks):.2%}")
        print(f"   Useful work efficiency (η): {self.calculate_useful_work_efficiency():.2%}")
        
        # Byzantine Analysis
        byzantine_miners = [m for m in self.miners if m.error_rate > self.byzantine_threshold]
        print(f"   {len(byzantine_miners)} miners showed Byzantine behavior (error rate > {self.byzantine_threshold:.0%})")
        
        print("\n2. Byzantine Miners (error rate > 20%):")
        # Sort byzantine miners by error rate
        byzantine_miners.sort(key=lambda x: x.error_rate, reverse=True)
        for miner in byzantine_miners:
            print(f"   Miner {miner.miner_id}: {miner.error_rate:.2%} error rate, selected {self.miner_selection_count[miner.miner_id]} times")
        
        print("\n3. Impact of Byzantine Behavior on Rewards:")
        # Sort all miners by tokens for top performers
        sorted_miners = sorted(self.miners, key=lambda x: x.tokens, reverse=True)
        top_performers = sorted_miners[:4]
        print("   Top performers:")
        for miner in top_performers:
            print(f"   Miner {miner.miner_id}: {miner.tasks_completed} tasks, {miner.error_rate:.2%} error rate, {miner.tokens:.0f} tokens")
        
        print("\n   Byzantine miners performance:")
        for miner in byzantine_miners:
            print(f"   Miner {miner.miner_id} ({miner.error_rate:.2%} error rate): {miner.tasks_completed} tasks completed, {miner.tokens:.0f} tokens")
        
        print("\n4. Byzantine Fault Tolerance Analysis:")
        print("   a. Task Distribution Impact:")
        avg_tasks_normal = sum(m.tasks_completed for m in self.miners if m.error_rate <= self.byzantine_threshold) / (len(self.miners) - len(byzantine_miners)) if len(self.miners) > len(byzantine_miners) else 0
        avg_tasks_byzantine = sum(m.tasks_completed for m in byzantine_miners) / len(byzantine_miners) if byzantine_miners else 0
        print(f"      - Average tasks per normal miner: {avg_tasks_normal:.1f}")
        print(f"      - Average tasks per Byzantine miner: {avg_tasks_byzantine:.1f}")
        
        print("\n   b. Token Distribution Impact:")
        avg_tokens_normal = sum(m.tokens for m in self.miners if m.error_rate <= self.byzantine_threshold) / (len(self.miners) - len(byzantine_miners)) if len(self.miners) > len(byzantine_miners) else 0
        avg_tokens_byzantine = sum(m.tokens for m in byzantine_miners) / len(byzantine_miners) if byzantine_miners else 0
        print(f"      - Average tokens per normal miner: {avg_tokens_normal:.0f}")
        print(f"      - Average tokens per Byzantine miner: {avg_tokens_byzantine:.0f}")
        
        print("\n5. Detailed Miner Statistics (sorted by tokens):")
        for miner in sorted_miners:
            print(f"\nMiner {miner.miner_id}:")
            print(f"   Score: {miner.score:.2f}")
            print(f"   Renewable Energy: {miner.renewable_energy_proportion:.2%}")
            print(f"   Tasks Completed: {miner.tasks_completed}")
            print(f"   Selection Count: {self.miner_selection_count[miner.miner_id]}")
            print(f"   Penalties: {miner.penalties}")
            print(f"   Error Rate: {miner.error_rate:.2%}")
            print(f"   Total Tokens: {miner.tokens:.0f}")
            print(f"   Status: {'BYZANTINE' if miner.error_rate > self.byzantine_threshold else 'Normal'}")

def run_multiple_simulations(num_runs: int = 10, **kwargs) -> Dict:
    """
    Run multiple simulations and compute statistics with confidence intervals.
    
    Returns:
        Dictionary with mean, std, and confidence intervals for key metrics.
    """
    results = []
    print(f"\nRunning {num_runs} simulations for statistical analysis...")
    
    # Remove 'verbose' from kwargs if present (it's for run_simulation, not __init__)
    kwargs_for_init = {k: v for k, v in kwargs.items() if k != 'verbose'}
    
    for i in range(num_runs):
        sim = BlockchainSimulation(seed=i, **kwargs_for_init)
        result = sim.run_simulation(verbose=False)
        results.append(result)
        print(f"  Run {i+1}/{num_runs} complete: Success rate = {result['success_rate']:.2%}")
    
    # Aggregate statistics
    success_rates = [r['success_rate'] for r in results]
    useful_efficiencies = [r['useful_work_efficiency'] for r in results]
    
    stats = {
        'num_runs': num_runs,
        'success_rate_mean': np.mean(success_rates),
        'success_rate_std': np.std(success_rates),
        'success_rate_ci': 1.96 * np.std(success_rates) / np.sqrt(num_runs),  # 95% CI
        'efficiency_mean': np.mean(useful_efficiencies),
        'efficiency_std': np.std(useful_efficiencies),
        'efficiency_ci': 1.96 * np.std(useful_efficiencies) / np.sqrt(num_runs),
        'raw_results': results
    }
    
    print(f"\n=== Aggregated Results ({num_runs} runs) ===")
    print(f"Success Rate: {stats['success_rate_mean']:.2%} ± {stats['success_rate_ci']:.2%} (95% CI)")
    print(f"Useful Work Efficiency: {stats['efficiency_mean']:.2%} ± {stats['efficiency_ci']:.2%} (95% CI)")
    
    return stats


def sensitivity_analysis_byzantine_error_rate(error_rates: List[float] = None, num_runs: int = 5):
    """
    Analyze system performance across different Byzantine error rates.
    Addresses reviewer comment on Eq. (3): Why 0.30 vs 0.02?
    """
    if error_rates is None:
        error_rates = [0.1, 0.2, 0.3, 0.4, 0.5]  # Range of Byzantine error rates
    
    print("\n=== Sensitivity Analysis: Byzantine Error Rate ===")
    results = []
    
    for rate in error_rates:
        print(f"\nTesting Byzantine error rate: {rate:.1%}")
        stats = run_multiple_simulations(
            num_runs=num_runs,
            num_miners=20,
            num_tasks=1000,
            max_byzantine=3,
            byzantine_error_rate=rate,
            verbose=False
        )
        results.append({
            'error_rate': rate,
            'success_rate': stats['success_rate_mean'],
            'success_rate_ci': stats['success_rate_ci']
        })
    
    print("\n=== Byzantine Error Rate Sensitivity Results ===")
    for r in results:
        print(f"Error Rate {r['error_rate']:.1%}: Success Rate = {r['success_rate']:.2%} ± {r['success_rate_ci']:.2%}")
    
    return results


def sensitivity_analysis_num_verifiers(verifier_counts: List[int] = None, num_runs: int = 5):
    """
    Analyze validation failure probability as function of V (number of verifiers).
    Addresses reviewer comment on Eqs. (11)-(12): What is V and its impact?
    """
    if verifier_counts is None:
        verifier_counts = [1, 3, 5, 7, 9]  # Range of verifier counts
    
    print("\n=== Sensitivity Analysis: Number of Verifiers (V) ===")
    results = []
    
    for V in verifier_counts:
        print(f"\nTesting V = {V} verifiers")
        stats = run_multiple_simulations(
            num_runs=num_runs,
            num_miners=20,
            num_tasks=1000,
            max_byzantine=3,
            num_verifiers=V,
            verbose=False
        )
        results.append({
            'num_verifiers': V,
            'success_rate': stats['success_rate_mean'],
            'success_rate_ci': stats['success_rate_ci'],
            'efficiency': stats['efficiency_mean']
        })
    
    print("\n=== Number of Verifiers Sensitivity Results ===")
    for r in results:
        print(f"V = {r['num_verifiers']}: Success Rate = {r['success_rate']:.2%} ± {r['success_rate_ci']:.2%}, Efficiency = {r['efficiency']:.2%}")
    
    return results


def ablation_study(num_runs: int = 5):
    """
    Ablation study: Test system with/without renewable bonus and fault tolerance.
    Addresses reviewer comment: need ablation studies.
    """
    print("\n=== Ablation Study ===")
    
    # Baseline: Full model
    print("\n1. Full Model (with renewable bonus + fault tolerance)")
    baseline = run_multiple_simulations(
        num_runs=num_runs,
        num_miners=20,
        num_tasks=1000,
        max_byzantine=3,
        renewable_energy_alpha=None,  # Random per miner
        fault_tolerance_enabled=True
    )
    
    # Ablation 1: No renewable bonus
    print("\n2. No Renewable Energy Bonus (α=0 for all)")
    no_green = run_multiple_simulations(
        num_runs=num_runs,
        num_miners=20,
        num_tasks=1000,
        max_byzantine=3,
        renewable_energy_alpha=0.0,  # No bonus
        fault_tolerance_enabled=True
    )
    
    # Ablation 2: No fault tolerance
    print("\n3. No Fault Tolerance (uniform selection)")
    no_ft = run_multiple_simulations(
        num_runs=num_runs,
        num_miners=20,
        num_tasks=1000,
        max_byzantine=3,
        renewable_energy_alpha=None,
        fault_tolerance_enabled=False
    )
    
    print("\n=== Ablation Study Summary ===")
    print(f"Full Model: Success = {baseline['success_rate_mean']:.2%}, Efficiency = {baseline['efficiency_mean']:.2%}")
    print(f"No Green Bonus: Success = {no_green['success_rate_mean']:.2%}, Efficiency = {no_green['efficiency_mean']:.2%}")
    print(f"No Fault Tolerance: Success = {no_ft['success_rate_mean']:.2%}, Efficiency = {no_ft['efficiency_mean']:.2%}")
    
    return {'baseline': baseline, 'no_green': no_green, 'no_ft': no_ft}


if __name__ == "__main__":
    import sys
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "sensitivity-error":
            sensitivity_analysis_byzantine_error_rate()
        elif mode == "sensitivity-verifiers":
            sensitivity_analysis_num_verifiers()
        elif mode == "ablation":
            ablation_study()
        elif mode == "multi-run":
            num_runs = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            run_multiple_simulations(num_runs=num_runs, num_miners=20, num_tasks=1000, max_byzantine=3)
        else:
            print("Unknown mode. Use: sensitivity-error, sensitivity-verifiers, ablation, or multi-run")
    else:
        # Default: Single simulation with thesis specifications
        print("Running single simulation. For analysis modes, use:")
        print("  python main.py sensitivity-error")
        print("  python main.py sensitivity-verifiers")
        print("  python main.py ablation")
        print("  python main.py multi-run [num_runs]")
        print()
        
        simulation = BlockchainSimulation(
            num_miners=20,                    # Thesis Section 3.1: 20 miners
            num_tasks=1000,                   # Number of computational tasks
            max_byzantine=3,                  # Thesis Section 3.1: up to 3 Byzantine miners
            byzantine_error_rate=0.3,         # Thesis Equation 3: 30% error rate for Byzantine
            reward_multiplier=1.0,            # Thesis Equations 5-8: k = 1.0
            renewable_energy_alpha=None,      # α_m ∈ [0, 0.5] - None = random per miner
            num_verifiers=3,                  # V = 3 verifiers per task (Equation 11)
            byzantine_threshold=0.2,          # 20% error rate threshold (Equation 2)
            fault_tolerance_enabled=True      # Enable Byzantine fault tolerance (Equation 4)
        )
        simulation.run_simulation(verbose=True) 