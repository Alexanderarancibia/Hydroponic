import os, glob, time, sys
import io
from datetime import datetime,date, time, timedelta
import Adafruit_ADS1x15  
from pytz import timezone
import sys
import digitalio
import board
import fcntl
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

import json

import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None
BAUDRATE = 64000000
spi = board.SPI()
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=240,
    height=240,
    x_offset=0,
    y_offset=80,
)
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 180
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
padding = -2
top = padding
bottom = height - padding
x = 0
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

VolumenAgua = 0

Nutriente1 = digitalio.DigitalInOut(board.D12)
Nutriente1.switch_to_output()
Nutriente2=digitalio.DigitalInOut(board.D6)
Nutriente2.switch_to_output()
ReductorPH= digitalio.DigitalInOut(board.D13)
ReductorPH.switch_to_output()
ElevadorPH=digitalio.DigitalInOut(board.D21)
ElevadorPH.switch_to_output()
ValvulaAgua = digitalio.DigitalInOut(board.D20)
ValvulaAgua.switch_to_output()
Mezclador1 = digitalio.DigitalInOut(board.D16)
Mezclador1.switch_to_output()
Rele7 = digitalio.DigitalInOut(board.D26)
Rele7.switch_to_output()
BombaAgua = digitalio.DigitalInOut(board.D19)
BombaAgua.switch_to_output()
buttonA = digitalio.DigitalInOut(board.D23)
buttonA.switch_to_input()
buttonB = digitalio.DigitalInOut(board.D24)
buttonB.switch_to_input()
NivelBajo = digitalio.DigitalInOut(board.D18)
NivelBajo.switch_to_input()
SensorNivel= digitalio.DigitalInOut(board.D7)
SensorNivel.switch_to_input()


def data_display():
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d' ' -f1"
    IP = "IP: " + subprocess.check_output(cmd, shell=True).decode("utf-8")
    with open('reporte.txt') as f:
        report = f.readlines()
    report = json.loads(report[0])
 
    y = top
    draw.text((x, y), IP, font=font, fill="#FFFFFF")
    y += font.getsize(IP)[1]
    draw.text((x, y),str(report['@timestamp'][2:]), font=font, fill="#FF0FFF")
    y += font.getsize(str(report['@timestamp']))[1]
    draw.text((x, y), "PH: " + str(report['PH']), font=font, fill="#0000FF")
    y += font.getsize("PH: " + str(report['PH']))[1]
    draw.text((x, y), "EC: " + str(report['EC']), font=font, fill="#0000FF")
    y += font.getsize(IP)[1]
    draw.text((x, y), "TAgua: " + str(report['TAgua']), font=font, fill="#0000FF")
    y += font.getsize(IP)[1]
    draw.text((x, y), "Modulo: " + str(report['Modulo']), font=font, fill="#00FF00")
    y += font.getsize(IP)[1]
    reporte = "Reporte :"+report['Reporte']
 
    n = 19  
    for i in range(0, len(reporte), n): 
        draw.text((x, y),reporte[i:i+n], font=font, fill="#FFFFFF")
        y += font.getsize(IP)[1]
        
    # Display image.
    disp.image(image, rotation)


f = open('/home/pi/Documents/Hydroponic/parametros.json')
parameter = json.load(f)

