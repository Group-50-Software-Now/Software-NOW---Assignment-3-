"""
app.py
Tkinter GUI for a simple image editor.

This file is responsible for the user interface side of the project:
- Menus: Open / Save / Save As / Exit + Undo / Redo
- Buttons: one-click actions like grayscale, edges, rotate, flip, resize
- Sliders: adjustable values for blur, brightness, and contrast
- Canvas: shows the current working image
- Status bar: shows filename, dimensions, undo/redo availability, and last action

Important note:
OpenCV images are stored in BGR format, while PIL/Tkinter display expects RGB.
So we convert BGR -> RGB only at the moment we render to the canvas.
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional

import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from image_processor import ImageProcessor
from history_manager import HistoryManager


@dataclass
class ImageInfo:
    """
    Small container used for status bar info.

    It keeps the status bar logic tidy instead of passing raw variables around.
    """
    filename: str = "No file"
    width: int = 0
    height: int = 0


class ImageEditorApp:
    """
    Main GUI class for the image editor.

    This class is designed to:
    - manage application state (current image, file path, modified state)
    - build the interface (menu, controls, canvas, status bar)
    - act as a coordinator between:
        * ImageProcessor (OpenCV operations)
        * HistoryManager (Undo/Redo)

    The key idea is separation of concerns:
    GUI stays here, image processing stays in image_processor.py.
    """

    SUPPORTED_FORMATS = [("Image Files", "*.jpg *.jpeg *.png *.bmp")]

    def __init__(self) -> None:
        """  
        Constructor for the application.

        Sets up:
        - the main window
        - core helper objects (processor, history)
        - initial state variables
        - all GUI elements
        """
        # Window setup
        self.root.title("AI Image Editor (Tkinter + OpenCV)") 
        self.root.geometry("1100x700") 
        self.root.minsize(900, 600) 
   
        # Core components 
       
        self.processor = ImageProcessor() self.history = HistoryManager(max_states=25)
       
        # Application state 
        self.current_image: Optional[np.ndarray] = None 
        self.current_path: Optional[str] = None 
        self.info = ImageInfo() 
        # These help drive the status bar and exit prompts 
        self.is_modified = False self.last_action = "Ready"
        
        # Tkinter PhotoImage must be stored as an attribute, 
        # otherwise it can get garbage collected and disappear from the UI. 
        
        self._tk_img: Optional[ImageTk.PhotoImage] = None
        # Slider session support:
        # When the user drags a slider, we preview the effect live,
        # but commit it as ONE history item once they release the mouse.
        self._slider_base_image: Optional[np.ndarray] = None
        self._active_slider: Optional[str] = None  # blur/brightness/contrast
        
        # Build the UI
        self._build_menu()
        self._build_layout()
        self._build_controls()
        self._update_status()

        # Intercept closing the window so we can warn about unsaved changes
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)

    def run(self) -> None:
        """
        Start the Tkinter main loop.

        This keeps the window alive and listens for user input (clicks, slider moves, etc).
        """
        self.root.mainloop()

    # GUI BUILD 

    def _build_menu(self) -> None:
        """
        Build the menu bar.

        Two menus are required:
        - File: Open, Save, Save As, Exit
        - Edit: Undo, Redo
        """
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open", command=self.open_image)
        file_menu.add_command(label="Save", command=self.save_image)
        file_menu.add_command(label="Save As", command=self.save_as_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_exit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)
        menubar.add_cascade(label="Edit", menu=edit_menu)

              self.root.config(menu=menubar)

    def _build_layout(self) -> None:
        """
        Build the main layout frames.

        Layout design:
        - Left side: control panel (buttons and sliders)
        - Right side: canvas to display the image
        - Bottom: status bar for file info + undo/redo + last action
        """
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Control panel on the left
        self.control_frame = tk.Frame(self.main_frame, width=320, padx=10, pady=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Display area on the right
        self.display_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Canvas is where the image is drawn
        self.canvas = tk.Canvas(self.display_frame, bg="#222222", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Status bar at the bottom
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            padx=10,
            pady=5,
            relief=tk.SUNKEN
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Whenever the canvas changes size (user resizes the window),
        # redraw the image so it stays centred and scaled correctly.
        self.canvas.bind("<Configure>", lambda _e: self._render_image())

    def _build_controls(self) -> None:
        """
        Create all interactive controls:
        - Buttons for instant effects
        - Sliders for adjustable effects (with value labels)
        - Resize slider + apply button
        """
        tk.Label(self.control_frame, text="Controls", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        # One-click buttons
        tk.Button(self.control_frame, text="Grayscale", command=self.apply_grayscale).pack(fill=tk.X, pady=2)
        tk.Button(self.control_frame, text="Edge Detection", command=self.apply_edges).pack(fill=tk.X, pady=2)

      
        # Rotation buttons
        rotate_frame = tk.LabelFrame(self.control_frame, text="Rotate")
        rotate_frame.pack(fill=tk.X, pady=8)

        tk.Button(rotate_frame, text="90°", command=lambda: self.apply_rotate(90)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=4)
        tk.Button(rotate_frame, text="180°", command=lambda: self.apply_rotate(180)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=4)
        tk.Button(rotate_frame, text="270°", command=lambda: self.apply_rotate(270)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=4)

        # Flip buttons
        flip_frame = tk.LabelFrame(self.control_frame, text="Flip")
        flip_frame.pack(fill=tk.X, pady=8)

        tk.Button(flip_frame, text="Horizontal", command=lambda: self.apply_flip("horizontal")).pack(fill=tk.X, padx=2, pady=2)
        tk.Button(flip_frame, text="Vertical", command=lambda: self.apply_flip("vertical")).pack(fill=tk.X, padx=2, pady=2)

        # Adjustment sliders
        slider_frame = tk.LabelFrame(self.control_frame, text="Adjustments")
        slider_frame.pack(fill=tk.X, pady=10)

        #  Blur
        self.blur_var = tk.IntVar(value=0)
        self.blur_label = tk.Label(slider_frame, text="Blur: 0", anchor="w")
        self.blur_label.pack(fill=tk.X)

        self.blur_scale = tk.Scale(
            slider_frame,
            from_=0,
            to=50,
            orient=tk.HORIZONTAL,
            variable=self.blur_var,
            # We hide Tkinter’s default value because it looks a bit clunky,
            # and instead show the number in a cleaner label above.
            showvalue=False
        )
        self.blur_scale.pack(fill=tk.X)

        # Brightness 
        self.bright_var = tk.IntVar(value=0)
        self.bright_label = tk.Label(slider_frame, text="Brightness: 0", anchor="w")
        self.bright_label.pack(fill=tk.X, pady=(6, 0))

        self.bright_scale = tk.Scale(
            slider_frame,
            from_=-100,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.bright_var,
            showvalue=False
        )
        self.bright_scale.pack(fill=tk.X)

        #Contrast 
        self.contrast_var = tk.IntVar(value=100)
        self.contrast_label = tk.Label(slider_frame, text="Contrast: 100", anchor="w")
        self.contrast_label.pack(fill=tk.X, pady=(6, 0))

        self.contrast_scale = tk.Scale(
            slider_frame,
            from_=0,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.contrast_var,
            showvalue=False
        )
        self.contrast_scale.pack(fill=tk.X)

        # Slider behaviour:
        # We preview the effect while dragging,
        # but only commit to history ONCE when the user releases the mouse.
        self.blur_scale.bind("<ButtonPress-1>", lambda _e: self._start_slider_edit("blur"))
        self.blur_scale.bind("<ButtonRelease-1>", lambda _e: self._commit_slider_edit())

        self.bright_scale.bind("<ButtonPress-1>", lambda _e: self._start_slider_edit("brightness"))
        self.bright_scale.bind("<ButtonRelease-1>", lambda _e: self._commit_slider_edit())

        self.contrast_scale.bind("<ButtonPress-1>", lambda _e: self._start_slider_edit("contrast"))
        self.contrast_scale.bind("<ButtonRelease-1>", lambda _e: self._commit_slider_edit())

        # Whenever a slider value changes:
        # - update the labels
        # - preview the effect (if the user is actively dragging)
        self.blur_var.trace_add("write", lambda *_: self._on_slider_value_change())
        self.bright_var.trace_add("write", lambda *_: self._on_slider_value_change())
        self.contrast_var.trace_add("write", lambda *_: self._on_slider_value_change())

        # Resize controls
        resize_frame = tk.LabelFrame(self.control_frame, text="Resize / Scale")
        resize_frame.pack(fill=tk.X, pady=10)

        self.scale_var = tk.IntVar(value=100)
        self.scale_label = tk.Label(resize_frame, text="Scale: 100%", anchor="w")
        self.scale_label.pack(fill=tk.X)

        tk.Scale(
            resize_frame,
            from_=10,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.scale_var,
            showvalue=False
        ).pack(fill=tk.X)

        # Update scale label as the user moves the slider
        self.scale_var.trace_add("write", lambda *_: self._update_scale_label())

        # Apply resize is intentionally a button:
        # resizing can be expensive, so doing it live while dragging could feel laggy.
        tk.Button(resize_frame, text="Apply Resize", command=self.apply_resize).pack(fill=tk.X, pady=6)

        # Reset sliders is a quick UX helper
        tk.Button(self.control_frame, text="Reset Sliders", command=self.reset_sliders).pack(fill=tk.X, pady=6)

        # Ensure labels match initial values right from the start
        self._refresh_slider_labels()

    #  Slider label helpers 

    def _refresh_slider_labels(self) -> None:
        """
        Refresh all slider labels.

        This keeps the sidebar feeling tidy and “live”
        because the numbers always reflect the current slider positions.
        """
        self.blur_label.config(text=f"Blur: {int(self.blur_var.get())}")
        self.bright_label.config(text=f"Brightness: {int(self.bright_var.get())}")
        self.contrast_label.config(text=f"Contrast: {int(self.contrast_var.get())}")
        self.scale_label.config(text=f"Scale: {int(self.scale_var.get())}%")

    def _update_scale_label(self) -> None:
        """
        Update only the scale label.

        This is separated because resize is applied by a button,
        but the label should still update immediately when the slider changes.
        """
        self.scale_label.config(text=f"Scale: {int(self.scale_var.get())}%")
        self._update_status()

    def _on_slider_value_change(self) -> None:
        """
        Called whenever blur/brightness/contrast values change.

        Two responsibilities:
        1) Update labels for a clean UI
        2) Preview the active effect (only during an active drag session)
        """
        self._refresh_slider_labels()
        self._preview_slider_effect()

    # File actions 

    def open_image(self) -> None:
        """
        Open an image file from disk.

        When a new image is opened:
        - history is cleared (undo/redo should not carry over)
        - sliders reset
        - status bar updates
        """
        path = filedialog.askopenfilename(title="Open Image", filetypes=self.SUPPORTED_FORMATS)
        if not path:
            return

        try:
            img = self.processor.read_image(path)
        except Exception as e:
            messagebox.showerror("Open Error", f"Could not open image:\n{e}")
            return

        self.current_image = img
        self.current_path = path
        self.history.clear()
        self.reset_sliders()

        self.is_modified = False
        self.last_action = "Opened image"
        self._update_info_from_image()
        self._render_image()

    def save_image(self) -> None:
        """
        Save the image to the current file path.

        If the file has not been saved before, we redirect to Save As.
        """
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return

        if not self.current_path:
            self.save_as_image()
            return

        try:
            self.processor.write_image(self.current_path, self.current_image)
            self.is_modified = False
            self.last_action = "Saved image"
            messagebox.showinfo("Saved", "Image saved successfully.")
            self._update_status()
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save image:\n{e}")

    def save_as_image(self) -> None:
        """Save the image to a new location chosen by the user."""
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return

        path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png",
            filetypes=self.SUPPORTED_FORMATS
        )
        if not path:
            return

        try:
            self.processor.write_image(path, self.current_image)
            self.current_path = path
            self.is_modified = False
            self.last_action = "Saved image as"
            messagebox.showinfo("Saved", "Image saved successfully.")
            self._update_info_from_image()
            self._render_image()
        except Exception as e:
            messagebox.showerror("Save As Error", f"Could not save image:\n{e}")

    def _on_exit(self) -> None:
        """
        Exit safely.

        If the user has unsaved work, we show a confirmation message
        to prevent accidental data loss.
        """
        if self.is_modified:
            if not messagebox.askyesno("Exit", "You have unsaved changes. Exit anyway?"):
                return
        self.root.destroy()

    # Undo/Redo

    def undo(self) -> None:
        """Undo the last edit (if possible)."""
        if self.current_image is None:
            return

        prev = self.history.undo(self.current_image)
        if prev is None:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return

        self.current_image = prev
        self.is_modified = True
        self.last_action = "Undo"
        self._update_info_from_image()
        self._render_image()

    def redo(self) -> None:
        """Redo the last undone edit (if possible)."""
        if self.current_image is None:
            return

        nxt = self.history.redo(self.current_image)
        if nxt is None:
            messagebox.showinfo("Redo", "Nothing to redo.")
            return

        self.current_image = nxt
        self.is_modified = True
        self.last_action = "Redo"
        self._update_info_from_image()
        self._render_image()

    # Apply changes 

    def _require_image(self) -> bool:
        """
        Guard helper: makes sure an image exists before we apply effects.

        This avoids crashes and gives a nicer user experience.
        """
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return False
        return True

    def _apply_change(self, new_img: np.ndarray, action: str) -> None:
        """
        Apply an edit and register it into undo history.

        Flow:
        - push current image into history (Undo support)
        - set new image
        - mark as modified
        - refresh canvas + status bar
        """
        if self.current_image is None:
            return

        self.history.push(self.current_image)
        self.current_image = new_img
        self.is_modified = True
        self.last_action = action

        self._update_info_from_image()
        self._render_image()

    def apply_grayscale(self) -> None:
        """Convert the image to grayscale."""
        if not self._require_image():
            return
        self._apply_change(self.processor.to_grayscale(self.current_image), "Grayscale applied")

    def apply_edges(self) -> None:
        """Apply edge detection to highlight boundaries in the image."""
        if not self._require_image():
            return
        self._apply_change(self.processor.edges(self.current_image), "Edges applied")

    def apply_rotate(self, angle: int) -> None:
        """Rotate image by 90/180/270 degrees."""
        if not self._require_image():
            return
        self._apply_change(self.processor.rotate(self.current_image, angle), f"Rotated {angle}°")

    def apply_flip(self, mode: str) -> None:
        """Flip the image horizontally or vertically."""
        if not self._require_image():
            return
        self._apply_change(self.processor.flip(self.current_image, mode), f"Flipped {mode}")

    def apply_resize(self) -> None:
        """Resize image using the current scale percentage slider value."""
        if not self._require_image():
            return
        percent = int(self.scale_var.get())
        self._apply_change(self.processor.resize_scale(self.current_image, percent), f"Resized to {percent}%")

    def reset_sliders(self) -> None:
        """
        Reset all slider values to defaults.

        This only resets the UI controls.
        It does not “undo” image changes — Undo/Redo is responsible for that.
        """
        self.blur_var.set(0)
        self.bright_var.set(0)
        self.contrast_var.set(100)
        self.scale_var.set(100)
        self._refresh_slider_labels()

        self.last_action = "Sliders reset"
        self._update_status()

    # Slider preview

    def _start_slider_edit(self, slider_name: str) -> None:
        """
        Start a slider edit session.

        We store the current image as a "base image" so that preview effects apply cleanly.
        Without this, the preview could stack repeatedly (which can reduce image quality).
        """
        if not self._require_image():
            return
        self._active_slider = slider_name
        self._slider_base_image = self.current_image.copy()

    def _preview_slider_effect(self) -> None:
        """
        Live preview for the active slider.

        Very important behaviour:
        - Only works during an active slider session
        - It previews on top of the base image, not on top of previous previews
        """
        if self.current_image is None or self._slider_base_image is None or self._active_slider is None:
            return

        base = self._slider_base_image

        if self._active_slider == "blur":
            preview = self.processor.blur(base, int(self.blur_var.get()))
        elif self._active_slider == "brightness":
            preview = self.processor.adjust_brightness(base, int(self.bright_var.get()))
        elif self._active_slider == "contrast":
            preview = self.processor.adjust_contrast(base, int(self.contrast_var.get()))
        else:
            return

        self.current_image = preview
        self.is_modified = True
        self.last_action = f"Adjusting {self._active_slider}"
        self._update_info_from_image()
        self._render_image()

    def _commit_slider_edit(self) -> None:
        """
        Commit the slider edit as ONE undo step.

        This makes Undo feel natural:
        even if the user drags the slider a lot,
        they only need to press Undo once to go back.
        """
        if self._slider_base_image is None:
            self._active_slider = None
            return

        # Push the base state (image before slider drag) into history
        self.history.push(self._slider_base_image)

        self._slider_base_image = None
        self._active_slider = None
        self._update_info_from_image()
        self._render_image()

    # Display + status

    def _update_info_from_image(self) -> None:
        """Update filename and dimensions in the status bar."""
        if self.current_image is None:
            self.info = ImageInfo()
            self._update_status()
            return

        h, w = self.current_image.shape[:2]
        name = os.path.basename(self.current_path) if self.current_path else "Unsaved image"
        self.info = ImageInfo(filename=name, width=w, height=h)
        self._update_status()

    def _update_status(self) -> None:
        """
        Update the status bar text.

        The status bar acts like a “quick feedback area”:
        it helps the user understand what the app is doing.
        """
        modified = " (modified)" if self.is_modified else ""
        self.status_var.set(
            f"{self.info.filename}{modified} | {self.info.width} x {self.info.height} | "
            f"Undo: {self.history.can_undo()} | Redo: {self.history.can_redo()} | "
            f"Last: {self.last_action}"
        )

    def _render_image(self) -> None:
        """
        Render the current image to the canvas.

        Steps:
        - clear the canvas
        - convert image for display (BGR -> RGB)
        - convert to PIL image
        - resize to fit canvas while keeping aspect ratio
        - draw on canvas and store PhotoImage reference
        """
        self._update_status()
        self.canvas.delete("all")

        if self.current_image is None:
            self.canvas.create_text(
                20, 20,
                anchor="nw",
                fill="white",
                text="Open an image from File > Open to start.",
                font=("Segoe UI", 12)
            )
            return

        c_w = max(1, self.canvas.winfo_width())
        c_h = max(1, self.canvas.winfo_height())

        # Convert BGR -> RGB for display
        rgb = self.processor.bgr_to_rgb(self.current_image)
        pil_img = Image.fromarray(rgb)

        # Resize for canvas display (aspect ratio preserved)
        pil_img = self._fit_to_canvas(pil_img, c_w, c_h)

        # Keep a reference to avoid disappearing images
        self._tk_img = ImageTk.PhotoImage(pil_img)
        self.canvas.create_image(c_w // 2, c_h // 2, image=self._tk_img, anchor="center")

    @staticmethod
    def _fit_to_canvas(pil_img: Image.Image, canvas_w: int, canvas_h: int) -> Image.Image:
        """
        Resize a PIL image to fit inside the canvas while preserving aspect ratio.

        This prevents images from being stretched unnaturally.
        """
        img_w, img_h = pil_img.size
        if img_w == 0 or img_h == 0:
            return pil_img

        scale = min(canvas_w / img_w, canvas_h / img_h)
        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))

        return pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
