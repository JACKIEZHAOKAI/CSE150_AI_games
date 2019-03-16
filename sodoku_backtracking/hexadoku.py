# implementation of Sudoku using back propagation and search
# author: ZHAOKAI XU
# ref: http://norvig.com/sudoku.html

from __future__ import print_function
import random
import copy
import numpy as np
import time
import heapq	

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
		for i in range(0,16):
			for j in range(0,16):
				peerList = []
				# add row 
				for row in range(0,16): 
					if row != i:	
						peerList.append((row,j))
				# add col 
				for col in range(0,16):
					if col != j:	
						peerList.append((i,col))
				# add grid
				rowLowerBound = int((i)/4)*4
				rowUpperBound = rowLowerBound+4
				colLowerBound = int((j)/4)*4		
				colUpperBound = colLowerBound+4
		
				for row in range(rowLowerBound, rowUpperBound):
					for col in range(colLowerBound, colUpperBound):
						if (row,col) != (i,j):
							peerList.append((row,col))

				self.peers[(i,j)] = peerList

	# parse the string of a problem into twoDArray[[][]...] and domains{key,value}
	def parse(self, problem):
		for i in range(0, 16):
			for j in range(0, 16):
				c = problem[i*16+j]
				if c == '.':
					self.domains[(i, j)] = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
				else:    # store the value
					if c == 'A' or c=='B' or c=='C' or c=='D' or c=='E' or c=='F':
					    self.domains[(i, j)] = [ord(c)-65+10]
					    # print("char", (i, j), "value ", [ord(c)-65+10])
					else:
					    self.domains[(i, j)] = [ord(c)-48]
					    # print("char", (i, j), "value ", [ord(c)-48])
		# print(self.domains)
	
	# Constraint Propagation
	def eliminateDomain(self):
		for i in range(0, 16):
			for j in range(0, 16):
				# check if the slot not filled
				spot = (i,j)
				if len(self.domains[spot]) > 1:
					for peer in self.peers[spot]:
						# print("self.domains[peer]",self.domains[peer])
						if len(self.domains[peer]) == 1:	# peer value already known
							peerValue = self.domains[peer][0]
							if peerValue in self.domains[spot]: 
								self.domains[spot].remove(peerValue)
		
	# display the twoD array
	def display(self):
		for i in range(0, 16):
			for j in range(0, 16):
				d = self.domains[(i, j)]
				# print(d," ")
				if len(d) == 1:
					if (d[0] == 10):
						print('A', end='')
					elif (d[0] == 11):
						print('B', end='')
					elif (d[0] == 12):
						print('C', end='')
					elif (d[0] == 13):
						print('D', end='')
					elif (d[0] == 14):
						print('E', end='')
					elif (d[0] == 15):
						print('F', end='')
					else:
						print(d[0], end='')
				else:
					print('.', end='')
				if j == 3 or j == 7 or j == 11:
					print(" | ", end='')
			print()
			if j == 3 or j == 7 or j == 11:
				print("---------------")

# Solver takes a grid of problem, solve the problem,
# return True/False if the problem can/can not be solved
class Solver:
	def __init__(self, grid):
		# sigma is the assignment function
		self.sigma = {}         # a dict of spot and its value        sigma == assignment
		self.grid = grid

		# store in sigma if the value is determined in the slot
		for i in range(0, 16):
			for j in range(0, 16):
				if len(self.grid.domains[(i, j)]) == 1:
					self.sigma[(i, j)] = self.grid.domains[(i, j)][0]
				else:
					self.sigma[(i, j)] = 0 

	def display(self):
		for i in range(0, 16):
			for j in range(0, 16):
				spot = (i, j)
				if spot in self.sigma: 
					if (self.sigma[spot] == 10):
						print('A', end='')
					if (self.sigma[spot] == 11):
						print('B', end='')
					if (self.sigma[spot] == 12):
						print('C', end='')
					if (self.sigma[spot] == 13):
						print('D', end='')
					if (self.sigma[spot] == 14):
						print('E', end='')
					if (self.sigma[spot] == 15):
						print('F', end='')
					else:
						print(self.sigma[spot], end='')
				else:
					print('.', end='')
				if j == 3 or j == 7 or j == 11:
					print(" | ", end='')
			print()
			if i == 3 or i == 7 or i == 11:
				print("---------------")

