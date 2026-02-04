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
        # Keeping a "last action" string is useful for a status bar / debugging.
        self.last_action: str = "Ready"

    # File I/O

    def read_image(self, path: str) -> np.ndarray:
        """
        Read an image from disk using OpenCV (BGR).

        Raises:
            ValueError if OpenCV cannot read the image.
        """
        img = cv2.imread(path)
        if img is None:
            raise ValueError("OpenCV could not read this image. File may be unsupported or corrupted.")
        self.last_action = "Opened image"
        return img


     def write_image(self, path: str, img: np.ndarray) -> None:
        """
        Save an image to disk using OpenCV.

        Raises:
            ValueError if OpenCV fails to write the image.
        """
        ok = cv2.imwrite(path, img)
        if not ok:
            raise ValueError("OpenCV could not save the image. Check the path and permissions.")
        self.last_action = "Saved image"

    # Display helpers 

    @staticmethod
    def bgr_to_rgb(img: np.ndarray) -> np.ndarray:
        """
        Convert BGR (OpenCV) to RGB (PIL/Tkinter).

        We do this only for display.
        We keep internal images in BGR so OpenCV operations remain consistent.
        """
        return img[:, :, ::-1]
