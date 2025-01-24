import random
from typing import List, Optional, Any
from task import Task, TaskType

class Miner:
    def __init__(self, miner_id: int):
        self.miner_id = miner_id
        self.score = 0.0
        self.renewable_energy_proportion = random.uniform(0.0, 1.0)
        self.tasks_completed = 0
        self.penalties = 0
        self.tokens = 0.0
        self.current_task: Optional[Task] = None
        self.error_probability = random.uniform(0.1, 0.3)  # 10-30% chance of error

    def execute_task(self, task: Task) -> Any:
        """Execute the assigned task and return the result."""
        self.current_task = task
        correct_result = task.execute()
        
        # Introduce potential errors based on error probability
        if random.random() < self.error_probability:
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
        """Calculate probability of being selected for a task."""
        if total_score == 0:
            return 1.0 / 100  # Default probability when no scores exist
        return self.score / total_score

    def __str__(self) -> str:
        return (f"Miner(id={self.miner_id}, score={self.score:.2f}, "
                f"renewable={self.renewable_energy_proportion:.2f}, "
                f"completed={self.tasks_completed}, penalties={self.penalties})") 