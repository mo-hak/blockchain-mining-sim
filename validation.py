from typing import List, Any
from task import Task
from miner import Miner

class ValidationManager:
    def __init__(self, k: float = 1.0):
        self.k = k  # Reward multiplier

    def validate_solution(self, task: Task, solution: Any) -> bool:
        """Validate a solution through verifier consensus."""
        approvals = 0
        for verifier in task.verifiers:
            if verifier.verify_task(task, solution):
                approvals += 1
        
        task.approvals = approvals
        task.is_validated = (approvals >= len(task.verifiers) / 2)
        return task.is_validated

    def calculate_miner_reward(self, task: Task) -> float:
        """Calculate reward for the task executor."""
        base_reward = self.k * task.cost
        renewable_bonus = task.assigned_miner.renewable_energy_proportion * self.k * task.cost / 2
        return base_reward + renewable_bonus

    def calculate_verifier_reward(self, task: Task) -> float:
        """Calculate reward for each verifier."""
        return self.k * task.cost / 2

    def process_validation(self, task: Task, solution: Any):
        """Process validation results and distribute rewards/penalties."""
        is_valid = self.validate_solution(task, solution)
        
        if is_valid:
            # Reward miner
            reward = self.calculate_miner_reward(task)
            task.assigned_miner.update_score(reward)
            task.assigned_miner.tasks_completed += 1
            task.assigned_miner.receive_tokens(reward)
            
            # Reward verifiers
            verifier_reward = self.calculate_verifier_reward(task)
            for verifier in task.verifiers:
                verifier.update_score(verifier_reward)
                verifier.receive_tokens(verifier_reward)
        else:
            # Apply penalty to miner
            penalty = task.cost
            task.assigned_miner.apply_penalty(penalty)

        return is_valid 