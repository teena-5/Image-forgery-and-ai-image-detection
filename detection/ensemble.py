"""
Ensemble Scoring Engine
Combines results from all five analysis modules using weighted voting
to produce a final classification verdict.
"""

from detection.ela_analyzer import analyze_ela
from detection.metadata_analyzer import analyze_metadata
from detection.noise_analyzer import analyze_noise
from detection.frequency_analyzer import analyze_frequency
from detection.texture_analyzer import analyze_texture


# Module weights for the ensemble
WEIGHTS = {
    "ela": 0.30,
    "metadata": 0.20,
    "noise": 0.20,
    "frequency": 0.15,
    "texture": 0.15,
}


def classify_image(image_path, output_dir=None):
    """
    Classify an image by running all analysis modules and combining results.

    Executes ELA, metadata, noise, frequency, and texture analyzers, then
    applies weighted voting to determine the final verdict.

    Args:
        image_path (str): Path to the input image.
        output_dir (str, optional): Directory to save analysis artifacts (e.g. ELA image).

    Returns:
        dict: Final classification containing:
            - verdict (str): 'REAL', 'EDITED', or 'AI_GENERATED'
            - confidence (float): Confidence score for the final verdict
            - votes (dict): Weighted vote percentages for each category
            - details (dict): Full results from each individual module
            - ela_image_path (str or None): Path to the ELA visualization image
    """
    # Run all five analyzers
    ela_result = analyze_ela(image_path, output_dir=output_dir)
    metadata_result = analyze_metadata(image_path)
    noise_result = analyze_noise(image_path)
    frequency_result = analyze_frequency(image_path)
    texture_result = analyze_texture(image_path)

    # Collect all module results
    details = {
        "ela": ela_result,
        "metadata": metadata_result,
        "noise": noise_result,
        "frequency": frequency_result,
        "texture": texture_result,
    }

    # Weighted voting
    # For each module, add weight * confidence/100 to that module's verdict category
    vote_scores = {}
    module_results = {
        "ela": ela_result,
        "metadata": metadata_result,
        "noise": noise_result,
        "frequency": frequency_result,
        "texture": texture_result,
    }

    for module_name, result in module_results.items():
        module_verdict = result["verdict"]
        module_confidence = result["confidence"]
        weight = WEIGHTS[module_name]

        weighted_vote = weight * (module_confidence / 100.0)

        if module_verdict not in vote_scores:
            vote_scores[module_verdict] = 0.0
        vote_scores[module_verdict] += weighted_vote

    # Normalize votes to percentages summing to 100
    total_votes = sum(vote_scores.values())
    if total_votes > 0:
        votes = {
            category: round((score / total_votes) * 100, 2)
            for category, score in vote_scores.items()
        }
    else:
        votes = vote_scores

    # Final verdict = category with highest vote percentage
    final_verdict = max(votes, key=votes.get)
    final_confidence = votes[final_verdict]

    # Extract ELA image path
    ela_image_path = ela_result.get("ela_image_path", None)

    return {
        "verdict": final_verdict,
        "confidence": round(final_confidence, 2),
        "votes": votes,
        "details": details,
        "ela_image_path": ela_image_path,
    }
