import os
import omni.ext
import omni.kit.commands
import omni.usd
from pxr import Usd, Sdf, Tf, Gf
import math
from pathlib import Path
from .robotmotion import RobotMotion
from .mesh_materials import MeshMaterials
import omni.kit.usd.layers as layers
from dotenv import load_dotenv

env = f"{Path(__file__).parents[7]}\\.env"

load_dotenv(env)

host = os.getenv('omniverse_host')
robot_base_path = os.getenv('robot_base_path')
jointList = os.getenv('robot_joint_paths')


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MsftOmniAnimateExtension(omni.ext.IExt):
    joints = str(jointList).replace(' ', '').split(',')
    robot = RobotMotion(robot_base_path, joints)

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[msft.omni.animate] msft omni animate startup")
        BASE_URL = f"omniverse://{host}/Projects/OVPOC/Stages"
        LIVE_URL = f"{BASE_URL}/donut.live"
        self.live_layer = Sdf.Layer.FindOrOpen(LIVE_URL)
        self._usd_context = omni.usd.get_context()
        self._stage = self._usd_context.get_stage()
        self._live_syncing = layers.get_live_syncing(self._usd_context)

        self._layers = layers.get_layers(self._usd_context)
        self._sessionLayer = self._stage.GetSessionLayer()

        self._sessionLayer.startTimeCode = 1
        self._sessionLayer.endTimeCode = 192

        self._iot_prim = self._stage.GetPrimAtPath("/iot")
        self.listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged,
                                           self._on_objects_changed,
                                           self._stage)
        self._mesh_materials = MeshMaterials()
        self._mesh_materials.start()

    def _get_context(self) -> Usd.Stage:
        # Get the UsdContext we are attached to
        return omni.usd.get_context()

    def on_shutdown(self):
        print("[msft.omni.animate] msft omni animate shutdown")

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

    def degrees_to_vector(self, angle_degrees, plane='xz'):
        # Convert the angle to radians
        angle_radians = math.radians(angle_degrees)

        # Calculate the vector components based on the specified plane
        if plane == 'xy':
            x = math.cos(angle_radians)
            y = math.sin(angle_radians)
            z = 0.0
        elif plane == 'xz':
            x = math.cos(angle_radians)
            y = 0.0
            z = math.sin(angle_radians)
        elif plane == 'yz':
            x = 0.0
            y = math.cos(angle_radians)
            z = math.sin(angle_radians)
        else:
            raise ValueError("Invalid plane. Supported planes: 'xy', 'xz', 'yz'")

        # Create a 3D vector
        return (x, y, z)

    def _on_objects_changed(self, notice, stage):
        updated_objects = []
        for p in notice.GetChangedInfoOnlyPaths():
            updated_objects.append(p)

        if len(updated_objects) > 0:
            self._update_frame(updated_objects)

    def _update_frame(self, updated_objects):
        try:
            for o in updated_objects:
                #attr = self.live_layer.GetAttributeAtPath(o.pathString)
                prim = self._stage.GetPrimAtPath(o.pathString.split('.')[0])
                attr = prim.GetAttribute(o.pathString.split('.')[1])
                if "Value" in o.pathString:
                    val = float(attr.Get())
                    # attr = self._sessionLayer.GetAttributeAtPath(o.pathString)
                    if "j0" in o.pathString:
                        self.robot.SetAngleDegrees(0, val)
                    elif "j1" in o.pathString:
                        self.robot.SetAngleDegrees(1, val)
                    elif "j2" in o.pathString:
                        self.robot.SetAngleDegrees(2, val)
                    elif "j3" in o.pathString:
                        self.robot.SetAngleDegrees(3, val)
                    elif "j4" in o.pathString:
                        self.robot.SetAngleDegrees(4, val)
                    elif "j5" in o.pathString:
                        self.robot.SetAngleDegrees(5, val)
                    elif "VacuumPressure" in o.pathString:
                        if val > 0:
                            self._mesh_materials.highlight_prim(prim_path=prim)
                        else:
                            self._mesh_materials.clear_prim_highlight(prim)
                    else:
                        continue
        except Exception as e:
            print(f"An error occurred: {e}")
