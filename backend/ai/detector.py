"""Person detection: YOLO/ByteTrack when installed, OpenCV HOG fallback."""
import math
from typing import List, Dict


class PersonDetector:
    def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.5):
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self._model = None  # lazy-loaded so importing this file doesn't require ultralytics yet
        self.engine = "uninitialized"
        self.device = "cpu"
        self._previous: dict[int, List[float]] = {}
        self._missed: dict[int, int] = {}
        self._next_track_id = 1

    def _load(self):
        if self._model is None:
            try:
                from ultralytics import YOLO
                import torch
                self._model = YOLO(self.model_path)
                self.device = 0 if torch.cuda.is_available() else "cpu"
                self.engine = f"YOLOv8 + ByteTrack ({'GPU' if self.device == 0 else 'CPU'})"
            except (ImportError, RuntimeError, OSError):
                import cv2
                hog = cv2.HOGDescriptor()
                hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
                self._model = hog
                self.engine = "OpenCV HOG fallback"
        return self._model

    def detect(self, frame) -> List[Dict]:
        model = self._load()
        if self.engine == "OpenCV HOG fallback":
            import cv2
            scale_factor = 1.5
            enlarged = cv2.resize(
                frame, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR
            )
            boxes, weights = model.detectMultiScale(
                enlarged, winStride=(8, 8), padding=(8, 8), scale=1.05
            )
            return [
                {
                    "class": "person",
                    # HOG's SVM score is not a probability; clamp it for the UI.
                    "confidence": min(1.0, max(0.0, float(weight))),
                    "bbox": [
                        x / scale_factor,
                        y / scale_factor,
                        (x + w) / scale_factor,
                        (y + h) / scale_factor,
                    ],
                }
                for (x, y, w, h), weight in zip(boxes, weights)
                if float(weight) >= self.conf_threshold
            ]
        results = model(frame, conf=self.conf_threshold, classes=[0], device=self.device, verbose=False)  # class 0 = person
        detections = []
        for box in results[0].boxes:
            detections.append({
                "class": "person",
                "confidence": float(box.conf[0]),
                "bbox": [float(v) for v in box.xyxy[0].tolist()],
            })
        return detections

    def track(self, frame) -> List[Dict]:
        """Detect people and assign stable IDs with Ultralytics ByteTrack."""
        model = self._load()
        if self.engine == "OpenCV HOG fallback":
            return self._assign_fallback_ids(self.detect(frame))
        results = model.track(
            frame,
            conf=self.conf_threshold,
            classes=[0],
            tracker="bytetrack.yaml",
            persist=True,
            verbose=False,
            device=self.device,
        )
        tracks = []
        boxes = results[0].boxes
        if boxes is None:
            return tracks
        for index, box in enumerate(boxes):
            track_id = int(box.id[0]) if box.id is not None else -(index + 1)
            tracks.append({
                "class": "person",
                "track_id": track_id,
                "confidence": float(box.conf[0]),
                "bbox": [float(v) for v in box.xyxy[0].tolist()],
            })
        return tracks

    def _assign_fallback_ids(self, detections: List[Dict]) -> List[Dict]:
        """Lightweight persistent centroid tracker for the CPU fallback.

        Tracks survive short detector drop-outs; this is important because the
        HOG detector is sampled rather than run on every frame.
        """
        available = dict(self._previous)
        next_previous: dict[int, List[float]] = dict(self._previous)
        matched: set[int] = set()
        tracks = []
        for detection in detections:
            x1, y1, x2, y2 = detection["bbox"]
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            best_id, best_distance = None, float("inf")
            for track_id, previous_bbox in available.items():
                px1, py1, px2, py2 = previous_bbox
                distance = math.hypot(cx - (px1 + px2) / 2, cy - (py1 + py2) / 2)
                if distance < best_distance:
                    best_id, best_distance = track_id, distance
            diagonal = math.hypot(x2 - x1, y2 - y1)
            if best_id is None or best_distance > max(100, diagonal * 2.5):
                best_id = self._next_track_id
                self._next_track_id += 1
            else:
                available.pop(best_id, None)
            matched.add(best_id)
            detection = {**detection, "track_id": best_id}
            tracks.append(detection)
            old = self._previous.get(best_id)
            if old:
                next_previous[best_id] = [old[i] * 0.35 + detection["bbox"][i] * 0.65 for i in range(4)]
            else:
                next_previous[best_id] = detection["bbox"]
            self._missed[best_id] = 0
        for track_id in list(next_previous):
            if track_id in matched:
                continue
            self._missed[track_id] = self._missed.get(track_id, 0) + 1
            if self._missed[track_id] > 20:
                next_previous.pop(track_id, None)
                self._missed.pop(track_id, None)
        self._previous = next_previous
        return tracks
