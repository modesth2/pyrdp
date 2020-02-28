"""
Common String Reading Utilities
"""
from io import BytesIO
from pyrdp.core.packing import Uint8, Uint16LE, Uint32LE


def read_encoded_uint16(s: BytesIO) -> int:
    """Read an encoded UINT16."""
    # 2.2.2.2.1.2.1.3
    b = Uint8.unpack(s)
    if b & 0x80:
        return (b & 0x7F) << 8 | Uint8.unpack(s)
    else:
        return b & 0x7F


def read_encoded_uint32(s: BytesIO) -> int:
    # 2.2.2.2.1.2.1.4
    b = Uint8.unpack(s)
    n = (b & 0xC0) >> 6
    if n == 0:
        return b & 0x3F
    elif n == 1:
        return (b & 0x3F) << 8 | Uint8.unpack(s)
    elif n == 2:
        return ((b & 0x3F) << 16 | Uint8.unpack(s) << 8 | Uint8.unpack(s))
    else:  # 3
        return ((b & 0x3F) << 24 |
                Uint8.unpack(s) << 16 |
                Uint8.unpack(s) << 8 |
                Uint8.unpack(s))


def read_color(s: BytesIO):
    """
    2.2.2.2.1.3.4.1.1 TS_COLORREF ->  rgb
    2.2.2.2.1.2.4.1   TS_COLOR_QUAD -> bgr
    """
    return Uint32LE.unpack(s) & 0x00FFFFFF


def read_utf16_str(s: BytesIO, size: int) -> bytes:
    return bytes([Uint16LE.unpack(s) for _ in range(size)])  # Decode into str?


def read_field_flags(s: BytesIO):
    pass
