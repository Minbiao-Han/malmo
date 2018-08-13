# Created by Roman Sharykin

from __future__ import print_function
from __future__ import division

from builtins import range
from past.utils import old_div
import MalmoPython
import json
import logging
import math
import os
import random
import sys
import time
import re
import uuid
from collections import namedtuple
from operator import add
import random
from random import *

EntityInfo = namedtuple('EntityInfo', 'x, y, z, name')

# Create one agent host for parsing:
agent_hosts = [MalmoPython.AgentHost()]

# Parse the command-line options:
agent_hosts[0].addOptionalFlag( "debug,d", "Display debug information.")
agent_hosts[0].addOptionalIntArgument("agents,n", "Number of agents to use, including observer.", 3)

try:
    agent_hosts[0].parse( sys.argv )
except RuntimeError as e:
    print('ERROR:',e)
    print(agent_hosts[0].getUsage())
    exit(1)
if agent_hosts[0].receivedArgument("help"):
    print(agent_hosts[0].getUsage())
    exit(0)

DEBUG = agent_hosts[0].receivedArgument("debug")
INTEGRATION_TEST_MODE = agent_hosts[0].receivedArgument("test")
agents_requested = agent_hosts[0].getIntArgument("agents")
NUM_AGENTS = max(1, agents_requested - 1) # Will be NUM_AGENTS robots running around, plus one static observer.

# Create the rest of the agent hosts - one for each robot, plus one to give a bird's-eye view:
agent_hosts += [MalmoPython.AgentHost() for x in range(1, NUM_AGENTS + 1) ]

# Set up debug output:
for ah in agent_hosts:
    ah.setDebugOutput(DEBUG)    # Turn client-pool connection messages on/off.

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools
    print = functools.partial(print, flush=True)


def safeStartMission(agent_host, my_mission, my_client_pool, my_mission_record, role, expId):
    used_attempts = 0
    max_attempts = 5
    print("Calling startMission for role", role)
    while True:
        try:
            # Attempt start:
            agent_host.startMission(my_mission, my_client_pool, my_mission_record, role, expId)
            break
        except MalmoPython.MissionException as e:
            errorCode = e.details.errorCode
            if errorCode == MalmoPython.MissionErrorCode.MISSION_SERVER_WARMING_UP:
                print("Server not quite ready yet - waiting...")
                time.sleep(2)
            elif errorCode == MalmoPython.MissionErrorCode.MISSION_INSUFFICIENT_CLIENTS_AVAILABLE:
                print("Not enough available Minecraft instances running.")
                used_attempts += 1
                if used_attempts < max_attempts:
                    print("Will wait in case they are starting up.", max_attempts - used_attempts, "attempts left.")
                    time.sleep(2)
            elif errorCode == MalmoPython.MissionErrorCode.MISSION_SERVER_NOT_FOUND:
                print("Server not found - has the mission with role 0 been started yet?")
                used_attempts += 1
                if used_attempts < max_attempts:
                    print("Will wait and retry.", max_attempts - used_attempts, "attempts left.")
                    time.sleep(2)
            else:
                print("Other error:", e.message)
                print("Waiting will not help here - bailing immediately.")
                exit(1)
        if used_attempts == max_attempts:
            print("All chances used up - bailing now.")
            exit(1)
    print("startMission called okay.")

def safeWaitForStart(agent_hosts):
    print("Waiting for the mission to start", end=' ')
    start_flags = [False for a in agent_hosts]
    start_time = time.time()
    time_out = 120  # Allow a two minute timeout.
    while not all(start_flags) and time.time() - start_time < time_out:
        states = [a.peekWorldState() for a in agent_hosts]
        start_flags = [w.has_mission_begun for w in states]
        errors = [e for w in states for e in w.errors]
        if len(errors) > 0:
            print("Errors waiting for mission start:")
            for e in errors:
                print(e.text)
            print("Bailing now.")
            exit(1)
        time.sleep(0.1)
        print(".", end=' ')
    if time.time() - start_time >= time_out:
        print("Timed out while waiting for mission to start - bailing.")
        exit(1)
    print()
    print("Mission has started.")


def moveRight(ah):
    ah.sendCommand("strafe 1")
    time.sleep(0.2)


def moveLeft(ah):
    ah.sendCommand("strafe -1")
    time.sleep(0.2)


def moveStraight(ah):
    ah.sendCommand("move 1")
    time.sleep(0.2)


def moveBack(ah):
    ah.sendCommand("move -1")
    time.sleep(0.2)


