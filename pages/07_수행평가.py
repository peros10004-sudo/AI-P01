import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go

st.set_page_config(page_title="상품 가격 분석", layout="wide")

@st.cache_data
def load_csv(path: Path):
    df = pd.read_csv(path)
    return df

# --- Locate CSV in repository root ---
# This file lives in the pages/ folder but Streamlit's working directory is
# usually the repository root. Still we resolve robustly.
ROOT = Path(__file__).resolve().parents[1]
CSV_CANDIDATES = [ROOT / "prices.csv", ROOT / "data.csv", ROOT / "prices.csv", ROOT / "dataset.csv", ROOT / "products.csv", ROOT / "prices.csv"]
CSV_PATH = None
for p in CSV_CANDIDATES:
    if p.exists():
        CSV_PATH = p
        break

if CSV_PATH is None:
    st.error("CSV 파일을 루트 폴더에 넣어주세요. 기본 파일명: prices.csv (또는 data.csv, dataset.csv, products.csv). 또는 코드 상단의 CSV_PATH 변수를 수정하세요.")
    st.stop()

try:
    df = load_csv(CSV_PATH)
except Exception as e:
    st.error(f"CSV 파일을 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# --- Try to normalize column names (handle English/Korean variations) ---
col_map = {}
lower_cols = {c.lower(): c for c in df.columns}
# product column
for candidate in ["product", "상품", "item", "상품명", "name"]:
    if candidate in lower_cols:
        col_map['product'] = lower_cols[candidate]
        break
# region column
for candidate in ["region", "지역", "city", "시도", "시군구"]:
    if candidate in lower_cols:
        col_map['region'] = lower_cols[candidate]
        break
# neighborhood column
for candidate in ["neighborhood", "동네", "동", "district", "구"]:
    if candidate in lower_cols:
        col_map['neighborhood'] = lower_cols[candidate]
        break
# price column
for candidate in ["price", "가격", "cost", "단가"]:
    if candidate in lower_cols:
        col_map['price'] = lower_cols[candidate]
        break

required = ['product', 'neighborhood', 'price']
if not all(k in col_map for k in required):
    st.error("CSV에 필요한 열이 없습니다. 최소한 'product(상품)', 'neighborhood(동/동네)', 'price(가격)' 열이 필요합니다. 열 이름 예: product, neighborhood, price 또는 상품, 동, 가격")
    st.write("현재 발견된 열:", list(df.columns))
    st.stop()

# Rename for internal use
df = df.rename(columns={col_map['product']: 'product', col_map['neighborhood']: 'neighborhood', col_map['price']: 'price'})
if 'region' in col_map:
    df = df.rename(columns={col_map['region']: 'region'})
else:
    df['region'] = "(region 없음)"

# Ensure numeric prices
df['price'] = pd.to_numeric(df['price'], errors='coerce')

st.title("📊 상품별 지역 가격 비교")
st.markdown("상품을 선택하면 동네별 가격을 그래프로 보여주고, 가장 싼 동네와 가장 비싼 동네를 강조합니다.")

# Sidebar controls
with st.sidebar:
    st.header("설정")
    product_list = sorted(df['product'].dropna().unique())
    selected_product = st.selectbox("상품 선택", product_list)
    agg_method = st.radio("집계 방식", ("평균 (mean)", "중앙값 (median)", "최저값 (min)"), index=0)
    show_table = st.checkbox("원본 데이터 테이블 보기", value=False)
    top_n = st.number_input("상위/하위 몇 개 동네 표시?", min_value=1, max_value=50, value=10)

# Filter
prod_df = df[df['product'] == selected_product].copy()
if prod_df.empty:
    st.warning("선택한 상품에 데이터가 없습니다.")
    st.stop()

# Aggregate by neighborhood
if agg_method.startswith("평균"):
    agg = prod_df.groupby(['region', 'neighborhood'], dropna=False)['price'].mean().reset_index()
elif agg_method.startswith("중앙값"):
    agg = prod_df.groupby(['region', 'neighborhood'], dropna=False)['price'].median().reset_index()
else:
    agg = prod_df.groupby(['region', 'neighborhood'], dropna=False)['price'].min().reset_index()

agg = agg.dropna(subset=['price'])
agg = agg.sort_values('price', ascending=False)

# Identify extreme neighborhoods
most_expensive = agg.iloc[0]
cheapest = agg.iloc[-1]

# Plot
fig = go.Figure()
colors = []
for idx, row in agg.iterrows():
    if row['neighborhood'] == most_expensive['neighborhood'] and row['region'] == most_expensive['region']:
        colors.append('red')
    elif row['neighborhood'] == cheapest['neighborhood'] and row['region'] == cheapest['region']:
        colors.append('green')
    else:
        colors.append('lightslategray')

fig.add_trace(go.Bar(
    x=agg['neighborhood'].astype(str) + " (" + agg['region'].astype(str) + ")",
    y=agg['price'],
    marker_color=colors,
    hovertemplate='%{x}<br>가격: %{y}<extra></extra>'
))
fig.update_layout(title=f"{selected_product} — 동네별 가격 ({agg_method})", xaxis_title="동네 (지역)", yaxis_title="가격", margin=dict(t=50, b=200), height=600)

st.plotly_chart(fig, use_container_width=True)

# Show metrics
col1, col2 = st.columns(2)
col1.metric("가장 비싼 동네", f"{most_expensive['neighborhood']} ({most_expensive['region']})", f"{most_expensive['price']:.2f}")
col2.metric("가장 싼 동네", f"{cheapest['neighborhood']} ({cheapest['region']})", f"{cheapest['price']:.2f}")

# Show top/bottom tables
st.subheader("상위/하위 동네")
left, right = st.columns(2)
with left:
    st.write(f"상위 {top_n} (비싼)")
    st.dataframe(agg.head(top_n).reset_index(drop=True))
with right:
    st.write(f"하위 {top_n} (싼)")
    st.dataframe(agg.tail(top_n).reset_index(drop=True))

if show_table:
    st.subheader("필터된 원본 데이터")
    st.dataframe(prod_df)

# Download aggregated results
csv_bytes = agg.to_csv(index=False).encode('utf-8')
st.download_button(label="Aggregated CSV 다운로드", data=csv_bytes, file_name=f"{selected_product}_aggregated.csv", mime='text/csv')

st.markdown("---")
st.markdown("### 사용 팁")
st.markdown("- CSV 파일은 루트 폴더에 `prices.csv` (또는 `data.csv`, `dataset.csv`, `products.csv`)로 넣어주세요.\n- 열 이름이 다르면 코드 상단의 `CSV_CANDIDATES` 또는 컬럼 매핑 부분을 수정하세요.\n- 이 파일을 GitHub에 올릴 때는 `pages/01_product_price_analysis.py` 경로를 유지하면 Streamlit Cloud 등에서 자동으로 페이지로 인식됩니다.")

# Requirements block (copy into requirements.txt)
# --- BEGIN REQUIREMENTS ---
# streamlit
# pandas
# plotly
# numpy
# --- END REQUIREMENTS ---

# End of file

