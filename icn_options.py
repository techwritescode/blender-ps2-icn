import bpy
from bpy.props import BoolProperty
from bpy.types import Panel, Operator

from .ops.validate import PS2_ICN_OT_validate

class ICN_OT_create_scene(Operator):
    bl_idname = "ps2_icn.create_scene"
    bl_label = "Create PS2 ICN"
    bl_description = "Create PS2 ICN scene"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        print("Setup")
        return {'FINISHED'}

class IcnPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

class SCENE_PT_icn_checklist(IcnPanel, Panel):
    bl_label = "Export Checklist"
    bl_parent_id = "SCENE_PT_icn"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        checklist = layout.column()
        checklist.label(text="Geometry")
        col = checklist.box()
        col.label(text="Has UV", icon='CHECKMARK')
        col.label(text="Triangles", icon='ERROR')

        checklist.label(text="Texture")
        col = checklist.box()
        col.label(text="Is 128x128 pixels", icon='CHECKMARK')

        checklist.separator()

        checklist.operator(PS2_ICN_OT_validate.bl_idname)

class SCENE_PT_icn_icon_sys(IcnPanel, Panel):
    bl_label="Icon.sys"
    bl_parent_id = "SCENE_PT_icn"

    def draw(self, context):
        pass

class SCENE_PT_icn_setup(IcnPanel, Panel):
    bl_label="Setup"
    bl_parent_id = "SCENE_PT_icn"

    def draw(self, context):
        layout = self.layout

        layout.operator(ICN_OT_create_scene.bl_idname)

class SCENE_PT_icn(IcnPanel, Panel):
    bl_label = "PS2 ICN"
    bl_idname = "SCENE_PT_icn"

    def draw(self, context):
        pass


classes = (
    SCENE_PT_icn,
    SCENE_PT_icn_checklist,
    SCENE_PT_icn_icon_sys,
    SCENE_PT_icn_setup,
    ICN_OT_create_scene
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
