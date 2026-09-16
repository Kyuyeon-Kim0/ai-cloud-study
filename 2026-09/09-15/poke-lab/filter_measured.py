import pandas as pd
from measure import ResourceLogger

df = pd.read_csv("data/pokemon_1m.csv")   # 100만 행

with ResourceLogger() as logger:
    logger.measure(lambda: df[df["legendary"] == 1],
                   target="pokemon_1m", action="filter", lib="단일조건")
    logger.measure(lambda: df[(df["type1"] == "불꽃") &
                                 (df["attack"] >= 150)],
                   target="pokemon_1m", action="filter", lib="복합조건")