"""End-to-end recorded MP4 analysis pipeline."""
from pathlib import Path
from typing import Iterator, Optional
from time import perf_counter

from ai.detector import PersonDetector
from ai.restricted_zone import point_in_polygon, foot_point
from ai.risk_object import RiskObjectDetector, TemporalRiskValidator


class VideoSource:
    def __init__(self, source: str, source_uri: str):
        self.source = source
        self.source_uri = source_uri
        self._cap = None

    def _open(self):
        import cv2  # local import — install opencv-python for this step

        if self.source == "webcam":
            self._cap = cv2.VideoCapture(int(self.source_uri))
        else:  # "mp4" or "rtsp" both open the same way in OpenCV
            self._cap = cv2.VideoCapture(self.source_uri)

        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open video source: {self.source_uri}")

    def frames(self) -> Iterator["Optional[object]"]:
        if self._cap is None:
            self._open()
        while True:
            ok, frame = self._cap.read()
            if not ok:
                break
            yield frame

    def dimensions(self) -> tuple[int, int]:
        if self._cap is None:
            self._open()
        w = int(self._cap.get(3))  # cv2.CAP_PROP_FRAME_WIDTH
        h = int(self._cap.get(4))  # cv2.CAP_PROP_FRAME_HEIGHT
        return w, h

    def release(self):
        if self._cap is not None:
            self._cap.release()


