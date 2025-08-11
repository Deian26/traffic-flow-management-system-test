# Simulation configuration
import os

# simulation constants
TRAFFIC_CYCLE_DURATION_S = 120 # the duration, in seconds, of the full traffic cycle (i.e., after all traffic lights were set to green for their determined duration)
MIN_TL_GREEN_DURATION_S = 10 # minimum duration, in seconds, for a green state

# traffic light timers (specific for the simulated scenario)
CONST_MAINSTREET_GREEN_TIMER_S = 60 # time, in seconds, during which the light will be kept on GREEN
CONST_SIDESTREET_GREEN_TIMER_S = 15

# constant lengths (meters)
CONST_VEHICLE_LENGTH_M = 5 # the length of a vehicle, in meters (constant for computing the traffic coefficient; this is the actual length of the simulated vehicles)
CONST_BUFFER_LENGTH_M = 2.5 # the length of a buffer between 2 queued vehicles (constant for computing the traffic coefficient)
CONST_ROAD_SEGMENT_LENGTH_M = 100 # the length of the observed segment of road, leading to the intersection

# intersection names
INTERSECTION = "intersection"

# light pahses (scenario-specific)
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
    "sideStreet_in" : None,
    "mainStreet_WE_in" : None,
    "mainStreet_EW_in" : None
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
MAX_SIM_STEPS = 20 #36_000 # maximum number of simulation steps
crt_file_path = os.path.dirname(__file__)
configuration_file_path = f"{crt_file_path}/config.json"
flow_file_path = f"{crt_file_path}/flow.json"
roadnet_file_path = f"{crt_file_path}/roadnet.json"