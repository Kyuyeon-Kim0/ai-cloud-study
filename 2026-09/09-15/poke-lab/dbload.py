"""
pokemon_1m.csv를 SQLite 데이터베이스(pokemon.db)로 변환하고 조회하는 예제입니다.

실행 방법
    python dbload.py

이 파일은 매 실행 때 data/pokemon.db를 새로 만듭니다. 따라서 CSV가 바뀌어도
이전 DB 내용이 남아 있지 않습니다. SQLite는 파이썬 표준 라이브러리(sqlite3)에
포함되어 있어 별도의 패키지 설치가 필요 없습니다.
"""

import csv
import sqlite3
import time
from pathlib import Path


# Path(__file__)을 기준으로 경로를 만들면, 어느 폴더에서 실행하더라도 같은
# poke-lab/data 폴더의 파일을 사용합니다.
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "pokemon_1m.csv"
DB_PATH = BASE_DIR / "data" / "pokemon.db"
TABLE_NAME = "pokemon"


def create_database() -> None:
    """CSV의 모든 행을 읽어 새 SQLite DB 파일과 pokemon 테이블을 만든다."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {CSV_PATH}")

    # 새 DB라는 조건을 지키기 위해 기존 파일이 있으면 먼저 삭제합니다.
    # unlink()는 지정한 파일 하나만 삭제하며 폴더나 다른 파일에는 영향이 없습니다.
    if DB_PATH.exists():
        DB_PATH.unlink()

    started_at = time.perf_counter()

    # connect()가 .db 파일을 만들고, with 블록이 정상 종료되면 commit(),
    # 예외가 나면 rollback() 및 연결 종료를 처리합니다.
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        # CSV 헤더의 각 열에 맞춰 SQLite 테이블을 정의합니다.
        # type2는 CSV에서 비어 있을 수 있으므로 NULL을 허용합니다.
        cursor.execute(
            """
            CREATE TABLE pokemon (
                id        INTEGER PRIMARY KEY,
                name      TEXT NOT NULL,
                type1     TEXT NOT NULL,
                type2     TEXT,
                generation INTEGER NOT NULL,
                hp        INTEGER NOT NULL,
                attack    INTEGER NOT NULL,
                defense   INTEGER NOT NULL,
                speed     INTEGER NOT NULL,
                legendary INTEGER NOT NULL CHECK (legendary IN (0, 1))
            )
            """
        )

        # type1 및 legendary 조건 검색을 빠르게 하기 위한 인덱스입니다.
        # 인덱스는 필터/그룹 조회 성능에는 도움이 되지만 DB 파일 크기는 조금 늘립니다.
        cursor.execute("CREATE INDEX idx_pokemon_type1 ON pokemon(type1)")
        cursor.execute("CREATE INDEX idx_pokemon_legendary ON pokemon(legendary)")

        insert_sql = """
            INSERT INTO pokemon
            (id, name, type1, type2, generation, hp, attack, defense, speed, legendary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # DictReader로 헤더 이름을 기준으로 읽으므로 CSV 열 순서가 바뀌어도 안전합니다.
        # executemany()에 행 묶음을 전달해 INSERT를 한 줄씩 실행하는 것보다 효율적입니다.
        batch: list[tuple[object, ...]] = []
        batch_size = 10_000
        inserted_count = 0

        with CSV_PATH.open("r", encoding="utf-8", newline="") as csv_file:
            for row in csv.DictReader(csv_file):
                batch.append(
                    (
                        int(row["id"]),
                        row["name"],
                        row["type1"],
                        row["type2"] or None,  # 빈 문자열은 SQL NULL로 저장
                        int(row["generation"]),
                        int(row["hp"]),
                        int(row["attack"]),
                        int(row["defense"]),
                        int(row["speed"]),
                        int(row["legendary"]),
                    )
                )

                if len(batch) == batch_size:
                    cursor.executemany(insert_sql, batch)
                    inserted_count += len(batch)
                    batch.clear()

            # 마지막 묶음은 batch_size보다 작을 수 있으므로 별도로 넣습니다.
            if batch:
                cursor.executemany(insert_sql, batch)
                inserted_count += len(batch)

    elapsed = time.perf_counter() - started_at
    print(f"DB 생성 완료: {DB_PATH}")
    print(f"CSV → DB 저장 건수: {inserted_count:,}건 ({elapsed:.3f}초)")


def show_database_results() -> None:
    """DB를 다시 열어 전체 건수, 분류별 건수/비율, 합계와 평균을 출력한다."""
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        # fetchone()[0]은 SELECT COUNT(*) 결과의 첫 번째 열(전체 행 수)입니다.
        total_count = cursor.execute("SELECT COUNT(*) FROM pokemon").fetchone()[0]
        print(f"\n[전체 건수]\n{total_count:,}건")

        print("\n[type1별 건수 및 비율]")
        print(f"{'타입':<10} {'건수':>12} {'비율':>10}")
        for type1, count in cursor.execute(
            """
            SELECT type1, COUNT(*)
            FROM pokemon
            GROUP BY type1
            ORDER BY COUNT(*) DESC, type1
            """
        ):
            ratio = count / total_count * 100 if total_count else 0
            print(f"{type1:<10} {count:>12,} {ratio:>9.2f}%")

        # SUM과 AVG는 DB 안에서 계산하므로 파이썬으로 100만 행을 다시 가져올 필요가 없습니다.
        hp_sum, hp_avg, attack_sum, attack_avg = cursor.execute(
            """
            SELECT SUM(hp), AVG(hp), SUM(attack), AVG(attack)
            FROM pokemon
            """
        ).fetchone()
        print("\n[합산 및 평균]")
        print(f"HP     합계: {hp_sum:,} / 평균: {hp_avg:.2f}")
        print(f"공격력 합계: {attack_sum:,} / 평균: {attack_avg:.2f}")


def compare_count_speed() -> None:
    """동일한 '전체 행 수 세기' 작업으로 CSV 순차 읽기와 DB COUNT 시간을 비교한다."""
    # CSV는 텍스트 파일이므로 행 수를 세려면 일반적으로 파일 전체를 순차적으로 읽습니다.
    csv_started_at = time.perf_counter()
    with CSV_PATH.open("r", encoding="utf-8", newline="") as csv_file:
        csv_count = sum(1 for _ in csv.DictReader(csv_file))
    csv_elapsed = time.perf_counter() - csv_started_at

    # SQLite의 COUNT(*)는 저장된 테이블을 SQL로 조회합니다. OS 파일 캐시, PC 사양,
    # 인덱스, 첫 실행 여부에 따라 시간이 달라질 수 있으므로 한 번의 결과는 참고용입니다.
    db_started_at = time.perf_counter()
    with sqlite3.connect(DB_PATH) as connection:
        db_count = connection.execute("SELECT COUNT(*) FROM pokemon").fetchone()[0]
    db_elapsed = time.perf_counter() - db_started_at

    print("\n[전체 건수 확인 속도 비교]")
    print(f"CSV 순차 읽기: {csv_count:,}건 / {csv_elapsed:.6f}초")
    print(f"DB COUNT(*) : {db_count:,}건 / {db_elapsed:.6f}초")
    if db_elapsed > 0:
        print(f"이번 실행의 CSV/DB 시간 비율: {csv_elapsed / db_elapsed:.2f}배")


if __name__ == "__main__":
    create_database()
    show_database_results()
    compare_count_speed()
