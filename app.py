import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Everest Explorer", page_icon="🏔️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background-color: #1a0010; }

h1 { color: #f7a8c4 !important; font-size: 2.4rem !important; font-weight: 700 !important; }
h2 { color: #e87fa8 !important; font-size: 1.4rem !important; font-weight: 600 !important; margin-top: 2rem !important; }

.metric-card {
    background: linear-gradient(135deg, #2d0020 0%, #3d0030 100%);
    border: 1px solid #8b3060;
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    text-align: center;
    margin-bottom: 0.4rem;
}
.metric-label { font-size: 0.75rem; color: #c47a9a; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.3rem; }
.metric-value { font-size: 1.9rem; font-weight: 700; color: #f7a8c4; }
.metric-sub   { font-size: 0.75rem; color: #9a5a7a; margin-top: 0.2rem; }

.insight-box {
    background: #2d0020;
    border-left: 4px solid #e05090;
    border-radius: 0 10px 10px 0;
    padding: 0.9rem 1.2rem;
    margin: 1rem 0;
    font-size: 0.9rem;
    color: #e8b0ca;
}
.insight-box b { color: #f7a8c4; }

section[data-testid="stSidebar"] {
    background: #130008 !important;
    border-right: 1px solid #5a1040 !important;
}

hr { border-color: #3d1030 !important; margin: 1.8rem 0 !important; }

div[data-testid="stRadio"] label, div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label, .stRadio p, label {
    color: #e8b0ca !important;
}
</style>
""", unsafe_allow_html=True)

PINK1  = "#e05090"
PINK2  = "#f7a8c4"
PINK3  = "#c03070"
LIGHT  = "#fcd5e5"
DARK   = "#6b1040"
BG     = "#1a0010"
BG2    = "#2d0020"

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    BG2,
    "axes.edgecolor":    "#5a1040",
    "axes.labelcolor":   PINK2,
    "xtick.color":       PINK2,
    "ytick.color":       PINK2,
    "text.color":        PINK2,
    "grid.color":        "#3d1030",
    "grid.alpha":        0.5,
    "axes.titlecolor":   PINK2,
})


@st.cache_data
def load_data():
    a = pd.read_csv("Mt_Everest_Ascent_Data.csv")
    a.columns = a.columns.str.strip()
    a["Oxy_num"] = a["Oxy"].map({"Y": 1, "No": 0})
    a["Dth_num"] = a["Dth"].map({"Y": 1, ".": 0})
    a["Sex_num"] = a["Sex"].map({"M": 1, "F": 0})
    a["Year"]    = a["Yr/Seas"].str.extract(r"(\d{4})").astype(int)
    a["Season"]  = a["Yr/Seas"].str.extract(r"\s(\w+)$")
    a["Decade"]  = (a["Year"] // 10) * 10
    a = a.dropna(subset=["Time"])

    d = pd.read_csv("mount_everest_deaths.csv")
    d.columns = d.columns.str.strip()
    d["Year"] = d["Date"].str.extract(r"(\d{4})")
    d = d.dropna(subset=["Year"])
    d["Year"]   = d["Year"].astype(int)
    d["Decade"] = (d["Year"] // 10) * 10
    d = d.dropna(subset=["Age", "Nationality", "Cause of death"])
    return a, d


ascents, deaths = load_data()

def styled_fig(w=10, h=5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG2)
    for spine in ax.spines.values():
        spine.set_edgecolor("#5a1040")
    ax.tick_params(colors=PINK2)
    ax.xaxis.label.set_color(PINK2)
    ax.yaxis.label.set_color(PINK2)
    return fig, ax

def styled_fig2(ncols=2, w=14, h=5):
    fig, axes = plt.subplots(1, ncols, figsize=(w, h))
    fig.patch.set_facecolor(BG)
    for ax in axes:
        ax.set_facecolor(BG2)
        for spine in ax.spines.values():
            spine.set_edgecolor("#5a1040")
        ax.tick_params(colors=PINK2)
        ax.xaxis.label.set_color(PINK2)
        ax.yaxis.label.set_color(PINK2)
    return fig, axes


# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏔️ Everest Explorer")
    section = st.radio(
        "Section",
        ["📊 Overview", "👤 Personal Stats", "📈 Plots", "🔬 Detailed Overview"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.78rem; color:#9a5a7a; line-height:1.7;">
    <b style="color:#e87fa8;">Data</b><br>
    Ascent Data 1953–2020 · 10 184 rows<br>
    Deaths since 1922 · 310 rows<br><br>
    Source: <a href="https://www.himalayandatabase.com" style="color:#e05090;">
    The Himalayan Database</a>
    </div>""", unsafe_allow_html=True)


st.markdown("# 🏔️ Everest Explorer")
st.markdown("<p style='color:#9a5a7a;margin-top:-0.6rem;'>Interactive analysis of Mount Everest ascents and fatalities · 1922–2020</p>", unsafe_allow_html=True)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════
if section == "📊 Overview":
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val, sub in [
        (c1, "Total Ascents",      f"{len(ascents):,}",                      "1953–2020"),
        (c2, "Fatalities",         f"{len(deaths):,}",                       "since 1922"),
        (c3, "Years Covered",      f"{ascents['Year'].max()-ascents['Year'].min()}", "years"),
        (c4, "Avg Mortality",      f"{ascents['Dth_num'].mean()*100:.1f}%",  "per ascent"),
        (c5, "Avg Climber Age",    f"{ascents['Age'].mean():.1f}",           "years old"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # 1. Line plot ascents by year
    st.markdown("## Number of ascents on Everest")
    by_year = ascents.groupby("Year").size().reset_index(name="Ascents")
    fig, ax = styled_fig(10, 4)
    ax.plot(by_year["Year"], by_year["Ascents"], color=PINK1, linewidth=2, marker="o", markersize=3)
    ax.set_title("Number of ascents on Everest", color=PINK2, fontsize=13)
    ax.set_xlabel("Year"); ax.set_ylabel("Number of Ascents")
    ax.set_xlim(1953, 2020)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig); plt.close()

    st.markdown("""<div class="insight-box">The number of ascents per year witnessed an upward trend from 1960, with striking fluctuations throughout — including dips after major disasters (1996, 2014–2015) and the COVID-19 closure.</div>""", unsafe_allow_html=True)
    st.markdown("---")

    # 2. Age histograms side-by-side
    st.markdown("## Spread of alpinists by age")
    fig, axes = styled_fig2(2, 14, 5)
    fig.suptitle("Spread of alpinists by age", color=PINK2, fontsize=14)
    axes[0].hist(ascents["Age"], bins=10, color=PINK1, edgecolor=BG)
    axes[0].set_title("Age of ascenders", color=PINK2)
    axes[0].set_xlabel("Age"); axes[0].set_ylabel("Number of climbers")
    axes[1].hist(deaths["Age"], bins=10, color=PINK3, edgecolor=BG)
    axes[1].set_title("Age of dead people", color=PINK2)
    axes[1].set_xlabel("Age"); axes[1].set_ylabel("Number of Dead People")
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    st.markdown("""<div class="insight-box">Both distributions are centred around 30–40 years old.</div>""", unsafe_allow_html=True)
    st.markdown("---")

    # 3. Bar chart by sex
    st.markdown("## Climbers by Sex")
    sex_counts = ascents["Sex"].value_counts()
    fig, ax = styled_fig(5, 4)
    ax.bar(sex_counts.index, sex_counts.values, color=[PINK1, PINK3])
    ax.set_title("Climbers by Sex", color=PINK2)
    ax.set_ylabel("Number of climbers"); ax.set_xlabel("Sex")
    st.pyplot(fig); plt.close()

    st.markdown("""<div class="insight-box">Everest climbers are overwhelmingly male.</div>""", unsafe_allow_html=True)
    st.markdown("---")

    # 4. Pie nationality deaths
    st.markdown("## Climbers by Nationality (fatalities)")
    nat = deaths["Nationality"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    pinks = [PINK1, PINK3, PINK2, "#d04080", "#f0c0d8", "#a02050",
             "#e890b8", "#b83068", "#f5b8d0", "#903058",
             "#c06090", "#802040", "#fae0ec", "#701830", "#c8a0b8"]
    ax.pie(nat.values, labels=nat.index, autopct="%1.1f%%",
           colors=pinks[:len(nat)], textprops={"color": PINK2})
    ax.set_title("Climbers by Nationality", color=PINK2)
    st.pyplot(fig); plt.close()

    st.markdown("""<div class="insight-box">Nepali climbers made up the largest single group among recorded fatalities, followed by American and Indian climbers.</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PERSONAL STATS
# ═══════════════════════════════════════════════════════════════════════════
elif section == "👤 Personal Stats":
    st.markdown("## How do you compare to Everest climbers?")

    col_in, _ = st.columns([1, 2])
    with col_in:
        user_age  = st.slider("Your age", 16, 76, 30)
        user_sex  = st.radio("Your sex", ["M", "F"], horizontal=True)
        user_year = st.selectbox("Pick a year to explore",
                                  sorted(ascents["Year"].unique()))

    st.markdown("---")

    # Age metrics
    window = ascents[(ascents["Age"] >= user_age - 5) & (ascents["Age"] <= user_age + 5)]
    mort   = window["Dth_num"].mean() * 100 if len(window) else 0
    pct    = (ascents["Age"] <= user_age).mean() * 100

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"""<div class="metric-card"><div class="metric-label">Climbers within ±5 yrs of your age</div><div class="metric-value">{len(window):,}</div></div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div class="metric-card"><div class="metric-label">Mortality rate at your age group</div><div class="metric-value">{mort:.1f}%</div></div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class="metric-card"><div class="metric-label">You are older than</div><div class="metric-value">{pct:.0f}%</div><div class="metric-sub">of all climbers</div></div>""", unsafe_allow_html=True)

    # Age histogram with user marker
    st.markdown("## Your age vs all climbers")
    fig, ax = styled_fig(10, 4)
    ax.hist(ascents["Age"], bins=25, color=PINK1, edgecolor=BG, alpha=0.85)
    ax.axvline(user_age, color=LIGHT, linewidth=3, linestyle="--",
               label=f"You ({user_age})")
    ax.set_title("Age Distribution of Everest Climbers", color=PINK2, fontsize=13)
    ax.set_xlabel("Age"); ax.set_ylabel("Number of climbers")
    ax.legend(facecolor=BG2, edgecolor=DARK, labelcolor=PINK2)
    st.pyplot(fig); plt.close()

    st.markdown("---")

    # Sex comparison
    sex_label = "Male" if user_sex == "M" else "Female"
    sex_group = ascents[ascents["Sex"] == user_sex]
    all_mort  = ascents["Dth_num"].mean() * 100
    sex_mort  = sex_group["Dth_num"].mean() * 100
    sex_pct   = len(sex_group) / len(ascents) * 100

    st.markdown(f"## You as a {sex_label} climber")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"""<div class="metric-card"><div class="metric-label">{sex_label} climbers</div><div class="metric-value">{len(sex_group):,}</div><div class="metric-sub">{sex_pct:.1f}% of all</div></div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div class="metric-card"><div class="metric-label">{sex_label} mortality</div><div class="metric-value">{sex_mort:.2f}%</div></div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class="metric-card"><div class="metric-label">Overall mortality</div><div class="metric-value">{all_mort:.2f}%</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Year snapshot
    st.markdown(f"## Year {user_year} — snapshot")
    yr_data   = ascents[ascents["Year"] == user_year]
    yr_deaths = deaths[deaths["Year"] == user_year]

    if len(yr_data) == 0:
        st.info(f"No ascent records for {user_year}.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"""<div class="metric-card"><div class="metric-label">Total ascents</div><div class="metric-value">{len(yr_data):,}</div></div>""", unsafe_allow_html=True)
        c2.markdown(f"""<div class="metric-card"><div class="metric-label">Deaths that year</div><div class="metric-value">{len(yr_deaths):,}</div></div>""", unsafe_allow_html=True)
        c3.markdown(f"""<div class="metric-card"><div class="metric-label">With oxygen</div><div class="metric-value">{yr_data['Oxy_num'].mean()*100:.0f}%</div></div>""", unsafe_allow_html=True)
        c4.markdown(f"""<div class="metric-card"><div class="metric-label">Avg age</div><div class="metric-value">{yr_data['Age'].mean():.1f}</div></div>""", unsafe_allow_html=True)

        # Sex bar for that year
        fig, ax = styled_fig(5, 3)
        yc = yr_data["Sex"].value_counts()
        ax.bar(yc.index, yc.values, color=[PINK1, PINK3])
        ax.set_title(f"Climbers by sex in {user_year}", color=PINK2)
        ax.set_ylabel("Count")
        st.pyplot(fig); plt.close()

        # Age hist for year vs user
        fig2, ax2 = styled_fig(8, 3)
        ax2.hist(yr_data["Age"], bins=15, color=PINK3, edgecolor=BG, alpha=0.8,
                 label=f"Climbers in {user_year}")
        ax2.axvline(user_age, color=LIGHT, linewidth=3, linestyle="--",
                    label=f"You ({user_age})")
        ax2.set_title(f"Age distribution in {user_year}", color=PINK2)
        ax2.set_xlabel("Age"); ax2.set_ylabel("Count")
        ax2.legend(facecolor=BG2, edgecolor=DARK, labelcolor=PINK2)
        st.pyplot(fig2); plt.close()


# ═══════════════════════════════════════════════════════════════════════════
# PLOTS (all notebook plots)
# ═══════════════════════════════════════════════════════════════════════════
elif section == "📈 Plots":

    # 1. Ascents over time
    st.markdown("## Number of ascents on Everest")
    by_year = ascents.groupby("Year").size().reset_index(name="Ascents")
    fig, ax = styled_fig(10, 4)
    ax.plot(by_year["Year"], by_year["Ascents"], color=PINK1, linewidth=2, marker="o", markersize=3)
    ax.set_title("Number of ascents on Everest", color=PINK2, fontsize=13)
    ax.set_xlabel("Year"); ax.set_ylabel("Number of Ascents")
    ax.set_xlim(1953, 2020); ax.grid(True, alpha=0.3)
    st.pyplot(fig); plt.close()
    st.markdown("""<div class="insight-box">The number of ascents per year generally witnessed an upward trend from 1960. We can observe striking fluctuations during the whole period.</div>""", unsafe_allow_html=True)
    st.markdown("---")

    # 2. Age histograms
    st.markdown("## Spread of alpinists by age")
    fig, axes = styled_fig2(2, 14, 5)
    fig.suptitle("Spread of alpinists by age", color=PINK2, fontsize=14)
    axes[0].hist(ascents["Age"], bins=10, color=PINK1, edgecolor=BG)
    axes[0].set_title("Age of ascenders", color=PINK2)
    axes[0].set_xlabel("Age"); axes[0].set_ylabel("Number of climbers")
    axes[1].hist(deaths["Age"], bins=10, color=PINK3, edgecolor=BG)
    axes[1].set_title("Age of dead people", color=PINK2)
    axes[1].set_xlabel("Age"); axes[1].set_ylabel("Number of Dead People")
    plt.tight_layout()
    st.pyplot(fig); plt.close()
    st.markdown("""<div class="insight-box">Both distributions are centred around 30–40 years old.</div>""", unsafe_allow_html=True)
    st.markdown("---")

    # 3. Bar climbers by sex
    st.markdown("## Climbers by Sex")
    sex_counts = ascents["Sex"].value_counts()
    fig, ax = styled_fig(5, 4)
    ax.bar(sex_counts.index, sex_counts.values, color=[PINK1, PINK3])
    ax.set_title("Climbers by Sex", color=PINK2)
    ax.set_ylabel("Number of climbers"); ax.set_xlabel("Sex")
    st.pyplot(fig); plt.close()
    st.markdown("""<div class="insight-box">The bar chart confirms that Everest climbers are overwhelmingly male.</div>""", unsafe_allow_html=True)
    st.markdown("---")

    # 4. Pie nationality deaths
    st.markdown("## Climbers by Nationality (fatalities)")
    nat = deaths["Nationality"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    pinks = [PINK1, PINK3, PINK2, "#d04080", "#f0c0d8", "#a02050",
             "#e890b8", "#b83068", "#f5b8d0", "#903058",
             "#c06090", "#802040", "#fae0ec", "#701830", "#c8a0b8"]
    ax.pie(nat.values, labels=nat.index, autopct="%1.1f%%",
           colors=pinks[:len(nat)], textprops={"color": PINK2})
    ax.set_title("Climbers by Nationality", color=PINK2)
    st.pyplot(fig); plt.close()
    st.markdown("""<div class="insight-box">Nepali climbers made up the largest single group among recorded fatalities, followed by American and Indian climbers.</div>""", unsafe_allow_html=True)
    st.markdown("---")

    # 5. Top 10 countries ascents + top causes death
    st.markdown("## Top countries by ascents vs top causes of death")
    fig, axes = styled_fig2(2, 16, 7)
    fig.suptitle("Everest: top countries by ascents vs. top causes of death",
                 color=PINK2, fontsize=16, fontweight="bold")

    top_c = ascents["Citizenship"].value_counts().head(10).sort_values()
    axes[0].barh(top_c.index, top_c.values, color=PINK1)
    axes[0].set_title("Top 10 countries by ascents", color=PINK2)
    axes[0].grid(axis="x", alpha=0.3)

    dc = deaths["Cause of death"].value_counts().head(7).sort_values()
    bars = axes[1].barh(dc.index, dc.values, color=PINK3)
    axes[1].set_title("Top causes of death", color=PINK2)
    axes[1].grid(axis="x", alpha=0.3)
    for bar in bars:
        axes[1].text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                     str(int(bar.get_width())), va="center", color=PINK2)
    plt.tight_layout()
    st.pyplot(fig); plt.close()
    st.markdown("---")

    # 6. Overlay age histograms
    st.markdown("## Age Distribution: Ascenders vs Fatalities")
    fig, ax = styled_fig(9, 5)
    ax.hist(ascents["Age"].dropna(), bins=10, alpha=1, label="All climbers",
            color=PINK1, edgecolor=BG)
    ax.hist(deaths["Age"].dropna(), bins=10, alpha=1, label="Climbers who died",
            color=PINK3, edgecolor=BG)
    ax.set_title("Age Distribution Comparison of Ascenders and dead people", color=PINK2)
    ax.set_xlabel("Age"); ax.set_ylabel("Count")
    ax.legend(facecolor=BG2, edgecolor=DARK, labelcolor=PINK2)
    st.pyplot(fig); plt.close()
    st.markdown("---")

    # 7. Ascents vs Deaths by decade
    st.markdown("## Ascents vs Deaths by Decade")
    asc_d = ascents[ascents["Year"] >= 1953].groupby("Decade").size()
    dth_d = deaths[deaths["Year"] >= 1953].groupby("Decade").size()
    decades = sorted(set(asc_d.index) | set(dth_d.index))
    asc_p = asc_d.reindex(decades, fill_value=0)
    dth_p = dth_d.reindex(decades, fill_value=0)
    mort_r = (dth_p / asc_p * 100).replace([np.inf, -np.inf], np.nan).fillna(0)

    fig, axes = styled_fig2(2, 14, 5)
    x = np.arange(len(decades))
    axes[0].bar(x - 0.2, asc_p.values, width=0.4, label="Ascents", color=PINK1)
    axes[0].bar(x + 0.2, dth_p.values, width=0.4, label="Deaths", color=PINK3)
    axes[0].set_xticks(x); axes[0].set_xticklabels(decades)
    axes[0].set_title("Ascents vs Deaths by Decade", color=PINK2)
    axes[0].legend(facecolor=BG2, edgecolor=DARK, labelcolor=PINK2)

    axes[1].bar(x, mort_r.values, color=PINK3)
    axes[1].set_xticks(x); axes[1].set_xticklabels(decades)
    axes[1].set_title("Mortality Rate (%) by Decade", color=PINK2)
    axes[1].set_ylabel("Mortality %")
    plt.tight_layout()
    st.pyplot(fig); plt.close()
    st.markdown("---")

    # 8. Oxygen vs non-oxygen time series
    st.markdown("## Oxygen vs Non-Oxygen Ascents Over Time")
    oxy_ts = ascents.groupby(["Year", "Oxy"]).size().unstack(fill_value=0)
    fig, ax = styled_fig(10, 4)
    if "Y" in oxy_ts.columns:
        ax.plot(oxy_ts.index, oxy_ts["Y"],  color=PINK1, linewidth=2, marker="o", markersize=3, label="With oxygen")
    if "No" in oxy_ts.columns:
        ax.plot(oxy_ts.index, oxy_ts["No"], color=PINK3, linewidth=2, marker="o", markersize=3, label="Without oxygen")
    ax.set_title("Oxygen vs Non-Oxygen Ascents Over Time", color=PINK2)
    ax.set_xlabel("Year"); ax.set_ylabel("Number of Ascents")
    ax.legend(facecolor=BG2, edgecolor=DARK, labelcolor=PINK2)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig); plt.close()


# ═══════════════════════════════════════════════════════════════════════════
# DETAILED OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════
elif section == "🔬 Detailed Overview":

    st.markdown("## H1 · Oxygen and Mortality by Age Group")
    ascents["AgeGroup"] = pd.cut(ascents["Age"],
                                  bins=[0, 35, 45, 55, 100],
                                  labels=["<35", "35–45", "45–55", "55+"])
    age_oxy = (ascents.groupby(["AgeGroup", "Oxy"], observed=True)["Dth_num"]
               .mean().reset_index())
    age_oxy["Dth_num"] *= 100

    groups    = age_oxy["AgeGroup"].unique()
    oxy_vals  = ["Y", "No"]
    x         = np.arange(len(groups))
    width     = 0.35

    fig, ax = styled_fig(9, 5)
    bars_y  = age_oxy[age_oxy["Oxy"] == "Y"]["Dth_num"].values
    bars_no = age_oxy[age_oxy["Oxy"] == "No"]["Dth_num"].values
    ax.bar(x - width/2, bars_y,  width, label="With oxygen",    color=PINK1)
    ax.bar(x + width/2, bars_no, width, label="Without oxygen", color=PINK3)
    ax.set_xticks(x); ax.set_xticklabels(groups)
    ax.set_title("Mortality Rate by Age Group and Oxygen Use", color=PINK2)
    ax.set_xlabel("Age Group"); ax.set_ylabel("Mortality Rate (%)")
    ax.legend(facecolor=BG2, edgecolor=DARK, labelcolor=PINK2)
    plt.tight_layout()
    st.pyplot(fig); plt.close()
    st.markdown("""<div class="insight-box"><b>Conclusion:</b> Mortality rates were significantly lower for climbers using supplemental oxygen. For climbers under 55, mortality dropped from 6–7% without oxygen to under 1% with it.</div>""", unsafe_allow_html=True)
    st.markdown("---")

    # H2: Mortality rate fell while ascents rose
    st.markdown("## H2 · Ascents (bars) vs Mortality rate (line) by decade")
    import plotly.graph_objects as go
    asc_d  = ascents[ascents["Year"] >= 1953].groupby("Decade").size()
    dth_d  = deaths[deaths["Year"] >= 1953].groupby("Decade").size()
    decades = sorted(set(asc_d.index) | set(dth_d.index))
    asc_p  = asc_d.reindex(decades, fill_value=0)
    dth_p  = dth_d.reindex(decades, fill_value=0)
    mort_r = (dth_p / asc_p * 100).replace([np.inf, -np.inf], np.nan).fillna(0)

    fig_p = go.Figure()
    fig_p.add_trace(go.Bar(x=[str(d) for d in decades], y=asc_p.values,
                           name="Ascents", marker_color=PINK1, opacity=0.7, yaxis="y1"))
    fig_p.add_trace(go.Scatter(x=[str(d) for d in decades], y=mort_r.values,
                                name="Mortality %", marker_color=LIGHT,
                                mode="lines+markers", line=dict(width=3), yaxis="y2"))
    fig_p.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG2, font_color=PINK2,
        title=dict(text="Ascents (bars) vs. Mortality rate (line) by decade", font_color=PINK2),
        yaxis=dict(title="Number of ascents", gridcolor="#3d1030"),
        yaxis2=dict(title="Mortality rate (%)", overlaying="y", side="right", gridcolor="#3d1030"),
        legend=dict(orientation="h", y=1.1, bgcolor=BG2, bordercolor=DARK),
        margin=dict(t=60, b=30),
    )
    st.plotly_chart(fig_p, use_container_width=True)
    st.markdown("""<div class="insight-box"><b>Conclusion:</b> From 1950s to 1990s mortality rate was higher. It peaked at 17.65% in 1980, then dropped to 2.76% in 2010s — despite record-high ascent numbers. The 2020 data point is statistical noise (only 22 ascents before COVID).</div>""", unsafe_allow_html=True)
    st.markdown("---")

    # H3: External vs Physiological
    st.markdown("## H3 · Age by Cause-of-Death Type")
    def classify_cause(cause):
        if pd.isna(cause): return "Unknown"
        t = cause.lower()
        ext = ["avalanche","fall","crevasse","serac","ice axe","rope accident","snowboarding","blizzard","snow blindness","drown"]
        phy = ["exhaustion","exposure","altitude sickness","hape","hace","oedema","edema","frostbite","hypothermia","heart","cardiac","stroke","starvation"]
        he, hp = any(k in t for k in ext), any(k in t for k in phy)
        if he and hp: return "Mixed"
        if he: return "External hazard"
        if hp: return "Physiological"
        if any(w in t for w in ["disappear","unknown","presumed dead"]): return "Unknown/Disappearance"
        return "Other"
    deaths["CauseType"] = deaths["Cause of death"].apply(classify_cause)

    subset3 = deaths[deaths["CauseType"].isin(["External hazard", "Physiological"])]
    fig, ax = styled_fig(9, 5)
    for ct, col in [("External hazard", PINK1), ("Physiological", PINK3)]:
        ages = subset3[subset3["CauseType"] == ct]["Age"]
        ax.hist(ages, bins=10, alpha=0.55, label=f"{ct} (n={len(ages)})",
                color=col, edgecolor=BG)
        ax.axvline(ages.mean(), linestyle="--", color=col, linewidth=2,
                   label=f"mean={ages.mean():.1f}")
    ax.set_title("Age distribution by cause-of-death type", color=PINK2)
    ax.set_xlabel("Age"); ax.set_ylabel("Count")
    ax.legend(facecolor=BG2, edgecolor=DARK, labelcolor=PINK2)
    st.pyplot(fig); plt.close()

    age_stats = subset3.groupby("CauseType")["Age"].agg(["mean","median","std","count"])
    diff = age_stats.loc["Physiological","mean"] - age_stats.loc["External hazard","mean"]
    st.markdown(f"""<div class="insight-box"><b>Conclusion:</b> Climbers who died from external hazards were on average <b>{diff:.1f} years younger</b>. std=12.43 vs 9.57 — among those dying from altitude/heart causes the age range is wider.</div>""", unsafe_allow_html=True)
    st.markdown("---")

    # H4: Nepal vs China
    st.markdown("## H4 · Nepal vs China/Tibet: Mortality & Oxygen")
    host_comp = ascents.groupby("Host").agg(
        MortalityRate=("Dth_num", "mean"),
        OxygenUseRate=("Oxy_num", "mean"),
        Ascents=("Dth_num", "size"),
        MeanAge=("Age", "mean"),
    )
    host_comp[["MortalityRate","OxygenUseRate"]] *= 100

    fig, axes = styled_fig2(2, 13, 5)
    hosts = host_comp.index.tolist()
    x = np.arange(len(hosts)); w = 0.35
    axes[0].bar(x - w/2, host_comp["MortalityRate"].values, w, label="Mortality %", color="#c03070")
    axes[0].bar(x + w/2, host_comp["OxygenUseRate"].values,  w, label="Oxygen use %", color=PINK1)
    axes[0].set_xticks(x); axes[0].set_xticklabels(hosts)
    axes[0].set_title("Nepal vs China/Tibet: mortality & oxygen use", color=PINK2)
    axes[0].set_ylabel("%")
    axes[0].legend(facecolor=BG2, edgecolor=DARK, labelcolor=PINK2)

    pinks2 = [PINK1, PINK3]
    axes[1].pie(host_comp["Ascents"].values, labels=hosts, autopct="%1.1f%%",
                colors=pinks2, textprops={"color": PINK2})
    axes[1].set_title("Share of ascents: Nepal vs China/Tibet", color=PINK2)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    side_decade = ascents.groupby(["Decade","Host"]).size().unstack(fill_value=0)
    fig, ax = styled_fig(10, 4)
    for i, host in enumerate(side_decade.columns):
        ax.plot(side_decade.index.astype(str), side_decade[host],
                marker="o", markersize=4, linewidth=2,
                color=[PINK1, PINK3][i % 2], label=host)
    ax.set_title("Ascents by decade: Nepal side vs China/Tibet side", color=PINK2)
    ax.set_xlabel("Decade"); ax.set_ylabel("Ascents")
    ax.legend(facecolor=BG2, edgecolor=DARK, labelcolor=PINK2)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig); plt.close()

    st.markdown("""<div class="insight-box"><b>Conclusion:</b> Hypothesis NOT supported. Nepal side mortality ~1.13% vs China/Tibet ~0.69% — a small difference. Oxygen use rates are almost identical (96.8% vs 98.2%). ~78% of all ascents are made from the Nepalese side.</div>""", unsafe_allow_html=True)
