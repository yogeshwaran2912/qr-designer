"""
QR Validation Module
Provides independent multi-engine QR decoding and verification.
Engines:
1. zxing-cpp (Google ZXing C++ port - standard QR engine used by mobile scanners)
2. cv2.QRCodeDetector (OpenCV Computer Vision QR detector)
"""

import os
from typing import Dict, Any, Optional
import numpy as np
from PIL import Image
import cv2
import zxingcpp


class QRValidator:
    """Independent multi-engine QR code validator."""

    def __init__(self):
        self.cv2_detector = cv2.QRCodeDetector()

    def validate(self, image_input, expected_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate and decode a QR code from a file path, PIL Image, or numpy array.
        
        Args:
            image_input: File path (str), PIL.Image.Image, or np.ndarray
            expected_url: Optional expected URL to verify exact match
            
        Returns:
            Dict containing validation results:
            - is_detected: bool
            - decoded_url: str or None
            - matches_expected: bool
            - engine_used: str or None
            - status: "SUCCESS" | "FAILED"
            - details: str
        """
        pil_img = None
        cv_img = None

        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                return {
                    "is_detected": False,
                    "decoded_url": None,
                    "matches_expected": False,
                    "engine_used": None,
                    "status": "FAILED",
                    "details": f"File does not exist: {image_input}"
                }
            pil_img = Image.open(image_input).convert("RGB")
            cv_img = cv2.imread(image_input)
        elif isinstance(image_input, Image.Image):
            pil_img = image_input.convert("RGB")
            cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, np.ndarray):
            cv_img = image_input
            if len(cv_img.shape) == 2:
                pil_img = Image.fromarray(cv_img)
            else:
                pil_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
        else:
            return {
                "is_detected": False,
                "decoded_url": None,
                "matches_expected": False,
                "engine_used": None,
                "status": "FAILED",
                "details": "Unsupported image format"
            }

        # 1. Primary Engine: zxing-cpp
        decoded_text = None
        engine_used = None

        try:
            results = zxingcpp.read_barcodes(pil_img)
            if results:
                for r in results:
                    if r.text and len(r.text.strip()) > 0:
                        decoded_text = r.text.strip()
                        engine_used = "ZXing-CPP (Google ZXing Engine)"
                        break
        except Exception as e:
            pass

        # 2. Secondary Engine: OpenCV QRCodeDetector (if zxing didn't catch it)
        if not decoded_text and cv_img is not None:
            try:
                val, points, _ = self.cv2_detector.detectAndDecode(cv_img)
                if val and len(val.strip()) > 0:
                    decoded_text = val.strip()
                    engine_used = "OpenCV QRCodeDetector"
            except Exception as e:
                pass

        # 3. Third Fallback: Grayscale / Contrast-enhanced scan
        if not decoded_text and cv_img is not None:
            try:
                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                # Otsu thresholding
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                results = zxingcpp.read_barcodes(Image.fromarray(thresh))
                if results and results[0].text:
                    decoded_text = results[0].text.strip()
                    engine_used = "ZXing-CPP (Adaptive Binarization)"
            except Exception:
                pass

        is_detected = decoded_text is not None and len(decoded_text) > 0
        matches_expected = True

        if expected_url:
            exp = expected_url.strip()
            # Normalize trailing slashes for comparison if identical host/path
            exp_clean = exp.rstrip("/")
            dec_clean = (decoded_text or "").rstrip("/")
            matches_expected = is_detected and (dec_clean == exp_clean or decoded_text == exp)

        status = "SUCCESS" if (is_detected and matches_expected) else "FAILED"

        details = ""
        if not is_detected:
            details = "No QR code pattern could be detected by independent decoders."
        elif expected_url and not matches_expected:
            details = f"QR code detected but decoded URL ({decoded_text}) does not match expected URL ({expected_url})."
        else:
            details = f"Verified scannable via {engine_used}."

        return {
            "is_detected": is_detected,
            "decoded_url": decoded_text,
            "matches_expected": matches_expected,
            "engine_used": engine_used,
            "status": status,
            "details": details
        }


# Global singleton instance
validator = QRValidator()
