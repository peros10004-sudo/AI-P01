import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Countries MBTI Dashboard", layout="wide")

# -----------------------------
# 1. 데이터 로드
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

st.title("🌍 Countries MBTI Dashboard")
st.write("국가를 선택하면 MBTI 비율을 인터랙티브 그래프로 보여줍니다!")

# -----------------------------
# 2. 국가 선택 UI
# -----------------------------
countries = df["Country"].unique()
selected_country = st.selectbox("국가 선택", countries)

# -----------------------------
# 3. 선택 국가의 MBTI 데이터 추출
# -----------------------------
row = df[df["Country"] == selected_country].iloc[0]

mbti_cols = [c for c in df.columns if c != "Country"]
values = row[mbti_cols].values

# MBTI별 값 정렬 (1등 색 강조 위해)
sorted_indices = values.argsort()[::-1]
sorted_mbti = [mbti_cols[i] for i in sorted_indices]
sorted_values = values[sorted_indices]

# -----------------------------
# 4. 색상 설정 (1등 빨간색 → 파란색 그라데이션)
# -----------------------------
colors = ["red"]  # 1등 빨간색

import numpy as np
blue_base = np.array([0, 0, 255])

# 2등부터 파란색 → 흰색으로 흐려지는 그라데이션
for i in range(1, len(sorted_mbti)):
    ratio = i / len(sorted_mbti)
    color_rgb = blue_base * (1 - ratio) + np.array([255, 255, 255]) * ratio
    color_hex = '#%02x%02x%02x' % tuple(color_rgb.astype(int))
    colors.append(color_hex)

# -----------------------------
# 5. Plotly 바차트 생성
# -----------------------------
fig = go.Figure()

fig.add_trace(go.Bar(
    x=sorted_mbti,
    y=sorted_values,
    marker_color=colors,
    text=[f"{v:.3f}" for v in sorted_values],
    textposition="outside"
))

fig.update_layout(
    title=f"🇨🇴 {selected_country} MBTI 비율",
    xaxis_title="MBTI Type",
    yaxis_title="Value",
    template="plotly_white",
    height=600,
)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import n_colors

# ---------------------------
# 데이터 로드
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")  
    return df

df = load_data()
countries = df['Country'].unique()
mbti_cols = [c for c in df.columns if c != "Country"]

# ---------------------------
# 탭 생성
# ---------------------------
tab1, tab2 = st.tabs(["국가별 MBTI 비율", "MBTI별 상위 국가"])

# ---------------------------
# 탭1: 국가 선택 → MBTI 비율
# ---------------------------
with tab1:
    st.header("🌍 국가별 MBTI 비율")
    selected_country = st.selectbox("국가를 선택하세요", countries)
    
    country_data = df[df['Country'] == selected_country][mbti_cols].T
    country_data.columns = ['Percentage']
    country_data = country_data.sort_values(by='Percentage', ascending=False)
    
    top_color = 'red'
    gradient_colors = n_colors('blue', 'lightblue', len(country_data)-1, colortype='rgb')
    colors = [top_color] + gradient_colors
    
    fig = go.Figure(
        data=go.Bar(
            x=country_data.index,
            y=country_data['Percentage'],
            marker_color=colors
        )
    )
    
    fig.update_layout(
        title=f"{selected_country} MBTI 비율",
        xaxis_title="MBTI 유형",
        yaxis_title="비율 (%)",
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
# ---------------------------
# 탭2: MBTI 유형 선택 → 상위 국가 (한국 포함)
# ---------------------------
with tab2:
    st.header("💡 MBTI별 상위 국가 (한국 포함)")
    selected_mbti = st.selectbox("MBTI 유형을 선택하세요", mbti_cols)
    
    # 선택 MBTI 기준 상위 10개 국가
    top_countries = df[['Country', selected_mbti]].sort_values(by=selected_mbti, ascending=False).head(10)
    
    # 한국 포함 확인
    if 'Korea' not in top_countries['Country'].values:
        korea_row = df[df['Country'] == 'Korea'][['Country', selected_mbti]]
        top_countries = pd.concat([top_countries, korea_row], ignore_index=True)
    
    # 색상 설정
    top_color = 'red'
    gradient_colors = n_colors('blue', 'lightblue', len(top_countries)-1, colortype='rgb')
    colors = [top_color] + gradient_colors
    
    # 막대그래프
    fig2 = go.Figure(
        data=go.Bar(
            x=top_countries['Country'],
            y=top_countries[selected_mbti],
            marker_color=colors
        )
    )
    
    fig2.update_layout(
        title=f"{selected_mbti} 비율 상위 국가",
        xaxis_title="국가",
        yaxis_title="비율 (%)",
        template="plotly_white"
    )
    
    st.plotly_chart(fig2, use_container_width=True)

