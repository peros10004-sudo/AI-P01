# Streamlit 상품 가격 비교 앱 (GitHub-ready)

아래 파일들이 포함되어 있습니다:

* `pages/01_product_prices.py` — Streamlit 페이지(앱 코드). **pages 폴더** 아래에 넣어주세요.
* `requirements.txt` — 깃허브 / 배포용 의존성 목록.
* `README.md` — 실행 방법 및 CSV 형식 설명.

---

## `pages/01_product_prices.py`

```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="상품 지역별 가격 비교", layout="wide")

@st.cache_data
def load_csv(path: str):
    # 읽을 때 유연하게 컬럼명을 처리합니다.
    df = pd.read_csv(path)
    # 가능한 컬럼명 후보
    product_cols = [c for c in df.columns if c.lower() in ("product","상품","item","name")]
    region_cols = [c for c in df.columns if c.lower() in ("dong","region","area","neighborhood","구","동","지역")]
    price_cols = [c for c in df.columns if c.lower() in ("price","가격","amount","cost")]

    if not product_cols or not region_cols or not price_cols:
        raise ValueError(
            "CSV에 최소한 'product', 'region(dong)', 'price'의 유효한 컬럼이 하나씩 있어야 합니다.\n"
            f"찾은 컬럼들: products={product_cols}, regions={region_cols}, prices={price_cols}"
        )

    # 표준 컬럼명으로 변경
    df = df.rename(columns={product_cols[0]: 'product', region_cols[0]: 'dong', price_cols[0]: 'price'})

    # price 숫자 변환
    df['price'] = pd.to_numeric(df['price'].astype(str).str.replace(',',''), errors='coerce')
    df = df.dropna(subset=['price','product','dong'])
    return df


def create_agg(df: pd.DataFrame, product: str):
    sel = df[df['product'].astype(str) == str(product)].copy()
    if sel.empty:
        return pd.DataFrame(columns=['dong','avg_price','count'])
    agg = (sel.groupby('dong', dropna=False)['price']
           .agg(['mean','count'])
           .reset_index()
           .rename(columns={'mean':'avg_price','count':'count'}))
    agg = agg.sort_values('avg_price', ascending=True).reset_index(drop=True)
    return agg


# ---------- 메인 UI ----------
st.title("📊 상품별 지역(동) 가격 비교")
st.markdown("CSV 파일은 레포지토리 루트에 두고 `prices.csv` (또는 원하는 파일명)를 사용하세요.")

# CSV 경로 입력(루트에 있다고 가정)
csv_default = "prices.csv"
csv_path = st.text_input("CSV 파일 경로 (루트 기준)", value=csv_default)

# 데이터 로드
try:
    df = load_csv(csv_path)
except Exception as e:
    st.error(f"CSV 로드 오류: {e}")
    st.stop()

products = sorted(df['product'].astype(str).unique())
if not products:
    st.warning("CSV에서 상품을 찾을 수 없습니다.")
    st.stop()

col1, col2 = st.columns([3,1])
with col1:
    selected_product = st.selectbox("상품 선택", products)
with col2:
    st.write("\n")
    st.write("\n")
    st.write("🔎 선택된 상품:")
    st.metric("상품", selected_product)

agg = create_agg(df, selected_product)
if agg.empty:
    st.info("선택된 상품의 데이터가 없습니다.")
    st.stop()

# 최저/최고 동
min_row = agg.loc[agg['avg_price'].idxmin()]
max_row = agg.loc[agg['avg_price'].idxmax()]

st.info(f"가장 싼 동: **{min_row['dong']}** — 평균가 {min_row['avg_price']:.0f}원 (표본 {int(min_row['count'])})")
st.info(f"가장 비싼 동: **{max_row['dong']}** — 평균가 {max_row['avg_price']:.0f}원 (표본 {int(max_row['count'])})")

# 차트 (막대)
fig = go.Figure()

# 기본 바 (회색)
fig.add_trace(go.Bar(
    x=agg['dong'],
    y=agg['avg_price'],
    name='평균가격',
    marker_color='lightgray',
    hovertemplate='<b>%{x}</b><br>평균가: %{y:.0f}원<br>샘플: %{customdata}',
    customdata=agg['count']
))

# min, max 강조 (다른 색)
fig.add_trace(go.Bar(
    x=[min_row['dong']],
    y=[min_row['avg_price']],
    name='최저가 동',
    marker_color='green',
    hovertemplate='<b>%{x}</b><br>평균가: %{y:.0f}원',
))
fig.add_trace(go.Bar(
    x=[max_row['dong']],
    y=[max_row['avg_price']],
    name='최고가 동',
    marker_color='red',
    hovertemplate='<b>%{x}</b><br>평균가: %{y:.0f}원',
))

fig.update_layout(
    title=f"'{selected_product}'의 동별 평균 가격",
    xaxis_title='동',
    yaxis_title='평균 가격 (원)',
    barmode='overlay',
    bargap=0.2,
    height=550,
    template='simple_white'
)

st.plotly_chart(fig, use_container_width=True)

# 데이터테이블
with st.expander("데이터 보기 (동별 평균)"):
    st.dataframe(agg.style.format({'avg_price':'{:.0f}'}))

# 다운로드 버튼: 동별 평균 csv
csv_bytes = agg.to_csv(index=False).encode('utf-8')
st.download_button("동별 평균 CSV 다운로드", data=csv_bytes, file_name=f"{selected_product}_dong_avg.csv", mime='text/csv')

# 맨 아래에 간단한 도움말
st.markdown("---")
st.markdown("**CSV 파일 예시 컬럼명(허용)**: `product`(또는 product/name/상품), `dong`(또는 region/area/지역/동), `price`(또는 price/가격/amount).\nCSV는 레포지토리 루트에 위치시키세요.\n")
```

---

## `requirements.txt`

```
streamlit>=1.24
pandas>=1.5
plotly>=5.0
```

---

## `README.md`

```md
# Streamlit 상품 지역별 가격 비교 앱

## 파일 구조 (권장)
```

project-root/
├─ pages/
│  └─ 01_product_prices.py
├─ prices.csv      # 루트에 위치한 CSV
├─ requirements.txt
└─ README.md

```

### CSV 형식
CSV는 세 가지 핵심 컬럼을 필요로 합니다 (컬럼명은 약간 다르게 적혀 있어도 인식합니다):
- `product` (또는 `상품`, `item`, `name`) — 상품 이름
- `dong` (또는 `region`, `area`, `지역`) — 동/구 수준의 지역 이름
- `price` (또는 `가격`, `amount`) — 가격 (숫자)

예시 행:
```

product,dong,price
사과,중구 1동,1200
사과,중구 1동,1300
바나나,서구 2동,900

```

### 실행 방법
1. 가상환경 생성
```

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

```
2. 루트에 `prices.csv`를 넣고
```

streamlit run pages/01_product_prices.py

```

### 깃허브에 올릴 때
- `pages/01_product_prices.py` 파일을 그대로 올리고 `prices.csv`는 개인정보/대용량이 아니라면 함께 올리거나 `data/` 폴더로 분리하세요.
```

```

---

앱 코드와 요구사항을 `pages/01_product_prices.py`, `requirements.txt`, `README.md`로 포함해 두었습니다. 필요하면 UI 문구(한국어/영어), 차트 색상 변경, 또는 CSV 컬럼명 규칙을 더 엄격하게 적용하도록 코드를 수정해 드릴게요.

```
