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

# -------------------------
