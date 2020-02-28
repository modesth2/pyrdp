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
    """
