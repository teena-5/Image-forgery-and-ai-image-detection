"""
Error Level Analysis (ELA) Module
Detects image manipulation by analyzing JPEG compression artifacts.
Re-saves the image at a known quality and measures pixel-wise differences.
"""

from PIL import Image, ImageChops, ImageEnhance
import numpy as np
import os
import io


def perform_ela(image_path, quality=90):
    """
    Perform Error Level Analysis on an image.

    Opens the image, re-saves it at the specified JPEG quality level using
    an in-memory buffer, then computes the pixel-wise difference between
    the original and the re-compressed version.

    Args:
        image_path (str): Path to the input image.
        quality (int): JPEG re-compression quality (default 90).

    Returns:
        PIL.Image: Brightness-enhanced difference image highlighting ELA artifacts.
    """
    original = Image.open(image_path).convert("RGB")

    # Re-save at specified quality into an in-memory buffer
    buffer = io.BytesIO()
    original.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    resaved = Image.open(buffer)

    # Compute pixel-wise difference
    ela_image = ImageChops.difference(original, resaved)

    # Enhance brightness to make differences visible
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    scale = 255.0 / max_diff
    enhancer = ImageEnhance.Brightness(ela_image)
    ela_image = enhancer.enhance(scale)

    return ela_image


def analyze_ela(image_path, output_dir=None):
    """
    Analyze an image using Error Level Analysis and produce a verdict.

    Runs perform_ela, converts the result to a numpy array, and computes
    statistical metrics to determine whether the image has been edited.

    Args:
        image_path (str): Path to the input image.
        output_dir (str, optional): Directory to save the ELA visualization image.

    Returns:
        dict: Analysis results containing:
            - verdict (str): 'REAL' or 'EDITED'
            - confidence (float): Confidence score (0-100)
            - metrics (dict): Detailed ELA statistics
            - ela_image_path (str or None): Path to saved ELA image
    """
    ela_image = perform_ela(image_path)
    ela_array = np.array(ela_image, dtype=np.float64)

    # Compute metrics
    mean_error = float(np.mean(ela_array))
    std_error = float(np.std(ela_array))
    max_error = float(np.max(ela_array))

    # Percentage of pixels with high error (threshold = 128)
    threshold = 128
    high_error_pixels = float(np.sum(ela_array > threshold) / ela_array.size * 100)

    # Save ELA image if output_dir is provided
    ela_image_path = None
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        ela_image_path = os.path.join(output_dir, f"{base_name}_ela.png")
        ela_image.save(ela_image_path)

    # Verdict logic
    if std_error > 50 and high_error_pixels > 5:
        verdict = "EDITED"
        confidence = min(95, 50 + std_error * 0.5 + high_error_pixels * 2)
    elif mean_error > 40 or high_error_pixels > 3:
        verdict = "EDITED"
        confidence = min(80, 40 + mean_error * 0.5 + high_error_pixels * 3)
    else:
        verdict = "REAL"
        confidence = max(30, 80 - mean_error * 1.5)

    return {
        "verdict": verdict,
        "confidence": round(confidence, 2),
        "metrics": {
            "mean_error": round(mean_error, 4),
            "std_error": round(std_error, 4),
            "max_error": round(max_error, 4),
            "high_error_pixels_pct": round(high_error_pixels, 4),
        },
        "ela_image_path": ela_image_path,
    }
