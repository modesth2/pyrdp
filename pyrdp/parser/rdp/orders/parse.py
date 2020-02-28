#
# This file is part of the PyRDP project.
# Copyright (C) 2019 GoSecure Inc.
# Licensed under the GPLv3 or later.
#
"""
Parse Drawing Orders.
"""
import logging
from io import BytesIO

from pyrdp.core import Uint16LE, Uint8, Uint32LE
from pyrdp.pdu.rdp.fastpath import FastPathOrdersEvent
from pyrdp.enum.rdp import GeneralExtraFlag
from pyrdp.enum.orders import Secondary, \
        DrawingOrderControlFlags as ControlFlags

from pyrdp.parser.rdp.orders.secondary import CBR2_BPP, CBR23_BPP, BMF_BPP, \
    CBR2_HEIGHT_SAME_AS_WIDTH, CBR2_PERSISTENT_KEY_PRESENT, CBR2_NO_BITMAP_COMPRESSION_HDR, CBR2_DO_NOT_CACHE

LOG = logging.getLogger('pyrdp.fastpath.parser')

# REFACTOR: Pull these constants.
BITMAP_CACHE_WAITING_LIST_INDEX = 0x7FFF
CG_GLYPH_UNICODE_PRESENT = 0x100


def _repr(n):
    """Convert a drawing order type into a string."""
    r = n.__doc__
    return r if r else 'UNKNOWN (%02x)'.format(n)


