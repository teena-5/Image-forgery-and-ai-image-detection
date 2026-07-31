"""
Noise Pattern Analysis Module
Analyzes noise distribution and consistency across the image to detect
signs of AI generation or editing.
"""

import cv2
import numpy as np


def analyze_noise(image_path):
    """
    Analyze noise patterns in an image to determine authenticity.

    Computes Laplacian variance (overall noise level), block-level noise
    consistency, and high-frequency noise uniformity to classify the image.

    Args:
        image_path (str): Path to the input image.

    Returns:
        dict: Analysis results containing:
            - verdict (str): 'REAL', 'EDITED', or 'AI_GENERATED'
            - confidence (float): Confidence score (0-100)
            - metrics (dict): Detailed noise statistics
    """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Overall noise level via Laplacian variance
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    noise_level = float(laplacian.var())

    # Block-level noise analysis (64x64 blocks)
    h, w = gray.shape
    block_size = 64
    block_variances = []

    for y in range(0, h - block_size + 1, block_size):
        for x in range(0, w - block_size + 1, block_size):
            block = gray[y : y + block_size, x : x + block_size]
            block_lap = cv2.Laplacian(block, cv2.CV_64F)
            block_variances.append(float(block_lap.var()))

    block_variances = np.array(block_variances)
    block_mean = float(np.mean(block_variances)) if len(block_variances) > 0 else 1.0
    block_std = float(np.std(block_variances)) if len(block_variances) > 0 else 0.0

    # Noise consistency = coefficient of variation (std / mean)
    if block_mean > 0:
        noise_consistency = block_std / block_mean
    else:
        noise_consistency = 0.0

    # High-frequency noise analysis
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    diff = cv2.subtract(gray, blurred)
    diff_float = diff.astype(np.float64)
    diff_mean = float(np.mean(diff_float)) if np.mean(diff_float) > 0 else 1.0
    diff_std = float(np.std(diff_float))

    # Noise uniformity = coefficient of variation of high-freq difference
    if diff_mean > 0:
        noise_uniformity = diff_std / diff_mean
    else:
        noise_uniformity = 0.0

    # Verdict logic
    if noise_level < 50 and noise_consistency < 0.5:
        verdict = "AI_GENERATED"
        confidence = 70 + (0.5 - noise_consistency) * 40
    elif noise_consistency > 1.5:
        verdict = "EDITED"
        confidence = 60 + min(30, noise_consistency * 10)
    elif noise_level < 100 and noise_consistency < 0.8:
        verdict = "AI_GENERATED"
        confidence = 55.0
    else:
        verdict = "REAL"
        confidence = 60 + min(30, noise_level * 0.05)

    # Cap confidence at 95
    confidence = min(95.0, confidence)

    return {
        "verdict": verdict,
        "confidence": round(confidence, 2),
        "metrics": {
            "noise_level": round(noise_level, 4),
            "noise_consistency": round(noise_consistency, 4),
            "noise_uniformity": round(noise_uniformity, 4),
            "block_noise_mean": round(block_mean, 4),
            "block_noise_std": round(block_std, 4),
            "num_blocks": len(block_variances),
        },
    }
