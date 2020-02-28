"""
Constants and state for Primary Drawing Orders.
"""
from io import BytesIO

from pyrdp.enum.orders import DrawingOrderControlFlags as ControlFlags
from pyrdp.core.packing import Uint8, Int8, Int16LE

# Lookup table for number of field bytes per order type

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

        # Whether the current draw order is bound.
        self.useBounds: bool = False

    def update(self, s: BytesIO, flags: int):
        """
        Update the context when parsing a new primary order.

        This method should be called at the beginning of every new
        primary order to read contextual updates.

        :param s BytesIO: The raw byte stream
        :param flags int: The controlFlags received in the UPDATE PDU.

        :return: The orderType to act upon.
        """

        if flags & ControlFlags.TS_TYPE_CHANGE:
            self.orderType = Uint8.unpack(s)
        assert self.orderType

        self.fieldFlags = read_field_flags(s, flags, self.orderType)

        if flags & ControlFlags.TS_BOUNDS:
            if not flags & ControlFlags.TS_ZERO_BOUNDS_DELTAS:
                self.bounds.update(s)

        self.deltaCoords = flags & ControlFlags.TS_DELTA_COORDS != 0

        return self.orderType
