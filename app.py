import time
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Everest Explorer",
    page_icon="🏔️",
    layout="wide",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #0f1117; color: #e0e0e0; }

    h1 { font-size: 2.6rem !important; font-weight: 700 !important;
         background: linear-gradient(90deg, #7eb8d4, #c2e0f0);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent;
         margin-bottom: 0 !important; }

    h2 { font-size: 1.5rem !important; font-weight: 600 !important;
         color: #a8cfe0 !important; margin-top: 2rem !important; }

    h3 { color: #7eb8d4 !important; }

    .metric-card {
        background: linear-gradient(135deg, #1a2332 0%, #1e2d3d 100%);
        border: 1px solid #2a3f55;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        text-align: center;
    }
    .metric-label { font-size: 0.78rem; color: #7a9bb5; text-transform: uppercase;
                    letter-spacing: 0.06em; margin-bottom: 0.3rem; }
    .metric-value { font-size: 2rem; font-weight: 700; color: #c2e0f0; }
    .metric-sub   { font-size: 0.78rem; color: #5a8fa8; margin-top: 0.2rem; }

    .insight-box {
        background: #1a2230;
        border-left: 4px solid #4c8fa8;
        border-radius: 0 10px 10px 0;
        padding: 0.9rem 1.2rem;
        margin: 1rem 0;
        font-size: 0.92rem;
        color: #b0cfe0;
    }
    .insight-box b { color: #7eb8d4; }

    .warn-box {
        background: #2a1e14;
        border-left: 4px solid #e8743b;
        border-radius: 0 10px 10px 0;
        padding: 0.9rem 1.2rem;
        margin: 1rem 0;
        font-size: 0.92rem;
        color: #e0b898;
    }

    section[data-testid="stSidebar"] {
        background: #0d1520;
        border-right: 1px solid #1e2d3d;
    }

    .stRadio label, .stSelectbox label, .stSlider label {
        color: #a8cfe0 !important;
        font-size: 0.9rem !important;
    }

    hr { border-color: #1e2d3d !important; margin: 2rem 0 !important; }

    .section-header {
        display: flex; align-items: center; gap: 0.6rem;
        padding: 0.5rem 0 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    ascents = pd.read_csv("Mt_Everest_Ascent_Data.csv")
    ascents.columns = ascents.columns.str.strip()
    ascents["Oxy_num"] = ascents["Oxy"].map({"Y": 1, "No": 0})
    ascents["Dth_num"] = ascents["Dth"].map({"Y": 1, ".": 0})
    ascents["Sex_num"] = ascents["Sex"].map({"M": 1, "F": 0})
    ascents["Year"] = ascents["Yr/Seas"].str.extract(r"(\d{4})").astype(int)
    ascents["Season"] = ascents["Yr/Seas"].str.extract(r"\s(\w+)$")
    ascents["Decade"] = (ascents["Year"] // 10) * 10
    ascents = ascents.dropna(subset=["Time"])

    deaths = pd.read_csv("mount_everest_deaths.csv")
    deaths.columns = deaths.columns.str.strip()
    deaths["Year"] = deaths["Date"].str.extract(r"(\d{4})")
    deaths = deaths.dropna(subset=["Year"])
    deaths["Year"] = deaths["Year"].astype(int)
    deaths["Decade"] = (deaths["Year"] // 10) * 10
    deaths = deaths.dropna(subset=["Age", "Nationality", "Cause of death"])

    def classify_cause(cause):
        if pd.isna(cause):
            return "Unknown"
        text = cause.lower()
        ext = ["avalanche", "fall", "crevasse", "serac", "ice axe",
               "rope accident", "snowboarding", "blizzard", "snow blindness", "drown"]
        phy = ["exhaustion", "exposure", "altitude sickness", "hape", "hace",
               "oedema", "edema", "frostbite", "hypothermia", "heart", "cardiac",
               "stroke", "starvation"]
        has_ext = any(kw in text for kw in ext)
        has_phy = any(kw in text for kw in phy)
        if has_ext and has_phy:
            return "Mixed"
        elif has_ext:
            return "External hazard"
        elif has_phy:
            return "Physiological"
        elif any(w in text for w in ["disappear", "unknown", "presumed dead"]):
            return "Unknown/Disappearance"
        return "Other"

    deaths["CauseType"] = deaths["Cause of death"].apply(classify_cause)
    return ascents, deaths


ascents, deaths = load_data()

BLUE   = "#4C8FA8"
ORANGE = "#E8743B"
TEAL   = "#2ec4b6"
RED    = "#C44E52"
GOLD   = "#f4a261"

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#b0c8d8",
    title_font_color="#c2e0f0",
    title_font_size=15,
    margin=dict(t=50, b=30, l=10, r=10),
)


def apply_layout(fig, **kwargs):
    fig.update_layout(**LAYOUT, **kwargs)
    fig.update_xaxes(gridcolor="#1e2d3d", zerolinecolor="#1e2d3d")
    fig.update_yaxes(gridcolor="#1e2d3d", zerolinecolor="#1e2d3d")
    return fig


# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏔️ Navigation")
    section = st.radio(
        "Go to",
        ["Overview", "Age Analysis", "Gender & Country",
         "Oxygen & Safety", "Time Trends", "Hypotheses", "Deaths Analysis"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.78rem; color:#5a8fa8; line-height:1.6;">
    <b style="color:#7eb8d4;">Data sources</b><br>
    • Mt Everest Ascent Data 1953–2020<br>
      (10 184 ascents)<br>
    • Everest Deaths since 1922<br>
      (310 recorded fatalities)<br><br>
    Courtesy of <a href="https://www.himalayandatabase.com" style="color:#4c8fa8;">
    The Himalayan Database</a>
    </div>
    """, unsafe_allow_html=True)


# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("# 🏔️ Everest Explorer")
st.markdown(
    "<p style='color:#5a8fa8; margin-top:-0.5rem;'>"
    "Interactive analysis of Mount Everest ascents and fatalities · 1922–2020"
    "</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════
if section == "Overview":

    c1, c2, c3, c4, c5 = st.columns(5)
    stats = [
        (c1, "Total Ascents", f"{len(ascents):,}", "1953–2020"),
        (c2, "Recorded Fatalities", f"{len(deaths):,}", "since 1922"),
        (c3, "Years Covered", f"{ascents['Year'].max() - ascents['Year'].min()}", "years of data"),
        (c4, "Avg Mortality Rate", f"{ascents['Dth_num'].mean()*100:.1f}%", "per ascent"),
        (c5, "Avg Climber Age", f"{ascents['Age'].mean():.1f}", "years old"),
    ]
    for col, label, val, sub in stats:
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("## Ascents Over Time")
    by_year = ascents.groupby("Year").size().reset_index(name="Ascents")
    fig = px.area(by_year, x="Year", y="Ascents",
                  color_discrete_sequence=[BLUE])
    fig.update_traces(line_width=2, fillcolor="rgba(76,143,168,0.15)")
    apply_layout(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key insight:</b> Ascents grew sharply after commercial expeditions opened in the 1990s.
    The chart shows notable dips around major disasters (1996, 2014–2015) and the COVID-19 closure.
    </div>""", unsafe_allow_html=True)

    st.markdown("## Ascents vs Deaths by Decade")
    asc_d = ascents[ascents["Year"] >= 1953].groupby("Decade").size()
    dth_d = deaths[deaths["Year"] >= 1953].groupby("Decade").size()
    decades = sorted(set(asc_d.index) | set(dth_d.index))
    asc_plot = asc_d.reindex(decades, fill_value=0)
    dth_plot = dth_d.reindex(decades, fill_value=0)
    mortality_d = (dth_plot / asc_plot * 100).replace([np.inf, -np.inf], np.nan).fillna(0)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=[str(d) for d in decades], y=asc_plot.values,
                          name="Ascents", marker_color=BLUE, opacity=0.7, yaxis="y1"))
    fig2.add_trace(go.Scatter(x=[str(d) for d in decades], y=mortality_d.values,
                               name="Mortality %", marker_color=ORANGE,
                               mode="lines+markers", line=dict(width=3), yaxis="y2"))
    apply_layout(fig2,
        yaxis=dict(title="Number of ascents", gridcolor="#1e2d3d"),
        yaxis2=dict(title="Mortality rate (%)", overlaying="y", side="right",
                    gridcolor="#1e2d3d"),
        legend=dict(orientation="h", y=1.1),
        title="Ascents (bars) vs Mortality rate % (line) by decade",
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key insight:</b> Mortality rate peaked at ~17.6% in the 1980s and fell to ~2.8% by the 2010s,
    even as annual ascent numbers hit record highs. Better gear, weather forecasting, and
    commercialisation of logistics drove this improvement.
    The 2020 data point (22.7%) is statistical noise — only 22 ascents were recorded before COVID closed the mountain.
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# AGE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
elif section == "Age Analysis":
    st.markdown("## Age Distribution")

    col_a, col_b = st.columns([1, 2])
    with col_a:
        age = st.slider("Your age", int(ascents["Age"].min()), int(ascents["Age"].max()), 35)
        window = ascents[(ascents["Age"] >= age - 5) & (ascents["Age"] <= age + 5)]
        mort = window["Dth_num"].mean() * 100 if len(window) else 0
        pct  = (ascents["Age"] <= age).mean() * 100

        st.markdown(f"""
        <div class="metric-card" style="margin-bottom:0.8rem">
            <div class="metric-label">Climbers within ±5 years</div>
            <div class="metric-value">{len(window):,}</div>
        </div>
        <div class="metric-card" style="margin-bottom:0.8rem">
            <div class="metric-label">Mortality Rate at this age</div>
            <div class="metric-value">{mort:.1f}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Older than</div>
            <div class="metric-value">{pct:.0f}%</div>
            <div class="metric-sub">of all climbers</div>
        </div>""", unsafe_allow_html=True)

    with col_b:
        fig = px.histogram(ascents, x="Age", nbins=30,
                           title="Age Distribution — All Climbers",
                           color_discrete_sequence=[BLUE])
        fig.add_vline(x=age, line_color=ORANGE, line_width=3,
                      annotation_text=f"You ({age})", annotation_position="top")
        apply_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("## Age: Climbers vs Fatalities (Overlay)")
    fig2 = go.Figure()
    fig2.add_trace(go.Histogram(x=ascents["Age"].dropna(), name="All climbers",
                                marker_color=BLUE, opacity=0.6, nbinsx=20))
    fig2.add_trace(go.Histogram(x=deaths["Age"].dropna(), name="Fatal cases",
                                marker_color=ORANGE, opacity=0.75, nbinsx=20))
    apply_layout(fig2, barmode="overlay",
                 title="Age distribution: all climbers vs fatal cases",
                 xaxis_title="Age", yaxis_title="Count")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key insight:</b> Both distributions peak in the 30–40 age range.
    Deaths skew slightly older, partly because physiological causes (altitude sickness, heart issues)
    become more prevalent with age.
    </div>""", unsafe_allow_html=True)

    st.markdown("## Mortality Rate by Age Group")
    ascents["AgeGroup"] = pd.cut(ascents["Age"],
                                  bins=[0, 30, 40, 50, 60, 100],
                                  labels=["<30", "30–40", "40–50", "50–60", "60+"])
    age_mort = ascents.groupby("AgeGroup", observed=True)["Dth_num"].mean() * 100
    fig3 = px.bar(age_mort.reset_index(), x="AgeGroup", y="Dth_num",
                  color="Dth_num", color_continuous_scale=[[0, BLUE], [1, ORANGE]],
                  title="Mortality Rate (%) by Age Group",
                  labels={"Dth_num": "Mortality %", "AgeGroup": "Age group"})
    apply_layout(fig3)
    fig3.update_coloraxes(showscale=False)
    st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# GENDER & COUNTRY
# ═══════════════════════════════════════════════════════════════════════════
elif section == "Gender & Country":
    st.markdown("## Climbers by Gender")

    sex_counts = ascents["Sex"].value_counts().reset_index()
    sex_counts.columns = ["Sex", "Count"]

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(sex_counts, names="Sex", values="Count", hole=0.55,
                     color_discrete_sequence=[BLUE, ORANGE],
                     title="Share of Male vs Female climbers")
        apply_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sex_mort = ascents.groupby("Sex")["Dth_num"].mean() * 100
        fig2 = px.bar(sex_mort.reset_index(), x="Sex", y="Dth_num",
                      color="Sex", color_discrete_sequence=[BLUE, ORANGE],
                      title="Mortality Rate (%) by Gender",
                      labels={"Dth_num": "Mortality %"}, text_auto=".2f")
        apply_layout(fig2)
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("## 🌍 Top Countries by Ascents")
    n_countries = st.slider("Number of countries to show", 5, 20, 12)
    top_c = (ascents["Citizenship"].value_counts()
             .head(n_countries).reset_index())
    top_c.columns = ["Country", "Ascents"]

    col_v = st.radio("Chart type", ["Horizontal bar", "Bubble"], horizontal=True)
    if col_v == "Horizontal bar":
        fig3 = px.bar(top_c.sort_values("Ascents"), x="Ascents", y="Country",
                      orientation="h", color="Ascents",
                      color_continuous_scale=[[0, "#1e3a4a"], [1, BLUE]],
                      title=f"Top {n_countries} Countries by Ascents")
        apply_layout(fig3)
        fig3.update_coloraxes(showscale=False)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        rng = np.random.default_rng(42)
        top_c["x"] = rng.uniform(0, 10, len(top_c))
        top_c["y"] = rng.uniform(0, 10, len(top_c))
        fig3 = px.scatter(top_c, x="x", y="y", size="Ascents", color="Country",
                          text="Country", size_max=80,
                          title=f"Top {n_countries} Countries — Bubble view")
        fig3.update_traces(textposition="middle center", textfont_size=11)
        fig3.update_xaxes(visible=False)
        fig3.update_yaxes(visible=False)
        apply_layout(fig3, showlegend=False, height=500)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("## Mortality Rate by Country (Top 10 by ascents)")
    top10 = ascents["Citizenship"].value_counts().head(10).index
    c_mort = (ascents[ascents["Citizenship"].isin(top10)]
              .groupby("Citizenship")["Dth_num"].mean() * 100
              .sort_values(ascending=False).reset_index())
    c_mort.columns = ["Country", "Mortality %"]
    fig4 = px.bar(c_mort, x="Country", y="Mortality %",
                  color="Mortality %",
                  color_continuous_scale=[[0, BLUE], [1, RED]],
                  title="Mortality Rate (%) — Top 10 Countries by ascents",
                  text_auto=".2f")
    apply_layout(fig4)
    fig4.update_coloraxes(showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("## Deaths by Nationality")
    nat = deaths["Nationality"].value_counts().head(10).reset_index()
    nat.columns = ["Nationality", "Deaths"]
    fig5 = px.bar(nat, x="Deaths", y="Nationality", orientation="h",
                  color="Deaths",
                  color_continuous_scale=[[0, "#2a1a14"], [1, ORANGE]],
                  title="Top 10 Nationalities among recorded fatalities")
    apply_layout(fig5)
    fig5.update_coloraxes(showscale=False)
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key insight:</b> Nepali climbers (mostly Sherpa guides) make up the largest single group
    among recorded fatalities, reflecting their disproportionately high exposure on the mountain.
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# OXYGEN & SAFETY
# ═══════════════════════════════════════════════════════════════════════════
elif section == "Oxygen & Safety":
    st.markdown("## Supplemental Oxygen and Mortality")

    oxy_choice = st.radio("Select climbing style:",
                          ["With Oxygen (Y)", "Without Oxygen (No)"],
                          horizontal=True)
    oxy_val = "Y" if "With" in oxy_choice else "No"
    subset_oxy = ascents[ascents["Oxy"] == oxy_val]
    rate = subset_oxy["Dth_num"].mean() * 100

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom:0.8rem">
            <div class="metric-label">Ascents in this group</div>
            <div class="metric-value">{len(subset_oxy):,}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Mortality Rate</div>
            <div class="metric-value">{rate:.2f}%</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        compare = ascents.groupby("Oxy")["Dth_num"].mean().reset_index()
        compare["Dth_num"] *= 100
        compare["Highlight"] = compare["Oxy"].apply(
            lambda x: "Selected" if x == oxy_val else "Other")
        fig = px.bar(compare, x="Oxy", y="Dth_num",
                     color="Highlight",
                     color_discrete_map={"Selected": ORANGE, "Other": BLUE},
                     title="Mortality Rate — With vs Without Oxygen",
                     labels={"Dth_num": "Mortality %", "Oxy": "Oxygen"},
                     text_auto=".2f")
        apply_layout(fig, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("## Oxygen Use Over Time")
    oxy_year = (ascents.groupby("Year")["Oxy_num"].mean() * 100).reset_index()
    oxy_year.columns = ["Year", "Oxygen use %"]
    fig2 = px.line(oxy_year, x="Year", y="Oxygen use %",
                   title="Supplemental Oxygen Usage Rate Over Years (%)",
                   color_discrete_sequence=[TEAL])
    fig2.update_traces(line_width=2)
    apply_layout(fig2)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("## Oxygen × Age Group: Mortality Breakdown")
    ascents["AgeGroup"] = pd.cut(ascents["Age"],
                                  bins=[0, 30, 40, 50, 60, 100],
                                  labels=["<30", "30–40", "40–50", "50–60", "60+"])
    age_oxy = (ascents.groupby(["AgeGroup", "Oxy"], observed=True)["Dth_num"]
               .mean().reset_index())
    age_oxy["Dth_num"] *= 100
    fig3 = px.bar(age_oxy, x="AgeGroup", y="Dth_num", color="Oxy",
                  barmode="group",
                  color_discrete_map={"Y": BLUE, "No": ORANGE},
                  title="Mortality Rate (%) by Age Group & Oxygen Use",
                  labels={"Dth_num": "Mortality %", "AgeGroup": "Age group",
                          "Oxy": "Oxygen"})
    apply_layout(fig3)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key insight:</b> Oxygen dramatically reduces mortality across all age groups.
    For climbers under 55, mortality drops from ~6–7% without oxygen to under 1% with it.
    Older climbers who attempt the summit without supplemental oxygen face substantially higher risk.
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# TIME TRENDS
# ═══════════════════════════════════════════════════════════════════════════
elif section == "Time Trends":
    st.markdown("## Ascents by Gender Over the Years")

    by_year_sex = (ascents.groupby(["Year", "Sex"]).size()
                   .reset_index(name="Climbers"))
    fig = px.bar(by_year_sex, x="Year", y="Climbers", color="Sex",
                 color_discrete_sequence=[BLUE, ORANGE],
                 title="Male and Female Climbers by Year")
    apply_layout(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("## Season Distribution")
    season_counts = ascents["Season"].value_counts().reset_index()
    season_counts.columns = ["Season", "Count"]
    fig2 = px.pie(season_counts, names="Season", values="Count", hole=0.5,
                  title="Ascents by Season",
                  color_discrete_sequence=[BLUE, ORANGE, TEAL, GOLD])
    apply_layout(fig2)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("## Mortality Rate Over Time (5-year rolling)")
    mort_yr = ascents.groupby("Year")["Dth_num"].mean() * 100
    mort_roll = mort_yr.rolling(5, center=True).mean().reset_index()
    mort_roll.columns = ["Year", "Mortality %"]
    fig3 = px.line(mort_roll, x="Year", y="Mortality %",
                   title="5-Year Rolling Mortality Rate (%)",
                   color_discrete_sequence=[ORANGE])
    fig3.update_traces(line_width=2.5)
    apply_layout(fig3)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("## Nepal vs China/Tibet Routes Over Time")
    side_decade = ascents.groupby(["Decade", "Host"]).size().unstack(fill_value=0)
    fig4 = go.Figure()
    colors_side = [BLUE, ORANGE]
    for i, host in enumerate(side_decade.columns):
        fig4.add_trace(go.Scatter(x=side_decade.index.astype(str),
                                   y=side_decade[host],
                                   mode="lines+markers", name=host,
                                   line=dict(color=colors_side[i % 2], width=2.5)))
    apply_layout(fig4, title="Ascents by Decade: Nepal vs China/Tibet",
                 xaxis_title="Decade", yaxis_title="Ascents")
    st.plotly_chart(fig4, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# HYPOTHESES
# ═══════════════════════════════════════════════════════════════════════════
elif section == "Hypotheses":
    hypo = st.selectbox(
        "Select hypothesis",
        [
            "H1: Oxygen halves mortality across all ages",
            "H2: Mortality rate fell while ascents rose",
            "H3: Younger climbers die from hazards, older from physiology",
            "H4: Nepal side more dangerous than China/Tibet side",
        ]
    )

    if "H1" in hypo:
        st.markdown("## H1: Oxygen halves mortality across all ages")
        ascents["AgeGroup"] = pd.cut(ascents["Age"],
                                      bins=[0, 30, 40, 50, 60, 100],
                                      labels=["<30", "30–40", "40–50", "50–60", "60+"])
        age_oxy = (ascents.groupby(["AgeGroup", "Oxy"], observed=True)["Dth_num"]
                   .mean().reset_index())
        age_oxy["Dth_num"] *= 100
        fig = px.bar(age_oxy, x="AgeGroup", y="Dth_num", color="Oxy",
                     barmode="group",
                     color_discrete_map={"Y": BLUE, "No": ORANGE},
                     title="Mortality Rate (%) by Age Group and Oxygen Use",
                     labels={"Dth_num": "Mortality %", "AgeGroup": "Age group",
                             "Oxy": "Oxygen use"})
        apply_layout(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
        <div class="insight-box">
        <b>✅ Hypothesis supported.</b> For climbers under 55, mortality drops from 6–7% (no oxygen)
        to under 1% (with oxygen). Oxygen deprivation mortality increases slightly with age (6.6% → 7.1%),
        but the protective effect of supplemental oxygen is consistent across all age groups.
        </div>""", unsafe_allow_html=True)

    elif "H2" in hypo:
        st.markdown("## H2: Mortality fell while ascents rose")
        asc_d = ascents[ascents["Year"] >= 1953].groupby("Decade").size()
        dth_d = deaths[deaths["Year"] >= 1953].groupby("Decade").size()
        decades = sorted(set(asc_d.index) | set(dth_d.index))
        asc_plot = asc_d.reindex(decades, fill_value=0)
        dth_plot = dth_d.reindex(decades, fill_value=0)
        mort_rate = (dth_plot / asc_plot * 100).replace([np.inf, -np.inf], np.nan).fillna(0)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=[str(d) for d in decades], y=asc_plot.values,
                             name="Ascents", marker_color=BLUE, opacity=0.6, yaxis="y1"))
        fig.add_trace(go.Scatter(x=[str(d) for d in decades], y=mort_rate.values,
                                  name="Mortality %", marker_color=ORANGE,
                                  mode="lines+markers", line=dict(width=3), yaxis="y2"))
        apply_layout(fig,
            yaxis=dict(title="Ascents", gridcolor="#1e2d3d"),
            yaxis2=dict(title="Mortality %", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.1),
            title="Ascents vs Mortality Rate by Decade",
        )
        st.plotly_chart(fig, use_container_width=True)

        early = mort_rate[mort_rate.index < 1990].mean()
        late  = mort_rate[(mort_rate.index >= 1990) & (mort_rate.index < 2020)].mean()
        col1, col2 = st.columns(2)
        col1.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg mortality before 1990</div>
            <div class="metric-value">{early:.2f}%</div>
        </div>""", unsafe_allow_html=True)
        col2.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg mortality 1990–2010s</div>
            <div class="metric-value">{late:.2f}%</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-box">
        <b>✅ Hypothesis supported.</b> Mortality peaked at ~17.6% in the 1980s and fell to ~2.8%
        by the 2010s — the decade with the highest absolute number of ascents.
        Better equipment, forecasting, and commercial logistics drove this improvement.
        </div>""", unsafe_allow_html=True)

    elif "H3" in hypo:
        st.markdown("## H3: Younger climbers die from hazards, older from physiology")
        subset_h3 = deaths[deaths["CauseType"].isin(["External hazard", "Physiological"])]
        fig = go.Figure()
        color_map = {"External hazard": BLUE, "Physiological": ORANGE}
        for ct, col in color_map.items():
            ages = subset_h3[subset_h3["CauseType"] == ct]["Age"]
            fig.add_trace(go.Histogram(x=ages, name=f"{ct} (n={len(ages)})",
                                        marker_color=col, opacity=0.6, nbinsx=12))
            fig.add_vline(x=ages.mean(), line_dash="dash", line_color=col,
                          annotation_text=f"mean={ages.mean():.1f}")
        apply_layout(fig, barmode="overlay",
                     title="Age distribution by cause-of-death type",
                     xaxis_title="Age", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

        age_stats = subset_h3.groupby("CauseType")["Age"].agg(["mean", "median", "std", "count"])
        st.dataframe(age_stats.round(2).style.background_gradient(
            cmap="Blues", axis=None), use_container_width=True)

        diff = age_stats.loc["Physiological", "mean"] - age_stats.loc["External hazard", "mean"]
        st.markdown(f"""
        <div class="insight-box">
        <b>✅ Hypothesis supported.</b> Climbers dying from external hazards (falls, avalanches)
        were on average <b style="color:{ORANGE}">{diff:.1f} years younger</b> than those dying from
        physiological causes. The wider std for physiological deaths (12.4 vs 9.6 years) reflects that
        altitude-induced conditions can strike both young predisposed climbers and older ones with
        limited physiological reserve.
        </div>""", unsafe_allow_html=True)

    elif "H4" in hypo:
        st.markdown("## H4: Nepal side more dangerous than China/Tibet side")
        host_comp = ascents.groupby("Host").agg(
            MortalityRate=("Dth_num", "mean"),
            OxygenUseRate=("Oxy_num", "mean"),
            Ascents=("Dth_num", "size"),
            MeanAge=("Age", "mean"),
        )
        host_comp[["MortalityRate", "OxygenUseRate"]] *= 100

        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=host_comp.index, y=host_comp["MortalityRate"],
                                  name="Mortality %", marker_color=RED))
            fig.add_trace(go.Bar(x=host_comp.index, y=host_comp["OxygenUseRate"],
                                  name="Oxygen use %", marker_color=BLUE))
            apply_layout(fig, barmode="group",
                         title="Mortality & Oxygen use by side",
                         yaxis_title="%")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = go.Figure(data=[go.Pie(
                labels=host_comp.index, values=host_comp["Ascents"],
                hole=0.5, marker_colors=[BLUE, ORANGE])])
            apply_layout(fig2, title="Share of ascents by side")
            st.plotly_chart(fig2, use_container_width=True)

        side_decade = ascents.groupby(["Decade", "Host"]).size().unstack(fill_value=0)
        fig3 = go.Figure()
        for i, host in enumerate(side_decade.columns):
            fig3.add_trace(go.Scatter(x=side_decade.index.astype(str),
                                       y=side_decade[host],
                                       mode="lines+markers", name=host,
                                       line=dict(color=[BLUE, ORANGE][i % 2], width=2.5)))
        apply_layout(fig3, title="Ascents by decade: Nepal vs China/Tibet",
                     xaxis_title="Decade", yaxis_title="Ascents")
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("""
        <div class="warn-box">
        <b>❌ Hypothesis NOT supported.</b> Nepal side mortality: ~1.13% vs China/Tibet side ~0.69% —
        a small difference. Oxygen use rates are almost identical (96.8% vs 98.2%).
        Despite the reputation of the southern route as "commercial" and the northern as "severe",
        the statistics are comparable. ~78% of all ascents originate from the Nepalese side.
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# DEATHS ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
elif section == "Deaths Analysis":
    st.markdown("## Causes of Death")

    n_causes = st.slider("Number of causes to show", 3, 15, 7)
    cause_counts = deaths["Cause of death"].value_counts().head(n_causes)

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(data=[go.Pie(
            labels=cause_counts.index, values=cause_counts.values,
            hole=0.45, pull=[0.05] * len(cause_counts),
            marker_colors=px.colors.sequential.Blues_r[:len(cause_counts)],
        )])
        apply_layout(fig, title=f"Top {n_causes} Causes of Death")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(cause_counts.reset_index().sort_values("count"),
                      x="count", y="Cause of death", orientation="h",
                      color="count",
                      color_continuous_scale=[[0, "#1a2a3a"], [1, BLUE]],
                      title=f"Top {n_causes} Causes — Count")
        apply_layout(fig2)
        fig2.update_coloraxes(showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("## Deaths Over Time")
    deaths_yr = deaths.groupby("Year").size().reset_index(name="Deaths")
    fig3 = px.bar(deaths_yr, x="Year", y="Deaths",
                  color="Deaths",
                  color_continuous_scale=[[0, "#1a1a2e"], [1, RED]],
                  title="Recorded Fatalities per Year")
    apply_layout(fig3)
    fig3.update_coloraxes(showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("## Death Location")
    if "Location" in deaths.columns:
        loc_counts = deaths["Location"].value_counts().head(10).reset_index()
        loc_counts.columns = ["Location", "Deaths"]
        fig4 = px.bar(loc_counts, x="Deaths", y="Location", orientation="h",
                      color="Deaths",
                      color_continuous_scale=[[0, "#1a2030"], [1, ORANGE]],
                      title="Top 10 Locations of Death on Everest")
        apply_layout(fig4)
        fig4.update_coloraxes(showscale=False)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("## Cause Type Breakdown")
    ct_counts = deaths["CauseType"].value_counts().reset_index()
    ct_counts.columns = ["CauseType", "Count"]
    fig5 = px.pie(ct_counts, names="CauseType", values="Count", hole=0.5,
                  title="Deaths by Cause Category",
                  color_discrete_sequence=[BLUE, ORANGE, TEAL, RED, GOLD])
    apply_layout(fig5)
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key insight:</b> Falls and avalanches account for the largest share of fatalities,
    highlighting environmental hazards as the primary killer. Exhaustion, altitude sickness,
    and frostbite are the leading physiological causes.
    </div>""", unsafe_allow_html=True)

    st.markdown("## Age of Death Distribution")
    fig6 = px.histogram(deaths, x="Age", nbins=20,
                         title="Age Distribution of Fatalities",
                         color_discrete_sequence=[RED])
    apply_layout(fig6, xaxis_title="Age", yaxis_title="Count")
    st.plotly_chart(fig6, use_container_width=True)
