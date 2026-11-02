"""Known-place gazetteer: coordinates ONLY for explicitly listed places.

Anything not in KNOWN_PLACES resolves to (None, None, False) and the UI
must show it as an unresolved/uncertain location. We never guess coords.
"""

from typing import Dict, Optional, Tuple

# name-key -> (display name, lat, lng). Kenya-focused for the demo scenario.
KNOWN_PLACES: Dict[str, Tuple[str, float, float]] = {
    "mathare": ("Mathare, Nairobi", -1.2618, 36.8733),
    "mathare north": ("Mathare North, Nairobi", -1.2589, 36.8701),
    "huruma": ("Huruma, Nairobi", -1.2697, 36.8761),
    "kimathi street": ("Kimathi Street, Nairobi", -1.2841, 36.8233),
    "thika": ("Thika, Kenya", -1.0393, 37.0715),
    "thika superhighway": ("Thika Superhighway", -1.1036, 36.9599),
    "kahawa wendani": ("Kahawa Wendani, Kenya", -1.2167, 36.9333),
    "kahawa": ("Kahawa, Kenya", -1.2167, 36.9367),
    "ruiru": ("Ruiru, Kenya", -1.1483, 36.9583),
    "kenyatta university": ("Kenyatta University, Kenya", -1.2232, 36.8946),
    "k.u.": ("Kenyatta University, Kenya", -1.2232, 36.8946),
    " ku ": ("Kenyatta University, Kenya", -1.2232, 36.8946),
    "westlands": ("Westlands, Nairobi", -1.2655, 36.8028),
    "kibera": ("Kibera, Nairobi", -1.3133, 36.7844),
    "kisumu": ("Kisumu, Kenya", -0.0917, 34.7680),
    "dunga": ("Dunga, Kisumu", -0.0833, 34.7500),
    "homa bay": ("Homa Bay, Kenya", -0.5167, 34.4833),
    "nairobi": ("Nairobi, Kenya", -1.2921, 36.8219),
    "nakuru": ("Nakuru, Kenya", -0.3031, 36.0800),
    "mombasa": ("Mombasa, Kenya", -4.0435, 39.6682),
    "eldoret": ("Eldoret, Kenya", 0.5143, 35.2698),
    "budalangi": ("Budalangi, Busia", 0.1167, 34.0333),
    "tana river": ("Tana River, Kenya", -1.5000, 40.0333),
    "kisii": ("Kisii, Kenya", -0.6833, 34.7667),
}


def resolve_location(text: Optional[str]):
    """Return (display_name, lat, lng, resolved).

    Longest case-insensitive substring match wins. No match -> unresolved.
    """
    if not text:
        return None, None, None, False
    lowered = f" {text.lower()} "
    best_key = None
    for key in KNOWN_PLACES:
        needle = key if key.startswith(" ") else key
        if needle in lowered and (best_key is None or len(key) > len(best_key)):
            best_key = key
    if best_key is None:
        return None, None, None, False
    display, lat, lng = KNOWN_PLACES[best_key]
    return display, lat, lng, True


def resolve_from_parts(*parts: Optional[str]):
    """Try several text parts in order; first resolution wins."""
    for part in parts:
        display, lat, lng, ok = resolve_location(part)
        if ok:
            return display, lat, lng, True
    return None, None, None, False
