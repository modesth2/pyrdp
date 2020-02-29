"""
Constants and state for Primary Drawing Orders.
"""
from io import BytesIO

from pyrdp.enum.orders import DrawingOrderControlFlags as ControlFlags
from pyrdp.core.packing import Uint8, Int8, Int16LE

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


class DstBlt:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'DstBlt':
        self = DstBlt()

        return self


class PatBlt:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'PatBlt':
        self = PatBlt()

        return self


class ScrBlt:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'ScrBlt':
        self = ScrBlt()

        return self


class DrawNineGrid:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'DrawNineGrid':
        self = DrawNineGrid()

        return self


class MultiDrawNineGrid:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'MultiDrawNineGrid':
        self = MultiDrawNineGrid()

        return self


class LineTo:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'LineTo':
        self = LineTo()

        return self


class OpaqueRect:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'OpaqueRect':
        self = OpaqueRect()

        return self


class SaveBitmap:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'SaveBitmap':
        self = SaveBitmap()

        return self


class MemBlt:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'MemBlt':
        self = MemBlt()

        return self


class Mem3Blt:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'Mem3Blt':
        self = Mem3Blt()

        return self


class MultiDstBlt:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'MultiDstBlt':
        self = MultiDstBlt()

        return self


class MultiPatBlt:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'MultiPatBlt':
        self = MultiPatBlt()

        return self


class MultiScrBlt:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'MultiScrBlt':
        self = MultiScrBlt()

        return self


class MultiOpaqueRect:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'MultiOpaqueRect':
        self = MultiOpaqueRect()

        return self


class FastIndex:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'FastIndex':
        self = FastIndex()

        return self


class PolygonSc:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'PolygonSc':
        self = PolygonSc()

        return self


class PolygonCb:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'PolygonCb':
        self = PolygonCb()

        return self


class PolyLine:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'PolyLine':
        self = PolyLine()

        return self


class FastGlyph:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'FastGlyph':
        self = FastGlyph()

        return self


class EllipseSc:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'EllipseSc':
        self = EllipseSc()

        return self


class EllipseCb:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'EllipseCb':
        self = EllipseCb()

        return self


class GlyphIndex:
    @staticmethod
    def parse(s: BytesIO, ctx: PrimaryContext) -> 'GlyphIndex':
        self = GlyphIndex()

        return self
