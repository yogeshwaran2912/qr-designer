# QR ART STUDIO – Transform Images into Scannable QR Artwork

An artistic image-based QR code generation application that integrates genuine, standards-compliant QR codes into user illustrations and photography while guaranteeing 100% optical scannability using independent multi-engine verification.

---

## 🌟 Key Features

1. **Computer Vision Image Analysis**:
   - Analyzes dimensions, aspect ratio, and luminance distribution.
   - Computes RMS contrast and pixel distribution (dark, midtone, bright).
   - Extracts Canny edge density to determine visual complexity.
   - Extracts a 5-color dominant palette via K-Means clustering with interactive click-to-tint module coloring.
   - Generates OpenCV Magma Luminance Heatmaps and Edge Complexity maps.

2. **Genuine & Standards-Compliant QR Codes**:
   - Generates genuine QR codes encoding any valid URL.
   - Employs Error Correction Level H (30% data recovery) by default (with options for Q, M, and L).
   - Preserves finder pattern geometry (1:1:3:1:1 ratio), timing patterns, and alignment patterns.

3. **6 Distinctive Artistic Integration Styles**:
   - **Classic Artistic QR**: Balanced colorized integration with crisp finder eyes.
   - **Image-Blended QR**: Luminance-aware soft fusion preserving natural illustration lighting.
   - **Dark Module Overlay**: Deep obsidian/charcoal modules framing the artwork.
   - **Transparent QR Artwork**: Maximum illustration visibility with subtle scannable sampling cores.
   - **High-Contrast QR**: Punchy shadows & boosted highlights for long-distance recognition.
   - **Creative Fantasy QR**: Inspired by fantasy castle artwork (`house1.png`) with masonry rhythm and enchanted lighting.

4. **Multi-Engine Scannability Verification & Self-Healing Remedy Loop**:
   - Scans generated images using independent decoders (`zxing-cpp` Google ZXing port & `cv2.QRCodeDetector`).
   - Verifies that the decoded URL matches the user URL exactly.
   - If validation fails, an automatic remedy loop progressively optimizes contrast, opacity, and version until verified scannable.
   - Never presents an artwork as successful unless verified scannable.

5. **Modern Glassmorphic UI/UX**:
   - Dark navy background with purple and cyan gradient accents.
   - Interactive Before/After split comparison slider.
   - Drag-and-drop image upload with auto-detection of images in the `input/` folder.
   - Instant export options: Lossless PNG and High-Quality JPG.
   - Automatic saving to `output/generated_qr.png`.

---

## 📁 Directory Structure

```
house/
├── input/
│   └── house1.png             # Reference fantasy castle illustration
├── output/
│   ├── generated_qr.png       # Primary generated QR artwork
│   ├── generated_qr.jpg       # High-quality JPG export
│   ├── analysis_heatmap.png   # OpenCV luminance heatmap
│   └── analysis_edges.png     # OpenCV edge complexity map
├── assets/                    # Assets and icons
├── qr_art_engine.py           # Core CV & artistic QR generation engine
├── qr_validator.py            # Independent multi-engine QR validator
├── app.py                     # Flask REST API & web server
├── run.py                     # Application launcher
├── templates/
│   └── index.html             # Glassmorphism frontend
└── static/
    ├── css/
    │   └── style.css          # Dark navy, purple/cyan glassmorphic styles
    └── js/
        └── app.js             # Interactive sliders, split comparison, API calls
```

---

## 🚀 Getting Started

### Prerequisites

Python 3.10+ with the following packages installed:
```bash
pip install opencv-python pillow numpy qrcode zxing-cpp flask flask-cors amzqr
```

### Running the Application

Execute the runner script:
```bash
python run.py
```
Or start with automatic browser launch:
```bash
python run.py --open
```

Open your browser at:
```
http://127.0.0.1:5000
```

---

## 🎨 Application Workflow

1. **Step 1 – Image Input**:
   - Drag and drop any PNG, JPG, JPEG, or WEBP image, or click on the pre-loaded `house1.png` fantasy castle preset.
2. **Step 2 – Image Analysis**:
   - View real-time computer vision metrics, dominant color palette chips, and luminance/edge diagnostic maps.
3. **Step 3 – URL Input**:
   - Type or paste your destination URL (e.g. `https://www.google.com`), or select one of the quick preset chips.
4. **Step 4 – Style Selection**:
   - Choose one of the 6 artistic integration styles.
5. **Step 5 – Fine-Tuning**:
   - Adjust QR opacity, contrast, brightness, module tint, and ECC level.
6. **Step 6 – Generation & Validation**:
   - Click **Generate Artistic QR Artwork**. The engine builds the QR code, integrates the artwork, runs independent decoding validation via ZXing-CPP, and displays the scannability verification badge.
7. **Step 7 – Output & Comparison**:
   - Drag the interactive Before/After slider to inspect the blend against the original illustration.
   - Download the artwork as PNG or JPG.
