# MCTS
# ZHAOKAI XU
# zhx121@ucsd.edu 

from __future__ import absolute_import, division, print_function
from math import sqrt, log
import random,copy
import logging

# state represent the state of the grid in a search MCT tree
# work like node in a tree
# init current state to be the root
######################################################################################
class State:
    def __init__(self, grid, player):
        self.grid = grid
        self.piece = player
        self.parent = None 
        self.reward = 0;        # number of wins
        self.visit = 0;         # number of times visited
        self.action = None      # how to reach this state from prev state, a tuple(r,c)
        self.game_over = False     # terminate only if one won
        self.expanded = False      # try all possible actions      
        self.children = []          # # list of child states    
        
        self.maxActions=0
        self.actionCounter=0
        self.possible_actions = []  # list of tuples
        self.winner =None


# limit search size to only nearby grid
    def get_options(self, grid):  
        #collect all occupied spots
        current_pcs = []
        for r in range(len(grid)):
            for c in range(len(grid)):
                if not grid[r][c] == '.':
                    current_pcs.append((r,c))

        #At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [(10//2, 10//2)]

        #Reasonable moves should be close to where the current pieces are
        #Think about what these calculations are doing
        #Note: min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-1)
        max_r = min(10, max(current_pcs, key=lambda x: x[0])[0]+1)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-1)
        max_c = min(10, max(current_pcs, key=lambda x: x[1])[1]+1)
        #Options of reasonable next step moves
        options = []
        for i in range(min_r, max_r+1):
            for j in range(min_c, max_c+1):
                if not (i, j) in current_pcs:
                    options.append((i,j))
        if len(options) == 0:
            #In the unlikely event that no one wins before board is filled
            #Make white win since black moved first
            self.game_over = True
            self.winner = 'w'
        return options

    def make_move(self):
        return random.choice(self.get_options(self.grid))
    
    def get_continuous_count(self, r, c, dr, dc):
        piece = self.grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < 11 and 0 <= new_c < 11:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result

    def check_win(self, r, c):
        n_count = self.get_continuous_count(r, c, -1, 0)
        s_count = self.get_continuous_count(r, c, 1, 0)
        e_count = self.get_continuous_count(r, c, 0, 1)
        w_count = self.get_continuous_count(r, c, 0, -1)
        se_count = self.get_continuous_count(r, c, 1, 1)
        nw_count = self.get_continuous_count(r, c, -1, -1)
        ne_count = self.get_continuous_count(r, c, -1, 1)
        sw_count = self.get_continuous_count(r, c, 1, -1)
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
            self.winner = self.grid[r][c]
            self.game_over = True

    def set_piece(self, r, c):
        if self.grid[r][c] == '.':
            self.grid[r][c] = self.piece
            if self.piece == 'b':
                self.piece = 'w'
            else:
                self.piece = 'b'
            return True
        return False

# Roll out for default policy
#'b' player wins, update 'w' player reward value along the path: {'b':0, 'w':1}
#'w' player store, update 'b' player reward value along the path: {'b':1, 'w':0}
    def rollout(self,state):
        # take a random action each time until game over
        while not self.game_over:
            r,c = self.make_move()
            self.set_piece(r,c)
            self.check_win(r,c)        

        return self.winner

# MCTS is used to process the MCTS 
# like a tree class, containing the root state
######################################################################################
class MCTS:
  
    def __init__(self, grid, player):
        self.grid = grid
        self.piece = player
        self.root = State( grid, player)


# core fucniton, wrapped up selection, expansion, simulation, backpropagation
# return the best move , a tuple (r,c)
    def uct_search(self):
        # number of iteration limited within 15 seconds 
        for i in range(100): 
            state = self.tree_policy(self.root)

            ### Super crucial to make a deep copy of the child state.  
            # And call copyState .rollout() instead of state.rollout()       Debug 5+hrs >_<
            # so that will not modify inner properties of child states
            # only want rollout()/default policy() to return the winner in curr state simulation
            copyState = copy.deepcopy(state)
            winner = copyState.rollout(copyState)

            self.backpropagation(state, winner)
         
        # calc the best child action under curr root state
        maxChild=None
        val = 0
        for child in self.root.children:
            if val < ( child.reward / child.visit ):
                maxChild =  child 
                val = ( child.reward / child.visit )

        print ("best action", maxChild.action)
        print ("best child.reward ",maxChild.reward ,"best child.visit", maxChild.visit)
        return maxChild.action

# Tree policy: expand OR find the best child 
    def tree_policy(self, state): 

        while state.game_over is False:
            if state.expanded is False:    
                return self.expansion(state) 
            else:      
                state = self.best_child(state)

        return state
        
# expand to create a new child and connect to the state
    def expansion(self, state):
        # get all reasonable moves (r,c) of a state 
        if len(state.possible_actions) is 0:
            state.possible_actions = copy.deepcopy( state.get_options(state.grid) )    
            state.maxActions = len( state.possible_actions)
 
        #create a new child state
        newAction =  state.possible_actions.pop()
        state.actionCounter += 1
 
        newPiece = ''
        if (state.piece == 'b'):
            newPiece =  'w'
        else:
            newPiece =  'b'
        newGrid = copy.deepcopy(state.grid)
        newGrid[newAction[0]][newAction[1]]=newPiece 
        newChild =  State( newGrid, newPiece)
        newChild.action = newAction

        #connect to parent state
        newChild.parent = state
        state.children.append(newChild)
    
        #add all possible actions into children states
        if state.actionCounter == state.maxActions:
            state.expanded = True

        return newChild

# compute the formular to find max child of the given state
    def best_child(self, state):
        max_ucb=0
        ucb_child=None
        for child in state.children:
            ucb = ( child.reward / child.visit ) + sqrt( (log(state.visit) / child.visit) )
            if max_ucb < ucb:
                max_ucb = ucb
                ucb_child = child
        return ucb_child


    def backpropagation(self, state, result):
        while state is not None:
            state.visit += 1
            if state.piece != result:
                state.reward += 1
            state = state.parent
