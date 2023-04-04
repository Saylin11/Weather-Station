# Weather-Station
Weather Station built for Sappi Tugela using a Raspberry Pi coded in Python.

A BME280 is used to measure Temperature, Humidity and Pressure.
WS303U Ultrasonic Wind Speed & Direction Sensor is also used.

This project sends live data directly to a web visualisation tool used at the mill (PI Vision).
When network connectivity, the system locally stores all data to a textfile which will automatically populate PI Vision once the connection is re-established. 
It also sends signals to the visualisation tool when there is an error with a sensor.

The main file runs the systems.
BME280.py is the pipeline for the BME280 sensor.
Comm_Flag.py is the python file to check the network connection between the Raspberry Pi and Sappi's network. Once re-established, it can pinpoint the time of failure on PI Vision.
wind-sesor.py is the pipeline for the WS303U sensor.
