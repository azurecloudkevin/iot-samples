## Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["WidgetInfoManipulator"]

from omni.ui import color as cl
from omni.ui import scene as sc
import omni.ui as ui
import omni.usd
from pxr import Usd, Sdf, Tf


class _ViewportLegacyDisableSelection:
    """Disables selection in the Viewport Legacy"""

    def __init__(self):
        self._focused_windows = None
        focused_windows = []
        try:
            # For some reason is_focused may return False, when a Window is definitely in fact is the focused window!
            # And there's no good solution to this when mutliple Viewport-1 instances are open; so we just have to
            # operate on all Viewports for a given usd_context.
            import omni.kit.viewport_legacy as vp

            vpi = vp.acquire_viewport_interface()
            for instance in vpi.get_instance_list():
                window = vpi.get_viewport_window(instance)
                if not window:
                    continue
                focused_windows.append(window)
            if focused_windows:
                self._focused_windows = focused_windows
                for window in self._focused_windows:
                    # Disable the selection_rect, but enable_picking for snapping
                    window.disable_selection_rect(True)
        except Exception:
            pass


class _DragPrioritize(sc.GestureManager):
    """Refuses preventing _DragGesture."""

    def can_be_prevented(self, gesture):
        # Never prevent in the middle of drag
        return gesture.state != sc.GestureState.CHANGED

    def should_prevent(self, gesture, preventer):
        if preventer.state == sc.GestureState.BEGAN or preventer.state == sc.GestureState.CHANGED:
            return True


class _DragGesture(sc.DragGesture):
    """"Gesture to disable rectangle selection in the viewport legacy"""

    def __init__(self):
        super().__init__(manager=_DragPrioritize())

    def on_began(self):
        # When the user drags the slider, we don't want to see the selection
        # rect. In Viewport Next, it works well automatically because the
        # selection rect is a manipulator with its gesture, and we add the
        # slider manipulator to the same SceneView.
        # In Viewport Legacy, the selection rect is not a manipulator. Thus it's
        # not disabled automatically, and we need to disable it with the code.
        self.__disable_selection = _ViewportLegacyDisableSelection()

    def on_ended(self):
        # This re-enables the selection in the Viewport Legacy
        self.__disable_selection = None


