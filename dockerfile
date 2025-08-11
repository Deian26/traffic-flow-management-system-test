# get CityFlow
FROM cityflowproject/cityflow:latest

# copy required files
ADD /proposed_method_implementation.py /_tfms/
ADD /common/ /_tfms/common/

# start simulation
ENTRYPOINT ["python3", "_tfms/proposed_method_implementation.py"]
