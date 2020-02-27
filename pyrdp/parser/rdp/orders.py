#
# This file is part of the PyRDP project.
# Copyright (C) 2018 GoSecure Inc.
# Licensed under the GPLv3 or later.
#

import logging
from io import BytesIO

from pyrdp.core import Uint16LE, Uint8
from pyrdp.pdu.rdp.fastpath import FastPathOrdersEvent
from pyrdp.enum.rdp import DrawingOrderControlFlags, \
     AltSecDrawingOrder

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
        pass

    def parseAlternate(stream: BytesIO, flags: int):
        """
        Parse an alternate secondary drawing order.
        """
        orderType = flags >> 2
