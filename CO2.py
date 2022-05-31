#!/usr/bin/python3
import co2lib as co
import threading
import random
import time
import time
import copy

# connect the client.

def main():
    co2cont = 0
    reporte = ""

    while 1:
        reporte = ""
        reporte = co.PLCinit(3,0x77,reporte)
        print("INICIO DEL PROGRAMA")
        now1, now = co.tiempo()
            
        HumP1 = co.HumPiso(0)
        HumP2 = "Seco"
        HumP3 = co.HumPiso(2)
        HumP4 = co.HumPiso(3)   
        HumA1,TemA1 = co.AHT(0)
        HumA2,TemA2 = co.AHT(1)
        HumA3,TemA3 = co.AHT(2)
        X,reporte = co.CO2(reporte)
        co2cont = co.control_CO2(now1,X,co2cont)
        reporte, mojado = co.controlbombas(HumP1,HumP2,HumP3,HumP4,reporte)
        data = [
        {
            "CO2":X,
            "HumP1":HumP1,
            "HumP2":HumP2,
            "HumP3":HumP3,
            "HumP4":HumP4,
            "HumA1":HumA1,
            "HumA2":HumA2,
            "HumA3":HumA3,
            "TemA1":TemA1,
            "TemA2":TemA2,
            "TemA3":TemA3,
            "Dispositivo":"CO2",
            "Timestamp" :now,
            "Reporte": reporte
        }
        ]
        co.send_data(data)
        print("mensaje enviado: ", data)
        if mojado ==1:
            time.sleep(3000)
        else:
            time.sleep(600)
    
        #except:
         #   os.execv(sys.executable, ['python3'] + sys.argv)
                             
if __name__ == '__main__':
    main()