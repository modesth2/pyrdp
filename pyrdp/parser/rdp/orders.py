#
# This file is part of the PyRDP project.
# Copyright (C) 2018 GoSecure Inc.
# Licensed under the GPLv3 or later.
#

import logging
from io import BytesIO

from pyrdp.core import Uint16LE, Uint8
from pyrdp.pdu.rdp.fastpath import FastPathOrdersEvent
# from pyrdp.enum.rdp import DrawingOrderControlFlags, \
#      AltSecDrawingOrder

LOG = logging.getLogger('pyrdp.fastpath.parser')

# REFACTOR: Pull all of this into pyrdp.enum ---------------------------------------------------
TS_STANDARD = 0x1
TS_SECONDARY = 0x2


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

    @staticmethod
    def toString(n: 'Primary'):
        """
        TODO: Do some hacky magic with OrderParser handlers and docstrings?
        """
        return 'TODO'


class Secondary:
    BITMAP_UNCOMPRESSED = 0x00
    CACHE_COLOR_TABLE = 0x01
    CACHE_BITMAP_COMPRESSED = 0x02
    CACHE_GLYPH = 0x03
    BITMAP_UNCOMPRESSED_V2 = 0x04
    BITMAP_COMPRESSED_V2 = 0x05
    CACHE_BRUSH = 0x07
    BITMAP_COMPRESSED_V3 = 0x08

    @staticmethod
    def toString(n: 'Secondary'):
        return 'TODO'


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

    @staticmethod
    def toString(n: 'Secondary'):
        return 'TODO'
# ------------------------------------------------------------------------------ [/REFACTOR]


class OrdersParser:
    """
    Drawing Order Parser.
    """

    def __init__(self):
        # TODO: Create GDI state here.
        self.orders: FastPathOrdersEvent = None
        pass

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
            self.parse_altsec(s, controlFlags)
        elif (controlFlags & TS_SECONDARY):
            self.parse_secondary(s, controlFlags)
        else:
            self.parse_primary(s, controlFlags)

    # Primary drawing orders.
    # ----------------------------------------------------------------------
    def parse_primary(self, s: BytesIO, flags: int):
        pass

    def parse_dstblt(self, s: BytesIO):
        pass

    def parse_patblt(self, s: BytesIO):
        pass

    def parse_scrblt(self, s: BytesIO):
        pass

    def parse_draw_nine_grid(self, s: BytesIO):
        pass

    def parse_multi_draw_nine_grid(self, s: BytesIO):
        pass

    def parse_line_to(self, s: BytesIO):
        pass

    def parse_opaque_rect(self, s: BytesIO):
        pass

    def parse_save_bitmap(self, s: BytesIO):
        pass

    def parse_memblt(self, s: BytesIO):
        pass

    def parse_mem3blt(self, s: BytesIO):
        pass

    def parse_multi_dstblt(self, s: BytesIO):
        pass

    def parse_multi_patblt(self, s: BytesIO):
        pass

    def parse_multi_scrblt(self, s: BytesIO):
        pass

    def parse_multi_opaque_rect(self, s: BytesIO):
        pass

    def parse_fast_index(self, s: BytesIO):
        pass

    def parse_polygon_sc(self, s: BytesIO):
        pass

    def parse_polygon_cb(self, s: BytesIO):
        pass

    def parse_polyline(self, s: BytesIO):
        pass

    def parse_fast_glyph(self, s: BytesIO):
        pass

    def parse_ellipse_sc(self, s: BytesIO):
        pass

    def parse_ellipse_cb(self, s: BytesIO):
        pass

    def parse_glyph_index(self, s: BytesIO):
        pass

    # Seocndary drawing orders.
    # ----------------------------------------------------------------------
    def parse_secondary(self, s: BytesIO, flags: int):
        pass

    def parse_cache_bitmap_v1(self, s: BytesIO, orderType: int):
        pass

    def parse_cache_color_table(self, s: BytesIO, orderType: int):
        pass

    def parse_cache_glyph(self, s: BytesIO, orderType: int):
        pass

    def parse_cache_bitmap_v2(self, s: BytesIO, orderType: int):
        pass

    def parse_cache_brush(self, s: BytesIO, orderType: int):
        pass

    def parse_cache_bitmap_v3(self, s: BytesIO, orderType: int):
        pass

    # Alternate secondary drawing orders.
    # ----------------------------------------------------------------------
    def parse_altsec(self, s: BytesIO, flags: int):
        pass

    def parse_create_offscreen_bitmap(self, s: BytesIO):
        pass

    def parse_switch_surface(self, s: BytesIO):
        pass

    def parse_create_nine_grid_bitmap(self, s: BytesIO):
        pass

    def parse_stream_bitmap_first(self, s: BytesIO):
        pass

    def parse_stream_bitmap_next(self, s: BytesIO):
        pass

    def parse_gdiplus_first(self, s: BytesIO):
        pass

    def parse_gdiplus_next(self, s: BytesIO):
        pass

    def parse_gdiplus_end(self, s: BytesIO):
        pass

    def parse_gdiplus_cache_first(self, s: BytesIO):
        pass

    def parse_gdiplus_cache_next(self, s: BytesIO):
        pass

    def parse_gdiplus_cache_end(self, s: BytesIO):
        pass

    def parse_window(self, s: BytesIO):
        # This is specified in MS-RDPERP for seamless applications.
        LOG.debug('WINDOW is not supported yet.')

    def parse_compdesk_first(self, s: BytesIO):
        LOG.debug('COMPDESK is not supported yet.')

    def parse_frame_marker(self, s: BytesIO):
        pass


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
