"""Run YOLOv8 on a video and produce annotated video + statistics."""
import json
from pathlib import Path
from collections import defaultdict

import cv2
from ultralytics import YOLO

from .config import MODEL_PATH, JOBS_DIR

"""Github add/commit test"""
def run(job_id: str) -> tuple[dict, str | None]:
    """
    Process video for job_id. Reads from jobs/<id>/input.mp4,
    writes to jobs/<id>/output.mp4 and jobs/<id>/stats.json.
    Returns (stats_dict, error_message). error_message is None on success.
    """
    job_dir = JOBS_DIR / job_id
    input_path = job_dir / "input.mp4"
    output_path = job_dir / "output.mp4"

    if not input_path.exists():
        return {}, f"Input video not found: {input_path}"

    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        return {}, f"Failed to load model: {e}"

    try:
        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            return {}, f"Could not open video: {input_path}"

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (w, h))

        detections_by_class = defaultdict(int)
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1

            results = model.predict(frame, verbose=False)
            if not results:
                out.write(frame)
                continue

            r = results[0]
            ann_frame = r.plot()
            out.write(ann_frame)

            if r.boxes is not None:
                names = r.names
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    name = names.get(cls_id, f"class_{cls_id}")
                    detections_by_class[name] += 1

        cap.release()
        out.release()

        out_stats = {
            "detections_by_class": dict(detections_by_class),
            "total_frames": frame_count,
        }

        stats_path = job_dir / "stats.json"
        stats_path.write_text(json.dumps(out_stats, indent=2), encoding="utf-8")

        return out_stats, None

    except Exception as e:
        return {}, str(e)
