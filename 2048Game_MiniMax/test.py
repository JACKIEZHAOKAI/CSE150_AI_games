# ZHAOKAI XU
from __future__ import absolute_import, division, print_function
import copy
import random
import heapq
MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}
PLAYERS = {'chance': 0, 'computer': 1}
class State:	
	"""game state, node of the GameTree"""
	def __init__(self, matrix, player, score):
		self.matrix = matrix
		self.player =player
		self.score = score
		self.children =  []
		self.isTerminal = False
		self.move =  -1		
	def setIsTerminal(self, terminal):
		self.isTerminal =  terminal
	def setMovement(self, move):
		self.move = move
	def getMatrix(self):
		return self.matrix		
	def getPlayer(self):
	    return self.player
	def getScore(self):
	    return self.score
	def getIsTerminal(self):
		return self.isTerminal
	def getMovement(self):
		return self.move 
	def print_max_tile(self):
		max_tile = 0
		for i in range(len(self.matrix)):
			for j in range (len(self.matrix)):
				if max_tile < self.matrix[i][j]:
						max_tile = self.matrix[i][j]
		print ("curr max tile: ", max_tile)
	def payoff(self):
		return self.score
		
class Gametree:
	"""main class for the AI"""
	def __init__(self, root_state, depth_of_tree, current_score): 
		'''construct a game tree from any state of the game'''
		self.stateRoot = State(root_state, PLAYERS['chance'], current_score)
		self.depth_of_tree =depth_of_tree
		self.stateAndChildren =  {} 	# key: state value:a list of children
	def subTreeGenerator(self,state,isTerminal):	
		childrenStates_list= []
		if state.getPlayer() == PLAYERS['chance']: 
			for i in range(4):
				#construct a simulator
				simulator = Simulator( copy.deepcopy(state.getMatrix()), state.getScore() )
				#move the state
				simulator.move(i)
				if( simulator.getMatrix() != copy.deepcopy(state.getMatrix()) ):
					# create a child state obj from the simulator   	
					child_state = State(simulator.getMatrix(), PLAYERS['computer'], simulator.getScore())
					child_state.setMovement(i)
					# link the child obj to its parent state
					if isTerminal:
						child_state.setIsTerminal(True)
					childrenStates_list.append(child_state) 
		elif state.getPlayer() == PLAYERS['computer']:
                    
			currMatrix = copy.deepcopy(state.getMatrix())
			for i in range(0, len(currMatrix)):
				for j in range(0, len(currMatrix)):
					if currMatrix[i][j] == 0: # only create a State object for the chance player if there is an empty space to place a 2-tile
						newMatrix = copy.deepcopy(state.getMatrix())
						newMatrix[i][j] = 2
						
						stateChild = State(newMatrix, PLAYERS['chance'], state.getScore())
						childrenStates_list.append(stateChild)
		self.stateAndChildren[state] = childrenStates_list #parent and its children are connected
# Construct a depth-3 game tree (4 points)
# Explicitly construct a game tree from any state of the game (like the tree you see in the slides). 
# The tree depth is required to be at least 3, that is, it can represent all the game states of a 
# player-computer-player sequence (the player makes a move, the computer place a tile, and 
# then the player makes another move).
	def growTree(self, state, depth):
		"""Grow the tree starting from root"""
		# call subTreeGenerator(self,state,isTerminal) to construct the tree
		
		"""Grow the full tree from root"""
		if( depth == 3):
			self.subTreeGenerator(self.stateRoot, False) #layer 1
			for i in range(0, len(self.stateAndChildren[self.stateRoot])): #layer 2
			    self.subTreeGenerator(self.stateAndChildren[self.stateRoot][i], False)
			for i in range(0, len(self.stateAndChildren[self.stateRoot])):  #layer 3
			    for j in range(0, len(self.stateAndChildren[ self.stateAndChildren[self.stateRoot][i] ]) ):
					self.subTreeGenerator( self.stateAndChildren[ self.stateAndChildren[self.stateRoot][i] ][j], True )
		elif( depth == 1):
			self.subTreeGenerator(self.stateRoot, True) #layer 1
# Compute expectimax values and optimal moves (6 points)
# Compute the expectimax values of all the nodes in the game tree, 
# and return the optimal move for the player.
	def minimax(self, state):
		"""Compute minimax values"""
		if state.getIsTerminal():
		    return state.payoff()
		elif state.getPlayer() == PLAYERS['chance']:
		    value = float('-inf')
		    for i in range(0, len( self.stateAndChildren[state])):
		       value = max( value, self.minimax( self.stateAndChildren[state][i] ) )
		    return value
		elif state.getPlayer() == PLAYERS['computer']:
			value = 0
			for i in range(0, len(self.stateAndChildren[state])):
				value = value + self.minimax(self.stateAndChildren[state][i]) * (1.0)/len(self.stateAndChildren[state])
			return value
		else:
			return 'Error'
			
