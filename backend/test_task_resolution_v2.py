"""Test script for task reference resolution (position, title, ID) - Fixed version"""
import re

def test_resolve_patterns():
    """Test regex patterns for extracting task references"""
    
    test_cases = [
        # Position-based
        ("mark task 1 as completed", {"number": 1, "title": None}),
        ("complete task 2", {"number": 2, "title": None}),
        ("delete task 3", {"number": 3, "title": None}),
        
        # Title-based
        ("complete jjs task", {"number": None, "title": "jjs"}),
        ("mark the lunch task as done", {"number": None, "title": "lunch"}),
        ("delete buy groceries", {"number": None, "title": "buy groceries"}),
        ("complete jjs", {"number": None, "title": "jjs"}),
        
        # ID-based (large numbers)
        ("mark task 36 as completed", {"number": 36, "title": None}),
        ("delete task 35", {"number": 35, "title": None}),
    ]
    
    print("=" * 60)
    print("Testing Task Reference Extraction (Fixed)")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for message, expected in test_cases:
        # Extract number
        number_match = re.search(r'\b(?:task|id)\s*#?(\d+)\b', message, re.IGNORECASE)
        number = int(number_match.group(1)) if number_match else None
        
        # Extract title ONLY if no number found
        title = None
        if not number:
            title_patterns = [
                r'(?:complete|delete|mark|finish)\s+(?:the\s+)?([a-zA-Z][a-zA-Z0-9\s]+?)\s+(?:task|as)',
                r'(?:complete|delete|mark|finish)\s+([a-zA-Z][a-zA-Z0-9\s]+)$',
            ]
            
            for pattern in title_patterns:
                title_match = re.search(pattern, message, re.IGNORECASE)
                if title_match:
                    title = title_match.group(1).strip()
                    break
        
        # Check results
        is_passed = (number == expected["number"] and title == expected["title"])
        status = "✓ PASS" if is_passed else "✗ FAIL"
        
        if is_passed:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status}: '{message}'")
        print(f"  Expected: number={expected['number']}, title={expected['title']}")
        print(f"  Got:      number={number}, title={title}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

if __name__ == "__main__":
    test_resolve_patterns()
