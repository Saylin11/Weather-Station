#!/usr/bin/python3
import requests
import os
import sys
import time
import math
import datetime
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280
import numpy as np
from random import random
import urllib3
urllib3.disable_warnings()

buffer_timestamps = []
buffer_OutTemp = []
buffer_pressure = []
buffer_humidity = []
sensor_flag = [0, 0, 0]
sensor_timestamp = [0, 0 , 0]
flag = 0
flagS = 0
OutTemp, pressure, humidity  = None, None, None
sensors = [OutTemp, pressure, humidity]

# PI Web API definitions
base_url = 'https://***'
webID_OutTemp =  'F1DPqtKYo_aVKU65kQXapRFORQqKUAAAVFVHVkxTMThcU1lTVDpPVVRET09SX1RFTVAz'
webID_pressure = 'F1DPqtKYo_aVKU65kQXapRFORQr6UAAAVFVHVkxTMThcU1lTVDpPVVRET09SX1RFTVA1'
webID_humidity = 'F1DPqtKYo_aVKU65kQXapRFORQrqUAAAVFVHVkxTMThcU1lTVDpPVVRET09SX1RFTVA0'

#[TempF, PressF, HumF]
webID_sensor_flag = ['F1DPqtKYo_aVKU65kQXapRFORQsqUAAAVFVHVkxTMThcU1lTVDpSQVNQX1BJX1dFQVRIRVJfVF9TRU5TT1I', 'F1DPqtKYo_aVKU65kQXapRFORQs6UAAAVFVHVkxTMThcU1lTVDpSQVNQX1BJX1dFQVRIRVJfUF9TRU5TT1I', 'F1DPqtKYo_aVKU65kQXapRFORQsaUAAAVFVHVkxTMThcU1lTVDpSQVNQX1BJX1dFQVRIRVJfSF9TRU5TT1I']

# Post to PI ***********************************************************
def post_to_pi(webID, timestamp, value):
    #print ("Post To PI")
    data = {'Timestamp':timestamp, 'Value':value}
    headers = {'Content-Type':'application/json'}
    response = requests.post(base_url + webID + '/value',json=data, headers=headers, verify=False, auth=requests.auth.HTTPBasicAuth('********','*********'))
    #print ("PI Response ;", response)
    return response

# Buffer***********************************************************
def buffer():               #Posts values to a textfile		
    print("In buffer")
    file = open("test.txt", "r+")
    lines = file.readlines()
    buffer_count = len(lines)
    lines.pop()

    for x in lines:                       #Splitting each line of textfile into sensors
        x = x.split(',')
        buffer_timestamps.append(x[0])
        buffer_OutTemp.append(x[1])
        buffer_pressure.append(x[2])
        buffer_humidity.append(x[3].replace("\n",""))
    
    for i in range(buffer_count-1):              #Posting each sensor value
        post_to_pi(webID_OutTemp, buffer_timestamps[i], float(buffer_OutTemp[i]))
        post_to_pi(webID_pressure, buffer_timestamps[i], float(buffer_pressure[i]))
        post_to_pi(webID_humidity, buffer_timestamps[i], float(buffer_humidity[i]))
        time.sleep(0.2)
    
    buffer_timestamps.clear()
    buffer_OutTemp.clear()
    file = open("test.txt", "r+")
    file.truncate(0)                          #clear buffer
    file.close()
    
#Create library object using out bus i2c port ***********************
i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

#Post Flag
print("Startup")
time_error = datetime.datetime.utcnow().isoformat() + 'Z'
timestamp = datetime.datetime.utcnow().isoformat() + 'Z'

try:
    file_time = open("sensor_flag.txt", "r+")
    z = file_time.read()
    
    #Checking if there is any values in timestamp buffer
    if(len(z) > 0):
        time_error = z
        file_time.truncate(0)
        file.close()
    
    for j in range (len(sensors)): 
        post_to_pi(webID_sensor_flag[j], time_error, 1)
        timestampF = datetime.datetime.utcnow().isoformat() + 'Z'
        post_to_pi(webID_sensor_flag[j], timestamp, 0)

except:
    flag = 1

# Main Software loop **************************************************
while True:
    
    #Initilising sensor value
    OutTemp, pressure, humidity  = None, None, None
    sensors = [OutTemp, pressure, humidity]
    
    try:
        #Sensor Values
        timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
        OutTemp = bme280.temperature
        pressure = bme280.pressure
        humidity = bme280.humidity
        sensors = [OutTemp, pressure, humidity]
        s = any(elem is None for elem in sensors)
        
        #Pinging PI server
        hostname = '168.155.xxx.xxx'
        response = os.system('ping -c 1 ' + hostname)
        
        if(response == 0):    #Successful Ping
            
            if(s == False and flagS == 1):     #sensors working + sensor flag high
                flagS = 0        
                file_time = open("sensor_flag.txt", "r+")
                z = file_time.read()
    
                #Checking if there is any values in timestamp buffer
                if(len(z) > 0):
                    time_error = z
                    for j in range (len(sensors)): 
                        post_to_pi(webID_sensor_flag[j], time_error, 1)   
                
                for j in range (len(sensors)):
                    post_to_pi(webID_sensor_flag[j], timestamp, 0)
                print("Sensor Flag reset")
                file = open("sensor_flag.txt", "r+")
                file.truncate(0)
                file.close()
                    
            #Post Values
            post_to_pi(webID_OutTemp, timestamp, OutTemp)
            post_to_pi(webID_pressure, timestamp, pressure)
            post_to_pi(webID_humidity, timestamp, humidity)                    

            #Checking if data is in textfile
            if(os.stat('test.txt').st_size != 0):
                print("Activate Buffer")
                buffer()
        
        if(response != 0):
            
            if(s == True and flagS == 0):
                flagS = 1
                sensor_time = datetime.datetime.utcnow().isoformat() + 'Z'
                file = open("sensor_flag.txt", "a") 
                file.write(sensor_time)
                file.close()
                
            if(s == False):
                flag = 0
                combine = timestamp + "," + str(OutTemp) + "," + str(pressure) + "," + str(humidity) + "\n"        #Adding values to textfile buffer
                file = open("test.txt", "a")    
                file.write(str(combine))
                file.close()
        
        #print (" =================== Sleep ===================================== ")
        time.sleep (30)
        
        
# END of main loop ***************************************

    except Exception as e:
        
        s = any(elem is None for elem in sensors)
        if(s == True and flagS == 0):
            flagS = 1
            
            hostname = '168.155.xxx.xxx'
            response = os.system('ping -c 1 ' + hostname)
        
            if(response == 0):
                for j in range (len(sensors)):
                    post_to_pi(webID_sensor_flag[j], timestamp, 1)
                    
            else:
                sensor_time = datetime.datetime.utcnow().isoformat() + 'Z'
                file = open("sensor_flag.txt", "a") 
                file.write(sensor_time)
                file.close()
        
        flag = 1
        print ("Exception Occured >>>>> " , (e))
        print (" =================== Exception Sleep =========================== ")
        print(e)
        time.sleep(15)
