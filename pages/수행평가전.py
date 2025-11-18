# Streamlit app: 지역 인구별 분석 및 시각화
# 파일명: streamlit_region_population_app.py
# 목적: 업로드된 CSV (예: 서울시 상권분석서비스(길단위인구-행정동).csv)를 꼼꼼히 분석하여
# 지역(행정동 / 길단위 등)별 인구 그래프를 생성합니다. GitHub에 올려 바로 실행 가능하도록 설계.
# 사용법:
# 1) 로컬에서: streamlit run streamlit_region_population_app.py
# 2) Streamlit Cloud/GitHub: 레포지토리에 이 파일과 requirements.txt를 올리면 됩니다.

################################################################
# 요구사항: 아래 requirements.txt 섹션을 파일로 저장하세요.
# ----------------- requirements.txt -----------------
# streamlit
# pandas
# plotly
# pydeck
# openpyxl
# ----------------------------------------------------
################################################################

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

st.set_page_config(page_title="지역 인구별 분석 대시보드", layout="wide")

st.title("📊 지역 인구별 꼼꼼한 분석 — Streamlit 앱")
st.markdown("업로드된 CSV 파일을 자동으로 분석하여 지역(행정동/길단위 등)별 인구 통계를 시각화합니다.")

DEFAULT_PATH = "/mnt/data/서울시 상권분석서비스(길단위인구-행정동).csv"

@st.cache_data
def load_csv(path_or_buffer):
    # pandas로 csv 읽기 시도 (utf-8, cp949 대응)
    try:
        df = pd.read_csv(path_or_buffer)
        return df
    except Exception:
        try:
            df = pd.read_csv(path_or_buffer, encoding='cp949')
            return df
        except Exception:
            # 시도: 엑셀로 읽기
            try:
                df = pd.read_excel(path_or_buffer)
                return df
            except Exception as e:
                raise e


def guess_population_columns(df):
    """데이터프레임에서 인구 관련 컬럼을 추측하여 반환.
    반환값: (total_col, male_cols, female_cols, age_cols)
    total_col: 문자열 또는 None
    male_cols / female_cols: 리스트 (나이대별 성별 컬럼이 있는 경우)
    age_cols: 나이대 컬럼 리스트 (성별 합계 형태일 때)
    """
    cols = df.columns.astype(str).tolist()
    lower = [c.lower() for c in cols]

    total_candidates = [c for c in cols if any(k in c.lower() for k in ['총인구','total','population','pop'])]
    total_col = total_candidates[0] if total_candidates else None

    male_cols = [c for c in cols if any(k in c.lower() for k in ['남','male','man'])]
    female_cols = [c for c in cols if any(k in c.lower() for k in ['여','female','woman'])]

    # 나이대 컬럼 추측 (예: 0~9, 10대, 20s 등)
    age_cols = [c for c in cols if any(char.isdigit() for char in c) and ('age' in c.lower() or '~' in c or '-' in c or '대' in c)]

    # 만약 total_col 없으면 numeric 컬럼 합으로 대체 후보 제공 (위치/위도 제외)
    if total_col is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        # 숫자지만 위도/경도 아닌 것들을 후보로 함
        lat_like = [c for c in numeric_cols if any(k in c.lower() for k in ['lat','lon','lng','x','y'])]
        candidate_numeric = [c for c in numeric_cols if c not in lat_like]
        # 사람이 추정되는 수치형 컬럼이 있다면 합쳐서 total로 사용
        if candidate_numeric:
            total_col = None  # signal to compute on the fly
    return total_col, male_cols, female_cols, age_cols


# ------------------ Load data ------------------
with st.sidebar:
    st.header("데이터 입력")
    st.write("기본 파일 경로를 사용하거나, 파일 업로드를 해주세요.")
    use_default = st.checkbox("기본 업로드 파일 사용 (/mnt/data/...)", value=True)
    uploaded = st.file_uploader("CSV 또는 Excel 파일 업로드", type=['csv','xlsx','xls'])

if use_default and uploaded is None:
    try:
        df = load_csv(DEFAULT_PATH)
        st.sidebar.success("기본 파일을 불러왔습니다.")
    except Exception as e:
        st.sidebar.error(f"기본 파일을 불러오지 못했습니다: {e}")
        df = None
else:
    if uploaded is not None:
        try:
            df = load_csv(uploaded)
            st.sidebar.success("업로드된 파일을 불러왔습니다.")
        except Exception as e:
            st.sidebar.error(f"업로드된 파일을 읽는 중 오류: {e}")
            df = None
    else:
        df = None

