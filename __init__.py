from . import importer, exporter, icn_options, gizmo
from .ops import validate

# class CreateICNOperator(bpy.types.Operator):
#     bl_idname = "object.create_icn"
#     bl_label = "Create ICN"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context):
#         bpy.ops.object.select_by_type(type='LIGHT')
#         bpy.ops.object.delete()

#         context.scene.camera.location = (0, -10.0, 0)
#         context.scene.camera.rotation_euler = (math.pi/2, 0, 0)
            
#         return {"FINISHED"}

#     def invoke(self, context, event):
#         return context.window_manager.invoke_confirm(self, event, message="This will delete all items in the scene. Continue?", icon='WARNING')

# class VIEW3D_PT_icn_panel(bpy.types.Panel):
#     bl_label = "ICN Panel"
#     bl_idname = "VIEW3D_PT_icn_panel"
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = 'ICN'

#     def draw(self, context):
#         layout = self.layout
#         layout.operator(CreateICNOperator.bl_idname, text="Create ICN")


def register():
    importer.register()
    exporter.register()
    icn_options.register()
    validate.register()
    gizmo.register()

def unregister():
    importer.unregister()
    exporter.unregister()
    icn_options.unregister()
    validate.unregister()
    gizmo.unregister()
    
