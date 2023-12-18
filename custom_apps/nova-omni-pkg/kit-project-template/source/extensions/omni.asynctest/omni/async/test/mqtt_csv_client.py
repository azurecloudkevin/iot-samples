import csv
from .robotmotion import RobotMotion
import omni
omni.kit.pipapi.install("paho.mqtt")
omni.kit.pipapi.install("asyncio")
omni.kit.pipapi.install("threading")
import paho.mqtt
from paho.mqtt import client as mqtt_client
import random
import json
import time
import os
import asyncio
import threading
from queue import Queue

class MQTTData:
    def __init__(self, pose):
        self.pose = pose
        self.file_name = "C:\Workspaces\pos.csv"
    async def read_csv(self):
        if self.file_name is None:
            print("enviorment variable not set")
            return
        data = {}
 
        with open(self.file_name, 'r', encoding='UTF-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:  
                try:
                    i = float(row[0])
                except ValueError:
                    continue   
                del(row[6])  
                outputarray = [0,0,0,0,0,0]
                for j in range(6):
                    self.pose[j] = float(row[j])    
                # print("point is ", self.pose)
                await asyncio.sleep(1)       

