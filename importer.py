import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from .icn import ICNParser

def read_icn(filepath: str):
    file = open(filepath, "rb")
    data_buffer = file.read()
    icn = ICNParser(data_buffer)
    image = create_image(icn)
    create_mesh(icn, image)


def create_image(icn: ICNParser):
    if icn.texture == None:
        return None
    image = bpy.data.images.get("ICN_TEXTURE")
    if not image:
        image = bpy.data.images.new("ICN_TEXTURE", width=128, height=128, alpha=True)
    
    image.alpha_mode = 'PREMUL'

    pixels = []
    for j in reversed(range(128)):
        for i in range(128):
            p = icn.texture[j * 128 + i]
            r = float(p & 0x1F) / 31
            g = float((p >> 5) & 0x1F) / 31
            b = float((p >> 10) & 0x1F) / 31
            a = 1

            pixels.extend([r, g, b, a])

    image.pixels = pixels
    image.update()
    return image


def create_mesh(icn: ICNParser, image):
    vertices = [(x / 4096, z / 4096, -y / 4096) for (x, y, z, w) in icn.shapes[0]]
    normals = [(x / 4096, z / 4096, -y / 4096) for (x, y, z, w) in icn.normals]
    uvs = [(u / 4096, 1-(v / 4096)) for (u, v) in icn.uvs]

    faces = [(i, i + 1, i + 2) for i in range(0, len(vertices), 3)]

    old_mesh = bpy.data.meshes.get("ICN_MESH")
    if old_mesh:
        bpy.data.meshes.remove(old_mesh)

    old_obj = bpy.data.objects.get("ICN_OBJECT")
    if old_obj:
        bpy.context.collection.objects.unlink(old_obj)
        bpy.data.objects.remove(old_obj)

    old_mat = bpy.data.materials.get("ICN_MATERIAL")
    if old_mat:
        bpy.data.materials.remove(old_mat)

    mesh = bpy.data.meshes.new("ICN_MESH")
    obj = bpy.data.objects.new("ICN_OBJECT", mesh)
    mat = bpy.data.materials.new("ICN_MATERIAL")
    bpy.context.collection.objects.link(obj)

    mesh.from_pydata(vertices, [], faces)

    mesh.uv_layers.new(name="UVMap")

    uv_layer = mesh.uv_layers.active.data
    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            loop_vert_index = mesh.loops[loop_index].vertex_index
            uv_layer[loop_index].uv = uvs[loop_vert_index]

    normals2 = []
    for l in mesh.loops:
        normals2.append(normals[l.vertex_index])
    mesh.normals_split_custom_set(normals2)
    mesh.update()

    if image != None:
        mat.use_nodes = True
        mat.blend_method = "BLEND"
        mat.use_backface_culling = False

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        output = nodes.new(type="ShaderNodeOutputMaterial")
        output.location = (200, 0)

        diffuse = nodes.new("ShaderNodeBsdfDiffuse")
        diffuse.location = (0, 0)

        tex: bpy.types.ShaderNodeTexImage = nodes.new("ShaderNodeTexImage")
        tex.location = (-300, 0)
        tex.image = image

        links.new(tex.outputs["Color"], diffuse.inputs["Color"])
        links.new(diffuse.outputs["BSDF"], output.inputs["Surface"])

        mesh.materials.append(mat)


class IMPORT_OT_ps2_icn(Operator, ImportHelper):
    bl_idname = "imports_scene.icn"
    bl_label = "Import PS2 ICN"
    bl_description = "Imports a PS2 .icn file"
    bl_options = {"PRESET", "UNDO"}

    filter_glob: StringProperty(default="*.icn", options={"HIDDEN"})  # type: ignore

    def execute(self, context):
        read_icn(self.filepath)
        return {"FINISHED"}


def menu_func_import(self: bpy.types.Panel, context: bpy.types.Context):
    self.layout.operator(IMPORT_OT_ps2_icn.bl_idname, text="PS2 ICN (.icn)")


def register():
    bpy.utils.register_class(IMPORT_OT_ps2_icn)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(IMPORT_OT_ps2_icn)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