def setup():
    inicio = datetime(parameter["FechaInicio"]["Anio"], parameter["FechaInicio"]["Mes"], parameter["FechaInicio"]["Dia"], 0, 0, 0)
    VolumenAgua = 0
    Nutriente1.value = True
    Nutriente2.value = True
    ValvulaAgua.value = True
    ElevadorPH.value = True
    ReductorPH.value = True
    BombaAgua.value = True
    Mezclador1.value = True
    Rele7.value = True
   
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
    cont = 0
    if GPIO.input(Nivelbajo):
        reporte += ", Nivel bajo de agua, "
        for i in range(10):
            if SensorNivel.value == True:
                print("NIVEL DE AGUA BAJO!!!") 
                BombaAgua.value = False
                ValvulaAgua.value = False
                VolumenAgua = VolumenAgua + 1000
                cont = cont + 1
                time.sleep(20)
                estado = ""
            else:
                print("Nivel de agua normal") 
                BombaAgua.value = True
                ValvulaAgua.value = True
                estado = "(Nivel Maximo)"
                break
            reporte += "Bomba de agua prendida"+str(cont*20)+"segundos, "+estado

        BombaAgua.value = True
        ValvulaAgua.value = True
        
    
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
    if SensorNivel.value == False:
        reporte += ", Nivel elevado de Agua"
        
        print("Nivel elevado de agua")
    else:
        print("Nivel Normal de agua")
        if float(EC) >EC_max and errorEC == False :
            x = float(EC) - EC_max
            print("Bomba de Agua activada")
            BombaAgua.value = False
            ValvulaAgua.value = False
            tiempo = round(parameter["Parametros_EC"][1]["BombaAgua"]*funcEC(x),2)
            time.sleep(tiempo)
            reporte += ", Bomba de agua activada: "+str(tiempo)+" segundos"
            BombaAgua.value = True
            ValvulaAgua.value = True
            print("Bomba de Agua desactivada")
            VolumenAgua = parameter["Parametros_EC"][1]["VolumenAgua"]*funcEC(x)*parameter["Parametros_EC"][1]["BombaAgua"]
        elif float(EC) <EC_min and errorEC == False :
            x = EC_min - float(EC) 
            GPIO.output(Mezclador1, GPIO.LOW)
            Mezclador1.value = False
            time.sleep(10)
            Nutriente1.value = False
            print("Bomba de Nutriente1 activada")
            tiempo1 = round(parameter["Parametros_EC"][1]["BombaNutriente1"]*funcEC(x),2)
            tiempo2 = round(parameter["Parametros_EC"][1]["BombaNutriente2"]*funcEC(x),2)
            time.sleep(tiempo1- tiempo2)
            Nutriente2.value = False
            print("Bomba de Nutriente2 activada")
            time.sleep(tiempo2)
            Nutriente1.value = True
            Nutriente2.value = True
            Mezclador1.value = True
            print("Bombas de Nutrientes desactivada")
            reporte += ", Bomba de agua Nutriente 1 activada: "+str(tiempo1)+" segundos"
            reporte += ", Bomba de agua Nutriente 2 activada: "+str(tiempo2)+" segundos"
                
        else:
            Nutriente1.value = True
            Nutriente2.value = True
            Mezclador1.value = True
            BombaAgua.value = True
            ValvulaAgua.value = True
         
    if float(PH) >parameter["Parametros_PH"]["Rango_PH"][1] and errorPH == False:
        x = float(PH) - parameter["Parametros_PH"]["Rango_PH"][1]
        ReductorPH.value = False
        print("Bomba Reductora activada")
        tiempo = round(parameter["Parametros_PH"]["BombaReductor"]*funcPH(x),2)
        time.sleep(tiempo)
        reporte += ", Bomba Reductora activada: "+str(tiempo)+" segundos"
        ReductorPH.value = True
        print("Bomba Reductora desactivada")
   
    elif float(PH) < parameter["Parametros_PH"]["Rango_PH"][0] and errorPH == False:
        x = parameter["Parametros_PH"]["Rango_PH"][1] - float(PH)
        ElevadorPH.value = False
        print("Bomba Elevadora de PH activada")
        tiempo = round(parameter["Parametros_PH"]["BombaElevador"]*funcPH(x),2)
        time.sleep(tiempo)
        reporte += ", Bomba Elevadora activada: "+str(tiempo)+" segundos"
        ElevadorPH.value = True
        print("Bomba Elevadora de PH desactivada")
    else:
        ElevadorPH.value = True
        ReductorPH.value = True
    return VolumenAgua,reporte

def reset():
    f = open('/home/pi/Documents/Hydroponic/parametros.json')
    parameter = json.load(f)
    f.close()


