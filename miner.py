import random
from typing import List, Optional, Any
from task import Task, TaskType

class Miner:
    # Class variable to track Byzantine miners
    _num_byzantine_miners = 0
    _max_byzantine_miners = 3  # We'll randomly choose 1-3 miners to be Byzantine

    def __init__(self, miner_id: int):
        self.miner_id = miner_id
        self.score = 0.0
        self.renewable_energy_proportion = random.uniform(0.0, 0.5)  # Range between 0 (no renewable) and 0.5
        self.tasks_completed = 0
        self.penalties = 0
        self.tokens = 0.0
        self.current_task: Optional[Task] = None
        
        # Determine if this miner should be Byzantine
        if Miner._num_byzantine_miners < Miner._max_byzantine_miners and random.random() < 0.15:  # 15% chance for eligible miners
            self.error_probability = 0.3  # Higher error rate for Byzantine miners
            Miner._num_byzantine_miners += 1
        else:
            self.error_probability = 0.02  # Very low error rate for honest miners
        
        self.total_tasks_attempted = 0
        self.total_failures = 0
        self.error_rate = 0.0
        self.is_byzantine = self.error_probability > 0.1

    @classmethod
    def reset_byzantine_count(cls):
        """Reset the Byzantine miner counter"""
        cls._num_byzantine_miners = 0

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

    def get_selection_probability(self, total_score: float) -> float:
        """Calculate probability of being selected for a task with Byzantine fault tolerance."""
        if total_score == 0:
            return 1.0 / 100  # Default probability when no scores exist
        
        # Reduce probability based on error rate (Byzantine fault tolerance)
        # If error rate > 20%, significantly reduce chances of selection
        if self.error_rate > 0.2:
            return (self.score / total_score) * 0.1  # 90% reduction in probability
        elif self.error_rate > 0.15:
            return (self.score / total_score) * 0.5  # 50% reduction in probability
        
        return self.score / total_score

    def __str__(self) -> str:
        status = "BYZANTINE" if self.is_byzantine else "Normal"
        return (f"Miner(id={self.miner_id}, score={self.score:.2f}, "
                f"renewable={self.renewable_energy_proportion:.2f}, "
                f"completed={self.tasks_completed}, penalties={self.penalties}, "
                f"error_rate={self.error_rate:.2%}, status={status})") 