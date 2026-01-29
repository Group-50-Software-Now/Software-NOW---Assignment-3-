"""
image_processor.py

This module contains all image processing logic for the application.
It acts as a dedicated processing layer between the GUI (Tkinter)
and the OpenCV library.

The GUI should never directly call OpenCV functions.
Instead, it communicates with this class, which keeps the code clean,
modular, and easy to maintain.

Supported image operations:
- Grayscale conversion
- Gaussian blur
- Edge detection (Canny)
- Brightness adjustment
- Contrast adjustment
- Rotation (90°, 180°, 270°)
- Flip (horizontal / vertical)
- Resize / scale by percentage
"""

from __future__ import annotations
from typing import Tuple
import cv2
import numpy as np


class ImageProcessor:
    """
    Image processing helper class using OpenCV.

    Images are stored internally as:
    - NumPy arrays
    - BGR colour format (OpenCV default)

    When images are displayed in Tkinter,
    they are converted to RGB in the GUI layer.
    """

    # Default threshold values used for Canny edge detection
    DEFAULT_CANNY: Tuple[int, int] = (80, 160)

    def __init__(self) -> None:
        """
        Constructor.

        The last_action attribute is useful for debugging
        or for displaying status messages in the GUI.
        """
        self.last_action: str = "Ready"

    
    # File Input / Output
    

    def read_image(self, path: str) -> np.ndarray:
        """
        Read an image from disk using OpenCV.

        Args:
            path: Full file path to the image.

        Returns:
            Image as a NumPy array in BGR format.

        Raises:
            ValueError: If the image cannot be loaded.
        """
          img = cv2.imread(path)

        
        # If OpenCV fails to read the image, img will be None
        if img is None:
            raise ValueError(
                "OpenCV could not read this image. "
                "The file may be unsupported or corrupted."
            )

        self.last_action = "Opened image"
        return img

    def write_image(self, path: str, img: np.ndarray) -> None:
        """
        Save an image to disk using OpenCV.

        Args:
            path: Destination file path.
            img: Image data in BGR format.

        Raises:
            ValueError: If saving fails.
        """
        ok = cv2.imwrite(path, img)

        # cv2.imwrite returns False if saving fails
        if not ok:
            raise ValueError(
                "OpenCV could not save the image. "
               
