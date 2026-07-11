## Course
CMPM 146: Game AI

## Name & Teammates
Brandon Loi

No Teammates

## mcts_vanilla.py
- Implemented Selection
- Implemented Expansion
- Implemented Rollout
- Implemented Backpropagation
- Implemented UCB
- Implemented action selection

## mcts_modified.py
- Modified the rollout policy by introducing heuristics.
- During rollout, the agent first checks for an immediate winning move.
- If no winning move exists, it prefers the center square.
- If the center is unavailable, it prefers corner squares.
- Otherwise it selects a random legal move.