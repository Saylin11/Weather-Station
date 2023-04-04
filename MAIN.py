import subprocess

#Runs multiple python files at once
subprocess.run("python3 Comm_Flag.py & python3 BME280.py & python3 wind-sensor.py", shell=True)
