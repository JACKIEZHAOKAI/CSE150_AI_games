# implementation of Sudoku using back propagation and search
# author: ZHAOKAI XU
# ref: http://norvig.com/sudoku.html

from __future__ import print_function
import random
import copy
import numpy as np
import time

class Grid:
	def __init__(self, problem):
		# self.spots = [(i, j) for i in range(1,10) for j in range(1,10)]
		# domian is a dictionary that maps each spot/tuple to a List of domain value
		self.domains = {}
		self.peers = {}     # peer is a dictionary of slots
		self.parse(problem)
		self.addPeers()
		self.eliminateDomain()	# eliminate values from domain if exist in same row/col/grid

	def addPeers(self):
		for i in range(1,10):
			for j in range(1,10):
				peerList = []
				# add row 
				for row in range(1, 10):
					if row != i:	
						peerList.append((row,j))
				# add col 
				for col in range(1, 10):
					if col != j:	
						peerList.append((i,col))
				# add grid
				rowLowerBound = int((i-1)/3)*3+1
				rowUpperBound = rowLowerBound+3
				colLowerBound = int((j-1)/3)*3+1		
				colUpperBound = colLowerBound+3

				for row in range(rowLowerBound, rowUpperBound):
					for col in range(colLowerBound, colUpperBound):
						if (row,col) != (i,j):
							peerList.append((row,col))

				self.peers[(i,j)] = peerList

	# parse the string of a problem into twoDArray[[][]...] and domains{key,value}
	def parse(self, problem):
		for i in range(0, 9):
			for j in range(0, 9):
				c = problem[i*9+j]
				if c == '.':
					self.domains[(i+1, j+1)] = [1,2,3,4,5,6,7,8,9]
				else:    # store the value
					self.domains[(i+1, j+1)] = [ord(c)-48]
	
	# Constraint Propagation
	def eliminateDomain(self):
		for i in range(1, 10):
			for j in range(1, 10):
				# check if the slot not filled
				spot = (i,j)
				if len(self.domains[spot]) > 1:
					for peer in self.peers[spot]:
						if len(self.domains[peer]) == 1:	# peer value already known
							peerValue = self.domains[peer][0]
							if peerValue in self.domains[spot]: 
								self.domains[spot].remove(peerValue)
		
	# display the twoD array
	def display(self):
		for i in range(0, 9):
			for j in range(0, 9):
				d = self.domains[(i+1, j+1)]
				if len(d) == 1:
					print(d[0], end='')
				else:
					print('.', end='')
				if j == 2 or j == 5:
					print(" | ", end='')
			print()
			if i == 2 or i == 5:
				print("---------------")

# Solver takes a grid of problem, solve the problem,
# return True/False if the problem can/can not be solved
class Solver:
	def __init__(self, grid):
		# sigma is the assignment function
		self.sigma = {}         # a dict of spot and its value        sigma == assignment
		self.grid = grid
		self.unassignedSpot = []
		
		# store in sigma if the value is determined in the slot
		for i in range(1, 10):
			for j in range(1, 10):
				if len(self.grid.domains[(i, j)]) == 1:
					self.sigma[(i, j)] = self.grid.domains[(i, j)][0]
				else:
					self.unassignedSpot.append((i, j))

	def display(self):
		for i in range(0, 9):
			for j in range(0, 9):
				spot = (i+1, j+1)
				if spot in self.sigma: 
					print(self.sigma[spot], end='')
				else:
					print('.', end='')
				if j == 2 or j == 5:
					print(" | ", end='')
			print()
			if i == 2 or i == 5:
				print("---------------")

###################################################################
# call search to search the problem recursively
###################################################################
	def solve(self):
		res = self.search(self.sigma, self.unassignedSpot)
		return res

