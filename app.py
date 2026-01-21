from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import json
import random
from typing import List, Dict, Any
from task import Task, TaskType
from miner import Miner
from distribution import TaskDistributor
from validation import ValidationManager
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)
CORS(app)

class WebBlockchainSimulation:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Get configuration parameters
        num_miners = config['num_miners']
        max_byzantine = config.get('max_byzantine_miners', 3)
        byzantine_error_rate = config.get('byzantine_error_rate', 0.3)
        
        # Random seed for reproducibility
        seed = config.get('seed')
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Get renewable energy alpha (α_m) - if None, random per miner
        # Per thesis: α_m ∈ [0, 0.5]
        renewable_alpha = config.get('renewable_energy_alpha')
        if renewable_alpha == 'random' or renewable_alpha == '' or renewable_alpha is None:
            renewable_alpha = None  # Will use random values per miner
        else:
            renewable_alpha = float(renewable_alpha)
        
        # Create miners with deterministic Byzantine selection
        self.miners = Miner.create_miners(
            num_miners=num_miners,
            max_byzantine=max_byzantine,
            byzantine_error_rate=byzantine_error_rate,
            renewable_energy_alpha=renewable_alpha
        )
        
        # Fault tolerance toggle (per thesis Equation 4)
        # When enabled: score-based selection with Byzantine penalty
        # When disabled: uniform selection (to see raw Byzantine impact)
        fault_tolerance_enabled = config.get('fault_tolerance_enabled', True)
        self.distributor = TaskDistributor(self.miners, fault_tolerance_enabled=fault_tolerance_enabled)
        
        # Create validation manager (per thesis Equations 5-8)
        self.validator = ValidationManager(
            k=config['reward_multiplier'],
            z=config.get('verifier_reward_multiplier', 0.5)
        )
        
        self.total_tasks = config['num_tasks']
        self.completed_tasks = 0
        self.successful_tasks = 0
        self.byzantine_threshold = config.get('byzantine_threshold', 0.2)
        self.input_size_min = config.get('input_size_min', 10)
        self.input_size_max = config.get('input_size_max', 100)
        self.num_verifiers = config.get('num_verifiers', 3)  # V: Number of verifiers per task (thesis Eq.11)
        self.fault_tolerance_enabled = fault_tolerance_enabled
        
        # Count actual Byzantine miners created
        self.actual_byzantine_count = sum(1 for m in self.miners if m.is_byzantine)
        
        # Enhanced metrics tracking for analysis
        self.miner_selection_count = {m.miner_id: 0 for m in self.miners}
        self.task_history = []
        
        # Metrics for visualization
        self.metrics_history = {
            'scores': {},
            'renewable_energy': [],
            'success_rate': [],
            'tokens': {},
            'useful_work_efficiency': []  # Track η over time
        }

    def generate_random_task(self) -> Task:
        """Generate a random task with random input size."""
        task_type = random.choice(list(TaskType))
        input_size = random.randint(self.input_size_min, self.input_size_max)
        return Task(task_type, input_size)

    def run_simulation(self):
        """Run the main simulation loop and return results."""
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

            # Execute task
            solution = miner.execute_task(task)

            # Validate and process rewards
            is_valid = self.validator.process_validation(task, solution)
            if is_valid:
                self.successful_tasks += 1

            self.completed_tasks += 1
            success_rate = self.successful_tasks / self.completed_tasks
            
            # Store task outcome for analysis
            self.task_history.append({
                'task_id': self.completed_tasks,
                'miner_id': miner.miner_id,
                'is_byzantine': miner.is_byzantine,
                'is_valid': is_valid,
                'num_verifiers': len(verifiers)
            })

            # Update metrics every 10 tasks to reduce data size
            if self.completed_tasks % 10 == 0:
                self.update_metrics(success_rate)

            # Yield progress for streaming
            if self.completed_tasks % 50 == 0:
                yield self.get_progress_data()

        # Final metrics update
        self.update_metrics(self.successful_tasks / self.completed_tasks)
        yield self.get_final_results()

    def calculate_useful_work_efficiency(self) -> float:
        """
        Calculate useful work efficiency η = U/(U+W).
        U = useful work (successful tasks), W = wasted work (failed tasks + verification overhead).
        """
        if self.completed_tasks == 0:
            return 0.0
        useful_work = self.successful_tasks
        wasted_work = (self.completed_tasks - self.successful_tasks) + (self.completed_tasks * self.num_verifiers * 0.1)
        return useful_work / (useful_work + wasted_work) if (useful_work + wasted_work) > 0 else 0
    
    def update_metrics(self, success_rate: float):
        """Update metrics for visualization."""
        for miner in self.miners:
            if miner.miner_id not in self.metrics_history['scores']:
                self.metrics_history['scores'][miner.miner_id] = []
            self.metrics_history['scores'][miner.miner_id].append(miner.score)

            if miner.miner_id not in self.metrics_history['tokens']:
                self.metrics_history['tokens'][miner.miner_id] = []
            self.metrics_history['tokens'][miner.miner_id].append(miner.tokens)

        avg_renewable = sum(m.renewable_energy_proportion for m in self.miners) / len(self.miners)
        self.metrics_history['renewable_energy'].append(avg_renewable)
        self.metrics_history['success_rate'].append(success_rate)
        self.metrics_history['useful_work_efficiency'].append(self.calculate_useful_work_efficiency())

    def get_progress_data(self):
        """Get current progress data."""
        return {
            'type': 'progress',
            'completed': self.completed_tasks,
            'total': self.total_tasks,
            'success_rate': self.successful_tasks / self.completed_tasks if self.completed_tasks > 0 else 0
        }

    def get_final_results(self):
        """Get final simulation results with enhanced metrics."""
        # Count miners with high error rates (detected as Byzantine)
        detected_byzantine = [m for m in self.miners if m.error_rate > self.byzantine_threshold]
        honest_miners = [m for m in self.miners if m.error_rate <= self.byzantine_threshold]
        
        miners_data = []
        for miner in sorted(self.miners, key=lambda x: x.tokens, reverse=True):
            miners_data.append({
                'id': miner.miner_id,
                'score': round(miner.score, 2),
                'renewable_energy': round(miner.renewable_energy_proportion, 4),
                'tasks_completed': miner.tasks_completed,
                'selection_count': self.miner_selection_count[miner.miner_id],
                'penalties': miner.penalties,
                'error_rate': round(miner.error_rate, 4),
                'tokens': round(miner.tokens, 2),
                'is_byzantine': miner.is_byzantine,  # Use actual Byzantine status
                'detected_byzantine': miner.error_rate > self.byzantine_threshold
            })

        return {
            'type': 'final',
            'summary': {
                'total_tasks': self.completed_tasks,
                'successful_tasks': self.successful_tasks,
                'success_rate': round(self.successful_tasks / self.completed_tasks, 4) if self.completed_tasks > 0 else 0,
                'useful_work_efficiency': round(self.calculate_useful_work_efficiency(), 4),
                'byzantine_count': self.actual_byzantine_count,
                'detected_byzantine_count': len(detected_byzantine),
                'avg_tasks_honest': round(np.mean([m.tasks_completed for m in honest_miners]), 2) if honest_miners else 0,
                'avg_tasks_byzantine': round(np.mean([m.tasks_completed for m in detected_byzantine]), 2) if detected_byzantine else 0,
                'avg_tokens_honest': round(np.mean([m.tokens for m in honest_miners]), 2) if honest_miners else 0,
                'avg_tokens_byzantine': round(np.mean([m.tokens for m in detected_byzantine]), 2) if detected_byzantine else 0,
                'num_verifiers': self.num_verifiers,
                'fault_tolerance_enabled': self.fault_tolerance_enabled
            },
            'miners': miners_data,
            'metrics': self.metrics_history
        }