###################################################################
# call search to search the problem recursively
###################################################################
	def solve(self):
		res = self.search(self.sigma, self.grid.domains)
		return res

###################################################################
# recursive call in DFS to solve the searching problem
###################################################################
	def search(self, assignment, domains):
		# mission completed
		if 0 not in assignment.values():
			self.sigma = assignment
			return True
	
		# select an unsigned spot with min domain from unassignedSpot list.
		n,spot = min((len(domains[s]), s) for s in assignment if assignment[s] == 0)
		print ("searching", spot)
		infrenceDict={}
	
		for value in domains[spot]:
			
			if self.consistent(spot, value, assignment):
				# add {spot=value} to assignment, and remove from unassignedSpot
				assignment[spot] = value  # guess spot to have value
			
				copy_domains = copy.deepcopy(domains)
				# inferences ←INFERENCE(unassignedSpot, var , value)
				infrenceDict, inferSucc = self.infer(spot, assignment, copy_domains)
			
				# if inferences not failure then
				if inferSucc == True:

					# add {inferences=inferencesValue} to assignment, and remove from unassignedSpot
					for infSpot, infVal in infrenceDict.items():
						assignment[infSpot] = infVal

					# recursive callr  esult ←BACKTRACK(assignment , unassignedSpot)
					result = self.search( assignment, copy_domains)	# no need for deepCopy, which is costy

					if result == True: 
						return True
						
			# !!!backtrack				
			assignment[spot] = 0
			for inference in infrenceDict:
				assignment[inference] = 0  

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
# Advanced infer, infer using the remained domain values
###################################################################
	def infer(self, guessSpot, assignment, domains):
		
		infrenceDict = {}  # dict mapping slot to its infer value
		guessValue = assignment[guessSpot]

		for peer in self.grid.peers[guessSpot]:
			if guessValue in domains[peer]:
				domains[peer].remove(guessValue)

		for peer in self.grid.peers[guessSpot]:
			
			# conflict value
			if len(domains[peer]) == 0:
				return {}, False

			# try to make inference, if domain reduced to 1 value
			if len(domains[peer]) == 1 and assignment[peer] == 0:
				inferVal = domains[peer][0]

				if not self.consistent(peer, inferVal, assignment):
					return {}, False
				
				# make an inference 
				infrenceDict[peer] = inferVal
				assignment[peer] = inferVal

				# recursive call to make more inferrence
				new_inference,valid = self.infer( peer,assignment, domains)

				if valid:
					for inference in new_inference:
						infrenceDict[inference] = new_inference[inference]
				else:
					assignment[peer] = 0
					# unassignedSpot.append(peer)
					return {}, False
				break

		return infrenceDict, True

hard16 = [
".D4F.....856.03..5...D9..4.A62..A..1...0..2.54F...8.B...D.E.9.....9C.....D.4.E......7CB...F.......0D...A3B..F87.....2E...7...C.0.....4..C......B....F.E..0......D.7.91..E5......6.52A8..F.B.0..946..1..D.E8.3.....183B..5..........3..C.0....F.6B......2..9C8.A1", 
"3.8E....1..C.B.A.75.A..1.D.8..9....AE5B..0...6.26.9...34..F.....01..5.6..3..E.....2..1D0......4..4B.F..7.....9..85.C3...E2.9.....F..2...0.D1.37.....8.....7.D..B..4.............A..3.0..6.....84..ED6C9.B..08....9....8....2C43.........8..6A..D50..7....C..2.F.", 
"1D.B.....7.....6.35A.C.F..E....0...02.4..5..C18A4....BD..2......28..B....F..4...5.......6....8..D1A..2C.0.7.........A...48...E0C7.36.9..8..2A..........D.A...3.........65.C..0BD.2E.4.80......7F6.79.0....5F...1.5...D1.2.0C.B...C.....9.13....8...23A......5..."
]


print("====Problem easy====")
counter=0
overallTime = 0
for problem in hard16:
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