###################################################################
# recursive call in DFS to solve the searching problem
###################################################################
	def search(self, assignment, unassignedSpot):
		# mission completed
		if(len(assignment) == 81):
			self.sigma = assignment
			return True

		# select an unsigned variable from unassignedSpot list
		spot = unassignedSpot[0]

		for value in self.grid.domains[spot]:
			# check consistence
			if self.consistent(spot, value, assignment):
				# add {spot=value} to assignment, and remove from unassignedSpot
				assignment[spot] = value  # guess spot to have value
				unassignedSpot.remove(spot)

				# inferences ←INFERENCE(unassignedSpot, var , value)
				infrenceDict, inferSucc = self.infer(spot, assignment)

				# if inferences not failure then
				if inferSucc == True:

					# add {inferences=inferencesValue} to assignment, and remove from unassignedSpot
					for infSlot, infVal in infrenceDict.items():
						assignment[infSlot] = infVal
						unassignedSpot.remove(infSlot)

					# recursive callr  esult ←BACKTRACK(assignment , unassignedSpot)
					result = self.search( assignment,copy.deepcopy(unassignedSpot))

					if result == True:  # totally correct, on the way to mission complete
						return True

					# if search failedm, Reverse operation add {inferences=inferencesValue} to assignment
					for infSpot, infVal in infrenceDict.items():
						assignment.pop(infSpot)
						unassignedSpot.append(infSpot)

				# !!!backtrack				
				# reverse operation add {spot=value} to assignment                          f
				assignment.pop(spot)     
				unassignedSpot.append(spot)        

		return False


###################################################################
	# check if consistent in row/col/grid
###################################################################
	def consistent(self, spot, value, assignment):	
		# check if value already exist in peers, if so, guess value fails
		for peer in self.grid.peers[spot]:
			if peer in assignment:
				if assignment[peer] == value:
					return False
		return True


###################################################################
	# For optimization in searching the value, especially solving hard problems
	# return a dict of slot with its inference value
###################################################################
	def infer(self, spot, assignment):
		
		infrenceDict = {}  # dict mapping slot to its infer value
		inferSuccess = True

		# row infer
		inferValue = [1,2,3,4,5,6,7,8,9]    # list of slot value
		emptySpots = []    # list of slot/tuple
		for j in range(1, 10):
			if (spot[0], j) in assignment:
				inferValue.remove(assignment[(spot[0], j)])
			else:
				emptySpots.append((spot[0], j))
		if len(emptySpots) == 1:    # only one empty spot, then do inference
			# again check consistence
			if self.consistent(emptySpots[0], inferValue[0], assignment) == True:
				infrenceDict[emptySpots[0]] = inferValue[0]
			else:
				inferSuccess = False     # infer conflict
				return infrenceDict, inferSuccess

		# col infer
		inferValue = [1,2,3,4,5,6,7,8,9]    # list of slot value
		emptySpots = []    # list of slot/tuple
		for i in range(1, 10):
			if (i, spot[1]) in assignment:
				inferValue.remove(assignment[(i, spot[1])])
			else:
				emptySpots.append((i, spot[1]))
		if len(emptySpots) == 1:    # only one empty spot, then do inference
			# again check consistence
			if self.consistent(emptySpots[0], inferValue[0], assignment) == True:
				infrenceDict[emptySpots[0]] = inferValue[0]
			else:
				inferSuccess = False     # infer conflict
				return infrenceDict, inferSuccess

		# grid infer
		rowLowerBound = int((spot[0]-1)/3)*3+1
		rowUpperBound = rowLowerBound+3
		colLowerBound = int((spot[1]-1)/3)*3+1		
		colUpperBound = colLowerBound+3

		inferValue = [1,2,3,4,5,6,7,8,9]
		emptySpots = [] 
		for m in range(rowLowerBound, rowUpperBound):
			for n in range(colLowerBound, colUpperBound):
				if (m, n) in assignment:
					inferValue.remove(assignment[(m, n)])
				else:
					emptySpots.append((m, n))
		if len(emptySpots) == 1:    # only one empty spot, then do inference
			# again check consistence
			if self.consistent(emptySpots[0], inferValue[0], assignment) == True:
				infrenceDict[emptySpots[0]] = inferValue[0]
			else:
				inferSuccess = False     # infer conflict
				return infrenceDict, inferSuccess

		return infrenceDict, inferSuccess


