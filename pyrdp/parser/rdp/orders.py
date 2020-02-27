#
# This file is part of the PyRDP project.
# Copyright (C) 2018 GoSecure Inc.
# Licensed under the GPLv3 or later.
#

import logging
from io import BytesIO

from pyrdp.core import Uint16LE, Uint8, Uint32LE
from pyrdp.pdu.rdp.fastpath import FastPathOrdersEvent
from pyrdp.enum.rdp import \
        GeneralExtraFlag

LOG = logging.getLogger('pyrdp.fastpath.parser')

# REFACTOR: Pull all of this into pyrdp.enum ---------------------------------------------------
TS_STANDARD = 0x1
TS_SECONDARY = 0x2


def _repr(n) -> str:
    """
    Convert a drawing order type into a string.
    """
    r = n.__doc__
    return r if r else 'UNKNOWN (%02x)'.format(n)


class Primary:
    DSTBLT = 0x00
    PATBLT = 0x01
    SCRBLT = 0x02
    DRAW_NINE_GRID = 0x07
    MULTI_DRAW_NINE_GRID = 0x08
    LINE_TO = 0x09
    OPAQUE_RECT = 0x0A
    SAVE_BITMAP = 0x0B
    MEMBLT = 0x0D
    MEM3BLT = 0x0E
    MULTI_DSTBLT = 0x0F
    MULTI_PATBLT = 0x10
    MULTI_SCRBLT = 0x11
    MULTI_OPAQUE_RECT = 0x12
    FAST_INDEX = 0x13
    POLYGON_SC = 0x14
    POLYGON_CB = 0x15
    POLYLINE = 0x16
    FAST_GLYPH = 0x18
    ELLIPSE_SC = 0x19
    ELLIPSE_CB = 0x1A
    GLYPH_INDEX = 0x1B


class Secondary:
    BITMAP_UNCOMPRESSED = 0x00
    CACHE_COLOR_TABLE = 0x01
    CACHE_BITMAP_COMPRESSED = 0x02
    CACHE_GLYPH = 0x03
    BITMAP_UNCOMPRESSED_V2 = 0x04
    BITMAP_COMPRESSED_V2 = 0x05
    CACHE_BRUSH = 0x07
    BITMAP_COMPRESSED_V3 = 0x08


# Secondary Specific Enums
CBR2_HEIGHT_SAME_AS_WIDTH = 0x01
CBR2_PERSISTENT_KEY_PRESENT = 0x02
CBR2_NO_BITMAP_COMPRESSION_HDR = 0x08
CBR2_DO_NOT_CACHE = 0x10

BITMAP_CACHE_WAITING_LIST_INDEX = 0x7FFF
CG_GLYPH_UNICODE_PRESENT = 0x100


class Alternate:
    SWITCH_SURFACE = 0x00
    CREATE_OFFSCREEN_BITMAP = 0x01
    STREAM_BITMAP_FIRST = 0x02
    STREAM_BITMAP_NEXT = 0x03
    CREATE_NINE_GRID_BITMAP = 0x04
    GDIPLUS_FIRST = 0x05
    GDIPLUS_NEXT = 0x06
    GDIPLUS_END = 0x07
    GDIPLUS_CACHE_FIRST = 0x08
    GDIPLUS_CACHE_NEXT = 0x09
    GDIPLUS_CACHE_END = 0x0A
    WINDOW = 0x0B
    COMPDESK_FIRST = 0x0C
    FRAME_MARKER = 0x0D


# 2.2.2.2.1.2.3
CBR2_BPP = [0, 0, 0, 8, 16, 24, 32]

BPP_CBR2 = [0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0,
            0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0]

CBR23_BPP = [0, 0, 0, 8, 16, 24, 32]

BPP_CBR23 = [0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0,
             0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0]

BMF_BPP = [0, 1, 0, 8, 16, 24, 32, 0]

BPP_BMF = [0, 1, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0,
           0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0]


# These are encoding optimizations proper to Draw Orders
def read_encoded_uint16(s: BytesIO) -> int:
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
# ------------------------------------------------------------------------------ [/REFACTOR]


