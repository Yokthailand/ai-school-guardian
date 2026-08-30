"""Potential-risk-object screening for mandatory human review.

COCO does not contain a firearm class, so firearm candidates are handled by a
dedicated YOLOv8 model. Every result remains a candidate and must never be
presented as a confirmed weapon.
"""
from pathlib import Path
from typing import Dict, List, Optional
import math


BACKEND_DIR = Path(__file__).resolve().parents[1]
DEFAULT_FIREARM_MODEL = BACKEND_DIR / "models" / "firearm-yolov8n.pt"


class RiskObjectDetector:
    GENERAL_RISK_LABELS = {"knife", "scissors", "baseball bat"}

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        firearm_model_path: str | Path = DEFAULT_FIREARM_MODEL,
        conf_threshold: float = 0.35,
        firearm_conf_threshold: float = 0.30,
        firearm_imgsz: int = 960,
        max_firearm_area_ratio: float = 0.025,
        deep_scan_confidence: float = 0.22,
    ):
        self.model_path = model_path
        self.firearm_model_path = Path(firearm_model_path)
        self.conf_threshold = conf_threshold
        self.firearm_conf_threshold = firearm_conf_threshold
        self.firearm_imgsz = firearm_imgsz
        self.max_firearm_area_ratio = max_firearm_area_ratio
        self.deep_scan_confidence = deep_scan_confidence
        self._general_model = None
        self._firearm_model = None
        self.engine = "uninitialized"
        self._attempted = False
        self.device = "cpu"

    def _load(self):
        if self._attempted:
            return self._general_model, self._firearm_model
        self._attempted = True
        try:
            from ultralytics import YOLO
            import torch

            self.device = 0 if torch.cuda.is_available() else "cpu"
            self._general_model = YOLO(self.model_path)
            if self.firearm_model_path.exists():
                self._firearm_model = YOLO(str(self.firearm_model_path))
            hardware = "GPU" if self.device == 0 else "CPU"
            firearm_status = "firearm + COCO" if self._firearm_model else "COCO only"
            self.engine = f"YOLOv8 {firearm_status} potential-risk screening ({hardware})"
        except (ImportError, RuntimeError, OSError):
            self.engine = "unavailable"
        return self._general_model, self._firearm_model

    @staticmethod
    def _is_near_person(bbox: List[float], person_boxes: List[List[float]]) -> bool:
        """Require a firearm candidate to lie inside a slightly expanded person box."""
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        for px1, py1, px2, py2 in person_boxes:
            pad_x = (px2 - px1) * 0.18
            pad_y = (py2 - py1) * 0.12
            if px1 - pad_x <= cx <= px2 + pad_x and py1 - pad_y <= cy <= py2 + pad_y:
                return True
        return False

    @staticmethod
    def _box_dict(box, model, label_override: Optional[str] = None) -> Dict:
        class_id = int(box.cls[0])
        label = label_override or str(model.names[class_id]).lower()
        return {
            "label": label,
            "event_type": "risk_object",
            "confidence": float(box.conf[0]),
            "bbox": [float(value) for value in box.xyxy[0].tolist()],
            "requires_human_verification": True,
        }

    @staticmethod
    def _iou(first: List[float], second: List[float]) -> float:
        x1, y1 = max(first[0], second[0]), max(first[1], second[1])
        x2, y2 = min(first[2], second[2]), min(first[3], second[3])
        intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
        first_area = max(0.0, first[2] - first[0]) * max(0.0, first[3] - first[1])
        second_area = max(0.0, second[2] - second[0]) * max(0.0, second[3] - second[1])
        union = first_area + second_area - intersection
        return intersection / union if union else 0.0

    def _filter_firearm_candidates(
        self,
        candidates: List[Dict],
        frame_area: float,
        people: List[List[float]],
        allow_unattended: bool,
    ) -> List[Dict]:
        accepted = []
        for candidate in sorted(candidates, key=lambda item: item["confidence"], reverse=True):
            x1, y1, x2, y2 = candidate["bbox"]
            box_area_ratio = max(0.0, x2 - x1) * max(0.0, y2 - y1) / frame_area
            if box_area_ratio > self.max_firearm_area_ratio:
                continue
            near_person = self._is_near_person(candidate["bbox"], people) if people else False
            if people and not near_person and not allow_unattended:
                continue
            candidate["associated_with_person"] = near_person
            candidate["validation_weight"] = (
                0.5 if candidate.get("scan_mode") == "tile" and not near_person else 1.0
            )
            if any(self._iou(candidate["bbox"], other["bbox"]) >= 0.40 for other in accepted):
                continue
            accepted.append(candidate)
        return accepted

    def _deep_scan(self, frame, model) -> List[Dict]:
        """Scan overlapping tiles so small or distant firearms get more pixels."""
        height, width = frame.shape[:2]
        tile_width, tile_height = int(width * 0.58), int(height * 0.58)
        candidates = []
        for offset_y in (0, height - tile_height):
            for offset_x in (0, width - tile_width):
                tile = frame[offset_y:offset_y + tile_height, offset_x:offset_x + tile_width]
                results = model.predict(
                    tile,
                    conf=self.deep_scan_confidence,
                    imgsz=640,
                    verbose=False,
                    device=self.device,
                )
                for box in results[0].boxes:
                    candidate = self._box_dict(box, model, label_override="gun")
                    candidate["bbox"] = [
                        candidate["bbox"][0] + offset_x,
                        candidate["bbox"][1] + offset_y,
                        candidate["bbox"][2] + offset_x,
                        candidate["bbox"][3] + offset_y,
                    ]
                    candidate["scan_mode"] = "tile"
                    candidates.append(candidate)
        return candidates

    def detect(
        self,
        frame,
        person_boxes: Optional[List[List[float]]] = None,
        deep_scan: bool = False,
        allow_unattended: bool = False,
    ) -> List[Dict]:
        general_model, firearm_model = self._load()
        detections: List[Dict] = []

        if general_model is not None:
            results = general_model.predict(
                frame, conf=self.conf_threshold, verbose=False, device=self.device
            )
            for box in results[0].boxes:
                class_id = int(box.cls[0])
                label = str(general_model.names[class_id]).lower()
                if label in self.GENERAL_RISK_LABELS:
                    detections.append(self._box_dict(box, general_model))

        if firearm_model is None:
            return detections

        frame_area = float(frame.shape[1] * frame.shape[0])
        results = firearm_model.predict(
            frame,
            conf=self.firearm_conf_threshold,
            imgsz=self.firearm_imgsz,
            verbose=False,
            device=self.device,
        )
        people = person_boxes or []
        firearm_candidates = []
        for box in results[0].boxes:
            candidate = self._box_dict(box, firearm_model, label_override="gun")
            candidate["scan_mode"] = "full"
            firearm_candidates.append(candidate)
        accepted = self._filter_firearm_candidates(
            firearm_candidates, frame_area, people, allow_unattended
        )
        if deep_scan and not accepted:
            accepted = self._filter_firearm_candidates(
                self._deep_scan(frame, firearm_model), frame_area, people, allow_unattended
            )
        detections.extend(accepted)
        return detections


