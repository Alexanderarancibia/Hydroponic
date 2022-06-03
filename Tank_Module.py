#!/usr/bin/python3
import hydrolib as hy
import RPi.GPIO as GPIO
import time
import copy
import re
import requests
import json
import string
import os, glob, time, sys
import io
from datetime import datetime,date, timedelta
import Adafruit_ADS1x15  
from pytz import timezone
import sys



# connect the client.

def main():
    
    print("INICIO DEL PROGRAMA")
    inicio = hy.setup()  #Inicializacion de las Salidas Digitales
    now1,now = hy.tiempo()
    numero_dias, numero_semanas = hy.dias_semanas(now1,inicio)
    modulo = hy.modulo()
    device_list = hy.get_devices()    #Lista de los Dispositivos Atlas I2C conectados
    T1,T2 = hy.read_temp()   #Lectura de la Temperatura
    reporte = ""
    PH, EC, errorPH,errorEC,reporte = hy.PH_EC(device_list,reporte,T1)    #Lectura del PH y EC
    VolumenAgua, reporte= hy.nivel_bajo(reporte)   # Control del nivel Bajo de Agua

    data = [
        {
        "PH" :PH,
        "EC" :EC,
        "TAgua" :T1,
        "Timestamp" :now,
        "DiasTranscurridos" :numero_dias,
        "Modulo" :modulo ,
        "VolumenAgua": VolumenAgua,
        "Reporte": reporte[2:]

        }
        ]
    print("lectura inicial: ", data)
    hy.send_data(data)    #Envio de Datos al Power BI
    

    while True:
        #try:
            print("__________________________________________")      
                 
            now1,now = hy.tiempo()
            numero_dias, numero_semanas = hy.dias_semanas(now1,inicio)
            #Lectura de Datos del tanque
            reporte= ""
            PH, EC, errorPH,errorEC,reporte = hy.PH_EC(device_list,reporte,T1)
            VolumenAgua,reporte = hy.control_bombas(PH,EC,numero_semanas,errorPH,errorEC,reporte)
            T1,T2= hy.read_temp()

            data = [
                {
                "PH" :PH,
                "EC" :EC,
                "TAgua" :T1,
                "Timestamp" :now,
                "DiasTranscurridos" :numero_dias,
                "Modulo" :modulo,
                "VolumenAgua":VolumenAgua,
                "Reporte": reporte[2:]
                }
                ]
            hy.send_data(data)

            print("mensaje enviado: ", data)
            time.sleep(600)
            hy.reset()
            

        #except:
         #   os.execv(sys.executable, ['python3'] + sys.argv)
         #   print("HUBO UN ERROR EN EL PROGRAMA!!!")
            
        
        

                    
if __name__ == '__main__':
    main()
