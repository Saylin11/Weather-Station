# Weather-Station
Weather Station built for Sappi Tugela using a Raspberry Pi

A BME280 is used to measure Temperature, Humidity and Pressure.
WS303U Ultrasonic Wind Speed & Direction Sensor is also used.

This project sends live data directly to a web visualisation tool used at the mill (PI Vision).
When network connectivity, the system locally stores all data to a textfile which will automatically populate PI Vision once the connection is re-established. 
It also sends signals to the visualisation tool when there is an error with a sensor.