@app.route('/')
def index():
    """Serve the main frontend page."""
    return render_template('index.html')

@app.route('/api/simulate', methods=['POST'])
def simulate():
    """Run simulation with provided parameters."""
    try:
        config = request.json
        
        # Validate configuration
        required_params = ['num_miners', 'num_tasks', 'reward_multiplier']
        for param in required_params:
            if param not in config:
                return jsonify({'error': f'Missing required parameter: {param}'}), 400

        simulation = WebBlockchainSimulation(config)
        
        def generate():
            for result in simulation.run_simulation():
                yield f"data: {json.dumps(result)}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulate/sync', methods=['POST'])
def simulate_sync():
    """Run simulation synchronously (no streaming)."""
    try:
        config = request.json
        
        # Validate configuration
        required_params = ['num_miners', 'num_tasks', 'reward_multiplier']
        for param in required_params:
            if param not in config:
                return jsonify({'error': f'Missing required parameter: {param}'}), 400

        simulation = WebBlockchainSimulation(config)
        
        # Run simulation and collect all results
        results = []
        for result in simulation.run_simulation():
            results.append(result)
        
        # Return the final result
        return jsonify(results[-1])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/default', methods=['GET'])
def get_default_config():
    """
    Get default simulation configuration.
    
    Defaults match thesis specifications:
    - 20 miners (Section 3.1)
    - Up to 3 Byzantine miners (Section 3.1)
    - k = 1.0, z = 0.5 (Equations 5-8)
    - α_m ∈ [0, 0.5] (Section 3.2) - renewable energy proportion
    - Byzantine error rate = 0.3 (Equation 3)
    - Byzantine threshold = 0.2 (Section 3.3)
    - V = 3 verifiers per task (Equation 11)
    - n ∈ [10, 100] (Equation 13)
    """
    return jsonify({
        'num_miners': 20,
        'num_tasks': 1000,
        'reward_multiplier': 1.0,            # k = 1.0 (thesis Equations 5-8)
        'verifier_reward_multiplier': 0.5,   # z = 0.5 (thesis Equation 8)
        'renewable_energy_alpha': 'random',  # α_m ∈ [0, 0.5] - 'random' or fixed value
        'byzantine_threshold': 0.2,          # e_m > 0.2 = Byzantine (thesis Equation 2)
        'byzantine_error_rate': 0.3,         # 30% error rate (thesis Equation 3)
        'num_verifiers': 3,                  # V = 3 verifiers per task (thesis Equation 11)
        'input_size_min': 10,                # n ∈ [10, 100] (thesis Equation 13)
        'input_size_max': 100,
        'max_byzantine_miners': 3,           # Up to 3 Byzantine (thesis Section 3.1)
        'fault_tolerance_enabled': True,     # Enable thesis Equation 4 (score-based selection)
        'seed': None                         # Random seed for reproducibility (None = random)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001, threaded=True)
