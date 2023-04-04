#!/usr/bin/python3
import requests
import os
import sys
import time
import math
import datetime
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np
from random import random
import urllib3
urllib3.disable_warnings()

buffer_timestamps = []
buffer_wind_speed = []
buffer_wind_dir = []
flag = 0
flagS = 0
wind_speed, wind_dir = None, None
sensors = [wind_speed, wind_dir]

# PI Web API definitions
base_url = 'https://***'
webID_wind_speed =  'F1DPqtKYo_aVKU65kQXapRFORQk6YAAAVFVHVkxTMThcU1lTVDpPVVRET09SX1dJTkRTUEVFRA'
webID_wind_dir = 'F1DPqtKYo_aVKU65kQXapRFORQmkYAAAVFVHVkxTMThcU1lTVDpPVVRET09SX1dJTkRESVJFQ1RJT04'
webID_wind_flag =  'F1DPqtKYo_aVKU65kQXapRFORQl6YAAAVFVHVkxTMThcU1lTVDpSQVNQX1BJX1dFQVRIRVJfVF19TRU5TT1I'



# Post to PI ***********************************************************
def post_to_pi(webID, timestamp, value):
    #print ("Post To PI")
    data = {'Timestamp':timestamp, 'Value':value}
    headers = {'Content-Type':'application/json'}
    response = requests.post(base_url + webID + '/value',json=data, headers=headers, verify=False, auth=requests.auth.HTTPBasicAuth('*******','********'))
    #print ("PI Response ;", response)
    return response

# Buffer***********************************************************
def buffer():
    print("In buffer")
    file = open("wind.txt", "r+")
    lines = file.readlines()
    buffer_count = len(lines)
    lines.pop()

    for x in lines:                       #Splitting each line of textfile into sensors
        x = x.split(',')
        buffer_timestamps.append(x[0])
        buffer_wind_speed.append(x[1])
        buffer_wind_dir.append(x[2].replace("\n",""))
    
    for i in range(buffer_count-1):              #Posting each sensor value
        post_to_pi(webID_wind_speed, buffer_timestamps[i], float(buffer_wind_speed[i]))
        post_to_pi(webID_wind_dir, buffer_timestamps[i], float(buffer_wind_dir[i]))
        time.sleep(0.2)
    
    buffer_timestamps.clear()
    buffer_wind_speed.clear()
    buffer_wind_dir.clear()
    file = open("wind.txt", "r+")
    file.truncate(0)                          #clear buffer
    file.close()

#Post Flag
print("Startup")
time_error = datetime.datetime.utcnow().isoformat() + 'Z'
timestamp = datetime.datetime.utcnow().isoformat() + 'Z'

try:
    file_time = open("wind_flag.txt", "r+")
    z = file_time.read()
    
    #Checking if there is any values in timestamp buffer
    if(len(z) > 0):
        time_error = z
        file_time.truncate(0)
        file.close()
    
    post_to_pi(webID_wind_flag, time_error, 1)
    timestampF = datetime.datetime.utcnow().isoformat() + 'Z'
    post_to_pi(webID_wind_flag, timestamp, 0)

except:
    flag = 1

# Main Software loop **************************************************
while True:
    
    #Initilising sensor value
    wind_speed, wind_dir = None, None
    sensors = [wind_speed, wind_dir]       
    
    try:
        
        timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
        
        #Create library object using out bus i2c port ***********************
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)

        
        #Sensor Values
        chan1 = AnalogIn(ads, ADS.P0)
        chan2 = AnalogIn(ads, ADS.P1)
        
        
        wind_speed = chan1.voltage/5            #Measured Input of 0-5 Volts
        wind_speed = wind_speed * 40
       # wind_speed = str(round(wind_speed, 3))
        
        wind_dir = chan2.voltage/5            #Measured Input of 0-5 Volts
        wind_dir = wind_dir * 360
        #wind_dir = str(round(wind_dir, 3))
        
        sensors = [wind_speed, wind_dir]
        s = any(elem is None for elem in sensors)
        
        #Pinging PI server
        hostname = '168.155.xxx.xxx'
        response = os.system('ping -c 1 ' + hostname)
        
        if(response == 0):    #Successful Ping
            
            if(s == False and flagS == 1):     #sensors working + sensor flag high
                flagS = 0        
                file_time = open("wind_flag.txt", "r+")
                z = file_time.read()
    
                #Checking if there is any values in timestamp buffer
                if(len(z) > 0):
                    time_error = z
                    post_to_pi(webID_wind_flag, time_error, 1)   
                
                post_to_pi(webID_wind_flag, timestamp, 0)
                print("Wind Flag reset")
                file = open("wind_flag.txt", "r+")
                file.truncate(0)
                file.close()
               
            #Post Values
            post_to_pi(webID_wind_speed, timestamp, wind_speed)
            post_to_pi(webID_wind_dir, timestamp, wind_dir)  

            #Checking if data is in textfile
            if(os.stat('wind.txt').st_size != 0):
                print("Activate Buffer")
                buffer()
        
        if(response != 0):
            
            if(s == True and flagS == 0):
                error_time = datetime.datetime.utcnow().isoformat() + 'Z'
                file = open("wind_flag.txt", "a") 
                file.write(error_time)
                file.close()
                
            if(s == False):
                flag = 0
                combine = timestamp + "," + str(wind_speed) + "," + str(wind_dir) + "\n"        #Adding values to textfile buffer
                file = open("wind.txt", "a")    
                file.write(str(combine))
                file.close()
        
        #print (" =================== Sleep ===================================== ")
        time.sleep (10)
        
        
# END of main loop ***************************************

    except Exception as e:
        
        s = any(elem is None for elem in sensors)
        if(s == True and flagS == 0):
            flagS = 1
            
            hostname = '168.155.xxx.xxx'
            response = os.system('ping -c 1 ' + hostname)
        
            if(response == 0):
                post_to_pi(webID_wind_flag, timestamp, 1)
                    
            else:
                error_time = datetime.datetime.utcnow().isoformat() + 'Z'
                file = open("wind_flag.txt", "a") 
                file.write(error_time)
                file.close()
        
        flag = 1
        print ("Exception Occured >>>>> " , (e))
        print (" =================== Exception Sleep =========================== ")
        time.sleep(15)