if df is None:
    st.warning("왼쪽 사이드바에서 파일을 업로드하거나 '기본 업로드 파일 사용'을 선택하세요.")
    st.stop()

# 기본 정보 출력
st.subheader("원본 데이터 미리보기")
st.dataframe(df.head())

st.markdown("---")

# 컬럼 분석
st.subheader("컬럼 탐색 — 자동 감지")
col_info_expander = st.expander("컬럼 목록 및 자동 추측 보기")
with col_info_expander:
    st.write("컬럼 수:", len(df.columns))
    st.write(df.columns.tolist())

# 컬럼명 정리 (문자열로 변환)
df.columns = df.columns.astype(str)

# 자동 추측
total_col, male_cols, female_cols, age_cols = guess_population_columns(df)

st.write("자동 추측 결과:")
st.write(f"총인구 칼럼 후보: {total_col}")
st.write(f"남성 칼럼 후보(부분 일치): {male_cols}")
st.write(f"여성 칼럼 후보(부분 일치): {female_cols}")
st.write(f"나이대 칼럼 후보: {age_cols}")

# 그룹화에 사용할 지역 컬럼 감지
region_candidates = [c for c in df.columns if any(k in c.lower() for k in ['동','행정','법정','읍','면','구','지역','도로','길','name','country'])]
if not region_candidates:
    region_candidates = df.columns.tolist()[:3]

region_col = st.selectbox("그룹(지역)으로 사용할 컬럼을 선택하세요", options=region_candidates, index=0)

# 위도/경도 컬럼 탐지
lat_candidates = [c for c in df.columns if any(k in c.lower() for k in ['lat','latitude','위도'])]
lon_candidates = [c for c in df.columns if any(k in c.lower() for k in ['lon','lng','longitude','경도'])]
lat_col = lat_candidates[0] if lat_candidates else None
lon_col = lon_candidates[0] if lon_candidates else None

# 총인구 컬럼이 없으면 숫자형 컬럼 합으로 계산
if total_col is None:
    st.info("명시적 '총인구' 컬럼이 감지되지 않아 숫자형 컬럼 합으로 총인구를 계산할 수 있습니다. 원하는 컬럼을 선택하세요.")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # 제외: 위도/경도
    numeric_cols = [c for c in numeric_cols if c not in ( [lat_col, lon_col] if lat_col and lon_col else [] )]
    chosen_for_total = st.multiselect("총인구 계산에 사용할 숫자형 컬럼 선택 (기본: 모두 선택)", options=numeric_cols, default=numeric_cols)
    def compute_total(row):
        return row[chosen_for_total].sum()
    df['_computed_total_population'] = df[chosen_for_total].sum(axis=1)
    computed_total_col = '_computed_total_population'
else:
    computed_total_col = total_col

# 그룹별 집계
agg_df = df.groupby(region_col).agg({computed_total_col: 'sum'})
agg_df = agg_df.sort_values(by=computed_total_col, ascending=False).reset_index()
agg_df.columns = [region_col, 'TotalPopulation']

# 시각화 선택
st.sidebar.header("시각화 설정")
show_top_n = st.sidebar.slider("Top N 지역 표시 (막대그래프)", min_value=5, max_value=50, value=15)
show_map = st.sidebar.checkbox("지도 위에 마커 표시 (위/경도 필요)", value=True)
show_age_pyramid = st.sidebar.checkbox("나이대-성별 피라미드 표시 (해당 컬럼이 있을 때)", value=True)

# 메인: Top N Bar Chart
st.subheader(f"Top {show_top_n} 지역별 총인구 (그룹: {region_col})")
fig_bar = px.bar(agg_df.head(show_top_n).sort_values('TotalPopulation'), x='TotalPopulation', y=region_col, orientation='h', title=f'Top {show_top_n} {region_col} 인구 수')
st.plotly_chart(fig_bar, use_container_width=True)

# 누적 비율 / 백분율 차트
agg_df['CumSum'] = agg_df['TotalPopulation'].cumsum()
agg_df['CumPct'] = 100 * agg_df['CumSum'] / agg_df['TotalPopulation'].sum()

st.subheader("누적 인구 비율")
fig_cum = px.line(agg_df.head(200), x=region_col, y='CumPct', title='지역별 누적 인구 비율 (상위 200개까지)')
fig_cum.update_layout(xaxis={'categoryorder':'array','categoryarray':agg_df[region_col].tolist()})
st.plotly_chart(fig_cum, use_container_width=True)

