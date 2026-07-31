"""
Color and Texture Statistics Module
Analyzes edge density, color histogram kurtosis, saturation uniformity,
and texture smoothness to detect image manipulation or AI generation.
"""

import cv2
import numpy as np


def analyze_texture(image_path):
    """
    Analyze texture and color statistics of an image.

    Computes edge density via Sobel operators, per-channel histogram kurtosis,
    saturation uniformity in HSV space, and local variance-based texture
    smoothness to classify the image.

    Args:
        image_path (str): Path to the input image.

    Returns:
        dict: Analysis results containing:
            - verdict (str): 'REAL', 'EDITED', or 'AI_GENERATED'
            - confidence (float): Confidence score (0-100)
            - metrics (dict): Detailed texture and color statistics
    """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # --- Edge Density ---
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    edge_density = float(np.mean(edge_magnitude))
    edge_std = float(np.std(edge_magnitude))

    # --- Color Histogram Kurtosis ---
    kurtosis_values = []
    for channel in range(3):  # BGR channels
        hist = cv2.calcHist([image], [channel], None, [256], [0, 256])
        hist_normalized = hist.flatten() / hist.sum()

        # Compute kurtosis: E[(X - mu)^4] / sigma^4 - 3
        bins = np.arange(256)
        mu = np.sum(bins * hist_normalized)
        sigma = np.sqrt(np.sum(((bins - mu) ** 2) * hist_normalized))

        if sigma > 0:
            kurtosis = (
                np.sum(((bins - mu) ** 4) * hist_normalized) / (sigma**4)
            ) - 3
        else:
            kurtosis = 0.0

        kurtosis_values.append(float(kurtosis))

    avg_kurtosis = float(np.mean(kurtosis_values))

    # --- Saturation Analysis ---
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1].astype(np.float64)
    sat_mean = float(np.mean(saturation))
    sat_std = float(np.std(saturation))

    if sat_mean > 0:
        sat_uniformity = sat_std / sat_mean
    else:
        sat_uniformity = 0.0

    # --- Texture Smoothness (local variance) ---
    gray_float = gray.astype(np.float64)
    local_mean = cv2.blur(gray_float, (5, 5))
    local_sq_mean = cv2.blur(gray_float**2, (5, 5))
    local_variance = local_sq_mean - local_mean**2
    smoothness = float(np.mean(local_variance))

    # --- Verdict Logic ---
    if edge_density < 15 and smoothness < 200:
        verdict = "AI_GENERATED"
        confidence = 65 + (15 - edge_density) * 3
    elif avg_kurtosis > 10 and smoothness < 300:
        verdict = "AI_GENERATED"
        confidence = 60.0
    elif edge_std > edge_density * 2:
        verdict = "EDITED"
        confidence = 60.0
    else:
        verdict = "REAL"
        confidence = 60 + min(30, edge_density * 0.5)

    # Cap confidence at 95
    confidence = min(95.0, confidence)

    return {
        "verdict": verdict,
        "confidence": round(confidence, 2),
        "metrics": {
            "edge_density": round(edge_density, 4),
            "edge_std": round(edge_std, 4),
            "avg_kurtosis": round(avg_kurtosis, 4),
            "kurtosis_per_channel": [round(k, 4) for k in kurtosis_values],
            "saturation_mean": round(sat_mean, 4),
            "saturation_std": round(sat_std, 4),
            "saturation_uniformity": round(sat_uniformity, 4),
            "texture_smoothness": round(smoothness, 4),
        },
    }
