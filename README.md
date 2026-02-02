# 🎨 AI Image Editor (Tkinter + OpenCV) — HIT137 Assignment 3

A clean, professional **desktop image editor** built with **Python (Tkinter GUI + OpenCV image processing)**.  
It follows the HIT137 requirements and includes a modern dark UI, undo/redo history, and adjustable sliders for effects.

---

## ✅ Key Features (As Required)

This app includes **all 8 required image editing features**:

- ✅ **Grayscale conversion**
- ✅ **Gaussian Blur (Adjustable slider)**
- ✅ **Edge Detection (Canny)**
- ✅ **Brightness adjustment (Adjustable slider)**
- ✅ **Contrast adjustment (Adjustable slider, 0–200)**
- ✅ **Rotation** (90°, 180°, 270°)
- ✅ **Flip** (Horizontal / Vertical)
- ✅ **Resize / Scale** by percentage (10% – 200%)

> ⚠️ **No extra feature buttons were added** beyond the assignment requirements.

---

## 🖥️ User Interface Highlights

- **Modern dark theme**
- **Colorful heading + “real app” look**
- **Scrollable left sidebar** (works well on smaller screens)
- Clean slider labels (professional UI, no messy default Tk numbers)
- Centered welcome screen when no image is loaded
- Status bar showing:
  - file name  
  - image size  
  - undo/redo availability  
  - last action taken  

---

## 🧠 OOP Design (HIT137 Requirement)

This project demonstrates strong OOP structure using multiple classes:

- `ImageEditorApp` → Handles GUI, user events, rendering, and workflow
- `ImageProcessor` → Handles all OpenCV image operations (filters + transformations)
- `HistoryManager` → Manages **Undo/Redo** states using stacks (clean and memory-limited)

This separation makes the project:
- easier to understand  
- easier to maintain  
- aligned with professional software design  

---

## 📁 Project Structure

```text
📦 AI-Image-Editor/
│
├── main.py               # Entry point (starts the app)
├── app.py                # Full GUI + sidebar controls + status bar
├── image_processor.py    # OpenCV image processing logic
├── history_manager.py    # Undo/Redo system
└── README.md             # This file



▶️ How to Run
1) Install dependencies
pip install opencv-python pillow numpy

2) Run the application
python main.py

⌨️ Shortcuts (Feels like a real desktop tool)

Ctrl + O → Open image

Ctrl + S → Save

Ctrl + Shift + S → Save As

Ctrl + Z → Undo

Ctrl + Y → Redo

📝 How Undo/Redo Works

Each edit stores a snapshot of the image in history.

Slider effects preview live while dragging, but the final change is saved as one undo step.

This means:
✅ Drag 20 times → press Undo once → returns to state before drag started.

✅ Testing Notes (What was checked)

Open/Save/Save As works correctly

All filters operate properly

Contrast reduction works correctly (low contrast values)

Undo/Redo works for:

one-click actions

slider edits

resize/rotate/flip

⚠️ Common Issue Fix (VS Code / NumPy / OpenCV not found)

If you see something like:

ModuleNotFoundError: No module named numpy

It usually means VS Code is using a different Python interpreter.

✅ Fix it like this:

Open VS Code

Press: Ctrl + Shift + P

Select: Python: Select Interpreter

Choose the interpreter where you installed packages

Run again

.
