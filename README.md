<p align="center">
  <h1 align="center">🔍 ForensicAI — Image Forgery Detection</h1>
  <p align="center">
    <em>A web application that detects image forgery using Error Level Analysis (ELA) and AI-generated image detection techniques.</em>
  </p>
</p>

---

## 📸 Screenshot

> _Screenshot placeholder — add a screenshot of the running application here._
>
> `![ForensicAI Screenshot](docs/screenshot.png)`

---

## 📖 Description

**ForensicAI** is a lightweight, browser-based image forensics tool that analyzes uploaded images and classifies them as **Authentic**, **Edited/Tampered**, or **AI-Generated**. It combines multiple detection techniques into an ensemble scoring pipeline to produce a confidence-weighted verdict — no GPU or cloud API required.

---

## ✨ Features

| Module | What it does |
|---|---|
| **Error Level Analysis (ELA)** | Re-compresses the image at a known JPEG quality and measures pixel-level differences to reveal tampered regions |
| **Metadata Analysis** | Inspects EXIF data for editing software signatures, missing camera info, and inconsistencies |
| **Noise Pattern Analysis** | Examines the image's noise residual for uniformity anomalies that indicate splicing or inpainting |
| **Frequency Domain Analysis** | Applies DCT/FFT transforms to detect unnatural frequency artifacts left by editing tools and AI generators |
| **Texture & Edge Analysis** | Measures local texture consistency and edge coherence to identify blending boundaries |
| **Ensemble Scoring** | Combines all module scores with configurable weights into a single classification verdict with confidence percentage |

---

## 🛠 Prerequisites

- **Python 3.8+** (3.10 or 3.11 recommended)
- **pip** (comes with Python)
- **VS Code** (recommended editor)

---

## 🚀 Setup Instructions (Windows)

### 1. Open a terminal in VS Code

Press `` Ctrl + ` `` or go to **Terminal → New Terminal**.

### 2. Navigate to the project folder

```bash
cd "C:\Users\Tanu's\OneDrive\Desktop\ImageForgeryDetection"
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

```bash
venv\Scripts\activate
```

> You should see `(venv)` at the beginning of your terminal prompt.

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

### 7. Open in your browser

Navigate to **[http://localhost:5000](http://localhost:5000)** and start analyzing images!

---

## 🧠 How It Works

### Error Level Analysis (ELA)
The image is re-saved as a JPEG at a known quality level (e.g., 90%). The pixel-by-pixel difference between the original and re-saved version is computed. Regions that were recently edited will show higher error levels because they haven't been through as many compression cycles.

### Metadata Analysis
EXIF metadata is parsed to look for tell-tale signs of manipulation — such as the presence of editing software tags (Photoshop, GIMP), missing camera model information, or date/time inconsistencies between creation and modification timestamps.

### Noise Pattern Analysis
Every digital camera leaves a unique noise fingerprint. This module extracts the noise residual using a denoising filter and checks for uniformity. Spliced or AI-generated regions often have a different noise profile than the rest of the image.

### Frequency Domain Analysis
A Discrete Cosine Transform (DCT) or Fast Fourier Transform (FFT) is applied to detect periodic artifacts. JPEG double-compression leaves characteristic peaks in the DCT histogram, while AI generators often produce unnaturally smooth frequency distributions.

### Texture & Edge Analysis
Local Binary Patterns (LBP) and edge detection filters (Laplacian, Canny) are used to measure texture consistency across the image. Tampered boundaries and AI-generated images often show abrupt changes in texture or unnaturally smooth edges.

### Ensemble Scoring
Each module produces an independent score. These scores are combined using a weighted average to produce a final classification:

| Classification | Description |
|---|---|
| ✅ **Authentic** | Image appears genuine with no significant signs of tampering |
| ⚠️ **Edited / Tampered** | Image shows signs of post-processing or regional manipulation |
| 🤖 **AI-Generated** | Image exhibits patterns consistent with AI/GAN generation |

---

## 🏗 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3, Flask |
| **Image Processing** | Pillow (PIL), OpenCV, NumPy, SciPy |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Deployment** | Local development server (Flask built-in) |

---

## 📁 Project Structure

```
image-forgery-detection/
├── app.py                  # Flask web server (entry point)
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── detection/              # Core detection modules
│   ├── __init__.py
│   ├── ela.py              # Error Level Analysis
│   ├── metadata.py         # EXIF metadata analysis
│   ├── noise.py            # Noise pattern analysis
│   ├── frequency.py        # Frequency domain analysis
│   ├── texture.py          # Texture & edge analysis
│   └── ensemble.py         # Ensemble scoring pipeline
├── templates/
│   └── index.html          # Main web interface
└── static/
    ├── css/                # Stylesheets
    ├── js/                 # Frontend scripts
    └── uploads/            # Uploaded images (auto-created)
```

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