# These are encoding optimizations proper to Draw Orders
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
            self._parse_order(s)

        return orders

    def _parse_order(self, s: BytesIO):
        controlFlags = Uint8.unpack(s)

        if not (controlFlags & ControlFlags.TS_STANDARD):
            print('Type: ALTSEC')  # DEBUG
            self._parse_altsec(s, controlFlags)
        elif (controlFlags & ControlFlags.TS_SECONDARY):
            print('Type: SECONDARY')  # DEBUG
            self._parse_secondary(s, controlFlags)
        else:
            print('Type: PRIMARY')  # DEBUG
            self._parse_primary(s, controlFlags)

    # Primary drawing orders.
    # ----------------------------------------------------------------------
    def _parse_primary(self, s: BytesIO, flags: int):
        if flags & ControlFlags.TS_TYPE_CHANGE:
            orderType = Uint8.unpack(s)

        read_field_flags(s)  # TODO:

    def _parse_dstblt(self, s: BytesIO):
        """DSTBLT"""
        pass

    def _parse_patblt(self, s: BytesIO):
        """PATBLT"""
        pass

    def _parse_scrblt(self, s: BytesIO):
        """SCRBLT"""
        pass

    def _parse_draw_nine_grid(self, s: BytesIO):
        """DRAW_NINE_GRID"""
        pass

    def _parse_multi_draw_nine_grid(self, s: BytesIO):
        """MULTI_DRAW_NINE_GRID"""
        pass

    def _parse_line_to(self, s: BytesIO):
        """LINE_TO"""
        pass

    def _parse_opaque_rect(self, s: BytesIO):
        """OPAQUE_RECT"""
        pass

    def _parse_save_bitmap(self, s: BytesIO):
        """SAVE_BITMAP"""
        pass

    def _parse_memblt(self, s: BytesIO):
        """MEMBLT"""
        pass

    def _parse_mem3blt(self, s: BytesIO):
        """MEM3BLT"""
        pass

    def _parse_multi_dstblt(self, s: BytesIO):
        """MULTI_DSTBLT"""
        pass

    def _parse_multi_patblt(self, s: BytesIO):
        """MULTI_PATBLT"""
        pass

    def _parse_multi_scrblt(self, s: BytesIO):
        """MULTI_SCRBLT"""
        pass

    def _parse_multi_opaque_rect(self, s: BytesIO):
        """MULTI_OPAQUE_RECT"""
        pass

    def _parse_fast_index(self, s: BytesIO):
        """FAST_INDEX"""
        pass

    def _parse_polygon_sc(self, s: BytesIO):
        """POLYGON_SC"""
        pass

    def _parse_polygon_cb(self, s: BytesIO):
        """POLYGON_CB"""
        pass

    def _parse_polyline(self, s: BytesIO):
        """POLYLINE"""
        pass

    def _parse_fast_glyph(self, s: BytesIO):
        """FAST_GLYPH"""
        pass

    def _parse_ellipse_sc(self, s: BytesIO):
        """ELLIPSE_SC"""
        pass

    def _parse_ellipse_cb(self, s: BytesIO):
        """ELLIPSE_CB"""
        pass

    def _parse_glyph_index(self, s: BytesIO):
        """GLYPH_INDEX"""
        pass

    # Secondary drawing orders.
    # ----------------------------------------------------------------------
    def _parse_secondary(self, s: BytesIO, flags: int):
        orderLength = Uint16LE.unpack(s)
        extraFlags = Uint16LE.unpack(s)  # TODO: Need to pass these through as well.
        orderType = Uint8.unpack(s)
        # nxt = orderLength + 7

        assert orderType >= 0 and orderType < len(_sec)

        fp = _sec[orderType]
        print(f'Order: {_repr(fp)}')  # DEBUG
        fp(self, s, orderType, extraFlags)

    def _parse_cache_bitmap_v1(self, s: BytesIO, orderType: int, flags: int):
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

    def _parse_cache_color_table(self, s: BytesIO, orderType: int, flags: int):
        """CACHE_COLOR_TABLE"""
        cacheIndex = Uint8.unpack(s)
        numberColors = Uint16LE.unpack(s)

        assert numberColors == 256
        colors = [read_color(s) for _ in range(numberColors)]

    def _parse_cache_glyph(self, s: BytesIO, orderType: int, flags: int):
        """CACHE_GLYPH"""
        # 2.2.2.2.1.2.5
        # FIXME: Need to know from capabilities whether the server is sending V1 or V2 glyph caches.
        #        currently only V1 is implemented.
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

    def _parse_cache_bitmap_v2(self, s: BytesIO, orderType: int, flags: int):
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

    def _parse_cache_brush(self, s: BytesIO, orderType: int, flags: int):
        """CACHE_BRUSH"""
        # 2.2.2.2.1.2.7
        cacheIndex = Uint8.unpack(s)
        iBitmapFormat = Uint8.unpack(s)
        assert iBitmapFormat >= 0 and iBitmapFormat < len(BMF_BPP)

        bpp = BMF_BPP[iBitmapFormat]

        cx = Uint8.unpack(s)
        cy = Uint8.unpack(s)
        style = Uint8.unpack(s)
        iBytes = Uint8.unpack(s)

        compressed = False
        if cx == 8 and cy == 8 and bpp == 1:  # 8x8 mono bitmap
            data = s.read(8)[::-1]
        elif bpp == 8 and iBytes == 20:
            compressed = True
        elif bpp == 16 and iBytes == 24:
            compressed = True
        elif bpp == 24 and iBytes == 32:
            compressed = True

        if compressed:  # Move this to brush object?
            print('BRUSH DECOMPRESSION IS NOT IMPLEMENTED')  # DEBUG
            data = self.decompress_brush(s, bpp)
        else:
            data = bytes(256)  # Preallocate
            scanline = (bpp // 8) * 8
            for i in range(7):
                # TODO: Verify correctness
                print(scanline)  # DEBUG
                o = (7-i)*scanline
                data[o:o+8] = s.read(scanline)

    def _parse_cache_bitmap_v3(self, s: BytesIO, orderType: int, flags: int):
        """CACHE_BITMAP_V3"""
        cacheId = flags & 0x00000003
        flags = (flags & 0x0000FF80) >> 7
        bitsPerPixelId = (flags & 0x00000078) >> 3
        bpp = CBR23_BPP[bitsPerPixelId]

        cacheIndex = Uint16LE.unpack(s)
        key1 = Uint32LE.unpack(s)
        key2 = Uint32LE.unpack(s)

        s.read(2)  # Reserved (2 bytes)
        codecId = Uint8.unpack(s)
        width = Uint16LE.unpack(s)
        height = Uint16LE.unpack(s)
        dataLen = Uint32LE.unpack(s)

        data = s.read(dataLen)

    # Alternate secondary drawing orders.
    # ----------------------------------------------------------------------
    def _parse_altsec(self, s: BytesIO, flags: int):
        orderType = flags >> 2

        # TODO: Log unsupported orders.
        assert orderType >= 0 and orderType < len(_alt)

        fp = _alt[orderType]
        print(f'Order: {_repr(fp)}')  # DEBUG
        fp(self, s)

    def _parse_create_offscreen_bitmap(self, s: BytesIO):
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

    def _parse_switch_surface(self, s: BytesIO):
        """SWITCH_SURFACE"""
        surfaceId = Uint16LE.unpack(s)

    def _parse_create_nine_grid_bitmap(self, s: BytesIO):
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

    def _parse_stream_bitmap_first(self, s: BytesIO):
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

    def _parse_stream_bitmap_next(self, s: BytesIO):
        """STREAM_BITMAP_NEXT"""
        flags = Uint8.unpack(s)
        bitmapType = Uint16LE.unpack(s)
        blockSize = skip16(s)

    def _parse_gdiplus_first(self, s: BytesIO):
        """GDIPLUS_FIRST"""
        s.read(1)  # Padding
        cbSize = Uint16LE.unpack(s)  # TODO: Store cbSize
        cbTotalSize = Uint32LE.unpack(s)
        cbTotalEmfSize = Uint32LE.unpack(s)
        emf = s.read(cbSize)

    def _parse_gdiplus_next(self, s: BytesIO):
        """GDIPLUS_NEXT"""
        s.read(1)  # Padding
        emf = s.read(cbSize)  # TODO: Get cbSize from context

    def _parse_gdiplus_end(self, s: BytesIO):
        """GDIPLUS_END"""
        s.read(1)  # Padding
        cbSize = Uint16LE.unpack(s)
        cbTotalSize = Uint32LE.unpack(s)
        cbTotalEmfSize = Uint32LE.unpack(s)
        emf = s.read(cbSize)  # TODO: Get cbSize from context

    def _parse_gdiplus_cache_first(self, s: BytesIO):
        """GDIPLUS_CACHE_FIRST"""
        flags = Uint8.unpack(s)
        cacheType = Uint16LE.unpack(s)
        cacheIndex = Uint16LE.unpack(s)
        cbSize = Uint16LE.unpack(s)
        cbTotalSize = Uint32LE.unpack(s)
        emf = s.read(cbSize)

    def _parse_gdiplus_cache_next(self, s: BytesIO):
        """GDIPLUS_CACHE_NEXT"""
        flags = Uint8.unpack(s)
        cacheType = Uint16LE.unpack(s)
        cacheIndex = Uint16LE.unpack(s)
        emf = s.read(cbSize)

    def _parse_gdiplus_cache_end(self, s: BytesIO):
        """GDIPLUS_CACHE_END"""
        flags = Uint8.unpack(s)
        cacheType = Uint16LE.unpack(s)
        cacheIndex = Uint16LE.unpack(s)
        cbSize = Uint16LE.unpack(s)
        cbTotalSize = Uint32LE.unpack(s)
        emf = s.read(cbSize)

    def _parse_window(self, s: BytesIO):
        """WINDOW"""
        # This is specified in MS-RDPERP for seamless applications.
        LOG.debug('WINDOW is not supported yet.')

    def _parse_compdesk_first(self, s: BytesIO):
        """COMPDESK"""
        LOG.debug('COMPDESK is not supported yet.')

    def _parse_frame_marker(self, s: BytesIO):
        """FRAME_MARKER"""
        action = Uint32LE.unpack(s)

    def decompress_brush(self, s: BytesIO, bpp: int):
        pass


# Parser Lookup Tables
_pri = [
    OrdersParser._parse_dstblt,                # 0x00
    OrdersParser._parse_patblt,                # 0x01
    OrdersParser._parse_scrblt,                # 0x02
    None,                                      # 0x03
    None,                                      # 0x04
    None,                                      # 0x05
    None,                                      # 0x06
    OrdersParser._parse_draw_nine_grid,        # 0x07
    OrdersParser._parse_multi_draw_nine_grid,  # 0x08
    OrdersParser._parse_line_to,               # 0x09
    OrdersParser._parse_opaque_rect,           # 0x0A
    OrdersParser._parse_save_bitmap,           # 0x0B
    None,                                      # 0x0C
    OrdersParser._parse_memblt,                # 0x0D
    OrdersParser._parse_mem3blt,               # 0x0E
    OrdersParser._parse_multi_dstblt,          # 0x0F
    OrdersParser._parse_multi_patblt,          # 0x10
    OrdersParser._parse_multi_scrblt,          # 0x11
    OrdersParser._parse_multi_opaque_rect,     # 0x12
    OrdersParser._parse_fast_index,            # 0x13
    OrdersParser._parse_polygon_sc,            # 0x14
    OrdersParser._parse_polygon_cb,            # 0x15
    OrdersParser._parse_polyline,              # 0x16
    None,                                      # 0x17
    OrdersParser._parse_fast_glyph,            # 0x18
    OrdersParser._parse_ellipse_sc,            # 0x19
    OrdersParser._parse_ellipse_cb,            # 0x1A
    OrdersParser._parse_glyph_index,           # 0x1B
]

assert len(_pri) == 0x1C

_sec = [
    OrdersParser._parse_cache_bitmap_v1,    # 0x00 : Uncompressed
    OrdersParser._parse_cache_color_table,  # 0x01
    OrdersParser._parse_cache_bitmap_v1,    # 0x02 : Compressed
    OrdersParser._parse_cache_glyph,        # 0x03
    OrdersParser._parse_cache_bitmap_v2,    # 0x04 : Uncompresed
    OrdersParser._parse_cache_bitmap_v2,    # 0x05 : Compressed
    None,                                   # 0x06
    OrdersParser._parse_cache_brush,        # 0x07
    OrdersParser._parse_cache_bitmap_v3,    # 0x08
]

assert len(_sec) == 0x09

_alt = [
    OrdersParser._parse_switch_surface,           # 0x00
    OrdersParser._parse_create_offscreen_bitmap,  # 0x01
    OrdersParser._parse_stream_bitmap_first,      # 0x02
    OrdersParser._parse_stream_bitmap_next,       # 0x03
    OrdersParser._parse_create_nine_grid_bitmap,  # 0x04
    OrdersParser._parse_gdiplus_first,            # 0x05
    OrdersParser._parse_gdiplus_next,             # 0x06
    OrdersParser._parse_gdiplus_end,              # 0x07
    OrdersParser._parse_gdiplus_cache_first,      # 0x08
    OrdersParser._parse_gdiplus_cache_next,       # 0x09
    OrdersParser._parse_gdiplus_cache_end,        # 0x0A
    OrdersParser._parse_window,                   # 0x0B
    OrdersParser._parse_compdesk_first,           # 0x0C
    OrdersParser._parse_frame_marker,             # 0x0D
]

assert len(_alt) == 0x0E
