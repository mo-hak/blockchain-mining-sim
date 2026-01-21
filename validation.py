from typing import List, Any
import math
from task import Task
from miner import Miner

class ValidationManager:
    """
    Manages solution validation and reward distribution.
    
    Implements thesis equations:
    - Equation 5: Base Reward R_b(t) = k × C(t)
    - Equation 6: Renewable Bonus R_r(t,m) = k × C(t) × α_m
    - Equation 7: Total Reward R_total = R_b + R_r
    - Equation 8: Verifier Reward R_v(t) = k × C(t) × z
    - Equation 11: Required Approvals = ⌈V/2⌉
    
    Where α_m ∈ [0, 0.5] is the renewable energy proportion for miner m
    """
    
    def __init__(self, k: float = 1.0, z: float = 0.5):
        """
        Initialize validation manager with reward parameters.
        
        Args:
            k: Base reward multiplier (thesis default: 1.0)
            z: Verifier reward coefficient (thesis default: 0.5)
        """
        self.k = k  # Reward multiplier (thesis Equation 5)
        self.z = z  # Verifier reward multiplier (thesis Equation 8)

    def validate_solution(self, task: Task, solution: Any) -> bool:
        """
        Validate a solution through verifier consensus.
        
        Per thesis Equation 11: Required Approvals = ⌈V/2⌉
        Per thesis Equation 12: Valid if Approvals ≥ ⌈V/2⌉
        """
        approvals = 0
        for verifier in task.verifiers:
            if verifier.verify_task(task, solution):
                approvals += 1
        
        task.approvals = approvals
        num_verifiers = len(task.verifiers)
        required_approvals = math.ceil(num_verifiers / 2)  # Thesis Equation 11: ⌈V/2⌉
        task.is_validated = (approvals >= required_approvals)
        return task.is_validated

    def calculate_miner_reward(self, task: Task) -> float:
        """
        Calculate reward for the task executor.
        
        Per thesis Equations 5-7:
        - Base Reward: R_b(t) = k × C(t)
        - Renewable Bonus: R_r(t,m) = k × C(t) × α_m
        - Total: R_total = R_b + R_r
        
        Where:
        - k = reward multiplier (default 1.0)
        - C(t) = task cost (from Equation 1)
        - α_m = miner's renewable energy proportion ∈ [0, 0.5]
        """
        base_reward = self.k * task.cost  # Equation 5: R_b = k × C(t)
        renewable_bonus = self.k * task.cost * task.assigned_miner.renewable_energy_proportion  # Equation 6: R_r = k × C(t) × α_m
        return base_reward + renewable_bonus  # Equation 7: R_total = R_b + R_r

    def calculate_verifier_reward(self, task: Task) -> float:
        """
        Calculate reward for each verifier.
        
        Per thesis Equation 8: R_v(t) = k × C(t) × z
        Where z = 0.5 (default verifier reward coefficient)
        """
        return self.k * task.cost * self.z

    def process_validation(self, task: Task, solution: Any):
        """
        Process validation results and distribute rewards/penalties.
        
        Per thesis Equations 9-10:
        - On success: S_new = S_current + R_total
        - On failure: S_new = max(0, S_current - C(t))
        """
        is_valid = self.validate_solution(task, solution)
        
        if is_valid:
            # Reward miner (Equation 9)
            reward = self.calculate_miner_reward(task)
            task.assigned_miner.update_score(reward)
            task.assigned_miner.tasks_completed += 1
            task.assigned_miner.receive_tokens(reward)
            
            # Reward verifiers (Equation 8)
            verifier_reward = self.calculate_verifier_reward(task)
            for verifier in task.verifiers:
                verifier.update_score(verifier_reward)
                verifier.receive_tokens(verifier_reward)
        else:
            # Apply penalty (Equation 10): S_new = max(0, S_current - C(t))
            penalty = task.cost
            task.assigned_miner.apply_penalty(penalty)

        return is_valid
