import omni.ui as ui
import omni.usd
import carb
from omni.ui import color as cl
from pxr import Usd, Tf, UsdGeom, UsdShade


class InfoWidgetProvider():
    """
        Info widget, showing a list of properties in a kkey value structure
    """

    def __init__(self):
        self.is_pinned = False
        self.usd_context = omni.usd.get_context()
        self.stage = self.usd_context.get_stage()
        self.stage_event_sub = omni.usd.get_context().get_stage_event_stream().create_subscription_to_pop(
            self._on_stage_event, name="Object Info Selection Update"
        )

    def _on_kit_selection_changed(self):
        # selection change, reset it for now

        self._current_path = ""

        if not self.stage:
            return

        prim_paths = self.usd_context.get_selection().get_selected_prim_paths()
        # if not prim_paths:
        #     self._item_changed(self.position)
        #     # Revoke the Tf.Notice listener, we don't need to update anything
        #     if self._stage_listener:
        #         self._stage_listener.Revoke()
        #         self._stage_listener = None
        #     return

        prim = self.stage.GetPrimAtPath(prim_paths[0])

        if prim.IsA(UsdGeom.Imageable):
            material, relationship = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
            if material:
                self.material_name = str(material.GetPath())
            else:
                self.material_name = "N/A"

            self._placer.visible = True
        else:
            self._prim = None
            return

        self._prim = prim
        self._current_path = prim_paths[0]

    def _on_stage_event(self, event):
        """Called by stage_event_stream"""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_kit_selection_changed()

    _whitelisted_props = (
        # allowed list of properties
    )

    def _order_and_filter_data(self):
        records = dict.copy(self._data)
        if self._whitelisted_props:
            records = dict((k, v) for k, v in records.items() if k in self._whitelisted_props)
        result = dict(sorted(records.items(), key=lambda kv: kv[0]))
        return result

    def _widget_header(self):
        with self._ui_header_frame:
            with ui.Stack(ui.Direction.RIGHT_TO_LEFT):
                ui.Button(text=" x ", width=0, height=0, clicked_fn=lambda *args: self.close())
                ui.Button(text="Unpin" if self.is_pinned else "Pin", width=0, height=0, clicked_fn=lambda *args: self.togglePin())
                ui.Spacer()

    def widget_header(self, style={"margin":2}):
        with ui.VStack(height=0,style=style):
            self._ui_header_frame = ui.Frame(name="ui_widget_header_frame")
            self._widget_header()

    def close(self):
        self._placer.visible = False

    def togglePin(self):
        self.is_pinned = not self.is_pinned
        self._widget_header()

    def build_widget(self, viewport_window):
        # if not self._placer.visible:
        #     self._placer.visible = True

        self._placer = ui.Placer(visible = False, draggable=True, offset_x=100, offset_y = 100, height = 50)
        with self._placer:
            with ui.ZStack(height=50, width=500, style={"margin":2}):
                ui.Rectangle(
                    style={
                        # "background_color": cl(0.2),
                        "background_color": cl("#000670bf"), #111eff   #00089f
                        "border_color": cl("#00055c"),
                        "border_width": 1,
                        "border_radius": 4,
                    }
                )

                with ui.VStack(height=50):
                    self.widget_header()
                    self._render_body()

    def _render_body(self):
        # def on_mouse_wheel(self, x, y, modifier):
        #     if modifier == carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT:
        #         # scroll horizontally
        #         scroll_x = max(0, min(self._scrollingFrame.scroll_x - x, self._scrollingFrame.scroll_x_max))
        #         self._scrollingFrame.scroll_here(scroll_x, self._scrollingFrame.scroll_y)
        #     else:
        #         # scroll vertically
        #         scroll_y = max(0, min(self._scrollingFrame.scroll_y - y, self._scrollingFrame.scroll_y_max))
        #         self._scrollingFrame.scroll_here(self._scrollingFrame.scroll_x, scroll_y)
        # self.viewport_window.frame.set_mouse_wheel_fn(on_mouse_wheel)


        self._zstack = ui.ZStack(height = 50)
        self._scrollingFrame = ui.ScrollingFrame(
                style={
                    "background_color": cl("#000000bf"),
                    "border_width": 10,
                    "border_color": cl(0.7),
                    "border_radius": 4,
                    "scrollbar_policy": ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    "scrollbar_width": 100,
                    "scrollbar_color": cl(0.9),
                    "scrollbar_background_color": cl(0.3),
                }
            )
        with self._zstack:
            self._scrollingFrame
                # with ui.Frame():
                #     # Create a grid layout manager
                #     with ui.Grid(ui.Direction.TOP_TO_BOTTOM, selected=True):
                #     # Add some labels to the grid
                #         for i in range(40):
                #             with ui.HStack(width=0):
                #                 self._J1_label_name = ui.Label(f"J{i}", name="prop_label", word_wrap=True, width=100)
            # self._rectangle = ui.Rectangle(
            #     width=800,
            #     height=800,
            #     style={
            #         "background_color": cl("#000000bf"),
            #         "border_color": cl(0.7),
            #         "border_width": 0,
            #         "border_radius": 4,
            #     }
            # )

            self._mainStack = ui.VStack(style={"font_size": 28,"margin": 8}, height = 50)
            with self._mainStack:
                # ui.Button(text=" x ", width=0, height=0, clicked_fn=lambda *args: self.close(), alignment=ui.Alignment.RIGHT)
                ui.Spacer(height=2)
                self._name_label = ui.Label("", height=0, alignment=ui.Alignment.CENTER)
                # sparkline = ui.Sparkline(parent=window, name='sparkline', data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
                # data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
                # with ui.HStack():
                #     ui.Spacer(width=200) # align the sparklines with the scrollable frame
                #     for value in data:
                #         with ui.VStack():
                #             ui.Sparkline(
                #                 data=[value],
                #                 style={
                #                     "sparkline_type": 0,
                #                     "sparkline_color": cl(0.9),
                #                     "sparkline_width": 2,
                #                     "marker_color": cl(0.9),
                #                     "marker_size": 4,
                #                     "show_markers": True,
                #                 },
                #             )
                #         ui.Label(str(value), alignment=ui.Alignment.CENTER)

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
                with ui.HStack(width=0):
                    self._robot_quality_name = ui.Label("quality", name="prop_label", word_wrap=True, width=100)
                    self._robot_quality_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._pressure_name = ui.Label("pressure", name="prop_label", word_wrap=False, width=100)
                    self._pressure_val = ui.Label("", name="prop_value")
                with ui.HStack(width=0):
                    self._alert_name = ui.Label("alert", name="prop_label", word_wrap=True, width=100)
                    self._alert_val = ui.Label("", name="prop_value")

        self._scrollingFrame.add_child(self._mainStack)
        # self._scrollingFrame.scroll_only_window_hovered = False
        # self._scrollingFrame.set_mouse_wheel_fn(on_mouse_wheel)
        # self._scrollingFrame.scroll_here(0, 1)

        # self._scrollingFrame.set_scroll_y_changed_fn(on_mouse_wheel)

        # Set the functions to be called when the scroll bars are moved
        self._scrollingFrame.set_scroll_x_changed_fn(lambda x: print(f"Horizontal scroll bar moved to {x}"))
        self._scrollingFrame.set_scroll_y_changed_fn(lambda y: print(f"Vertical scroll bar moved to {y}"))

        self.listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_objects_changed, self.stage)

        # Register the function to be called when a mouse wheel event occurs
        # carb.events.register_listener(self.handle_mouse_wheel, "carb.input.mouse.wheel")

        # self._scrollingFrame = ui.ScrollingFrame
        # self._scrollingFrame.set_mouse_wheel_fn(on_mouse_wheel)

    def _on_objects_changed(self, notice, stage):
        updated_objects = []
        for p in notice.GetChangedInfoOnlyPaths():
            if "Value" in str(p.pathString):
                updated_objects.append(p)

        if len(updated_objects) > 0:
            self._update_frame(updated_objects)

    def _update_frame(self, updated_objects):
        path = None
        try:
            for o in updated_objects:
                path = o.pathString
                prim = self.stage.GetPrimAtPath(o.pathString.split('.')[0])
                attr = prim.GetAttribute(o.pathString.split('.')[1])
                if attr is None:
                    continue

                val = str(round(float(attr.Get()), 2))
                # path = str(o.pathString)
                if 'j0' in o.pathString:
                    self._J0_label_val.text = val
                elif 'j1' in o.pathString:
                    self._J1_label_val.text = val
                elif 'j2' in o.pathString:
                    self._J2_label_val.text = val
                elif 'j3' in o.pathString:
                    self._J3_label_val.text = val
                elif 'j4' in o.pathString:
                    self._J4_label_val.text = val
                elif 'j5' in o.pathString:
                    self._J5_label_val.text = val
                elif 'quality' in o.pathString:
                    self._robot_quality_val.text = val
                elif 'pressure' in o.pathString:
                    self._pressure_val.text = val
                elif 'alert' in o.pathString:
                    self._alert_val.text = val
                else:
                    continue
        except Exception as e:
            print(f'Failed to update frame {path} with error: {e}')