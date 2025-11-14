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

st.plotly_chart(fig, use_container_width=True)
import streamlit as st
import pandas as pd
import numpy as np
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
mbti_cols = [c for c in df.columns if c != "Country"]

# -----------------------------
# 2. 탭 생성
# -----------------------------
tab1, tab2 = st.tabs(["🌍 국가별 MBTI 분석", "📊 MBTI별 상위 국가 Top 10"])

# ============================================================
# 🌍 TAB 1 : 국가 선택 → MBTI 비율 그래프
# ============================================================
with tab1:
    st.title("🌍 국가 선택 → MBTI 비율 보기")

    countries = df["Country"].unique()
    selected_country = st.selectbox("국가 선택", countries)

    row = df[df["Country"] == selected_country].iloc[0]
    values = row[mbti_cols].values

    # 값 정렬
    sorted_indices = values.argsort()[::-1]
    sorted_mbti = [mbti_cols[i] for i in sorted_indices]
    sorted_values = values[sorted_indices]

    # 색상 (1등 빨간색 → 파란 그라데이션)
    colors = ["red"]
    blue_base = np.array([0, 0, 255])

    for i in range(1, len(sorted_mbti)):
        ratio = i / len(sorted_mbti)
        color_rgb = blue_base * (1 - ratio) + np.array([255, 255, 255]) * ratio
        color_hex = '#%02x%02x%02x' % tuple(color_rgb.astype(int))
        colors.append(color_hex)

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

    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 📊 TAB 2 : MBTI 선택 → 상위 10개 국가 차트
# ============================================================
with tab2:
    st.title("📊 MBTI 유형 선택 → 상위 10개 국가")

    selected_mbti = st.selectbox("MBTI 선택", mbti_cols)

    # 해당 MBTI 기준으로 정렬
    top10 = df[["Country", selected_mbti]].sort_values(
        by=selected_mbti, ascending=False
    ).head(10)

    # 그래프 색: 1등 빨간색 → 파란색 흐려짐
    colors2 = ["red"]
    for i in range(1, len(top10)):
        ratio = i / len(top10)
        color_rgb = blue_base * (1 - ratio) + np.array([255, 255, 255]) * ratio
        colors2.append('#%02x%02x%02x' % tuple(color_rgb.astype(int)))

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=top10["Country"],
        y=top10[selected_mbti],
        marker_color=colors2,
        text=[f"{v:.3f}" for v in top10[selected_mbti]],
        textposition="outside"
    ))

    fig2.update_layout(
        title=f"🏆 MBTI {selected_mbti} 비율이 높은 상위 10개 국가",
        xaxis_title="Country",
        yaxis_title="Value",
        template="plotly_white",
        height=600
    )

    st.plotly_chart(fig2, use_container_width=True)


