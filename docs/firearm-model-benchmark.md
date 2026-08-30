# Firearm detector selection notes

## Local validation set

The comparison used nine positive frames taken from human-reviewed Event
timestamps in the project's own school-camera videos, plus 23 regularly sampled
frames from two videos with no reviewed firearm candidate. This is a small,
domain-specific smoke test, not a safety certification or a replacement for a
proper labeled holdout set.

| Model | Positive frames found | Negative sampled frames flagged | Decision |
|---|---:|---:|---|
| Subh775 Firearm YOLOv8n | 8 / 9 | 0 / 23 | Primary model |
| cosgun99 Gun/Knife YOLO11n | 2 / 9 | 2 / 23 | Rejected for this camera domain |
| Subh775 Threat YOLOv8n | 2 / 9 | 2 / 23 | Rejected for this camera domain |

The public metrics supplied by each author were treated as screening evidence
only. The choice was made from the local footage because camera angle, toy/prop
appearance, distance, occlusion, and compression differ from the authors'
datasets.

## Pipeline improvements

- The strongest local model remains the primary detector.
- A periodic overlapping-tile pass increases the apparent size of distant objects.
- Normal candidates require repeated spatially consistent evidence within 0.75 s.
- Unattended candidates seen only by the tile scan carry half evidence weight.
- A candidate at 80% confidence can alert immediately only when it came from a
  full-frame scan or is associated with a detected person.
- Oversized boxes and overlapping duplicates are filtered before validation.
- Every result remains a Potential Risk candidate requiring human review.

## Sources

- https://huggingface.co/Subh775/Firearm_Detection_Yolov8n
- https://huggingface.co/cosgun99/gun-knife-yolo11n
- https://huggingface.co/Subh775/Threat-Detection-YOLOv8n
