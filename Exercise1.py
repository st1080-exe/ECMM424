# ECMM424 ASSESSMENT
# Exercise 1: M/M/C/C queuing system
# Code based off of work done for workshops week 3 - 5
# As well as pseudo code from leactures 5 and 6

import math
import numpy
import random
import matplotlib.pyplot as plt

# vars
# all time is measured in seconds
simTime = 0
timeLastEvent = 0

nextEventSlot = 0
totalServerUtil = 0
totalLoss = 0
customerNum = 0
meanInterval = 0
meanService = 0
serverNum = 0
numOfRuns = 0
serverStatus = 0
areaServerStatus = 0
timeNextEvent = 0
serverUtil = 0


# main
def main(customersTotal, meanIntervalTime, meanServiceTime, numOfServers):

    # sets up variables
    init(customersTotal, meanIntervalTime, meanServiceTime, numOfServers)

    # sets up first arrival event
    timeNextEvent[0] = simTime + randExpnt(meanIntervalTime)

    # runs sim for required customer amount
    while(customerNum < numOfRuns):

        # fastforwards sim to next event
        timing()

        # updates sim time and server statuses
        updateStats()

        #if the next event is an arrival puts another customer in q
        # cutomer count only goes up on an arrival
        if(nextEventSlot == 0):
            arrive()
        # else: depart customer
        else:
            depart()

    return report()

# sets up variables according to simulation set up
def init(customersTotal, meanIntervalTime, meanServiceTime, numOfServers):

    global meanInterval, meanService, serverNum, numOfRuns
    global serverStatus, areaServerStatus, timeNextEvent, serverUtil
    global simTime, timeLastEvent, nextEventSlot, totalLoss, customerNum, totalServerUtil

    # reset state of the sim
    simTime = 0
    timeLastEvent = 0
    nextEventSlot = 0
    totalLoss = 0
    customerNum = 0
    totalServerUtil = 0

    meanInterval = meanIntervalTime
    meanService = meanServiceTime
    serverNum = numOfServers
    numOfRuns = customersTotal

    # fills the arrays with num of servers
    # arrays with a +1 leave a slot open for arrivals
    serverStatus = numpy.zeros(serverNum + 1)
    areaServerStatus = numpy.zeros(serverNum)
    timeNextEvent = numpy.full(serverNum + 1, 1000000000)
    serverUtil = numpy.zeros(serverNum)


# fast-forwards the sim time to when the next earliest event occurs
def timing():

    global simTime, timeLastEvent, nextEventSlot

    # picks the first event to happen
    nextEventSlot = int(numpy.argmin(timeNextEvent))
    timeLastEvent = simTime

    # fast fowards sim time to the chosen event
    simTime = timeNextEvent[nextEventSlot]

# updates the sim
def updateStats():

    #updates time
    timePast = simTime - timeLastEvent

    # updates server total time
    for i in range(serverNum):
        areaServerStatus[i] += (timePast * serverStatus[i+1])

# cutomer arrival function
def arrive():

    global totalLoss, customerNum

    # arrival event
    timeNextEvent[0] = simTime + randExpnt(meanInterval)

    serverIdle = 0
    #finds first free server
    # starts at 1 since 0 is the customer arrival index
    for i in range(serverNum):
        if(serverStatus[i+1] == 0):
            serverIdle = i+1
            break

    # if a free server is found it queues an event in their slot
    if(serverIdle != 0):
        serverStatus[serverIdle] = 1
        timeNextEvent[serverIdle] = simTime + randExpnt(meanService)

    # if not the customer "leaves"
    else:
        totalLoss += 1

    customerNum += 1


# when customer leaves
def depart():

    # sets server to free
    serverStatus[nextEventSlot] = 0

    # resets slot for next run
    timeNextEvent[nextEventSlot] = 100000000

# picks a random number based on the given exponent graph
def randExpnt(average):
    num = -(average * math.log(random.random()))
    return num

