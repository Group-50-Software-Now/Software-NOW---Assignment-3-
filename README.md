# HIT137 – Software Now (Group Project)

This repository is created for the **group project** of the unit **HIT137 – Software Now** at **Charles Darwin University (CDU)**.

---

## Unit Information
- **Unit Code:** HIT137  
- **Unit Name:** Software Now  
- **Institution:** Charles Darwin University (CDU)  
- **Project Type:** Group Assignment  
- **Assessment:** Assignment 3  

---

## Team Members
- **Roman Bisural (CyberDevilSec1)** — S397541  
- **Suriya Sankar (suriya-sankar24)** — S397448  
- **Khushi (khushi-cdu)** — S398777  
- **Bittu Kumar Gupta (Iambittukumar)** — S397540  

---

## Project Overview
This project contains the solution for **Assignment 3** of HIT137.

The application is a **Python desktop Image Editor** developed using **Object-Oriented Programming (OOP)** and a **Tkinter GUI**, with image processing features powered by **OpenCV** and **Pillow**.  
It supports common editing operations (filters, adjustments, and transformations) and is structured for clear collaboration and version control using GitHub.

The purpose of this repository is to allow group members to **collaborate**, **share code**, and **manage assignment files** efficiently using GitHub.

---

## Key Features (Assignment 3)
- Open and display images
- Save edited images
- Image filters (e.g., Grayscale, Edge Detection)
- Adjustments using sliders (e.g., Brightness, Contrast, Blur if implemented)
- Transformations (Rotate 90°/180°/270°, Flip Horizontal/Vertical)
- User-friendly interface with sidebar controls and status updates
- Error handling for invalid images and save failures
- (Optional if implemented) Undo/Redo / History support

> Note: Feature list may vary depending on the final implemented version of the app.

---

## Repository Structure 

```text
📦 AI-Image-Editor/
│
├── main.py               # Entry point (starts the app)
├── app.py                # Full GUI + sidebar controls + status bar
├── image_processor.py    # OpenCV image processing logic
├── history_manager.py    # Undo/Redo system
└── README.md             # This file
```

## Tools & Technologies
- **Python**
- **Tkinter**
- **OpenCV (cv2)**
- **Pillow (PIL)**
- **NumPy**
- **GitHub**
- **Visual Studio Code (VS Code)**

---

## How to Run (Basic)

1. Clone the repository:
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the program:
 ```
python app.py

```

