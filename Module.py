#!/usr/bin/python3
import hydrolib as hy
import sendtoaws as aws
import time

 
def main():
    aws.subscribe("prueba",1)
    
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
            contbomba = contbomba + 1 
            if contbomba == 1:
                print("Control de Bombas")
                reporte = hy.control_bombas(PH,EC,numero_semanas,errorPH,errorEC,reporte)
                    
                print("Contador:  "+str(contbomba))
 
            elif contbomba == 5:
                contbomba = 0
                VolumenAgua = 0
                print("Reset Contador: "+str(contbomba))
               
            msg = aws.message()
            msg.addData("PH",PH)
            msg.addData("EC",EC)
            msg.addData("TAgua",T1)
            msg.addData("@timestamp",now)
            msg.addData("DiasTranscurridos",numero_dias)
            msg.addData("Modulo",modulo)
            msg.addData("Reporte",reporte[2:])
            msg.endData()
            try:
                aws.publish("raspberry/tanque2",msg.payload,0)

            except:
                pass
            
            with open("reporte.txt", "w") as f:
                f.write(msg.payload)
            print(msg.payload)
            
            time.sleep(10)
            hy.reset()
            

        #except:
        #    os.execv(sys.executable, ['python3'] + sys.argv)
        #    print("HUBO UN ERROR EN EL PROGRAMA!!!")
            
        
        

                    
if __name__ == '__main__':
    main()


