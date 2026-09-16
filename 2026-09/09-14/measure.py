import os, csv, time, psutil
from datetime import datetime
import os, re


def to_mb(bytes_value):
    """바이트를 MB로 바꿔 소수 첫째 자리까지."""
    return round(bytes_value / 1024**2, 1)


FIELDS = ["time", "target", "action", "lib", "width", "height",
          "mem_before_mb", "mem_after_mb", "mem_delta_mb",
          "cpu_pct", "elapsed_s"]

def append_row(row, path="logs/resource_log.csv"):
    """측정 한 줄을 CSV에 추가한다. 파일이 없으면 헤더부터 쓴다."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    is_new = not os.path.exists(path)

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow(row)


PROC = psutil.Process(os.getpid())

def measure(func, target="", action="", lib="", width="", height=""):
    """func 을 실행하면서 메모리·CPU·시간을 측정해 딕셔너리로 돌려준다."""
    PROC.cpu_percent(interval=None)        # 기준점
    before = to_mb(PROC.memory_info().rss)
    t0 = time.perf_counter()

    result = func()                        # ← 실제 작업

    elapsed = time.perf_counter() - t0
    after = to_mb(PROC.memory_info().rss)
    cpu = PROC.cpu_percent(interval=None)

    row = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "target": target, "action": action, "lib": lib,
        "width": width, "height": height,
        "mem_before_mb": before, "mem_after_mb": after,
        "mem_delta_mb": round(after - before, 1),
        "cpu_pct": cpu, "elapsed_s": round(elapsed, 3),
    }
    return row, result


class ResourceLogger:
    def __init__(self, path="logs/resource_log.csv"):
        self.path = path
        self.rows = []
        self.proc = psutil.Process(os.getpid())

    def __enter__(self):
        return self                # with ... as logger 의 logger

    def __exit__(self, exc_type, exc_value, tb):
        self.save()                  # 오류가 나도 실행됩니다
        return False               # 오류는 숨기지 않고 그대로 전달

    def measure(self, func, **info):
        self.proc.cpu_percent(interval=None)
        before = to_mb(self.proc.memory_info().rss)
        t0 = time.perf_counter()
        result = func()
        elapsed = time.perf_counter() - t0
        after = to_mb(self.proc.memory_info().rss)

        row = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "mem_before_mb": before, "mem_after_mb": after,
               "mem_delta_mb": round(after - before, 1),
               "cpu_pct": self.proc.cpu_percent(interval=None),
               "elapsed_s": round(elapsed, 3)}
        row.update(info)             # target, lib, width, height ...
        self.rows.append(row)
        return result

    def save(self):
        for r in self.rows:
            append_row(r, self.path)