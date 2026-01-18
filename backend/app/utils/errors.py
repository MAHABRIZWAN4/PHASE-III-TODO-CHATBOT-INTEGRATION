"""Error message translations for English and Urdu.

This module provides error messages in multiple languages to support
internationalization of error responses in the API.
"""

from typing import Dict, Literal


# Error message translations dictionary
# Structure: {error_code: {language: message}}
ERROR_MESSAGES: Dict[str, Dict[str, str]] = {
    "RATE_LIMIT": {
        "english": "Too many requests. Please try again later.",
        "urdu": "بہت زیادہ درخواستیں۔ براہ کرم بعد میں دوبارہ کوشش کریں۔"
    },
    "VALIDATION_ERROR": {
        "english": "Invalid input. Please check your request and try again.",
        "urdu": "غلط ان پٹ۔ براہ کرم اپنی درخواست چیک کریں اور دوبارہ کوشش کریں۔"
    },
    "UNAUTHORIZED": {
        "english": "Unauthorized access. Please log in to continue.",
        "urdu": "غیر مجاز رسائی۔ جاری رکھنے کے لیے براہ کرم لاگ ان کریں۔"
    },
    "NOT_FOUND": {
        "english": "Resource not found. The requested item does not exist.",
        "urdu": "وسیلہ نہیں ملا۔ درخواست کردہ آئٹم موجود نہیں ہے۔"
    },
    "DATABASE_ERROR": {
        "english": "Database error. Please try again later.",
        "urdu": "ڈیٹا بیس کی خرابی۔ براہ کرم بعد میں دوبارہ کوشش کریں۔"
    },
    "INTERNAL_ERROR": {
        "english": "Internal server error. Please contact support if the problem persists.",
        "urdu": "اندرونی سرور کی خرابی۔ اگر مسئلہ برقرار رہے تو براہ کرم سپورٹ سے رابطہ کریں۔"
    }
}


def get_error_message(
    code: str,
    language: str = "english"
) -> str:
    """Get an error message in the specified language.

    This function retrieves the appropriate error message for a given error code
    and language. It includes fallback logic to handle edge cases gracefully.

    Args:
        code: The error code (e.g., "RATE_LIMIT", "VALIDATION_ERROR").
              Should match one of the keys in ERROR_MESSAGES dictionary.
        language: The language for the error message. Should be either
                 "english" or "urdu". Defaults to "english".

    Returns:
        str: The error message in the requested language. If the error code
             or language is not found, returns a generic error message in English.

    Examples:
        >>> get_error_message("RATE_LIMIT", "english")
        'Too many requests. Please try again later.'

        >>> get_error_message("RATE_LIMIT", "urdu")
        'بہت زیادہ درخواستیں۔ براہ کرم بعد میں دوبارہ کوشش کریں۔'

        >>> get_error_message("UNKNOWN_ERROR", "english")
        'An error occurred. Please try again.'

        >>> get_error_message("RATE_LIMIT", "french")  # Unsupported language
        'Too many requests. Please try again later.'

        >>> get_error_message("", "english")  # Empty code
        'An error occurred. Please try again.'

        >>> get_error_message(None, "english")  # None code
        'An error occurred. Please try again.'

    Notes:
        - If the error code is not found, returns a generic error message
        - If the language is not supported, falls back to English
        - Handles None and empty string values gracefully
        - Always returns a string (never None)
    """
    # Handle edge case: None or empty error code
    if not code:
        return "An error occurred. Please try again."

    # Handle edge case: None or empty language
    if not language:
        language = "english"

    # Normalize language to lowercase for case-insensitive matching
    language = language.lower()

    # Check if error code exists in ERROR_MESSAGES
    if code not in ERROR_MESSAGES:
        # Return generic error message for unknown error codes
        return "An error occurred. Please try again."

    # Get the error messages for this code
    error_dict = ERROR_MESSAGES[code]

    # Check if the requested language is available
    if language in error_dict:
        return error_dict[language]

    # Fallback to English if requested language is not available
    if "english" in error_dict:
        return error_dict["english"]

    # Final fallback (should never reach here with current structure)
    return "An error occurred. Please try again."