##########################################################################
#	another implementation of infer, with some err not fixed
##########################################################################
		# infrenceDict = {}  # dict mapping slot to its infer value
		# inferSuccess = True
		# prunedPeers = []
		# value = assignment[spot]

		# print ("spot ",spot, " guess", value)
		# # 1	loop to purne(remove value from) all its peer's domain
		# for peer in self.grid.peers[spot]:
		# 	if value in self.grid.domains[peer]:
		# 		print("add to prunedPeers", peer,"self.grid.domains[peer]",self.grid.domains[peer])
		# 		self.grid.domains[peer].remove(value)
		# 		prunedPeers.append(peer)
		# 		# prevent value conflict 
		# 		if len(self.grid.domains[peer]) == 0:
		# 			# reverse domains[peer].remove(value)
		# 			for p in prunedPeers:
		# 				self.grid.domains[p].append(value)
		# 			inferSuccess = False
		# 			return infrenceDict,inferSuccess

		# # 2	loop to check if any peer's d
		# for peer in prunedPeers:
		# 	if len(self.grid.domains[peer]) == 1:
		# 		print ("peer",peer, "with value", self.grid.domains[peer])
		# 		# make an inference
		# 		infrenceDict[peer] = self.grid.domains[peer][0]
				
		# # 3 prevent infer conflict
		# for infspot, infVal in infrenceDict.items():
		# 	if self.consistent( infspot, infVal, assignment) == False:	
		# 		for p in prunedPeers:
		# 			self.grid.domains[p].append(value)
		# 		inferSuccess = False
		# 		return infrenceDict,inferSuccess

		# return infrenceDict, inferSuccess
##########################################################################
		

# all 50 problems 
easy = ['..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..',
 '2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3',
 '......9.7...42.18....7.5.261..9.4....5.....4....5.7..992.1.8....34.59...5.7......',
 '.3..5..4...8.1.5..46.....12.7.5.2.8....6.3....4.1.9.3.25.....98..1.2.6...8..6..2.',
 '.2.81.74.7....31...9...28.5..9.4..874..2.8..316..3.2..3.27...6...56....8.76.51.9.',
 '1..92....524.1...........7..5...81.2.........4.27...9..6...........3.945....71..6',
 '.43.8.25.6.............1.949....4.7....6.8....1.2....382.5.............5.34.9.71.',
 '48...69.2..2..8..19..37..6.84..1.2....37.41....1.6..49.2..85..77..9..6..6.92...18',
 '...9....2.5.1234...3....16.9.8.......7.....9.......2.5.91....5...7439.2.4....7...',
 '..19....39..7..16..3...5..7.5......9..43.26..2......7.6..1...3..42..7..65....68..',
 '...1254....84.....42.8......3.....95.6.9.2.1.51.....6......3.49.....72....1298...',
 '.6234.75.1....56..57.....4.....948..4.......6..583.....3.....91..64....7.59.8326.',
 '3..........5..9...2..5.4....2....7..16.....587.431.6.....89.1......67.8......5437',
 '63..........5....8..5674.......2......34.1.2.......345.....7..4.8.3..9.29471...8.',
 '....2..4...8.35.......7.6.2.31.4697.2...........5.12.3.49...73........1.8....4...',
 '361.259...8.96..1.4......57..8...471...6.3...259...8..74......5.2..18.6...547.329',
 '.5.8.7.2.6...1..9.7.254...6.7..2.3.15.4...9.81.3.8..7.9...762.5.6..9...3.8.1.3.4.',
 '.8...5........3457....7.8.9.6.4..9.3..7.1.5..4.8..7.2.9.1.2....8423........1...8.',
 '..35.29......4....1.6...3.59..251..8.7.4.8.3.8..763..13.8...1.4....2......51.48..',
 '...........98.51...519.742.29.4.1.65.........14.5.8.93.267.958...51.36...........',
 '.2..3..9....9.7...9..2.8..5..48.65..6.7...2.8..31.29..8..6.5..7...3.9....3..2..5.',
 '..5.....6.7...9.2....5..1.78.415.......8.3.......928.59.7..6....3.4...1.2.....6..',
 '.4.....5...19436....9...3..6...5...21.3...5.68...2...7..5...2....24367...3.....4.',
 '..4..........3...239.7...8.4....9..12.98.13.76..2....8.1...8.539...4..........8..',
 '36..2..89...361............8.3...6.24..6.3..76.7...1.8............418...97..3..14',
 '5..4...6...9...8..64..2.........1..82.8...5.17..5.........9..84..3...6...6...3..2',
 '..72564..4.......5.1..3..6....5.8.....8.6.2.....1.7....3..7..9.2.......4..63127..',
 '..........79.5.18.8.......7..73.68..45.7.8.96..35.27..7.......5.16.3.42..........',
 '.3.....8...9...5....75.92..7..1.5..8.2..9..3.9..4.2..1..42.71....2...8...7.....9.',
 '2..17.6.3.5....1.......6.79....4.7.....8.1.....9.5....31.4.......5....6.9.6.37..2',
 '.......8.8..7.1.4..4..2..3.374...9......3......5...321.1..6..5..5.8.2..6.8.......',
 '.......85...21...996..8.1..5..8...16.........89...6..7..9.7..523...54...48.......',
 '6.8.7.5.2.5.6.8.7...2...3..5...9...6.4.3.2.5.8...5...3..5...2...1.7.4.9.4.9.6.7.1',
 '.5..1..4.1.7...6.2...9.5...2.8.3.5.1.4..7..2.9.1.8.4.6...4.1...3.4...7.9.2..6..1.',
 '.53...79...97534..1.......2.9..8..1....9.7....8..3..7.5.......3..76412...61...94.',
 '..6.8.3...49.7.25....4.5...6..317..4..7...8..1..826..9...7.2....75.4.19...3.9.6..',
 '..5.8.7..7..2.4..532.....84.6.1.5.4...8...5...7.8.3.1.45.....916..5.8..7..3.1.6..',
 '...9..8..128..64...7.8...6.8..43...75.......96...79..8.9...4.1...36..284..1..7...',
 '....8....27.....54.95...81...98.64...2.4.3.6...69.51...17...62.46.....38....9....',
 '...6.2...4...5...1.85.1.62..382.671...........194.735..26.4.53.9...2...7...8.9...',
 '...9....2.5.1234...3....16.9.8.......7.....9.......2.5.91....5...7439.2.4....7...',
 '38..........4..785..9.2.3...6..9....8..3.2..9....4..7...1.7.5..495..6..........92',
 '...158.....2.6.8...3.....4..27.3.51...........46.8.79..5.....8...4.7.1.....325...',
 '.1.5..2..9....1.....2..8.3.5...3...7..8...5..6...8...4.4.1..7.....7....6..3..4.5.',
 '.8.....4....469...4.......7..59.46...7.6.8.3...85.21..9.......5...781....6.....1.',
 '9.42....7.1..........7.65.....8...9..2.9.4.6..4...2.....16.7..........3.3....57.2',
 '...7..8....6....31.4...2....24.7.....1..3..8.....6.29....8...7.86....5....2..6...',
 '..1..7.9.59..8...1.3.....8......58...5..6..2...41......8.....3.1...2..79.2.7..4..',
 '.....3.17.15..9..8.6.......1....7.....9...2.....5....4.......2.5..6..34.34.2.....',
 '3..2........1.7...7.6.3.5...7...9.8.9...2...4.1.8...5...9.4.3.1...7.2........8..6']