class OrdersParser:
    """
    Drawing Order Parser.
    """

    def __init__(self):
        # TODO: Create GDI state here.
        self.orders: FastPathOrdersEvent = None

    def parse(self, orders: FastPathOrdersEvent, s: BytesIO):
        """
        Entrypoint for parsing TS_FP_UPDATE_ORDERS.
        """
        self.orders = orders

        numberOrders = Uint16LE.unpack(s)
        for _ in range(numberOrders):
            self.parse_order(s)

        return orders

    def parse_order(self, s: BytesIO):
        controlFlags = Uint8.unpack(s)

        if not (controlFlags & TS_STANDARD):
            print('Type: ALTSEC')  # DEBUG
            self.parse_altsec(s, controlFlags)
        elif (controlFlags & TS_SECONDARY):
            print('Type: SECONDARY')  # DEBUG
            self.parse_secondary(s, controlFlags)
        else:
            print('Type: PRIMARY')  # DEBUG
            self.parse_primary(s, controlFlags)

    # Primary drawing orders.
    # ----------------------------------------------------------------------
    def parse_primary(self, s: BytesIO, flags: int):
        pass

    def parse_dstblt(self, s: BytesIO):
        """DSTBLT"""
        pass

    def parse_patblt(self, s: BytesIO):
        """PATBLT"""
        pass

    def parse_scrblt(self, s: BytesIO):
        """SCRBLT"""
        pass

    def parse_draw_nine_grid(self, s: BytesIO):
        """DRAW_NINE_GRID"""
        pass

    def parse_multi_draw_nine_grid(self, s: BytesIO):
        """MULTI_DRAW_NINE_GRID"""
        pass

    def parse_line_to(self, s: BytesIO):
        """LINE_TO"""
        pass

    def parse_opaque_rect(self, s: BytesIO):
        """OPAQUE_RECT"""
        pass

    def parse_save_bitmap(self, s: BytesIO):
        """SAVE_BITMAP"""
        pass

    def parse_memblt(self, s: BytesIO):
        """MEMBLT"""
        pass

    def parse_mem3blt(self, s: BytesIO):
        """MEM3BLT"""
        pass

    def parse_multi_dstblt(self, s: BytesIO):
        """MULTI_DSTBLT"""
        pass

    def parse_multi_patblt(self, s: BytesIO):
        """MULTI_PATBLT"""
        pass

    def parse_multi_scrblt(self, s: BytesIO):
        """MULTI_SCRBLT"""
        pass

    def parse_multi_opaque_rect(self, s: BytesIO):
        """MULTI_OPAQUE_RECT"""
        pass

    def parse_fast_index(self, s: BytesIO):
        """FAST_INDEX"""
        pass

    def parse_polygon_sc(self, s: BytesIO):
        """POLYGON_SC"""
        pass

    def parse_polygon_cb(self, s: BytesIO):
        """POLYGON_CB"""
        pass

    def parse_polyline(self, s: BytesIO):
        """POLYLINE"""
        pass

    def parse_fast_glyph(self, s: BytesIO):
        """FAST_GLYPH"""
        pass

    def parse_ellipse_sc(self, s: BytesIO):
        """ELLIPSE_SC"""
        pass

    def parse_ellipse_cb(self, s: BytesIO):
        """ELLIPSE_CB"""
        pass

    def parse_glyph_index(self, s: BytesIO):
        """GLYPH_INDEX"""
        pass

    # Secondary drawing orders.
    # ----------------------------------------------------------------------
    def parse_secondary(self, s: BytesIO, flags: int):
        orderLength = Uint16LE.unpack(s)
        extraFlags = Uint16LE.unpack(s)  # TODO: Need to pass these through as well.
        orderType = Uint8.unpack(s)
        # nxt = orderLength + 7

        assert orderType >= 0 and orderType < len(_sec)

        fp = _sec[orderType]
        print(f'Order: {_repr(fp)}')  # DEBUG
        fp(self, s, orderType, extraFlags)

    def parse_cache_bitmap_v1(self, s: BytesIO, orderType: int, flags: int):
        """CACHE_BITMAP_V1"""
        cacheId = Uint8.unpack(s)
        s.read(1)  # Padding
        bitmapWidth = Uint8.unpack(s)
        bitmapHeight = Uint8.unpack(s)
        bitmapBpp = Uint8.unpack(s)

        bitmapLength = Uint16LE.unpack(s)
        cacheIndex = Uint16LE.unpack(s)

        if orderType & Secondary.CACHE_BITMAP_COMPRESSED and \
           not flags & GeneralExtraFlag.NO_BITMAP_COMPRESSION_HDR:
            compression = s.read(8)
            bitmapLength -= 8

        data = s.read(bitmapLength)

    def parse_cache_color_table(self, s: BytesIO, orderType: int, flags: int):
        """CACHE_COLOR_TABLE"""
        cacheIndex = Uint8.unpack(s)
        numberColors = Uint16LE.unpack(s)

        assert numberColors == 256
        colors = [read_color(s) for _ in range(numberColors)]

    def parse_cache_glyph(self, s: BytesIO, orderType: int, flags: int):
        """CACHE_GLYPH"""
        # 2.2.2.2.1.2.5
        cacheId = Uint8.unpack(s)
        cGlyphs = Uint8.unpack(s)

        for _ in range(cGlyphs):
            cacheIndex = Uint16LE.unpack(s)
            cx = Uint16LE.unpack(s)
            cy = Uint16LE.unpack(s)

            cb = ((cx + 7) / 8) * cy
            cb += 4 - (cb % 4) if ((cb % 4) > 0) else 0

            aj = s.read(cb)
            # onGlyph

        if flags & CG_GLYPH_UNICODE_PRESENT and cGlyphs > 0:
            unicodeChars = read_utf16_str(s, cGlyphs)

        # onGlyphUnicodeChars

    def parse_cache_bitmap_v2(self, s: BytesIO, orderType: int, flags: int):
        """CACHE_BITMAP_V2"""
        # 2.2.2.2.1.2.3
        cacheId = flags & 0x0003
        bitmapFlags = (flags & 0xFF80) >> 7
        bpp = CBR2_BPP[(flags & 0x0078) >> 3]

        if bitmapFlags & CBR2_PERSISTENT_KEY_PRESENT:
            key1 = Uint32LE.unpack(s)
            key2 = Uint32LE.unpack(s)

        if bitmapFlags & CBR2_HEIGHT_SAME_AS_WIDTH:
            h = w = read_encoded_uint16(s)
        else:
            w = read_encoded_uint16(s)
            h = read_encoded_uint16(s)

        bitmapLength = read_encoded_uint32(s)
        cacheIndex = read_encoded_uint16(s)

        if bitmapFlags & CBR2_DO_NOT_CACHE:
            cacheIndex = BITMAP_CACHE_WAITING_LIST_INDEX

        if orderType & Secondary.BITMAP_COMPRESSED_V2 and not \
           (bitmapFlags & CBR2_NO_BITMAP_COMPRESSION_HDR):
            # Parse compression header
            cbCompFirstRowSize = Uint16LE.unpack(s)
            cbCompMainBodySize = Uint16LE.unpack(s)
            cbScanWidth = Uint16LE.unpack(s)
            cbUncompressedSize = Uint16LE.unpack(s)

            bitmapLength = cbCompMainBodySize

        # Read bitmap data
        data = s.read(bitmapLength)
        print(data)  # DEBUG

    def parse_cache_brush(self, s: BytesIO, orderType: int, flags: int):
        """CACHE_BRUSH"""
        pass

    def parse_cache_bitmap_v3(self, s: BytesIO, orderType: int, flags: int):
        """CACHE_BITMAP_V3"""
        pass

    # Alternate secondary drawing orders.
    # ----------------------------------------------------------------------
    def parse_altsec(self, s: BytesIO, flags: int):
        orderType = flags >> 2

        # TODO: Log unsupported orders.
        assert orderType >= 0 and orderType < len(_alt)

        fp = _alt[orderType]
        print(f'Order: {_repr(fp)}')  # DEBUG
        fp(self, s)

    def parse_create_offscreen_bitmap(self, s: BytesIO):
        """CREATE_OFFSCREEN_BITMAP"""
        flags = Uint16LE.unpack(s)
        bitmapId = flags & 0x7FFF
        delete = flags & 0x8000 != 0
        cx = Uint16LE.unpack(s)
        cy = Uint16LE.unpack(s)
        # TODO: Create new bitmap entry (Through an observer?)

        # Handle delete list
        # TODO: Update cache (in python this can be a dict.)
        if delete:
            cIndices = Uint16LE.unpack(s)
            for _ in range(cIndices):
                i = Uint16LE.unpack(s)
                # TODO: Delete bitmap from cache.

    def parse_switch_surface(self, s: BytesIO):
        """SWITCH_SURFACE"""
        surfaceId = Uint16LE.unpack(s)

    def parse_create_nine_grid_bitmap(self, s: BytesIO):
        """CREATE_NINEGRID_BITMAP"""
        bpp = Uint8.unpack(s)
        bmpId = Uint16LE.unpack(s)

        flFlags = Uint32LE.unpack(s)
        ulLeftWidth = Uint16LE.unpack(s)
        ulRightWidth = Uint16LE.unpack(s)
        ulTopHeight = Uint16LE.unpack(s)
        ulBottomHeight = Uint16LE.unpack(s)
        rgb = colorref(s)
        # TODO: Allocate the bitmap entry

    def parse_stream_bitmap_first(self, s: BytesIO):
        """STREAM_BITMAP_FIRST"""
        flags = Uint8.unpack(s)
        bpp = Uint8.unpack(s)

        # if bpp < 1 or bpp > 32: Invalid bpp

        bitmapType = Uint16LE.unpack(s)
        width = Uint16LE.unpack(s)
        height = Uint16LE.unpack(s)

        size = 0
        if flags & STREAM_BITMAP_V2:
            size = Uint32LE.unpack(s)
        else:
            size = Uint16LE.unpack(s)

        blockSize = skip16(s)

    def parse_stream_bitmap_next(self, s: BytesIO):
        """STREAM_BITMAP_NEXT"""
        flags = Uint8.unpack(s)
        bitmapType = Uint16LE.unpack(s)
        blockSize = skip16(s)

    def parse_gdiplus_first(self, s: BytesIO):
        """GDIPLUS_FIRST"""
        s.read(1)  # Padding
        cbSize = Uint16LE.unpack(s)  # TODO: Store cbSize
        cbTotalSize = Uint32LE.unpack(s)
        cbTotalEmfSize = Uint32LE.unpack(s)
        emf = s.read(cbSize)

    def parse_gdiplus_next(self, s: BytesIO):
        """GDIPLUS_NEXT"""
        s.read(1)  # Padding
        emf = s.read(cbSize)  # TODO: Get cbSize from context

    def parse_gdiplus_end(self, s: BytesIO):
        """GDIPLUS_END"""
        s.read(1)  # Padding
        cbSize = Uint16LE.unpack(s)
        cbTotalSize = Uint32LE.unpack(s)
        cbTotalEmfSize = Uint32LE.unpack(s)
        emf = s.read(cbSize)  # TODO: Get cbSize from context

    def parse_gdiplus_cache_first(self, s: BytesIO):
        """GDIPLUS_CACHE_FIRST"""
        flags = Uint8.unpack(s)
        cacheType = Uint16LE.unpack(s)
        cacheIndex = Uint16LE.unpack(s)
        cbSize = Uint16LE.unpack(s)
        cbTotalSize = Uint32LE.unpack(s)
        emf = s.read(cbSize)

    def parse_gdiplus_cache_next(self, s: BytesIO):
        """GDIPLUS_CACHE_NEXT"""
        flags = Uint8.unpack(s)
        cacheType = Uint16LE.unpack(s)
        cacheIndex = Uint16LE.unpack(s)
        emf = s.read(cbSize)

    def parse_gdiplus_cache_end(self, s: BytesIO):
        """GDIPLUS_CACHE_END"""
        flags = Uint8.unpack(s)
        cacheType = Uint16LE.unpack(s)
        cacheIndex = Uint16LE.unpack(s)
        cbSize = Uint16LE.unpack(s)
        cbTotalSize = Uint32LE.unpack(s)
        emf = s.read(cbSize)

    def parse_window(self, s: BytesIO):
        """WINDOW"""
        # This is specified in MS-RDPERP for seamless applications.
        LOG.debug('WINDOW is not supported yet.')

    def parse_compdesk_first(self, s: BytesIO):
        """COMPDESK"""
        LOG.debug('COMPDESK is not supported yet.')

    def parse_frame_marker(self, s: BytesIO):
        """FRAME_MARKER"""
        action = Uint32LE.unpack(s)


