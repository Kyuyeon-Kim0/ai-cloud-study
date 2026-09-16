import pandas as pd

df = pd.read_csv("data/pokemon_100k.csv")

# 타입별 마릿수
print(df.groupby("type1").size())

# 타입별 평균 공격력
print(df.groupby("type1")["attack"].mean())

# 세대별 최대 체력
print(df.groupby("generation")["hp"].max())

# 여러 집계 한번에
result = df.groupby("type1").agg(
    마릿수=("id", "count"),
    평균공격=("attack", "mean"),
    최대체력=("hp", "max"),
    전설수=("legendary", "sum"),
)

result = result.round(1).sort_values("평균공격", ascending=False)
print(result)

# 세대별, 그 안에서 타입별
g = df.groupby(["generation", "type1"])["attack"].mean()
print(g.head(12))

# 표 형태로 펼치기 — 행은 세대, 열은 타입
table = df.pivot_table(
    index="generation",
    columns="type1",
    values="attack",
    aggfunc="mean",
).round(1)
print(table)
