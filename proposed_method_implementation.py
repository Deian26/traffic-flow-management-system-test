# The implementation for the method proposed in the dissertation thesis appended to this repository.
import cityflow
import os, time, datetime, copy
from common.configuration import *
from common.functions import *

# configure simulation
print("    > DISSERTATION THESIS METHOD")
print("    > Creating CityFlow simulation engine...")
engine = cityflow.Engine(configuration_file_path, thread_num = SIM_THREAD_NUM)

maxNumberOfWaitingVehicles = 0
numberOfWaitingVehicles = 0
numberOfStatisticSamples = 0

def getYellowLightStatistics():
    """
    Calculates and stores traffic statistics
    """

    global numberOfWaitingVehicles
    global numberOfStatisticSamples
    global maxNumberOfWaitingVehicles

    numberOfStatisticSamples += 1

    crtWaitingVehiclesCount = GetWaitingVehiclesCount(engine.get_lane_waiting_vehicle_count())
    
    numberOfWaitingVehicles += crtWaitingVehiclesCount
    
    if crtWaitingVehiclesCount > maxNumberOfWaitingVehicles:
        maxNumberOfWaitingVehicles = crtWaitingVehiclesCount
###
# start simulation
with open(os.path.join(logsDir,"proposed_method_log.txt"),"w") as logFile: # logging
    print("    > Simulation started")
    print(f"{engine.get_current_time()} > SIMULATION START", file=logFile)

    engine.set_save_replay(True) # start replay saving

    newDayLastSimTimestamp = 0 # stores the timestamp from the simulation whent he day index was last updated (in seconds)
    crtDayIndex = 0 # counts the simulated days of the week (0-7; 0 = Monday); resets to 0 after 6
    dayTrafficCycleCounter = 0 # counts the traffic cycles in a day; max 86 400 / TRAFFIC_CYCLE_DURATION_S (seconds in a day / traffic cycle duration in seconds)
    absoluteTrafficCycleCounter = 0 # used mostly for logging
    crtTrafficCycleStartTimestamp = engine.get_current_time() # timestamp when the current traffic cycle started
    crtTrafficCycleSegmentIndex = 0 
    crtTrafficCycleSegmentAndYellowBufferStartTimestamp = engine.get_current_time()
    crtGreenTimers = copy.deepcopy(trafficLightTimers) # timers actually used to simulate the intersection
    crtTrafficCycleSegmentTimers = list(crtGreenTimers.items())
    firstTimersComputedFlag = False # will be set to True after the first timers are computed

    # log initial info
    print(f"{engine.get_current_time()} > Total number of vehicles: {engine.get_vehicle_count()}", file=logFile)

    # initialize the traffic lights with a default configuration (scenario-specific):
    # initially, the side street traffic light will always be RED and the main street traffic lights will always be GREEN
    lastVehicleDetectedTimestamp = engine.get_current_time() # initialize timestamp for simulation stop timeout
    engine.set_tl_phase(intersection_id = INTERSECTION,
                        phase_id = TL_MAINSTREET_GREEN) # index from the 'lightPhases' of the intersection
    
    engine.next_step() # simulate a step

    #---# SIMULATION #---#
    crtSimStep = 1
    while True and crtSimStep <= MAX_SIM_STEPS:
        print("",file=logFile)
        print(f"{engine.get_current_time()} > Step: {crtSimStep}", file=logFile)    
        # skip until vehicles are detected on any road
        if engine.get_vehicle_count() == 0:
            engine.next_step(); crtSimStep+=1

            # check if the simulation should be stopped
            if engine.get_current_time() - lastVehicleDetectedTimestamp > NO_VEHICLE_TIMEOUT_S: # stop simulation
                print(f"{engine.get_current_time()} > Timeout reached before vehicles were detected on the road ({NO_VEHICLE_TIMEOUT_S} seconds)!", file = logFile)
                break
            
            continue

        
        lastVehicleDetectedTimestamp = engine.get_current_time() # mark the timestamp when vehicles were detected on any road

        ## Compute traffic cycle parameters
        # compute traffic coefficients for the intersection
        
        roadVehicleCounters = GetRoadVehicleCount(engine.get_lane_vehicle_count()) # get the number of vehicles in each lane
        
        #region traffic-coefficient
        # calculate the traffic coefficient for every road
        for road in trafficCoefficients.keys():
            #print(f"{engine.get_current_time()}        > Step: {crtSimStep} : Vehicles detected on road {road} : {roadVehicleCounters[road]}", file=logFile)
            trafficCoefficient = round(ComputeTrafficCoefficient(
                                                                Ql = roadVehicleCounters[road] * CONST_VEHICLE_LENGTH_M, # the length of each vehicle is configurable for the CityFlow simulation; this constant was chosen for all vehicles
                                                                Qb = roadVehicleCounters[road] * CONST_BUFFER_LENGTH_M, # this is the minimum buffer between 2 vehicles, defined for the CitFlow simulation
                                                                R = CONST_ROAD_SEGMENT_LENGTH_M), 3) # 3 digit precision after the comma
            
            if trafficCoefficient > trafficCoefficients[road]: # only store the value if is is greater than the previously stored one; the dictionary will be reset at the beginning og the traffic cycle
                trafficCoefficients[road] = trafficCoefficient
            
        #endregion


        #region end-of-cycle
        ## End of traffic cycle
        if firstTimersComputedFlag == False or engine.get_current_time() - crtTrafficCycleStartTimestamp > TRAFFIC_CYCLE_DURATION_S + CONST_YELLOW_TIMER_S: 
            if firstTimersComputedFlag == True:
                print(f"#-# END OF ABSOLUTE CYCLE {absoluteTrafficCycleCounter} #-#\n", file=logFile)
            else:
                print("#-# FIRST COMPUTED TIMERS #-#", file=logFile)
            
            # get sum of coefficients
            trafficCoefficientSum = 0
            for roadGroupName in trafficCoefficients.keys():
                trafficCoefficientSum += trafficCoefficients[roadGroupName]

            # store traffic cycle data
            dayTrafficCycleCounter += 1
            absoluteTrafficCycleCounter += 1

            #region next-cycle-timers
            # compute the timers for the next traffic cycle
            maxTimer = -1
            maxTimerRoadGroupName = None
            timerSum = 0 # sum of the timers; used for re-scaling, if needed (e.g., due to linked traffic lights)
            
            print("", file=logFile)
            trafficLoadPercentageSum = 0 # the sum of traffic load percentages (may exceed 100% is historical data is taken into account)
            for roadGroupName in roadGroups.keys():
                trafficLoadPercentages[roadGroupName] = 0 # reset timer
                for road in roadGroups[roadGroupName]: # linked roads
                    print(f"{engine.get_current_time()}    > Traffic coefficient for road {road} : {trafficCoefficients[road]}/{trafficCoefficientSum}", file=logFile)

                    l = trafficCoefficients[road] / trafficCoefficientSum
                    # get historical data for the next traffic cycle
                    historicalLoadPercentage = history[road][crtDayIndex].get(dayTrafficCycleCounter + 1,None) 

                    if historicalLoadPercentage != None: # historical data exists
                        l = (l + historicalLoadPercentage) / 2
                    #else: no historical data found => the load percentage to be used remains unchanged
                     
                    if l > trafficLoadPercentages[roadGroupName]:
                        trafficLoadPercentages[roadGroupName] = l # store higher traffic load percentage
                        trafficLoadPercentageSum += l
                
            # scale percentages for the entire cycle to the current max value (100%), in case they exceed 100% when historical data is taken into account
            for timersRoadGroupName in trafficLoadPercentages.keys():
                trafficLoadPercentages[timersRoadGroupName] = trafficLoadPercentages[timersRoadGroupName] / trafficLoadPercentageSum
                # log traffic load percentages
                print(f"{engine.get_current_time()}    > Maximum traffic load percentage for road group {timersRoadGroupName} : {trafficLoadPercentages[timersRoadGroupName]*100}%", file=logFile)
            
            for roadGroupName in roadGroups.keys():
                # compute the green state timers for each traffic light, for the next cycle
                trafficLightTimers[roadGroupName][0] =  trafficLoadPercentages[roadGroupName] * TRAFFIC_CYCLE_DURATION_S # seconds
                
                if trafficLightTimers[roadGroupName][0] > maxTimer:
                    maxTimer = trafficLightTimers[roadGroupName][0]
                    maxTimerRoadGroupName = roadGroupName
                
                # impose minimum timer duration (in case the sum of timers exceeds the total traffic cycle duration, the timer with the highest value will be decremented until the sum is respected)
                if trafficLightTimers[roadGroupName][0] < MIN_TL_GREEN_DURATION_S:
                    trafficLightTimers[maxTimerRoadGroupName][0] -= (MIN_TL_GREEN_DURATION_S - trafficLightTimers[roadGroupName][0])
                    trafficLightTimers[roadGroupName][0] = MIN_TL_GREEN_DURATION_S

                    if trafficLightTimers[maxTimerRoadGroupName][0] <= 0: # error checking, just in case
                        raise ValueError(f"Invalid maximum green timer value: {trafficLightTimers[maxTimerRoadGroupName][0]} for absolute cycle {absoluteTrafficCycleCounter }!") # error
                
                timerSum += trafficLightTimers[roadGroupName][0]

            # scale timers so that they occupy the entire duration of the traffic cycle (might be needed if there are linked traffic lights)
            for roadGroupName in trafficLightTimers.keys():
                trafficLightTimers[roadGroupName][0] = (trafficLightTimers[roadGroupName][0] / timerSum) * TRAFFIC_CYCLE_DURATION_S
                print(f"{engine.get_current_time()}    > Scaled traffic light timer for road group {roadGroupName} : {trafficLightTimers[roadGroupName][0]} s", file=logFile)
            firstTimersComputedFlag = True
            #endregion

            #region next-cycle-details
            # reset traffic coefficients
            for road in trafficCoefficients.keys():
                trafficCoefficients[road] = 0
            trafficCoefficientSum = 0

            # get traffic cycle segment start timestamp
            crtTrafficCycleSegmentAndYellowBufferStartTimestamp = engine.get_current_time()
            # get new timers
            crtGreenTimers = copy.deepcopy(trafficLightTimers)
            # reset traffic cycle segment counter
            crtTrafficCycleSegmentIndex = 0 # the first segment is set up in this 'if' branch
            # get next traffic cycle segment timer
            crtTrafficCycleSegmentTimers = list(crtGreenTimers.items())
            #print(f"{engine.get_current_time()} > Green state timers computed for absolute cycle {absoluteTrafficCycleCounter} : {trafficLightTimers}\n", file=logFile)
            print(f"{engine.get_current_time()} > Current number of vehicles on each road (only input roads are used for traffic management): {GetRoadVehicleCount(engine.get_lane_vehicle_count())}", file=logFile)
            print("", file=logFile)
            #endregion

            # set traffic lights to 'yellow' (all lights are RED)
            engine.set_tl_phase(intersection_id = INTERSECTION, 
                    phase_id = TL_NO_GREEN)

            # log the start of a new traffic cycle
            print(f"{engine.get_current_time()} > #-# START OF ABSOLUTE CYCLE {absoluteTrafficCycleCounter} #-#", file=logFile)
            crtTrafficCycleStartTimestamp = engine.get_current_time()
        
        #endregion


        #region end-of-yello-light
        if engine.get_current_time() - crtTrafficCycleSegmentAndYellowBufferStartTimestamp > CONST_YELLOW_TIMER_S:
            # get statistics
            getYellowLightStatistics()

            # set up the next segment
            engine.set_tl_phase(intersection_id = INTERSECTION, 
                                phase_id = crtTrafficCycleSegmentTimers[crtTrafficCycleSegmentIndex][1][1]) # first traffic cycle segment


        #endregion


        #region end-of-segment
        ## End of traffic cycle segment (1 traffic light group)
        if engine.get_current_time() - crtTrafficCycleSegmentAndYellowBufferStartTimestamp > crtTrafficCycleSegmentTimers[crtTrafficCycleSegmentIndex][1][0] + CONST_YELLOW_TIMER_S:
            print(f"{engine.get_current_time()}    > End of traffic cycle segment index {crtTrafficCycleSegmentIndex}", file=logFile)
            
            # get start timestamp
            crtTrafficCycleSegmentAndYellowBufferStartTimestamp = engine.get_current_time()

            # get next segment details
            crtTrafficCycleSegmentIndex += 1

            # set traffic lights to 'yellow' (all lights are RED)
            engine.set_tl_phase(intersection_id = INTERSECTION, 
                    phase_id = TL_NO_GREEN)
        #endregion


        #region time-update
        ### Update time
        if newDayLastSimTimestamp + 86_400 <= engine.get_current_time(): # new day
            newDayLastSimTimestamp = engine.get_current_time() # get new timestamp
            dayTrafficCycleCounter = 0 # reset traffic cycle counter
            crtDayIndex += 1 # count day of the week
            
            if crtDayIndex > 6: # new week
                crtDayIndex = 0 # reset

        #endregion

        # simulate step
        engine.next_step()
        crtSimStep += 1

    print(f"{engine.get_current_time()} > SIMULATION STOP", file=logFile)
    print("    > Simulation stopped")
    print(f"Simulation stopped after {crtSimStep-1} steps", file=logFile)
    print("", file=logFile)
    print("Statistics")
    print(f"Average travel time: {engine.get_average_travel_time()} seconds", file=logFile)
    
    if numberOfStatisticSamples > 0:
        print(f"Average number of waiting vehicles during the yellow lights phase: {(numberOfWaitingVehicles / numberOfStatisticSamples)}", file=logFile)
    
    print(f"Maximum number of waiting vehicles during a yellow light phase: {maxNumberOfWaitingVehicles}", file=logFile)