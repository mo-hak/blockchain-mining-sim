import random
from typing import List, Optional, Any
from task import Task, TaskType

class Miner:
    # Class variable to track Byzantine miners
    _num_byzantine_miners = 0
    _max_byzantine_miners = 3
    _byzantine_error_rate = 0.3  # Error rate for Byzantine miners (per thesis Equation 3: 30%)

    def __init__(self, miner_id: int, force_byzantine: bool = False):
        self.miner_id = miner_id
        self.score = 0.0
        self.renewable_energy_proportion = random.uniform(0.0, 0.5)  # Range between 0 (no renewable) and 0.5
        self.tasks_completed = 0
        self.penalties = 0
        self.tokens = 0.0
        self.current_task: Optional[Task] = None
        
        # Determine if this miner should be Byzantine
        # Now deterministic based on force_byzantine flag
        if force_byzantine:
            self.error_probability = Miner._byzantine_error_rate
            self.is_byzantine = True
            Miner._num_byzantine_miners += 1
        else:
            self.error_probability = 0.02  # Very low error rate for honest miners
            self.is_byzantine = False
        
        self.total_tasks_attempted = 0
        self.total_failures = 0
        self.error_rate = 0.0

    @classmethod
    def reset_byzantine_count(cls):
        """Reset the Byzantine miner counter"""
        cls._num_byzantine_miners = 0

    @classmethod
    def set_byzantine_error_rate(cls, rate: float):
        """Set the error rate for Byzantine miners"""
        cls._byzantine_error_rate = rate

    @classmethod
    def create_miners(cls, num_miners: int, max_byzantine: int, 
                      byzantine_error_rate: float = 0.3,
                      renewable_energy_alpha: float = None) -> List['Miner']:
        """
        Create miners with exactly max_byzantine Byzantine miners.
        Byzantine miners are randomly selected but guaranteed to be created.
        
        Per thesis:
        - Equation 3: Byzantine error probability = 0.3 (30%)
        - α_m ∈ [0, 0.5] is the renewable energy proportion
        
        Args:
            num_miners: Number of miners to create
            max_byzantine: Exact number of Byzantine miners
            byzantine_error_rate: Error probability for Byzantine miners (default 0.3)
            renewable_energy_alpha: If set, all miners use this α value.
                                   If None, random α in [0, 0.5] per miner.
        """
        cls.reset_byzantine_count()
        cls._max_byzantine_miners = max_byzantine
        cls._byzantine_error_rate = byzantine_error_rate
        
        miners = []
        
        # Randomly select which miner IDs will be Byzantine
        byzantine_ids = set()
        if max_byzantine > 0 and num_miners > 0:
            num_byzantine = min(max_byzantine, num_miners)
            byzantine_ids = set(random.sample(range(num_miners), num_byzantine))
        
        # Create miners
        for i in range(num_miners):
            is_byzantine = i in byzantine_ids
            miner = Miner(i, force_byzantine=is_byzantine)
            
            # Set renewable energy proportion (α_m)
            if renewable_energy_alpha is not None:
                # Use fixed α for all miners (for testing/simulation)
                miner.renewable_energy_proportion = renewable_energy_alpha
            # else: keep the random value assigned in __init__
            
            miners.append(miner)
        
        return miners

    def execute_task(self, task: Task) -> Any:
        """Execute the assigned task and return the result."""
        self.current_task = task
        self.total_tasks_attempted += 1
        correct_result = task.execute()
        
        # Introduce potential errors based on error probability
        if random.random() < self.error_probability:
            self.total_failures += 1
            self.error_rate = self.total_failures / self.total_tasks_attempted
            if task.task_type == TaskType.ADDITION:
                return correct_result + random.randint(-10, 10)
            elif task.task_type == TaskType.MULTIPLICATION:
                return correct_result * random.uniform(0.9, 1.1)
            elif task.task_type == TaskType.SORTING:
                # Randomly swap two elements in the sorted list
                result = list(correct_result)
                if len(result) > 1:
                    i, j = random.sample(range(len(result)), 2)
                    result[i], result[j] = result[j], result[i]
                return result
            elif task.task_type == TaskType.SEARCHING:
                return not correct_result
        
        # Update error rate even on success
        self.error_rate = self.total_failures / self.total_tasks_attempted if self.total_tasks_attempted > 0 else 0
        return correct_result

    def verify_task(self, task: Task, solution: Any) -> bool:
        """Verify another miner's solution."""
        return task.verify_solution(solution)

    def update_score(self, reward: float):
        """Update miner's score based on reward."""
        self.score += reward

    def apply_penalty(self, penalty: float):
        """Apply penalty to miner's score."""
        self.score = max(0, self.score - penalty)
        self.penalties += 1

    def receive_tokens(self, amount: float):
        """Receive tokens as reward."""
        self.tokens += amount

    def get_selection_probability(self, total_score: float, fault_tolerance_enabled: bool = True) -> float:
        """
        Calculate probability of being selected for a task.
        
        When fault_tolerance_enabled=True (default):
        Per thesis Equation 4:
        P(m) = 
            - 0.1 × (s_m / Σs_i)  if e_m > 0.2 (Byzantine behavior)
            - 0.5 × (s_m / Σs_i)  if 0.15 < e_m ≤ 0.2 (suspicious behavior)
            - s_m / Σs_i          otherwise (honest behavior)
        
        When fault_tolerance_enabled=False:
        All miners have equal probability (for testing Byzantine impact)
        """
        if not fault_tolerance_enabled:
            # Equal probability for all miners (disables fault tolerance)
            return 1.0
        
        if total_score == 0:
            return 1.0 / 100  # Default probability when no scores exist
        
        base_probability = self.score / total_score
        
        # Thesis Equation 4: Reduce probability based on error rate
        if self.error_rate > 0.2:
            # Byzantine behavior: 90% reduction (multiply by 0.1)
            return base_probability * 0.1
        elif self.error_rate > 0.15:
            # Suspicious behavior: 50% reduction (multiply by 0.5)
            return base_probability * 0.5
        
        # Honest behavior: full probability
        return base_probability

    def __str__(self) -> str:
        status = "BYZANTINE" if self.is_byzantine else "Normal"
        return (f"Miner(id={self.miner_id}, score={self.score:.2f}, "
                f"renewable={self.renewable_energy_proportion:.2f}, "
                f"completed={self.tasks_completed}, penalties={self.penalties}, "
                f"error_rate={self.error_rate:.2%}, status={status})")