# Parser Lookup Tables
_pri = [
    OrdersParser.parse_dstblt,  # 0x00
    OrdersParser.parse_patblt,  # 0x01
    OrdersParser.parse_scrblt,  # 0x02
    None,  # 0x03
    None,  # 0x04
    None,  # 0x05
    None,  # 0x06
    OrdersParser.parse_draw_nine_grid,  # 0x07
    OrdersParser.parse_multi_draw_nine_grid,  # 0x08
    OrdersParser.parse_line_to,  # 0x09
    OrdersParser.parse_opaque_rect,  # 0x0A
    OrdersParser.parse_save_bitmap,  # 0x0B
    None,  # 0x0C
    OrdersParser.parse_memblt,  # 0x0D
    OrdersParser.parse_mem3blt,  # 0x0E
    OrdersParser.parse_multi_dstblt,  # 0x0F
    OrdersParser.parse_multi_patblt,  # 0x10
    OrdersParser.parse_multi_scrblt,  # 0x11
    OrdersParser.parse_multi_opaque_rect,  # 0x12
    OrdersParser.parse_fast_index,  # 0x13
    OrdersParser.parse_polygon_sc,  # 0x14
    OrdersParser.parse_polygon_cb,  # 0x15
    OrdersParser.parse_polyline,  # 0x16
    None,
    OrdersParser.parse_fast_glyph,  # 0x18
    OrdersParser.parse_ellipse_sc,  # 0x19
    OrdersParser.parse_ellipse_cb,  # 0x1A
    OrdersParser.parse_glyph_index,  # 0x1B
]

