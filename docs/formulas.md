# Mathematical Models and Formulas

## 1. Task Cost Calculation
```
Task Cost = Complexity Factor × Input Size

Where:
- Complexity Factor:
  - Addition: O(n) = 1
  - Multiplication: O(n) = 1
  - Sorting: O(n log n) = input_size
  - Searching: O(n) = 1
```

## 2. Miner Selection Probability
```
Base Probability = Miner Score / Total Score of All Miners

Adjusted Probability based on Byzantine behavior:
- If error_rate > 20%: Probability = Base × 0.1 (90% reduction)
- If error_rate > 15%: Probability = Base × 0.5 (50% reduction)
- Otherwise: Probability = Base
```

## 3. Reward Calculation
```
Base Reward = k × Task Cost
Renewable Bonus = k × Task Cost × Miner's Renewable Energy Proportion × 0.5
Total Reward = Base Reward + Renewable Bonus

Where:
- k is the reward multiplier (default = 1.0)
- Renewable Energy Proportion is between 0 and 1
```

## 4. Verifier Reward
```
Verifier Reward = k × Task Cost × 0.5
```

## 5. Penalty Calculation
```
Penalty = Task Cost
Score After Penalty = max(0, Current Score - Penalty)
```

## 6. Byzantine Detection
```
Error Rate = Total Failures / Total Tasks Attempted
Byzantine Threshold = 0.2 (20%)

A miner is considered Byzantine if:
Error Rate > Byzantine Threshold
```

## 7. Consensus Mechanism
```
Required Approvals = ceil(Number of Verifiers / 2)
Task is validated if:
Number of Approvals ≥ Required Approvals
```

## 8. Performance Metrics

### Success Rate
```
Success Rate = Successful Tasks / Total Tasks Completed
```

### Average Tasks per Miner Type
```
Avg Tasks (Normal) = Total Tasks by Normal Miners / Number of Normal Miners
Avg Tasks (Byzantine) = Total Tasks by Byzantine Miners / Number of Byzantine Miners
```

### Token Distribution Impact
```
Avg Tokens (Normal) = Total Tokens of Normal Miners / Number of Normal Miners
Avg Tokens (Byzantine) = Total Tokens of Byzantine Miners / Number of Byzantine Miners
```

## 9. Error Probability Distribution
```
Byzantine Miners: 30% chance of error per task
Honest Miners: 2% chance of error per task
```

## 10. Task Generation
```
Input Size = random(10, 100)
Task Type = random choice from [Addition, Multiplication, Sorting, Searching]
``` 