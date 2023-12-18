# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subRobotPositionJect to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import pandas as pd
import time
import paho.mqtt.client as mqtt_client
import random
import json


# connect to mqtt broker
def connect_mqtt(iot_topic):
    topic = f"{iot_topic}"    
    # called when a message arrives
    def on_message(client, userdata, msg):
        msg_content = msg.payload.decode()
        print(f"Received `{msg_content}` from `{msg.topic}` topic")

    # called when connection to mqtt broker has been established
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            # connect to our topic
            print(f"Connected to MQTT Broker!")
            #client.subscribe(topic)
        else:
            print(f"Failed to connect, return code {rc}")

    # let us know when we've subscribed
    def on_subscribe(client, userdata, mid, granted_qos):
        print(f"subscribed {mid} {granted_qos} {userdata}")

    # Set Connecting Client ID
    client = mqtt_client.Client(f"python-mqtt-{random.randint(0, 1000)}")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.username_pw_set(username='sdm-authn-ID')
    client.tls_set(
    certfile='C:\\Users\\murphysean\\Downloads\\sdm-authn-ID.pem',
    keyfile='C:\\Users\\murphysean\\Downloads\\sdm-authn-ID.key'
    )
    result = client.connect("simulated-plant-eg.eastus-1.ts.eventgrid.azure.net", 8883)
    client.loop_start()
    return client

# publish to mqtt broker
def write_to_mqtt(mqtt_client, iot_topic, group, seq):
    
    payload = {}
    
    for index, row in group.iterrows():
        payload["Timestamp"] = row["TimeStamp"] 
        payload["Payload"] = {}              
        payload["Payload"]["RobotPositionJ0"]= {}
        payload["Payload"]["RobotPositionJ0"]["Value"] = row["x"]
        payload["Payload"]["RobotPositionJ0"]["SouceTimestamp"] = row["TimeStamp"]
        payload["Payload"]["RobotPositionJ1"]= {}
        payload["Payload"]["RobotPositionJ1"]["Value"] = row["y"]
        payload["Payload"]["RobotPositionJ1"]["SouceTimestamp"] = row["TimeStamp"]
        payload["Payload"]["RobotPositionJ2"]= {}
        payload["Payload"]["RobotPositionJ2"]["Value"] = row["z"]
        payload["Payload"]["RobotPositionJ2"]["SouceTimestamp"] = row["TimeStamp"]
        payload["Payload"]["RobotPositionJ3"]= {}
        payload["Payload"]["RobotPositionJ3"]["Value"] = row["o"]
        payload["Payload"]["RobotPositionJ3"]["SouceTimestamp"] = row["TimeStamp"]
        payload["Payload"]["RobotPositionJ4"]= {}
        payload["Payload"]["RobotPositionJ4"]["Value"] = row["a"]
        payload["Payload"]["RobotPositionJ4"]["SouceTimestamp"] = row["TimeStamp"]
        payload["Payload"]["RobotPositionJ5"]= {}
        payload["Payload"]["RobotPositionJ5"]["Value"] = row["t"]
        payload["Payload"]["RobotPositionJ5"]["SouceTimestamp"] = row["TimeStamp"]
        payload["DataSetWriterName"] = "robot"
        payload["SequenceNumber"] = seq
        
    mqtt_client.publish(iot_topic, json.dumps(payload, indent=2).encode("utf-8"))   
    
    print(f"Published `{payload}` to topic `{iot_topic}`")
    
    
import pandas as pd
from datetime import datetime, timedelta

def add_timestamp(filename):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(filename)

    # Get the current time
    current_time = datetime.now()

    # Create a list to hold the timestamps
    timestamps = []

    # For each row in the DataFrame, create a timestamp and add it to the list
    for _ in df.index:
        timestamps.append(current_time)
        current_time += timedelta(milliseconds=1000)

    # Add the list of timestamps as a new column in the DataFrame
    df['Timestamp'] = timestamps

    # Save the DataFrame back to the CSV file
    df.to_csv(filename, index=False)

# Call the function with the name of your CSV file



def run(iot_topic, filepath):
    # we assume that the file contains the data for single device
    data = pd.read_csv(filepath)
    data.head()

    # Converting to DateTime Format and drop ms
    #data["TimeStamp"] = pd.to_datetime(data["TimeStamp"])
    #data["TimeStamp"] = data["TimeStamp"].dt.floor("s")

    data.set_index("TimeStamp")
    start_time = data.min()["TimeStamp"]
    last_time = start_time
    grouped = data.groupby("TimeStamp")

    mqtt_client = connect_mqtt(iot_topic)

    # play back the data in real-time
    seq = 0
    for next_time, group in grouped:
        time.sleep(1)
        seq = seq + 1   
        write_to_mqtt(mqtt_client, iot_topic, group, seq)
    last_time = next_time

    mqtt_client = None


def add_timestamp_column(filepath):
    # Read the existing CSV file
    data = pd.read_csv(filepath)

    # Get the current UTC time
    current_time = datetime.utcnow()

    # Create a list of timestamps
    timestamps = [current_time + timedelta(milliseconds=i*100) for i in range(len(data))]

    # Add the timestamps as a new column in the DataFrame
    data['TimeStamp'] = timestamps

    # Save the DataFrame back to the CSV file
    data.to_csv(filepath, index=False)

if __name__ == "__main__":
    IOT_TOPIC = "alice-springs-solution/data/opc-ua-connector/opc-ua-connector-0/robot"
    try:
        run(IOT_TOPIC, 'C:\\Users\\murphysean\\Downloads\\pos.csv')
        input()
    finally:
        exit()