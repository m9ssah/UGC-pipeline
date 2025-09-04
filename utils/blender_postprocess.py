"""
After the mesh is generated, this script will run in Blender to do some post-processing such as decimating the mesh, triangulating, and UV unwrapping.
This process must happen so that the mesh meets roblox's UGC mesh requirements.
Then, it will export the mesh as a .fbx file for Roblox Studio to import.
"""

import bpy, sys, os

obj = next(o for o in bpy.data.objects if o.type == 'MESH')

# Decimate the mesh to reduce polycount
dec = obj.modifiers.new(name='Decimate', type='DECIMATE'); dec.ratio = 0.5
bpy.context.view_layer.objects.active = obj
bpy.ops.object.modifier_apply(modifier=dec.name)

# Triangulate the mesh
tri = obj.modifiers.new(name='Triangulate', type='TRIANGULATE')
bpy.ops.object.modifier_apply(modifier=tri.name)

# Export as .fbx
bpy.ops.export_scene.fbx(filepath=os.getenv('FBX_OUTPUT_PATH'), use_selection=True, apply_scale_options='FBX_SCALE_ALL')