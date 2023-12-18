# Copyright 2019-2023 NVIDIA CORPORATION

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import omni.ext
import omni.ui as ui
from .robotmotion import RobotMotion as robot
import asyncio
from .mqtt_csv_client import MQTTData as mqtt


# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print(f"[omni.hello.world] some_public_function was called with {x}")
    return x ** x


async def start_threads():
    ROBOT_BASE= '/Root/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003'
    ROBOT_LINKS= ['link1piv_003', 'link2piv_003', 'link3piv_003', 'link4piv_003', 'link5piv_003', 'link6piv_003']  
    robot_usd = robot(ROBOT_BASE,ROBOT_LINKS)
    q = asyncio.Queue()
    MQTT = mqtt(robot_usd.pose)
    asyncio.Task(robot_usd.startAnimating())
    # asyncio.run_coroutine_threadsafe(robot_usd.startAnimating(), loop=loop)
    await MQTT.read_csv()
    

    # asyncio.gather(MQTT.read_csv(), robot_usd.startAnimating())
    # asyncio.Task(MQTT.read_csv())
    # asyncio.Task(robot_usd.startAnimating())

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    


    def on_startup(self, ext_id):
        print("[omni.async.test] MyExtension startup")

        self._count = 0

        self._window = ui.Window("Async Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                label = ui.Label("Async Window")                

                def on_click():
                    self._count += 1
                    label.text = f"count: {self._count}"
                    asyncio.ensure_future(start_threads())

                def on_reset():
                    self._count = 0
                    label.text = "empty"

                on_reset()

                with ui.HStack():
                    ui.Button("Add", clicked_fn=on_click)
                    ui.Button("Reset", clicked_fn=on_reset)

    def on_shutdown(self):
        print("[omni.async.test] MyExtension shutdown")

