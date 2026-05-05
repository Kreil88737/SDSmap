import struct
import base64

PREFIX_B64 = "AAEAAAD/////AQAAAAAAAAAMAgAAAEZBc3NlbWJseS1DU2hhcnAsIFZlcnNpb249MC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1udWxsBQEAAAAIU2F2ZURhdGEBAAAABXRpbGVzA3VTeXN0ZW0uQ29sbGVjdGlvbnMuR2VuZXJpYy5MaXN0YDFbW1RpbGVEYXRhLCBBc3NlbWJseS1DU2hhcnAsIFZlcnNpb249MC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1udWxsXV0CAAAACQMAAAAEAwAAAHVTeXN0ZW0uQ29sbGVjdGlvbnMuR2VuZXJpYy5MaXN0YDFbW1RpbGVEYXRhLCBBc3NlbWJseS1DU2hhcnAsIFZlcnNpb249MC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1udWxsXV0DAAAABl9pdGVtcwVfc2l6ZQhfdmVyc2lvbgQAAApUaWxlRGF0YVtdAgAAAAgICQQAAAA="
BACKGROUND_COLOR_IDS = (27, 26)
SPAWN_POINT_ID = 22
LIQUID_TYPE_ID = 25
DEFAULT_CAPACITY = 32
BACKGROUND_CAPACITY = 4
BACKGROUND_VERSION = 34


def _get_capacity(n: int, minimum: int = DEFAULT_CAPACITY) -> int:
    if n == 0:
        return 0
    cap = minimum
    while cap < n:
        cap *= 2
    return cap


def _channel_to_float(value) -> float:
    if isinstance(value, int):
        return max(0.0, min(1.0, value / 255.0))

    value = float(value)
    if value > 1.0:
        value /= 255.0
    return max(0.0, min(1.0, value))


def _normalize_color(color) -> dict:
    if isinstance(color, dict):
        r = color["r"]
        g = color["g"]
        b = color["b"]
        a = color.get("a", 255)
    else:
        r, g, b, *rest = color
        a = rest[0] if rest else 255

    return {
        "r": _channel_to_float(r),
        "g": _channel_to_float(g),
        "b": _channel_to_float(b),
        "a": _channel_to_float(a),
    }


def _background_records(background: dict) -> list:
    if background is None:
        return []
    if background.get("color1") is None or background.get("color2") is None:
        return []

    color1 = _normalize_color(background["color1"])
    color2 = _normalize_color(background["color2"])

    return [
        {
            "id": 27,
            "position": {"x": color1["r"], "y": color1["g"]},
            "scale": {"x": color1["b"], "y": color1["a"]},
            "rotation": 0.0,
        },
        {
            "id": 26,
            "position": {"x": color2["r"], "y": color2["g"]},
            "scale": {"x": color2["b"], "y": color2["a"]},
            "rotation": 0.0,
        },
    ]


def _read_position(value) -> tuple:
    if isinstance(value, dict):
        position = value.get("position", value)
        return float(position.get("x", 0.0)), float(position.get("y", 0.0))

    try:
        x, y = value
        return float(x), float(y)
    except TypeError:
        return 0.0, float(value)


def _spawn_records(spawn) -> list:
    if spawn is None:
        return []

    if isinstance(spawn, dict):
        position = spawn.get("position", spawn)
        scale = spawn.get("scale", {})
        x = float(position.get("x", 0.0))
        y = float(position.get("y", 0.0))
        scale_x = float(scale.get("x", 1.5))
        scale_y = float(scale.get("y", 4.785813331604004))
        rotation = float(spawn.get("rotation", 0.0))
    else:
        x, y = _read_position(spawn)
        scale_x = 1.5
        scale_y = 4.785813331604004
        rotation = 0.0

    return [
        {
            "id": SPAWN_POINT_ID,
            "position": {"x": x, "y": y},
            "scale": {"x": scale_x, "y": scale_y},
            "rotation": rotation,
        }
    ]


def _liquid_records(liquid) -> list:
    if liquid is None:
        return []

    if isinstance(liquid, dict):
        liquid_type = float(liquid["type"])
    else:
        liquid_type = float(liquid)

    return [
        {
            "id": LIQUID_TYPE_ID,
            "position": {"x": liquid_type, "y": 0.0},
            "scale": {"x": 2.0, "y": 2.0},
            "rotation": 0.0,
        }
    ]


