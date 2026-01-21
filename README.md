🖼️ AI Image Editor

HIT137 – Software Now | Group Assignment 3

📌 Project Overview

This project is a desktop image editing application developed for HIT137 – Software Now (Group Assignment 3).
The application demonstrates practical understanding of:

Object-Oriented Programming (OOP)

Tkinter GUI development

Image processing using OpenCV

Version control and collaboration using GitHub

The focus of the project is to build a clean, user-friendly application while maintaining good software design, modular code structure, and readability.

🛠 Technologies Used

Python 3

Tkinter – Graphical User Interface

OpenCV (cv2) – Image processing

NumPy – Image data manipulation

Pillow (PIL) – Image rendering for Tkinter

GitHub – Version control and collaboration

📂 Project Structure
assigment 3/
│
├── app.py                # Main Tkinter GUI and application logic
├── image_processor.py    # OpenCV image processing operations
├── history_manager.py    # Undo / Redo functionality
├── main.py               # Application entry point
├── requirements.txt      # Required Python libraries
├── github_link.txt       # GitHub repository link
└── README.md             # Project documentation

🎯 Application Features
🖼 Image Processing (OpenCV)

The application supports the following image operations:

Grayscale conversion

Gaussian blur (adjustable intensity)

Edge detection (Canny algorithm)

Brightness adjustment

Contrast adjustment

Image rotation (90°, 180°, 270°)

Image flip (horizontal / vertical)

Resize / scale by percentage

All image processing logic is handled in a dedicated processing class, keeping the GUI code clean and maintainable.

🧩 Graphical User Interface (Tkinter)

The GUI includes all required elements:

Main application window with proper sizing

Menu bar:

File → Open, Save, Save As, Exit

Edit → Undo, Redo

Image display area using a Canvas

Control panel with buttons and sliders

Live slider previews for blur, brightness, and contrast

Status bar displaying:

File name

Image dimensions

Undo / Redo availability

Last performed action

Message boxes for errors, confirmations, and warnings

🧠 Object-Oriented Design

The application is structured using multiple classes to clearly demonstrate OOP principles:

Key Classes

ImageEditorApp

Manages the GUI and user interactions

ImageProcessor

Handles all OpenCV image processing logic

HistoryManager

Manages undo and redo functionality

OOP Concepts Demonstrated

Classes and objects

Constructors

Instance and class attributes

Encapsulation

Method-based class interaction

Clear separation of responsibilities

▶ How to Run the Application
1️⃣ Install Required Libraries
pip install -r requirements.txt

2️⃣ Run the Application
python main.py

👥 Group Work & GitHub Usage

The project is maintained in a public GitHub repository

All group members are added as collaborators

Commits show continuous development from start to submission

GitHub is used to track progress, collaboration, and contributions

The repository link is provided in github_link.txt as required.

📝 Notes

Supported image formats: JPG, PNG, BMP

Images are processed internally using OpenCV (BGR format)

Conversion to RGB is done only for display in Tkinter

Undo / Redo allows safe experimentation with image edits

Code is documented with clear, human-readable docstrings and comments

✅ Conclusion

This project demonstrates a complete Python desktop application that integrates GUI development, image processing, and object-oriented programming principles.
The focus was on producing clean, readable, and maintainable code while delivering all required functionality in a user-friendly interface.
