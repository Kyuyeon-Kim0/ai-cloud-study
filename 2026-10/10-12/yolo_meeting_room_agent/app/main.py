import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from app.config import Settings
from app.analyzer import RoomAnalyzer
from app.agent import write_report
from app.guardrails import validate_detection


def main() -> None:
    parser = argparse.ArgumentParser(description='YOLO meeting room analysis with optional OpenAI agent')
    parser.add_argument('--input', type=Path, default=Path('images'))
    parser.add_argument('--output', type=Path, default=Path('outputs'))
    args = parser.parse_args()
    settings = Settings()
    settings.validate()
    args.output.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in args.input.iterdir() if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'})
    if not files:
        print('No images found in', args.input)
        return
    analyzer = RoomAnalyzer(settings)
    records = []
    for image in files:
        try:
            result = analyzer.analyze(image, args.output)
            validate_detection(result)
            result['timestamp_utc'] = datetime.now(timezone.utc).isoformat()
            result['agent'] = None
            if settings.enable_agent:
                try:
                    result['agent'] = write_report(result, settings.model)
                except Exception as exc:
                    result['agent_error'] = f'{type(exc).__name__}: agent unavailable; deterministic result retained'
            records.append(result)
            print(f"\n[{image.name}]")
            print(f"탐지 결과: 인원 {result['people']}명 / 상태 {result['status']}")
            if result['agent']:
                print(f"에이전트 요약: {result['agent']['summary']}")
                print(f"활용 제안: {result['agent']['recommendation']}")
                print(f"분석 한계: {result['agent']['limitations']}")
            elif 'agent_error' in result:
                print(f"에이전트 응답을 생성하지 못했습니다: {result['agent_error']}")
            elif not settings.enable_agent:
                print('에이전트 분석: 비활성화됨 (ENABLE_AGENT=false)')
        except Exception as exc:
            print(f'Skipped {image.name}: {type(exc).__name__}: {exc}')
    (args.output / 'results.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    with (args.output / 'summary.csv').open('w', encoding='utf-8-sig', newline='') as fp:
        writer = csv.DictWriter(fp, fieldnames=['image', 'people', 'chairs', 'tables', 'status', 'timestamp_utc'])
        writer.writeheader()
        for r in records:
            writer.writerow({'image': r['image'], 'people': r['people'], 'chairs': r['counts']['chair'],
                             'tables': r['counts']['dining table'], 'status': r['status'], 'timestamp_utc': r['timestamp_utc']})

if __name__ == '__main__':
    main()
