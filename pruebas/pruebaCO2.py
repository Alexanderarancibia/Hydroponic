#!/usr/bin/python3
import os, glob, time, sys
import io
from datetime import datetime,date, time, timedelta
from pytz import timezone
import sys
import re
import requests
import json
import string
from AtlasI2C import (
	 AtlasI2C
)
import threading
import random
import time
import fcntl
import RPi.GPIO as GPIO
import time
import copy
import re
import requests
import json
import string

import threading
import random
import time
from datetime import datetime as dt
from datetime import timedelta as td
import Adafruit_ADS1x15

GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False)
url = "https://api.powerbi.com/beta/01c4d789-4148-49f6-8723-7f73c88d38af/datasets/7e0e52e4-5d18-4223-b81d-7b04cdb4a5d2/rows?key=L0oAg1YhLY0gWydH834GClS7ljPqASgmOfo65jRa%2Fc2lMtlhhspjPSQP1kZNIlvfKG9IS70GfZXk%2BTFsmOBq1Q%3D%3D"
headers = {
  "Content-Type": "application/json"
  }

# connect the client.
adc = Adafruit_ADS1x15.ADS1115()

from Adafruit_GPIO import I2C
tca = I2C.get_i2c_device(address=0x70)

import board
import adafruit_ahtx0  
    
Galon = 20
BombaAgua2 = 16
BombaAgua1 = 26

GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False)
GPIO.setup(Galon,GPIO.OUT)
GPIO.setup(BombaAgua1,GPIO.OUT)
GPIO.setup(BombaAgua2,GPIO.OUT)

def get_devices():
    device = AtlasI2C()
    device_address_list = device.list_i2c_devices()
    device_list = []
    
    for i in device_address_list:
        device.set_i2c_address(i)
        response = device.query("I")
        moduletype = response.split(",")[1] 
        response = device.query("name,?").split(",")[1]
        device_list.append(AtlasI2C(address = i, moduletype = moduletype, name = response))
    return device_list
def read_to_float(result):
    
    x = re.findall(r'\b\d+\b',result)
    if len(x) >1:
        value = x[0]+"."+x[1]
    else:
        value = x[0]        
    return value

def read(user_cmd,device,device_list):
    READ = 0
    if user_cmd.upper().strip().startswith("LIST"):
        print_devices(device_list, device)
            
    elif user_cmd.upper().startswith("HELP"):
        print_help_text()
            
    elif user_cmd.upper().strip().startswith("POLL"):
        cmd_list = user_cmd.split(',')
        if len(cmd_list) > 1:
            delaytime = float(cmd_list[1])
        else:
            delaytime = device.long_timeout

        if delaytime < device.long_timeout:
            print("Polling time is shorter than timeout, setting polling time to %0.2f" % device.long_timeout)
            delaytime = device.long_timeout
        try:
            while True:
                print("-------press ctrl-c to stop the polling")
                for dev in device_list:
                    dev.write("R")
                time.sleep(delaytime)
                for dev in device_list:
                    READ = read_to_float(dev.read())
                    

        except KeyboardInterrupt:
            print("Continuous polling stopped")
            print_devices(device_list, device)
              
    elif user_cmd.upper().strip().startswith("ALL:"):
        cmd_list = user_cmd.split(":")
        for dev in device_list:
            dev.write(cmd_list[1])
            
        timeout = device_list[0].get_command_timeout(cmd_list[1].strip())
        if(timeout):
            time.sleep(timeout)
            for dev in device_list:

                READ = read_to_float(dev.read())

    else:
        try:
            cmd_list = user_cmd.split(":")
            if(len(cmd_list) > 1):
                addr = cmd_list[0]
                switched = False
                for i in device_list:
                    if(i.address == int(addr)):
                        device = i
                        switched = True
                if(switched):
                    READ =device.query(cmd_list[1])
                    READ = read_to_float(READ)
                   
                    
                else:
                    print("No device found at address " + addr)
            else:
                    # if no address change, just send the command to the device
                print(device.query(user_cmd))
        except IOError:
            print("Query failed \n - Address may be invalid, use list command to see available addresses")
    return READ
def CO2(device_list):
    if len(device_list) == 0:
        CO2 = 400
    else:
        device = device_list[0]
        CO2 =read("105:R",device,device_list)

    return float(CO2)
       
def control_CO2(now1,CO2,co2cont):
    print(now1)
    if co2cont < 6:
        if now1.today().weekday() == 3 or now1.today().weekday() == 1 :
            co2_min = 600
            print("Rango de CO2: 600-700")
        else :
            co2_min = 400
            print("Rango de CO2: 400-600")
            
        if 11 <= now1.hour <=14:  
            if float(CO2) < co2_min:
                GPIO.output(Galon, GPIO.LOW)
                print("Galon de CO2 abierto por "+str(co2cont+1)+"vez")
                time.sleep(60)
                GPIO.output(Galon, GPIO.HIGH)
            else:
                GPIO.output(Galon, GPIO.HIGH)
        else:
            pass
        co2cont = co2cont +1
    else:
        pass
    
def main():
    #GPIO.output(BombaAgua, GPIO.LOW)
    GPIO.output(Galon, GPIO.HIGH)
    print("INICIO DEL PROGRAMA")
    GPIO.output(Galon, GPIO.LOW)
    time.sleep(120)

    GPIO.output(Galon, GPIO.HIGH)
    while 1:
        try:
            device_list = get_devices()
            X = CO2(device_list)
        except:
            X = 400
        print(X)
            
            
        
        

                    
if __name__ == '__main__':
    main()