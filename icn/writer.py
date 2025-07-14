from mathutils import Vector
from bpy.types import Image
import io
import struct


class ICNWriter(object):
    def __init__(
        self,
        vertices: list[Vector],
        uvs: list[(float, float)],
        normals: list[Vector],
        texture: Image,
    ):
        buffer = io.BytesIO()

        magic = 0x10000
        animation_shape_count = 1
        texture_type = 0b0100
        reserved = 0x3F800000
        vertex_count = len(vertices)

        buffer.write(
            struct.pack(
                "IIIII",
                magic,
                animation_shape_count,
                texture_type,
                reserved,
                vertex_count,
            ),
        )

        for i in range(vertex_count):
            # Vertex
            buffer.write(
                struct.pack(
                    "hhhH",
                    int(vertices[i].x * 4096),
                    int(-vertices[i].z * 4096),
                    int(vertices[i].y * 4096),
                    4096,
                )
            )
            # Normal
            buffer.write(
                struct.pack(
                    "hhhH",
                    int(normals[i].x * 4096),
                    int(-normals[i].z * 4096),
                    int(normals[i].y * 4096),
                    4096,
                )
            )
            # UV
            buffer.write(
                struct.pack(
                    "hh",
                    int(uvs[i][0] * 4096),
                    int((1-uvs[i][1]) * 4096),
                )
            )
            # Colour
            buffer.write(struct.pack("BBBB", 255, 255, 255, 255))

        # Animation Header
        tag = 0x01
        frame_length = 31
        anim_speed = 1.0
        play_offset = 0
        frame_count = 0

        buffer.write(
            struct.pack(
                "IIfII", tag, frame_length, anim_speed, play_offset, frame_count
            )
        )

        # TODO: Add animation

        pixels = texture.pixels
        for i in range(0, 128 * 128 * 4, 4):
            r = int(pixels[i+0] * 31) & 0x1F
            g = int(pixels[i+1] * 31) & 0x1F
            b = int(pixels[i+2] * 31) & 0x1F
            a = int(0)

            word = a | (b << 10) | (g << 5) | r
            
            buffer.write(struct.pack("H", word))

        self.buffer = buffer
