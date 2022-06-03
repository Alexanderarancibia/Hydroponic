import os, glob, time, sys
import io
from datetime import datetime,date, time, timedelta
import Adafruit_ADS1x15  
from pytz import timezone
import sys

import fcntl
import RPi.GPIO as GPIO
import time
import copy
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
from datetime import datetime as dt
from datetime import timedelta as td




Nutriente1 = 12
Nutriente2=6
ReductorPH= 13
ElevadorPH=21
ValvulaAgua = 20
SensorNivel = 16
Nivelbajo = 26
BombaAgua = 19
VolumenAgua = 0
GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False)
GPIO.setup(ValvulaAgua,GPIO.OUT)
GPIO.setup(Nutriente1,GPIO.OUT)
GPIO.setup(Nutriente2,GPIO.OUT)
GPIO.setup(ReductorPH,GPIO.OUT)
GPIO.setup(ElevadorPH,GPIO.OUT)
GPIO.setup(SensorNivel,GPIO.IN)
GPIO.setup(Nivelbajo,GPIO.IN)
GPIO.setup(BombaAgua,GPIO.OUT)
f = open('/home/pi/Documents/Hydroponic/parametros.json')
parameter = json.load(f)

def setup():
    inicio = datetime(parameter["FechaInicio"]["Año"], parameter["FechaInicio"]["Mes"], parameter["FechaInicio"]["Dia"], 0, 0, 0)
    VolumenAgua = 0
     
    GPIO.output(Nutriente1, GPIO.HIGH)
    GPIO.output(Nutriente2, GPIO.HIGH)
    GPIO.output(ValvulaAgua, GPIO.HIGH)
    GPIO.output(ElevadorPH, GPIO.HIGH)
    GPIO.output(ReductorPH, GPIO.HIGH)
    GPIO.output(BombaAgua, GPIO.HIGH)
    return inicio
    
def read_temp():
    try:
        device_folder = glob.glob('/sys/bus/w1/devices/28*')
        temp = [25,25]
        for i in range(len(device_folder)):   
            device_file = device_folder[i] + '/w1_slave'
            f = open(device_file, 'r')
            lines = f.readlines()
            f.close()
            if lines[0].strip()[-3:] == 'YES':
                equals_pos = lines[1].find('t=')
                temp[i] = float(lines[1][equals_pos+2:])/1000
            else:
                temp[i] =-1
        return temp
    except IndexError:
        temp = [25,25]
    return temp

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
def PH_EC(device_list,reporte ,T=25):
    errorPH = False
    errorEC = False
    
    if len(device_list) == 0:
        PH , EC = 7,16000
    else:
        device = device_list[0]
        #PH, EC,CO2 =read("ALL:RT,"+str(T),device,device_list)
    try: 
        PH =read("99:RT,"+str(T),device,device_list)
        
    except:
        errorPH = True
        reporte += ", Fallo Sensor PH"
        PH = 7
    try:
        EC =read("100:RT,"+str(T),device,device_list)
        
    except:
        errorEC = True
        EC = 16000
        reporte += ", Fallo Sensor EC"
       
    return float(PH), float(EC)/10, errorPH, errorEC,reporte 

def tiempo():
    #año mes dia
    
    now1 =datetime.now(timezone('Etc/GMT+5'))
    now = datetime.strftime(now1,
    "%Y-%m-%dT%H:%M:%S")
    return now1,now

def dias_semanas(now1,inicio):
    numero_dias= (30*(now1.month-inicio.month)+now1.day-inicio.day)
    numero_semanas = numero_dias/7
    return numero_dias, numero_semanas

def modulo():
    return parameter["Modulo"]
def nivel_bajo(reporte):
    VolumenAgua = 0
    if GPIO.input(Nivelbajo):
        reporte += ", Nivel bajo de agua"
        for i in range(8):
            if GPIO.input(SensorNivel) == True:
                print("NIVEL DE AGUA BAJO!!!") 
                GPIO.output(BombaAgua, GPIO.LOW)
                GPIO.output(ValvulaAgua, GPIO.LOW)
                VolumenAgua = VolumenAgua + 1000
                time.sleep(60)
            else:
                print("Nivel de agua normal") 
                GPIO.output(BombaAgua, GPIO.HIGH)
                GPIO.output(ValvulaAgua, GPIO.HIGH)
                reporte += " regulado"
                break

        GPIO.output(BombaAgua, GPIO.HIGH)
        GPIO.output(ValvulaAgua, GPIO.HIGH)
    
    return VolumenAgua,reporte
def funcPH(x):
    return max((2*x/pow((1+4*pow(x,2)),0.5)),0.4)

def funcEC(x):
    return max((0.006*x/pow((1+0.000036*pow(x,2)),0.5)),0.4)

