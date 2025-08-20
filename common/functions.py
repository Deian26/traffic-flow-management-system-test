# Common functions

def ComputeTrafficCoefficient(Ql:float, Qb:float, R:float)->float:
    """
    Computes the traffic coefficient based on the given values
    
    :param Ql: the sum of the lengths of incoming vehicles
    :type Ql: float

    :param Qb: the sum of the lengths of inter-vehicle buffer segments
    :type Qb: float
    
    :param R: the length of the observed road segment
    :type R: float


    :returns trafficCoefficient: the computed traffic coefificent
    :rtype: float
    """

    return (Ql + Qb) / R # Formula 1

def GetRoadVehicleCount(laneCounters:dict) -> dict:
    """
    Returns the vehicle count for all roads from the given dictionary.
    This function sums the number of vehicle for each lane on a road and stores that value for the entire road.

    :param laneCounters: a dictionary returned by CityFlow's 'get_lane_vehicle_count' engine function
    :type laneCounters: dict[str, int]

    :returns: a dictionary containing the number of vehicles on each road (road meaning a segment of road leading to an intersection) (the names of the roads are the keys)
    :rtype: dict[str, int]
    """

    roadVehicleCounters = {}

    for lane in laneCounters.keys():
        # get the road name by removing lane index suffix
        road = '_'.join(lane.split('_')[:-1])

        if road in roadVehicleCounters: # this is not the first lane for this road from this dictionary
            roadVehicleCounters[road] += laneCounters[lane] # add number of vehicles
        else: # this is the first lane encountered for this road
            roadVehicleCounters.update({road : laneCounters[lane]}) # store the current number of vehicles (the entry is created now)
    
    return roadVehicleCounters

def GetWaitingVehiclesCount(waitingLaneVehicles:dict) -> int:
    """
    Returns the total number of waiting vehicles form the lanes provided.
    'waitingLaneVehicles' must be a valid dictionary returned by 'get_lane_waiting_vehicle_count()' from CityFlow
    
    :param waitingLaneVehicles: the simulated lanes and the vehicle count for each of them
    :type waitingLaneVehicles: dict[str, int]

    :returns: the total number of waiting vehicles
    :rtype: int
    """

    waitingVehicles = 0
    for lane in waitingLaneVehicles.keys():
        waitingVehicles += waitingLaneVehicles[lane]

    return waitingVehicles