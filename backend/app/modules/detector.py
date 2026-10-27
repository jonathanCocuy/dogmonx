import logging
from typing import Optional
import numpy as np
from ultralytics import YOLO

logger = logging.getLogger(__name__)

_model: Optional[YOLO] = None
DOG_CLASS_ID = 16  # COCO class id for "dog"


def get_model() -> YOLO:
    global _model
    if _model is None:
        logger.info("Loading YOLO model (yolov8n.pt)...")
        _model = YOLO("yolov8n.pt")
        logger.info("YOLO model loaded")
    return _model


def detect_dogs(frame: np.ndarray) -> dict:
    """
    Runs YOLO on a frame and returns detection info.
    Returns: {dogs_count, bounding_boxes, motion_score, raw_labels}
    """
    model = get_model()
    results = model(frame, verbose=False)[0]

    dogs = []
    all_labels = []
    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = model.names[cls_id]
        all_labels.append(label)
        if cls_id == DOG_CLASS_ID and conf > 0.25:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            dogs.append({
                "confidence": round(conf, 3),
                "bbox": [round(x1), round(y1), round(x2), round(y2)],
            })

    return {
        "dogs_count": len(dogs),
        "dogs": dogs,
        "motion_score": 0.0,  # computed externally from frame diffs
        "other_objects": [l for l in all_labels if l != "dog"],
    }
