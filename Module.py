#!/usr/bin/python3
import hydrolib as hy
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
import sendtoaws as aws
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# connect the client.
 
def main():
    contbomba = 0
    print("INICIO DEL PROGRAMA")
    inicio = hy.setup()  #Inicializacion de las Salidas Digitales
    modulo = hy.modulo()
    device_list = hy.get_devices()
    while True:
        #try:
            
            print("__________________________________________")      
                 
            now1,now = hy.tiempo()
            numero_dias, numero_semanas = hy.dias_semanas(now1,inicio)
            #Lectura de Datos del tanque
            reporte= ""
            T1,T2= hy.read_temp()
            PH, EC, errorPH,errorEC,reporte = hy.PH_EC(device_list,reporte,T1)
            if contbomba == 0:
                VolumenAgua,reporte = hy.control_bombas(PH,EC,numero_semanas,errorPH,errorEC,reporte)
                contbomba = contbomba + 1
            elif contbomba == 5:
                contbomba = 0
            msg = aws.message()
            msg.addData("PH",PH)
            msg.addData("EC",EC)
            msg.addData("TAgua",T1)
            msg.addData("@timestamp",now)
            msg.addData("DiasTranscurridos",numero_dias)
            msg.addData("Modulo",modulo)
            msg.addData("VolumenAgua",VolumenAgua)
            msg.addData("Reporte",reporte[2:])
            msg.endData()
            aws.publish("raspberry/modulo3",msg.payload,0)
            
            with open("reporte.txt", "w") as f:
                f.write(msg.payload)
            hy.data_display()
            print(msg.payload)
            
            time.sleep(240)
            hy.reset()
            

        #except:
        #    os.execv(sys.executable, ['python3'] + sys.argv)
        #    print("HUBO UN ERROR EN EL PROGRAMA!!!")
            
        
        

                    
if __name__ == '__main__':
    main()

