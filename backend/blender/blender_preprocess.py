"""
After the mesh is generated, this script will run in Blender to do some post-processing such as decimating the mesh, triangulating, and UV unwrapping.
This process must happen so that the mesh meets roblox's UGC mesh requirements.
Then, it will export the mesh as a .fbx file for Roblox Studio to import.
"""

import sys
import os
import subprocess
import asyncio
import logging
from pathlib import Path

# try to import bpy (only works inside blender)
try:
    import bpy
    import bmesh

    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None
    bmesh = None

# logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlenderProcessor:
    def __init__(self):
        """
        Initialize Blender processor for Roblox UGC optimization
        """
        self.blender_executable = self.find_blender_executable()
        if not self.blender_executable:
            logger.warning("Blender executable not found. Please install Blender.")

    def find_blender_executable(self) -> str:
        """Find Blender executable on the system"""
        possible_paths = [
            "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 3.5\\blender.exe",
            "blender",  # if in PATH
        ]

        for path in possible_paths:
            if os.path.exists(path) or path == "blender":
                try:
                    # test if blender runs
                    result = subprocess.run(
                        [path, "--version"], capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        logger.info(f"Found Blender at: {path}")
                        return path
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue

        return None

    async def roblox_preprocessing(self, mesh_path: str, task_id: str) -> str:
        """
        Process mesh to satisfy Roblox UGC requirements
        """
        if not self.blender_executable:
            raise Exception("Blender not found. Please install Blender.")

        try:
            # create output directory
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)

            fbx_output = output_dir / f"ugc_{task_id}.fbx"

            # create Blender script (only 2 parameters now)
            script_content = self.generate_blender_script(
                input_path=mesh_path,
                fbx_output=str(fbx_output),
            )

            # save script to temporary file
            script_path = Path("temp") / f"blender_script_{task_id}.py"
            script_path.parent.mkdir(exist_ok=True)

            with open(script_path, "w") as f:
                f.write(script_content)

            # run Blender with script
            cmd = [
                self.blender_executable,
                "--background",
                "--python",
                str(script_path),
            ]

            logger.info(f"Running Blender processing: {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown Blender error"
                logger.error(f"Blender processing failed: {error_msg}")
                raise Exception(f"Blender processing failed: {error_msg}")

            logger.info("Blender processing completed successfully")

            # clean up
            script_path.unlink()
            return str(fbx_output)

        except Exception as e:
            logger.error(f"Error in Blender processing: {e}")
            raise

    def generate_blender_script(self, input_path: str, fbx_output: str) -> str:
        """Generate Blender Python script for processing"""
        return f"""
import bpy
import bmesh
import os
import sys

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# import mesh
input_path = r"{input_path}"
if input_path.endswith('.obj'):
    bpy.ops.import_scene.obj(filepath=input_path)
elif input_path.endswith('.ply'):
    bpy.ops.import_mesh.ply(filepath=input_path)
else:
    print("Unsupported file format: " + input_path)
    sys.exit(1)

# get imported object
obj = None
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        obj = o
        break

if not obj:
    print("No mesh object found")
    sys.exit(1)

# select 
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# enter edit mode
bpy.ops.object.mode_set(mode='EDIT')

# get rid of doubles/merge by distance
bmesh_obj = bmesh.from_mesh(obj.data)
bmesh.ops.remove_doubles(bmesh_obj, verts=bmesh_obj.verts, dist=0.001)
bmesh_obj.to_mesh(obj.data)
bmesh_obj.free()

# exit edit mode
bpy.ops.object.mode_set(mode='OBJECT')

# apply scale + rotation
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Roblox UGC Requirements Processing

# 1. decimate mesh to reduce polygon count (Roblox limit: 10K triangles)
decimate_modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
decimate_modifier.ratio = 0.3  # Adjust based on original mesh complexity
bpy.ops.object.modifier_apply(modifier=decimate_modifier.name)

# 2. triangulate the mesh
triangulate_modifier = obj.modifiers.new(name="Triangulate", type='TRIANGULATE')
bpy.ops.object.modifier_apply(modifier=triangulate_modifier.name)

# 3. UV Unwrapping
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
bpy.ops.object.mode_set(mode='OBJECT')

# 4. center the object
bpy.ops.object.origin_set(type='GEOMETRY_TO_ORIGIN', center='MEDIAN')

# 5. scale to reasonable size (Roblox studs)
obj.scale = (2, 2, 2)  # Adjust as needed
bpy.ops.object.transform_apply(scale=True)

# create material (basic for now)
mat = bpy.data.materials.new(name="UGC_Material")
mat.use_nodes = True
obj.data.materials.append(mat)

# export as FBX
fbx_path = r"{fbx_output}"
bpy.ops.export_scene.fbx(
    filepath=fbx_path,
    use_selection=True,
    apply_scale_options='FBX_SCALE_ALL',
    object_types={{'MESH'}},
    use_mesh_modifiers=True,
    mesh_smooth_type='FACE',
    use_tspace=True
)

print("FBX exported to: " + fbx_path)
"""


def run_standalone_processing():
    """Run standalone Blender processing (called from Blender)"""
    # function runs when the script is executed directly in Blender

    input_path = os.getenv("MESH_INPUT_PATH")
    fbx_output = os.getenv("FBX_OUTPUT_PATH")

    if not input_path or not fbx_output:
        print("Missing required environment variables")
        sys.exit(1)

    # process the mesh (simplified version of the full script)
    try:
        # clear scene (the cube)
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

        # import mesh
        if input_path.endswith(".obj"):
            bpy.ops.import_scene.obj(filepath=input_path)

        # get mesh obj
        obj = next((o for o in bpy.context.scene.objects if o.type == "MESH"), None)
        if not obj:
            raise Exception("No mesh found")

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # decimate
        decimate_modifier = obj.modifiers.new(name="Decimate", type="DECIMATE")
        decimate_modifier.ratio = 0.5
        bpy.ops.object.modifier_apply(modifier=decimate_modifier.name)

        # triangulate
        triangulate_modifier = obj.modifiers.new(name="Triangulate", type="TRIANGULATE")
        bpy.ops.object.modifier_apply(modifier=triangulate_modifier.name)

        # export
        bpy.ops.export_scene.fbx(
            filepath=fbx_output, use_selection=True, apply_scale_options="FBX_SCALE_ALL"
        )

        print(f"Successfully exported to: {fbx_output}")

    except Exception as e:
        print(f"Error in processing: {e}")
        sys.exit(1)


if __name__ == "__main__" and "bpy" in sys.modules:
    run_standalone_processing()
