# Implementation for the algorithm proposed in:
# Zhuravleva, N., Volkova, E. and Solovyev, D., 2020. Smart technology implementation for road traffic management. In E3S Web of Conferences (Vol. 220, p. 01063). EDP Sciences. - https://www.e3s-conferences.org/articles/e3sconf/pdf/2020/80/e3sconf_ses2020_01063.pdf, last accessed: May 27, 2025

# Used to compare the method proposed in the dissertation thesis appended to this repository with the one proposed in the paper referenced above

import cityflow
import os, time, datetime
from common.configuration import *
from common.functions import *

# configure simulation
print("    > DYNAMIC TIMERS BASED ON QUEUE COUNTERS (QUEUE THEOR; PAPER 5) METHOD")
print("    > Creating CityFlow simulation engine...")
engine = cityflow.Engine(f"{crt_file_path}/config_paper5Method.json", thread_num = SIM_THREAD_NUM)

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

def SimulateTraffic(engine, simTimeSec:float) -> int:
    """
    Simulate the traffic for the given time, using the provided simulation engine.

    :param engine: CityFlow simulation engine
    :type: CityFlow engine

    :param simTimeSec: simulated time, in s
    :type simTimeSec: float


    :returns: the number of simulated steps
    :rtype: int
    """

    simSteps = 0
    t0 = engine.get_current_time() # get initial time

    while engine.get_current_time() - t0 < simTimeSec:
        engine.next_step() # simulate step
        simSteps += 1 # count simulated steps
        getSimStepStatistics()

    return simSteps

###
# start simulation
with open(os.path.join(logsDir,"paper_5_method_log.txt"),"w") as logFile: # logging
    print("    > Simulation started")
    print(f"{engine.get_current_time()} > SIMULATION START", file=logFile)
    print(f"Fixed green state timers: side street {trafficLightTimers['sideStreet'][0]}s; main street {trafficLightTimers['mainStreet'][0]}s", file=logFile)

    engine.set_save_replay(True) # start replay saving

    absoluteTrafficCycleCounter = 0 # used mostly for logging

    # log initial info
    print(f"{engine.get_current_time()} > Total number of vehicles: {engine.get_vehicle_count()}", file=logFile)

    # initialize the traffic lights with a default configuration (scenario-specific):
    # initially, the side street traffic light will always be RED and the main street traffic lights will always be GREEN
    engine.set_tl_phase(intersection_id = INTERSECTION,
                        phase_id = TL_MAINSTREET_GREEN) # index from the 'lightPhases' of the intersection

    #---# SIMULATION #---#
    crtSimStep = 1
    while True and crtSimStep <= MAX_SIM_STEPS: # 1 step = 100 simulated ms (0.1s)
        # get the number of vehicles on the side street
        sideStreetVehicleCount = GetRoadVehicleCount(engine.get_lane_vehicle_count())["sideStreet_in"]

        if sideStreetVehicleCount > 0: # cars detected on the side street
            # set all traffic lights to RED for 3s (to simulate the 'yellow light' phase)
            engine.set_tl_phase(intersection_id = INTERSECTION,
                        phase_id = TL_NO_GREEN)
            crtSimStep += SimulateTraffic(engine = engine, simTimeSec = 3)

            # set the side street traffic light to GREEN and the main street lights to RED for 15s
            engine.set_tl_phase(intersection_id = INTERSECTION,
                        phase_id = TL_SIDESTREET_GREEN)
            crtSimStep += SimulateTraffic(engine = engine, simTimeSec = 15)

            # set all lights to RED ('yellow light phase') for 3s
            engine.set_tl_phase(intersection_id = INTERSECTION,
                        phase_id = TL_NO_GREEN)
            crtSimStep += SimulateTraffic(engine = engine, simTimeSec = 3)

            # set the side street light to RED and the main street lights to GREEN (for at least 60s)
            engine.set_tl_phase(intersection_id = INTERSECTION,
                        phase_id = TL_MAINSTREET_GREEN)
            crtSimStep += SimulateTraffic(engine = engine, simTimeSec = 60)

        # store traffic cycle data
        engine.next_step(); crtSimStep += 1; getSimStepStatistics()

    print(f"{engine.get_current_time()} > SIMULATION STOP", file=logFile)
    print("    > Simulation stopped")
    print(f"Simulation stopped after {crtSimStep} steps", file=logFile)
    print(f"Average travel time: {engine.get_average_travel_time()} seconds", file=logFile)
    
    if numberOfStatisticSamples > 0:
        print(f"Average number of waiting vehicles / step: {(numberOfWaitingVehicles / numberOfStatisticSamples)}", file=logFile)
    
    print(f"Maximum number of waiting vehicles / step: {maxNumberOfWaitingVehicles}", file=logFile)
    print()