def analyze_mp4(
    source_path: str,
    output_path: str,
    zones: list[dict],
    confidence: float = 0.35,
    snapshots_dir: str | None = None,
    camera_id: int = 1,
) -> dict:
    """Analyze an MP4 and return summary plus event candidates.

    Loitering uses the video's clock (frame/fps), so results are independent
    of how fast the host computer processes the recording.
    """
    import cv2

    source = VideoSource("mp4", source_path)
    source._open()
    width, height = source.dimensions()
    fps = float(source._cap.get(cv2.CAP_PROP_FPS) or 25.0)
    total_frames = int(source._cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        source.release()
        raise RuntimeError("Could not create processed video")

    detector = PersonDetector(conf_threshold=confidence)
    risk_detector = RiskObjectDetector(conf_threshold=max(0.25, confidence))
    risk_validator = TemporalRiskValidator()
    unique_tracks: set[int] = set()
    restricted_entries: set[tuple[int, int]] = set()
    active_zone_tracks: set[tuple[int, int]] = set()
    zone_entered_at: dict[tuple[int, int], float] = {}
    zone_last_seen: dict[tuple[int, int], float] = {}
    loitering_fired: set[tuple[int, int]] = set()
    analysis_events: list[dict] = []
    last_risk_event: dict[str, float] = {}
    active_risks: list[dict] = []
    max_people = 0
    processed_frames = 0
    tracks: list[dict] = []

    try:
        for frame in source.frames():
            frame_started = perf_counter()
            inference_frame = frame.copy()
            # The lightweight fallback is sampled every third frame; YOLO/ByteTrack
            # runs every frame. Reusing boxes keeps CPU-only demo analysis practical.
            if detector.engine == "uninitialized" or detector.engine.startswith("YOLO") or processed_frames % 3 == 0:
                tracks = detector.track(frame)
            max_people = max(max_people, len(tracks))
            processed_frames += 1
            video_seconds = processed_frames / fps

            current_zone_tracks: set[tuple[int, int]] = set()
            for zone in zones:
                polygon = zone.get("polygon", [])
                if len(polygon) < 3:
                    continue
                points = [
                    (int(x * width), int(y * height)) for x, y in polygon
                ]
                cv2.polylines(frame, [__import__("numpy").array(points)], True, (0, 165, 255), 2)
                cv2.putText(
                    frame,
                    zone.get("name", "Monitored zone"),
                    points[0],
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 165, 255),
                    2,
                )

            for track in tracks:
                track_id = track["track_id"]
                unique_tracks.add(track_id)
                x1, y1, x2, y2 = map(int, track["bbox"])
                color = (61, 255, 154)
                track_events: list[dict] = []
                track_confidence = float(track.get("confidence", 0.0))
                for zone in zones:
                    if point_in_polygon(foot_point(track["bbox"], width, height), zone["polygon"]):
                        key = (track_id, int(zone["id"]))
                        current_zone_tracks.add(key)
                        if key not in zone_entered_at:
                            zone_entered_at[key] = video_seconds
                        zone_last_seen[key] = video_seconds
                        if zone.get("zone_type") == "restricted" and key not in restricted_entries:
                            restricted_entries.add(key)
                            track_events.append({
                                "event_type": "restricted_zone",
                                "track_id": track_id,
                                "confidence": track_confidence,
                                "video_seconds": video_seconds,
                                "response_time_ms": round((perf_counter() - frame_started) * 1000, 2),
                            })
                        threshold = int(zone.get("loitering_threshold") or 30)
                        duration = video_seconds - zone_entered_at[key]
                        if duration >= threshold and key not in loitering_fired:
                            loitering_fired.add(key)
                            track_events.append({
                                "event_type": "loitering",
                                "track_id": track_id,
                                "confidence": track_confidence,
                                "video_seconds": video_seconds,
                                "duration_seconds": round(duration, 1),
                                "response_time_ms": round((perf_counter() - frame_started) * 1000, 2),
                            })
                        color = (0, 165, 255)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame,
                    f"PERSON #{track_id} {track['confidence']:.0%}",
                    (x1, max(20, y1 - 7)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2,
                )
                for event in track_events:
                    analysis_events.append({**event, "frame": frame.copy()})

            # Keep boxes visible between sampled inference frames so the
            # annotation is readable and does not flicker.
            if processed_frames % 5 == 0:
                person_boxes = [track["bbox"] for track in tracks]
                raw_risks = risk_detector.detect(
                    inference_frame,
                    person_boxes=person_boxes,
                    deep_scan=processed_frames % 30 == 0,
                    allow_unattended=True,
                )
                detected_risks = risk_validator.update(raw_risks, video_seconds)
                if detected_risks:
                    active_risks = [
                        {**risk, "visible_until": video_seconds + 0.65}
                        for risk in detected_risks
                    ]
                for risk in detected_risks:
                    label = risk["label"]
                    if video_seconds - last_risk_event.get(label, -999) < 5.0:
                        continue
                    last_risk_event[label] = video_seconds
                    snapshot_frame = frame.copy()
                    sx1, sy1, sx2, sy2 = map(int, risk["bbox"])
                    cv2.rectangle(snapshot_frame, (sx1, sy1), (sx2, sy2), (0, 0, 239), 3)
                    cv2.putText(
                        snapshot_frame,
                        f"POTENTIAL RISK: {label.upper()} - REVIEW",
                        (sx1, max(24, sy1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (0, 0, 239),
                        2,
                    )
                    analysis_events.append({
                        "event_type": "risk_object",
                        "track_id": None,
                        "confidence": risk["confidence"],
                        "risk_label": label,
                        "requires_human_verification": True,
                        "video_seconds": video_seconds,
                        "response_time_ms": round((perf_counter() - frame_started) * 1000, 2),
                        "frame": snapshot_frame,
                    })

            active_risks = [
                risk for risk in active_risks if risk["visible_until"] >= video_seconds
            ]
            for risk in active_risks:
                x1, y1, x2, y2 = map(int, risk["bbox"])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 239), 3)
                cv2.putText(
                    frame,
                    f"POTENTIAL RISK: {risk['label'].upper()} - REVIEW",
                    (x1, max(24, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 0, 239),
                    2,
                )

            for key in list(zone_entered_at):
                # Brief detector drop-outs should not reset a person's zone
                # session or loitering timer.
                if video_seconds - zone_last_seen.get(key, 0) > 1.5:
                    zone_entered_at.pop(key, None)
                    zone_last_seen.pop(key, None)
                    loitering_fired.discard(key)
            active_zone_tracks = set(zone_entered_at)
            cv2.putText(
                frame,
                f"AI SCHOOL GUARDIAN | PEOPLE: {len(tracks)}",
                (16, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (61, 255, 154),
                2,
            )
            writer.write(frame)
    finally:
        writer.release()
        source.release()

    snapshots_path = Path(snapshots_dir) if snapshots_dir else None
    serialized_events = []
    if snapshots_path:
        snapshots_path.mkdir(parents=True, exist_ok=True)
    for index, event in enumerate(analysis_events, start=1):
        frame = event.pop("frame")
        snapshot_url = None
        if snapshots_path:
            filename = f"camera_{camera_id}_{event['event_type']}_{index}.jpg"
            cv2.imwrite(str(snapshots_path / filename), frame)
            snapshot_url = f"/media/snapshots/{filename}"
        serialized_events.append({**event, "snapshot": snapshot_url})

    return {
        "detector_engine": detector.engine,
        "processed_frames": processed_frames,
        "total_frames": total_frames,
        "fps": round(fps, 2),
        "width": width,
        "height": height,
        "unique_people": len([track for track in unique_tracks if track >= 0]),
        "max_people_in_frame": max_people,
        "restricted_zone_entries": len(restricted_entries),
        "loitering_events": sum(1 for e in serialized_events if e["event_type"] == "loitering"),
        "risk_object_events": sum(1 for e in serialized_events if e["event_type"] == "risk_object"),
        "risk_detector_engine": f"{risk_detector.engine} + multiscale temporal confirmation",
        "events": serialized_events,
    }
