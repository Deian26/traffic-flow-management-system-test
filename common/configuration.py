# Simulation configuration
import os

# simulation constants
TRAFFIC_CYCLE_DURATION_S = 120 # the duration, in seconds, of the traffic cycle, except the yellow light duration which is set to 'CONST_YELLOW_TIMER_S' seconds and is present after each traffic cycle segment
MIN_TL_GREEN_DURATION_S = 10 # minimum duration, in seconds, for a green state

# traffic light timers (specific for the simulated scenario)
CONST_MAINSTREET_GREEN_TIMER_S = 60 # time, in seconds, during which the light will be kept on GREEN
CONST_SIDESTREET_GREEN_TIMER_S = 15
CONST_YELLOW_TIMER_S = 3 # value used as in paper [5], for better comparison # all lights are RED for this amount a time before the traffic phase is changed

# constant lengths (meters)
CONST_VEHICLE_LENGTH_M = 5 # the length of a vehicle, in meters (constant for computing the traffic coefficient; this is the actual length of the simulated vehicles)
CONST_BUFFER_LENGTH_M = 2.5 # the length of a buffer between 2 queued vehicles (constant for computing the traffic coefficient)
CONST_ROAD_SEGMENT_LENGTH_M = 200 # the length of the observed segment of road, leading to the intersection

# intersection names
INTERSECTION = "intersection"

# light phases (scenario-specific)
TL_NO_GREEN = 0 # NO GREEN lights
TL_SIDESTREET_GREEN = 1 # only the side street light will be GREEN
TL_MAINSTREET_GREEN = 2 # only the main street lights (both directions) will be GREEN

# only the incoming roads (marked 'in') are taken into account
# intersection
roadGroups = { # format: {road group name : road name(s)}
    "sideStreet" : ["sideStreet_in"],
    "mainStreet" : ["mainStreet_WE_in", "mainStreet_EW_in"],
}

trafficCoefficients = {
    "sideStreet_in" : 0,
    "mainStreet_WE_in" : 0,
    "mainStreet_EW_in" : 0
}

trafficLoadPercentages = { # format: { road group name (e.g., main street) : traffic load percentage }
    "sideStreet" : 0,
    "mainStreet" : 0
}

trafficLightTimers = { #format: { road group name : [timer value in seconds, corresponding CityFlow traffic light phase index] }
    "sideStreet" : [None, TL_SIDESTREET_GREEN],
    "mainStreet" : [None, TL_MAINSTREET_GREEN]
}

history = { # format: { road name : {day (1-7, int) : {traffic cycle index : green timer value (in seconds)} } }
    "sideStreet_in" : {
        0 : {},
        1 : {},
        2 : {},
        3 : {},
        4 : {},
        5 : {},
        6 : {},
    }, 

    "mainStreet_WE_in" : {
        0 : {},
        1 : {},
        2 : {},
        3 : {},
        4 : {},
        5 : {},
        6 : {},
    }, 

    "mainStreet_EW_in" : {
        0 : {},
        1 : {},
        2 : {},
        3 : {},
        4 : {},
        5 : {},
        6 : {},
    }, 
}

# config
wd = "_tfms" # working directory (root)
logsDir = os.path.join(wd, "logs") # logs directory
os.makedirs(logsDir, exist_ok=True) # create the logs directory
NO_VEHICLE_TIMEOUT_S = 5 * 60 # the maximum duration, in simulated seconds, for which the program waits for new vehicles to enter the road network; if no vehicles are detected on any road for this time interval, the simulation is stopped
MAX_SIM_STEPS = 1 * 36_000 # maximum number of simulation steps; 1 step = 0.1 s
SIM_THREAD_NUM = 1
crt_file_path = os.path.dirname(__file__)
flow_file_path = f"{crt_file_path}/flow.json"
roadnet_file_path = f"{crt_file_path}/roadnet.json"