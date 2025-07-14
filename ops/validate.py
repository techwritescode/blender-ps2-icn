import bpy
from bpy.types import Operator

def validate():
    texture = bpy.data.images.get("ICN_TEXTURE")
    if texture is None:
        return "Missing Texture ICN_TEXTURE"
    
    width, height = texture.size
    if width != 128 or height != 128:
        return "Texture must be 128x128 pixels"
    
    obj = bpy.data.objects.get("ICN_OBJECT")
    if obj is None:
        return "Missing Object ICN_OBJECT"

    mesh = bpy.data.meshes.get("ICN_MESH")
    if mesh is None:
        return "Missing Mesh ICN_MESH"
    
    if len(mesh.uv_layers) == 0:
        return "Missing UV layer"

class PS2_ICN_OT_validate(Operator):
    bl_idname = "ps2_icn.validate"
    bl_label = "Validate"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        results = validate()

        if results:
            self.report({'ERROR'}, f"ICN Error: {results}")
            return {'CANCELLED'}
        
        self.report({'INFO'}, "ICN Validation Succeeded")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PS2_ICN_OT_validate)

def unregister():
    bpy.utils.unregister_class(PS2_ICN_OT_validate)