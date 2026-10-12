from pathlib import Path
from ultralytics import YOLO
from app.config import Settings

ALLOWED = {'person', 'chair', 'dining table'}

class RoomAnalyzer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = YOLO(settings.yolo_model)

    def analyze(self, image: Path, output_dir: Path) -> dict:
        if image.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
            raise ValueError('Unsupported image extension')
        if image.stat().st_size > 15 * 1024 * 1024:
            raise ValueError('Image too large (max 15 MB)')
        results = self.model.predict(source=str(image), conf=self.settings.confidence, verbose=False)
        result = results[0]
        counts = {'person': 0, 'chair': 0, 'dining table': 0}
        boxes = []
        for box in result.boxes:
            name = result.names[int(box.cls[0])]
            if name not in ALLOWED:
                continue
            counts[name] += 1
            boxes.append({'label': name, 'confidence': round(float(box.conf[0]), 3),
                          'xyxy': [round(float(x), 1) for x in box.xyxy[0].tolist()]})
        n = counts['person']
        status = ('비어 있음' if n == 0 else '소규모' if n <= self.settings.small_max
                  else '혼잡' if n >= self.settings.crowded_min else '보통')
        output_dir.mkdir(parents=True, exist_ok=True)
        annotated = output_dir / f'{image.stem}_boxed.jpg'
        from PIL import Image
        Image.fromarray(result.plot()[..., ::-1]).save(annotated)
        return {'image': image.name, 'counts': counts, 'people': n, 'status': status,
                'boxes': boxes, 'annotated_image': str(annotated),
                'warning': '이미지 한 장의 탐지 결과이며 실제 예약/재실 상태를 보장하지 않습니다.'}
