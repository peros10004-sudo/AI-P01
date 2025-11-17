import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Top 10 Subway Stations", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("../CARD_SUBWAY_MONTH_202510.csv", encoding='utf-8') # 경로 수정 필요 시 변경("CARD_SUBWAY_MONTH_202510.csv")

df = load_data()

# Preprocess
# Combined passenger count
df["총승객수"] = df["승차총승객수"] + df["하차총승객수"]

# Sidebar selection
st.sidebar.header("🔎 조건 선택")
unique_dates = sorted(df["사용일자"].unique())
unique_lines = sorted(df["노선명"].unique())

selected_date = st.sidebar.selectbox("📅 날짜 선택", unique_dates)
selected_line = st.sidebar.selectbox("🚇 호선 선택", unique_lines)

# Filter data
filtered = df[(df["사용일자"] == selected_date) & (df["노선명"] == selected_line)]

# Top 10
top10 = filtered.sort_values("총승객수", ascending=False).head(10)

# Color gradient
red = "rgba(255,0,0,0.9)"
fades = [f"rgba(0,0,255,{0.9 - i*0.07})" for i in range(10)]
colors = [red] + fades[1:]

# Plotly bar chart
fig = go.Figure()
fig.add_trace(go.Bar(
    x=top10["역명"].astype(str),
    y=top10["총승객수"],
    marker_color=colors,
))

fig.update_layout(
    title=f"{selected_date} / {selected_line} 상위 10개 역 승객수",
    xaxis_title="역명",
    yaxis_title="총승객수",
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)

st.write("### 📌 데이터 미리보기")
st.dataframe(top10)
