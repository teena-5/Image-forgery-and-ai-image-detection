"""
EXIF Metadata Analysis Module
Analyzes image EXIF metadata to detect signs of editing, AI generation,
or authentic camera capture.
"""

from PIL import Image
from PIL.ExifTags import TAGS
import os


# Known editing software signatures (lowercase for matching)
KNOWN_EDITING_SOFTWARE = [
    "photoshop",
    "gimp",
    "lightroom",
    "snapseed",
    "pixlr",
    "canva",
    "paint",
]

# Known AI generation software signatures (lowercase for matching)
KNOWN_AI_SOFTWARE = [
    "dall-e",
    "midjourney",
    "stable diffusion",
    "comfyui",
    "automatic1111",
    "novelai",
]


def analyze_metadata(image_path):
    """
    Analyze image EXIF metadata to determine authenticity.

    Extracts EXIF data from the image and checks for camera information,
    GPS data, timestamps, and software signatures to classify the image.

    Args:
        image_path (str): Path to the input image.

    Returns:
        dict: Analysis results containing:
            - verdict (str): 'REAL', 'EDITED', or 'AI_GENERATED'
            - confidence (float): Confidence score (0-100)
            - metrics (dict): Detailed metadata statistics
    """
    image = Image.open(image_path)

    # Attempt to extract EXIF data
    exif_data = {}
    raw_exif = None
    try:
        raw_exif = image._getexif()
    except (AttributeError, Exception):
        raw_exif = None

    has_exif = False
    total_exif_tags = 0

    if raw_exif is not None:
        has_exif = True
        for tag_id, value in raw_exif.items():
            tag_name = TAGS.get(tag_id, str(tag_id))
            exif_data[tag_name] = value
        total_exif_tags = len(exif_data)

    # Check for camera Make/Model
    camera_make = exif_data.get("Make", None)
    camera_model = exif_data.get("Model", None)
    has_camera = camera_make is not None or camera_model is not None

    # Check for GPS information
    has_gps = "GPSInfo" in exif_data

    # Check for date/time fields
    datetime_field = exif_data.get("DateTime", None)
    datetime_original = exif_data.get("DateTimeOriginal", None)
    datetime_digitized = exif_data.get("DateTimeDigitized", None)
    has_datetime = any([datetime_field, datetime_original, datetime_digitized])

    # Check for software tag
    software = exif_data.get("Software", None)
    software_detected = str(software).lower() if software else ""

    # Detect editing or AI software
    is_edited_software = any(
        s in software_detected for s in KNOWN_EDITING_SOFTWARE
    )
    is_ai_software = any(
        s in software_detected for s in KNOWN_AI_SOFTWARE
    )

    # Metadata richness score
    metadata_richness = sum([has_exif, has_camera, has_gps, has_datetime]) / 4.0

    # Verdict logic
    if is_ai_software:
        verdict = "AI_GENERATED"
        confidence = 90.0
    elif not has_exif or (not has_camera and not has_datetime):
        verdict = "AI_GENERATED"
        confidence = 65.0
    elif is_edited_software:
        verdict = "EDITED"
        confidence = 80.0
    elif software and not has_camera:
        verdict = "EDITED"
        confidence = 55.0
    elif metadata_richness > 0.5:
        verdict = "REAL"
        confidence = 70 + metadata_richness * 20
    else:
        verdict = "REAL"
        confidence = 50.0

    return {
        "verdict": verdict,
        "confidence": round(confidence, 2),
        "metrics": {
            "has_exif": has_exif,
            "has_camera_info": has_camera,
            "has_gps": has_gps,
            "has_datetime": has_datetime,
            "software_detected": software_detected if software_detected else None,
            "metadata_richness": round(metadata_richness, 4),
            "total_exif_tags": total_exif_tags,
        },
    }
