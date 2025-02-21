# Mathematical Models and Formulas

## 1. Task Complexity and Cost
Let \(n\) be the input size where \(n \in [10, 100]\), then for a task \(t\):

\[
C(t) = \begin{cases}
0.5n & \text{if } t \text{ is Addition} \\
1.0n & \text{if } t \text{ is Multiplication} \\
n^2 & \text{if } t \text{ is Sorting} \\
2.0n & \text{if } t \text{ is Searching}
\end{cases}
\]

## 2. Miner Selection Model
For a miner \(m\) with score \(s_m\) and error rate \(e_m\), the selection probability \(P(m)\) is:

\[
P(m) = \begin{cases}
0.1 \cdot \frac{s_m}{\sum_{i=1}^{M} s_i} & \text{if } e_m > 0.2 \\
0.5 \cdot \frac{s_m}{\sum_{i=1}^{M} s_i} & \text{if } 0.15 < e_m \leq 0.2 \\
\frac{s_m}{\sum_{i=1}^{M} s_i} & \text{otherwise}
\end{cases}
\]

where \(M\) is the total number of miners.

## 3. Reward System
For a task \(t\) completed by miner \(m\), with reward multiplier \(k\):

Base Reward: \[R_b(t) = k \cdot C(t)\]
Renewable Bonus: \[R_r(t,m) = k \cdot C(t) \cdot \alpha_m\]
Total Reward: \[R_{total}(t,m) = R_b(t) + R_r(t,m)\]

where \(\alpha_m \in [0, 0.5]\) is the renewable energy proportion of miner \(m\).

## 4. Verification Model
For a verifier \(v\) validating task \(t\):
\[R_v(t) = k \cdot C(t) \cdot z\]
where \(z\) is the verifier reward multiplier (default: 0.5).

## 5. Penalty Model
For an invalid solution:
\[P(t) = C(t)\]
Updated score: \[S_{new} = \max(0, S_{current} - P(t))\]

## 6. Byzantine Detection
For a miner \(m\):
\[E(m) = \frac{F_m}{T_m}\]
where:
- \(E(m)\) is the error rate
- \(F_m\) is the number of failed tasks
- \(T_m\) is the total tasks attempted

Byzantine classification:
\[
B(m) = \begin{cases}
1 & \text{if } E(m) > 0.2 \\
0 & \text{otherwise}
\end{cases}
\]

Error probabilities:
\[
p_{error}(m) = \begin{cases}
0.3 & \text{if } m \text{ is Byzantine} \\
0.02 & \text{otherwise}
\end{cases}
\]

## 7. Consensus Protocol
For a task validation with \(V\) verifiers:
\[
\text{Required Approvals} = \left\lceil\frac{V}{2}\right\rceil
\]

Task validation state:
\[
Valid(t) = \begin{cases}
1 & \text{if } Approvals \geq \left\lceil\frac{V}{2}\right\rceil \\
0 & \text{otherwise}
\end{cases}
\]

## 8. Performance Metrics
Success Rate: \[\eta = \frac{T_{successful}}{T_{total}}\]

Average Tasks per Type:
\[
\overline{T}_{normal} = \frac{\sum_{m \in M_{normal}} T_m}{|M_{normal}|}
\]
\[
\overline{T}_{byzantine} = \frac{\sum_{m \in M_{byzantine}} T_m}{|M_{byzantine}|}
\]

Token Distribution:
\[
\overline{\tau}_{normal} = \frac{\sum_{m \in M_{normal}} \tau_m}{|M_{normal}|}
\]
\[
\overline{\tau}_{byzantine} = \frac{\sum_{m \in M_{byzantine}} \tau_m}{|M_{byzantine}|}
\]

where \(\tau_m\) represents the tokens of miner \(m\).

## 9. Task Generation
```
Input Size = random(10, 100)
Task Type = random choice from [Addition, Multiplication, Sorting, Searching]
```