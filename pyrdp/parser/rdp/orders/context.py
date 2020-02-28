#
# This file is part of the PyRDP project.
# Copyright (C) 2019 GoSecure Inc.
# Licensed under the GPLv3 or later.
#
"""
Drawing Order Context.

"""

from .secondary import SecondaryContext as Secondary
from .primary import PrimaryContext as Primary
from .alternate import AlternateContext as Alternate


class GdiContext:
    """
    Keeps track of the internal drawing order state.

    This class is used by the OrdersParser to manage the state of the
    GDI stack and update it when messages are parsed.
    """

    def __init__(self):
        """Create a default GDI context."""
        self.secondary: Secondary = Secondary()
        self.primary: Primary = Primary()
        self.altsec: Alternate = Alternate()


class GdiContextObserver:
    """
    Interface for objects that monitor the GdiContext.

    This class provides abstract methods to be used by modules
    interested in listening and acting upon context updates.
    Its primary purpose is for the PyRDP player to render the
    remote desktop.

    NOTE: Unimplemented methods will act as No-Op.
    """
    # REFACTOR: Split into 3 separate observers?

    # Primary Handlers
    def dstBlt(self, state):
        pass

    def patBlt(self, state):
        pass

    def scrBlt(self, state):
        pass

    def drawNineGrid(self, state):
        pass

    def multiDrawNineGrid(self, state):
        pass

    def lineTo(self, state):
        pass

    def opaqueRect(self, state):
        pass

    def saveBitmap(self, state):
        pass

    def memblt(self, state):
        pass

    def mem3blt(self, state):
        pass

    def multiDstblt(self, state):
        pass

    def multiPatblt(self, state):
        pass

    def multiScrblt(self, state):
        pass

    def multiOpaqueRect(self, state):
        pass

    def fastIndex(self, state):
        pass

    def polygonSc(self, state):
        pass

    def polygonCb(self, state):
        pass

    def polyline(self, state):
        pass

    def fastGlyph(self, state):
        pass

    def ellipseSc(self, state):
        pass

    def ellipseCb(self, state):
        pass

    def glyphIndex(self, state):
        pass

    # Secondary Handlers
    def cacheBitmapV1(self, state):
        pass

    def cacheBitmapV2(self, state):
        pass

    def cacheBitmapV3(self, state):
        pass

    def cacheColorTable(self, state):
        pass

    def cacheGlyph(self, state):
        pass

    def cacheBrush(self, state):
        pass

    # Alternate Secondary Handlers
    def frameMarker(self, action: int):
        pass

    def createOffscreenBitmap(self, state):
        pass

    def switchSurface(self, state):
        pass

    def createNineGridBitmap(self, state):
        pass

    def streamBitmapFirst(self, state):
        pass

    def streamBitmapNext(self, state):
        pass

    def drawGdiPlusFirst(self, state):
        pass

    def drawGdiPlusNext(self, state):
        pass

    def drawGdiPlusEnd(self, state):
        pass

    def drawGdiPlusCacheFirst(self, state):
        pass

    def drawGdiPlusCacheNext(self, state):
        pass

    def drawGdiPlusCacheEnd(self, state):
        pass
