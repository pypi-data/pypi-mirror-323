"""Tests Lexical Density Grade Scale"""

from audio_case_grade import get_grade


def test_get_grade():
    """Testing Lexical Density Scale"""
    actual_1 = get_grade(45)
    actual_2 = get_grade(35)
    actual_3 = get_grade(25)
    actual_4 = get_grade(15)
    assert actual_1 == "Advanced"
    assert actual_2 == "Proficient"
    assert actual_3 == "Average"
    assert actual_4 == "Low"
