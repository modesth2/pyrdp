"""
TS_FP_UPDATE_ORDERS parser.
"""
# flake8: noqa
#
# This file is part of the PyRDP project.
# Copyright (C) 2018 GoSecure Inc.
# Licensed under the GPLv3 or later.
#

import logging
from io import BytesIO

from pyrdp.core import Uint16LE, Uint8
from pyrdp.pdu.rdp.fastpath import FastPathOrdersEvent
from pyrdp.enum.rdp import DrawingOrderControlFlags

LOG = logging.getLogger('pyrdp.fastpath.parser')

class OrdersParser:
    """
    Parser responsible for TS_FP_UPDATE_ORDERS messages.
    """

    def __init__(self):
        self.orders = None

    # [REFACTOR] The parser should receive the context of the UPDATE message
    #            instead of a pre-built OrdersEvent.
    def parse(self, orders: FastPathOrdersEvent, stream: BytesIO) -> FastPathOrdersEvent:
        """
        Parse a TS_UPDATE_ORDERS message.
        """
        self.orders = orders
        self.orders.numberOrders = Uint16LE.unpack(stream)

        LOG.debug('Parsing TS_FP_UPDATE_ORDERS with %d orders', orders.numberOrders)

        for _ in range(orders.numberOrders):
            controlFlags = Uint8.unpack(stream)

            orderType = controlFlags & (DrawingOrderControlFlags.TS_SECONDARY |
                                        DrawingOrderControlFlags.TS_STANDARD)
            assert orderType != 0

            if orderType == DrawingOrderControlFlags.TS_STANDARD: 
                self.parsePrimary(controlFlags, stream)
            elif orderType == DrawingOrderControlFlags.TS_SECONDARY:
                self.parseAlternate(controlFlags, stream)
            else:
                self.parseSecondary(controlFlags, stream)

        return orders

    def write(self, orders: FastPathOrdersEvent, stream: BytesIO):
        """
        Serialize a TS_UPDATE_ORDERS message.
        """
        raise Exception('Repacking drawing orders is not supported yet!')

    def parsePrimary(stream: BytesIO, flags: int):
        """
        Parse a primary drawing order.
        """
        pass

    def parseSecondary(stream: BytesIO, flags: int):
        """
        Parse a secondary drawing order.
        """
        # stream = BytesIO(orderData)
        # controlFlags = Uint8.unpack(stream.read(1))  # Is the same byte? Looks like it.
        # orderLength = Uint16LE.unpack(stream.read(2)) + 13  # See Spec.
        # LOG.debug('   %d/%d' % (orderLength, size))
        # extraFlags = Uint16LE.unpack(stream.read(2))
        # orderType = Uint8.unpack(stream.read(1))
        # stream.read(orderLength)  # Skip the order length for now.
        # ordersEvent.secondaryDrawingOrders = SecondaryDrawingOrder(controlFlags, orderLength, extraFlags, orderType)
        pass

    def parseAlternate(stream: BytesIO, flags: int):
        """
        Parse an alternate secondary drawing order.

        const char* orders[] = {
            "[0x%02" PRIx8 "] Switch Surface",         "[0x%02" PRIx8 "] Create Offscreen Bitmap",
            "[0x%02" PRIx8 "] Stream Bitmap First",    "[0x%02" PRIx8 "] Stream Bitmap Next",
            "[0x%02" PRIx8 "] Create NineGrid Bitmap", "[0x%02" PRIx8 "] Draw GDI+ First",
            "[0x%02" PRIx8 "] Draw GDI+ Next",         "[0x%02" PRIx8 "] Draw GDI+ End",
            "[0x%02" PRIx8 "] Draw GDI+ Cache First",  "[0x%02" PRIx8 "] Draw GDI+ Cache Next",
            "[0x%02" PRIx8 "] Draw GDI+ Cache End",    "[0x%02" PRIx8 "] Windowing",
            "[0x%02" PRIx8 "] Desktop Composition",    "[0x%02" PRIx8 "] Frame Marker"
        };
        """
        orderType = flags >> 2
        pass
