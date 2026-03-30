import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="GDP vs 기대수명",
    page_icon="🌍",
    layout="wide",
)

# ── 커스텀 CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .metric-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        border: 1px solid #e9ecef;
    }
    h1 { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── 데이터 로드 ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df = px.data.gapminder()
    df = df.rename(columns={
        "country":       "국가",
        "continent":     "대륙",
        "year":          "연도",
        "lifeExp":       "기대수명",
        "pop":           "인구",
        "gdpPercap":     "1인당 GDP",
    })
    continent_map = {
        "Asia":     "아시아",
        "Europe":   "유럽",
        "Africa":   "아프리카",
        "Americas": "아메리카",
        "Oceania":  "오세아니아",
    }
    df["대륙"] = df["대륙"].map(continent_map)
    return df

df = load_data()
years = sorted(df["연도"].unique())
continents = sorted(df["대륙"].unique())

# ── 헤더 ────────────────────────────────────────────────────
st.title("🌍 GDP vs 기대수명")
st.caption("출처: Gapminder · 1952–2007년 데이터 · 버블 크기 = 인구")

st.divider()

# ── 사이드바 컨트롤 ──────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 설정")

    selected_year = st.slider(
        "연도",
        min_value=int(years[0]),
        max_value=int(years[-1]),
        value=2007,
        step=5,
    )

    selected_continents = st.multiselect(
        "대륙 필터",
        options=continents,
        default=continents,
    )

    st.markdown("---")
    st.subheader("🔵 버블 크기 조절")
    bubble_scale = st.slider(
        "버블 최대 크기",
        min_value=10,
        max_value=80,
        value=40,
        step=5,
        help="버블이 너무 크거나 작으면 여기서 조절하세요.",
    )

    log_x = st.checkbox("GDP 축 로그 스케일", value=True)

    st.markdown("---")
    st.subheader("🔍 국가 하이라이트")
    all_countries = sorted(df["국가"].unique())
    highlight_countries = st.multiselect(
        "강조할 국가 선택",
        options=all_countries,
        default=["Korea, Rep.", "Japan", "United States", "China", "Germany"],
        max_selections=10,
    )

# ── 데이터 필터 ──────────────────────────────────────────────
filtered = df[
    (df["연도"] == selected_year) &
    (df["대륙"].isin(selected_continents))
].copy()

# 하이라이트 국가 영문명 → 한글 매핑용 컬럼
filtered["강조"] = filtered["국가"].apply(
    lambda x: "★ " + x if x in highlight_countries else x
)

# ── 요약 지표 ────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("📅 선택 연도", f"{selected_year}년")
col2.metric("🌐 국가 수", f"{len(filtered)}개국")
col3.metric("⏳ 평균 기대수명", f"{filtered['기대수명'].mean():.1f}세")
col4.metric("💰 중앙값 GDP", f"${filtered['1인당 GDP'].median():,.0f}")

st.markdown("")

# ── 버블 차트 ────────────────────────────────────────────────
color_map = {
    "아시아":    "#4C78A8",
    "유럽":     "#F58518",
    "아프리카":  "#54A24B",
    "아메리카":  "#E45756",
    "오세아니아":"#B279A2",
}

fig = px.scatter(
    filtered,
    x="1인당 GDP",
    y="기대수명",
    size="인구",
    color="대륙",
    color_discrete_map=color_map,
    hover_name="국가",
    hover_data={
        "1인당 GDP": ":$,.0f",
        "기대수명":  ":.1f",
        "인구":      ":,",
        "대륙":      True,
    },
    size_max=bubble_scale,
    log_x=log_x,
    title=f"{selected_year}년 · 1인당 GDP vs 기대수명",
    labels={
        "1인당 GDP": "1인당 GDP (USD)",
        "기대수명":  "기대수명 (세)",
    },
    template="plotly_white",
)

# 강조 국가에 텍스트 레이블 추가
if highlight_countries:
    hl_df = filtered[filtered["국가"].isin(highlight_countries)]
    fig.add_trace(go.Scatter(
        x=hl_df["1인당 GDP"],
        y=hl_df["기대수명"],
        mode="text",
        text=hl_df["국가"],
        textposition="top center",
        textfont=dict(size=11, color="#333333"),
        showlegend=False,
        hoverinfo="skip",
    ))

fig.update_layout(
    height=580,
    margin=dict(l=20, r=20, t=60, b=20),
    legend=dict(
        title="대륙",
        orientation="v",
        x=1.01,
        y=0.98,
    ),
    xaxis=dict(
        title="1인당 GDP (USD, 로그 스케일)" if log_x else "1인당 GDP (USD)",
        gridcolor="#eeeeee",
        showline=True,
        linecolor="#cccccc",
    ),
    yaxis=dict(
        title="기대수명 (세)",
        gridcolor="#eeeeee",
        showline=True,
        linecolor="#cccccc",
        range=[30, 90],
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Pretendard, Apple SD Gothic Neo, sans-serif", size=13),
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 보조 차트: 대륙별 평균 ──────────────────────────────────
st.subheader("📊 대륙별 평균 비교")

col_a, col_b = st.columns(2)

with col_a:
    avg_gdp = (
        filtered.groupby("대륙")["1인당 GDP"]
        .mean()
        .reset_index()
        .sort_values("1인당 GDP", ascending=True)
    )
    fig_gdp = px.bar(
        avg_gdp,
        x="1인당 GDP",
        y="대륙",
        orientation="h",
        color="대륙",
        color_discrete_map=color_map,
        text_auto="$,.0f",
        title="대륙별 평균 1인당 GDP",
        template="plotly_white",
    )
    fig_gdp.update_traces(textposition="outside")
    fig_gdp.update_layout(
        height=300,
        showlegend=False,
        margin=dict(l=10, r=60, t=40, b=10),
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#eeeeee"),
    )
    st.plotly_chart(fig_gdp, use_container_width=True)

with col_b:
    avg_life = (
        filtered.groupby("대륙")["기대수명"]
        .mean()
        .reset_index()
        .sort_values("기대수명", ascending=True)
    )
    fig_life = px.bar(
        avg_life,
        x="기대수명",
        y="대륙",
        orientation="h",
        color="대륙",
        color_discrete_map=color_map,
        text_auto=".1f",
        title="대륙별 평균 기대수명",
        template="plotly_white",
    )
    fig_life.update_traces(textposition="outside")
    fig_life.update_layout(
        height=300,
        showlegend=False,
        margin=dict(l=10, r=40, t=40, b=10),
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#eeeeee"),
    )
    st.plotly_chart(fig_life, use_container_width=True)

# ── 원본 데이터 테이블 ───────────────────────────────────────
with st.expander("📋 원본 데이터 보기"):
    display_df = (
        filtered[["국가", "대륙", "기대수명", "1인당 GDP", "인구"]]
        .sort_values("1인당 GDP", ascending=False)
        .reset_index(drop=True)
    )
    display_df.index += 1
    display_df["1인당 GDP"] = display_df["1인당 GDP"].map("${:,.0f}".format)
    display_df["인구"] = display_df["인구"].map("{:,}".format)
    display_df["기대수명"] = display_df["기대수명"].map("{:.1f}세".format)
    st.dataframe(display_df, use_container_width=True)

st.caption("Made with ❤️ using Streamlit + Plotly · Gapminder Dataset")
