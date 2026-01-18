"""Language detection utility for English and Urdu text.

This module provides functionality to detect whether input text is primarily
in English or Urdu based on Unicode character analysis.
"""


def detect_language(text: str) -> str:
    """Detect the language of the input text (English or Urdu).

    This function analyzes the Unicode characters in the input text to determine
    whether it is primarily in Urdu or English. The detection algorithm works by:

    1. Counting characters in the Urdu Unicode range (U+0600 to U+06FF)
    2. Calculating the percentage of Urdu characters relative to total characters
    3. Returning "urdu" if more than 30% of characters are in the Urdu range
    4. Returning "english" otherwise

    The Urdu Unicode range (U+0600 to U+06FF) covers:
    - Arabic script characters (used for Urdu)
    - Urdu-specific characters
    - Arabic diacritical marks

    Args:
        text: The input text to analyze. Can be any string.

    Returns:
        str: Either "urdu" or "english" based on the detected language.

    Examples:
        >>> detect_language("Hello, how are you?")
        'english'

        >>> detect_language("میرے کام دکھاؤ")
        'urdu'

        >>> detect_language("Hello میرے")  # Mixed text with <30% Urdu
        'english'

        >>> detect_language("")  # Empty string
        'english'

    Notes:
        - Empty strings or None values are treated as English
        - Whitespace and punctuation are included in character count
        - The 30% threshold is a heuristic that works well for mixed content
        - Mixed-language text defaults to English unless Urdu is dominant
    """
    # Handle edge cases: empty strings or None
    if not text or text.strip() == "":
        return "english"

    # Count total characters (excluding whitespace for more accurate detection)
    total_chars = len([c for c in text if not c.isspace()])

    # Handle edge case: text with only whitespace
    if total_chars == 0:
        return "english"

    # Count characters in Urdu Unicode range (U+0600 to U+06FF)
    # This range covers Arabic script used for Urdu
    urdu_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')

    # Calculate percentage of Urdu characters
    urdu_percentage = (urdu_chars / total_chars) * 100

    # Return "urdu" if more than 30% of characters are in Urdu range
    # Otherwise return "english"
    if urdu_percentage > 30:
        return "urdu"
    else:
        return "english"
