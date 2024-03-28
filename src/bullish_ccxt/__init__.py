import sys
import os
# So that this module can self add itself, when used by a file outside of the module
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from bullish import bullish
from abstract.bullish import ImplicitAPI

__all__ = ["bullish", "ImplicitAPI"]