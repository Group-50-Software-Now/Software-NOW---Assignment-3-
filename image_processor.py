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

#  Required filters 

    def to_grayscale(self, img: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale.

        We convert back to BGR at the end so the rest of the app
        can always assume a 3-channel image.
        """
        self.last_action = "Grayscale"
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    def blur(self, img: np.ndarray, intensity: int) -> np.ndarray:
        """
        Apply Gaussian blur.

        intensity is used as a kernel size (must be odd and >= 1).
        """
        self.last_action = f"Blur ({intensity})"
        if intensity <= 0:
            return img.copy()

        # Kernel must be odd; if user gives even, shift it up by 1.
        k = max(1, int(intensity))
        if k % 2 == 0:
            k += 1

        return cv2.GaussianBlur(img, (k, k), 0)

    def edges(self, img: np.ndarray, low: int = None, high: int = None) -> np.ndarray:

 """
        Adjust brightness.

        A value range of about -100..100 is usually usable.
        """
        self.last_action = f"Brightness ({value})"
        return cv2.convertScaleAbs(img, alpha=1.0, beta=int(value))

    def adjust_contrast(self, img: np.ndarray, value: int) -> np.ndarray:
        """
        Adjust contrast.

        value is in range 0..200 where:
        - 100 means normal contrast
        - <100 reduces contrast (flatter)
        - >100 increases contrast (stronger)
        """
        self.last_action = f"Contrast ({value})"
        alpha = max(0.0, float(value) / 100.0)
        return cv2.convertScaleAbs(img, alpha=alpha, beta=0)

    def rotate(self, img: np.ndarray, angle: int) -> np.ndarray:

 """Rotate image by 90, 180, or 270 degrees."""
        self.last_action = f"Rotate ({angle})"
        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        if angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        if angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return img.copy()

    def flip(self, img: np.ndarray, mode: str) -> np.ndarray:
        """Flip image: mode is 'horizontal' or 'vertical'."""
        self.last_action = f"Flip ({mode})"
        if mode == "horizontal":
            return cv2.flip(img, 1)
        if mode == "vertical":
            return cv2.flip(img, 0)
        return img.copy()
       
 def resize_scale(self, img: np.ndarray, percent: int) -> np.ndarray:
        """Resize image by percentage (10..200 recommended)."""
        percent = int(percent)
        percent = max(10, min(200, percent))
        self.last_action = f"Resize ({percent}%)"

        h, w = img.shape[:2]
        new_w = max(1, int(w * (percent / 100.0)))
        new_h = max(1, int(h * (percent / 100.0)))

        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
