import omni.ext
import omni.kit.commands
import omni.usd
from pxr import Usd, Sdf, Tf
import math
from pxr import Gf
from .robotmotion import RobotMotion


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MsftOmniAnimateExtension(omni.ext.IExt):
    robot = RobotMotion('/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003', ['link1piv_003', 'link2piv_003', 'link3piv_003', 'link4piv_003','link5piv_003', 'link6piv_003'])

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[msft.omni.animate] msft omni animate startup")
        BASE_URL = "omniverse://localhost/Projects/OVPOC/Stages"
        LIVE_URL = f"{BASE_URL}/donut.live"
        self.live_layer = Sdf.Layer.FindOrOpen(LIVE_URL)
        self._usd_context = omni.usd.get_context()
        self._stage = self._usd_context.get_stage()
        self.listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_objects_changed, self._stage)

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
                attr = self.live_layer.GetAttributeAtPath(o.pathString)
                if("J0" in o.pathString):
                    self.robot.SetAngleDegrees(0,attr.default)
                elif("J1" in o.pathString):
                    self.robot.SetAngleDegrees(1,attr.default)
                elif("J2" in o.pathString):
                    self.robot.SetAngleDegrees(2,attr.default)
                elif("J3" in o.pathString):
                    self.robot.SetAngleDegrees(3,attr.default)
                elif("J4" in o.pathString):
                    self.robot.SetAngleDegrees(4,attr.default)
                elif("J5" in o.pathString):
                    self.robot.SetAngleDegrees(5,attr.default)
                else:
                    continue
        except:
            print()
