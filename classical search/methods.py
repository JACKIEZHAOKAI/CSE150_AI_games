from __future__ import print_function
#Use priority queues from Python libraries, don't waste time implementing your own
import heapq

ACTIONS = [(0,-1),(-1,0),(0,1),(1,0)]

class Agent:

    def __init__(self, grid, start, goal, type):
        self.grid = grid
        self.previous = {}
        self.explored = []
        self.start = start 
        self.grid.nodes[start].start = True
        self.goal = goal
        self.grid.nodes[goal].goal = True
        self.new_plan(type)

    def new_plan(self, type):
        #define a heuristic function
        def heuristic(a,b):
            return  (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2

        self.finished = False
        self.failed = False
        self.type = type

        # reinitialized graph for each testing 
        if self.type == "dfs" :
            self.frontier = [self.start]
            self.explored = []
        elif self.type == "bfs":
            self.frontier = [self.start]
            self.explored = []

        elif self.type == "ucs":
            # maintain a priority queue
            self.frontier =  [(0,self.start)]
            self.explored = []

        elif self.type == "astar":
            self.frontier =  [(heuristic(self.goal,self.start),0,self.start)]
            self.explored = []
    
    def show_result(self):
        current = self.goal
        while not current == self.start:
            current = self.previous[current]
            self.grid.nodes[current].in_path = True #This turns the color of the node to red
    
    def make_step(self):
        if self.type == "dfs":
            self.dfs_step()
        elif self.type == "bfs":
            self.bfs_step()
        elif self.type == "ucs":
            self.ucs_step()
        elif self.type == "astar":
            self.astar_step()
   
    def dfs_step(self):
        #check if the frontier is empyt
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        current = self.frontier.pop()
        print("current node: ", current)

        #marked current node as visited and add to explored list
        self.grid.nodes[current].checked = True
        self.grid.nodes[current].frontier = False
        self.explored.append(current)
        children = [(current[0]+a[0], current[1]+a[1]) for a in ACTIONS]
       
        #iterate all the neighbour of current node
        for node in children:
            #See what happens if you disable this check here
            #stuck in looping if keep re-visiting the visited nodes
            if node in self.explored or node in self.frontier:
                print("explored before: ", node)
                continue
            #check if the neighbour is out of range 
            if node[0] in range(self.grid.row_range) and node[1] in range(self.grid.col_range):
                #check if hit the puddle
                if self.grid.nodes[node].puddle:
                    print("puddle at: ", node)
                else:
                    #check if the node is match the goal, if so finished
                    self.previous[node] = current
                    if node == self.goal:
                        self.finished = True
                        return
                    else:
                        #push the node to top of the stack
                        self.frontier.append(node)
                        #mark the node to be in the frontier
                        self.grid.nodes[node].frontier = True
            else:
                print("out of range: ", node)

    def bfs_step(self):
        #check if the frontier is empyt
        if not self.frontier:
            self.failed = True
            print("no path")
            return

        current = self.frontier.pop()
        print("current node: ", current)

        #marked current node as visited and add to explored list
        self.grid.nodes[current].checked = True
        self.grid.nodes[current].frontier = False
        self.explored.append(current)
        children = [(current[0]+a[0], current[1]+a[1]) for a in ACTIONS]
        
        #iterate all the neighbour of current node
        for node in children:
            #See what happens if you disable this check here
            #stuck in looping if keep re-visiting the visited nodes
            if node in self.explored or node in self.frontier:
                print("explored before: ", node)
                continue
            #check if the neighbour is out of range 
            if node[0] in range(self.grid.row_range) and node[1] in range(self.grid.col_range):
                #check if hit the puddle
                if self.grid.nodes[node].puddle:
                    print("puddle at: ", node)
                else:
                    #check if the node is match the goal, if so finished
                    self.previous[node] = current
                    if node == self.goal:
                        self.finished = True
                        return
                    else:
                        # enqueue 
                        self.frontier.insert(0,node)
                        #mark the node to be in the frontier
                        self.grid.nodes[node].frontier = True
            else:
                print("out of range: ", node)


    

    def ucs_step(self):
        #[Hint] you can get the cost of a node by node.cost()
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        
        curr_cost,current = heapq.heappop(self.frontier)
        print("current node: ", current)
        
        #update current node information and marked as visited
        self.grid.nodes[current].checked = True
        self.grid.nodes[current].frontier = False
        self.explored.append(current)
        children = [(current[0]+a[0], current[1]+a[1]) for a in ACTIONS]
       
        #iterate all the neighbour of current node
        for node in children:
            #See what happens if you disable this check here
            #stuck in looping if keep re-visiting the visited nodes
            if node in self.explored or node in self.frontier:
                print("explored before: ", node)
                continue
            #check if the neighbour is out of range 
            if node[0] in range(self.grid.row_range) and node[1] in range(self.grid.col_range):
                #check if hit the puddle
                if self.grid.nodes[node].puddle:
                    print("puddle at: ", node)
                else:
                    #check if the node is match the goal, if so finished
                    self.previous[node] = current
                    if node == self.goal:
                        self.finished = True
                        print ("total cost is:", heapq.heappop(self.frontier)[0])   # LOST 1 points for not printing out  >_<
                        return
                    else:
                    	new_cost = self.grid.nodes[node].cost() + curr_cost
                    	flag = True
                    	# check the dupliated items in PQ
                    	for item in self.frontier:
                    		#found duplication
                    		if item[1] == node:
                    			flag = False
                    			# if found lower cost, update the item cost in PQ
                    			if new_cost < item[0]:
	                    			self.frontier.remove(item)
	                    			heapq.heappush( self.frontier, (new_cost, node))
	                    			self.grid.nodes[node].frontier = True
                    	# firstly visited, add to PQ
                    	if flag:
                    		heapq.heappush( self.frontier, (new_cost, node))
                    		self.grid.nodes[node].frontier = True                    		
            else:
                print("out of range: ", node)


    def astar_step(self):
        #define a heuristic function
        def heuristic(a,b):
            return  (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2

        #[Hint] you need to declare a heuristic function for c
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        
        curr_F_score,curr_G_score,current = heapq.heappop(self.frontier)
        print("current node: ", current)
        
        #update current node information and marked as visited
        self.grid.nodes[current].checked = True
        self.grid.nodes[current].frontier = False
        self.explored.append(current)
        children = [(current[0]+a[0], current[1]+a[1]) for a in ACTIONS]
       
        #iterate all the neighbour of current node
        for node in children:
            #See what happens if you disable this check here
            #stuck in looping if keep re-visiting the visited nodes
            if node in self.explored or node in self.frontier:
                print("explored before: ", node)
                continue
            #check if the neighbour is out of range 
            if node[0] in range(self.grid.row_range) and node[1] in range(self.grid.col_range):
                #check if hit the puddle
                if self.grid.nodes[node].puddle:
                    print("puddle at: ", node)
                else:
                    #check if the node is match the goal, if so finished
                    self.previous[node] = current
                    if node == self.goal:
                        self.finished = True
                        print ("total cost is:", heapq.heappop(self.frontier)[0]) 
                        return
                    else:
                        print(self.goal, "  now visiting",node)

                        #calculate F = G + H and add current node to PQ
                        new_F_score = self.grid.nodes[node].cost() + curr_G_score + heuristic(self.goal,node)  
                        new_G_score = self.grid.nodes[node].cost() + curr_G_score
                        heapq.heappush( self.frontier, ( new_F_score,new_G_score , node) )
                        #mark the node to be in the frontier
                        self.grid.nodes[node].frontier = True
        else:
                print("out of range: ", node)
         












