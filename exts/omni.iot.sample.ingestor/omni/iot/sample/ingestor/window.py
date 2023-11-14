__all__ = ["MsftAdtWindow"]
import os
import omni.kit
import omni.ext
import omni.usd
import omni.ui as ui
import asyncio
import carb.settings
from typing import List
from .style import *
from .robotmotion import RobotMotion
# from pxr import Sdf, Usd
# from .robotdata import getPose, RobotPose
from .settings import Settings

class MsftAdtWindow(ui.Window):
    motions: List[RobotMotion] = [None, None, None, None]
    count = 0
    """MsftAdtWindow"""

    title = "MSFT ADT"

    _ui_connection_status_frame = None
    _ui_twins_list_frame = None
    _ui_connection_btn = None
    _ui_zoom_on_selections = None
    _ui_show_viewport_twin_popup = None
    _ui_show_twin_raw_data_at_app_panel = None

    def __init__(self, **kwargs):
        super().__init__(MsftAdtWindow.title, **kwargs)

        with self.frame:
            with ui.VStack(height=0,style=style):
                ui.Button('Move', clicked_fn=self._move_click, style=style)
                self._ui_connection_status_frame = ui.Frame(name="connection_status_frame",style=style)

                with ui.HStack(height=0, width=0):
                    self._ui_show_viewport_twin_popup = ui.CheckBox(
                        style={'margin': 5},
                    )
                    ui.Label("Show Twin data when selected")

                with ui.HStack(height=0, width=0):
                    self._ui_zoom_on_selections = ui.CheckBox(
                        style={'margin': 5},
                    )
                    ui.Label("Focus at Twin when selected")

                with ui.HStack(height=0):
                    ui.Spacer()
                    ui.Label("Zoom value")
                    self._ui_zoom_value = ui.FloatSlider(min=0, max=1, step=0.01, height=0)

                with ui.HStack(height=0, width=0):
                    self._ui_show_twin_raw_data_at_app_panel = ui.CheckBox(
                        style={'margin': 5},

                    )
                    ui.Label("Show Twin raw data at side panel when selected")


        self._ui_show_viewport_twin_popup.model.set_value(Settings.get(Settings.UI_SHOW_TWIN_VIEWPORT_POPUP_WHEN_SELECTED))
        self._ui_show_viewport_twin_popup.model.add_value_changed_fn(
            lambda model: Settings.set(Settings.UI_SHOW_TWIN_VIEWPORT_POPUP_WHEN_SELECTED, model.get_value_as_bool())
        )

        self._ui_zoom_value.model.set_value(Settings.get(Settings.UI_ZOOM_IN_VALUE))
        self._ui_zoom_value.model.add_value_changed_fn(
            lambda model: Settings.set(Settings.UI_ZOOM_IN_VALUE, model.get_value_as_float())
        )

        self._ui_zoom_on_selections.model.set_value(Settings.get(Settings.UI_ZOOM_INOUT_ON_PRIM_SELECTION))
        self._ui_zoom_on_selections.model.add_value_changed_fn(
            lambda model: Settings.set(Settings.UI_ZOOM_INOUT_ON_PRIM_SELECTION, model.get_value_as_bool())
        )
        self._ui_show_twin_raw_data_at_app_panel.model.set_value(Settings.get(Settings.UI_SHOW_TWIN_RAW_DATA_AT_APP_PANEL))
        self._ui_show_twin_raw_data_at_app_panel.model.add_value_changed_fn(
            lambda model: Settings.set(Settings.UI_SHOW_TWIN_RAW_DATA_AT_APP_PANEL, model.get_value_as_bool())
        )

                # omni.kit.commands.execute('CreateMeshPrimWithDefaultXform',prim_type='Cube')
                # omni.kit.commands.subscribe_on_change(self._event_triggered)

        # usd_context = omni.usd.get_context()
        # self._events = usd_context.get_stage_event_stream()
        # self._stage_event_sub = self._events.create_subscription_to_pop(
        #     self._on_stage_event, name="Object Info Selection Update"
        # )
        # omni.usd.StageEventType.SELECTION_CHANGED

    def _move_click(self):
        # if self.motion is None:
        # self.motion = RobotMotion('/World/khi_rs007n_vac_UNIT1/world_003/base_link_003',
        #                           ['link1piv_003', 'link2piv_003', 'link3piv_003', 'link4piv_003',
        #                            'link5piv_003', 'link6piv_003'])

        if self.motions[0] is not None and self.motions[0].animating:
            self.motions[0].stopAnimating()
            self.motions[1].stopAnimating()
            self.motions[2].stopAnimating()
            self.motions[3].stopAnimating()
            return

        # self.motions[0] = RobotMotion('/World/khi_rs007n_vac_UNIT3/world/base_link',
        #                               ['link1piv', 'link2piv', 'link3piv', 'link4piv',
        #                                'link5piv', 'link6piv'])
        # self.motions[1] = RobotMotion('/World/khi_rs007n_vac_UNIT2/world_001/base_link_001',
        #                               ['link1piv_001', 'link2piv_001', 'link3piv_001', 'link4piv_001',
        #                                'link5piv_001', 'link6piv_001'])
        # self.motions[2] = RobotMotion('/World/khi_rs007n_vac_UNIT4/world_002/base_link_002',
        #                               ['link1piv_002', 'link2piv_002', 'link3piv_002', 'link4piv_002',
        #                                'link5piv_002', 'link6piv_002'])
        # self.motions[3] = RobotMotion('/World/khi_rs007n_vac_UNIT1/world_003/base_link_003',
        #                               ['link1piv_003', 'link2piv_003', 'link3piv_003', 'link4piv_003',
        #                                'link5piv_003', 'link6piv_003'])

        # asyncio.ensure_future(self.motions[0].startAnimating())
        # asyncio.ensure_future(self.motions[1].startAnimating())
        # asyncio.ensure_future(self.motions[2].startAnimating())
        # asyncio.ensure_future(self.motions[3].startAnimating())

        # allPoses = [
        #     RobotPose.zero, RobotPose.deg10, RobotPose.rest, RobotPose.fcartup, RobotPose.fcartdn, RobotPose.ecartup,
        #     RobotPose.ecartdn, RobotPose.key00up, RobotPose.key00dn, RobotPose.key01up, RobotPose.key01dn,
        #     RobotPose.key02up, RobotPose.key02dn, RobotPose.key03up, RobotPose.key03dn,
        #     RobotPose.zero, RobotPose.Pose099900, RobotPose.Pose090000, RobotPose.Pose099999,
        #     RobotPose.Pose099000, RobotPose.Pose099990, RobotPose.Pose999999]

        # print("Move " + str(self.count))
        # self.motion.setPose(getPose(allPoses[self.count]))
        # self.count = self.count + 1
        # if self.count >= len(allPoses):
        #     self.count = 0
        # self.motion.setPose([0, 0, 0, 0, 0, 0])
        # self.motion.setPose(getPose(RobotPose.rest))

    # async def _send_message(self):
    #     uri = "ws://localhost:3000/67"
    #     async with websockets.connect(uri) as websocket:
    #         await websocket.send(self.label1.text)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
