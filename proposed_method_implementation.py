# The implementation for the method proposed in the dissertation thesis appended to this repository.
import cityflow
import os, time, datetime, copy
from common.configuration import *
from common.functions import *

# configure simulation
print("    > DISSERTATION THESIS METHOD")
print("    > Creating CityFlow simulation engine...")
engine = cityflow.Engine(f"{crt_file_path}/config_proposedMethod.json", thread_num = SIM_THREAD_NUM)

maxNumberOfWaitingVehicles = 0
numberOfWaitingVehicles = 0
numberOfStatisticSamples = 0

def getSimStepStatistics():
    """
    Calculates and stores traffic statistics for a simulation step.
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

# use pre-recorded historical data

# historical data
history = {'sideStreet_in': {0: {1: 0.1978609625668449, 2: 0.2615873015873016, 3: 0.22888888888888886, 4: 0.2597333333333333, 5: 0.264961915125136, 6: 0.23523261892315736, 7: 0.25, 8: 0.24483133841131666, 9: 0.23523261892315733, 10: 0.2763904653802497, 11: 0.24483133841131666, 12: 0.25539160045402953, 13: 0.2398720682302772, 14: 0.25, 15: 0.24986118822876177, 16: 0.27055555555555555, 17: 0.24974358974358973, 18: 0.21548117154811716, 19: 0.2496969696969697, 20: 0.2608695652173913, 21: 0.23382519863791146, 22: 0.2388405797101449, 23: 0.27055555555555555, 24: 0.27055555555555555, 25: 0.23369256948383438, 26: 0.2552467385138968, 27: 0.28231884057971013, 28: 0.24974358974358973, 29: 0.24000000000000002, 30: 0.24986118822876177}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}, 'mainStreet_WE_in': {0: {1: 0.40106951871657753, 2: 0.11936507936507937, 3: 0.125, 4: 0.14026666666666668, 5: 0.10228509249183895, 6: 0.09827496079456352, 7: 0.125, 8: 0.10228509249183895, 9: 0.15682174594877155, 10: 0.10669693530079455, 11: 0.10228509249183895, 12: 0.12769580022701477, 13: 0.10021321961620469, 14: 0.125, 15: 0.10438645197112714, 16: 0.10444444444444444, 17: 0.13487179487179488, 18: 0.11767782426778244, 19: 0.11393939393939395, 20: 0.08695652173913043, 21: 0.0851305334846765, 22: 0.1089855072463768, 23: 0.10444444444444444, 24: 0.08333333333333333, 25: 0.10663641520136133, 26: 0.10663641520136133, 27: 0.1089855072463768, 28: 0.11538461538461539, 29: 0.08, 30: 0.10438645197112714}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}, 'mainStreet_EW_in': {0: {1: 0.40106951871657753, 2: 0.6190476190476191, 3: 0.6461111111111111, 4: 0.6, 5: 0.6327529923830251, 6: 0.6664924202822792, 7: 0.625, 8: 0.6528835690968443, 9: 0.6079456351280711, 10: 0.6169125993189557, 11: 0.6528835690968443, 12: 0.6169125993189557, 13: 0.6599147121535182, 14: 0.625, 15: 0.645752359800111, 16: 0.625, 17: 0.6153846153846154, 18: 0.6668410041841004, 19: 0.6363636363636365, 20: 0.6521739130434783, 21: 0.681044267877412, 22: 0.6521739130434783, 23: 0.625, 24: 0.6461111111111111, 25: 0.6596710153148043, 26: 0.638116846284742, 27: 0.6086956521739131, 28: 0.6348717948717949, 29: 0.6799999999999999, 30: 0.645752359800111}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}}

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
                    else: #no historical data found => the load percentage to be used remains unchanged; update the historical record
                        history[road][crtDayIndex].update({dayTrafficCycleCounter : l}) # first value recorded
                     
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


        #region update
        ### Update time
        if newDayLastSimTimestamp + 86_400 <= engine.get_current_time(): # new day
            newDayLastSimTimestamp = engine.get_current_time() # get new timestamp
            dayTrafficCycleCounter = 0 # reset traffic cycle counter
            crtDayIndex += 1 # count day of the week
            
            if crtDayIndex > 6: # new week
                crtDayIndex = 0 # reset
        #endregion

        # simulate step
        engine.next_step(); crtSimStep += 1; getSimStepStatistics()
        

    print(f"{engine.get_current_time()} > SIMULATION STOP", file=logFile)
    print("    > Simulation stopped")
    print(f"Simulation stopped after {crtSimStep-1} steps", file=logFile)
    print("", file=logFile)
    print(f"Average travel time: {engine.get_average_travel_time()} seconds", file=logFile)
    
    if numberOfStatisticSamples > 0:
        print(f"Average number of waiting vehicles / step: {(numberOfWaitingVehicles / numberOfStatisticSamples)}", file=logFile)
    
    print(f"Maximum number of waiting vehicles / step: {maxNumberOfWaitingVehicles}", file=logFile)
    print(history, file=logFile) # log data
    print()