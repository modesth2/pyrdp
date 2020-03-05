#
# This file is part of the PyRDP project.
# Copyright (C) 2019 GoSecure Inc.
# Licensed under the GPLv3 or later.
#

"""
GDI Cache Management Layer.
"""

from pyrdp.parser.rdp.orders.secondary import CacheBitmap


class BitmapCache:
    """
    Keeps track of bitmaps.
    """

    def __init__(self, persist=False):
        self.caches = {}
        self.persist = persist
        if persist:
            raise Exception('Persistent cache is not supported yet.')

    def has(self, cid: int, idx: int) -> bool:
        """
        Check whether a cache contains an entry.

        :param cid: The cache id to use.
        :param idx: The cache entry index.

        :returns: True if (cid:idx) is in the cache, false otherwise.
        """
        if cid not in self.caches:
            return False
        cache = self.caches[cid]
        return idx in cache

    def get(self, cid: int, idx: int) -> CacheBitmap:
        """
        Retrieve an entry from the cache.

        :param cid: The cache id to use.
        :param idx: The cache entry index.

        :returns: The cache entry or None if it does not exist.
        """
        if cid not in self.caches:
            return None
        cache = self.caches[cid]
        if idx not in cache:
            return None
        return cache[idx]

    def add(self, entry: CacheBitmap) -> bool:
        """
        Add an entry to the cache.

        :returns: True if the entry is a fresh entry, False if it replaced an existing one.
        """
        cid = entry.cacheId
        idx = entry.cacheIndex
        if cid not in self.caches:
            self.caches[cid] = {}
        cache = self.caches[cid]
        cache[idx] = entry

    def evict(self, cid: int, idx: int) -> bool:
        """
        Evict an entry from the cache.

        :param cid: The cache id to use.
        :param idx: The cache entry index.

        :returns: True if an entry was evicted, false otherwise.
        """
        if not self.has(cid, idx):
            return False
        del self.caches[cid][idx]
