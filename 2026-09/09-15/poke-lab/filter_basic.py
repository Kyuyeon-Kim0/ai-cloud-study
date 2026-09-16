import pandas as pd

df = pd.read_csv("data/pokemon_100k.csv")

# 전설 포켓몬만
legend = df[df["legendary"] == 1]
print(len(legend))

# 불꽃 타입만
fire = df[df["type1"] == "불꽃"]

# 공격력 150 이상
strong = df[df["attack"] >= 150]

print(len(legend), len(fire), len(strong))


## 조건 결합
# 그리고 — 둘 다 만족
strong_fire = df[(df["type1"] == "불꽃") & (df["attack"] >= 150)]

# 또는 — 하나만 만족해도
fire_or_water = df[(df["type1"] == "불꽃") | (df["type1"] == "물")]

# 여러 값 중 하나 — isin 이 편합니다
some = df[df["type1"].isin(["불꽃", "물", "풀"])]

# 아닌 것 — 앞에 ~ 를 붙임
not_normal = df[~df["type1"].isin(["노말"])]

# 범위
mid = df[df["hp"].between(100, 150)]


## type2 가 있는 포켓몬 / 없는 포켓몬
# 빈 값인 행
single = df[df["type2"].isna()]

# 빈 값이 아닌 행
dual = df[df["type2"].notna()]

print(f"단일 타입 {len(single):,} / 복합 타입 {len(dual):,}")

# 빈 값을 다른 값으로 채우기
df["type2"] = df["type2"].fillna("없음")


## 열 고르기와 조합
# 조건으로 거른 뒤 필요한 열만
result = df[df["legendary"] == 1][["name", "type1", "attack", "hp"]]

# 읽기 쉽게 줄을 나눠 쓰기
result = (
    df[(df["legendary"] == 1) & (df["attack"] >= 150)]
    [["name", "type1", "attack"]]
    .sort_values("attack", ascending=False)
    .head(10)
)
print(result)