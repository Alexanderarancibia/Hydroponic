import os, glob, time, sys
import io
from datetime import datetime,date, timedelta
from pytz import timezone
import time
import sys
import random
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
class message:
    def __init__(self):
        self.payload = "{"
    def addData(self, argument,value):
        if isinstance(value, str) == True:
            self.payload = self.payload+'"{}":"{}",'.format(argument,value)
        else:
            self.payload = self.payload+'"{}":{},'.format(argument,value)
    def endData(self):
        self.payload =self.payload[:-1]+ "}"

clientID = "CO2"
endpoint = "a2v4k4vgiu7b77-ats.iot.us-east-2.amazonaws.com"
root = "/home/pi/Documents/Hydroponic/certs/RootCA1.pem"
privatekey = "/home/pi/Documents/Hydroponic/certs/private.pem.key"
certificate = "/home/pi/Documents/Hydroponic/certs/certificate.pem.crt"
myMQTTClient = AWSIoTMQTTClient(clientID)
myMQTTClient.configureEndpoint(endpoint,8883)
myMQTTClient.configureCredentials(root, privatekey,certificate )
Myvar= myMQTTClient.connect()
def on_message_received(client, userdata, message) :
    print('message: ')
    print(message.payload)
    print('topic: ')
    print(message.topic)
    print('--------------')
    
def publish(topicpublish,msg,qos):
    myMQTTClient.publish(topicpublish,msg,qos)
def subscribe(topicsubscribe,qos): 
    myMQTTClient.subscribe(topicsubscribe, qos,on_message_received)

if __name__ == "__main__":
    print("Ga")

    print(round(2345.1252342,4))
 
