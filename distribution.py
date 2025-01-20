import random
from typing import List, Optional
from task import Task
from miner import Miner

class TaskDistributor:
    def __init__(self, miners: List[Miner]):
        self.miners = miners
        self.task_queue: List[Task] = []

    def add_task(self, task: Task):
        """Add a new task to the queue."""
        self.task_queue.append(task)

    def get_total_score(self) -> float:
        """Calculate total score of all miners."""
        return sum(miner.score for miner in self.miners)

    def select_miner(self) -> Miner:
        """Select a miner based on their score probability."""
        total_score = self.get_total_score()
        probabilities = [miner.get_selection_probability(total_score) for miner in self.miners]
        return random.choices(self.miners, weights=probabilities, k=1)[0]

    def select_verifiers(self, task: Task, excluded_miner: Miner, num_verifiers: int = 3) -> List[Miner]:
        """Select random verifiers excluding the task executor."""
        available_verifiers = [m for m in self.miners if m != excluded_miner]
        return random.sample(available_verifiers, min(num_verifiers, len(available_verifiers)))

    def distribute_task(self) -> Optional[tuple[Task, Miner, List[Miner]]]:
        """Distribute the next task in queue to a miner and select verifiers."""
        if not self.task_queue:
            return None

        task = self.task_queue.pop(0)
        selected_miner = self.select_miner()
        verifiers = self.select_verifiers(task, selected_miner)
        
        task.assigned_miner = selected_miner
        task.verifiers = verifiers
        
        return task, selected_miner, verifiers 