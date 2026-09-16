import json, os
import pandas as pd
import time, requests
from measure import ResourceLogger

CACHE = "data/pokemon_api.json"

def extract(data):
    """API 응답에서 필요한 값만 꺼내 딕셔너리 하나로."""
    types = [t["type"]["name"] for t in data["types"]]
    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}

    return {
        "id": data["id"],
        "name": data["name"],
        "type1": types[0],
        "type2": types[1] if len(types) > 1 else "",
        "height": data["height"],
        "weight": data["weight"],
        "hp": stats.get("hp", 0),
        "attack": stats.get("attack", 0),
        "defense": stats.get("defense", 0),
        "speed": stats.get("speed", 0),
        "image": data["sprites"]["front_default"],
    }

def fetch_many(n=50):
    rows, total_bytes = [], 0
    for i in range(1, n + 1):
        url = f"https://pokeapi.co/api/v2/pokemon/{i}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            total_bytes += len(res.content)
            rows.append(extract(res.json()))
        time.sleep(0.1)              # 서버 배려 — 아래 설명
    print(f"전송량 {total_bytes/1024/1024:.1f} MB")
    return rows

with ResourceLogger() as logger:
    rows = logger.measure(lambda: fetch_many(50),
                          target="pokeapi", action="fetch", lib="requests-50")
print(len(rows), "마리")

def load_or_fetch(n=50):
    """저장된 것이 있으면 읽고, 없으면 받아서 저장한다."""
    if os.path.exists(CACHE):
        print("저장된 파일 사용")
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)

    print("API 에서 받는 중...")
    rows = fetch_many(n)
    os.makedirs("data", exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    return rows

rows = load_or_fetch(50)

# pandas 로 넘기면 1권에서 배운 것을 그대로 씁니다
df = pd.DataFrame(rows)
df.to_csv("data/pokemon_api.csv", index=False, encoding="utf-8-sig")
print(df.head())