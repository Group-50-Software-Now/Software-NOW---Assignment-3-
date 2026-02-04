"""
image_processor.py

All image processing lives here (OpenCV).

The GUI should not contain OpenCV logic directly — it should call this class instead.
That keeps the code clean and stops the GUI file from becoming messy.

This class supports:
- Grayscale
- Blur (Gaussian)
- Edge detection (Canny)
- Brightness adjustment
- Contrast adjustment
- Rotation (90, 180, 270)
- Flip (horizontal/vertical)
- Resize/scale by percentage
"""

from __future__ import annotations
from typing import Tuple
import cv2
import numpy as np


class ImageProcessor:
   """
    Image processing helper using OpenCV.

    The application stores images in OpenCV's default format:
    - numpy array
    - BGR channel order

    When displaying in Tkinter, we convert BGR -> RGB.
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
               
