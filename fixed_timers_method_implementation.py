# Fixed timers for all traffic lights in the intersection
import cityflow
import os, time, datetime
from common.configuration import *
from common.functions import *

# configure simulation
print("    > FIXED TIMERS METHOD")
print("    > Creating CityFlow simulation engine...")
engine = cityflow.Engine(configuration_file_path, thread_num = SIM_THREAD_NUM)

# set fixed timers
trafficLightTimers.update({
    "sideStreet" : [15, TL_SIDESTREET_GREEN], 
    "mainStreet" : [60, TL_MAINSTREET_GREEN]
})

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
with open(os.path.join(logsDir,"fixed_timers_method_log.txt"),"w") as logFile: # logging
    print("    > Simulation started")
    print(f"{engine.get_current_time()} > SIMULATION START", file=logFile)
    print(f"Fixed green state timers: side street {trafficLightTimers['sideStreet'][0]}s; main street {trafficLightTimers['mainStreet'][0]}s", file=logFile)

    engine.set_save_replay(True) # start replay saving

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
        print(f"{engine.get_current_time()} > #-# START OF ABSOLUTE CYCLE {absoluteTrafficCycleCounter} #-#", file=logFile)
        
        # skip until vehicles are detected on any road
        if engine.get_vehicle_count() == 0:
            engine.next_step(); crtSimStep+=1

            # check if the simulation should be stopped
            if engine.get_current_time() - lastVehicleDetectedTimestamp > NO_VEHICLE_TIMEOUT_S: # stop simulation
                print(f"{engine.get_current_time()} > Timeout reached before vehicles were detected on the road ({NO_VEHICLE_TIMEOUT_S} seconds)!", file = logFile)
                break
            
            continue
        lastVehicleDetectedTimestamp = engine.get_current_time() # mark the timestamp when vehicles were detected on any road

        ## Simulate the traffic cycle
        for trafficLightGroup in trafficLightTimers.keys():
            # set the traffic lights to 'yellow' (all traffic lights will be set to RED for 'CONST_YELLOW_TIMER_S')
            engine.set_tl_phase(intersection_id = INTERSECTION, 
                    phase_id = TL_NO_GREEN)
            
            # simulate traffic furing the yellow lights phase
            t0 = engine.get_current_time()
            while engine.get_current_time() - t0 <= CONST_YELLOW_TIMER_S:
                getYellowLightStatistics()
                engine.next_step(); crtSimStep+=1

            # set the green timer to be the same for all traffic lights in the group
            engine.set_tl_phase(intersection_id = INTERSECTION, 
                                phase_id = trafficLightTimers[trafficLightGroup][1])

            # simulate traffic cycle segment
            t0 = engine.get_current_time()
            while engine.get_current_time() - t0 <= trafficLightTimers[trafficLightGroup][0]:
                engine.next_step(); crtSimStep+=1

        print("#-# END OF CYCLE #-#\n", file=logFile)

        # store traffic cycle data
        absoluteTrafficCycleCounter += 1


    print(f"{engine.get_current_time()} > SIMULATION STOP", file=logFile)
    print("    > Simulation stopped")
    print(f"Simulation stopped after {crtSimStep} steps", file=logFile)
    print(f"Average travel time: {engine.get_average_travel_time()} seconds", file=logFile)
    
    if numberOfStatisticSamples > 0:
        print(f"Average number of waiting vehicles during the yellow lights phase: {(numberOfWaitingVehicles / numberOfStatisticSamples)}", file=logFile)
    
    print(f"Maximum number of waiting vehicles during a yellow light phase: {maxNumberOfWaitingVehicles}", file=logFile)