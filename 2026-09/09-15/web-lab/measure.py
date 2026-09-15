"""여러 실습에서 공통으로 쓰는 자원 측정 및 CSV 기록 도구."""

import csv
import os
import time
from datetime import datetime

import psutil


FIELDS = [
    "time",
    "target",
    "action",
    "lib",
    "row_count",
    "file_size_bytes",
    "width",
    "height",
    "mem_before_mb",
    "mem_after_mb",
    "mem_delta_mb",
    "cpu_pct",
    "elapsed_s",
]


def to_mb(value: int) -> float:
    return round(value / 1024**2, 1)


def append_row(row: dict[str, object], path: str = "logs/resource_log.csv") -> None:
    """측정 한 줄을 CSV에 추가한다. 파일이 없으면 헤더부터 쓴다."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    is_new = not os.path.exists(path)

    with open(path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow(row)


class ResourceLogger:
    """측정 결과를 모아 컨텍스트 블록 종료 시 CSV에 누적한다."""

    def __init__(self, path: str = "logs/resource_log.csv") -> None:
        self.path = path
        self.rows: list[dict[str, object]] = []
        self.proc = psutil.Process(os.getpid())

    def __enter__(self) -> "ResourceLogger":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> bool:
        self.save()
        return False

    def measure(self, func: object, **info: object) -> object:
        self.proc.cpu_percent(interval=None)
        before = to_mb(self.proc.memory_info().rss)
        started = time.perf_counter()
        result = func()
        elapsed = time.perf_counter() - started
        after = to_mb(self.proc.memory_info().rss)

        row: dict[str, object] = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mem_before_mb": before,
            "mem_after_mb": after,
            "mem_delta_mb": round(after - before, 1),
            "cpu_pct": self.proc.cpu_percent(interval=None),
            "elapsed_s": round(elapsed, 3),
        }
        row.update(info)
        self.rows.append(row)
        return result

    def save(self) -> None:
        for row in self.rows:
            append_row(row, self.path)
