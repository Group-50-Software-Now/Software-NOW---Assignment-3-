"""
app.py

Tkinter GUI for a simple image editor.

This file handles:
- menus (Open/Save/Save As/Exit, Undo/Redo)
- buttons for one-click actions (grayscale, edges, rotate, flip, resize)
- sliders for adjustable effects (blur, brightness, contrast)
- displaying the image on a canvas
- a status bar showing filename, size, and last action

OpenCV uses BGR images, but Tkinter/PIL expects RGB for display.
So we convert BGR -> RGB only when rendering.

UI goals for this version:
- modern dark theme
- colourful heading (more "real app" feel)
- scrollable sidebar (so it still looks good on small screens)
- clean value labels for sliders (no ugly 0..200 text on the side)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

from image_processor import ImageProcessor
from history_manager import HistoryManager


@dataclass
class ImageInfo:
    """Small container for what we show in the status bar."""
    filename: str = "No file loaded"
    width: int = 0
    height: int = 0


class ImageEditorApp:
    """
    Main GUI application class.

    This class is responsible for:
    - all Tkinter UI layout and styling
    - user input events (buttons, sliders, menus)
    - calling ImageProcessor for OpenCV effects
    - calling HistoryManager for Undo/Redo
    """

    SUPPORTED_FORMATS = [("Image Files", "*.jpg *.jpeg *.png *.bmp")]

    # ---- Theme colours (kept here so you can tweak in one place) ----
    BG = "#0b1020"         # main background
    PANEL = "#0f172a"      # sidebar / cards
    CARD = "#111c33"       # slightly lighter panel block
    TEXT = "#e5e7eb"       # main text
    MUTED = "#94a3b8"      # muted text
    ACCENT = "#22c55e"     # green accent

    def __init__(self) -> None:
        # ------------ Core state ------------
        self.root = tk.Tk()
        self.root.title("AI Image Editor (Tkinter + OpenCV)")
        self.root.geometry("1180x740")
        self.root.minsize(980, 620)
        self.root.configure(bg=self.BG)

        # Processing + history objects (class interaction requirement)
        self.processor = ImageProcessor()
        self.history = HistoryManager(max_states=25)

        self.current_image: Optional[np.ndarray] = None
        self.current_path: Optional[str] = None
        self.info = ImageInfo()

        self.is_modified: bool = False
        self.last_action: str = "Ready"

        # Tkinter ImageTk reference (if we don't store this, Tkinter may not display it)
        self._tk_img: Optional[ImageTk.PhotoImage] = None

        # Slider edit session state
        # We preview live while dragging, but commit as ONE undo step at release.
        self._active_slider: Optional[str] = None          # "blur", "brightness", "contrast"
        self._slider_base_image: Optional[np.ndarray] = None

        # ------------ UI setup ------------
        self._setup_styles()
        self._build_menu()
        self._build_layout()
        self._build_controls()

        # Status shown immediately
        self._update_status()
        self._render_image()  # shows welcome screen text

        # Confirm close
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)

        # Keyboard shortcuts (feels like a real desktop app)
        self.root.bind_all("<Control-o>", lambda _e: self.open_image())
        self.root.bind_all("<Control-s>", lambda _e: self.save_image())
        self.root.bind_all("<Control-Shift-S>", lambda _e: self.save_as_image())
        self.root.bind_all("<Control-z>", lambda _e: self.undo())
        self.root.bind_all("<Control-y>", lambda _e: self.redo())

    def run(self) -> None:
        """Start Tkinter main loop."""
        self.root.mainloop()

    # ------------------------ Styling ------------------------

    def _setup_styles(self) -> None:
        """
        Configure ttk styles.

        ttk styling is a bit "manual", but once it’s set up,
        the app looks cleaner and more consistent.
        """
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=self.BG)
        style.configure("Card.TFrame", background=self.PANEL)

        style.configure("TLabel", background=self.BG, foreground=self.TEXT, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=self.BG, foreground=self.MUTED, font=("Segoe UI", 10))
        style.configure("SubTitle.TLabel", background=self.BG, foreground=self.MUTED, font=("Segoe UI", 10))

        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=9)
        style.map("TButton",
                  background=[("active", self.CARD)],
                  foreground=[("active", self.TEXT)])

        style.configure("TLabelframe", background=self.PANEL, foreground=self.TEXT, borderwidth=0)
        style.configure("TLabelframe.Label", background=self.PANEL, foreground=self.TEXT,
                        font=("Segoe UI", 10, "bold"))

        style.configure("Vertical.TScrollbar", background=self.PANEL, troughcolor=self.BG)

    # ------------------------ Menu ------------------------

    def _build_menu(self) -> None:
        """Build menu bar: File + Edit (Undo/Redo)."""
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open (Ctrl+O)", command=self.open_image)
        file_menu.add_command(label="Save (Ctrl+S)", command=self.save_image)
        file_menu.add_command(label="Save As (Ctrl+Shift+S)", command=self.save_as_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_exit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Undo (Ctrl+Z)", command=self.undo)
        edit_menu.add_command(label="Redo (Ctrl+Y)", command=self.redo)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=menubar)

    # ------------------------ Layout ------------------------

    def _build_layout(self) -> None:
        """
        Create the main layout:
        - Header
        - Main body: Sidebar (left) + Canvas display (right)
        - Status bar
        """
        # ----- Header -----
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=14, pady=(14, 10))

        # We use a canvas for the title so we can colour different words.
        brand = tk.Canvas(header, height=54, bg=self.BG, highlightthickness=0)
        brand.pack(fill=tk.X)

        x = 8
        y = 28
        brand.create_text(x, y, text="AI", fill=self.ACCENT, font=("Segoe UI", 26, "bold"), anchor="w")
        brand.create_text(x + 44, y, text=" Image", fill=self.TEXT, font=("Segoe UI", 26, "bold"), anchor="w")
        brand.create_text(x + 156, y, text=" Editor", fill="#a78bfa", font=("Segoe UI", 26, "bold"), anchor="w")
        brand.create_line(8, 48, 220, 48, fill=self.ACCENT, width=3)

        subtitle = ttk.Label(
            header,
            text="HIT137 • Desktop Image Editor (Tkinter + OpenCV) • Undo/Redo supported",
            style="SubTitle.TLabel",
        )
        subtitle.pack(anchor="w", padx=6, pady=(2, 0))

        # ----- Main body -----
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 12))

        # Sidebar outer
        self.control_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        # Scrollable sidebar (canvas + scrollbar)
        self.sidebar_canvas = tk.Canvas(
            self.control_frame,
            bg=self.PANEL,
            highlightthickness=0,
            width=340
        )
        self.sidebar_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        sidebar_scroll = ttk.Scrollbar(self.control_frame, orient="vertical", command=self.sidebar_canvas.yview)
        sidebar_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.sidebar_canvas.configure(yscrollcommand=sidebar_scroll.set)

        # Inner sidebar content frame
        self.sidebar_inner = ttk.Frame(self.sidebar_canvas, style="Card.TFrame")
        self.sidebar_window = self.sidebar_canvas.create_window((0, 0), window=self.sidebar_inner, anchor="nw")

        def _on_sidebar_config(_e=None):
            self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))
            self.sidebar_canvas.itemconfig(self.sidebar_window, width=self.sidebar_canvas.winfo_width())

        self.sidebar_inner.bind("<Configure>", _on_sidebar_config)
        self.sidebar_canvas.bind("<Configure>", _on_sidebar_config)

        # Right: display frame and canvas
        self.display_frame = ttk.Frame(self.main_frame)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.display_frame, bg="#060812", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Redraw image when resizing
        self.canvas.bind("<Configure>", lambda _e: self._render_image())

        # ----- Status bar -----
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg="#070b14",
            fg=self.TEXT,
            anchor="w",
            padx=12,
            pady=10
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # ------------------------ Controls ------------------------

    def _build_controls(self) -> None:
        """
        Build sidebar controls.
        Important: We do NOT add extra feature buttons.
        Only what the assignment requires:
        - Grayscale
        - Blur (adjustable)
        - Edge detection
        - Brightness (adjustable)
        - Contrast (adjustable)
        - Rotate (90/180/270)
        - Flip (H/V)
        - Resize/scale
        """
        wrap = ttk.Frame(self.sidebar_inner, style="Card.TFrame")
        wrap.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Sidebar mini brand
        brand_side = tk.Frame(wrap, bg=self.PANEL)
        brand_side.pack(fill=tk.X, pady=(0, 12))

        tk.Label(brand_side, text="AI", bg=self.PANEL, fg=self.ACCENT,
                 font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)
        tk.Label(brand_side, text=" Image Editor", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)
        tk.Label(brand_side, text="HIT137", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.RIGHT)

        # -------- Quick actions --------
        actions = ttk.LabelFrame(wrap, text="Quick Actions")
        actions.pack(fill=tk.X, pady=(0, 12))

        ttk.Button(actions, text="Grayscale", command=self.apply_grayscale).pack(fill=tk.X, pady=6, padx=8)
        ttk.Button(actions, text="Edge Detection", command=self.apply_edges).pack(fill=tk.X, pady=6, padx=8)

        # -------- Rotate --------
        rotate_frame = ttk.LabelFrame(wrap, text="Rotate")
        rotate_frame.pack(fill=tk.X, pady=(0, 12))

        row = ttk.Frame(rotate_frame)
        row.pack(fill=tk.X, padx=8, pady=8)

        ttk.Button(row, text="90°", command=lambda: self.apply_rotate(90)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
        ttk.Button(row, text="180°", command=lambda: self.apply_rotate(180)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
        ttk.Button(row, text="270°", command=lambda: self.apply_rotate(270)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)

        # -------- Flip --------
        flip_frame = ttk.LabelFrame(wrap, text="Flip")
        flip_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Button(flip_frame, text="Horizontal", command=lambda: self.apply_flip("horizontal")).pack(fill=tk.X, pady=6, padx=8)
        ttk.Button(flip_frame, text="Vertical", command=lambda: self.apply_flip("vertical")).pack(fill=tk.X, pady=6, padx=8)

        # -------- Adjustments (sliders) --------
        adjust = ttk.LabelFrame(wrap, text="Adjustments")
        adjust.pack(fill=tk.X, pady=(0, 12))

        # Blur
        self.blur_var = tk.IntVar(value=0)
        self.blur_label = tk.Label(adjust, text="Blur: 0", bg=self.PANEL, fg=self.TEXT, font=("Segoe UI", 10, "bold"), anchor="w")
        self.blur_label.pack(fill=tk.X, padx=10, pady=(10, 2))

        self.blur_scale = tk.Scale(
            adjust, from_=0, to=50, orient=tk.HORIZONTAL,
            variable=self.blur_var, showvalue=False,
            bg=self.PANEL, fg=self.TEXT, troughcolor=self.BG,
            highlightthickness=0
        )
        self.blur_scale.pack(fill=tk.X, padx=10, pady=(0, 8))

        # Brightness
        self.bright_var = tk.IntVar(value=0)
        self.bright_label = tk.Label(adjust, text="Brightness: 0", bg=self.PANEL, fg=self.TEXT, font=("Segoe UI", 10, "bold"), anchor="w")
        self.bright_label.pack(fill=tk.X, padx=10, pady=(8, 2))

        self.bright_scale = tk.Scale(
            adjust, from_=-100, to=100, orient=tk.HORIZONTAL,
            variable=self.bright_var, showvalue=False,
            bg=self.PANEL, fg=self.TEXT, troughcolor=self.BG,
            highlightthickness=0
        )
        self.bright_scale.pack(fill=tk.X, padx=10, pady=(0, 8))

        # Contrast
        # NOTE: 0..200 is correct; 100 = normal.
        self.contrast_var = tk.IntVar(value=100)
        self.contrast_label = tk.Label(adjust, text="Contrast: 100", bg=self.PANEL, fg=self.TEXT, font=("Segoe UI", 10, "bold"), anchor="w")
        self.contrast_label.pack(fill=tk.X, padx=10, pady=(8, 2))

        self.contrast_scale = tk.Scale(
            adjust, from_=0, to=200, orient=tk.HORIZONTAL,
            variable=self.contrast_var, showvalue=False,
            bg=self.PANEL, fg=self.TEXT, troughcolor=self.BG,
            highlightthickness=0
        )
        self.contrast_scale.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Slider session behaviour:
        # - record base image on press
        # - preview live during drag
        # - push ONE undo state when release
        self.blur_scale.bind("<ButtonPress-1>", lambda _e: self._start_slider_edit("blur"))
        self.blur_scale.bind("<ButtonRelease-1>", lambda _e: self._commit_slider_edit())

        self.bright_scale.bind("<ButtonPress-1>", lambda _e: self._start_slider_edit("brightness"))
        self.bright_scale.bind("<ButtonRelease-1>", lambda _e: self._commit_slider_edit())

        self.contrast_scale.bind("<ButtonPress-1>", lambda _e: self._start_slider_edit("contrast"))
        self.contrast_scale.bind("<ButtonRelease-1>", lambda _e: self._commit_slider_edit())

        # Live updates
        self.blur_var.trace_add("write", lambda *_: self._on_slider_value_change())
        self.bright_var.trace_add("write", lambda *_: self._on_slider_value_change())
        self.contrast_var.trace_add("write", lambda *_: self._on_slider_value_change())

        # -------- Resize --------
        resize = ttk.LabelFrame(wrap, text="Resize / Scale")
        resize.pack(fill=tk.X, pady=(0, 12))

        self.scale_var = tk.IntVar(value=100)
        self.scale_label = tk.Label(resize, text="Scale: 100%", bg=self.PANEL, fg=self.TEXT, font=("Segoe UI", 10, "bold"), anchor="w")
        self.scale_label.pack(fill=tk.X, padx=10, pady=(10, 2))

        self.scale_scale = tk.Scale(
            resize, from_=10, to=200, orient=tk.HORIZONTAL,
            variable=self.scale_var, showvalue=False,
            bg=self.PANEL, fg=self.TEXT, troughcolor=self.BG,
            highlightthickness=0
        )
        self.scale_scale.pack(fill=tk.X, padx=10, pady=(0, 8))
        self.scale_var.trace_add("write", lambda *_: self._update_scale_label())

        ttk.Button(resize, text="Apply Resize", command=self.apply_resize).pack(fill=tk.X, padx=10, pady=(2, 10))

        # Reset sliders (requested)
        ttk.Button(wrap, text="Reset Sliders", command=self.reset_sliders).pack(fill=tk.X, pady=(0, 10))

        # Ensure labels match defaults
        self._refresh_slider_labels()

    # ---------------- Slider helpers ----------------

    def _refresh_slider_labels(self) -> None:
        """Keep slider labels in sync with current values."""
        self.blur_label.config(text=f"Blur: {int(self.blur_var.get())}")
        self.bright_label.config(text=f"Brightness: {int(self.bright_var.get())}")
        self.contrast_label.config(text=f"Contrast: {int(self.contrast_var.get())}")
        self.scale_label.config(text=f"Scale: {int(self.scale_var.get())}%")

    def _update_scale_label(self) -> None:
        """Update the scale label only (used when slider moves)."""
        self.scale_label.config(text=f"Scale: {int(self.scale_var.get())}%")
        self._update_status()

    def _on_slider_value_change(self) -> None:
        """
        When a slider moves:
        - update labels for a clean UI
        - if user is actively dragging, preview the effect
        """
        self._refresh_slider_labels()
        self._preview_slider_effect()

    def _start_slider_edit(self, slider_name: str) -> None:
        """
        Start a slider edit session.

        We store the base image once so preview does not stack edits on edits.
        That gives a smoother preview and avoids quality loss.
        """
        if not self._require_image():
            return
        self._active_slider = slider_name
        self._slider_base_image = self.current_image.copy()

    def _preview_slider_effect(self) -> None:
        """
        Live preview for the active slider.

        We ONLY preview during an active slider drag session.
        If no slider is active, moving programmatically (like reset) should not edit the image.
        """
        if self.current_image is None or self._slider_base_image is None or self._active_slider is None:
            return

        base = self._slider_base_image

        if self._active_slider == "blur":
            preview = self.processor.blur(base, int(self.blur_var.get()))
        elif self._active_slider == "brightness":
            preview = self.processor.adjust_brightness(base, int(self.bright_var.get()))
        elif self._active_slider == "contrast":
            # contrast range 0..200 works properly here (including low contrast)
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
        Commit slider edits as ONE undo step.

        Meaning:
        - user drags the slider many times
        - pressing Undo once returns to the image before the drag started
        """
        if self._slider_base_image is None:
            self._active_slider = None
            return

        # Save the base image for Undo
        self.history.push(self._slider_base_image)

        self._slider_base_image = None
        self._active_slider = None
        self._update_info_from_image()
        self._render_image()

    def reset_sliders(self) -> None:
        """
        Reset slider values to defaults.

        This resets controls only; it doesn't automatically revert the image.
        Undo/Redo is still the correct way to revert image changes.
        """
        self.blur_var.set(0)
        self.bright_var.set(0)
        self.contrast_var.set(100)
        self.scale_var.set(100)

        self._refresh_slider_labels()
        self.last_action = "Sliders reset"
        self._update_status()

    # ---------------- File actions ----------------

    def open_image(self) -> None:
        """Open an image using a file dialog."""
        path = filedialog.askopenfilename(title="Open Image", filetypes=self.SUPPORTED_FORMATS)
        if not path:
            return

        try:
            img = self.processor.read_image(path)
        except Exception as e:
            messagebox.showerror("Open Error", f"Could not open image:\n\n{e}")
            return

        self.current_image = img
        self.current_path = path

        # Fresh state on new image
        self.history.clear()
        self.reset_sliders()

        self.is_modified = False
        self.last_action = "Opened image"
        self._update_info_from_image()
        self._render_image()

    def save_image(self) -> None:
        """Save to the current path (or fallback to Save As if needed)."""
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
            messagebox.showerror("Save Error", f"Could not save image:\n\n{e}")

    def save_as_image(self) -> None:
        """Save image to a new path."""
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
            messagebox.showerror("Save As Error", f"Could not save image:\n\n{e}")

    def _on_exit(self) -> None:
        """Exit safely, warning if there are unsaved changes."""
        if self.is_modified:
            if not messagebox.askyesno("Exit", "You have unsaved changes. Exit anyway?"):
                return
        self.root.destroy()

    # ---------------- Undo / Redo ----------------

    def undo(self) -> None:
        """Undo the last edit."""
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
        """Redo the last undone edit."""
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

    # ---------------- Apply effects ----------------

    def _require_image(self) -> bool:
        """Prevent crashes if user clicks controls before loading an image."""
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return False
        return True

    def _apply_change(self, new_img: np.ndarray, action: str) -> None:
        """
        Apply an edit safely:
        - store current image in history for Undo
        - switch to new image
        - refresh UI
        """
        if self.current_image is None:
            return

        self.history.push(self.current_image)  # correct method, not "<<"
        self.current_image = new_img
        self.is_modified = True
        self.last_action = action

        self._update_info_from_image()
        self._render_image()

    def apply_grayscale(self) -> None:
        if not self._require_image():
            return
        self._apply_change(self.processor.to_grayscale(self.current_image), "Grayscale applied")

    def apply_edges(self) -> None:
        if not self._require_image():
            return
        self._apply_change(self.processor.edges(self.current_image), "Edge detection applied")

    def apply_rotate(self, angle: int) -> None:
        if not self._require_image():
            return
        self._apply_change(self.processor.rotate(self.current_image, angle), f"Rotated {angle}°")

    def apply_flip(self, mode: str) -> None:
        if not self._require_image():
            return
        self._apply_change(self.processor.flip(self.current_image, mode), f"Flipped {mode}")

    def apply_resize(self) -> None:
        if not self._require_image():
            return
        percent = int(self.scale_var.get())
        self._apply_change(self.processor.resize_scale(self.current_image, percent), f"Resized to {percent}%")

    # ---------------- Display + status ----------------

    def _update_info_from_image(self) -> None:
        """Update filename and dimensions shown in the status bar."""
        if self.current_image is None:
            self.info = ImageInfo()
            self._update_status()
            return

        h, w = self.current_image.shape[:2]
        name = os.path.basename(self.current_path) if self.current_path else "Unsaved image"
        self.info = ImageInfo(filename=name, width=w, height=h)
        self._update_status()

    def _update_status(self) -> None:
        """Update the status bar text. (No rendering here to avoid recursion issues.)"""
        modified = " (modified)" if self.is_modified else ""
        self.status_var.set(
            f"{self.info.filename}{modified} | {self.info.width} x {self.info.height} | "
            f"Undo: {self.history.can_undo()} | Redo: {self.history.can_redo()} | "
            f"Last: {self.last_action}"
        )

    def _render_image(self) -> None:
        """
        Draw current image on the canvas.

        If no image is loaded, show a clean welcome screen in the center.
        """
        self._update_status()
        self.canvas.delete("all")

        if self.current_image is None:
            cw = max(1, self.canvas.winfo_width())
            ch = max(1, self.canvas.winfo_height())

            # Big welcome text in the middle (no animation, so no recursion bug)
            self.canvas.create_text(
                cw // 2, ch // 2 - 30,
                text="Welcome 👋",
                
