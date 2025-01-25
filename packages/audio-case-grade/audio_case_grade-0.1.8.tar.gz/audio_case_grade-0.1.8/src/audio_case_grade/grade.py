"""Top level display objects like grade and assignments for student"""


def get_grade(lexical_density: float) -> str:
    """Grade a score with a weighted grade on a scale of 100"""
    if lexical_density >= 40:
        return "Advanced"
    if 30 <= lexical_density < 40:
        return "Proficient"
    if 20 <= lexical_density < 30:
        return "Average"

    return "Low"
