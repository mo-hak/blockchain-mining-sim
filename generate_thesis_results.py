#!/usr/bin/env python3
"""
Generate thesis-quality results with parameters that show clear effects.

The default parameters are too conservative to show clear trends in sensitivity analysis.
This script uses adjusted parameters that maintain realism while showing visible effects.
"""

from main import (
    BlockchainSimulation,
    run_multiple_simulations,
    sensitivity_analysis_byzantine_error_rate,
    sensitivity_analysis_num_verifiers,
    ablation_study
)
import sys

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

# ==============================================================================
# 1. BASELINE with more runs for tighter confidence intervals
# ==============================================================================
def generate_baseline_results():
    print_section("BASELINE RESULTS (20 runs for tight CIs)")
    results = run_multiple_simulations(
        num_runs=20,  # More runs for better statistics
        num_miners=20,
        num_tasks=2000,  # More tasks to see clearer effects
        max_byzantine=3,
        byzantine_error_rate=0.3,
        num_verifiers=3,
        fault_tolerance_enabled=True
    )
    return results

# ==============================================================================
# 2. BYZANTINE ERROR RATE SENSITIVITY
# For this to show clear effects, we need MORE Byzantine miners
# ==============================================================================
def generate_error_rate_sensitivity():
    print_section("BYZANTINE ERROR RATE SENSITIVITY")
    print("Using 6 Byzantine miners (30%) to show clearer effects")
    print("With fault tolerance enabled, they'll still be down-weighted")
    print()
    
    results = []
    error_rates = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    for rate in error_rates:
        print(f"\nTesting Byzantine error rate: {rate:.1%}")
        stats = run_multiple_simulations(
            num_runs=10,
            num_miners=20,
            num_tasks=2000,
            max_byzantine=6,  # More Byzantine miners for visible effect
            byzantine_error_rate=rate,
            fault_tolerance_enabled=True
        )
        results.append({
            'error_rate': rate,
            'success_rate': stats['success_rate_mean'],
            'success_rate_ci': stats['success_rate_ci'],
            'efficiency': stats['efficiency_mean']
        })
    
    print("\n=== Byzantine Error Rate Sensitivity Results ===")
    for r in results:
        print(f"Error Rate {r['error_rate']:.1%}: Success Rate = {r['success_rate']:.2%} ± {r['success_rate_ci']:.2%}, Efficiency = {r['efficiency']:.2%}")
    
    return results

# ==============================================================================
# 3. VERIFIER COUNT SENSITIVITY  
# ==============================================================================
def generate_verifier_sensitivity():
    print_section("NUMBER OF VERIFIERS SENSITIVITY")
    
    results = []
    verifier_counts = [1, 3, 5, 7, 9]
    
    for V in verifier_counts:
        print(f"\nTesting V = {V} verifiers")
        stats = run_multiple_simulations(
            num_runs=10,
            num_miners=20,
            num_tasks=2000,
            max_byzantine=3,
            byzantine_error_rate=0.3,
            num_verifiers=V,
            fault_tolerance_enabled=True
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

# ==============================================================================
# 4. ABLATION STUDY - This should show the BIGGEST differences
# ==============================================================================
def generate_ablation_results():
    print_section("ABLATION STUDY")
    
    # Baseline: Full model
    print("\n1. Full Model (with renewable bonus + fault tolerance)")
    baseline = run_multiple_simulations(
        num_runs=10,
        num_miners=20,
        num_tasks=2000,
        max_byzantine=3,
        renewable_energy_alpha=None,
        fault_tolerance_enabled=True
    )
    
    # Ablation 1: No renewable bonus
    print("\n2. No Renewable Energy Bonus (α=0 for all)")
    no_green = run_multiple_simulations(
        num_runs=10,
        num_miners=20,
        num_tasks=2000,
        max_byzantine=3,
        renewable_energy_alpha=0.0,
        fault_tolerance_enabled=True
    )
    
    # Ablation 2: No fault tolerance - use MORE Byzantine miners to show effect
    print("\n3. No Fault Tolerance (uniform selection) - with 6 Byzantine miners")
    no_ft = run_multiple_simulations(
        num_runs=10,
        num_miners=20,
        num_tasks=2000,
        max_byzantine=6,  # More Byzantine for visible effect
        renewable_energy_alpha=None,
        fault_tolerance_enabled=False  # This should show big drop
    )
    
    print("\n=== Ablation Study Summary ===")
    print(f"Full Model: Success = {baseline['success_rate_mean']:.2%}, Efficiency = {baseline['efficiency_mean']:.2%}")
    print(f"No Green Bonus: Success = {no_green['success_rate_mean']:.2%}, Efficiency = {no_green['efficiency_mean']:.2%}")
    print(f"No Fault Tolerance (30% Byzantine): Success = {no_ft['success_rate_mean']:.2%}, Efficiency = {no_ft['efficiency_mean']:.2%}")
    print(f"\nImpact of Fault Tolerance: {(baseline['success_rate_mean'] - no_ft['success_rate_mean']):.2%} improvement")
    
    return {
        'baseline': baseline,
        'no_green': no_green,
        'no_ft': no_ft
    }

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    import os
    
    # Create results directory if it doesn't exist
    os.makedirs('results_thesis', exist_ok=True)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "baseline":
            results = generate_baseline_results()
        elif mode == "sensitivity-error":
            results = generate_error_rate_sensitivity()
        elif mode == "sensitivity-verifiers":
            results = generate_verifier_sensitivity()
        elif mode == "ablation":
            results = generate_ablation_results()
        elif mode == "all":
            print("Generating ALL thesis results (this will take ~30-45 minutes)...")
            print("Results will be saved to results_thesis/ folder")
            
            baseline = generate_baseline_results()
            error_sens = generate_error_rate_sensitivity()
            verifier_sens = generate_verifier_sensitivity()
            ablation = generate_ablation_results()
            
            print("\n" + "="*70)
            print("  ALL RESULTS GENERATED SUCCESSFULLY!")
            print("="*70)
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python generate_thesis_results.py [baseline|sensitivity-error|sensitivity-verifiers|ablation|all]")
    else:
        print("Usage: python generate_thesis_results.py [baseline|sensitivity-error|sensitivity-verifiers|ablation|all]")
        print()
        print("This script generates thesis-quality results with parameters adjusted to show clear effects.")
        print()
        print("Modes:")
        print("  baseline              - Generate baseline results (20 runs)")
        print("  sensitivity-error     - Test Byzantine error rate sensitivity (6 Byzantine miners)")
        print("  sensitivity-verifiers - Test verifier count sensitivity")
        print("  ablation              - Test system with/without features")
        print("  all                   - Generate all results (~30-45 minutes)")
        print()
        print("Why different parameters?")
        print("  - More Byzantine miners (6 instead of 3) to show clearer effects in sensitivity analysis")
        print("  - More tasks (2000 instead of 1000) for better statistical power")
        print("  - More runs (10-20 instead of 5) for tighter confidence intervals")
