import random
from typing import List
import time
from task import Task, TaskType
from miner import Miner
from distribution import TaskDistributor
from validation import ValidationManager
from visualization import Visualizer

class BlockchainSimulation:
    def __init__(self, num_miners: int = 5, num_tasks: int = 100):
        self.miners = [Miner(i) for i in range(num_miners)]
        self.distributor = TaskDistributor(self.miners)
        self.validator = ValidationManager(k=1.0)
        self.visualizer = Visualizer()
        self.total_tasks = num_tasks
        self.completed_tasks = 0
        self.successful_tasks = 0

    def generate_random_task(self) -> Task:
        """Generate a random task with random input size."""
        task_type = random.choice(list(TaskType))
        input_size = random.randint(10, 100)
        return Task(task_type, input_size)

    def run_simulation(self):
        """Run the main simulation loop."""
        print("Starting blockchain mining simulation...")

        # Generate initial task queue
        for _ in range(self.total_tasks):
            self.distributor.add_task(self.generate_random_task())

        while self.completed_tasks < self.total_tasks:
            # Distribute task
            distribution_result = self.distributor.distribute_task()
            if not distribution_result:
                break

            task, miner, verifiers = distribution_result
            print(f"\nTask {self.completed_tasks + 1}/{self.total_tasks}")
            print(f"Assigned to: {miner}")
            print(f"Verifiers: {len(verifiers)}")

            # Execute task
            solution = miner.execute_task(task)

            # Validate and process rewards
            is_valid = self.validator.process_validation(task, solution)
            if is_valid:
                self.successful_tasks += 1
                print("Task completed successfully!")
            else:
                print("Task failed validation.")

            self.completed_tasks += 1
            success_rate = self.successful_tasks / self.completed_tasks
            print(f"Current success rate: {success_rate:.2%}")

            # Update visualization
            self.visualizer.update_metrics(self.miners, success_rate)
            if self.completed_tasks % 10 == 0:  # Update plot every 10 tasks
                self.visualizer.plot_metrics()

        # Final visualization
        self.visualizer.plot_metrics()
        self.print_final_stats()

    def print_final_stats(self):
        """Print final simulation statistics."""
        print("\n=== Final Statistics ===")
        print(f"Total tasks completed: {self.completed_tasks}")
        print(f"Successful tasks: {self.successful_tasks}")
        print(f"Overall success rate: {(self.successful_tasks / self.completed_tasks):.2%}")
        print("\nMiner Statistics:")
        for miner in self.miners:
            print(f"\n{miner}")
            print(f"Total tokens: {miner.tokens:.2f}")
            print(f"Tasks completed: {miner.tasks_completed}")
            print(f"Penalties received: {miner.penalties}")

if __name__ == "__main__":
    # Run simulation with 5 miners and 100 tasks
    simulation = BlockchainSimulation(num_miners=5, num_tasks=100)
    simulation.run_simulation() 