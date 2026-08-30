"""
Step 6 — Person Tracking (ByteTrack).

Assigns a stable track_id to each detected person across frames, so
Loitering (Step 8) can time how long the same person has been in a zone.

Usage once implemented:
    tracker = PersonTracker()
    tracks = tracker.update(detections)
    # -> [{"track_id": 15, "bbox": [x1, y1, x2, y2]}, ...]
"""
from typing import List, Dict


class PersonTracker:
    def __init__(self):
        self._tracker = None

    def _load(self):
        if self._tracker is None:
            # Ultralytics ships ByteTrack — wire this up when you reach Step 6:
            #   model.track(frame, tracker="bytetrack.yaml", persist=True)
            # This stub keeps the interface stable so Step 7/8 can be built now.
            raise NotImplementedError("ByteTrack integration lands in Step 6")
        return self._tracker

    def update(self, detections: List[Dict]) -> List[Dict]:
        raise NotImplementedError("ByteTrack integration lands in Step 6")
