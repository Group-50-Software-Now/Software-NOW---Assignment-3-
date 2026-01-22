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
        """Clear all history (useful when opening a new image)."""
        self.__undo_stack.clear()
        self.__redo_stack.clear()

    def push(self, img: np.ndarray) -> None:
        """
        Save the current image state into undo history.

        Note:
        - whenever a new change happens, redo history becomes invalid and is cleared.
        """
        if img is None:
            return

        self.__undo_stack.append(img.copy())
        self.__redo_stack.clear()

        # Keep memory under control
        if len(self.__undo_stack) > self.max_states:
            self.__undo_stack.pop(0)

    def can_undo(self) -> bool:
        """Return True if undo is possible."""
        return len(self.__undo_stack) > 0

    def can_redo(self) -> bool:
        """Return True if redo is possible."""
        return len(self.__redo_stack) > 0

    def undo(self, current: np.ndarray) -> Optional[np.ndarray]:
        """
        Undo one step.

        Returns:
            Previous image if available, else None.
        """
        if not self.can_undo() or current is None:
            return None

        self.__redo_stack.append(current.copy())
        return self.__undo_stack.pop()

    def redo(self, current: np.ndarray) -> Optional[np.ndarray]:
        """
        Redo one step.

        Returns:
            Next image if available, else None.
        """
        if not self.can_redo() or current is None:
            return None

        self.__undo_stack.append(current.copy())
        return self.__redo_stack.pop()
