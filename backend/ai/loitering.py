"""
Step 8 — Loitering Detection.

Tracks how long each (track_id, zone_id) pair has stayed inside a zone,
using wall-clock time. When a person leaves the zone their timer is
cleared, so this only fires for continuous presence.
"""
import time
from typing import Dict, Tuple, Optional


class LoiteringTracker:
    def __init__(self, default_threshold_seconds: int = 30):
        self.default_threshold_seconds = default_threshold_seconds
        # (track_id, zone_id) -> {"enter_time": float, "last_seen": float}
        self._sessions: Dict[Tuple[int, int], Dict[str, float]] = {}

    def update_presence(self, track_id: int, zone_id: int) -> Optional[Dict]:
        """Call once per frame for every track currently inside zone_id.
        Returns a loitering event dict once the threshold is crossed, else None.
        """
        key = (track_id, zone_id)
        now = time.time()
        session = self._sessions.get(key)
        if session is None:
            self._sessions[key] = {"enter_time": now, "last_seen": now}
            return None

        session["last_seen"] = now
        duration = now - session["enter_time"]
        if duration >= self.default_threshold_seconds:
            return {
                "track_id": track_id,
                "zone_id": zone_id,
                "type": "loitering",
                "duration_seconds": round(duration, 1),
            }
        return None

    def clear_absent(self, present_keys: set) -> None:
        """Call once per frame with the set of (track_id, zone_id) pairs
        still present, so anyone who left has their timer reset."""
        for key in list(self._sessions.keys()):
            if key not in present_keys:
                del self._sessions[key]
