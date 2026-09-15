"""동일한 1,000행 CSV·JSON 파일을 네 가지 방식으로 읽어 비교한다."""

import csv
import gc
import json
from pathlib import Path

import pandas as pd

from measure import ResourceLogger


BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR / "static" / "data.csv"
JSON_PATH = BASE_DIR / "static" / "data.json"
LOG_PATH = BASE_DIR / "logs" / "resource_log.csv"
REPEAT_COUNT = 5


with ResourceLogger(str(LOG_PATH)) as logger:
    for _ in range(REPEAT_COUNT):
        data = logger.measure(
            lambda: list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline=""))),
            target=CSV_PATH.name,
            action="read",
            lib="csv",
        )
        logger.rows[-1].update(row_count=len(data), file_size_bytes=CSV_PATH.stat().st_size)
        del data
        gc.collect()

    for _ in range(REPEAT_COUNT):
        data = logger.measure(
            lambda: json.loads(JSON_PATH.read_text(encoding="utf-8")),
            target=JSON_PATH.name,
            action="read",
            lib="json",
        )
        logger.rows[-1].update(row_count=len(data), file_size_bytes=JSON_PATH.stat().st_size)
        del data
        gc.collect()

    for _ in range(REPEAT_COUNT):
        data = logger.measure(
            lambda: pd.read_csv(CSV_PATH),
            target=CSV_PATH.name,
            action="read",
            lib="pandas-csv",
        )
        logger.rows[-1].update(row_count=len(data), file_size_bytes=CSV_PATH.stat().st_size)
        del data
        gc.collect()

    for _ in range(REPEAT_COUNT):
        data = logger.measure(
            lambda: pd.read_json(JSON_PATH),
            target=JSON_PATH.name,
            action="read",
            lib="pandas-json",
        )
        logger.rows[-1].update(row_count=len(data), file_size_bytes=JSON_PATH.stat().st_size)
        del data
        gc.collect()