# 지도 표시 (위도/경도 필요)
if show_map and lat_col and lon_col:
    st.subheader("지도: 지역 위치(마커)")
    map_df = df[[region_col, lat_col, lon_col, computed_total_col]].copy()
    map_df = map_df.rename(columns={lat_col:'lat', lon_col:'lon', computed_total_col:'population'})
    # st.map requires lat/lon
    st.map(map_df.rename(columns={'lat':'lat','lon':'lon'})[['lat','lon']])
    # 간단한 pydeck scatter
    try:
        import pydeck as pdk
        midpoint = (map_df['lat'].mean(), map_df['lon'].mean())
        st.write(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=midpoint[0], longitude=midpoint[1], zoom=11, pitch=0),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=map_df,
                    get_position='[lon, lat]',
                    get_radius='population / population.max() * 200',
                    pickable=True
                )
            ]
        ))
    except Exception:
        st.info("pydeck 불러오기 실패 또는 사용 불가 — 기본 st.map을 표시했습니다.")
elif show_map:
    st.info("데이터에 위도/경도(lat/lon) 컬럼이 없어 지도를 표시할 수 없습니다. 컬럼명을 확인해보세요.")

# 나이대-성별 피라미드 (가능하면 생성)
if show_age_pyramid and (male_cols or female_cols or age_cols):
    st.subheader("나이대 및 성별 분석")
    # 케이스 1: 성별별 나이대가 분리되어 있는 경우 (예: '남_0_9','여_0_9')
    # 케이스 2: 단순히 남/여 합계만 있는 경우 -> 파이차트
    try:
        if male_cols and female_cols and len(male_cols)==len(female_cols):
            # 정렬된 나이대 추출을 시도
            age_labels = [c for c in male_cols]
            # 산술: 각 지역에서 age별 남/여 합계를 그룹화
            age_m = df[male_cols].sum()
            age_f = df[female_cols].sum()
            # 정렬 (index는 컬럼명)
            fig = go.Figure()
            fig.add_trace(go.Bar(y=age_labels, x=-age_m.values, orientation='h', name='Male'))
            fig.add_trace(go.Bar(y=age_labels, x=age_f.values, orientation='h', name='Female'))
            fig.update_layout(barmode='overlay', title='전체 데이터 기준 — 나이대별 성별 분포 (음수는 남성 표시)')
            st.plotly_chart(fig, use_container_width=True)
        elif 'age' in ''.join(age_cols).lower() or age_cols:
            # 나이대 컬럼이 있으면 전체 합 기준 막대그래프
            age_totals = df[age_cols].sum().sort_index()
            fig = px.bar(x=age_totals.values, y=age_totals.index, orientation='h', title='나이대별 합계')
            st.plotly_chart(fig, use_container_width=True)
        else:
            # fallback: 남/여 합계 파이차트
            male_total = df[male_cols].sum().sum() if male_cols else None
            female_total = df[female_cols].sum().sum() if female_cols else None
            if male_total is not None and female_total is not None:
                fig = px.pie(values=[male_total, female_total], names=['Male','Female'], title='성별 비율 (전체)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info('나이대/성별 관련 적절한 컬럼을 찾지 못했습니다.')
    except Exception as e:
        st.error(f"나이대-성별 시각화 중 오류: {e}")

# 추가 분석: 지역별 밀집도, 평균 등
st.subheader("추가 통계")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("총 지역 수", int(agg_df.shape[0]))
with col2:
    st.metric("전체 인구 합계", int(agg_df['TotalPopulation'].sum()))
with col3:
    mean_pop = agg_df['TotalPopulation'].mean()
    st.metric("지역별 평균 인구", f"{mean_pop:,.0f}")

# CSV로 결과 다운로드
st.subheader("결과 다운로드")
if st.button("Top N 집계 CSV 다운로드"):
    csv_buf = agg_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(label='Download CSV', data=csv_buf, file_name='region_population_agg.csv', mime='text/csv')

# 마무리 메모
st.markdown("---")
st.write("앱 설명: 이 앱은 업로드된 파일에 따라 자동으로 인구 관련 칼럼을 추측하고, 지역별 합계와 시각화를 제공합니다. 데이터 컬럼명이 표준적이지 않거나 복잡한 경우 사이드바의 옵션(그룹 컬럼, 총인구 계산 칼럼 선택)을 통해 수동으로 조정하세요.")
st.write("원하시면 이 대시보드를 더 고급화(정교한 지도 시각화, 행정동 GeoJSON 연동, 대시보드 레이아웃 개선)를 도와드릴게요.")

# EOF
