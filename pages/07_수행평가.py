# pages/price_by_region.py
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="지역별 가격 비교", layout="wide")

st.title("상품별 지역 가격 비교")
st.markdown("`pp.csv` (루트)에 있는 데이터를 사용합니다. 상품을 선택하면 동네별 가격을 그래프로 보여주고, 가장 싼/비싼 동네를 표시합니다.")

@st.cache_data
def load_data(path="pp.csv"):
    # 인코딩 문제를 대비해 여러 인코딩 시도
    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8", "latin1"]
    for e in encodings:
        try:
            df = pd.read_csv(path, encoding=e)
            return df, e
        except Exception:
            continue
    raise ValueError(f"파일을 읽을 수 없습니다. 시도한 인코딩: {encodings}")

df, used_encoding = load_data("pp.csv")
st.caption(f"데이터 로드: {used_encoding} 인코딩 사용")

# 기본 컬럼 이름 추출
all_cols = list(df.columns)
# 보통 앞쪽에 '품목', '조사기준', '구평균가격' 같은 컬럼이 있으므로 제외하고 동네 컬럼만 선택
non_region_cols = {"품목", "조사기준", "구평균가격"}
region_cols = [c for c in all_cols if c not in non_region_cols]

if "품목" not in df.columns:
    st.error("CSV에 '품목' 컬럼이 없습니다. 컬럼명을 확인해주세요.")
    st.stop()

# 상품 리스트
products = df["품목"].astype(str).unique().tolist()
products.sort()

col1, col2 = st.columns([2, 1])

with col1:
    selected = st.selectbox("상품 선택", products)

with col2:
    st.write("데이터 요약")
    st.write(f"전체 행: {len(df)}")
    st.write(f"지역(동네) 수: {len(region_cols)}")

# 선택된 상품의 행(들) 필터
sel_df = df[df["품목"].astype(str) == str(selected)]

if sel_df.empty:
    st.warning("선택한 상품의 데이터가 없습니다.")
    st.stop()

# 여러 행이 있을 수 있으므로(조사기준 등), 평균을 내거나 첫 행 사용
# 우선 각 동네별 숫자값으로 변환(문자열에 콤마가 있는 경우 처리)
def to_numeric_series(s):
    return pd.to_numeric(s.astype(str).str.replace(",", "").str.strip(), errors="coerce")

# 합치기: 동네별 평균(숫자)
region_values = {}
for c in region_cols:
    vals = to_numeric_series(sel_df[c])
    # 평균을 사용 (가능하면 single value)
    region_values[c] = vals.mean(skipna=True)

region_ser = pd.Series(region_values).dropna()
if region_ser.empty:
    st.error("동네별 숫자 데이터가 없습니다. CSV 값을 확인하세요.")
    st.stop()

# 최저/최고 동네
min_region = region_ser.idxmin()
min_price = region_ser.min()
max_region = region_ser.idxmax()
max_price = region_ser.max()

# 그래프 준비 (Altair)
chart_df = region_ser.reset_index()
chart_df.columns = ["dong", "price"]
chart_df = chart_df.sort_values("price", ascending=False)

highlight = alt.selection_single(fields=["dong"], bind="legend", empty="none")
base = alt.Chart(chart_df).encode(
    x=alt.X("dong:N", sort="-y", title="동네"),
    y=alt.Y("price:Q", title="가격"),
    tooltip=["dong", alt.Tooltip("price", format=",.0f")]
)

bars = base.mark_bar().encode(
    color=alt.condition(
        (alt.datum.dong == min_region) | (alt.datum.dong == max_region),
        alt.value("#d62728"),  # 강조 색 (altair 기본 색상 사용하지 못하면 색 지정됨)
        alt.value("#1f77b4")
    )
)

text = base.mark_text(
    dy=-8,
    size=12
).encode(
    text=alt.Text("price:Q", format=",.0f")
)

st.subheader(f"{selected} — 지역별 가격 (평균 기준)")
st.altair_chart((bars + text).properties(height=450, width=900), use_container_width=True)

# 정보 박스: 최저/최고 동네
st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    st.metric(label="가장 싼 동네", value=f"{min_region}", delta=f"{int(min_price):,} (원)")
    st.caption("같은 상품의 해당 동네 가격의 평균값을 사용합니다.")
with col_b:
    st.metric(label="가장 비싼 동네", value=f"{max_region}", delta=f"{int(max_price):,} (원)")
    st.caption("같은 상품의 해당 동네 가격의 평균값을 사용합니다.")

# 상/하위 표
st.markdown("### 상/하위 지역 (가격 기준)")
top_n = 5
cols = st.columns(2)
with cols[0]:
    st.write(f"가장 저렴한 {top_n} 동네")
    st.table(chart_df.sort_values("price").head(top_n).assign(price=lambda d: d["price"].map(lambda x: f"{int(x):,}")))
with cols[1]:
    st.write(f"가장 비싼 {top_n} 동네")
    st.table(chart_df.head(top_n).assign(price=lambda d: d["price"].map(lambda x: f"{int(x):,}")))

st.markdown("**원본 데이터 (선택된 상품의 행)**")
st.dataframe(sel_df.reset_index(drop=True))
