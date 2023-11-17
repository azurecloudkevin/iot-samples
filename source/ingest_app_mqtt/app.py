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

import asyncio
import os
import omni.client
from pxr import Usd, Sdf
from pathlib import Path
import pandas as pd
from paho.mqtt import client as mqtt_client
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
mqtt_user = os.getenv('ingest_mqtt_user')
iot_topic = os.getenv('iot_topic')

OMNI_HOST = os.environ.get("OMNI_HOST", "localhost")
BASE_URL = "omniverse://" + OMNI_HOST + "/Projects/OVPOC/Stages"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONTENT_DIR = Path(SCRIPT_DIR).resolve().parents[1].joinpath("content")

messages = []


def log_handler(thread, component, level, message):
    # print(message)
    messages.append((thread, component, level, message))


def initialize_device_prim(live_layer, iot_topic):
    iot_root = live_layer.GetPrimAtPath("/iot")
    iot_spec = live_layer.GetPrimAtPath(f"/iot/{iot_topic}")
    if not iot_spec:
        iot_spec = Sdf.PrimSpec(iot_root, iot_topic, Sdf.SpecifierDef, "PickAndPlace Type")
    if not iot_spec:
        raise Exception("Failed to create the IoT Spec.")

    # clear out any attrubutes that may be on the spec
    for attrib in iot_spec.attributes:
        iot_spec.RemoveProperty(attrib)

    IOT_TOPIC_DATA = f"{CONTENT_DIR}/{iot_topic}_iot_data.csv"
    data = pd.read_csv(IOT_TOPIC_DATA)
    data.head()

    # create all the IoT attributes that will be written
    attr = Sdf.AttributeSpec(iot_spec, "Timestamp", Sdf.ValueTypeNames.TimeCode)
    if not attr:
        raise Exception(f"Could not define the attribute: {attr}")

    # infer the unique data points in the CSV.
    # The values may be known in advance and can be hard coded
    grouped = data.groupby("Id")
    for attrName, group in grouped:
        attr = Sdf.AttributeSpec(iot_spec, clean_text(attrName), Sdf.ValueTypeNames.Double)
        if not attr:
            raise Exception(f"Could not define the attribute: {attrName}")

    omni.client.live_process()


def create_live_layer(iot_topic):
    LIVE_URL = f"{BASE_URL}/{iot_topic}.live"

    live_layer = Sdf.Layer.CreateNew(LIVE_URL)
    if not live_layer:
        raise Exception(f"Could load the live layer {LIVE_URL}.")

    iot_root = Sdf.PrimSpec(live_layer, "iot", Sdf.SpecifierDef, "IoT Root")
    live_layer.Save()
    return live_layer


async def initialize_async():
    # copy a the Conveyor Belt to the target nucleus server
    # LOCAL_URL = f"file:{CONTENT_DIR}/ConveyorBelt_{iot_topic}.usd"
    STAGE_URL = f"{BASE_URL}/houston_facility_{iot_topic}.usd"
    # STAGE_URL = f"{BASE_URL}/ConveyorBelt_{iot_topic}.usd"
    LIVE_URL = f"{BASE_URL}/{iot_topic}.live"
    # result = await omni.client.copy_async(
    #     LOCAL_URL,
    #     STAGE_URL,
    #     behavior=omni.client.CopyBehavior.ERROR_IF_EXISTS,
    #     message="Copy Conveyor Belt",
    # )

    stage = Usd.Stage.Open(STAGE_URL)
    if not stage:
        raise Exception(f"Could not load the stage {STAGE_URL}.")

    root_layer = stage.GetRootLayer()
    live_layer = Sdf.Layer.FindOrOpen(LIVE_URL)
    if not live_layer:
        live_layer = create_live_layer(iot_topic)

    found = False
    subLayerPaths = root_layer.subLayerPaths
    for subLayerPath in subLayerPaths:
        if subLayerPath == live_layer.identifier:
            found = True

    if not found:
        root_layer.subLayerPaths.append(live_layer.identifier)
        root_layer.Save()

    initialize_device_prim(live_layer, iot_topic)

    # set the live layer as the edit target
    stage.SetEditTarget(live_layer)
    return stage, live_layer


def write_to_live(live_layer, iot_topic, msg_content):
    # write the iot values to the usd prim attributes
    payload = json.loads(msg_content)
    with Sdf.ChangeBlock():
        for i, (id, value) in enumerate(payload["Payload"].items()):
            attr = live_layer.GetAttributeAtPath(f"/iot/{iot_topic}.{clean_text(id)}")
            if not attr:
                raise Exception(f"Could not find attribute /iot/{iot_topic}.{id}.")
            attr.default = float(value["Value"])
    omni.client.live_process()


def clean_text(input):
    input = input.replace('dtmi:com:example:Magnemotion;1:', '')
    input = input.replace(' ', '')
    return input


# publish to mqtt broker
def write_to_mqtt(mqtt_client, iot_topic, group, ts):
    # write the iot values to the usd prim attributes
    topic = f"iot/{iot_topic}"
    print(group.iloc[0]["TimeStamp"])
    payload = {"_ts": ts}
    for index, row in group.iterrows():
        payload[row["Id"]] = row["Value"]
    mqtt_client.publish(topic, json.dumps(payload, indent=2).encode("utf-8"))


# connect to mqtt broker
def connect_mqtt():
    # called when a message arrives
    def on_message(client, userdata, msg):
        msg_content = msg.payload.decode()
        write_to_live(live_layer, iot_topic, msg_content)
        print(f"Received `{msg_content}` from `{msg.topic}` topic")

    # called when connection to mqtt broker has been established
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            # connect to our topic
            print(f"Subscribing to topic: {mqtt_topic}")
            client.subscribe(mqtt_topic)
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


def run(stage, live_layer):
    # we assume that the file contains the data for single device
    connect_mqtt()


if __name__ == "__main__":
    omni.client.initialize()
    omni.client.set_log_level(omni.client.LogLevel.DEBUG)
    omni.client.set_log_callback(log_handler)
    try:
        stage, live_layer = asyncio.run(initialize_async())
        run(stage, live_layer)
        input()
    finally:
        omni.client.shutdown()