def encode(
    blocks: list,
    background: dict = None,
    liquid=None,
    spawn=None,
) -> bytes:
    background_recs = _background_records(background)
    liquid_recs = _liquid_records(liquid)
    spawn_recs = _spawn_records(spawn)
    if background_recs or liquid_recs or spawn_recs:
        metadata_ids = set(BACKGROUND_COLOR_IDS)
        metadata_ids.add(LIQUID_TYPE_ID)
        metadata_ids.add(SPAWN_POINT_ID)
        blocks = liquid_recs + background_recs + spawn_recs + [
            b for b in blocks
            if b["id"] not in metadata_ids
        ]

    if not blocks:
        blocks = [{"id": 25, "position": {"x": 0.0, "y": 0.0}, "scale": {"x": 2.0, "y": 2.0}, "rotation": 0.0}]

    N = len(blocks)

    out = bytearray(base64.b64decode(PREFIX_B64))
    capacity = _get_capacity(N, BACKGROUND_CAPACITY if background_recs or spawn_recs else DEFAULT_CAPACITY)
    if (background_recs or spawn_recs) and capacity == BACKGROUND_CAPACITY:
        version = BACKGROUND_VERSION
    else:
        version = capacity + N

    out.extend(struct.pack('<I', N))
    out.extend(struct.pack('<I', version))

    out.extend(b'\x07\x04\x00\x00\x00\x00\x01\x00\x00\x00')
    out.extend(struct.pack('<I', capacity))
    out.extend(b'\x04\x08TileData\x02\x00\x00\x00')

    for i in range(N):
        out.extend(b'\x09' + struct.pack('<I', 5 + i))

    null_count = capacity - N
    if null_count == 1:
        out.extend(b'\x0a')
    elif null_count > 1:
        if null_count <= 255:
            out.extend(b'\x0d' + struct.pack('<B', null_count))
        else:
            out.extend(b'\x0e' + struct.pack('<I', null_count))

    vectors_to_write = []
    vector_id_counter = 5 + N

    for i, b in enumerate(blocks):
        b_id = b["id"]
        rot = float(b.get("rotation", 0.0))
        pos = b["position"]
        scl = b["scale"]

        s_vid = vector_id_counter
        vectors_to_write.append((s_vid, float(scl["x"]), float(scl["y"])))
        vector_id_counter += 1

        p_vid = vector_id_counter
        vectors_to_write.append((p_vid, float(pos["x"]), float(pos["y"])))
        vector_id_counter += 1

        if i == 0:
            class_def = (b'\x05\x05\x00\x00\x00\x08TileData\x04\x00\x00\x00'
                         b'\x02id\x05scale\x08position\x08rotation\x00'
                         b'\x07\x07\x00\x08\x0b\x0b\x0b\x02\x00\x00\x00')
            out.extend(class_def)
        else:
            out.extend(b'\x01' + struct.pack('<I', 5 + i) + b'\x05\x00\x00\x00')

        out.extend(struct.pack('<i', b_id))
        out.extend(b'\x09' + struct.pack('<I', s_vid))
        out.extend(b'\x09' + struct.pack('<I', p_vid))
        out.extend(struct.pack('<f', rot))

    for vid, x, y in vectors_to_write:
        out.extend(b'\x0f' + struct.pack('<I', vid) + b'\x02\x00\x00\x00\x0b' + struct.pack('<ff', x, y))

    out.extend(b'\x0b')

    return bytes(out)


def encode_map(map_data: dict) -> bytes:
    """Encodes a decoded map dictionary with blocks and map-level values."""
    return encode(
        map_data["blocks"],
        background=map_data.get("background"),
        liquid=map_data.get("liquid"),
        spawn=map_data.get("spawn"),
    )


def encode_file(
    blocks: list,
    filepath: str,
    background: dict = None,
    liquid=None,
    spawn=None,
):
    """Encodes blocks into binary and saves the .fun map file."""
    with open(filepath, 'wb') as f:
        f.write(encode(blocks, background=background, liquid=liquid, spawn=spawn))


def encode_map_file(map_data: dict, filepath: str):
    """Encodes a map dictionary and saves the .fun map file."""
    with open(filepath, 'wb') as f:
        f.write(encode_map(map_data))
