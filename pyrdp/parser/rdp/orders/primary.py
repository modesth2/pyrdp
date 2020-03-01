"""
Constants and state for Primary Drawing Orders.
"""
from io import BytesIO

from pyrdp.enum.orders import DrawingOrderControlFlags as ControlFlags
from pyrdp.core.packing import Uint8, Int8, Int16LE, Uint16LE

# This follows the PrimaryDrawOrderType enum
ORDERTYPE_FIELDBYTES = [1, 2, 1, 0, 0, 0, 0, 1, 1, 2, 1, 1, 0, 2, 3, 1, 2, 2, 2, 2, 1, 2, 1, 0, 2, 1, 2, 3]

BOUND_LEFT = 0x01
BOUND_TOP = 0x02
BOUND_RIGHT = 0x04
BOUND_BOTTOM = 0x08
BOUND_DELTA_LEFT = 0x10
BOUND_DELTA_TOP = 0x20
BOUND_DELTA_RIGHT = 0x40
BOUND_DELTA_BOTTOM = 0x80


def read_field_flags(s: BytesIO, flags: int, orderType: int) -> int:
    """Reads encoded field flags."""

    # REFACTOR: This could be internal to the context class.
    assert orderType >= 0 and orderType < len(ORDERTYPE_FIELDBYTES)

    fieldBytes = ORDERTYPE_FIELDBYTES[orderType]
    assert fieldBytes != 0  # Should be a valid orderType

    if flags & ControlFlags.TS_ZERO_FIELD_BYTE_BIT0:
        fieldBytes -= 1

    if flags & ControlFlags.TS_ZERO_FIELD_BYTE_BIT1:
        if fieldBytes > 1:
            fieldBytes -= 2
        else:
            fieldBytes = 0

    fieldFlags = 0
    for i in range(fieldBytes):
        fieldFlags |= Uint8.unpack(s) << (i * 8)

    return fieldFlags


def read_coord(s: BytesIO, delta: bool, prev: int):
    if delta:
        return prev + Int8.unpack(s)
    else:
        return Int16LE.unpack(s)


class Bounds:
    """A bounding rectangle."""
    def __init__(self):
        self.left = 0
        self.top = 0
        self.bottom = 0
        self.right = 0

    def update(self, s: BytesIO):
        flags = Uint8.unpack(s)

        if flags & BOUND_LEFT:
            self.left = Int16LE.unpack(s)
        elif flags & BOUND_DELTA_LEFT:
            self.left += Int8.unpack(s)

        if flags & BOUND_TOP:
            self.top = Int16LE.unpack(s)
        elif flags & BOUND_DELTA_TOP:
            self.top += Int8.unpack(s)

        if flags & BOUND_RIGHT:
            self.right = Int16LE.unpack(s)
        elif flags & BOUND_DELTA_RIGHT:
            self.right += Int8.unpack(s)

        if flags & BOUND_BOTTOM:
            self.bottom = Int16LE.unpack(s)
        elif flags & BOUND_DELTA_BOTTOM:
            self.bottom += Int8.unpack(s)


