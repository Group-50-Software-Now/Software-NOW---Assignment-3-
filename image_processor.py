

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

    # -------------------------------------------------
    # File Input / Output
    # -------------------------------------------------

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
                "Check file path and permissions."
            )

        self.last_action = "Saved image"

    # -------------------------------------------------
    # Display Helpers
    # -------------------------------------------------

    @staticmethod
    def bgr_to_rgb(img: np.ndarray) -> np.ndarray:
        """
        Convert a BGR image (OpenCV format) to RGB format.

        This conversion is required because:
        - OpenCV uses BGR
        - PIL / Tkinter expect RGB
        """
        return img[:, :, ::-1]

    # -------------------------------------------------
    # Image Filters and Transformations
    # -------------------------------------------------

    def to_grayscale(self, img: np.ndarray) -> np.ndarray:
        """
        Convert an image to grayscale.

        The output is converted back to BGR so that
        the rest of the application can continue
        treating images consistently.
        """
        self.last_action = "Grayscale"

        # Convert to grayscale (single channel)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Convert back to BGR so GUI code remains uniform
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    def blur(self, img: np.ndarray, intensity: int) -> np.ndarray:
        """
        Apply Gaussian blur to the image.

        Args:
            intensity: Blur strength (kernel size).
                       Must be a positive odd number.

        Returns:
            Blurred image.
        """
        self.last_action = f"Blur ({intensity})"

        # No blur requested
        if intensity <= 0:
            return img.copy()

        # Kernel size must be odd for GaussianBlur
        k = max(1, int(intensity))
        if k % 2 == 0:
            k += 1

        return cv2.GaussianBlur(img, (k, k), 0)

    def edges(self, img: np.ndarray, low: int = None, high: int = None) -> np.ndarray:
        """
        Apply Canny edge detection.

        Args:
            low: Lower threshold for hysteresis.
            high: Upper threshold for hysteresis.

        If thresholds are not provided,
        default values are used.
        """
        self.last_action = "Edges"

        if low is None or high is None:
            low, high = self.DEFAULT_CANNY

        # Edge detection works best on grayscale images
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, int(low), int(high))

        # Convert result back to BGR for consistency
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    def adjust_brightness(self, img: np.ndarray, value: int) -> np.ndarray:
        """
        Adjust image brightness.

        Args:
            value: Brightness offset.
                   Positive values make image brighter,
                   negative values make it darker.
        """
        self.last_action = f"Brightness ({value})"

        # beta controls brightness offset
        return cv2.convertScaleAbs(img, alpha=1.0, beta=int(value))

    def adjust_contrast(self, img: np.ndarray, value: int) -> np.ndarray:
        """
        Adjust image contrast.

        Args:
            value: Contrast level (0..200).
                   100 means no change.
        """
        self.last_action = f"Contrast ({value})"

        # alpha controls contrast scaling
        alpha = max(0.0, float(value) / 100.0)

        return cv2.convertScaleAbs(img, alpha=alpha, beta=0)

    def rotate(self, img: np.ndarray, angle: int) -> np.ndarray:
        """
        Rotate the image by a fixed angle.

        Supported angles:
        - 90 degrees clockwise
        - 180 degrees
        - 270 degrees clockwise
        """
        self.last_action = f"Rotate ({angle})"

        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

        if angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)

        if angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # If angle is invalid, return a copy of the image
        return img.copy()

    def flip(self, img: np.ndarray, mode: str) -> np.ndarray:
        """
        Flip the image horizontally or vertically.

        Args:
            mode:
                'horizontal' -> mirror left to right
                'vertical'   -> flip top to bottom
        """
        self.last_action = f"Flip ({mode})"

        if mode == "horizontal":
            return cv2.flip(img, 1)

        if mode == "vertical":
            return cv2.flip(img, 0)

        # Invalid mode, return unchanged image
        return img.copy()

    def resize_scale(self, img: np.ndarray, percent: int) -> np.ndarray:
        """
        Resize an image based on percentage scale.

        Args:
            percent: Scale percentage (10..200 recommended).

        Returns:
            Resized image.
        """
        percent = int(percent)
        percent = max(10, min(200, percent))

        self.last_action = f"Resize ({percent}%)"

        # Original dimensions
        h, w = img.shape[:2]

        # New dimensions based on percentage
        new_w = max(1, int(w * (percent / 100.0)))
        new_h = max(1, int(h * (percent / 100.0)))

        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
