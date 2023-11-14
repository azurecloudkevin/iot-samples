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

import os
import asyncio
import omni.ext
from .robotmotion import RobotMotion
from .app import app
from pxr import Usd, Sdf, Tf, UsdGeom

os.environ["OMNI_USER"] = "andre.ballard"
os.environ["OMNI_PASS"] = "Marsden1"
os.environ["OMNI_HOST"] = "nucleus.azurenucleus.co.uk"

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.


class OmniIotSampleIngestor(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[omni.iot.sample.ingestor] startup")
        self.workload = app("donut")
           # asyncio.ensure_future(self.workload.run())
        self.workload.run()


        # robot = RobotMotion("/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003", ['link1piv_003', 'link2piv_003', 'link3piv_003', 'link4piv_003', "link5piv_003", "link6piv_003"])
        # asyncio.ensure_future(robot.startAnimating())
        # self.listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_objects_changed, self._stage)


    def _on_objects_changed(self, notice, stage):
        base_prim_id="/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003/"
        Tf.Notice.Send
        prim = stage.GetPrimAtPath(base_prim_id+id1)
        if prim:
            attribute = prim.GetAttribute("xformOp:orient")
            attribute_value = attribute.Get()
            new_rotation =self.vector_to_quat(0,0,self.joints[0])
            attribute.Set(value=new_rotation)

        updated_objects = []
        for p in notice.GetChangedInfoOnlyPaths():
            if p.IsPropertyPath() and p.GetParentPath() == self._selected_prim.GetPath():
                updated_objects.append(p)

    def _get_context(self) -> Usd.Stage:
        # Get the UsdContext we are attached to
        return omni.usd.get_context()

    def on_shutdown(self):
        print("[omni.iot.sample.ingestor] shutdown")
        self.workload.stop()
        self.workload = None