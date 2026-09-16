import streamlit as st
import pandas as pd
import time
from measure import ResourceLogger

## Step 1. 페이지 설정

st.set_page_config(page_title="포켓몬 대시보드", layout="wide")
st.title("포켓몬 대시보드")
st.write("여기에 내용이 들어갑니다")

## Step 2. CSV 읽기

def load_data():
    """CSV 를 읽어 표로 돌려준다. 걸린 시간도 함께."""
    t0 = time.perf_counter()
    df = pd.read_csv("data/pokemon_1m.csv")
    elapsed = time.perf_counter() - t0
    return df, elapsed

with ResourceLogger() as logger:
    df, load_time = logger.measure(
        load_data,
        target="pokemon_1m",
        action="dashboard-base",
        lib="pandas-read",
    )
st.caption(f"데이터 {len(df):,} 행 · 읽는 데 {load_time:.2f} 초")

## Step 3. 지표 표시

c1, c2, c3, c4 = st.columns(4)      # 가로로 4칸

c1.metric("전체", f"{len(df):,}")
c2.metric("전설", f"{int(df['legendary'].sum()):,}")
c3.metric("평균 공격", f"{df['attack'].mean():.1f}")
c4.metric("최대 체력", f"{int(df['hp'].max())}")

## Step 4. 필터

st.sidebar.header("필터")

types = sorted(df["type1"].unique())
sel_types = st.sidebar.multiselect("타입", types, default=types[:3])

gen = st.sidebar.slider("세대", 1, 9, (1, 9))
only_legend = st.sidebar.checkbox("전설만 보기")

# 필터 적용 — 1권의 필터링 문법 그대로
def apply_filters():
    filtered = df[df["type1"].isin(sel_types)]
    filtered = filtered[filtered["generation"].between(gen[0], gen[1])]
    if only_legend:
        filtered = filtered[filtered["legendary"] == 1]
    return filtered


with ResourceLogger() as logger:
    f = logger.measure(
        apply_filters,
        target="pokemon_1m",
        action="dashboard-base",
        lib="pandas-filter",
    )

st.caption(f"조건에 맞는 포켓몬 {len(f):,} 마리")

left, right = st.columns(2)

## Step 5. 차트

with left:
    st.subheader("타입별 마릿수")
    by_type = f["type1"].value_counts()
    st.bar_chart(by_type)

with right:
    st.subheader("세대별 평균 공격력")
    by_gen = f.groupby("generation")["attack"].mean()
    st.line_chart(by_gen)


## Step 6. 테이블

st.subheader("공격력 상위 20")

top = f.nlargest(20, "attack")[
    ["name", "type1", "type2", "generation", "hp", "attack"]
]
st.dataframe(top, use_container_width=True)

# 화면 아래에 성능 정보 표시
st.divider()
st.caption(f"읽기 {load_time:.2f}초 · 전체 {len(df):,}행 · 필터 후 {len(f):,}행")