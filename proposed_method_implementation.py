# The implementation for the method proposed in the dissertation thesis appended to this repository.
import cityflow
import os, time, datetime
from common.configuration import *
from common.functions import *

# Simulated intersection
# 

# configure simulation
engine = cityflow.Engine(configuration_file_path, thread_num = 1)

###
# start simulation
with open(os.path.join(logsDir,"proposed_method_log.txt"),"w") as logFile: # logging
    print("Simulation started")
    print(f"{engine.get_current_time()} > SIMULATION START", file=logFile)

    engine.set_save_replay(True) # start replay saving

    newDayLastSimTimestamp = 0 # stores the timestamp from the simulation whent he day index was last updated (in seconds)
    crtDayIndex = 0 # counts the simulated days of the week (0-7; 0 = Monday); resets to 0 after 6
    dayTrafficCycleCounter = 0 # counts the traffic cycles in a day; max 86 400 / TRAFFIC_CYCLE_DURATION_S (seconds in a day / traffic cycle duration in seconds)
    absoluteTrafficCycleCounter = 0 # used mostly for logging

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
        print("Simulation ongoing...")
        # skip until vehicles are detected on any road
        if engine.get_vehicle_count() == 0:
            engine.next_step(); crtSimStep+=1
            print(f"{engine.get_current_time()} > No vehicles...", file = logFile)

            # check if the simulation should be stopped
            if engine.get_current_time() - lastVehicleDetectedTimestamp > NO_VEHICLE_TIMEOUT_S: # stop simulation
                print(f"{engine.get_current_time()} > Timeout reached before vehicles were detected on the road ({NO_VEHICLE_TIMEOUT_S} seconds)!", file = logFile)
                break
            
            continue
            
        print(f"{engine.get_current_time()} > Vehicles detected ({engine.get_vehicle_count()})", file = logFile)
        lastVehicleDetectedTimestamp = engine.get_current_time() # mark the timestamp when vehicles were detected on any road

        ## Compute traffic cycle parameters
        # compute traffic coefficients for the intersection
        
        roadVehicleCounters = GetRoadVehicleCount(engine.get_lane_vehicle_count()) # get the number of vehicles in each lane
        
        # calculate the traffic coefficient for every road
        trafficCoefficientSum = 0
        for road in trafficCoefficients.keys():
            trafficCoefficients[road] = ComputeTrafficCoefficient(
                                                                Ql = roadVehicleCounters[road] * CONST_VEHICLE_LENGTH_M, # the length of each vehicle is configurable for the CityFlow simulation; this constant was chosen for all vehicles
                                                                Qb = roadVehicleCounters[road] * CONST_BUFFER_LENGTH_M, # this is the minimum buffer between 2 vehicles, defined for the CitFlow simulation
                                                                R = CONST_ROAD_SEGMENT_LENGTH_M)
            trafficCoefficientSum += trafficCoefficients[road]
        
        # compute the timers for the next traffic cycle
        maxTimer = -1
        maxTimerRoadGroupName = None

        for roadGroupName in roadGroups.keys():
            for road in roadGroups[roadGroupName]: # linked roads
                l = trafficCoefficients[road] / trafficCoefficientSum

                # get historical data for the next traffic cycle
                historicalLoadPercentage = history[road][crtDayIndex].get(dayTrafficCycleCounter + 1,None) 

                if historicalLoadPercentage != None: # historical data exists
                    l = (l + historicalLoadPercentage) / 2
                #else: no historical data found => the load percentage to be used remains unchanged

                if l > trafficLoadPercentages[roadGroupName]:
                    trafficLoadPercentages[roadGroupName] = l # store higher traffic load percentage

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
                    raise ValueError(f"Invalid maximum green timer value: {trafficLightTimers[maxTimerRoadGroupName][0]} for absolute cycle {absoluteTrafficCycleCounter }!")
        # store traffic cycle data
        dayTrafficCycleCounter += 1
        absoluteTrafficCycleCounter += 1

        # update time
        if newDayLastSimTimestamp + 86_400 <= engine.get_current_time(): # new day
            newDayLastSimTimestamp = engine.get_current_time() # get new timestamp
            dayTrafficCycleCounter = 0 # reset traffic cycle counter
            crtDayIndex += 1 # count day of the week
            
            if crtDayIndex > 6: # new week
                crtDayIndex = 0 # reset

        ## Simulate the traffic cycle
        for trafficLightGroup in trafficLightTimers.keys():
            # set the green timer to be the same for all traffic lights in the group
            engine.set_tl_phase(intersection_id = INTERSECTION, 
                                phase_id = trafficLightTimers[trafficLightGroup][1])

            # simulate traffic cycle segment
            t0 = engine.get_current_time()
            while engine.get_current_time() - t0 <= trafficLightTimers[trafficLightGroup][0]:
                engine.next_step(); crtSimStep+=1

    print(f"{engine.get_current_time()} > SIMULATION STOP", file=logFile)
    print("Simulation stopped")
    print(f"Simulation stopped after {crtSimStep} steps", file=logFile)

    #engine.set_save_replay(False) # stop replay saving