# funciton to be called by 2048.py
	def compute_decision(self):
		'''function to return best decision to game'''
		self.growTree(self.stateRoot,3) 
		self.stateRoot.print_max_tile()
	
		# fird the max Minimax children
		max_minimax = 0
		max_minimax_index = 0
		for i in range( len(self.stateAndChildren[self.stateRoot])): 
			# print ("minimax ", self.stateAndChildren[self.stateRoot][i])
			if self.minimax( self.stateAndChildren[self.stateRoot][i] ) > max_minimax:
				max_minimax = self.minimax( self.stateAndChildren[self.stateRoot][i] )
				max_minimax_index = i
		max_minimax_state = self.stateAndChildren[self.stateRoot][max_minimax_index]
		#Replace the following decision with what you compute
		optimal_move = max_minimax_state.getMovement()
		
		print ("next move:", MOVES[optimal_move])
		print ("expectimax", self.minimax(self.stateRoot) )
		
		return optimal_move

#	Game simulator (3 points)
# You can mostly copy/paste the game engine code to create a game simulator. 
# It will be used to return the game state (and evaluate its score) after the player 
# makes any move from any reasonable game state.
class Simulator:
	"""Simulation of the game"""
	def __init__(self, matrix, score):
		self.matrix = matrix
		self.score = score
	def getMatrix(self):
            return self.matrix
	
	def getScore(self):
            return self.score
	def move(self, direction):
		for i in range(0, direction):
			self.rotateMatrixClockwise()
		if self.canMove():
			self.moveTiles()
			self.mergeTiles()
		for j in range(0, (4 - direction) % 4):
			self.rotateMatrixClockwise()
	# placeRandomTile() removed
	
	def moveTiles(self):
		# store the matrix before moving 
		tm = self.matrix
		size_board = len(self.matrix)
		for i in range(0, size_board):      
			for j in range(0, size_board - 1): 
				while tm[i][j] == 0 and sum(tm[i][j:]) > 0:
					for k in range(j, size_board - 1): 
						tm[i][k] = tm[i][k + 1]
					tm[i][size_board - 1] = 0  
	def mergeTiles(self): 
		tm = self.matrix
		size_board = len(self.matrix)
		for i in range(0, size_board):
			for k in range(0, size_board - 1):
				if tm[i][k] == tm[i][k + 1] and tm[i][k] != 0:
					tm[i][k] = tm[i][k] * 2
					tm[i][k + 1] = 0
					self.score += tm[i][k]
					self.moveTiles()
           
	def checkIfCanGo(self):
		tm = self.matrix
		size_board = len(self.matrix)
		for i in range(0, size_board ** 2): 
			if tm[int(i / size_board)][i % size_board] == 0: 
				return True		
		for i in range(0, size_board):      
			for j in range(0, size_board - 1):  
				if tm[i][j] == tm[i][j + 1]:
					return True
				elif tm[j][i] == tm[j + 1][i]:
					return True
		return False
	
	def canMove(self): 
		tm = self.matrix
		size_board = len(self.matrix)
		for i in range(0, size_board):
			for j in range(1, size_board):
				if tm[i][j-1] == 0 and tm[i][j] > 0:
					return True
				elif (tm[i][j-1] == tm[i][j]) and tm[i][j-1] != 0:
					return True
		return False
	# saveGameState() 	removed
	# loadGameState()	removed
	def rotateMatrixClockwise(self):	
		tm = self.matrix
		size_board = len(self.matrix)
		for i in range(0, int(size_board/2)): 
			for k in range(i, size_board- i - 1): 
				temp1 = tm[i][k]
				temp2 = tm[size_board - 1 - k][i] 
				temp3 = tm[size_board - 1 - i][size_board - 1 - k] 
				temp4 = tm[k][size_board - 1 - i] 
				tm[size_board - 1 - k][i] = temp1 
				tm[size_board - 1 - i][size_board - 1 - k] = temp2 
				tm[k][size_board - 1 - i] = temp3  
				tm[i][k] = temp4	
	def convertToLinearMatrix(self):  
		m = []
		size_board = len(self.matrix)
		for i in range(0, size_board ** 2):
			m.append(self.matrix[int(i / size_board)][i % size_board]) ##
		m.append(self.matrixBeforeScore)
		return m