class TemporalRiskValidator:
    """Confirm a risk candidate across frames before raising an alert."""

    def __init__(self, required_hits: int = 2, window_seconds: float = 0.75, immediate_confidence: float = 0.80):
        self.required_hits = required_hits
        self.window_seconds = window_seconds
        self.immediate_confidence = immediate_confidence
        self._states: List[Dict] = []
        self._next_id = 1

    @staticmethod
    def _matches(first: List[float], second: List[float]) -> bool:
        if RiskObjectDetector._iou(first, second) >= 0.10:
            return True
        first_cx, first_cy = (first[0] + first[2]) / 2, (first[1] + first[3]) / 2
        second_cx, second_cy = (second[0] + second[2]) / 2, (second[1] + second[3]) / 2
        distance = math.hypot(first_cx - second_cx, first_cy - second_cy)
        diagonal = max(
            math.hypot(first[2] - first[0], first[3] - first[1]),
            math.hypot(second[2] - second[0], second[3] - second[1]),
        )
        return distance <= max(28.0, diagonal * 0.65)

    def update(self, detections: List[Dict], now_seconds: float) -> List[Dict]:
        self._states = [
            state for state in self._states
            if now_seconds - state["last_seen"] <= self.window_seconds
        ]
        confirmed = []
        matched_state_ids = set()
        for detection in sorted(detections, key=lambda item: item["confidence"], reverse=True):
            state = next((
                item for item in self._states
                if item["id"] not in matched_state_ids
                and item["label"] == detection["label"]
                and self._matches(item["bbox"], detection["bbox"])
            ), None)
            if state is None:
                state = {
                    "id": self._next_id,
                    "label": detection["label"],
                    "bbox": detection["bbox"],
                    "hits": 0,
                    "evidence_score": 0.0,
                    "max_confidence": 0.0,
                    "last_seen": now_seconds,
                }
                self._next_id += 1
                self._states.append(state)
            state["hits"] += 1
            state["evidence_score"] += float(detection.get("validation_weight", 1.0))
            state["bbox"] = detection["bbox"]
            state["last_seen"] = now_seconds
            state["max_confidence"] = max(state["max_confidence"], detection["confidence"])
            matched_state_ids.add(state["id"])
            strong_immediate = (
                detection["confidence"] >= self.immediate_confidence
                and detection.get("validation_weight", 1.0) >= 1.0
            )
            if state["evidence_score"] >= self.required_hits or strong_immediate:
                confirmed.append({
                    **detection,
                    "confidence": state["max_confidence"],
                    "temporal_hits": state["hits"],
                    "evidence_score": state["evidence_score"],
                    "candidate_id": state["id"],
                })
        return confirmed
