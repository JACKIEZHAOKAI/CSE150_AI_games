# Gumoku


Apply Monte Carlo Tree Search algorithm to build a tree,

uct_search() majorly includes four processes: Selection,  Expansion,    Simulation,   Backpropagation

corresponding to MCTS.tree_policy(), MCTS.expansion(), state.rollout(), and MCTS.backpropagation()in mcts.py file

and it will return the optimal move for the player. 

## Usage

```
  python3 gomoku.py
 
```
gomoku.py calls board.py, and then calls either randplay.py OR mcts.py to determine
if you want to play with a stupid random AI OR MCTS smart AI. 

Also, you can enter ENTER in the game to choose random AI plays against with MCTS AI

TO modify the playing mode, you can access the gomoku.py file


## Ref article:
https://zhuanlan.zhihu.com/p/30458774

http://mcts.ai/pubs/mcts-survey-master.pdf

