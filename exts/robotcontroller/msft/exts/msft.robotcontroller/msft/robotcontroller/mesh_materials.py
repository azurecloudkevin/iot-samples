import omni.usd
import carb
from .gesture import KeyDown
from .constants import Constants
from .messenger import Messenger
from pxr import Usd, Sdf, UsdShade



class MaterialType():
    MATERIAL_ERROR = '/World/Looks/ErrorOverlayMaterial'
    MATERIAL_SELECTED = '/World/Looks/SelectedOverlayMaterial'

class MeshMaterials():
    _hightlighted_prims = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MeshMaterials, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        pass

    def start(self):
        # Track selection
        usd_context = self._get_context()
        self._events = usd_context.get_stage_event_stream()
        self._stage_event_sub = self._events.create_subscription_to_pop(
            self._on_stage_event, name="Object Info Selection Update"
        )

    def _get_context(self) -> Usd.Stage:
        # Get the UsdContext we are attached to
        return omni.usd.get_context()

    def _on_stage_event(self, event):
        """Called by stage_event_stream"""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_kit_selection_changed()

    def highlight_prim(self, prim_path: str, material_path:str = MaterialType.MATERIAL_SELECTED):
        context = self._get_context()
        stage = context.get_stage()
        mtl = UsdShade.Material.Get(stage, Sdf.Path(material_path))
        prim = stage.GetPrimAtPath(prim_path)
        prim.ApplyAPI(UsdShade.MaterialBindingAPI)
        UsdShade.MaterialBindingAPI(prim).Bind(mtl)
        UsdShade.MaterialBindingAPI(prim).SetMaterialBindingStrength(prim.GetAuthoredProperties()[0], UsdShade.Tokens.strongerThanDescendants)
        self._hightlighted_prims[str(prim_path)]=''

    def clear_prim_highlight(self, prim_path: str):
        stage = self._get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        try:
            # print(f"clear prim :::::: {prim_path}")
            UsdShade.MaterialBindingAPI(prim).UnbindDirectBinding()

            del self._hightlighted_prims[str(prim_path)]
        except:
            pass

    def clear_all_highlight(self):
        for prim_path in self.get_hightlighted_prims():
            # carb.log_info(f"clearing prim highlight: {prim_path}")
            self.clear_prim_highlight(prim_path)

    def toggle_selection(self, prim_path: str):
        context = self._get_context()
        stage = context.get_stage()
        prim = stage.GetPrimAtPath(prim_path)

        material_prim = UsdShade.MaterialBindingAPI(prim).GetDirectBinding().GetMaterial().GetPrim()
        if str(material_prim) != Constants.INVALID_NULL_PRIM \
            and material_prim.GetPath() == MaterialType.MATERIAL_SELECTED:

            self.clear_prim_highlight(prim_path)
        else:
            self.highlight_prim(prim_path)

    def _on_kit_selection_changed(self):
        alt_down = KeyDown().test(carb.input.KeyboardInput.LEFT_ALT, carb.input.KeyboardInput.RIGHT_ALT)
        if alt_down:
            old_hightlighted_prims = self._hightlighted_prims.copy()
            prim_paths = self._get_context().get_selection().get_selected_prim_paths()
            for prim_path in prim_paths:
                carb.log_info(f"stage selected prim {prim_path}")
                # print(f"stage selected prim {prim_path}")
                self.toggle_selection(prim_path)

            # print(f"old_hightlighted_prims-> {old_hightlighted_prims}")
            # print(f"self._hightlighted_prims-> {self._hightlighted_prims}")
            if len(set(old_hightlighted_prims.keys()).symmetric_difference(self._hightlighted_prims.keys())) > 0:
                payload = {
                    'old': list(old_hightlighted_prims.keys()),
                    'new': list(self._hightlighted_prims.keys())
                }
                Messenger().push(Messenger.EVENT_HIGHTLIGHTED_PRIMS_CHANGED, payload)

    def get_hightlighted_prims(self):
        return self._hightlighted_prims.keys()

    @staticmethod
    def setup_materials():
        context = omni.usd.get_context()
        stage = context.get_stage()

        # Create Error Overlay Material
        prim = stage.GetPrimAtPath(Sdf.Path(MaterialType.MATERIAL_ERROR))
        if str(prim) == Constants.INVALID_NULL_PRIM:
            mtl_path = Sdf.Path(MaterialType.MATERIAL_ERROR)
            mtl = UsdShade.Material.Define(stage, mtl_path)
            shader = UsdShade.Shader.Define(stage, mtl_path.AppendPath("Shader"))
            shader.CreateIdAttr("UsdPreviewSurface")
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((1.0, 0.0, 0.0))
            shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)
            shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)

            mtl.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")


        prim = stage.GetPrimAtPath(Sdf.Path(MaterialType.MATERIAL_SELECTED))
        if str(prim) == Constants.INVALID_NULL_PRIM:
            # Create Selected part Overlay Material
            mtl_path = Sdf.Path(MaterialType.MATERIAL_SELECTED)
            mtl = UsdShade.Material.Define(stage, mtl_path)
            shader = UsdShade.Shader.Define(stage, mtl_path.AppendPath("Shader"))
            shader.CreateIdAttr("UsdPreviewSurface")
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.0, 0.964, 1.0))
            shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)
            shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
            mtl.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")