hard = [
	'4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......',
 '52...6.........7.13...........4..8..6......5...........418.........3..2...87.....'
  '6..3.2....5.....1..........7.26............543.........8.15........4.2........7..'
 ]

print("====Problem easy====")
counter=0
overallTime = 0
for problem in easy:
	print("====Initial {}===".format(counter))
	counter = counter + 1
	g = Grid(problem)
	# Display the original problem
	g.display()

	start = time.time()
	s = Solver(g)
	if s.solve():
		print("====Solution===")
		# Display the solution
		# Feel free to call other functions to display
		s.display()
		end = time.time()
		print("time cost: ",end - start)
		overallTime = overallTime + (end - start)
	else:
		print("==No solution==")

print("overallTime:", overallTime)
print("AverageTime:",overallTime/50)

# print("====Problem hard====")
# counter=0
# overallTime = 0
# for problem in hard:
# 	print("====Initial {}===".format(counter))
# 	counter = counter + 1
# 	g = Grid(problem)
# 	# Display the original problem
# 	g.display()

# 	start = time.time()
# 	s = Solver(g)
# 	if s.solve():
# 		print("====Solution===")
# 		# Display the solution
# 		# Feel free to call other functions to display
# 		s.display()
# 		end = time.time()
# 		print("time cost: ",end - start)
# 		overallTime = overallTime + (end - start)
# 	else:
# 		print("==No solution==")

# print("overallTime:", overallTime)
# print("AverageTime:",overallTime/3)