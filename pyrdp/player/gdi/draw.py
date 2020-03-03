#
# This file is part of the PyRDP project.
# Copyright (C) 2019 GoSecure Inc.
# Licensed under the GPLv3 or later.
#

from pyrdp.parser.rdp.orders import GdiFrontend

from pyrdp.parser.rdp.orders.alternate import CreateOffscreenBitmap, SwitchSurface, CreateNineGridBitmap, \
    StreamBitmapFirst, StreamBitmapNext, GdiPlusFirst, GdiPlusNext, GdiPlusEnd, GdiPlusCacheFirst, \
    GdiPlusCacheNext, GdiPlusCacheEnd, FrameMarker

from pyrdp.parser.rdp.orders.secondary import CacheBitmapV1, CacheBitmapV2, CacheBitmapV3, CacheColorTable, \
    CacheGlyph, CacheBrush

from pyrdp.parser.rdp.orders.primary import DstBlt, PatBlt, ScrBlt, DrawNineGrid, MultiDrawNineGrid, \
    LineTo, OpaqueRect, SaveBitmap, MemBlt, Mem3Blt, MultiDstBlt, MultiPatBlt, MultiScrBlt, MultiOpaqueRect, \
    FastIndex, PolygonSc, PolygonCb, PolyLine, FastGlyph, EllipseSc, EllipseCb, GlyphIndex

from pyrdp.ui import QRemoteDesktop, RDPBitmapToQtImage

from PySide2.QtGui import QImage, QPainter, QColor


class GdiQtFrontend(GdiFrontend):
    """
    A Qt Frontend for GDI drawing operations.

    This acts as a straight adapter from GDI to Qt as much as
    possible, but GDI specific operations that are not supported by Qt
    are implemented here.
    """

    def __init__(self, dc: QRemoteDesktop):
        self.dc = dc
        self._surface = QImage(dc.width(), dc.height(), QImage.Format_RGB32)
        self._old = None

        # For now this is a rudimentary cache implementation.
        self.bmpCache = {}

    def dstBlt(self, state: DstBlt):
        print('dstBlt')

    def patBlt(self, state: PatBlt):
        print('patBlt')

    def scrBlt(self, state: ScrBlt):
        # TODO: ROP3 operation
        p = QPainter(self._surface)
        p.drawImage(state.nLeftRect, state.nTopRect, self._old, state.nXSrc, state.nYSrc, state.nWidth, state.nHeight)
        p.setBrush(QColor.fromRgb(0xff, 0, 0, 0x20))

    def drawNineGrid(self, state: DrawNineGrid):
        print('drawNineGrid')

    def multiDrawNineGrid(self, state: MultiDrawNineGrid):
        print('multiDrawNineGrid')

    def lineTo(self, state: LineTo):
        print('lineTo')

    def opaqueRect(self, state: OpaqueRect):
        print('opaqueRect')

    def saveBitmap(self, state: SaveBitmap):
        print('saveBitmap')

    def memBlt(self, state: MemBlt):
        cache = self.bmpCache[state.cacheId]
        bmp = cache[state.cacheIndex]

        # TODO: Check if NOHDR from general caps otherwise check COMPHDR
        img = RDPBitmapToQtImage(bmp.width, bmp.height,  bmp.bpp, True, bmp.data)

        p = QPainter(self._surface)

        ySrc = (bmp.height - state.height) - state.ySrc
        p.drawImage(state.left, state.top, img, state.xSrc, ySrc)

    def mem3Blt(self, state: Mem3Blt):
        print('mem3Blt')

    def multiDstBlt(self, state: MultiDstBlt):
        print('multiDstBlt')

    def multiPatBlt(self, state: MultiPatBlt):
        print('multiPatBlt')

    def multiScrBlt(self, state: MultiScrBlt):
        print('multiScrBlt')

    def multiOpaqueRect(self, state: MultiOpaqueRect):
        print('multiOpaqueRect')

    def fastIndex(self, state: FastIndex):
        print('fastIndex')

    def polygonSc(self, state: PolygonSc):
        print('polygonSc')

    def polygonCb(self, state: PolygonCb):
        print('polygonCb')

    def polyLine(self, state: PolyLine):
        print('polyLine')

    def fastGlyph(self, state: FastGlyph):
        print('fastGlyph')

    def ellipseSc(self, state: EllipseSc):
        print('ellipseSc')

    def ellipseCb(self, state: EllipseCb):
        print('ellipseCb')

    def glyphIndex(self, state: GlyphIndex):
        print('glyphIndex')

    # Secondary Handlers
    def cacheBitmapV1(self, state: CacheBitmapV1):
        print('cacheBitmapV1')

    def cacheBitmapV2(self, state: CacheBitmapV2):
        cid = state.cacheId
        idx = state.cacheIndex

        # Create cache if needed.
        if cid not in self.bmpCache:
            self.bmpCache[cid] = {}

        cache = self.bmpCache[cid]
        cache[idx] = state

    def cacheBitmapV3(self, state: CacheBitmapV3):
        print('cacheBitmapV3')

    def cacheColorTable(self, state: CacheColorTable):
        print('cacheColorTable')

    def cacheGlyph(self, state: CacheGlyph):
        print('cacheGlyph')

    def cacheBrush(self, state: CacheBrush):
        print('cacheBrush')

    # Alternate Secondary Handlers
    def frameMarker(self, state: FrameMarker):
        if state.action == 0x01:  # END
            self.dc.notifyImage(0, 0, self._surface, self.dc.width(), self.dc.height())
        else:  # BEGIN
            self._old = self._surface
            self._surface = self._old.copy()

    def createOffscreenBitmap(self, state: CreateOffscreenBitmap):
        print('createOffscreenBitmap')

    def switchSurface(self, state: SwitchSurface):
        print('switchSurface')

    def createNineGridBitmap(self, state: CreateNineGridBitmap):
        print('createNineGridBitmap')

    def streamBitmapFirst(self, state: StreamBitmapFirst):
        print('streamBitmapFirst')

    def streamBitmapNext(self, state: StreamBitmapNext):
        print('streamBitmapNext')

    def drawGdiPlusFirst(self, state: GdiPlusFirst):
        print('drawGdiPlusFirst')

    def drawGdiPlusNext(self, state: GdiPlusNext):
        print('drawGdiPlusNext')

    def drawGdiPlusEnd(self, state: GdiPlusEnd):
        print('drawGdiPlusEnd')

    def drawGdiPlusCacheFirst(self, state: GdiPlusCacheFirst):
        print('drawGdiPlusCacheFirst')

    def drawGdiPlusCacheNext(self, state: GdiPlusCacheNext):
        print('drawGdiPlusCacheNext')

    def drawGdiPlusCacheEnd(self, state: GdiPlusCacheEnd):
        print('drawGdiPlusCacheEnd')