# erlang b function
# code taken from https://en.wikipedia.org/wiki/Erlang_(unit)#Erlang_B_formula
def erlangB(E, m):
    invB = 1.0
    for i in range(1, m + 1):
        invB = 1.0 + invB * (i/E)
    return (1.0 / invB)

# returns a report based on findings
def report():

    global serverUtil, totalServerUtil

    # how busy the server was
    # takes server occupation time and total sim time for each server
    serverUtil = areaServerStatus / simTime

    # gets average of all servers
    totalServerUtil = serverUtil.sum() / serverNum

    # hypothetical server load if we had infinite servers
    hypotheticalLoad = (1/meanInterval) / (1/meanService)

    # code taken from https://en.wikipedia.org/wiki/Erlang_(unit)#Erlang_B_formula
    lossProbability = erlangB(hypotheticalLoad, serverNum)

    # theoretical server util
    theoryUtil = (hypotheticalLoad / serverNum) * (1 - lossProbability)

    # calls lost per calls taken
    simLoss = totalLoss / numOfRuns

    return simLoss, totalServerUtil, lossProbability, theoryUtil



# main simulation run loop

# sets seed for random
random.seed(20)

# parameters laid out in assignment
CELL_SERVERS = 16
AVERAGE_LEN = 100
CALLS_PER_RUN = 100000

# arrival rate range
# splits into 19 runs
arrivalRates = numpy.arange(0.01, 0.1001, 0.005)

# list of vars
blockedCalls = []
serverUtilization = []
theoreticalLoss = []
theoreticalUtility = []

# runs the sim for each arrival rate
for i in range(len(arrivalRates)):

    # runs the sim based on the given arrival rate
    bC, sU, tL, tU = main(CALLS_PER_RUN, 1 / arrivalRates[i], AVERAGE_LEN, CELL_SERVERS)

    # adds stats to list
    blockedCalls.append(bC)
    serverUtilization.append(sU)
    theoreticalLoss.append(tL)
    theoreticalUtility.append(tU)

    print(f"""
    Arrival Rate: {arrivalRates[i]}
    Blcoked Calls: {bC}
    Server Utilization: {sU}
    Theoretical Loss: {tL}
    Theoretical Utility: {tU}
          """)



# figures for question 1.2

# blocking probability
plt.figure(figsize = (8, 5))

# simualtion values
plt.plot(arrivalRates, blockedCalls, '-', label = "Simulation")

# theorietical
plt.plot(arrivalRates, theoreticalLoss, '-', label = "Theoretical=")

#labels
plt.xlabel("Arrival rate")
plt.ylabel("Blocking probability")
plt.title("Blocking probability on different arrival rates")


plt.grid(True, alpha = 0.5)
plt.legend()

plt.savefig('penis.png', dpi=150)

# server util
plt.figure(figsize = (8, 5))

#simulation values
plt.plot(arrivalRates, serverUtilization, '-', label = "Simulation")

# theoretical values
plt.plot(arrivalRates, theoreticalUtility, '-', label = "Theoretical")


plt.xlabel("Arrival rate")
plt.ylabel("Server utilization")
plt.title("Server utilization on different arrival rates")

plt.grid(True, alpha = 0.5)
plt.legend()

plt.savefig('server_utilization.png', dpi=150)

plt.show()

# function for question 1.3
def maxRateForBlocking(target, serverNum, meanServiceTime):

    # sets search range
    minVal = 0.0001
    maxVal = 0.5

    # arbitrary search breadth
    # to be changed
    for i in range(50):

        # gets middle point of min and max
        mid = (minVal + maxVal) / 2

        # if its under the target, decrease range by moving min up to the middle point
        if erlangB(mid * meanServiceTime, serverNum) < target:
            minVal = mid

        # if its over move the max down to mid
        else:
            maxVal = mid
            
    return minVal


maxArrivalRate = maxRateForBlocking(0.01, CELL_SERVERS, AVERAGE_LEN)

print(f"Maximum value for arrival rates so that the blocking probability is <0.01 is {maxArrivalRate}")