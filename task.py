from enum import Enum
import random
import time
from typing import List, Any, Optional

class TaskType(Enum):
    ADDITION = "addition"
    MULTIPLICATION = "multiplication"
    SORTING = "sorting"
    SEARCHING = "searching"

class Task:
    def __init__(self, task_type: TaskType, input_size: int):
        self.task_type = task_type
        self.input_size = input_size
        self.input_data = self._generate_input()
        self.assigned_miner = None
        self.cost = self._calculate_cost()
        self.result = None
        self.is_validated = False
        self.verifiers = []
        self.approvals = 0

    def _generate_input(self) -> List[int]:
        """Generate random input data based on task type and size."""
        return [random.randint(1, 100) for _ in range(self.input_size)]

    def _calculate_cost(self) -> float:
        """Calculate task cost based on time complexity and input size."""
        complexity_map = {
            TaskType.ADDITION: 1,  # O(n)
            TaskType.MULTIPLICATION: 1,  # O(n)
            TaskType.SORTING: self.input_size,  # O(n log n)
            TaskType.SEARCHING: 1,  # O(n)
        }
        return complexity_map[self.task_type] * self.input_size

    def execute(self) -> Any:
        """Execute the task based on its type."""
        if self.task_type == TaskType.ADDITION:
            return sum(self.input_data)
        elif self.task_type == TaskType.MULTIPLICATION:
            result = 1
            for num in self.input_data:
                result *= num
            return result
        elif self.task_type == TaskType.SORTING:
            return sorted(self.input_data)
        elif self.task_type == TaskType.SEARCHING:
            target = random.choice(self.input_data)
            return target in self.input_data

    def verify_solution(self, solution: Any) -> bool:
        """Verify if the provided solution is correct."""
        correct_solution = self.execute()
        return solution == correct_solution

    def __str__(self) -> str:
        return f"Task(type={self.task_type.value}, size={self.input_size}, cost={self.cost})" 