def control_bombas(PH,EC,numero_semanas,errorPH,errorEC,reporte):
    #if numero_semanas < 0.5:
    #    break
    
    print(numero_semanas)
    if numero_semanas<1:
        EC_min = parameter["Parametros_EC"][0]["Semana1_EC"][0]
        EC_max = parameter["Parametros_EC"][0]["Semana1_EC"][1]
    elif 1 <= numero_semanas<2:
        EC_min = parameter["Parametros_EC"][0]["Semana1_EC"][0]
        EC_max = parameter["Parametros_EC"][0]["Semana2_EC"][1]
    elif 2 <=  numero_semanas<3:
        EC_min = parameter["Parametros_EC"][0]["Semana3_EC"][0]
        EC_max = parameter["Parametros_EC"][0]["Semana3_EC"][1]
    elif 3 <=  numero_semanas<4:
        EC_min = parameter["Parametros_EC"][0]["Semana4_EC"][0]
        EC_max = parameter["Parametros_EC"][0]["Semana4_EC"][1]
    elif 4 <=  numero_semanas<10:
        EC_min = parameter["Parametros_EC"][0]["Semana5_EC"][0]
        EC_max = parameter["Parametros_EC"][0]["Semana5_EC"][1]

    else:
        EC_min = parameter["Parametros_EC"][0]["Semana6_EC"][0]
        EC_max = parameter["Parametros_EC"][0]["Semana6_EC"][1]
    print("EC min : ", EC_min)
    print("EC max : ", EC_max)
     
    VolumenAgua = 0
    
    if GPIO.input(SensorNivel) == False:
        reporte += ", Nivel elevado de Agua"
        
        print("Nivel elevado de agua")
    else:
        print("Nivel Normal de agua")
        if float(EC) >EC_max and errorEC == False :
            x = float(EC) - EC_max
            print("Bomba de Agua activada")
            GPIO.output(BombaAgua, GPIO.LOW)
            GPIO.output(ValvulaAgua, GPIO.LOW)
            tiempo = parameter["Parametros_EC"][1]["BombaAgua"]*funcEC(x)
            time.sleep(tiempo)
            reporte += ", Bomba de agua activada: "+str(tiempo)+" segundos"
            GPIO.output(BombaAgua, GPIO.HIGH)
            GPIO.output(ValvulaAgua, GPIO.HIGH)
            print("Bomba de Agua desactivada")
            VolumenAgua = parameter["Parametros_EC"][1]["VolumenAgua"]*funcEC(x)*parameter["Parametros_EC"][1]["BombaAgua"]
        elif float(EC) <EC_min and errorEC == False :
            x = EC_min - float(EC) 
            GPIO.output(Nutriente1, GPIO.LOW)
            print("Bomba de Nutriente1 activada")
            tiempo1 = parameter["Parametros_EC"][1]["BombaNutriente1"]*funcEC(x)
            tiempo2 = parameter["Parametros_EC"][1]["BombaNutriente2"]*funcEC(x)
            time.sleep(tiempo1- tiempo2)
            GPIO.output(Nutriente2, GPIO.LOW)
            print("Bomba de Nutriente2 activada")
            time.sleep(tiempo2)
            GPIO.output(Nutriente1, GPIO.HIGH)
            GPIO.output(Nutriente2, GPIO.HIGH)
            print("Bombas de Nutrientes desactivada")
            reporte += ", Bomba de agua Nutriente 1 activada: "+str(tiempo1)+" segundos"
            reporte += ", Bomba de agua Nutriente 2 activada: "+str(tiempo2)+" segundos"
                
        else:
            GPIO.output(Nutriente1, GPIO.HIGH)
            GPIO.output(Nutriente2, GPIO.HIGH)
            GPIO.output(BombaAgua, GPIO.HIGH)
            GPIO.output(ValvulaAgua, GPIO.HIGH)    
    
    if float(PH) >parameter["Parametros_PH"]["Rango_PH"][1] and errorPH == False:
        x = float(PH) - parameter["Parametros_PH"]["Rango_PH"][1]
        GPIO.output(ReductorPH, GPIO.LOW)
        print("Bomba Reductora activada")
        tiempo = parameter["Parametros_PH"]["BombaReductor"]*funcPH(x)
        time.sleep(tiempo)
        reporte += ", Bomba Reductora activada: "+str(tiempo)+" segundos"
        GPIO.output(ReductorPH, GPIO.HIGH)
        print("Bomba Reductora desactivada")
   
    elif float(PH) < parameter["Parametros_PH"]["Rango_PH"][0] and errorPH == False:
        x = parameter["Parametros_PH"]["Rango_PH"][1] - float(PH)
        GPIO.output(ElevadorPH, GPIO.LOW)
        print("Bomba Elevadora de PH activada")
        tiempo = parameter["Parametros_PH"]["BombaElevador"]*funcPH(x)
        time.sleep(tiempo)
        reporte += ", Bomba Elevadora activada: "+str(tiempo)+" segundos"
        GPIO.output(ElevadorPH, GPIO.HIGH)
        print("Bomba Elevadora de PH desactivada")
    else:
        GPIO.output(ReductorPH, GPIO.HIGH)
        GPIO.output(ElevadorPH, GPIO.HIGH)
    time.sleep(600)
    return VolumenAgua,reporte

def send_data(data):
    url = "https://api.powerbi.com/beta/01c4d789-4148-49f6-8723-7f73c88d38af/datasets/0aba6e3c-fcbe-4094-9dfb-e9b7c847de8b/rows?key=unvXnB4CFgEUZx1snfOLsQClNcEfVO%2BikaW9FrATpzhNjaHm1ULnlRAkREtP9yj6tmXYfAuizrMWtYSRceM5%2Fg%3D%3D"
    headers = {
    "Content-Type": "application/json"
    }
    response = requests.request(
                method="POST",
                url=url,
                headers=headers,
                data=json.dumps(data))
    
def reset():
    f = open('/home/pi/Documents/Hydroponic/parametros.json')
    parameter = json.load(f)
    f.close()