def enemyAgentMove(agent, ws):
    illegal = legalMoves(ws)
    legal = ['right', 'left', 'forward', 'back']
    for i in illegal:
        if i in legal:
            legal.remove(i)

    x = legal[randrange(len(legal))]
    if x == "right":
        moveRight(agent)
    elif x == "left":
        moveLeft(agent)
    elif x == "forward":
        moveStraight(agent)
    else:
        moveBack(agent)


def legalMoves(world_state):
    blocks = []
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        observations = json.loads(msg)
        grid = observations.get(u'floor3x3W', 0)
        if grid[3] == u'diamond_block':
            blocks.append("right")
        if grid[1] == u'diamond_block':
            blocks.append("back")
        if grid[5] == u'diamond_block':
            blocks.append("left")
        if grid[7] == u'diamond_block':
            blocks.append("forward")

        return blocks

def manhattan_distance(start, end):
    sx, sy = start
    ex, ey = end
    return abs(ex - sx) + abs(ey - sy)

def evalfuncReflex(pos):
    if pos == (eCurr['x'], eCurr['z']):
        return(-100000)
    else:
        enemydist = manhattan_distance(pos, (eCurr['x'], eCurr['z']))
        escore = -10/enemydist
        closestfood = min([manhattan_distance(pos, i) for i in food])
        return(-2 * closestfood) + escore - (100 * len(food))


def reflexAgentMove(agent, pos, wstate):
     illegalgrid = legalMoves(wstate)
     dirscores = []
     scores = []
     if "left" not in illegalgrid:
         score = evalfuncReflex((pos[0]+1, pos[1]))
         scores.append(score)
         dirscores.append(('left', evalfuncReflex((pos[0]+1, pos[1]))))
     if "forward" not in illegalgrid:
         score = evalfuncReflex((pos[0], pos[1] + 1))
         scores.append(score)
         dirscores.append(('forward', evalfuncReflex((pos[0], pos[1]+1))))
     if "right" not in illegalgrid:
         score = evalfuncReflex((pos[0]-1, pos[1]))
         scores.append(score)
         dirscores.append(('right', evalfuncReflex((pos[0]-1, pos[1]))))
     if "back" not in illegalgrid:
         score = evalfuncReflex((pos[0], pos[1]-1))
         scores.append(score)
         dirscores.append(('back', score))
     togo = max(scores)
     togolst = []
     for i in dirscores:
         if i[1] == togo:
             togolst.append(i)

     lengo = len(togolst) -1

     rand = randint(0, lengo)
     togo = togolst[rand]

     if togo[0] == "right":
         moveRight(agent)
     elif togo[0] == "left":
         moveLeft(agent)
     elif togo[0] == "forward":
         moveStraight(agent)
     elif togo[0] == "back":
         moveBack(agent)


def getLayout(name):
    matrix = tryToLoad("../layouts/" + name)
    return matrix

def tryToLoad(fullname):
    if (not os.path.exists(fullname)): return None
    f = open(fullname)
    Matrix = [line.strip() for line in f]
    f.close()
    return Matrix

level_mat = getLayout("smallClassic.lay")

def drawItems():
    xml = ""
    for i in range(NUM_ITEMS):
        x = str(random.randint(-17,17))
        z = str(random.randint(-17,17))
        xml += '<DrawItem x="' + x + '" y="224" z="' + z + '" type="apple"/>'
    return xml

def GenBlock(x, y, z, blocktype):
    return '<DrawBlock x="' + str(x) + '" y="' + str(y) + '" z="' + str(z) + '" type="' + blocktype + '"/>'

def GenPlayerStart(x, z):
    return '<Placement x="' + str(x + 0.5) + '" y="56" z="' + str(z + 0.5) + '" yaw="0"/>'

def GenEnemyStart(x, z):
    return '<Placement x="' + str(x + 0.5) + '" y="56" z="' + str(z + 0.5) + '" yaw="0"/>'

pStart = {'x': 0, 'z': 0}
eStart = {'x': 0, 'z': 0}

pCurr = {'x': 0, 'z': 0}
eCurr = {'x': 0, 'z': 0}

food = []

