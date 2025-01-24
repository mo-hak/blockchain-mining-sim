import matplotlib.pyplot as plt
from typing import List, Dict
import numpy as np
from miner import Miner

class Visualizer:
    def __init__(self):
        self.miner_scores_history: Dict[int, List[float]] = {}
        self.renewable_energy_history: List[float] = []
        self.task_success_history: List[float] = []
        self.token_distribution_history: Dict[int, List[float]] = {}

    def update_metrics(self, miners: List[Miner], success_rate: float):
        """Update metrics for visualization."""
        # Update miner scores
        for miner in miners:
            if miner.miner_id not in self.miner_scores_history:
                self.miner_scores_history[miner.miner_id] = []
            self.miner_scores_history[miner.miner_id].append(miner.score)

            if miner.miner_id not in self.token_distribution_history:
                self.token_distribution_history[miner.miner_id] = []
            self.token_distribution_history[miner.miner_id].append(miner.tokens)

        # Update renewable energy usage
        avg_renewable = sum(m.renewable_energy_proportion for m in miners) / len(miners)
        self.renewable_energy_history.append(avg_renewable)

        # Update task success rate
        self.task_success_history.append(success_rate)

    def plot_metrics(self):
        """Generate plots for all metrics."""
        plt.style.use('default')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        # Plot miner scores
        for miner_id, scores in self.miner_scores_history.items():
            ax1.plot(scores, label=f'Miner {miner_id}')
        ax1.set_title('Miner Scores Over Time')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Score')
        ax1.legend()

        # Plot renewable energy usage
        ax2.plot(self.renewable_energy_history)
        ax2.set_title('Average Renewable Energy Usage')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Proportion')

        # Plot task success rate
        ax3.plot(self.task_success_history)
        ax3.set_title('Task Success Rate')
        ax3.set_xlabel('Time')
        ax3.set_ylabel('Success Rate')

        # Plot final token distribution
        miner_ids = list(self.token_distribution_history.keys())
        final_tokens = [history[-1] for history in self.token_distribution_history.values()]
        ax4.bar(miner_ids, final_tokens)
        ax4.set_title('Final Token Distribution')
        ax4.set_xlabel('Miner ID')
        ax4.set_ylabel('Tokens')

        plt.tight_layout()
        plt.savefig('simulation_results.png')
        plt.close()

    def plot_live_update(self):
        """Update plots in real-time during simulation."""
        plt.ion()  # Enable interactive mode
        self.plot_metrics()
        plt.pause(0.1) 