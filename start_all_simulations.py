# Start all simulations
import subprocess, time, os

subprocess.run(["python3", f"{os.path.dirname(__file__)}/proposed_method_implementation.py"])
time.sleep(1)
print()
subprocess.run(["python3", f"{os.path.dirname(__file__)}/paper_5_method_implementation.py"])
time.sleep(1)
print()
subprocess.run(["python3", f"{os.path.dirname(__file__)}/fixed_timers_method_implementation.py"])