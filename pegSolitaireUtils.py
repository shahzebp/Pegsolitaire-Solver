import readGame
from copy import deepcopy
import numpy as np

class game:
  def __init__(self, filePath):
    self.gameState = readGame.readGameState(filePath)
    self.nodesExpanded = 0
    self.trace = []

    # Define a goal state to keep it handy for comparison

    self.goalState = [[0 for x in range(7)] for x in range(7)]
    self.goalState[3][3] = 1
    for x in range(7):
      for y in range(7):
        if (x < 2 and (y < 2 or y > 4)) or (x > 4 and (y < 2 or y> 4)):
          self.goalState[x][y] = -1

    
  def is_corner(self, pos):
    #Checks if the given position is a corner
    x = pos[0]
    y = pos[1]
    if (x < 2 and (y < 2 or y > 4)) or (x > 4 and (y < 2 or y> 4)):
        return True

    return False

  def getNextPosition(self, oldPos, direction):
  #Gets next move position from old position and given direction
    x = oldPos[0]
    y = oldPos[1]

    if direction == 'N':
        newPos = (x-2, y)
    elif direction == 'S':
        newPos = (x+2, y)
    elif direction == 'E':
        newPos = (x, y+2)
    elif direction == 'W':
        newPos = (x, y-2)
    return newPos


  def getAllNeighbours(self):
    #This functions calculates all possible neighbour gameStates
    #for the current gameState and adds them to a list allNeighbours
    #along with the tuple of old position of i and j and the position after the neighbour is reached
    #The tuple (i,j) and newPosition are used to find trace
    
    allNeighbours = []

    for i in range(7):
      for j in range(7):
        if 1 == self.gameState[i][j] :
          for key in {'N', 'S', 'E', 'W'}:
            if True == self.is_validMove((i, j), key) :
              neighbourRow = []
              modifiedState = self.getNextState((i, j), key)
              newPosition = self.getNextPosition((i, j), key)
              neighbourRow.append(modifiedState)
              neighbourRow.append(newPosition)
              neighbourRow.append((i, j))

              allNeighbours.append(neighbourRow)

    return allNeighbours

  def getImmNewPos(self, oldPos, direction):
    #This function takes oldpos and direction and returns the position
    #of the immidiate next cell to be used for condition checking
    x = oldPos[0]
    y = oldPos[1]

    if direction == 'N':
        x = x-1
    elif direction == 'S':
        x = x+1
    elif direction == 'E':
        y = y+1
    elif direction == 'W':
        y = y-1

    immPos = (x,y)
    return immPos

  def is_validMove(self, oldPos, direction):
  	#This function returns a boolean based deciding if
	  #there is a valid move possible for a peg in given position
  	#and direction
      newPos = self.getNextPosition(oldPos, direction)
      
      if self.is_corner(newPos):
          return False

      x = newPos[0]
      y = newPos[1]

      #out of board
      if x > 6 or y > 6 or x < 0 or y < 0:
          return False

      #move is occupied
      if self.gameState[x][y] == 1:
          return False

      #in between oldPos and newPos must be occupied
      immPos = self.getImmNewPos(oldPos, direction)

      x = immPos[0]
      y = immPos[1]

      if self.gameState[x][y] != 1:
          return False

      return True

  def getNextState(self, oldPos, direction):
	  #This function returns the next gameState based upon the
  	#predecided valid move
    
    self.nodesExpanded += 1
    
    if not self.is_validMove(oldPos, direction):
      print "Error, You are not checking for valid move"
      exit(0)

    #since we are here, move is valid
    #create a copy of gamestate matrix

    copyGameState = deepcopy(self.gameState)

    #make old position 0
    x = oldPos[0]
    y = oldPos[1]

    copyGameState[x][y] = 0

    #update removed peg with 0
    removePos = self.getImmNewPos(oldPos, direction)
    x = removePos[0]
    y = removePos[1]

    if copyGameState[x][y] != 1:
      print("something went wrong, removed peg should always be 1")
    copyGameState[x][y] = 0

    #update new position with 1
    newPos = self.getNextPosition(oldPos, direction)
    x = newPos[0]
    y = newPos[1]

    copyGameState[x][y] = 1

    return copyGameState
