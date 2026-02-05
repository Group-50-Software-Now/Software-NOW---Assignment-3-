"""
history_manager.py

Undo/Redo system for the image editor.

Why this file exists:
- Undo/Redo is a separate concern from GUI and image processing
- Keeping it isolated makes the code easier to test and maintain

Design:
- We store *copies* of images (numpy arrays)
- Undo stack keeps the “past”
- Redo stack keeps the “future” after undo
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np


@dataclass
class HistoryManager:
    """
    Manages Undo/Redo states.

    This class is deliberately small but robust:
    - push(image) saves a snapshot for Undo
    - undo(current) returns the previous snapshot
    - redo(current) returns the next snapshot

    Notes:
    - We always store copies so later edits don't modify old history states.
    - max_states prevents memory blow-ups if the user edits a lot.
    """
    max_states: int = 25
    _undo_stack: List[np.ndarray] = field(default_factory=list)
    _redo_stack: List[np.ndarray] = field(default_factory=list)

    # --------- "nice-to-have" OOP extras (clean but not overkill) ---------

    def __len__(self) -> int:
        """Total number of stored states (undo + redo)."""
        return len(self._undo_stack) + len(self._redo_stack)

    @property
    def undo_count(self) -> int:
        """How many undo steps are available."""
        return len(self._undo_stack)

    @property
    def redo_count(self) -> int:
        """How many redo steps are available."""
        return len(self._redo_stack)
    # ---------------- Core API used by the GUI ----------------

    def clear(self) -> None:
        """Remove all saved states (usually called when opening a new image)."""
        self._undo_stack.clear()
        self._redo_stack.clear()

    def can_undo(self) -> bool:
        """True if Undo is currently possible."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """True if Redo is currently possible."""
        return len(self._redo_stack) > 0

    def push(self, img: np.ndarray) -> None:
        """
        Save a snapshot of the current image into undo history.

        Important:
        - Whenever we push a new edit, redo history becomes invalid,
          because redo only makes sense after an undo.
        """
        self._undo_stack.append(img.copy())
        self._redo_stack.clear()

        # Keep memory usage controlled
        if len(self._undo_stack) > self.max_states:
            self._undo_stack.pop(0)

    def undo(self, current_img: np.ndarray) -> Optional[np.ndarray]:
        """
        Undo one step.

        We move:
        - current image -> redo stack
        - last undo state -> returned to the caller

        Returns:
            The previous image state, or None if nothing to undo.
        """
        if not self.can_undo():
            return None
        

        self._redo_stack.append(current_img.copy())
        return self._undo_stack.pop()

    def redo(self, current_img: np.ndarray) -> Optional[np.ndarray]:
        """
        Redo one step.

        We move:
        - current image -> undo stack
        - last redo state -> returned to the caller
        
        Returns:
            The next image state, or None if nothing to redo.
        """
        if not self.can_redo():
            return None

        self._undo_stack.append(current_img.copy())
        return self._redo_stack.pop()


