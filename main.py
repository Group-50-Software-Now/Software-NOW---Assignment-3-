"""
main.py

Entry point for the HIT137 Image Editor application.

This file stays intentionally small:
- It creates the GUI app
- It starts the Tkinter event loop

Keeping this separate makes the project structure cleaner and easier to mark.
"""

from app import ImageEditorApp


def main() -> None:
    """Create the app and run it."""
    app = ImageEditorApp()
    app.run()


if __name__ == "__main__":
    main()