class PrimaryContext:
    """Primary drawing order context."""

    def __init__(self):
        # The field flags for the current order.
        self.fieldFlags: int = 0

        # Whether coordinates are being sent as a delta.
        self.deltaCoords: bool = False

        # A cache of the previous order type received.
        self.orderType: int = None

        # The configured bounding rectangle
        self.bounds: Bounds = Bounds()

        # Whether the current draw order is bounded by a rectangle..
        self.bounded: bool = False

        # Track state for each drawing order.
        self.dstBlt = DstBlt(self)
        self.patBlt = PatBlt(self)
        self.scrBlt = ScrBlt(self)
        self.drawNineGrid = DrawNineGrid(self)
        self.multiDrawNineGrid = MultiDrawNineGrid(self)
        self.lineTo = LineTo(self)
        self.opaqueRect = OpaqueRect(self)
        self.saveBitmap = SaveBitmap(self)
        self.memBlt = MemBlt(self)
        self.mem3Blt = Mem3Blt(self)
        self.multiDstBlt = MultiDstBlt(self)
        self.multiPatBlt = MultiPatBlt(self)
        self.multiScrBlt = MultiScrBlt(self)
        self.multiOpaqueRect = MultiOpaqueRect(self)
        self.fastIndex = FastIndex(self)
        self.polygonSc = PolygonSc(self)
        self.polygonCb = PolygonCb(self)
        self.polyLine = PolyLine(self)
        self.fastGlyph = FastGlyph(self)
        self.ellipseSc = EllipseSc(self)
        self.ellipseCb = EllipseCb(self)
        self.glyphIndex = GlyphIndex(self)

    def update(self, s: BytesIO, flags: int):
        """
        Update the context when parsing a new primary order.

        This method should be called at the beginning of every new
        primary order to process contextual changes.

        :param s BytesIO: The raw byte stream
        :param flags int: The controlFlags received in the UPDATE PDU.

        :return: The orderType to act upon.
        """

        if flags & ControlFlags.TS_TYPE_CHANGE:
            self.orderType = Uint8.unpack(s)
        assert self.orderType

        self.fieldFlags = read_field_flags(s, flags, self.orderType)

        # Process bounding rectangle updates
        if flags & ControlFlags.TS_BOUNDS:
            self.bounded = True
            if not flags & ControlFlags.TS_ZERO_BOUNDS_DELTAS:
                self.bounds.update(s)
        else:
            self.bounded = False

        self.deltaCoords = flags & ControlFlags.TS_DELTA_COORDS != 0

        return self.orderType

    def field(self, n: int):
        return self.fieldFlags & (1 << (n - 1))


class DstBlt:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx
        self.nLeftRect = 0
        self.nTopRect = 0
        self.nWidth = 0
        self.nHeight = 0
        self.rop = 0

    def update(self, s: BytesIO):

        if self.ctx.field(1):
            self.nLeftRect = read_coord(s, self.ctx.deltaCoords, self.nLeftRect)
        if self.ctx.field(2):
            self.nTopRect = read_coord(s, self.ctx.deltaCoords, self.nTopRect)
        if self.ctx.field(3):
            self.nWidth = read_coord(s, self.ctx.deltaCoords, self.nWidth)
        if self.ctx.field(4):
            self.nHeight = read_coord(s, self.ctx.deltaCoords, self.nHeight)
        if self.ctx.field(5):
            self.rop = Uint8.unpack(s)

        return self


class PatBlt:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class ScrBlt:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class DrawNineGrid:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class MultiDrawNineGrid:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class LineTo:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class OpaqueRect:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class SaveBitmap:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class MemBlt:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx
        self.leftRect = self.topRect = self.width = self.height = 0
        self.x = self.y = 0
        self.cacheIndex = 0
        self.cacheId = 0
        self.colorIndex = 0

    def update(self, s: BytesIO) -> 'MemBlt':
        ctx = self.ctx

        # How to make this nice?
        if ctx.field(1): self.cacheId = Uint16LE.unpack(s)  # NOQA
        if ctx.field(2):
            self.leftRect = read_coord(s, ctx.deltaCoords, self.leftRect)
        if ctx.field(3):
            self.topRect = read_coord(s, ctx.deltaCoords, self.topRect)
        if ctx.field(4):
            self.width = read_coord(s, ctx.deltaCoords, self.width)
        if ctx.field(5):
            self.height = read_coord(s, ctx.deltaCoords, self.leftRect)
        if ctx.field(6):
            self.rop = Uint8.unpack(s)
        if ctx.field(7):
            self.x = read_coord(s, ctx.deltaCoords, self.x)
        if ctx.field(8):
            self.y = read_coord(s, ctx.deltaCoords, self.y)
        if ctx.field(9):
            self.cacheIndex = Uint16LE.unpack(s)

        self.colorIndex = self.cacheId >> 8
        self.cacheId = self.cacheId & 0xFF

        return self


class Mem3Blt:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class MultiDstBlt:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class MultiPatBlt:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class MultiScrBlt:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class MultiOpaqueRect:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class FastIndex:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class PolygonSc:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class PolygonCb:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class PolyLine:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class FastGlyph:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class EllipseSc:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class EllipseCb:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self


class GlyphIndex:
    def __init__(self, ctx: PrimaryContext):
        self.ctx = ctx

    def update(self, s: BytesIO):

        return self
