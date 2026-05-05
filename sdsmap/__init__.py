"""
SDSMap (Supreme Duelist Stickman Map Library)

"""

__version__ = "1.0.0"

from .decoder import (
    KNOWN_BLOCK_IDS,
    decode,
    decode_background,
    decode_background_file,
    decode_file,
    decode_liquid,
    decode_liquid_file,
    decode_map,
    decode_map_file,
    decode_spawn,
    decode_spawn_file,
)
from .encoder import encode, encode_file, encode_map, encode_map_file

__all__ = [
    "KNOWN_BLOCK_IDS",
    "decode",
    "decode_background",
    "decode_background_file",
    "decode_file",
    "decode_liquid",
    "decode_liquid_file",
    "decode_map",
    "decode_map_file",
    "decode_spawn",
    "decode_spawn_file",
    "encode",
    "encode_file",
    "encode_map",
    "encode_map_file",
]
