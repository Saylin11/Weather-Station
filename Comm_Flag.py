#!/usr/bin/python3
import requests
import os
import sys
import time
import math
import datetime
import numpy as np
from random import random
import urllib3
urllib3.disable_warnings()

# PI Web API definitions
base_url = 'https://tugvls08.za.sappi.com/piwebapi/streams/'
webID_flag = 'F1DPqtKYo_aVKU65kQXapRFORQraUAAAVFVHVkxTMThcU1lTVDpSQVNQX1BJX1dFQVRIRVJfTEFO'

# Post to PI ***********************************************************
def post_to_pi(webID, timestamp, value):
    #print ("Post To PI")
    data = {'Timestamp':timestamp, 'Value':value}
    headers = {'Content-Type':'application/json'}
    response = requests.post(base_url + webID + '/value',json=data, headers=headers, verify=False, auth=requests.auth.HTTPBasicAuth('*******','*******'))
    #print ("PI Response ;", response)
    return response

time_error = datetime.datetime.utcnow().isoformat() + 'Z'
timestamp = datetime.datetime.utcnow().isoformat() + 'Z'

try:
    file_time = open("timestamp.txt", "r+")
    z = file_time.read()
    
    #Checking if there is any values in timestamp buffer
    if(len(z) > 0):
        time_error = z
        file_time.truncate(0)
        file.close()
        
    post_to_pi(webID_flag, time_error, 1)
    print("Flag!")
    flag = 0
    post_to_pi(webID_flag, timestamp, 0)
    print("Flag reset")

except:
    flag = 1

# Main Software loop **************************************************
while True:
    
    try:
        timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
        
        #Network connection error check
        hostname = '168.155.xxx.xxx'
        response = os.system('ping -c 1 ' + hostname)

        if(response != 0 and flag == 0):
            flag = 1
            time_error = datetime.datetime.utcnow().isoformat() + 'Z'     #Network connection error timestamp
            file = open("timestamp.txt", "a")    
            file.write(time_error)
            file.close()

        #Post the time which network error occurs and recovers and resets flag
        if(flag == 1 and response == 0):
            post_to_pi(webID_flag, time_error, 1)
            print("Flag!")
            flag = 0
            post_to_pi(webID_flag, timestamp, 0)
            print("Flag reset")
            file = open("timestamp.txt", "r+")
            file.truncate(0)
            file.close()

        #print (" =================== Sleep ===================================== ")
        time.sleep (30)
        
# END of main loop ***************************************

    except Exception as e:
        flag = 1
        print ("Exception Occured >>>>> " , (e))
        print (" =================== Exception Sleep =========================== ")
        print(e)
        time.sleep(30)
















