"""
QR Art Studio - Core Computer Vision & Artistic QR Generation Engine
Integrates OpenCV, Pillow, NumPy, and qrcode to transform user images
into scannable artistic QR artworks across 6 distinctive visual styles.
"""

import os
import time
import base64
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
from PIL import Image, ImageEnhance, ImageChops, ImageFilter, ImageOps
import cv2
from amzqr import amzqr

from qr_validator import validator


class QRArtEngine:
    """Core engine for computer vision analysis and artistic QR synthesis."""

    STYLES = {
        "classic": {
            "name": "Classic Artistic QR",
            "desc": "Clean, balanced integration with crisp finder eyes and vibrant image coloring."
        },
        "image_blended": {
            "name": "Image-Blended QR",
            "desc": "Luminance-aware blend where modules softly fuse into the illustration's natural lighting."
        },
        "dark_overlay": {
            "name": "Dark Module Overlay",
            "desc": "Deep obsidian/charcoal modules with enhanced edges, naturally framing the artwork."
        },
        "transparent": {
            "name": "Transparent QR Artwork",
            "desc": "Maximum artwork visibility with subtle, high-clarity sampling cores for instant scanning."
        },
        "high_contrast": {
            "name": "High-Contrast QR",
            "desc": "Punchy shadows, luminous highlights, and sharpened details for high-distance readability."
        },
        "fantasy": {
            "name": "Creative Fantasy QR",
            "desc": "Inspired by fantasy castle artwork: rich stone tones, mystical lighting, and architectural rhythm."
        }
    }

    def __init__(self, output_dir: str = "output", assets_dir: str = "assets"):
        self.output_dir = output_dir
        self.assets_dir = assets_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze an image using OpenCV and Pillow.
        Extracts dimensions, luminance distribution, contrast (RMS),
        edge complexity, and dominant 5-color palette.
        Also generates diagnostic visual heatmaps.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")

        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            raise ValueError(f"Could not read image at {image_path}")

        h, w, c = img_bgr.shape
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # 1. Dimensions & Aspect Ratio
        aspect_ratio = round(w / h, 2)
        total_pixels = gray.size

        # 2. Luminance & Contrast
        mean_lum = float(np.mean(gray))
        std_lum = float(np.std(gray))  # RMS Contrast
        min_lum = int(np.min(gray))
        max_lum = int(np.max(gray))

        dark_pct = float(np.sum(gray < 64) / total_pixels * 100)
        mid_pct = float(np.sum((gray >= 64) & (gray <= 192)) / total_pixels * 100)
        bright_pct = float(np.sum(gray > 192) / total_pixels * 100)

        # 3. Edge Complexity (Canny)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = float(np.sum(edges > 0) / total_pixels * 100)

        # 4. Dominant Color Palette (K-Means Clustering)
        pixels = img_bgr.reshape(-1, 3).astype(np.float32)
        k = 5
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 15, 1.0)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 3, cv2.KMEANS_PP_CENTERS)

        counts = np.bincount(labels.flatten())
        palette = []
        for i in range(k):
            b, g, r = centers[i].astype(int)
            b = max(0, min(255, int(b)))
            g = max(0, min(255, int(g)))
            r = max(0, min(255, int(r)))
            hex_code = f"#{r:02x}{g:02x}{b:02x}"
            pct = round(float(counts[i]) / total_pixels * 100, 1)
            palette.append({
                "hex": hex_code,
                "rgb": [r, g, b],
                "percent": pct
            })
        palette.sort(key=lambda x: x["percent"], reverse=True)

        # 5. Smart Recommendation
        recommended_style = "fantasy"
        reason = "Well-balanced artwork with intricate illustration details."
        if mean_lum < 85:
            recommended_style = "high_contrast"
            reason = "Dark overall scene; high contrast will boost module legibility."
        elif bright_pct > 35:
            recommended_style = "dark_overlay"
            reason = "Bright highlight regions; dark module overlay provides strong separation."
        elif edge_density > 18:
            recommended_style = "fantasy"
            reason = "Rich architectural or textured lines; ideal for Creative Fantasy QR styling."
        else:
            recommended_style = "image_blended"
            reason = "Smooth color transitions; Image-Blended QR maintains full color fidelity."

        # 6. Generate Diagnostic Visual Maps
        # Luminance Heatmap (Magma)
        heatmap = cv2.applyColorMap(gray, cv2.COLORMAP_MAGMA)
        heatmap_path = os.path.join(self.output_dir, "analysis_heatmap.png")
        cv2.imwrite(heatmap_path, heatmap)

        # Edge Map (Inverted for aesthetic display)
        edges_inv = 255 - edges
        edge_colored = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
        # Tint edges with purple cyan neon
        edge_colored[edges > 0] = [212, 182, 6]  # Cyan in BGR
        edge_path = os.path.join(self.output_dir, "analysis_edges.png")
        cv2.imwrite(edge_path, edge_colored)

        return {
            "width": w,
            "height": h,
            "aspect_ratio": aspect_ratio,
            "mean_brightness": round(mean_lum, 1),
            "min_lum": min_lum,
            "max_lum": max_lum,
            "contrast_rms": round(std_lum, 1),
            "dark_pct": round(dark_pct, 1),
            "mid_pct": round(mid_pct, 1),
            "bright_pct": round(bright_pct, 1),
            "edge_density": round(edge_density, 1),
            "palette": palette,
            "recommended_style": recommended_style,
            "recommendation_reason": reason,
            "heatmap_path": heatmap_path,
            "edge_path": edge_path
        }

    def _hex_to_rgb(self, hex_str: str) -> Tuple[int, int, int]:
        """Convert hex color string (#rrggbb) to RGB tuple."""
        hex_str = hex_str.lstrip("#")
        if len(hex_str) == 3:
            hex_str = "".join([c * 2 for c in hex_str])
        if len(hex_str) != 6:
            return (15, 23, 42)
        try:
            return tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))
        except Exception:
            return (15, 23, 42)

    def generate(
        self,
        image_path: str,
        url: str,
        style: str = "fantasy",
        opacity: float = 0.85,
        contrast: float = 1.15,
        brightness: float = 1.05,
        module_color: str = "#0f172a",
        error_correction: str = "H",
        version: Optional[int] = None,
        save_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an artistic QR code integrated with the user's image.
        Executes automatic verification and self-healing remedy loop if needed.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Input image not found: {image_path}")

        url = url.strip()
        if not url:
            raise ValueError("URL cannot be empty.")

        style = style.lower()
        if style not in self.STYLES:
            style = "fantasy"

        level = error_correction.upper()
        if level not in ("L", "M", "Q", "H"):
            level = "H"

        target_version = version if (version and 1 <= version <= 40) else 5

        # Ensure base amzqr runs with sanitized inputs
        # Generate raw artistic blend
        timestamp = int(time.time())
        temp_filename = f"art_temp_{timestamp}_{style}.png"
        final_filename = save_name or "generated_qr.png"
        final_path = os.path.join(self.output_dir, final_filename)

        # Loop with auto-remedy if validation fails
        cur_contrast = contrast
        cur_brightness = brightness
        cur_opacity = opacity
        cur_version = target_version
        attempt = 0
        max_attempts = 4
        validation_result = None

        while attempt < max_attempts:
            attempt += 1
            try:
                # 1. Base generation via AMZQR with verified geometric mask
                actual_ver, actual_ecl, raw_qr_path = amzqr.run(
                    url,
                    version=cur_version,
                    level=level,
                    picture=image_path,
                    colorized=True,
                    contrast=cur_contrast,
                    brightness=cur_brightness,
                    save_name=temp_filename,
                    save_dir=self.output_dir
                )

                # 2. Post-processing for chosen style
                raw_img = Image.open(raw_qr_path).convert("RGBA")
                orig_bg = Image.open(image_path).convert("RGBA").resize(raw_img.size, Image.Resampling.LANCZOS)
                rgb_mod_color = self._hex_to_rgb(module_color)

                styled_img = self._apply_style_postprocessing(
                    base_qr=raw_img,
                    orig_bg=orig_bg,
                    style=style,
                    opacity=cur_opacity,
                    module_color=rgb_mod_color,
                    contrast=cur_contrast,
                    brightness=cur_brightness
                )

                # Preserve integer module geometry & add clean white quiet zone for optical camera detection
                raw_w, raw_h = styled_img.size
                margin = max(40, int(raw_w * 0.05))
                final_res = Image.new("RGB", (raw_w + 2 * margin, raw_h + 2 * margin), (255, 255, 255))
                final_res.paste(styled_img.convert("RGB"), (margin, margin))
                final_res.save(final_path, quality=98)

                # Save timestamped copy in output
                timestamped_name = f"qr_{style}_{timestamp}.png"
                timestamped_path = os.path.join(self.output_dir, timestamped_name)
                final_res.save(timestamped_path, quality=95)

                # Also save High-Quality JPG
                jpg_filename = os.path.splitext(final_filename)[0] + ".jpg"
                jpg_path = os.path.join(self.output_dir, jpg_filename)
                final_res.save(jpg_path, quality=95)

                # Clean up temp file
                if os.path.exists(raw_qr_path):
                    try:
                        os.remove(raw_qr_path)
                    except Exception:
                        pass

                # 3. QR Validation (Independent Decoders)
                validation_result = validator.validate(final_path, expected_url=url)

                if validation_result["status"] == "SUCCESS":
                    break

                # Self-healing remedy adjustments for next attempt
                if attempt == 1:
                    cur_contrast = min(2.5, cur_contrast + 0.25)
                    cur_opacity = min(1.0, cur_opacity + 0.1)
                elif attempt == 2:
                    cur_contrast = min(2.5, cur_contrast + 0.2)
                    cur_brightness = max(0.9, cur_brightness - 0.1)
                    cur_version = min(40, cur_version + 2)
                elif attempt == 3:
                    cur_opacity = 0.95
                    cur_contrast = 1.4

            except Exception as e:
                if attempt >= max_attempts:
                    raise RuntimeError(f"QR generation failed: {str(e)}")
                cur_version = min(40, cur_version + 2)

        return {
            "status": validation_result["status"] if validation_result else "FAILED",
            "is_valid": validation_result["status"] == "SUCCESS" if validation_result else False,
            "decoded_url": validation_result["decoded_url"] if validation_result else None,
            "engine_used": validation_result["engine_used"] if validation_result else None,
            "validation_details": validation_result["details"] if validation_result else "Validation incomplete",
            "output_path": final_path,
            "output_filename": final_filename,
            "jpg_path": jpg_path,
            "timestamped_path": timestamped_path,
            "style": style,
            "style_name": self.STYLES[style]["name"],
            "version": actual_ver if "actual_ver" in locals() else target_version,
            "level": level,
            "attempts": attempt,
            "url": url
        }

    def _apply_style_postprocessing(
        self,
        base_qr: Image.Image,
        orig_bg: Image.Image,
        style: str,
        opacity: float,
        module_color: Tuple[int, int, int],
        contrast: float,
        brightness: float
    ) -> Image.Image:
        """Apply specialized styling transformations for each of the 6 artistic styles."""
        
        # 1. Classic Artistic QR
        if style == "classic":
            # Clean standard presentation with slight module color tinting if not default
            if module_color != (15, 23, 42):
                base_qr = self._tint_dark_modules(base_qr, module_color)
            return base_qr

        # 2. Image-Blended QR
        elif style == "image_blended":
            # Luminance-aware blend: dark modules subtly multiply into image
            # Blend base_qr with orig_bg at selected opacity
            blended = Image.blend(orig_bg, base_qr, max(0.72, min(0.92, opacity)))
            if module_color != (15, 23, 42):
                blended = self._tint_dark_modules(blended, module_color, strength=0.5)
            return blended

        # 3. Dark Module Overlay
        elif style == "dark_overlay":
            # Deepen dark modules, enhance contrast and clarity
            tinted = self._tint_dark_modules(base_qr, module_color)
            enh = ImageEnhance.Contrast(tinted.convert("RGB")).enhance(1.25)
            enh = ImageEnhance.Sharpness(enh).enhance(1.2)
            return enh.convert("RGBA")

        # 4. Transparent QR Artwork
        elif style == "transparent":
            # Maximum illustration visibility; blend original background with QR
            # Keep opacity between 0.75 and 0.85 to guarantee scannability
            safe_opacity = max(0.76, min(0.88, opacity))
            blended = Image.blend(orig_bg, base_qr, safe_opacity)
            return blended

        # 5. High-Contrast QR
        elif style == "high_contrast":
            # Punchy shadows, luminous highlights, sharpened finder eyes
            tinted = self._tint_dark_modules(base_qr, module_color)
            enh = ImageEnhance.Contrast(tinted.convert("RGB")).enhance(1.35)
            enh = ImageEnhance.Sharpness(enh).enhance(1.3)
            return enh.convert("RGBA")

        # 6. Creative Fantasy QR
        elif style == "fantasy":
            # Specially tailored for fantasy castle / mythical artwork
            # Tint dark modules with rich deep indigo / obsidian
            fantasy_dark = (
                min(255, int(module_color[0] * 0.9)),
                min(255, int(module_color[1] * 0.95)),
                min(255, int(module_color[2] * 1.15))
            )
            tinted = self._tint_dark_modules(base_qr, fantasy_dark)
            # Enhance color saturation and gentle contrast for an enchanted aesthetic
            enh_color = ImageEnhance.Color(tinted.convert("RGB")).enhance(1.2)
            enh_cont = ImageEnhance.Contrast(enh_color).enhance(1.18)
            enh_sharp = ImageEnhance.Sharpness(enh_cont).enhance(1.15)
            return enh_sharp.convert("RGBA")

        return base_qr

    def _tint_dark_modules(
        self,
        img: Image.Image,
        target_color: Tuple[int, int, int],
        strength: float = 0.85
    ) -> Image.Image:
        """Tint dark QR pixels towards target_color while preserving scannable luminance."""
        arr = np.array(img).astype(np.float32)
        # Compute grayscale luminance
        lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
        dark_mask = lum < 110

        for ch in range(3):
            orig_ch = arr[:, :, ch]
            tinted_ch = orig_ch * (1.0 - strength) + target_color[ch] * strength
            arr[dark_mask, ch] = tinted_ch[dark_mask]

        arr = np.clip(arr, 0, 255).astype(np.uint8)
        return Image.fromarray(arr, "RGBA" if img.mode == "RGBA" else "RGB")


# Global singleton instance
engine = QRArtEngine()
