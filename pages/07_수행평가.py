# pages/01_product_prices.py
# Streamlit app — 상품 선택 시 지역(동)별 가격 그래프 표시, 최저가/최고가 동 표시
# 위치: 이 파일은 프로젝트의 pages/ 폴더에 넣어주세요.
# CSV 파일(데이터)은 프로젝트 루트에 'pp.csv' 또는 원하는 이름으로 두세요.
# 파일 경로: 이 파일은 pages/ 아래에 있으므로 CSV 파일은 상위 폴더('../pp.csv')에서 로드합니다.

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="상품별 지역 가격 비교", layout="wide")

@st.cache_data
def load_data(csv_path: Path):
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}\n루트에 pp.csv 파일이 있는지 확인하세요.")
    df = pd.read_csv(csv_path)
    return df

# --- helper utilities ----------------------------------------------------
PRODUCT_KEYS = ["product", "상품", "상품명", "item", "item_name", "품목"]
PRICE_KEYS = ["price", "가격", "단가", "cost", "amount"]
REGION_KEYS = ["동", "읍면동", "시군구", "구", "군", "시", "도", "지역", "location", "region", "addr", "address"]


def find_column(cols, candidates):
    for c in cols:
        for k in candidates:
            if k.lower() == str(c).lower():
                return c
    # fuzzy contains
    for c in cols:
        for k in candidates:
            if k.lower() in str(c).lower():
                return c
    return None


# --- main ----------------------------------------------------------------
st.title("🛒 상품별 지역(동) 가격 비교")

# compute CSV path relative to this file (pages/..)
BASE = Path(__file__).resolve().parents[1]
CSV_DEFAULT = BASE / "pp.csv"

# allow user to override path if desired
csv_path_input = st.text_input("CSV 경로 (pages/ 폴더에서 상대) — 기본: '../pp.csv'", value=str(CSV_DEFAULT))
try:
    csv_path = Path(csv_path_input).expanduser()
    df = load_data(csv_path)
except Exception as e:
    st.error(f"데이터 로드 실패: {e}")
    st.stop()

st.write(f"데이터 불러옴 — 행: {len(df):,}  열: {len(df.columns)}")

# try to detect useful columns
cols = list(df.columns)
product_col = find_column(cols, PRODUCT_KEYS) or st.selectbox("상품(또는 항목) 컬럼을 선택하세요", options=cols, index=0)
price_col = find_column(cols, PRICE_KEYS) or st.selectbox("가격 컬럼을 선택하세요", options=cols, index=min(1, len(cols)-1))

# region/dong detection: prefer the most-granular available (동/읍면동)
region_col = find_column(cols, ["동", "읍면동"]) or find_column(cols, REGION_KEYS)
if not region_col:
    region_col = st.selectbox("지역(동 등)으로 사용할 컬럼을 선택하세요", options=cols, index=min(2, len(cols)-1))

# Ensure price column numeric
try:
    df[price_col] = pd.to_numeric(df[price_col].astype(str).str.replace(',', '').str.strip(), errors='coerce')
except Exception:
    df[price_col] = pd.to_numeric(df[price_col], errors='coerce')

# build product list
product_list = df[product_col].dropna().unique().tolist()
product_list_sorted = sorted(product_list, key=lambda x: str(x))

selected_product = st.selectbox("상품 선택", options=product_list_sorted)

# filter
filtered = df[df[product_col] == selected_product].copy()
if filtered.empty:
    st.warning("선택한 상품의 데이터가 없습니다.")
    st.stop()

# create a region label — if there are multiple region-like columns, combine them
# find additional region columns (구/군/시 등) to build a full label if present
additional_region_cols = [c for c in cols if c not in [product_col, price_col, region_col] and any(k.lower() in str(c).lower() for k in ["구", "군", "시", "도", "읍", "면"])]

if additional_region_cols:
    filtered['region_label'] = filtered[[region_col] + additional_region_cols].astype(str).agg(' '.join, axis=1)
else:
    filtered['region_label'] = filtered[region_col].astype(str)

# aggregate by region_label
agg = filtered.groupby('region_label', dropna=False)[price_col].agg(['count','mean','median','min','max']).reset_index()
agg = agg.rename(columns={ 'mean':'avg_price', 'min':'min_price', 'max':'max_price' })
# use avg_price for sorting/plotting
agg = agg.sort_values('avg_price', ascending=True)

# highlight min and max region
min_row = agg.iloc[0]
max_row = agg.iloc[-1]

col1, col2 = st.columns([3,1])
with col1:
    st.subheader(f"{selected_product} — 지역별 평균 가격")
    # plotly bar with color for min/max
    agg['color_flag'] = 'normal'
    agg.loc[agg['region_label'] == min_row['region_label'], 'color_flag'] = 'cheapest'
    agg.loc[agg['region_label'] == max_row['region_label'], 'color_flag'] = 'most_expensive'

    fig = px.bar(agg, x='region_label', y='avg_price', hover_data=['count','median','min_price','max_price'],
                 title=f"{selected_product} — 지역별 평균 가격 (단위: {price_col})")
    # set bar color manually by mapping to marker color sequence
    colors = []
    for flag in agg['color_flag']:
        if flag == 'cheapest':
            colors.append('green')
        elif flag == 'most_expensive':
            colors.append('red')
        else:
            colors.append(None)
    # Apply colors
    for i, bar in enumerate(fig.data):
        # When plotly creates a single trace for bars, set marker colors directly
        pass
    fig.update_traces(marker_color=colors)
    fig.update_layout(xaxis_title='지역(동)', yaxis_title=f'평균 {price_col}', xaxis_tickangle=-45, height=600)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.metric(label="가장 싼 동/지역", value=min_row['region_label'], delta=f"평균 {min_row['avg_price']:.0f} {price_col}")
    st.metric(label="가장 비싼 동/지역", value=max_row['region_label'], delta=f"평균 {max_row['avg_price']:.0f} {price_col}")
    st.markdown("---")
    st.write("**상세 통계 (선택한 상품)**")
    st.dataframe(agg[['region_label','count','avg_price','median','min_price','max_price']].sort_values('avg_price'))

# download filtered rows for the selected product
csv_bytes = filtered.to_csv(index=False).encode('utf-8-sig')
st.download_button(label="선택 상품 데이터 다운로드 (CSV)", data=csv_bytes, file_name=f"{selected_product}_data.csv", mime='text/csv')

st.info("참고: 컬럼명이 다양할 수 있어 앱이 자동으로 적절한 컬럼을 추정합니다. 필요한 경우 상단에서 수동으로 컬럼을 선택하세요.")

# ----------------- requirements.txt content ------------------------------
# 아래는 requirements.txt에 넣을 패키지들입니다. 이 파일을 프로젝트 루트에 requirements.txt로 저장하세요.
# streamlit
# pandas
# plotly

# (선택) 만약 다른 시각화 라이브러리를 원한다면 추가하세요.

