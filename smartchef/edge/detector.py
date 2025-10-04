# smartchef/edge/detector.py
import os

WHITELIST = {
    "egg","eggs","tomato","spinach","cheese","milk","yogurt","pasta","onion","garlic","bread","banana","apple"
}

def detect_foods(image_path: str) -> list[str]:
    # Minimal heuristic: guess from filename; fallback to a small set
    name = os.path.basename(image_path).lower()
    found = {w for w in WHITELIST if w in name}
    return sorted(found) or ["egg", "tomato", "spinach"]
