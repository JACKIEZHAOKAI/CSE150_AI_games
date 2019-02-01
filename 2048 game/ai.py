# CSE 150 PA2
# ZHAOKAI XU

from __future__ import absolute_import, division, print_function
import copy
import random
import heapq
MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}
PLAYERS = {'player': 0, 'computer': 1}


class Node:	
	"""Node of the GameTree"""
	def __init__(self, matrix, player, score):
		self.matrix = matrix
		self.player =player
		self.score = score
		self.children =  []
		self.move =  -1
		self.isTerminal = False

	def setMovement(self, move):
		self.move = move
	def setisTerminal(self):
		self.isTerminal = True

	def getMatrix(self):
		return self.matrix		
	def getPlayer(self):
	    return self.player
	def getScore(self):
	    return self.score
	def getMovement(self):
		return self.move 
	def getisTerminal(self):
		return self.isTerminal
	def payoff(self):
		return self.score

	def addchildren(self,newnode):
		self.children.append(newnode)
	def getChildren(self):
		return self.children
	def chance(self):
		return 1.0/len(self.children)


class Gametree:
	"""main class for the AI"""

	def __init__(self, root_state, depth_of_tree, current_score): 
		'''construct a game tree from any Node of the game'''

		self.root = Node(root_state, PLAYERS['player'], current_score)
		self.depth_of_tree = depth_of_tree

	def treeGenerator(self,node,isTerminal):	

		if node.getPlayer() == PLAYERS['player']: 
			# simulate the four possible moves
			for i in range(4):
				simulator = Simulator( copy.deepcopy(node.getMatrix()), node.getScore() )

				if simulator.checkIfCanGo():
					simulator.move(i)
					
					if( simulator.getMatrix() != copy.deepcopy(node.getMatrix()) ):
						
						# create a child Node obj from the simulator   	
						child = Node(copy.deepcopy(simulator.getMatrix()), PLAYERS['computer'], simulator.getScore())

						child.setMovement(i)

						if isTerminal:
							child.setisTerminal()

						node.addchildren(child)


		elif node.getPlayer() == PLAYERS['computer']:
                    
			currMatrix = copy.deepcopy(node.getMatrix())

			# create a possible set of 2 in each child node
			for i in range(len(currMatrix)):
				for j in range(len(currMatrix)):
					if currMatrix[i][j] == 0:
						newMatrix = copy.deepcopy(currMatrix)
						newMatrix[i][j] = 2
						
						child = Node(newMatrix, PLAYERS['player'], node.getScore())
						node.addchildren(child)


	def growTree(self, node):
		'''Construct a depth-3 game tree by calling treeGenerator()'''
		
		self.treeGenerator(self.root,False) 
		print ("layer1")

		for child in self.root.getChildren(): 
			# print ("layer2")
			self.treeGenerator(child, False)

		for child in self.root.getChildren():  
		    for grandChild in child.getChildren():
		    	# print ("layer3")
		    	self.treeGenerator(grandChild,True)


	def expectimax(self, node):
		'''Compute expectimax values and optimal moves'''

		# if it is the leaf node, return the value
		if node.getisTerminal():
		    return node.payoff()
		# if is player, generate possibilities of the four direction move
		elif node.getPlayer() == PLAYERS['player']:
		    value = float('-inf')
		    for child in node.getChildren():
		       value = max( value, self.expectimax(child) )
		    return value
		# if is computer, set the chance of appearing the next 2 to be equal in all empty tile 
		elif node.getPlayer() == PLAYERS['computer']:
			value = 0
			for child in node.getChildren():
				value = value + self.expectimax(child) * node.chance()
			return value
		else:
			return 'Error'


	def compute_decision(self):
		'''function to return best decision to game'''

		# 1	grow the tree
		self.growTree(self.root) 
	
		# 2	find the path to generate the max value from its subtree
		maxValue = 0
		optimal_move = 0

		for child in self.root.getChildren():

			child_value = self.expectimax(child)
			# print ("child_move", child.getMovement())
			# print ("child_value",child_value)

			if child_value > maxValue:
				maxValue = child_value
				optimal_move = child.getMovement()
	
		print ("next move:", MOVES[optimal_move])
		print ("score", maxValue )

		return optimal_move


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
