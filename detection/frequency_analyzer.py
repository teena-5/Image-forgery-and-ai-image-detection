"""
FFT Frequency Analysis Module
Analyzes the frequency domain of an image using Fast Fourier Transform
to detect anomalies indicative of editing or AI generation.
"""

import cv2
import numpy as np


def analyze_frequency(image_path):
    """
    Analyze frequency domain characteristics of an image.

    Resizes the image to 512x512, applies FFT, and examines energy distribution
    across low, mid, and high frequency bands along with spectral flatness
    and peak detection.

    Args:
        image_path (str): Path to the input image.

    Returns:
        dict: Analysis results containing:
            - verdict (str): 'REAL', 'EDITED', or 'AI_GENERATED'
            - confidence (float): Confidence score (0-100)
            - metrics (dict): Detailed frequency statistics
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (512, 512))

    # Apply FFT
    f_transform = np.fft.fft2(image.astype(np.float64))
    f_shift = np.fft.fftshift(f_transform)
    magnitude = np.log1p(np.abs(f_shift))

    # Create radial distance map from center
    rows, cols = magnitude.shape
    center_row, center_col = rows // 2, cols // 2
    y_coords, x_coords = np.ogrid[:rows, :cols]
    distance = np.sqrt((y_coords - center_row) ** 2 + (x_coords - center_col) ** 2)
    max_radius = np.sqrt(center_row**2 + center_col**2)

    # Normalize distances
    normalized_distance = distance / max_radius

    # Create frequency band masks
    low_mask = normalized_distance < 0.2
    mid_mask = (normalized_distance >= 0.2) & (normalized_distance <= 0.6)
    high_mask = normalized_distance > 0.6

    # Compute energy in each band
    total_energy = float(np.sum(magnitude))
    if total_energy == 0:
        total_energy = 1.0

    low_energy = float(np.sum(magnitude[low_mask]))
    mid_energy = float(np.sum(magnitude[mid_mask]))
    high_energy = float(np.sum(magnitude[high_mask]))

    low_ratio = low_energy / total_energy
    mid_ratio = mid_energy / total_energy
    high_ratio = high_energy / total_energy

    # Spectral flatness: exp(mean(log(mag))) / mean(mag)
    mag_positive = magnitude[magnitude > 0]
    if len(mag_positive) > 0:
        spectral_flatness = float(
            np.exp(np.mean(np.log(mag_positive))) / np.mean(mag_positive)
        )
    else:
        spectral_flatness = 0.0

    # Peak detection: count pixels significantly above mean
    mag_mean = float(np.mean(magnitude))
    mag_std = float(np.std(magnitude))
    peak_threshold = mag_mean + 3 * mag_std
    peak_count = int(np.sum(magnitude > peak_threshold))
    peaks = peak_count / magnitude.size

    # Verdict logic
    if high_ratio < 0.15 and spectral_flatness > 0.6:
        verdict = "AI_GENERATED"
        confidence = 65 + (0.15 - high_ratio) * 200
    elif peaks > 0.01:
        verdict = "EDITED"
        confidence = 60 + min(30, peaks * 2000)
    elif high_ratio < 0.2:
        verdict = "AI_GENERATED"
        confidence = 55.0
    else:
        verdict = "REAL"
        confidence = 60 + high_ratio * 100

    # Cap confidence at 95
    confidence = min(95.0, confidence)

    return {
        "verdict": verdict,
        "confidence": round(confidence, 2),
        "metrics": {
            "low_freq_ratio": round(low_ratio, 4),
            "mid_freq_ratio": round(mid_ratio, 4),
            "high_freq_ratio": round(high_ratio, 4),
            "spectral_flatness": round(spectral_flatness, 4),
            "peaks": round(peaks, 6),
        },
    }
