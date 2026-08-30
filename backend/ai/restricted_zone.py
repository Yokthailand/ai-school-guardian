"""
Step 7 — Restricted Zone Detection.

Pure geometry, no ML dependency, so it's implemented in full now
(doesn't need to wait for Step 5/6).

Uses the foot point (bottom-center of the bounding box) as the person's
ground position, then checks it against each zone's normalized polygon.
"""
from typing import List, Dict, Tuple


def foot_point(bbox: List[float], frame_width: int, frame_height: int) -> Tuple[float, float]:
    """bbox = [x1, y1, x2, y2] in pixels -> normalized (x, y) foot point."""
    x1, y1, x2, y2 = bbox
    fx = (x1 + x2) / 2
    fy = y2
    return (fx / frame_width, fy / frame_height)


def point_in_polygon(point: Tuple[float, float], polygon: List[List[float]]) -> bool:
    """Ray casting algorithm. polygon = [[x, y], ...] normalized 0-1."""
    x, y = point
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersect = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi
        )
        if intersect:
            inside = not inside
        j = i
    return inside


def check_restricted_zones(
    tracks: List[Dict], zones: List[Dict], frame_width: int, frame_height: int
) -> List[Dict]:
    """
    tracks: [{"track_id": 15, "bbox": [...]}]
    zones:  [{"id": 3, "polygon": [[x,y],...], "zone_type": "restricted"}]
    Returns a list of violation events (empty if none):
        [{"track_id": 15, "zone_id": 3, "type": "restricted_zone"}]
    """
    violations = []
    restricted = [z for z in zones if z.get("zone_type") == "restricted"]
    for track in tracks:
        point = foot_point(track["bbox"], frame_width, frame_height)
        for zone in restricted:
            if point_in_polygon(point, zone["polygon"]):
                violations.append({
                    "track_id": track["track_id"],
                    "zone_id": zone["id"],
                    "type": "restricted_zone",
                })
    return violations
