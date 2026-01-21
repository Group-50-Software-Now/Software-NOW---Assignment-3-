"""
main.py

This is the entry point of the application.

Keeping this file small is intentional:
- It makes the project easy to understand (one clear starting point)
- The GUI logic stays inside app.py where it belongs
"""

from app import ImageEditorApp


def main() -> None:
    """Create the app object and start the Tkinter main loop."""
    app = ImageEditorApp()
    app.run()


if __name__ == "__main__":
    main()
