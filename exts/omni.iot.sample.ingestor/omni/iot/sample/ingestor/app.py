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
import math
import os
import ssl as _ssl
import omni.client
from enum import Enum
from typing import List
from pxr import Usd, Sdf, Gf, UsdGeom, Tf
from pathlib import Path
from .robotmotion import RobotMotion
import pandas as pd
import time
from paho.mqtt import client as mqtt_client
import random
import json

OMNI_HOST = os.environ.get("OMNI_HOST", "localhost")
BASE_URL = "omniverse://" + OMNI_HOST + "/Projects/OVPOC/Stages"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONTENT_DIR = Path(SCRIPT_DIR).resolve().parents[1].joinpath("content")

messages = []


class app:
    robot = RobotMotion('/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003',['link1piv_003', 'link2piv_003', 'link3piv_003', 'link4piv_003','link5piv_003', 'link6piv_003'])

    def __init__(self, topic: str):
        self._topic = topic

    def log_handler(thread, component, level, message):
        # print(message)
        messages.append((thread, component, level, message))

    def initialize_device_prim(self, live_layer, iot_topic):
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
            raise Exception("Could not define the attribute: Timestamp")

        # infer the unique data points in the CSV.
        # The values may be known in advance and can be hard coded
        grouped = data.groupby("Id")
        for attrName, group in grouped:
            attr = Sdf.AttributeSpec(iot_spec, self.clean_text(attrName), Sdf.ValueTypeNames.Double)
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

    def initialize(self, iot_topic):
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
            live_layer = self.create_live_layer(iot_topic)

        found = False
        subLayerPaths = root_layer.subLayerPaths
        for subLayerPath in subLayerPaths:
            if subLayerPath == live_layer.identifier:
                found = True

        if not found:
            root_layer.subLayerPaths.append(live_layer.identifier)
            root_layer.Save()

        self.initialize_device_prim(live_layer, iot_topic)

        # set the live layer as the edit target
        stage.SetEditTarget(live_layer)
        return stage, live_layer

    def write_to_live(self, live_layer, iot_topic, msg_content):
        # write the iot values to the usd prim attributes
        payload = json.loads(msg_content)
        # payloadMessage = payload['Payload']#.dtmi:com:example:Thermostat;1:temperature.Value']
        # if 'temperature' in payloadMessage:
        #     tempMessage = payloadMessage['temperature']
        #     value = tempMessage['Value']
        #     id = 'Ambient_Temperature'
        #     attr = live_layer.GetAttributeAtPath(f"/iot/{iot_topic}.{id}")
        #     if not attr:
        #         raise Exception(f"Could not find attribute /iot/{iot_topic}.{id}.")
        #     attr.default = value
        with Sdf.ChangeBlock():
            for i, (id, value) in enumerate(payload["Payload"].items()):
                attr = live_layer.GetAttributeAtPath(f"/iot/{iot_topic}.{self.clean_text(id)}")
                if not attr:
                    raise Exception(f"Could not find attribute /iot/{iot_topic}.{id}.")
                attr.default = value["Value"]
        omni.client.live_process()

    # async def move_joints(self, msg_content, robot):
    #     # write the iot values to the usd prim attributes
    #     payload = json.loads(msg_content)
    #     joints = [0,0,0,0,0,0]
    #     joints[0] = payload["Payload"]["RobotPositionJ0"]["Value"]
    #     joints[1] = payload["Payload"]["RobotPositionJ1"]["Value"]
    #     joints[2] = payload["Payload"]["RobotPositionJ2"]["Value"]
    #     joints[3] = payload["Payload"]["RobotPositionJ3"]["Value"]
    #     joints[4] = payload["Payload"]["RobotPositionJ4"]["Value"]
    #     joints[5] = payload["Payload"]["RobotPositionJ5"]["Value"]
    #     robot.SetMqttPose(joints)

    def clean_text(self, input):
        input = input.replace('dtmi:com:example:Magnemotion;1:','')
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

    def move_joints(self, msg_content):
        self.payload = json.loads(msg_content)
        self.pos0 = float(str(self.payload["Payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ0"]["Value"]))
        self.pos1 = float(str(self.payload["Payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ1"]["Value"]))
        self.pos2 = float(str(self.payload["Payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ2"]["Value"]))
        self.pos3 = float(str(self.payload["Payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ3"]["Value"]))
        self.pos4 = float(str(self.payload["Payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ4"]["Value"]))
        self.pos5 = float(str(self.payload["Payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ5"]["Value"]))
        self.robot.SetAngleDegrees(0,self.pos0)
        self.robot.SetAngleDegrees(1,self.pos1)
        self.robot.SetAngleDegrees(2,self.pos2)
        self.robot.SetAngleDegrees(3,self.pos3)
        self.robot.SetAngleDegrees(4,self.pos4)
        self.robot.SetAngleDegrees(5,self.pos5)

    def _get_context(self) -> Usd.Stage:
        # Get the UsdContext we are attached to
        return omni.usd.get_context()

    async def move_prim_joints(self, msg_content):
        self.payload = json.loads(msg_content)

        # data_file_path = os.path.join(os.path.dirname(__file__), "payload.json")
        # self.payload = json.load(open(data_file_path))

        self.joints = [0,0,0,0,0,0]
        self.pos0 = str(self.payload["Payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ0"]["Value"])
        self.pos1 = str(self.payload["Payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ1"]["Value"])
        self.pos2 = str(self.payload["Payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ2"]["Value"])
        self.pos3 = str(self.payload["Payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ3"]["Value"])
        self.pos4 = str(self.payload["Payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ4"]["Value"])
        self.pos5 = str(self.payload["Payload"]["dtmi:com:example:Magnemotion;1:RobotPositionJ5"]["Value"])
        self.joints[0] = float(self.pos0)
        self.joints[1] = float(self.pos1)
        self.joints[2] = float(self.pos2)
        self.joints[3] = float(self.pos3)
        self.joints[4] = float(self.pos4)
        self.joints[5] = float(self.pos5)

        base_prim_id="/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003/"
        self.level1 = 0
        self.level2 = 0
        self.level3 = 0
        self.level4 = 0

        id1="link1piv_003"
        id2="link1piv_003/link2piv_003"
        id3="link1piv_003/link2piv_003/link3piv_003"
        id4="link1piv_003/link2piv_003/link3piv_003/link4piv_003/link5piv_003"

        context = self._get_context()
        stage = context.get_stage()

        prim = stage.GetPrimAtPath(base_prim_id+id1)
        if prim:
            attribute = prim.GetAttribute("xformOp:orient")
            attribute_value = attribute.Get()
            new_rotation =self.vector_to_quat(0,0,self.joints[0])
            attribute.Set(value=new_rotation)

        prim = stage.GetPrimAtPath(base_prim_id+id2)
        if prim:
            attribute = prim.GetAttribute("xformOp:orient")
            attribute_value = attribute.Get()
            new_rotation =self.vector_to_quat(0,self.joints[1],0)
            attribute.Set(value=new_rotation)

        prim = stage.GetPrimAtPath(base_prim_id+id3)
        if prim:
            attribute = prim.GetAttribute("xformOp:orient")
            attribute_value = attribute.Get()
            new_rotation =self.vector_to_quat(0,self.joints[2],0)
            attribute.Set(value=new_rotation)


        prim = stage.GetPrimAtPath(base_prim_id+id4)
        if prim:
            attribute = prim.GetAttribute("xformOp:orient")
            attribute_value = attribute.Get()
            new_rotation =self.vector_to_quat(0,self.joints[3],0)
            attribute.Set(value=new_rotation)

    def vector_to_quat(self, roll, pitch, yaw) -> Gf.Quatf:
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)

        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy

        return Gf.Quatf(w, x, y, z)

    # connect to mqtt broker
    def connect_mqtt(self, iot_topic, live_layer):
        # topic = f"iot/{iot_topic}"
        # topic = f"alice-springs-solution/data/opc-ua-connector/opc-ua-connector-0/thermostat"
        topic = "alice-springs-solution/data/opc-ua-connector/opc-ua-connector-0/robot"
        # topic = f"opcua/data/opc-ua-connector/#"

        # called when a message arrives
        def on_message(client, userdata, msg):
            msg_content = msg.payload.decode()
            self.write_to_live(live_layer, iot_topic, msg_content)
            #self.move_joints(msg_content)
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
        client.username_pw_set(username='client2-authn-ID')
        client.tls_set(
            certfile='C:\\Workspaces\\iot-samples\\source\\ingest_app_mqtt\\client2-authn-ID.pem',
            keyfile='C:\\Workspaces\\iot-samples\\source\\ingest_app_mqtt\\client2-authn-ID.key'
        )
        client.connect("simulated-plant-eg.eastus-1.ts.eventgrid.azure.net", 8883)
        client.loop_start()
        return client

    def run(self):
        omni.client.initialize()
        omni.client.set_log_level(omni.client.LogLevel.DEBUG)
        # omni.client.set_log_callback(app.log_handler)
        stage, live_layer = self.initialize(self._topic)
        #   run(stage, live_layer, self.IOT_TOPIC)

        # we assume that the file contains the data for single device
        # IOT_TOPIC_DATA = f"{CONTENT_DIR}/{iot_topic}_iot_data.csv"
        # data = pd.read_csv(IOT_TOPIC_DATA)
        # data.head()

        # Converting to DateTime Format and drop ms
        # data["TimeStamp"] = pd.to_datetime(data["TimeStamp"])
        # data["TimeStamp"] = data["TimeStamp"].dt.floor("s")

        # data.set_index("TimeStamp")
        # start_time = data.min()["TimeStamp"]
        # last_time = start_time
        # grouped = data.groupby("TimeStamp")

        self.mqtt_client = self.connect_mqtt(self._topic, live_layer)

        #self.move_prim_joints({})

        # play back the data in real-time
        # for next_time, group in grouped:
        #   diff = (next_time - last_time).total_seconds()
        #   if diff > 0:
        #       time.sleep(diff)
        #       write_to_mqtt(mqtt_client, iot_topic, group, (next_time - start_time).total_seconds())
        # last_time = next_time

        # mqtt_client = None

    def stop(self):
        self.mqtt_client.disconnect()

    # if __name__ == "__main__":
    #     IOT_TOPIC = "donut"
    #     #IOT_TOPIC = "A08_PR_NVD_01"
    #     # robot = RobotMotion("/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003", ['link1piv_003', 'link2piv_003', 'link3piv_003', 'link4piv_003', "link5piv_003", "link6piv_003"])
    #     # robot.startAnimating([ -20.454347610473633,
    #     #                       36.701641082763672,
    #     #                       -66.095443725585938,
    #     #                       0.010845709592103958,
    #     #                       -77.266159057617188,
    #     #                       -159.88578796386719
    #     #                     ])
    #     omni.client.initialize()
    #     omni.client.set_log_level(omni.client.LogLevel.DEBUG)
    #     omni.client.set_log_callback(log_handler)
    #     try:
    #         stage, live_layer = asyncio.run(initialize_async(IOT_TOPIC))
    #         run(stage, live_layer, IOT_TOPIC)
    #         input()
    #     finally:
    #         omni.client.shutdown()
