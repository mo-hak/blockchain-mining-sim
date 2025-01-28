import random
from typing import List
import time
from task import Task, TaskType
from miner import Miner
from distribution import TaskDistributor
from validation import ValidationManager
from visualization import Visualizer

class BlockchainSimulation:
    def __init__(self, num_miners: int = 20, num_tasks: int = 1000):
        # Reset Byzantine counter before creating new miners
        Miner.reset_byzantine_count()
        self.miners = [Miner(i) for i in range(num_miners)]
        self.distributor = TaskDistributor(self.miners)
        self.validator = ValidationManager(k=1.0)
        self.visualizer = Visualizer()
        self.total_tasks = num_tasks
        self.completed_tasks = 0
        self.successful_tasks = 0
        self.byzantine_threshold = 0.2

    def generate_random_task(self) -> Task:
        """Generate a random task with random input size."""
        task_type = random.choice(list(TaskType))
        input_size = random.randint(10, 100)
        return Task(task_type, input_size)

    def run_simulation(self):
        """Run the main simulation loop."""
        print("Starting blockchain mining simulation...")
        print(f"Number of miners: {len(self.miners)}")
        print(f"Number of tasks: {self.total_tasks}")
        print("Byzantine fault tolerance enabled (threshold: 20% error rate)")
        print("\nInitial miner states:")
        for miner in self.miners:
            print(miner)
        print("\nStarting tasks...")

        # Generate initial task queue
        for _ in range(self.total_tasks):
            self.distributor.add_task(self.generate_random_task())

        while self.completed_tasks < self.total_tasks:
            # Distribute task
            distribution_result = self.distributor.distribute_task()
            if not distribution_result:
                break

            task, miner, verifiers = distribution_result
            
            # Only print every 100th task to avoid console spam
            if (self.completed_tasks + 1) % 100 == 0:
                print(f"\nTask {self.completed_tasks + 1}/{self.total_tasks}")
                print(f"Assigned to: {miner}")
                print(f"Verifiers: {len(verifiers)}")

            # Execute task
            solution = miner.execute_task(task)

            # Validate and process rewards
            is_valid = self.validator.process_validation(task, solution)
            if is_valid:
                self.successful_tasks += 1
                if (self.completed_tasks + 1) % 100 == 0:
                    print("Task completed successfully!")
            else:
                if (self.completed_tasks + 1) % 100 == 0:
                    print("Task failed validation.")
                    if miner.error_rate > self.byzantine_threshold:
                        print(f"WARNING: Miner {miner.miner_id} shows Byzantine behavior! "
                              f"Error rate: {miner.error_rate:.2%}")

            self.completed_tasks += 1
            success_rate = self.successful_tasks / self.completed_tasks
            if (self.completed_tasks) % 100 == 0:
                print(f"Current success rate: {success_rate:.2%}")

            # Update visualization
            self.visualizer.update_metrics(self.miners, success_rate)
            if self.completed_tasks % 100 == 0:  # Update plot every 100 tasks
                self.visualizer.plot_metrics()

        # Final visualization
        self.visualizer.plot_metrics()
        self.print_final_stats()

    def print_final_stats(self):
        """Print final simulation statistics with detailed Byzantine analysis."""
        print("\n=== Final Statistics ===")
        print("\n1. Overall Performance:")
        print(f"   Total tasks completed: {self.completed_tasks}")
        print(f"   Successful tasks: {self.successful_tasks}")
        print(f"   Overall success rate: {(self.successful_tasks / self.completed_tasks):.2%}")
        
        # Byzantine Analysis
        byzantine_miners = [m for m in self.miners if m.error_rate > self.byzantine_threshold]
        print(f"   {len(byzantine_miners)} miners showed Byzantine behavior (error rate > {self.byzantine_threshold:.0%})")
        
        print("\n2. Byzantine Miners (error rate > 20%):")
        # Sort byzantine miners by error rate
        byzantine_miners.sort(key=lambda x: x.error_rate, reverse=True)
        for miner in byzantine_miners:
            print(f"   Miner {miner.miner_id}: {miner.error_rate:.2%} error rate")
        
        print("\n3. Impact of Byzantine Behavior on Rewards:")
        # Sort all miners by tokens for top performers
        sorted_miners = sorted(self.miners, key=lambda x: x.tokens, reverse=True)
        top_performers = sorted_miners[:4]
        print("   Top performers:")
        for miner in top_performers:
            print(f"   Miner {miner.miner_id}: {miner.tasks_completed} tasks, {miner.error_rate:.2%} error rate, {miner.tokens:.0f} tokens")
        
        print("\n   Byzantine miners performance:")
        for miner in byzantine_miners:
            print(f"   Miner {miner.miner_id} ({miner.error_rate:.2%} error rate): {miner.tasks_completed} tasks completed, {miner.tokens:.0f} tokens")
        
        print("\n4. Byzantine Fault Tolerance Analysis:")
        print("   a. Task Distribution Impact:")
        avg_tasks_normal = sum(m.tasks_completed for m in self.miners if m.error_rate <= self.byzantine_threshold) / (len(self.miners) - len(byzantine_miners))
        avg_tasks_byzantine = sum(m.tasks_completed for m in byzantine_miners) / len(byzantine_miners) if byzantine_miners else 0
        print(f"      - Average tasks per normal miner: {avg_tasks_normal:.1f}")
        print(f"      - Average tasks per Byzantine miner: {avg_tasks_byzantine:.1f}")
        
        print("\n   b. Token Distribution Impact:")
        avg_tokens_normal = sum(m.tokens for m in self.miners if m.error_rate <= self.byzantine_threshold) / (len(self.miners) - len(byzantine_miners))
        avg_tokens_byzantine = sum(m.tokens for m in byzantine_miners) / len(byzantine_miners) if byzantine_miners else 0
        print(f"      - Average tokens per normal miner: {avg_tokens_normal:.0f}")
        print(f"      - Average tokens per Byzantine miner: {avg_tokens_byzantine:.0f}")
        
        print("\n5. Detailed Miner Statistics (sorted by tokens):")
        for miner in sorted_miners:
            print(f"\nMiner {miner.miner_id}:")
            print(f"   Score: {miner.score:.2f}")
            print(f"   Renewable Energy: {miner.renewable_energy_proportion:.2%}")
            print(f"   Tasks Completed: {miner.tasks_completed}")
            print(f"   Penalties: {miner.penalties}")
            print(f"   Error Rate: {miner.error_rate:.2%}")
            print(f"   Total Tokens: {miner.tokens:.0f}")
            print(f"   Status: {'BYZANTINE' if miner.error_rate > self.byzantine_threshold else 'Normal'}")

if __name__ == "__main__":
    simulation = BlockchainSimulation(num_miners=20, num_tasks=1000)
    simulation.run_simulation() 