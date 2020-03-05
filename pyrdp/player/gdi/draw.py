#
# This file is part of the PyRDP project.
# Copyright (C) 2019 GoSecure Inc.
# Licensed under the GPLv3 or later.
#

import logging
from pyrdp.logging import LOGGER_NAMES

from pyrdp.parser.rdp.orders import GdiFrontend

from pyrdp.parser.rdp.orders.alternate import CreateOffscreenBitmap, SwitchSurface, CreateNineGridBitmap, \
    StreamBitmapFirst, StreamBitmapNext, GdiPlusFirst, GdiPlusNext, GdiPlusEnd, GdiPlusCacheFirst, \
    GdiPlusCacheNext, GdiPlusCacheEnd, FrameMarker

from .cache import BitmapCache
from .raster import rop3, rop2

from pyrdp.parser.rdp.orders.secondary import CacheBitmapV1, CacheBitmapV2, CacheBitmapV3, CacheColorTable, \
    CacheGlyph, CacheBrush

from pyrdp.parser.rdp.orders.primary import DstBlt, PatBlt, ScrBlt, DrawNineGrid, MultiDrawNineGrid, \
    LineTo, OpaqueRect, SaveBitmap, MemBlt, Mem3Blt, MultiDstBlt, MultiPatBlt, MultiScrBlt, MultiOpaqueRect, \
    FastIndex, PolygonSc, PolygonCb, PolyLine, FastGlyph, EllipseSc, EllipseCb, GlyphIndex

from pyrdp.ui import QRemoteDesktop, RDPBitmapToQtImage

from PySide2.QtGui import QImage, QPainter, QColor

LOG = logging.getLogger(LOGGER_NAMES.PLAYER + '.gdi')

SCREEN_BITMAP_SURFACE = 0xFFFF


class GdiQtFrontend(GdiFrontend):
    """
    A Qt Frontend for GDI drawing operations.

    This acts as a straight adapter from GDI to Qt as much as
    possible, but GDI specific operations that are not supported by Qt
    are implemented here.
    """

    def __init__(self, dc: QRemoteDesktop):
        self.dc = dc

        # Initialize cache.
        self.bitmaps = BitmapCache()

        # Surfaces and Offscreen bitmaps.
        self.surfaces = {SCREEN_BITMAP_SURFACE: QImage(dc.width(), dc.height(), QImage.Format_RGB32)}
        self.activeSurface = SCREEN_BITMAP_SURFACE

    @property
    def surface(self) -> QImage:
        return self.surfaces[self.activeSurface]

    def dstBlt(self, state: DstBlt):
        LOG.debug(state)

    def patBlt(self, state: PatBlt):
        LOG.debug(state)

    def scrBlt(self, state: ScrBlt):
        LOG.debug(state)
        # TODO: ROP3 operation
        prv = QImage.copy(self.surface)
        p = QPainter(self.surface)
        p.drawImage(state.nLeftRect, state.nTopRect, prv, state.nXSrc, state.nYSrc, state.nWidth, state.nHeight)

    def drawNineGrid(self, state: DrawNineGrid):
        LOG.debug(state)

    def multiDrawNineGrid(self, state: MultiDrawNineGrid):
        LOG.debug(state)

    def lineTo(self, state: LineTo):
        LOG.debug(state)

    def opaqueRect(self, state: OpaqueRect):
        LOG.debug(state)

    def saveBitmap(self, state: SaveBitmap):
        LOG.debug(state)

    def memBlt(self, state: MemBlt):
        LOG.debug(state)
        bmp = self.bitmaps.get(state.cacheId, state.cacheIndex)

        if bmp is None:
            return  # Ignore cache misses.

        # TODO: Check if NOHDR from general caps otherwise check COMPHDR
        img = RDPBitmapToQtImage(bmp.width, bmp.height,  bmp.bpp, True, bmp.data)

        p = QPainter(self.surface)

        ySrc = (bmp.height - state.height) - state.ySrc
        p.drawImage(state.left, state.top, img, state.xSrc, ySrc)

    def mem3Blt(self, state: Mem3Blt):
        LOG.debug(state)

    def multiDstBlt(self, state: MultiDstBlt):
        LOG.debug(state)

    def multiPatBlt(self, state: MultiPatBlt):
        LOG.debug(state)

    def multiScrBlt(self, state: MultiScrBlt):
        LOG.debug(state)

    def multiOpaqueRect(self, state: MultiOpaqueRect):
        LOG.debug(state)

    def fastIndex(self, state: FastIndex):
        LOG.debug(state)

    def polygonSc(self, state: PolygonSc):
        LOG.debug(state)

    def polygonCb(self, state: PolygonCb):
        LOG.debug(state)

    def polyLine(self, state: PolyLine):
        LOG.debug(state)

    def fastGlyph(self, state: FastGlyph):
        LOG.debug(state)

    def ellipseSc(self, state: EllipseSc):
        LOG.debug(state)

    def ellipseCb(self, state: EllipseCb):
        LOG.debug(state)

    def glyphIndex(self, state: GlyphIndex):
        LOG.debug(state)

    # Secondary Handlers
    def cacheBitmapV1(self, state: CacheBitmapV1):
        LOG.debug(state)
        self.bitmaps.add(state)

    def cacheBitmapV2(self, state: CacheBitmapV2):
        LOG.debug(state)
        self.bitmaps.add(state)

    def cacheBitmapV3(self, state: CacheBitmapV3):
        LOG.debug(state)
        self.bitmaps.add(state)

    def cacheColorTable(self, state: CacheColorTable):
        LOG.debug(state)

    def cacheGlyph(self, state: CacheGlyph):
        LOG.debug(state)

    def cacheBrush(self, state: CacheBrush):
        LOG.debug(state)

    # Alternate Secondary Handlers
    def frameMarker(self, state: FrameMarker):
        LOG.debug(state)
        if state.action == 0x01:  # END
            self.dc.notifyImage(0, 0, self.surface, self.dc.width(), self.dc.height())

    def createOffscreenBitmap(self, state: CreateOffscreenBitmap):
        LOG.debug(state)
        self.surfaces[state.id] = QImage(state.cx, state.cy, QImage.Format_RGB32)

        for d in state.delete:
            if d in self.surfaces:
                del self.surfaces[d]

    def switchSurface(self, state: SwitchSurface):
        LOG.debug(state)
        if state.id not in self.surfaces:
            LOG.warning('Request for uninitialized surface: %d', state.id)
            return
        self.activeSurface = state.id

    def createNineGridBitmap(self, state: CreateNineGridBitmap):
        LOG.debug(state)

    def streamBitmapFirst(self, state: StreamBitmapFirst):
        LOG.debug(state)

    def streamBitmapNext(self, state: StreamBitmapNext):
        LOG.debug(state)

    def drawGdiPlusFirst(self, state: GdiPlusFirst):
        LOG.debug(state)

    def drawGdiPlusNext(self, state: GdiPlusNext):
        LOG.debug(state)

    def drawGdiPlusEnd(self, state: GdiPlusEnd):
        LOG.debug(state)

    def drawGdiPlusCacheFirst(self, state: GdiPlusCacheFirst):
        LOG.debug(state)

    def drawGdiPlusCacheNext(self, state: GdiPlusCacheNext):
        LOG.debug(state)

    def drawGdiPlusCacheEnd(self, state: GdiPlusCacheEnd):
        LOG.debug(state)
