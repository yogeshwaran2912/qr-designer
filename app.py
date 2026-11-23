"""
QR Art Studio - Flask Web Application
Provides RESTful APIs and UI serving for the Artistic Image-Based QR Code Generator.
"""

import os
import re
import time
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from qr_art_engine import engine
from qr_validator import validator

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def is_valid_url(url: str) -> bool:
    if not url:
        return False
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/inputs", methods=["GET"])
def list_inputs():
    """List all available images in the input/ folder."""
    files = []
    if os.path.exists(INPUT_DIR):
        for fname in sorted(os.listdir(INPUT_DIR)):
            if allowed_file(fname):
                fpath = os.path.join(INPUT_DIR, fname)
                try:
                    size_bytes = os.path.getsize(fpath)
                    files.append({
                        "filename": fname,
                        "size_kb": round(size_bytes / 1024, 1),
                        "url": f"/api/file/input/{fname}",
                        "is_sample": fname.startswith("house")
                    })
                except Exception:
                    pass
    return jsonify({"success": True, "files": files})


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Upload an image file into the input/ directory."""
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Unsupported file format. Please upload PNG, JPG, JPEG, or WEBP."}), 400

    filename = secure_filename(file.filename)
    # Avoid collisions
    base, ext = os.path.splitext(filename)
    unique_filename = f"{base}_{int(time.time())}{ext}"
    save_path = os.path.join(INPUT_DIR, unique_filename)
    file.save(save_path)

    # Automatically analyze uploaded image
    try:
        analysis = engine.analyze_image(save_path)
    except Exception as e:
        analysis = None

    return jsonify({
        "success": True,
        "filename": unique_filename,
        "file_url": f"/api/file/input/{unique_filename}",
        "analysis": analysis
    })


@app.route("/api/analyze", methods=["POST"])
def analyze_image_endpoint():
    """Run OpenCV and Pillow computer vision analysis on selected input image."""
    data = request.get_json() or {}
    filename = data.get("filename")
    if not filename:
        return jsonify({"success": False, "error": "Filename is required"}), 400

    filepath = os.path.join(INPUT_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"success": False, "error": f"File '{filename}' not found in input folder"}), 404

    try:
        analysis = engine.analyze_image(filepath)
        analysis["heatmap_url"] = "/api/file/output/analysis_heatmap.png"
        analysis["edge_url"] = "/api/file/output/analysis_edges.png"
        return jsonify({"success": True, "analysis": analysis})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/generate", methods=["POST"])
def generate_qr():
    """Generate artistic QR artwork and validate scannability."""
    data = request.get_json() or {}
    filename = data.get("filename")
    url = data.get("url", "").strip()
    style = data.get("style", "fantasy")
    opacity = float(data.get("opacity", 0.85))
    contrast = float(data.get("contrast", 1.15))
    brightness = float(data.get("brightness", 1.05))
    module_color = data.get("module_color", "#0f172a")
    error_correction = data.get("error_correction", "H")
    version = data.get("version")
    if version:
        try:
            version = int(version)
        except Exception:
            version = None

    # URL Validation
    if not url:
        return jsonify({"success": False, "error": "URL is required."}), 400

    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    if not is_valid_url(url):
        return jsonify({"success": False, "error": "Please enter a valid website URL (e.g. https://www.google.com)."}), 400

    if not filename:
        return jsonify({"success": False, "error": "Please select or upload an image."}), 400

    filepath = os.path.join(INPUT_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"success": False, "error": f"Image file not found: {filename}"}), 404

    start_time = time.time()
    try:
        gen_result = engine.generate(
            image_path=filepath,
            url=url,
            style=style,
            opacity=opacity,
            contrast=contrast,
            brightness=brightness,
            module_color=module_color,
            error_correction=error_correction,
            version=version,
            save_name="generated_qr.png"
        )
        elapsed = round(time.time() - start_time, 2)

        return jsonify({
            "success": True,
            "data": {
                "status": gen_result["status"],
                "is_valid": gen_result["is_valid"],
                "decoded_url": gen_result["decoded_url"],
                "engine_used": gen_result["engine_used"],
                "validation_details": gen_result["validation_details"],
                "qr_image_url": f"/api/file/output/generated_qr.png?t={int(time.time())}",
                "download_png_url": "/api/download/generated_qr.png",
                "download_jpg_url": "/api/download/generated_qr.jpg",
                "original_image_url": f"/api/file/input/{filename}",
                "style": gen_result["style"],
                "style_name": gen_result["style_name"],
                "version": gen_result["version"],
                "level": gen_result["level"],
                "attempts": gen_result["attempts"],
                "elapsed_seconds": elapsed,
                "url": url
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/validate_url", methods=["POST"])
def validate_url_endpoint():
    """Validate a URL string."""
    data = request.get_json() or {}
    url = data.get("url", "").strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    valid = is_valid_url(url)
    return jsonify({
        "valid": valid,
        "formatted_url": url if valid else None,
        "message": "Valid URL" if valid else "Invalid URL scheme or format"
    })


@app.route("/api/file/<folder>/<filename>")
def serve_file(folder, filename):
    """Safely serve images from input, output, or assets folder."""
    folder = folder.lower()
    if folder == "input":
        target_dir = INPUT_DIR
    elif folder == "output":
        target_dir = OUTPUT_DIR
    elif folder == "assets":
        target_dir = ASSETS_DIR
    else:
        return jsonify({"error": "Invalid directory"}), 400

    filename = secure_filename(filename)
    return send_from_directory(target_dir, filename)


@app.route("/api/download/<filename>")
def download_file(filename):
    """Download generated output file as attachment."""
    filename = secure_filename(filename)
    fpath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(fpath):
        return jsonify({"error": "File not found"}), 404
    return send_file(fpath, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
