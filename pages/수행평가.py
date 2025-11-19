# Streamlit App: 지역별 · 품목별 가격 분석 그래프
# 파일 구조 가정
# - 최상위 폴더: 수행.csv 존재
# - Streamlit 페이지 코드: pages/ 에 위치
# - GitHub/Streamlit Cloud에서 바로 실행 가능하도록 구성

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="지역별 · 품목별 가격 분석", layout="wide")

st.title("📊 지역별 · 품목별 가격 분석 대시보드")
st.write("CSV 파일(수행.csv)을 기반으로 지역/품목별 평균 가격 그래프를 제공합니다.")

# ------------------ 데이터 불러오기 ------------------
DATA_PATH = "../수행.csv"  # pages/ 내부에서 실행하므로 상위 폴더에 있는 CSV를 불러옴

@st.cache_data
def load_data(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.read_csv(path, encoding='cp949')

df = load_data(DATA_PATH)

st.subheader("📄 데이터 미리보기")
st.dataframe(df.head())

# ------------------ 컬럼 자동 탐지 ------------------
columns = df.columns.tolist()
lower = [c.lower() for c in columns]

# 품목 후보
item_cols = [c for c in columns if '품목' in c or 'item' in c.lower()]
if not item_cols:
    item_cols = [columns[1]]  # 임의 두번째 컬럼

# 지역 후보
region_cols = [c for c in columns if any(k in c.lower() for k in ['지역','구','동','district','area','region'])]
if not region_cols:
    region_cols = [columns[0]]

# 가격 후보
price_cols = [c for c in columns if any(k in c.lower() for k in ['가격','price','cost'])]
if not price_cols:
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    price_cols = [numeric_cols[-1]]  # 마지막 숫자 컬럼

region_col = st.selectbox("지역 컬럼 선택", region_cols)
item_col = st.selectbox("품목 컬럼 선택", item_cols)
price_col = st.selectbox("가격 컬럼 선택", price_cols)

# ------------------ 집계 ------------------
agg_df = df.groupby([region_col, item_col])[price_col].mean().reset_index()

# ------------------ 필터 ------------------
st.sidebar.header("필터")
selected_region = st.sidebar.multiselect("지역 선택", agg_df[region_col].unique(), default=agg_df[region_col].unique())
selected_item = st.sidebar.multiselect("품목 선택", agg_df[item_col].unique(), default=agg_df[item_col].unique())

filtered = agg_df[(agg_df[region_col].isin(selected_region)) & (agg_df[item_col].isin(selected_item))]

# ------------------ 그래프 1: 지역별 품목 가격 비교 ------------------
st.subheader("📈 지역별 품목별 평균 가격 그래프")
fig1 = px.bar(filtered, x=region_col, y=price_col, color=item_col, barmode='group', title="지역별 · 품목별 평균 가격")
st.plotly_chart(fig1, use_container_width=True)

# ------------------ 그래프 2: 품목별 지역 비교 라인 그래프 ------------------
st.subheader("📉 품목별 지역 가격 추세")
fig2 = px.line(filtered, x=region_col, y=price_col, color=item_col, markers=True, title="품목별 평균 가격 추세")
st.plotly_chart(fig2, use_container_width=True)

# ------------------ 다운로드 ------------------
st.subheader("⬇️ 집계 데이터 다운로드")
csv = filtered.to_csv(index=False).encode('utf-8-sig')
st.download_button("CSV 다운로드", csv, "지역별_품목별_가격집계.csv", "text/csv")
import os

def get_csv_path():
    # 1) Streamlit Cloud 기본 경로 (최상위 폴더)
    path1 = "수행.csv"
    # 2) 로컬 개발 환경에서 pages/ 폴더에서 실행할 때
    path2 = "../수행.csv"

    if os.path.exists(path1):
        return path1
    elif os.path.exists(path2):
        return path2
    else:
        st.error("❌ 수행.csv 파일을 찾을 수 없습니다.")
        return None

DATA_PATH = get_csv_path()

@st.cache_data
def load_data(path):
    return pd.read_csv(path, encoding="utf-8-sig")

