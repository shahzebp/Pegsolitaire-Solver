import 	pegSolitaireUtils
import 	config
import 	numpy as np
import 	itertools

from 	collections import defaultdict
from 	copy import deepcopy

try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q


######	Start of Algorithms ########

# This is a depth first search algorithm with recursive implementation


# List to store previously encountered game state
# Important note: this list is local to each depth. This 
# is achieved by resetting it before running DFS for each depth

repeatedStates = {}

def DFS(pegSolitaireObject, depth):

	# If a repetead state is found, return as it had already been explored.
	
	lexedState = str(pegSolitaireObject.gameState)	
	if lexedState in repeatedStates:
		return False
	
	if 0 == depth :
		return False
	for i in range(7):
		for j in range(7):
			if 1 == pegSolitaireObject.gameState[i][j] :
				for key in {'N', 'S', 'E', 'W'}:
					if True == pegSolitaireObject.is_validMove((i, j), key) :
						modifiedState = pegSolitaireObject.getNextState((i, j), key)
						modifiedStateStr = str(pegSolitaireObject.gameState)
						repeatedStates[modifiedStateStr] = True

						# Goal State has been found

						if modifiedState == pegSolitaireObject.goalState :
							newPosition = pegSolitaireObject.getNextPosition((i, j), key)
							pegSolitaireObject.trace.insert(0, newPosition)
							pegSolitaireObject.trace.insert(0, (i, j))	
							return True

						# Goal State not found but the move has been valid (Produced a child)

						else :	
							parentState = deepcopy(pegSolitaireObject.gameState)
							pegSolitaireObject.gameState = modifiedState
							
							# Run the DFS on the produced child with reduced depth

							rc = DFS(pegSolitaireObject, depth - 1)
							if rc == True:
								newPosition = pegSolitaireObject.getNextPosition((i, j), key)
								pegSolitaireObject.trace.insert(0, newPosition)
								pegSolitaireObject.trace.insert(0, (i, j))	
								return True
							else:
								pegSolitaireObject.gameState = deepcopy(parentState)
								
		
	return False

# Run Iterative deepening for all possible depths
# Depth possible for our PegSolitaure Puzzle is 32 and Only those marbles can be filled 
# at a time on the board

def ItrDeepSearch(pegSolitaireObject):
	for depth in range(1, 32):
		repeatedStates.clear()
        	rc = DFS(pegSolitaireObject, depth)
        	
		if rc:
			return True
	return False


# Function to fill the trace. This uses a map that has record
# of parent for every child. The function uses bottom top approach
# to fill the trace 

parentRecord	= dict()

def fillTrace(pegSolitaireObject, parentRecord, currentState):

	while currentState in parentRecord:
		parentStateTuple = parentRecord[currentState]
		currentState     = parentStateTuple[0]
		newPos		 = parentStateTuple[1]
		oldPos		 = parentStateTuple[2]
		pegSolitaireObject.trace.insert(0, newPos)
		pegSolitaireObject.trace.insert(0, oldPos)


def aStarOne(pegSolitaireObject):

	# This is the first heursitic. This function calculates Manhattan Distance
	# of each marble on the peg board from the center (3, 3) peg. It then sums up
	# distances of all marbles on the peg. This sum serves has the heursitic.
	# The lesser the sum, more fruitful is the state

	def ManhattanCost(gameState):

		ManDist = 0
		for i in range(7):
			for j in range(7):
				if 1 == gameState[i][j]:
					ManDist = ManDist + abs(i - 3) + abs(j - 3)

		return ManDist

	parentRecord.clear()

	closedList	= list()
	gValue		= dict()
	fValue		= dict()
	
	# Priority Queue to retrive nodes according to their fValue (heursitic + distance from root)

	fringeList	= Q.PriorityQueue()
	
	initGameState 	= pegSolitaireObject.gameState

	gValue[str(initGameState)] = 0

	# Calculate fValue for initial node

	fValue[str(initGameState)] = gValue[str(initGameState)] + ManhattanCost(initGameState)

	fringeList.put((fValue[str(initGameState)], initGameState))
	
	# Keep looking for goal state till fringe list is empty

	while False == fringeList.empty(): 
		
		currentGameState = (deepcopy(fringeList.queue[0]))[1]

		# We found the goal state in the first state itself

		if currentGameState == (deepcopy(pegSolitaireObject.goalState)): 
			return

		# We put it in the list of Closed States which are useless henceforth

		fringeList.get()
		closedList.append(currentGameState)

		pegSolitaireObject.gameState = currentGameState
		
 		# Calculate all neighbours(childs) of a given state and iterate over them
		
		for neighbourRow in pegSolitaireObject.getAllNeighbours():

			neighbour = neighbourRow[0]
			
			# If the neighbour has already been encountered, its useless to use it again

			if neighbour in closedList:
				continue

			# If goal state found, fill the parent record and return
	
			if neighbour == pegSolitaireObject.goalState: 

				parentTuple = (str(currentGameState), (neighbourRow[1]), (neighbourRow[2]))
				childTuple  = (str(neighbour))
				
				parentRecord[childTuple]     = parentTuple
			
				fillTrace(pegSolitaireObject, parentRecord, str(neighbour))

				return

			# calculate distance of the neighbour from the root
		
			neighbourGValue = gValue[str(currentGameState)] + 1
			
			# Check if gValue was not calculated
			# If calculated, it should be less than the present calculated on
				
			priorCheck = False

			if False == gValue.has_key(str(neighbour)) :
				priorCheck = True
			else:
				if neighbourGValue < gValue[str(neighbour)]:
					priorCheck = True


			if neighbour not in list(fringeList.queue) or True == priorCheck:
				# Keep a record of parent state, its child and the movement of peg that produced the child
				# Store this in a hashmap

				parentTuple = (str(currentGameState), (neighbourRow[1]), (neighbourRow[2]))
				childTuple  = (str(neighbour))
				parentRecord[childTuple]     = parentTuple

				# Calculate fValue (heursitic + distance from root for the neighbour

				gValue[str(neighbour)]	     = neighbourGValue
				fValue[str(neighbour)]	     = gValue[str(neighbour)] + ManhattanCost(neighbour)
				
				# if neighbour is not in fringelist, add it

				if neighbour not in list(fringeList.queue):
					fringeList.put((fValue[str(initGameState)], neighbour))
				
	return False


