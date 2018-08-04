from __future__ import print_function

# Minbiao Han and Roman Sharykin
# AI fall 2018

from builtins import range
import MalmoPython
import os
import sys
import time
import json
import sys

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools

    print = functools.partial(print, flush=True)


def getLayout(name):
    matrix = tryToLoad("layouts/" + name)
    return matrix


def tryToLoad(fullname):
    if (not os.path.exists(fullname)): return None
    f = open(fullname)
    Matrix = [line.strip() for line in f]
    f.close()
    return Matrix


level_mat = getLayout("bigMaze.lay")

def GenBlock(x, y, z, blocktype):
    return '<DrawBlock x="' + str(x) + '" y="' + str(y) + '" z="' + str(z) + '" type="' + blocktype + '"/>'

def GenPlayerStart(x, z):
    return '<Placement x="' + str(x + 0.5) + '" y="56" z="' + str(z + 0.5) + '" yaw="0"/>'

pStart = {'x': 0, 'z': 0}
pEnd = {'x': 0, 'z': 0}

def mazeCreator():
    genstring = ""
    for i in range(len(level_mat)):
        for j in range(len(level_mat[0])):

            if level_mat[i][j] == "%":
                genstring += GenBlock(i, 54, j, "diamond_block") + "\n"
                genstring += GenBlock(i, 55, j, "diamond_block") + "\n"
                genstring += GenBlock(i, 56, j, "diamond_block") + "\n"

            elif level_mat[i][j] == "P":
                pStart['x'] = i
                pStart['z'] = j

            elif level_mat[i][j] == ".":
                genstring += GenBlock(i, 55, j, "glowstone") + "\n"
                pEnd['x'] = i
                pEnd['z'] = j

    return genstring


missionXML = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
              <About>
                <Summary>Hello world!</Summary>
              </About>

              <ServerSection>
                <ServerHandlers>
                  <FlatWorldGenerator generatorString="3;7,44*49,73,35:1,159:4,95:13,35:13,159:11,95:10,159:14,159:6,35:6,95:6;12;"/>
                  <DrawingDecorator>
                    ''' + mazeCreator() + '''
                  </DrawingDecorator>
                  <ServerQuitFromTimeUp timeLimitMs="45000"/>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>

              <AgentSection mode="Survival">
                <Name>MalmoTutorialBot</Name>
                <AgentStart> '''   + GenPlayerStart(pStart['x'], pStart['z']) +  ''' </AgentStart>
                <AgentHandlers>
                  <DiscreteMovementCommands/>
                  <ObservationFromFullStats/>
                  <ObservationFromGrid>
                      <Grid name="floor3x3W">
                        <min x="-1" y="0" z="-1"/>
                        <max x="1" y="0" z="1"/>
                      </Grid>
                      <Grid name="floor3x3F">
                        <min x="-1" y="-1" z="-1"/>
                        <max x="1" y="-1" z="1"/>
                      </Grid>
                  </ObservationFromGrid>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''

# Create default Malmo objects:

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse(sys.argv)
except RuntimeError as e:
    print('ERROR:', e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)

def moveRight():
    agent_host.sendCommand("strafe 1")
    time.sleep(0.2)
    #print("moving right")


def moveLeft():
    agent_host.sendCommand("strafe -1")
    time.sleep(0.2)
    #print("moving left")

def moveStraight():
    agent_host.sendCommand("move 1")
    time.sleep(0.2)
    #print("moving straight")


def moveBack():
    agent_host.sendCommand("move -1")
    time.sleep(0.2)
    #print("moving backwards")




def isWallAhead(world_state):
    blocks = {'N': 0, 'E': 0, 'S': 0, 'W': 0}
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        observations = json.loads(msg)
        grid = observations.get(u'floor3x3W', 0)

        if grid[3]==u'diamond_block':
            blocks['N'] = 1
        if grid[1]==u'diamond_block':
            blocks['E'] = 1
        if grid[5]==u'diamond_block':
            blocks['S'] = 1
        if grid[7]==u'diamond_block':
            blocks['W'] = 1

        return grid

def isGoalReached(world_state):
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        observations = json.loads(msg)
        grid = observations.get(u'floor3x3F', 0)
        if grid[4]==u'glowstone':
            return True
        else:
            return False

basic_operations = 0

def BFS(maze, start, end):

    queue = [start]
    visited = set()

    while len(queue) != 0:
        if queue[0] == start:
            path = [queue.pop(0)]  # Required due to a quirk with tuples in Python
        else:
            path = queue.pop(0)
        front = path[-1]
        if front == end:
            return path
        elif front not in visited:
            for adjacentSpace in getAdjacentSpaces(maze, front, visited):
                newPath = list(path)
                newPath.append(adjacentSpace)
                queue.append(newPath)
                global basic_operations
                basic_operations += 1
            visited.add(front)
    return None


def getAdjacentSpaces(maze, space, visited):
    spaces = list()
    spaces.append((space[0]-1, space[1]))  # Up
    spaces.append((space[0]+1, space[1]))  # Down
    spaces.append((space[0], space[1]-1))  # Left
    spaces.append((space[0], space[1]+1))  # Right

    final = list()
    for i in spaces:
        if maze[i[0]][i[1]] != '%' and i not in visited:
            final.append(i)
    return final

my_mission = MalmoPython.MissionSpec(missionXML, True)
my_mission_record = MalmoPython.MissionRecordSpec()

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        agent_host.startMission(my_mission, my_mission_record)
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print("Error starting mission:", e)
            exit(1)
        else:
            time.sleep(2)

# Loop until mission starts:
print("Waiting for the mission to start ", end=' ')
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:", error.text)

print()
print("Mission running ", end=' ')

print(pStart)

#path = [(3, 11), (3, 12), (3, 13), (4, 13), (5, 13), (5, 12), (6, 12), (7, 12), (7, 11), (7, 10), (8, 10), (8, 9), (8, 8), (8, 7), (8, 6), (8,5), (8,4), (8,3), (8,2), (8,1)]
path = BFS(level_mat, (pStart['x'], pStart['z']), (pEnd['x'], pEnd['z']))

while len(path) != 1:
    point = path.pop(0)
    x_cur = point[0]
    y_cur = point[1]
    next = path[0]

    if(x_cur == next[0] and y_cur == (next[1] - 1)):
        moveStraight()

    elif (x_cur == next[0] and y_cur == (next[1] + 1)):
        moveBack()

    elif (x_cur == (next[0] - 1) and y_cur == next[1]):
        moveLeft()

    elif (x_cur == (next[0] + 1) and y_cur == next[1]):
        moveRight()

    else:
        print("current: " + str(point))
        print("next: " + str(next))
        print("The path you entered is not continuous. Please fix your path input and try again.")
        break


while world_state.is_mission_running:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    if(isGoalReached(world_state)):
        break



print()
print("Mission ended")
# Mission has ended.
