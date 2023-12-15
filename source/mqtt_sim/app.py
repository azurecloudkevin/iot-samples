# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
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

# pip install pandas
# pip install paho-mqtt

import csv
import os
from pathlib import Path
import time
from paho.mqtt import client as mqtt_client
from datetime import datetime
import random
import json
from dotenv import load_dotenv

env = f"{Path(__file__).parents[2]}\\.env"

load_dotenv(env)

cert_path = os.getenv('sim_cert_path')
key_path = os.getenv('sim_key_path')
mqtt_host = os.getenv('ingest_mqtt_host')
mqtt_port = int(os.getenv('ingest_mqtt_port'))
mqtt_topic = os.getenv('ingest_mqtt_topic')
mqtt_user = os.getenv('sim_mqtt_user')

OMNI_HOST = os.environ.get("OMNI_HOST", "localhost")
BASE_URL = "omniverse://" + OMNI_HOST + "/Projects/OVPOC/Stages"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONTENT_DIR = Path(SCRIPT_DIR).resolve().parents[1].joinpath("content")

messages = []


def log_handler(thread, component, level, message):
    # print(message)
    messages.append((thread, component, level, message))


def start_sim(mqtt_client: mqtt_client):
    count = 0
    alert_enabled = False
    while (True):
        with open(SCRIPT_DIR + "\\pos.csv", 'r', encoding='UTF-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                try:
                    date = str(datetime.now())
                    payload = {}
                    payload["TimeStamp"] = date
                    payload["payload"] = {}
                    payload["dataSetWriterName"] = 'Robot'
                    payload["payload"]["dtmi:com:example:Magnemotion;1:LoadingCycleCount"] = {}
                    payload["payload"]["dtmi:com:example:Magnemotion;1:UnloadingCycleCount"] = {}
                    payload["payload"]["dtmi:com:example:Magnemotion;1:LoadedCounterPowerOn"] = {}
                    payload["payload"]["dtmi:com:example:Magnemotion;1:VacuumPressure"] = {}
                    payload["payload"]["dtmi:com:example:Magnemotion;1:Quality"] = {}
                    payload["payload"]["dtmi:com:example:Magnemotion;1:Fault"] = {}
                    payload["payload"]["dtmi:com:example:Magnemotion;1:Vacuum_Alert"] = {}
                    payload["payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ0"] = {}
                    payload["payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ1"] = {}
                    payload["payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ2"] = {}
                    payload["payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ3"] = {}
                    payload["payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ4"] = {}
                    payload["payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ5"] = {}
                    populate_payload(payload, "dtmi:com:example:Magnemotion;1:LoadingCycleCount", float(50))
                    populate_payload(payload, "dtmi:com:example:Magnemotion;1:UnloadingCycleCount", float(50))
                    populate_payload(payload, "dtmi:com:example:Magnemotion;1:LoadedCounterPowerOn", float(1))

                    if count % 100 == 0:
                        alert_enabled = not alert_enabled

                    if alert_enabled:
                        populate_payload(payload, "dtmi:com:example:Magnemotion;1:VacuumPressure", float(0))
                        populate_payload(payload, "dtmi:com:example:Magnemotion;1:Vacuum_Alert", float(1))
                    else:
                        populate_payload(payload, "dtmi:com:example:Magnemotion;1:VacuumPressure", float(1))
                        populate_payload(payload, "dtmi:com:example:Magnemotion;1:Vacuum_Alert", float(0))

                    populate_payload(payload, "dtmi:com:example:Magnemotion;1:Quality", float(1))
                    populate_payload(payload, "dtmi:com:example:Magnemotion;1:Fault", float(1))
                    populate_payload(payload, "dtmi:com:example:Magnemotion;1:RobotPositionJ0", float(row[0]))
                    populate_payload(payload, "dtmi:com:example:Magnemotion;1:RobotPositionJ1", float(row[1]))
                    populate_payload(payload, "dtmi:com:example:Magnemotion;1:RobotPositionJ2", float(row[2]))
                    populate_payload(payload, "dtmi:com:example:Magnemotion;1:RobotPositionJ3", float(row[3]))
                    populate_payload(payload, "dtmi:com:example:Magnemotion;1:RobotPositionJ4", float(row[4]))
                    populate_payload(payload, "dtmi:com:example:Magnemotion;1:RobotPositionJ5", float(row[5]))
                    mqtt_client.publish(mqtt_topic, json.dumps(payload, indent=2).encode("utf-8"))
                    count = count + 1
                except ValueError:
                    continue
                time.sleep(.1)


def populate_payload(payload: dict, path: str, val: float):
    payload["payload"][path]["Value"] = val
    payload["payload"][path]["SourceTimeStamp"] = payload["TimeStamp"]


# connect to mqtt broker
def connect_mqtt():
    topic = mqtt_topic

    # called when a message arrives
    def on_message(client, userdata, msg):
        msg_content = msg.payload.decode()
        print(f"Received `{msg_content}` from `{msg.topic}` topic")

    # called when connection to mqtt broker has been established
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            # connect to our topic
            print(f"Subscribing to topic: {topic}")
            client.subscribe(topic)
        else:
            print(f"Failed to connect, return code {rc}")

    # let us know when we've subscribed
    def on_subscribe(client, userdata, mid, granted_qos):
        print(f"subscribed {mid} {granted_qos}")

    # Set Connecting Client ID
    client = mqtt_client.Client(f"python-mqtt-{random.randint(0, 1000)}")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    client.username_pw_set(username=mqtt_user)
    client.tls_set(
        certfile=cert_path,
        keyfile=key_path
    )
    client.connect(mqtt_host, mqtt_port)
    client.loop_start()
    return client


if __name__ == "__main__":
    mqtt_client = connect_mqtt()
    start_sim(mqtt_client)