class WidgetInfoManipulator(sc.Manipulator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        BASE_URL = "omniverse://localhost/Projects/OVPOC/Stages"
        LIVE_URL = f"{BASE_URL}/donut.live"
        self.live_layer = Sdf.Layer.FindOrOpen(LIVE_URL)
        self._usd_context = omni.usd.get_context()
        self._stage = self._usd_context.get_stage()
        # self.alert = 0
        self.listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_objects_changed, self._stage)

        self.destroy()

        self._root = sc.Transform(visible=False)
        self._radius = 2
        self._distance_to_top = 5
        self._thickness = 2
        self._radius_hovered = 20

    def destroy(self):
        self._root = None
        self._slider_subscription = None
        self._name_label = None
        self._name_telemtry1 = None
        self._J0_label_name = None
        self._J0_label_val = None
        self._J1_label_name = None
        self._J1_label_val = None
        self._J2_label_name = None
        self._J2_label_val = None
        self._J3_label_name = None
        self._J3_label_val = None
        self._J4_label_name = None
        self._J4_label_val = None
        self._J5_label_name = None
        self._J5_label_val = None
    # def _on_objects_changed(self, notice, stage):
    #     updated_objects = []
    #     for p in notice.GetChangedInfoOnlyPaths():
    #         updated_objects.append(p)

    #     if len(updated_objects) > 0:
    #         self._update_frame(updated_objects)

    # def _update_frame(self, updated_objects):
    #     # properties = []
    #     for o in updated_objects:
    #         attr = self.live_layer.GetAttributeAtPath(o.pathString)
    #         # properties.append(attr)l
    #         path = str(o.pathString)
    #         if "Vacuum_Alert" in path:
    #             self.alert = str(attr.default)
    #             print(f"default: {self.alert}")
    #         else:
    #             continue

    def _on_build_widgets(self):
        with ui.ZStack():
            ui.Rectangle(
                style={
                    "background_color": cl("#000000bf"),
                    "border_color": cl(0.7),
                    "border_width": 0,
                    "border_radius": 4,
                }
            )
            with ui.VStack(style={"font_size": 28,"margin": 8}):


                ui.Spacer(height=2)
                self._name_label = ui.Label("", height=0, alignment=ui.Alignment.CENTER)

                with ui.HStack(width=0):
                    self._J0_label_name = ui.Label("J0", name="prop_label", word_wrap=True, width=100)
                    self._J0_label_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._J1_label_name = ui.Label("J1", name="prop_label", word_wrap=True, width=100)
                    self._J1_label_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._J2_label_name = ui.Label("J2", name="prop_label", word_wrap=True, width=100)
                    self._J2_label_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._J3_label_name = ui.Label("J3", name="prop_label", word_wrap=True, width=100)
                    self._J3_label_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._J4_label_name = ui.Label("J4", name="prop_label", word_wrap=True, width=100)
                    self._J4_label_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._J5_label_name = ui.Label("J5", name="prop_label", word_wrap=True, width=100)
                    self._J5_label_val = ui.Label("", name="prop_value")

                ui.Spacer(height=2)
                self._name_telemtry1 = ui.Label("", height=0, alignment=ui.Alignment.CENTER)

                ui.Spacer(height=10)


        self.on_model_updated(None)

        # Additional gesture that prevents Viewport Legacy selection
        self._widget.gestures += [_DragGesture()]

    def on_build(self):
        """Called when the model is chenged and rebuilds the whole slider"""
        self._root = sc.Transform(visible=False)
        with self._root:
            with sc.Transform(scale_to=sc.Space.SCREEN):
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 100, 0)):
                    # Label
                    with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                        self._widget = sc.Widget(600, 405, update_policy=sc.Widget.UpdatePolicy.ON_MOUSE_HOVERED)
                        self._widget.frame.set_build_fn(self._on_build_widgets)

    def on_model_updated(self, _):
        # if we don't have selection then show nothing
        if not self.model or not self.model.get_item("name"):
            self._root.visible = False
            return

        # Update the shapes
        position = self.model.get_as_floats(self.model.get_item("position"))
        self._root.transform = sc.Matrix44.get_translation_matrix(*position)
        self._root.visible = True

        # Update the slider
        def update_scale(prim_name, value):
            print(f"changing scale of {prim_name}, {value}")


        # Update the shape name
        if self._name_label:
            self._name_label.text = f"Prim:{self.model.get_item('name')}"

        if self._quality_label_val:
            self._name_label.text = f"Prim:{self.model.get_item('name')}"

    def _on_objects_changed(self, notice, stage):
        updated_objects = []
        for p in notice.GetChangedInfoOnlyPaths():
            updated_objects.append(p)

        if len(updated_objects) > 0:
            self._update_frame(updated_objects)

    def _update_frame(self, updated_objects):
        try:
            for o in updated_objects:
                attr = self.live_layer.GetAttributeAtPath(o.pathString)
                path = str(o.pathString)
                if 'RobotPositionJ0' in path:
                    self._J0_label_val.text = str(attr.default)
                elif 'RobotPositionJ1' in path:
                    self._J1_label_val.text = str(attr.default)
                elif 'RobotPositionJ2' in path:
                    self._J2_label_val.text = str(attr.default)
                elif 'RobotPositionJ3' in path:
                    self._J3_label_val.text = str(attr.default)
                elif 'RobotPositionJ4' in path:
                    self._J4_label_val.text = str(attr.default)
                elif 'RobotPositionJ5' in path:
                    self._J5_label_val.text = str(attr.default)
                else:
                    continue
        except:
            print()