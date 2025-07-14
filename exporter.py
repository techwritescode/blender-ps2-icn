import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper
import bmesh

from .icn.writer import ICNWriter
from .ops.validate import validate

class EXPORT_OT_ps2_icn(Operator, ExportHelper):
    bl_idname = "exports_scene.icn"
    bl_label = "Export PS2 ICN"
    bl_description = "Exports a PS2 .icn file"
    bl_options = {'PRESET', 'REGISTER', 'UNDO_GROUPED'}

    filename_ext = ".icn"

    def execute(self, context):
        validate()
        
        
        mesh = bpy.data.meshes.get("ICN_MESH")
        bm = bmesh.new()
        bm.from_mesh(mesh)

        bmesh.ops.triangulate(bm, faces=bm.faces)

        temp_mesh = bpy.data.meshes.new("icn_export_tri_mesh")
        bm.to_mesh(temp_mesh)
        bm.free()

        texture = bpy.data.images.get("ICN_TEXTURE")

        uv_layer = temp_mesh.uv_layers.active.uv

        vertices = []
        uvs = []
        normals = []

        for poly in temp_mesh.polygons:
            if len(poly.vertices) != 3:
                # Should never happen, but just in case
                continue

            for loop_index in poly.loop_indices:
                loop = temp_mesh.loops[loop_index]
                vert_index = loop.vertex_index
                vertex = temp_mesh.vertices[vert_index]

                vertices.append(vertex.co.copy())
                normals.append(loop.normal.copy())
                
                uv = uv_layer[loop_index].vector
                uvs.append((uv.x, 1-uv.y))

        bpy.data.meshes.remove(temp_mesh)

        writer = ICNWriter(vertices, uvs, normals, texture)
        
        with open(self.filepath, "wb") as f:
            f.write(writer.buffer.getvalue())

        return {'FINISHED'}

def menu_func_export(self: bpy.types.Panel, context: bpy.types.Context):
    self.layout.operator(EXPORT_OT_ps2_icn.bl_idname, text="PS2 ICN (.icn)")

def register():
    bpy.utils.register_class(EXPORT_OT_ps2_icn)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(EXPORT_OT_ps2_icn)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)