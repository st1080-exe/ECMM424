# ECMM424 ASSESSMENT
# Exercise 2: M1+M2/M/C/C queuing system
# Code modified from exercise 1
# As well as pseudo code from leacture 6
# Any further referrences will be cited in comments

import math
import numpy
import random
import matplotlib.pyplot as plt

#vars
# time measured in seconds
simTime = 0
timeLastEvent = 0

nextEventSlot = 0
totalServerUtil = 0
callLost = 0
handoverLost = 0

customerNum = 0
newCallArrival = 0
handoverArrival = 0

meanInterval = 0
meanHandoverInterval = 0
meanService = 0
serverNum = 0
numOfRuns = 0
threshold = 0

serverStatus = 0
areaServerStatus = 0
timeNextEvent = 0
serverUtil = 0



# main
def main(customersTotal, meanIntervalTime, meanHandoverTime, meanServiceTime, numOfServers, thresholdValue):

    # sets up variables
    init(customersTotal, meanIntervalTime, meanHandoverTime, meanServiceTime, numOfServers, thresholdValue)

    # sets up first arrival and handover event
    timeNextEvent[0] = simTime + randExpnt(meanInterval)
    timeNextEvent[1] = simTime + randExpnt(meanHandoverInterval)

    # runs sim for required customer amount
    while(customerNum < numOfRuns):

        # fastforwards sim to next event
        timing()

        # updates sim time and server statuses
        updateStats()

        #if the next event is an arrival puts another customer in q
        # cutomer count only goes up on an arrival
        if(nextEventSlot < 2):
            arrive()
        # else: depart customer
        else:
            depart()

    return report()

# sets up vars according to sim set up
def init(customersTotal, meanIntervalTime, meanHandoverTime, meanServiceTime, numOfServers, thresholdValue):

    global meanInterval, meanHandoverInterval, meanService, serverNum, numOfRuns, threshold
    global serverStatus, areaServerStatus, timeNextEvent, serverUtil
    global simTime, timeLastEvent, nextEventSlot, totalServerUtil
    global customerNum, newCallArrival, handoverArrival, callLoss, handoverLoss

    # reset state of the sim
    simTime = 0
    timeLastEvent = 0
    nextEventSlot = 0
    callLoss = 0
    handoverLoss = 0
    customerNum = 0
    totalServerUtil = 0
    newCallArrival = 0
    handoverArrival = 0

    meanInterval = meanIntervalTime
    meanHandoverInterval = meanHandoverTime
    meanService = meanServiceTime
    serverNum = numOfServers
    numOfRuns = customersTotal
    threshold = thresholdValue

    # fills the arrays with num of servers
    # arrays with a +2 leave a slot open for arrivals and handovers
    serverStatus = numpy.zeros(serverNum + 2)
    areaServerStatus = numpy.zeros(serverNum)
    timeNextEvent = numpy.full(serverNum + 2, 100000000)
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
        areaServerStatus[i] += (timePast * serverStatus[i+2])

# cutomer arrival function
def arrive():

    global customerNum, newCallArrival, handoverArrival, callLoss, handoverLoss

    # adds customer to total
    customerNum += 1

    # schedule the next arrival of the same kind
    # 0 is the call slot and 1 is the handover slot
    if nextEventSlot == 0:
        newCallArrival += 1
        timeNextEvent[0] = simTime + randExpnt(meanInterval)
    else:
        handoverArrival += 1
        timeNextEvent[1] = simTime + randExpnt(meanHandoverInterval)

    # finds first free servers and counts idle servers
    # starts at 2 since first 2 slots are arrival and handover

    serverIdle = 0
    serverIdleNum = 0

    for i in range(serverNum):

        if serverStatus[i + 2] == 0:
            serverIdleNum += 1

            if serverIdle == 0:
                serverIdle = i + 2

    # stored in vars to avoid too much nesting

    # event slot 0 is main call stream and slot 1 is handover
    # call accepted into main stream if the threshold of idle servers is met
    if nextEventSlot == 0:
        accepted = serverIdleNum > threshold

    # call accepted into handover if there is an idle server
    else:
        accepted = serverIdleNum > 0

    # if call taken
    if accepted:
        # set server to busy and set call duration
        serverStatus[serverIdle] = 1
        timeNextEvent[serverIdle] = simTime + randExpnt(meanService)
    else:
        # if cant take call tally the loss
        if nextEventSlot == 0:
            callLoss += 1
        else:
            handoverLoss += 1


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

