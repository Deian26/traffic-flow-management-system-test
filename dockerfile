# get CityFlow
FROM cityflowproject/cityflow:latest

# add required files to the image
ADD /proposed_method_implementation.py /_tfms/
ADD /fixed_timers_method_implementation.py /_tfms/
ADD /paper_5_method_implementation.py /_tfms/

ADD /common/ /_tfms/common/

# start simulation

# proposed method
#ENTRYPOINT ["python3", "_tfms/proposed_method_implementation.py"]

# fixed timers method
ENTRYPOINT ["python3", "_tfms/fixed_timers_method_implementation.py"]

# paper 5 method
#ENTRYPOINT ["python3", "_tfms/paper_5_method_implementation.py"]