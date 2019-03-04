from __future__ import absolute_import, division, print_function
import random

class Randplay:
    def __init__(self, grid, player):
        self.grid = grid
        self.maxrc = len(grid)-1
        self.piece = player
        self.grid_size = 52
        self.grid_count = 11
        self.game_over = False
        self.winner = None
    
    # to limit search size to only nearby grid
    def get_options(self, grid):  
        #collect all occupied spots
        current_pcs = []
        for r in range(len(grid)):
            for c in range(len(grid)):
                if not grid[r][c] == '.':
                    current_pcs.append((r,c))

        #At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [(self.maxrc//2, self.maxrc//2)]

        #Reasonable moves should be close to where the current pieces are
        #Think about what these calculations are doing
        #Note: min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-1)
        max_r = min(self.maxrc, max(current_pcs, key=lambda x: x[0])[0]+1)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-1)
        max_c = min(self.maxrc, max(current_pcs, key=lambda x: x[1])[1]+1)
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

        print ("options: " , options)
        return options

    def make_move(self):
        return random.choice(self.get_options(self.grid))
   
