This class stores snapshots of images so users can undo and redo changes.
It uses two stacks:
- undo stack: previous states
- redo stack: states that were undone

Important detail:
We store COPY of the numpy array (img.copy()) so history states don't get
accidentally modified when the current image changes.
"""

from __future__ import annotations
from typing import List, Optional
import numpy as np


class HistoryManager:
    """
    A small utility class that manages Undo/Redo stacks.

    The stacks are private to protect them from accidental outside modifications.
    """
    def __init__(self, max_states: int = 25) -> None:
        """
        Args:
            max_states: Maximum number of undo states to keep in memory.
        """
        self.__undo_stack: List[np.ndarray] = []
        self.__redo_stack: List[np.ndarray] = []
        self.max_states = max_states

    def clear(self) -> None:
