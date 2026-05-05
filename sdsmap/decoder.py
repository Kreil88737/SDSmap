import struct
import math
import re

BACKGROUND_COLOR_IDS = (27, 26)
SPAWN_POINT_ID = 22
LIQUID_TYPE_ID = 25
LIQUID_TYPE_NAMES = {
    0: "default",
    1: "lava",
    2: "acid",
}
KNOWN_BLOCK_IDS = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
    20, 21, 23, 24, 28, 29, 30, 31, 32, 33,
)

def _float_to_byte(value: float) -> int:
    return max(0, min(255, int(round(value * 255))))


def _decode_tile_records(data: bytes) -> list:
    vectors = {}
    vec_pat = re.compile(b'\x0f(....)\x02\x00\x00\x00\x0b(.{8})', re.DOTALL)
    for m in vec_pat.finditer(data):
        obj_id = struct.unpack('<I', m.group(1))[0]
        x, y = struct.unpack('<ff', m.group(2))
        vectors[obj_id] = (x, y)

    records = []

    for i in range(4, len(data) - 14):
        if data[i] == 0x09 and data[i+5] == 0x09:
            s_ref = struct.unpack('<I', data[i+1:i+5])[0]
            p_ref = struct.unpack('<I', data[i+6:i+10])[0]

            if s_ref in vectors and p_ref in vectors:
                b_id = struct.unpack('<i', data[i-4:i])[0]
                rot = struct.unpack('<f', data[i+10:i+14])[0]

                if not math.isnan(rot) and not math.isinf(rot):
                    sx, sy = vectors[s_ref]
                    px, py = vectors[p_ref]

                    records.append({
                        "id": b_id,
                        "position": {"x": px, "y": py},
                        "scale": {"x": sx, "y": sy},
                        "rotation": rot,
                    })

    return records


def _decode_color(record: dict) -> dict:
    r = record["position"]["x"]
    g = record["position"]["y"]
    b = record["scale"]["x"]
    a = record["scale"]["y"]

    return {
        "r": _float_to_byte(r),
        "g": _float_to_byte(g),
        "b": _float_to_byte(b),
        "a": _float_to_byte(a),
    }


def _decode_background(records: list):
    colors = {
        record["id"]: _decode_color(record)
        for record in records
        if record["id"] in BACKGROUND_COLOR_IDS
    }
    if not colors:
        return None

    background = {}
    if 27 in colors:
        background["color1"] = colors[27]
    if 26 in colors:
        background["color2"] = colors[26]
    return background


def _decode_liquid(records: list):
    liquid_record = next((record for record in records if record["id"] == LIQUID_TYPE_ID), None)
    if liquid_record is None:
        return None

    liquid_type = int(round(liquid_record["position"]["x"]))
    return {
        "type": liquid_type,
        "name": LIQUID_TYPE_NAMES.get(liquid_type),
    }


def _decode_spawn(records: list):
    spawn_record = next((record for record in records if record["id"] == SPAWN_POINT_ID), None)
    if spawn_record is None:
        return None

    return {
        "position": dict(spawn_record["position"]),
    }


def decode_background(data: bytes) -> dict:
    """
    Decodes the two background gradient colors.
    Color 1 is stored in TileData id 27, color 2 in TileData id 26.
    Channels are stored as normalized floats: position.x=r, position.y=g,
    scale.x=b, scale.y=a.
    """
    return _decode_background(_decode_tile_records(data))


def decode_liquid(data: bytes) -> dict:
    """
    Decodes the bottom liquid type.
    The value is stored in TileData id 25 as position.x:
    0=default, 1=lava, 2=acid.
    """
    return _decode_liquid(_decode_tile_records(data))


def decode_spawn(data: bytes):
    """
    Decodes the explicit player spawn point, if the map stores one.
    The value is stored in TileData id 22 as position.x/position.y.
    Maps without this record use the game's default spawn point.
    """
    return _decode_spawn(_decode_tile_records(data))


def decode_map(data: bytes) -> dict:
    """Decodes user-facing map data: blocks and known optional map values."""
    records = _decode_tile_records(data)
    blocks = [
        {
            "id": record["id"],
            "position": dict(record["position"]),
            "scale": dict(record["scale"]),
            "rotation": record["rotation"],
        }
        for record in records
        if record["id"] in KNOWN_BLOCK_IDS
    ]

    map_data = {"blocks": blocks}

    background = _decode_background(records)
    if background is not None:
        map_data["background"] = background

    liquid = _decode_liquid(records)
    if liquid is not None:
        map_data["liquid"] = liquid

    spawn = _decode_spawn(records)
    if spawn is not None:
        map_data["spawn"] = spawn

    return map_data


def decode(data: bytes) -> list:
    """
    Decodes MS-NRBF binary bytes representing a Supreme Duelist physical map.
    Returns a list of block dictionaries representing the level layout.
    """
    return decode_map(data)["blocks"]


def decode_file(filepath: str) -> list:
    """Reads a .fun file from disk and decodes it."""
    with open(filepath, 'rb') as f:
        data = f.read()
    return decode(data)


def decode_background_file(filepath: str) -> dict:
    """Reads a .fun file from disk and decodes background colors."""
    with open(filepath, 'rb') as f:
        data = f.read()
    return decode_background(data)


def decode_liquid_file(filepath: str) -> dict:
    """Reads a .fun file from disk and decodes the bottom liquid type."""
    with open(filepath, 'rb') as f:
        data = f.read()
    return decode_liquid(data)


def decode_spawn_file(filepath: str):
    """Reads a .fun file from disk and decodes the explicit player spawn point."""
    with open(filepath, 'rb') as f:
        data = f.read()
    return decode_spawn(data)


def decode_map_file(filepath: str) -> dict:
    """Reads a .fun file from disk and decodes blocks and known map-level values."""
    with open(filepath, 'rb') as f:
        data = f.read()
    return decode_map(data)
