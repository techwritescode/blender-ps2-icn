import bpy
from mathutils import Matrix, Vector
import gpu
from gpu_extras.batch import batch_for_shader

class ICNBBoxGizmo(bpy.types.Gizmo):
    bl_idname = "VIEW3D_GT_icn_bbox"

    def setup(self):
        self.matrix_basis = Matrix.Identity(4)
    
    def draw(self, context):
        self.draw_cube(context)

    def draw_cube(self, context):
        size = 5.0
        corners = [Vector((x, y, z)) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        corners = [c * (size * 0.5) for c in corners]
        
        edges = [
            (0, 1), (0, 2), (0, 4),
            (1, 3), (1, 5),
            (2, 3), (2, 6),
            (3, 7),
            (4, 5), (4, 6),
            (5, 7),
            (6, 7)
        ]

        cube_world_position = Vector((0, 0, 2.5))
        corners_world = [self.matrix_basis @ (v + cube_world_position) for v in corners]

        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", (1.0, 1.0, 0.0, 1.0))

        for edge in edges:
            v1, v2 = corners_world[edge[0]], corners_world[edge[1]]
            batch = batch_for_shader(shader, 'LINES', {"pos": [v1, v2]})
            batch.draw(shader)

class ICNBBoxGizmoGroup(bpy.types.GizmoGroup):
    bl_idname = "VIEW3D_GGT_icn_bbox"
    bl_label = "PS2 ICN BBox"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D',  'PERSISTENT'}
    bl_gizmo_group_type = "PS2 ICN"

    def setup(self, context):
        gz = self.gizmos.new(ICNBBoxGizmo.bl_idname)
        gz.use_draw_modal = True
        self.gizmo = gz

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.window_manager.show_ps2_icn_bbox_gizmo

    def refresh(self, context):
        self.gizmo.matrix_basis = Matrix.Translation((0, 0, 0))


def draw_bbox_gizmo_toggle(self: bpy.types.Panel, context: bpy.types.Context):
    layout = self.layout

    layout.separator()
    col = layout.column()
    col.label(text="PS2 ICN")
    col.prop(context.window_manager, "show_ps2_icn_bbox_gizmo")

    if context.window_manager.show_ps2_icn_bbox_gizmo:
        bpy.types.WindowManager.gizmo_group_type_ensure(ICNBBoxGizmoGroup.bl_idname)
    else:
        bpy.types.WindowManager.gizmo_group_type_unlink_delayed(ICNBBoxGizmoGroup.bl_idname)

def register():
    bpy.utils.register_class(ICNBBoxGizmo)
    bpy.utils.register_class(ICNBBoxGizmoGroup)
    bpy.types.VIEW3D_PT_gizmo_display.append(draw_bbox_gizmo_toggle)
    bpy.types.WindowManager.show_ps2_icn_bbox_gizmo = bpy.props.BoolProperty(
        name="Extent",
        description="Toggle display of the PS2 ICN extent bounding box",
        default=False
    )

def unregister():
    bpy.utils.unregister_class(ICNBBoxGizmo)
    bpy.utils.unregister_class(ICNBBoxGizmoGroup)
    bpy.types.VIEW3D_PT_gizmo_display.remove(draw_bbox_gizmo_toggle)
    del bpy.types.WindowManager.show_ps2_icn_bbox_gizmo