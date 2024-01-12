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

import omni.ext
import omni.ui as ui
from pxr import Usd, Sdf, Tf, UsdGeom, UsdShade
import omni.ui.color_utils as cl
import omni.kit.material as material
TRANSLATE_OFFSET = "xformOp:translate:offset"
ROTATE_SPIN = "xformOp:rotateX:spin"


class uiTextStyles:
    title = {"margin": 10, "color": 0xFFFFFFFF, "font_size": 18, "alignment": ui.Alignment.LEFT_CENTER}
    title2 = {"margin": 10, "color": 0xFFFFFFFF, "font_size": 18, "alignment": ui.Alignment.LEFT_CENTER}


class uiElementStyles:
    mainWindow = {"Window": {"background_color": cl.color(32, 42, 87, 100), "width": 350}}


class uiButtonStyles:
    mainButton = {
        "Button": {"background_color": cl.color(32, 42, 87, 125), "width": 175, "height": 80},
        "Button:hovered": {"background_color": cl.color(32, 42, 87, 200)},
    }

    # geometry manipulation


class LiveCube:
    def __init__(self, stage: Usd.Stage, path: str):
        self._prim = stage.GetPrimAtPath(path)
        self._op = self._prim.HasProperty(TRANSLATE_OFFSET)
        if self._prim:
            self._xform = UsdGeom.Xformable(self._prim)

    def resume(self):
        if self._xform and not self._op:
            op = self._xform.AddTranslateOp(opSuffix="offset")
            op.Set(time=1, value=(0, -20.0, 0))
            op.Set(time=96, value=(0, -450, 150))
            op.Set(time=192, value=(0, -950, 0))
            self._op = True

    def pause(self):
        if self._xform and self._op:
            default_ops = []
            for op in self._xform.GetOrderedXformOps():
                if op.GetOpName() != TRANSLATE_OFFSET:
                    default_ops.append(op)
            self._xform.SetXformOpOrder(default_ops)
            self._prim.RemoveProperty(TRANSLATE_OFFSET)
            self._op = False


class LiveRoller:
    def __init__(self, stage: Usd.Stage, path: str):
        self._prim = stage.GetPrimAtPath(path)
        self._op = self._prim.HasProperty(ROTATE_SPIN)
        if self._prim:
            self._xform = UsdGeom.Xformable(self._prim)

    def resume(self):
        if self._xform and not self._op:
            op = self._xform.AddRotateXOp(opSuffix="spin")
            op.Set(time=1, value=0)
            op.Set(time=192, value=1440)
            self._op = True

    def pause(self):
        if self._xform and self._op:
            default_ops = []
            for op in self._xform.GetOrderedXformOps():
                if op.GetOpName() != ROTATE_SPIN:
                    default_ops.append(op)
            self._xform.SetXformOpOrder(default_ops)
            self._prim.RemoveProperty(ROTATE_SPIN)
            self._op = False

class MaterialType():
    MATERIAL_ERROR = '/World/Looks/Blue_Glass'
    #MATERIAL_SELECTED = '/World/Looks/Blue_Glass'
    MATERIAL_SELECTED = '/World/Looks/ABS_Hard_Leather_Vintage_Rose_07'
    MDL_NAME = 'mdl::uber'
    MDL_TYPE = 'UsdPreviewSurface'



# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class OmniIotSamplePanelExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[omni.iot.sample.panel] startup")
        self._hightlighted_prims = {}
        self._usd_context = omni.usd.get_context()
        self._stage = self._usd_context.get_stage()
        self._selected_prim = None
        live_layer_path = None
        root_layer = self._stage.GetRootLayer()
        subLayerPaths = root_layer.subLayerPaths
        for subLayerPath in subLayerPaths:
            if subLayerPath.endswith(".live"):
                live_layer_path = subLayerPath

        self._window = ui.Window("Sample IoT Data", width=350, height=380, raster_policy=ui.RasterPolicy.NEVER)
        self._window.frame.set_style(uiElementStyles.mainWindow)
        self._stage.SetEditTarget(root_layer)
        root_layer.startTimeCode = 1
        root_layer.endTimeCode = 192
        UsdGeom.SetStageUpAxis(self._stage, UsdGeom.Tokens.z)


        if live_layer_path:
            # live_layer = None
            # for sub_layer in self._stage.GetLayerStack():
            #     if sub_layer.realPath == live_layer_path:
            #         live_layer = sub_layer

            # if live_layer:
            #     live_layer.startTimeCode = 1
            #     live_layer.endTimeCode = 192
            #     # self._stage.SetEditTarget(live_layer)
            self._iot_prim = self._stage.GetPrimAtPath("/iot")
            #     self._cube = LiveCube(self._stage, "/World/Cube")
            #     self._rollers = []

            #     for x in range(38):
            #         self._rollers.append(
            #             LiveRoller(self._stage, f"/World/Geometry/SM_ConveyorBelt_A08_Roller{x+1:02d}_01")
            #         )

            # this will capture when the select changes in the stage_selected_iot_prim_label
            # self._stage_event_sub = self._usd_context.get_stage_event_stream().create_subscription_to_pop(
            #     self._on_stage_event, name="Stage Update"
            # )

            # this will capture changes to the IoT data
            self.listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_objects_changed, self._stage)

            # create an simple window with empty VStack for the IoT data
            with self._window.frame:
                with ui.VStack():
                    with ui.HStack(height=22):
                        ui.Label("Robot telemetry:", style=uiTextStyles.title, width=75)
                        self._selected_iot_prim_label = ui.Label(" ", style=uiTextStyles.title)
                    self._property_stack = ui.VStack(height=22)

            # if self._iot_prim:
            #     self._on_selected_prim_changed()


        self.build_frame()

        self.j0_button = ui.Button("J0", style=uiButtonStyles.mainButton)
        self.j1_button = ui.Button("J1", style=uiButtonStyles.mainButton)
        self.j2_button = ui.Button("J2", style=uiButtonStyles.mainButton)
        self.j3_button = ui.Button("J3", style=uiButtonStyles.mainButton)
        self.j4_button = ui.Button("J4", style=uiButtonStyles.mainButton)
        self.j5_button = ui.Button("J5", style=uiButtonStyles.mainButton)
        self.vacuum_pressure_button = ui.Button("Vacuum pressure", style=uiButtonStyles.mainButton)
        self.vacuum_alert_button = ui.Button("Vacuum alert", style=uiButtonStyles.mainButton)


        hStack = ui.HStack()
        hStack.add_child(self.j0_button)
        hStack.add_child(self.j1_button)

        self._property_stack.add_child(hStack)

        hStack = ui.HStack()
        hStack.add_child(self.j2_button)
        hStack.add_child(self.j3_button)

        self._property_stack.add_child(hStack)

        hStack = ui.HStack()
        hStack.add_child(self.j4_button)
        hStack.add_child(self.j5_button)


        self._property_stack.add_child(hStack)

        hStack = ui.HStack()
        hStack.add_child(self.vacuum_pressure_button)
        hStack.add_child(self.vacuum_alert_button)


        self._property_stack.add_child(hStack)

    def on_shutdown(self):
        print("[omni.iot.sample.panel] shutdown")

    def _on_velocity_changed(self, speed):
        print(f"[omni.iot.sample.panel] _on_velocity_changed: {speed}")
        if speed is not None and speed > 0.0:
            with Sdf.ChangeBlock():
                self._cube.resume()
                for roller in self._rollers:
                    roller.resume()
        else:
            with Sdf.ChangeBlock():
                self._cube.pause()
                for roller in self._rollers:
                    roller.pause()

    def build_frame(self):
        self._property_stack.clear()
        button_height = uiButtonStyles.mainButton["Button"]["height"]
        self._property_stack.height.value = (round(5 / 2) + 1) * button_height
        x = 0
        hStack = ui.HStack()
        self._property_stack.add_child(hStack)

    def _update_frame(self, updated_objects):
        robot_prims = [
            "/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003/link1piv_003/Visuals_1_003/unnamed_1_003/RS007N_J1_003/RS007_Body_mid_A_003/Scene_001/Scene_001",
            "/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003/link1piv_003/link2piv_003/link2_003/Visuals_2_003/unnamed_2_003/RS007N_J2_003/RS007_Body_arm_mid_003/Scene_002/Scene_002",
            "/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003/link1piv_003/link2piv_003/link3piv_003/link3_003/Visuals_3_003/unnamed_3_003/RS007N_J3_003/RS007_Body_arm_upper_004/Scene_003/Scene_003",
            "/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003/link1piv_003/link2piv_003/link3piv_003/link4piv_003/link4old_003/Visuals_4_003/unnamed_4_003/RS007N_J4_003/RS007_Body_arm_top_003/Scene_004/Scene_004",
            "/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003/link1piv_003/link2piv_003/link3piv_003/link4piv_003/link5piv_003/link5_003/Visuals_5_003/unnamed_5_003/RS007N_J5_003/RS007_gripper_A_003/Scene_005/Scene_005"
            "/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003/link1piv_003/link2piv_003/link3piv_003/link4piv_003/link4old_003/Visuals_4_003/unnamed_4_003/RS007N_J4_003/RS007_Body_arm_top_003/Scene_004/Scene_004"
        ]
        robot_prim = "/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003/link1piv_003/link2piv_003/link3piv_003/link3_003/Visuals_3_003/unnamed_3_003/RS007N_J3_003/RS007_Body_arm_upper_004/Scene_003/Scene_003"
        #/link1piv_003/link1piv_003/link1piv_003/link2piv_003/link2_003/Visuals_2_003/unnamed_2_003/RS007N_J2_003/RS007_Body_arm_mid_003/Scene_002/Scene_002"
        #if self._selected_prim is not None:
            #self._property_stack.clear()
            #properties = self._selected_prim.GetProperties()


        # repopulate the VStack with the IoT data attributes
        for prop in updated_objects:
            try:
                if "Value" in prop.pathString:
                    prim = self._stage.GetPrimAtPath(prop.pathString.split('.')[0])
                    attr = prim.GetAttribute(prop.pathString.split('.')[1])
                    teste = str(prop.pathString).split("/")[9]
                    teste = teste.split(".")[0]
                    prop_name = teste
                    prop_value = float(attr.Get())
                    prop_value = round(prop_value, 4)
                    if "j0" in prop_name:
                        self.j0_button.text = f"J0\n{str(prop_value)}"
                    if "j1" in prop_name:
                        self.j1_button.text = f"J1\n{str(prop_value)}"
                    if "j2" in prop_name:
                        self.j2_button.text = f"J2\n{str(prop_value)}"
                    if "j3" in prop_name:
                        self.j3_button.text = f"J3\n{str(prop_value)}"
                    if "j4" in prop_name:
                        self.j4_button.text = f"J4\n{str(prop_value)}"
                    if "j5" in prop_name:
                        self.j5_button.text = f"J5\n{str(prop_value)}"
                    if "vacuumpressure" in prop_name:
                        self.vacuum_pressure_button.text = f"Vacuum pressure\n{str(prop_value)}"
                    if "vacuum_alert" in prop_name:
                        self.vacuum_alert_button.text = f"Vacuum alert\n{str(prop_value)}"
                        if prop_value == 1:
                            for prim in robot_prims:
                                self.clear_prim_highlight(prim)
                        else:
                            for prim in robot_prims:
                                self.highlight_prim(prim)

                    if prop_name == "Velocity":
                        self._on_velocity_changed(prop_value)

            except Exception as e:
                print(e)




    def _on_selected_prim_changed(self):
        print("[omni.iot.sample.panel] _on_selected_prim_changed")
        selected_prim = self._usd_context.get_selection()
        selected_paths = selected_prim.get_selected_prim_paths()
        if selected_paths and len(selected_paths):
            sdf_path = Sdf.Path(selected_paths[0])

            # only handle data that resides under the /iot prim
            if (
                sdf_path.IsPrimPath()
                and sdf_path.HasPrefix(self._iot_prim.GetPath())
                and sdf_path != self._iot_prim.GetPath()
            ):
                self._selected_prim = self._stage.GetPrimAtPath(sdf_path)
                self._selected_iot_prim_label.text = str(sdf_path)
                self._update_frame()

    # ===================== stage events START =======================
    def _on_selection_changed(self):
        print("[omni.iot.sample.panel] _on_selection_changed")
        if self._iot_prim:
            self._on_selected_prim_changed()

    def _on_asset_opened(self):
        print("[omni.iot.sample.panel] on_asset_opened")

    def _on_stage_event(self, event):
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_selection_changed()
        elif event.type == int(omni.usd.StageEventType.OPENED):
            self._on_asset_opened()

    def _on_objects_changed(self, notice, stage):
        updated_objects = []
        for p in notice.GetChangedInfoOnlyPaths():
            # if p.IsPropertyPath() and p.GetParentPath() == self._selected_prim.GetPath():
            updated_objects.append(p)

        if len(updated_objects) > 0:
            self._update_frame(updated_objects)

    # ===================== stage events END =======================

    # ===================== prim highlight START =======================

    # def highlight_prim(self, prim_path: str, material_path:str = MaterialType.MATERIAL_SELECTED):
    #     mtl = UsdShade.Material.Get(self._stage, Sdf.Path(material_path))
    #     prim = self._stage.GetPrimAtPath(prim_path)
    #     prim.ApplyAPI(UsdShade.MaterialBindingAPI)
    #     UsdShade.MaterialBindingAPI(prim).Bind(mtl)
    #     myRel = prim.CreateRelationship("myRel")
    #     #UsdShade.MaterialBindingAPI(prim).SetMaterialBindingStrength(prim.GetAuthoredPropertyNames()[0], UsdShade.Tokens.strongerThanDescendants)
    #     #UsdShade.MaterialBindingAPI(prim).SetMaterialBindingStrength(bindingRel, UsdShade.Tokens.strongerThanDescendants)
    #     UsdShade.MaterialBindingAPI(prim).SetMaterialBindingStrength(myRel, UsdShade.Tokens.strongerThanDescendants)
    #     self._hightlighted_prims[str(prim_path)]=''

    # def clear_prim_highlight(self, prim_path: str):
    #     prim = self._stage.GetPrimAtPath(prim_path)
    #     try:
    #         # print(f"clear prim :::::: {prim_path}")
    #         UsdShade.MaterialBindingAPI(prim).UnbindDirectBinding()

    #         del self._hightlighted_prims[str(prim_path)]
    #     except Exception as e:
    #         print(e)

    def highlight_prim():
        material.library.CreateAndBindMdlMaterialFromLibrary(mdl_name=MaterialType.MATERIAL_SELECTED).do()

    def clear_prim_highlight():
        material.library.CreateAndBindMdlMaterialFromLibrary(mdl_name=MaterialType.MATERIAL_SELECTED).undo()

# ===================== prim highlight END =======================