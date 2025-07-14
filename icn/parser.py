
import struct


class ICNAnimationData(object):
    def __init__(self, tag, frame_length, anim_speed, play_offset, frame_count, frames):
        self.tag = tag
        self.frame_length = frame_length
        self.anim_speed = anim_speed
        self.play_offset = play_offset
        self.frame_count = frame_count
        self.frames = frames

    @classmethod
    def parse(cls, buf: bytes, offset):
        (tag, frame_length, anim_speed, play_offset, frame_count) = struct.unpack(
            "IIfII", buf[offset : offset + 0x14]
        )
        offset += 0x14

        assert tag == 0x01

        frames = []
        for j in range(frame_count):
            shape_id, key_count = struct.unpack("II", buf[offset : offset + 0x8])
            offset += 0x8

            keys = []

            for i in range(key_count):
                time, value = struct.unpack("ff", buf[offset : offset + 0x8])
                offset += 0x8
                keys.append((time, value))

            frames.append((shape_id, key_count, keys))

        return offset, ICNAnimationData(
            tag, frame_length, anim_speed, play_offset, frame_count, frames
        )


class ICNParser(object):
    def __init__(self, buf: bytes):
        offset = 0
        (
            self.magic,
            self.animation_shape_count,
            self.texture_type,
            self.reserved,
            self.vertex_count,
        ) = struct.unpack("IIIII", buf[offset : offset + 0x14])
        offset += 0x14

        if self.magic != 0x10000:
            raise ValueError("Invalid ICN file")

        self.shapes = [
            [(0, 0, 0, 0) for i in range(self.vertex_count)]
            for j in range(self.animation_shape_count)
        ]
        self.normals = []
        self.uvs = []
        self.colors = []

        for i in range(self.vertex_count):
            for j in range(self.animation_shape_count):
                x, y, z, w = struct.unpack("hhhH", buf[offset : offset + 0x8])
                offset += 0x8
                self.shapes[j][i] = (x, y, z, w)

            x, y, z, w = struct.unpack("hhhH", buf[offset : offset + 0x8])
            offset += 0x8
            self.normals.append((x, y, z, w))

            u, v = struct.unpack("hh", buf[offset : offset + 0x4])
            offset += 0x4
            self.uvs.append((u, v))

            r, g, b, a = struct.unpack("BBBB", buf[offset : offset + 0x4])
            offset += 0x4
            self.colors.append((r, g, b, a))

        offset, self.animation_data = ICNAnimationData.parse(buf, offset)

        self.parse_texture(buf, offset)

    def parse_texture(self, buf, offset):
        if self.texture_type & 0b0100 > 0:
            if self.texture_type & 0b1000 > 0:
                self.parse_texture_compressed(buf, offset)
            else:
                self.parse_texture_uncompressed(buf, offset)
        else:
            self.texture = None

    def parse_texture_uncompressed(self, buf, offset):
        (self.texture,) = struct.unpack("16384H", buf[offset : offset + 16384])

    def parse_texture_compressed(self, buf, offset):
        (size,) = struct.unpack("I", buf[offset : offset + 4])
        short_size = size // 2
        offset += 4

        compressed = list(struct.unpack(f"{short_size}H", buf[offset : offset + size]))

        TEXTURE_SIZE = 16384

        pixels = [0 for i in range(TEXTURE_SIZE)]

        idx = 0
        off = 0

        while off < short_size:
            rep_count = compressed[off]
            off += 1

            if rep_count < 0xFF00:
                pixel = compressed[off]
                off += 1
                for i in range(rep_count):
                    if idx > TEXTURE_SIZE:
                        break
                    pixels[idx] = pixel
                    idx += 1
            else:
                actual_count = 0xFFFF ^ rep_count
                for i in range(actual_count + 1):
                    if idx >= TEXTURE_SIZE:
                        break
                    pixel = compressed[off]
                    off += 1
                    pixels[idx] = pixel
                    idx += 1
        self.texture = pixels