assert len(_pri) == 0x1C

_sec = [
    OrdersParser.parse_cache_bitmap_v1,  # 0x00 : Uncompressed
    OrdersParser.parse_cache_color_table,  # 0x01
    OrdersParser.parse_cache_bitmap_v1,  # 0x02 : Compressed
    OrdersParser.parse_cache_glyph,  # 0x03
    OrdersParser.parse_cache_bitmap_v2,  # 0x04 : Uncompresed
    OrdersParser.parse_cache_bitmap_v2,  # 0x05 : Compressed
    None,  # 0x06
    OrdersParser.parse_cache_brush,  # 0x07
    OrdersParser.parse_cache_bitmap_v3,  # 0x08
]

assert len(_sec) == 0x09

_alt = [
    OrdersParser.parse_switch_surface,  # 0x00
    OrdersParser.parse_create_offscreen_bitmap,  # 0x01
    OrdersParser.parse_stream_bitmap_first,  # 0x02
    OrdersParser.parse_stream_bitmap_next,  # 0x03
    OrdersParser.parse_create_nine_grid_bitmap,  # 0x04
    OrdersParser.parse_gdiplus_first,  # 0x05
    OrdersParser.parse_gdiplus_next,  # 0x06
    OrdersParser.parse_gdiplus_end,  # 0x07
    OrdersParser.parse_gdiplus_cache_first,  # 0x08
    OrdersParser.parse_gdiplus_cache_next,  # 0x09
    OrdersParser.parse_gdiplus_cache_end,  # 0x0A
    OrdersParser.parse_window,  # 0x0B
    OrdersParser.parse_compdesk_first,  # 0x0C
    OrdersParser.parse_frame_marker,  # 0x0D
]

assert len(_alt) == 0x0E