def aStarTwo(pegSolitaireObject):

	
	def NumberofPegsCost(gameState):

		PegCount = 0
		for i in range(7):
			for j in range(7):
				if 1 == gameState[i][j]:
					PegCount = PegCount + 1

		
		tempPegSolitaireObject 		  = deepcopy(pegSolitaireObject)
		tempPegSolitaireObject.gamestate  = gameState

		negativePossiblechilds = 32 - len(tempPegSolitaireObject.getAllNeighbours())

		return PegCount + negativePossiblechilds

	parentRecord.clear()

	closedList	= list()
	gValue		= dict()
	fValue		= dict()
	
	# Priority Queue to retrive nodes according to their fValue (heursitic + distance from root)

	fringeList	= Q.PriorityQueue()
	
	initGameState 	= pegSolitaireObject.gameState

	gValue[str(initGameState)] = 0

	# Calculate fValue for initial node

	fValue[str(initGameState)] = gValue[str(initGameState)] + NumberofPegsCost(initGameState)

	fringeList.put((fValue[str(initGameState)], initGameState))
	
	# Keep looking for goal state till fringe list is empty

	while False == fringeList.empty(): 
		
		currentGameState = (deepcopy(fringeList.queue[0]))[1]

		# We found the goal state in the first state itself

		if currentGameState == (deepcopy(pegSolitaireObject.goalState)): 
			return True

		# We put it in the list of Closed States which are useless henceforth

		fringeList.get()
		closedList.append(currentGameState)

		pegSolitaireObject.gameState = currentGameState
		
 		# Calculate all neighbours(childs) of a given state and iterate over them
		
		for neighbourRow in pegSolitaireObject.getAllNeighbours():

			neighbour = neighbourRow[0]
			
			# If the neighbour has already been encountered, its useless to use it again

			if neighbour in closedList:
				continue

			# If goal state found, fill the parent record and return
	
			if neighbour == pegSolitaireObject.goalState: 

				parentTuple = (str(currentGameState), (neighbourRow[1]), (neighbourRow[2]))
				childTuple  = (str(neighbour))
				
				parentRecord[childTuple]     = parentTuple
			
				fillTrace(pegSolitaireObject, parentRecord, str(neighbour))
				return True

			# calculate distance of the neighbour from the root
		
			neighbourGValue = gValue[str(currentGameState)] + 1
			
			# Check if gValue was not calculated
			# If calculated, it should be less than the present calculated on
				
			priorCheck = False

			if False == gValue.has_key(str(neighbour)) :
				priorCheck = True
			else:
				if neighbourGValue < gValue[str(neighbour)]:
					priorCheck = True


			if neighbour not in list(fringeList.queue) or True == priorCheck:
				# Keep a record of parent state, its child and the movement of peg that produced the child
				# Store this in a hashmap

				parentTuple = (str(currentGameState), (neighbourRow[1]), (neighbourRow[2]))
				childTuple  = (str(neighbour))
				parentRecord[childTuple]     = parentTuple

				# Calculate fValue (heursitic + distance from root for the neighbour

				gValue[str(neighbour)]	     = neighbourGValue
				fValue[str(neighbour)]	     = gValue[str(neighbour)] + NumberofPegsCost(neighbour)
				
				# if neighbour is not in fringelist, add it

				if neighbour not in list(fringeList.queue):
					fringeList.put((fValue[str(initGameState)], neighbour))
	
	return False
