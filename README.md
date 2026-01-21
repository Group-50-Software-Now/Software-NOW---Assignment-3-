# AI Image Editor – HIT137 Group Assignment 3
📌 Overview

This project is a desktop Image Editing Application developed as part of HIT137 – Software Now (Group Assignment 3).
The application demonstrates the practical use of Object-Oriented Programming (OOP) concepts, Tkinter GUI development, and image processing using OpenCV.

The goal of the project is to design a clean, user-friendly desktop tool that allows users to load an image, apply multiple image processing effects, and save the results, while maintaining good software structure and code quality.

🛠 Technologies Used

Python 3

Tkinter – GUI development

OpenCV (cv2) – Image processing

NumPy – Image data handling

Pillow (PIL) – Image display support in Tkinter

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
🖼 Image Processing Functions (OpenCV)

The application supports the following image operations:

Grayscale conversion

Gaussian blur (adjustable)

Edge detection (Canny)

Brightness adjustment

Contrast adjustment

Image rotation (90°, 180°, 270°)

Image flip (horizontal / vertical)

Resize / scale by percentage

All processing is handled through a dedicated processing class to keep the GUI logic clean and modular.

🧩 GUI Features (Tkinter)

Main application window with proper sizing

Menu bar:

File → Open, Save, Save As, Exit

Edit → Undo, Redo

Image display area using a Canvas

Control panel with buttons and sliders

Live slider previews for blur, brightness, and contrast

Status bar showing:

File name

Image dimensions

Undo/Redo availability

Last performed action

Confirmation and error dialogs for better user experience

🧠 Object-Oriented Design

The project is structured using multiple classes to clearly demonstrate OOP concepts:

ImageEditorApp

Manages the GUI and user interactions

ImageProcessor

Handles all OpenCV image processing logic

HistoryManager

Manages undo and redo operations using internal stacks

The design demonstrates:

Encapsulation

Constructors

Instance and class attributes

Method-based interaction between classes

Clean separation of responsibilities

▶ How to Run the Application
1️⃣ Install required libraries
pip install -r requirements.txt

2️⃣ Run the application
python main.py

👥 Group Work & GitHub Usage

This project is maintained in a public GitHub repository

All group members are added as collaborators

Commits reflect continuous development from start to submission

GitHub is used to track progress, changes, and teamwork

The repository link is provided in github_link.txt as required.

✅ Notes

The application supports common image formats: JPG, PNG, BMP

Images are processed internally using OpenCV (BGR format) and converted to RGB only for display

Undo/Redo functionality allows safe experimentation with image effects

Code is documented with clear docstrings and comments for readability

📌 Conclusion

This project demonstrates a complete desktop application built using Python, combining GUI development, image processing, and object-oriented programming principles.
The focus was on writing clean, maintainable code while delivering all required functionality in a user-friendly interface.
