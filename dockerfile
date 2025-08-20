# get CityFlow
FROM cityflowproject/cityflow:latest

# add required files to the image
ADD /proposed_method_implementation.py /_tfms/
ADD /fixed_timers_method_implementation.py /_tfms/
ADD /paper_5_method_implementation.py /_tfms/
ADD /start_all_simulations.py /_tfms/

ADD /common/ /_tfms/common/

# start simulation
ENTRYPOINT ["python3", "_tfms/start_all_simulations.py"]