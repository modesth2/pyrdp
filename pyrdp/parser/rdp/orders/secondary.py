"""
Constants and state for Secondary Drawing Orders.
"""

CBR2_BPP = [0, 0, 0, 8, 16, 24, 32]
BPP_CBR2 = [0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0,
            0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0]

CBR23_BPP = [0, 0, 0, 8, 16, 24, 32]
BPP_CBR23 = [0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0,
             0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0]

BMF_BPP = [0, 1, 0, 8, 16, 24, 32, 0]
BPP_BMF = [0, 1, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0,
           0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0]

CBR2_HEIGHT_SAME_AS_WIDTH = 0x01
CBR2_PERSISTENT_KEY_PRESENT = 0x02
CBR2_NO_BITMAP_COMPRESSION_HDR = 0x08
CBR2_DO_NOT_CACHE = 0x10


class SecondaryContext:
    """Secondary drawing order context."""
