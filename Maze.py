import random

# Shamelessly taken fromm own's project. Full version not here
def CheckNeighborTiles(maze, p, w, h):
    possibleTile = []

    UpT    = {'x': p['x'], 'y': p['y'] - 1}
    DownT  = {'x': p['x'], 'y': p['y'] + 1}
    LeftT  = {'x': p['x'] - 1, 'y': p['y']}
    RightT = {'x': p['x'] + 1, 'y': p['y']}

    if ( UpT['y'] > 0 and maze[ UpT['y'] * 2 - 1 ][ UpT['x'] * 2 - 1 ] == "#"):
        possibleTile.append(UpT)
    if ( DownT['y'] <= h and maze[ DownT['y'] * 2 - 1 ][ DownT['x'] * 2 - 1 ] == "#"):
        possibleTile.append(DownT)
    if ( LeftT['x'] > 0 and maze[ LeftT['y'] * 2 - 1 ][ LeftT['x'] * 2 - 1 ] == "#"):
        possibleTile.append(LeftT)
    if ( RightT['x'] <= w and maze[ RightT['y'] * 2 - 1 ][ RightT['x'] * 2 - 1 ] == "#"):
        possibleTile.append(RightT)

    if len(possibleTile) == 0:
        return p
    else:
        return random.choice(possibleTile)

# Depth-first search algorithm
def CreateASCIIMap(height, width): # This only include moveable line ( # . # . # ) mean a width of 2
    trueW = width * 2 + 1
    trueH = height * 2 + 1

    Maze = [ ['#' for i in range(trueW)] for j in range(trueH) ]

    Path = [] # The Path to backtrack when the miner got to a dead end
    
    Visited = 1 # The Visited Tile, the map is completed when Visited is equal to total tiles (w*h)

    Pos = {'x': random.randint(1, width), 'y': random.randint(1, height)}

    Maze[Pos['y'] * 2 - 1][Pos['x'] * 2 - 1] = "."

    Path.append(Pos) # Add first tile to Path

    while Visited < width * height:
        Next = CheckNeighborTiles(Maze, Pos, width, height) # Check if any possible tile is expandable (not already used)

        if Next == Pos: # No tile available: backtrack to previous tile
            Path.pop()
            Pos = Path[-1]
        else: # tile available: expand, go to new tile, add tile to path to backtrack later
            Maze[Next['y'] * 2 - 1][Next['x'] * 2 - 1] = '.'
            Maze[Next['y'] + Pos['y'] - 1][Next['x'] + Pos['x'] - 1] = '.'
            Path.append(Next)
            Pos = Next
            Visited += 1

    return Maze

def PrintMazeObject(maze):
    for line in maze:
        for c in line:
            print(c, end=" ")
        print()

def ASCIIMapToVertices(maze, startPos, verticesGap):
    # How work: start from a corner (here used top-left corner), check for available route, then prioritize going left
    # Note: a point is a list consisted of 2 value: 1st value for x and 2nd value for y

    verticesAmount = (len(maze) - 1) * (len(maze[0]) - 1)
    verticesVisited = 0

    verticesList = []

    startP = [0, 0]
    r = [0, 0] # runner, short name for easier code
    direction = 1 # Direction: 0. up, 1. right, 2. down, 3. left. This will be used for other direction stuff down the line too

    verticesList.append(r)

    while verticesAmount > verticesVisited:
        # Check all available route
        up = [r[0], r[1] - 1]
        down = [r[0], r[1] + 1]
        left = [r[0] - 1, r[1]]
        right = [r[0] + 1, r[1]]

        available = []

        # 2D Array take thing a little different, since y is basically the first argument instead of the 2nd, so we have to flip thing up

        # check availability of up
        if not direction == 2 and (maze[r[1]][r[0]] == "." or maze[r[1]][r[0] + 1] == '.'):
            available.append(0)

        # check availability of down
        if not direction == 0 and (maze[r[1] + 1][r[0]] == "." or maze[r[1] + 1][r[0] + 1] == '.'):
            available.append(2)

        # check availability of left
        if not direction == 1 and (maze[r[1]][r[0]] == "." or maze[r[1] + 1][r[0]] == '.'):
            available.append(3)

        # check availability of right
        if not direction == 3 and (maze[r[1]][r[0] + 1] == "." or maze[r[1] + 1][r[0] + 1] == '.'):
            available.append(1)

        choosenDir = -1
        priority = 1

        for dir in available:
            if dir == (direction + 3) % 4:
                choosenDir = dir
                priority = 3

            if priority < 3 and dir == direction:
                choosenDir = dir
                priority = 2
            
            if priority < 2 and dir == (direction + 1) % 4:
                choosenDir = dir

        choosenVer = []

        if choosenDir == 0: choosenVer = up
        if choosenDir == 1: choosenVer = right
        if choosenDir == 2: choosenVer = down
        if choosenDir == 3: choosenVer = left

        verticesVisited += 1

        if not direction == choosenDir:
            verticesList.append(r)

        r = choosenVer
        direction = choosenDir

        # Maze not fully filled and runner have comeback to starting point
        if r == startP: break

    # Vertices Gap: 1. Height, 2. Width
    for ver in verticesList:
        ver[0] = ver[0] * verticesGap[1] + startPos[1]
        ver[1] = ver[1] * verticesGap[0] + startPos[0]

    #verticesList.append(verticesList[0])

    return verticesList

# Test run
if __name__ == '__main__':
    maze = CreateASCIIMap(15, 20)

    startPos = [10, 10]
    verticesGap = [15, 15]

    PrintMazeObject(maze)

    vertices = ASCIIMapToVertices(maze, startPos, verticesGap)

    print(vertices)
    print(len(vertices))