def report():

    global serverUtil, totalServerUtil

    # how busy the server was
    # takes server occupation time and total sim time for each server
    serverUtil = areaServerStatus / simTime

    # gets average of all servers
    totalServerUtil = serverUtil.sum() / serverNum

    # fraction of calls that were blocked
    callBlockChance = callLoss / newCallArrival
    handoverBlockChance = handoverLoss / handoverArrival


    return callBlockChance, handoverBlockChance

# single sim run
# random.seed(20)

# call = 0
# handover = 0

# call, handover = main(100000, 1/ 0.05, 1/0.02, 100, 16,2)

# print(f"""
# Call block prob: {call}
# handover block prob: {handover}
# server ulti: {totalServerUtil}
# """)

# question 2.2
#finds the maximum handover rate where the aggrevated blockiing probability is less than the given rate
# tries 100 random handover rates between 0 and and the given rate
def handoverRateTrial(callRate, customersTotal, numPoints):

    # fixed settings for this experiment
    callDuration = 100
    servers = 16
    thresholdValue = 2

    # sorted rates so theyre searched in increasing order
    handoverRates = sorted(random.uniform(0, 0.2) for i in range(numPoints))

    # returns none if none are found
    maxRate = None
    abps = []
    cbps = []
    hbps = []

    for i in range(len(handoverRates)):

        callBlockProb, handoverBlockProb = main(customersTotal, 1 / callRate, 1 / handoverRates[i], callDuration, servers, thresholdValue)

        # equation from assignment brief
        aggregatedBlockingProb = callBlockProb + (10 * handoverBlockProb)

        if aggregatedBlockingProb < 0.02:
            maxRate = handoverRates[i]

        abps.append(aggregatedBlockingProb)
        cbps.append(callBlockProb)
        hbps.append(handoverBlockProb)

    print(f"Max handover where aggregates blocking probability < 0.02: {maxRate}")
    return maxRate, abps, cbps, hbps, handoverRates

# question 2.3
# finds the maximum new call rate where aggrevated blockiing probability is less than the given rate
# modified version of the above function
def callRateTrial(handoverRate, customersTotal, numPoints):

    # fixed settings for this experiment
    callDuration = 100
    servers = 16
    thresholdValue = 2

    # sorted rates so theyre searched in increasing order
    callRates = sorted(random.uniform(0, 0.1) for i in range(numPoints))

    # returns none if none are found
    maxRate = None
    abps = []
    cbps = []
    hbps = []

    for i in range (len(callRates)):

        # main wants mean times between arrivals, so rates are turned into 1 / rate
        callBlockProb, handoverBlockProb = main(customersTotal, 1 / callRates[i], 1 / handoverRate, callDuration, servers, thresholdValue)

        # equation from assignment brief
        aggregatedBlockProb = callBlockProb + (10 * handoverBlockProb)

        if aggregatedBlockProb < 0.02:
            maxRate = callRates[i]

        abps.append(aggregatedBlockProb)
        cbps.append(callBlockProb)
        hbps.append(handoverBlockProb)

    print(f"Max new call rate where aggregates blocking probability < 0.02: {maxRate}")
    return maxRate, abps, cbps, hbps, callRates

# runs simulations
random.seed(20)

numTrials = 10

# sims for 2.2
foundRates = []
lowestABP = 1000

for i in range(numTrials):
    maxRate, abps, cbps, hbps, handoverRates = handoverRateTrial(0.1, 100000, 100)

    if maxRate is not None:
        foundRates.append(maxRate)

    lowestABP = min(lowestABP, min(abps))

if len(foundRates) > 0:
    print(f"max handover rate found: {max(foundRates)}. average: {sum(foundRates) / len(foundRates)}")
else:
    print("no handover rates less than 0.2 found")


# sims for 2.3
foundRates = []
for i in range(numTrials):
    maxRate, abps, cbps, hbps, callRates = callRateTrial(0.03, 100000, 100)
    
    if maxRate is not None:
        foundRates.append(maxRate)

if len(foundRates) > 0:
    print(f" max call rate found: {max(foundRates)}. average: {sum(foundRates) / len(foundRates)}")
else:
    print("no call rates less than 0.2 found")