def mazeCreator():
    genstring = ""
    genstring += GenBlock(5, 75, 10, "glass") + "\n"
    for i in range(len(level_mat)):
        for j in range(len(level_mat[0])):

            if level_mat[i][j] == "%":
                genstring += GenBlock(i, 54, j, "diamond_block") + "\n"
                genstring += GenBlock(i, 55, j, "diamond_block") + "\n"
                genstring += GenBlock(i, 56, j, "diamond_block") + "\n"

            elif level_mat[i][j] == "P":
                pStart['x'] = i
                pStart['z'] = j
                pCurr['x'] = i
                pCurr['z'] = j

            elif level_mat[i][j] == ".":
                genstring += GenBlock(i, 55, j, "glowstone") + "\n"
                food.append((i, j))

            elif level_mat[i][j] == "G":
                eStart['x'] = i
                eStart['z'] = j
                eCurr['x'] = i
                eCurr['z'] = j

    return genstring

def invMake():
    xml = ""
    for i in range(0, 39):
        xml += '<InventoryObject type="diamond_axe" slot="' + str(i) + '" quantity="1"/>'
    return(xml)

def getXML(reset):
    # Set up the Mission XML:
    xml = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
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
                <Name>Player</Name>
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
              <AgentSection mode="Survival">
                <Name>Enemy</Name>
                <AgentStart> 
                '''   + GenEnemyStart(eStart['x'], eStart['z']) +  ''' 
                <Inventory>''' + invMake() + '''</Inventory>
                </AgentStart>
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
              </AgentSection>'''


    xml += '''<AgentSection mode="Creative">
        <Name>TheWatcher</Name>
        <AgentStart>
          <Placement x="5.5" y="76" z="10.5" pitch="90"/>
        </AgentStart>
        <AgentHandlers>
          <ContinuousMovementCommands turnSpeedDegs="360"/>
          <MissionQuitCommands/>
          <VideoProducer>
            <Width>640</Width>
            <Height>640</Height>
          </VideoProducer>
        </AgentHandlers>
      </AgentSection>'''

    xml += '</Mission>'
    return xml

client_pool = MalmoPython.ClientPool()
for x in range(10001, 10001 + NUM_AGENTS + 1):
    client_pool.add( MalmoPython.ClientInfo('127.0.0.1', x) )


print("Running mission")
# Create mission xml - use forcereset if this is the first mission.
my_mission = MalmoPython.MissionSpec(getXML("true"), True)

experimentID = str(uuid.uuid4())

for i in range(len(agent_hosts)):
    safeStartMission(agent_hosts[i], my_mission, client_pool, MalmoPython.MissionRecordSpec(), i, experimentID)

safeWaitForStart(agent_hosts)

time.sleep(1)
running = True

current_pos = [(0,0) for x in range(NUM_AGENTS)]
# When an agent is killed, it stops getting observations etc. Track this, so we know when to bail.

timed_out = False
g_score = 0
while not timed_out and food:
    for i in range(NUM_AGENTS):
        ah = agent_hosts[i]
        world_state = ah.getWorldState()
        if world_state.is_mission_running == False:
            timed_out = True
        if world_state.is_mission_running and world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text
            ob = json.loads(msg)

            if "XPos" in ob and "ZPos" in ob:
                current_pos[i] = (ob[u'XPos'], ob[u'ZPos'])
                #print(current_pos[i])
            if ob['Name'] == 'Enemy':
                enemyAgentMove(ah, world_state)
                eCurr['x'] = current_pos[i][0]
                eCurr['z'] = current_pos[i][1]
                if (current_pos[i] == (pCurr['x'], pCurr['z'])):
                    g_score -= 100
                    timed_out = True
                    break

            if ob['Name'] == 'Player':
                if((current_pos[i][0]-0.5,current_pos[i][1]-0.5) in food):
                    print("Food found!")
                    food.remove((current_pos[i][0]-0.5,current_pos[i][1]-0.5))
                    g_score += 10
                if(current_pos[i] == (eCurr['x'], eCurr['z'])):
                    g_score -= 100
                    timed_out = True
                    break
                reflexAgentMove(ah, current_pos[i], world_state)
                pCurr['x'] = current_pos[i][0]
                pCurr['z'] = current_pos[i][1]
                grid = ob.get(u'floor3x3W', 0)

    time.sleep(0.05)
print(food)
print(g_score)

print("Waiting for mission to end ", end=' ')
# Mission should have ended already, but we want to wait until all the various agent hosts
# have had a chance to respond to their mission ended message.
hasEnded = True
while not hasEnded:
    hasEnded = True # assume all good
    print(".", end="")
    time.sleep(0.1)
    for ah in agent_hosts:
        world_state = ah.getWorldState()
        if world_state.is_mission_running:
            hasEnded = False # all not good


time.sleep(2)