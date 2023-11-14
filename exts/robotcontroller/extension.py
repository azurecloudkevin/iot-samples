import omni.ext
import asyncio
import omni.ui as ui
import omni.kit.commands
import omni.usd
import carb
import pxr
from pxr import Usd, Sdf, UsdShade
import math
from math import degrees
from pxr import Gf, UsdGeom
from pxr import Gf

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MsftOmniAnimateExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[msft.omni.animate] msft omni animate startup")

        base_prim_id="/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003/"
        self.level1 = 0
        self.level2 = 0
        self.level3 = 0
        self.level4 = 0
      
        self._window = ui.Window("Robot Controller", width=300, height=300)
        with self._window.frame:
            with ui.VStack():

                context = self._get_context()
                stage = context.get_stage()

                async def startAnimating(self):
                    self.animating = True
                    while self.animating:
                        prim = stage.GetPrimAtPath(base_prim_id+id)
                        if prim:
                            attribute = prim.GetAttribute("xformOp:orient")
                            attribute_value = attribute.Get()
                            self.level1+=1
                            new_rotation =self.vector_to_quat(0,0,self.level1)
                            attribute.Set(value=new_rotation)
                        await asyncio.sleep(self.ms / 1000)

                def stopAnimating(self):
                    self.animating = False

                def rotate_plus(id,angle):
                    on_move(id,.1,angle)

                def rotate_minus(id,angle):
                    on_move(id,-.1,angle)

                def on_move(id,count,level):
                    prim = stage.GetPrimAtPath(base_prim_id+id)
                    if prim:
                        attribute = prim.GetAttribute("xformOp:orient")
                        attribute_value = attribute.Get()

                        if(level=="level1"):
                            self.level1+=count
                            new_rotation =self.vector_to_quat(0,0,self.level1)
                        if(level=="level2"):
                            self.level2+=count
                            new_rotation =self.vector_to_quat(0,self.level2,0)
                        if(level=="level3"):
                            self.level3+=count
                            new_rotation =self.vector_to_quat(0,self.level3,0)
                        if(level=="level4"):
                            self.level4+=count
                            new_rotation =self.vector_to_quat(0,self.level4,0)

                        attribute.Set(value=new_rotation)


                with ui.HStack(): 
                    level1="level1"
                    id1="link1piv_003"
                    ui.Button("Base Rotate +", clicked_fn=lambda: rotate_plus(id1,level1))
                    ui.Button("Base Rotate -", clicked_fn=lambda: rotate_minus(id1,level1))
                
                with ui.HStack():
                    level2="level2"
                    id2="link1piv_003/link2piv_003"
                    ui.Button("Arm 1 Rotate +", clicked_fn=lambda: rotate_plus(id2,level2))
                    ui.Button("Arm 1 Rotate -", clicked_fn=lambda: rotate_minus(id2,level2))

                with ui.HStack():
                    level3="level3"
                    id3="link1piv_003/link2piv_003/link3piv_003"
                    ui.Button("Arm 2 Rotate +", clicked_fn=lambda: rotate_plus(id3,level3))
                    ui.Button("Arm 2 Rotate -", clicked_fn=lambda: rotate_minus(id3,level3))
                
                with ui.HStack():
                    level4="level4"
                    id4="link1piv_003/link2piv_003/link3piv_003/link4piv_003/link5piv_003"
                    ui.Button("Arm 3 Rotate +", clicked_fn=lambda: rotate_plus(id4,level4))
                    ui.Button("Arm 3 Rotate -", clicked_fn=lambda: rotate_minus(id4,level4))
    
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

    def degrees_to_vector(self,angle_degrees, plane='xz'):
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

