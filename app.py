import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Everest Explorer", page_icon="🏔️", layout="wide")

# ── THEME ────────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

with st.sidebar:
    st.markdown("## 🏔️ Everest Explorer")
    st.session_state.dark_mode = st.toggle("🌙 Dark mode", value=st.session_state.dark_mode)
    st.markdown("---")
    page = st.radio("Navigate", [
        "Datasets",
        "Exploratory Plots",
        "Hypotheses",
        "Personal Stats",
    ], label_visibility="collapsed")

DARK = st.session_state.dark_mode

if DARK:
    BG = "#1a0010";
    BG2 = "#2d0020";
    BG3 = "#3d0030"
    FG = "#f7a8c4";
    FG2 = "#e8b0ca";
    FG3 = "#c47a9a"
    ACC1 = "#e05090";
    ACC2 = "#f7a8c4";
    ACC3 = "#c03070"
    BORDER = "#8b3060";
    CARD = "#2d0020"
    TEXT = "white";
    SUBTEXT = "#c47a9a"
    PLT_BG = "#1a0010";
    PLT_AX = "#2d0020";
    PLT_TICK = "#f7a8c4"
    PLT_GRID = "#3d1030"
else:
    BG = "#fff5f8";
    BG2 = "#ffe0ed";
    BG3 = "#fcc8df"
    FG = "#8b1a4a";
    FG2 = "#b03060";
    FG3 = "#c07090"
    ACC1 = "#c03070";
    ACC2 = "#e05090";
    ACC3 = "#901050"
    BORDER = "#e090b0";
    CARD = "#ffe0ed"
    TEXT = "#2a0018";
    SUBTEXT = "#904060"
    PLT_BG = "#fff5f8";
    PLT_AX = "#ffe0ed";
    PLT_TICK = "#8b1a4a"
    PLT_GRID = "#f0c0d8"

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif;}}
.stApp{{background-color:{BG};color:{FG2};}}
h1{{color:{FG}!important;font-size:2.2rem!important;font-weight:700!important;}}
h2{{color:{ACC1}!important;font-size:1.3rem!important;font-weight:600!important;margin-top:1.6rem!important;}}
h3{{color:{FG}!important;}}
section[data-testid="stSidebar"]{{background:{BG2}!important;border-right:1px solid {BORDER}!important;}}
hr{{border-color:{BG3}!important;margin:1.5rem 0!important;}}
.card{{background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:1rem 1.2rem;text-align:center;margin-bottom:.5rem;}}
.card-label{{font-size:.72rem;color:{FG3};text-transform:uppercase;letter-spacing:.06em;margin-bottom:.3rem;}}
.card-value{{font-size:1.75rem;font-weight:700;color:{FG};}}
.card-sub{{font-size:.72rem;color:{SUBTEXT};margin-top:.2rem;}}
.insight{{background:{BG2};border-left:4px solid {ACC1};border-radius:0 10px 10px 0;padding:.8rem 1.1rem;margin:.8rem 0;font-size:.88rem;color:{FG2};}}
.insight b{{color:{FG};}}
.tag{{display:inline-block;background:{BG3};color:{FG};border-radius:20px;padding:.15rem .7rem;font-size:.75rem;font-weight:600;margin:.1rem;}}
.section-badge{{display:inline-block;background:{ACC1};color:white;border-radius:8px;padding:.2rem .8rem;font-size:.8rem;font-weight:600;margin-bottom:.5rem;}}
</style>""", unsafe_allow_html=True)


def card(col, label, value, sub=""):
    col.markdown(f"""<div class="card">
        <div class="card-label">{label}</div>
        <div class="card-value">{value}</div>
        <div class="card-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)


def insight(text):
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)


def badge(text):
    st.markdown(f'<span class="section-badge">{text}</span>', unsafe_allow_html=True)


#  MATPLOTLIB THEME
plt.rcParams.update({
    "figure.facecolor": PLT_BG,
    "axes.facecolor": PLT_AX,
    "axes.edgecolor": BORDER,
    "axes.labelcolor": PLT_TICK,
    "xtick.color": PLT_TICK,
    "ytick.color": PLT_TICK,
    "text.color": PLT_TICK,
    "grid.color": PLT_GRID,
    "grid.alpha": 0.5,
})

PINKS = [ACC1, ACC2, ACC3, "#d04080", "#f0c0d8", "#a02050",
         "#e890b8", "#b83068", "#f5b8d0", "#903058",
         "#c06090", "#802040", "#fae0ec", "#701830", "#c8a0b8"]


def mfig(w=10, h=5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(PLT_BG)
    ax.set_facecolor(PLT_AX)
    for s in ax.spines.values(): s.set_edgecolor(BORDER)
    ax.tick_params(colors=PLT_TICK)
    ax.xaxis.label.set_color(PLT_TICK)
    ax.yaxis.label.set_color(PLT_TICK)
    return fig, ax


def mfig2(nc=2, w=14, h=5):
    fig, axes = plt.subplots(1, nc, figsize=(w, h))
    fig.patch.set_facecolor(PLT_BG)
    for ax in axes:
        ax.set_facecolor(PLT_AX)
        for s in ax.spines.values(): s.set_edgecolor(BORDER)
        ax.tick_params(colors=PLT_TICK)
        ax.xaxis.label.set_color(PLT_TICK)
        ax.yaxis.label.set_color(PLT_TICK)
    return fig, axes


def plotly_layout():
    return dict(
        paper_bgcolor=PLT_BG, plot_bgcolor=PLT_AX,
        font_color=PLT_TICK,
        title_font_color=FG,
        xaxis=dict(gridcolor=PLT_GRID, zerolinecolor=PLT_GRID),
        yaxis=dict(gridcolor=PLT_GRID, zerolinecolor=PLT_GRID),
        margin=dict(t=50, b=30, l=10, r=10),
    )


#  DATA
@st.cache_data
def load_data():
    bar = st.progress(0, text="Loading ascent data…")
    a = pd.read_csv("Mt_Everest_Ascent_Data.csv")
    a.columns = a.columns.str.strip()
    bar.progress(20, text="Cleaning ascent data…")
    a["Oxy_num"] = a["Oxy"].map({"Y": 1, "No": 0})
    a["Dth_num"] = a["Dth"].map({"Y": 1, ".": 0})
    a["Sex_num"] = a["Sex"].map({"M": 1, "F": 0})
    a["Year"] = a["Yr/Seas"].str.extract(r"(\d{4})").astype(int)
    a["Season"] = a["Yr/Seas"].str.extract(r"\s(\w+)$")
    a["Decade"] = (a["Year"] // 10) * 10
    a["AgeGroup"] = pd.cut(a["Age"], bins=[0, 30, 40, 50, 60, 100],
                           labels=["<30", "30–40", "40–50", "50–60", "60+"])
    a = a.dropna(subset=["Time"])
    bar.progress(50, text="Loading deaths data…")

    d = pd.read_csv("mount_everest_deaths.csv")
    d.columns = d.columns.str.strip()
    d["Year"] = d["Date"].str.extract(r"(\d{4})")
    d = d.dropna(subset=["Year"])
    d["Year"] = d["Year"].astype(int)
    d["Decade"] = (d["Year"] // 10) * 10
    d = d.dropna(subset=["Age", "Nationality", "Cause of death"])
    bar.progress(80, text="Classifying causes…")

    def classify(c):
        if pd.isna(c): return "Unknown"
        t = c.lower()
        ext = ["avalanche", "fall", "crevasse", "serac", "ice axe", "rope", "snowboarding", "blizzard", "drown"]
        phy = ["exhaustion", "exposure", "altitude sickness", "hape", "hace", "oedema", "edema",
               "frostbite", "hypothermia", "heart", "cardiac", "stroke", "starvation"]
        he, hp = any(k in t for k in ext), any(k in t for k in phy)
        if he and hp: return "Mixed"
        if he: return "External hazard"
        if hp: return "Physiological"
        if any(w in t for w in ["disappear", "unknown", "presumed"]): return "Unknown/Disappearance"
        return "Other"

    d["CauseType"] = d["Cause of death"].apply(classify)
    bar.progress(100, text="Done!")
    bar.empty()
    return a, d


ascents, deaths = load_data()

st.markdown("# 🏔️ Everest Explorer")
st.markdown(
    f"<p style='color:{SUBTEXT};margin-top:-.5rem;'>Interactive analysis of Mount Everest ascents & fatalities · 1922–2020</p>",
    unsafe_allow_html=True)
if "play_audio" not in st.session_state:
    st.session_state.play_audio = False

# Кнопка для запуска
if st.button("▶️"):
    st.session_state.play_audio = True


if st.session_state.play_audio:

    audio_url = "Labrinth - Mount Everest (Official Audio).mp3"

    st.audio(audio_url, format="audio/mp3", autoplay=True)


    if st.button("⏹️"):
        st.session_state.play_audio = False
        st.rerun()


if page == "Datasets":

    # ── Dataset 1 ────────────────────────────────────────────────────────
    badge("Dataset 1 · Ascent Records")
    st.markdown("## Mt Everest Ascent Data (1953–2020)")
    st.markdown(f"<p style='color:{SUBTEXT};'>Records of successful summit ascents on Mount Everest. "
                "Each row is one climber's summit attempt with details on age, gender, nationality, "
                "oxygen use, season, and whether the climber survived.</p>", unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    card(c1, "Total Rows", f"{len(ascents):,}", "ascent records")
    card(c2, "Columns", f"{ascents.shape[1]}", "features")
    card(c3, "Years", f"{ascents['Year'].min()}–{ascents['Year'].max()}", "covered")
    card(c4, "Nationalities", f"{ascents['Citizenship'].nunique()}", "unique countries")
    card(c5, "Null values", f"{ascents.isnull().sum().sum():,}", "across all cols")

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    card(c1, "Avg Age", f"{ascents['Age'].mean():.1f}", "years")
    card(c2, "Age Range", f"{int(ascents['Age'].min())}–{int(ascents['Age'].max())}", "years")
    card(c3, "With Oxygen", f"{ascents['Oxy_num'].mean() * 100:.1f}%", "of ascents")
    card(c4, "Mortality", f"{ascents['Dth_num'].mean() * 100:.1f}%", "died on ascent")

    st.markdown("---")
    st.markdown(f"<span class='tag'>Age</span><span class='tag'>Sex</span>"
                "<span class='tag'>Citizenship</span><span class='tag'>Oxygen (Oxy)</span>"
                "<span class='tag'>Season</span><span class='tag'>Year</span>"
                "<span class='tag'>Death (Dth)</span><span class='tag'>Host country</span>",
                unsafe_allow_html=True)

    insight("<b>Key columns:</b> <code>Oxy</code> — supplemental oxygen (Y/No), "
            "<code>Dth</code> — death indicator (Y/.), "
            "<code>Yr/Seas</code> — year and season of ascent, "
            "<code>Host</code> — Nepal or China/Tibet route.")

    st.markdown("---")

    # ── Dataset 2
    badge("Dataset 2 · Fatalities")
    st.markdown("## Mount Everest Deaths (1922–2020)")
    st.markdown(f"<p style='color:{SUBTEXT};'>Catalogue of climbers who died on Everest — "
                "including their age, nationality, date and cause of death. "
                "Covers both summiteers and those who died during approach or descent.</p>",
                unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    card(c1, "Total Deaths", f"{len(deaths):,}", "on record")
    card(c2, "Columns", f"{deaths.shape[1]}", "features")
    card(c3, "Years", f"{deaths['Year'].min()}–{deaths['Year'].max()}", "covered")
    card(c4, "Nationalities", f"{deaths['Nationality'].nunique()}", "unique")
    card(c5, "Null values", f"{deaths.isnull().sum().sum():,}", "across all cols")

    st.markdown("---")
    top_cause = deaths["Cause of death"].value_counts().index[0]
    top_nat = deaths["Nationality"].value_counts().index[0]
    peak_yr = deaths.groupby("Year").size().idxmax()
    peak_cnt = deaths.groupby("Year").size().max()
    c1, c2, c3, c4 = st.columns(4)
    card(c1, "Avg Age at Death", f"{deaths['Age'].mean():.1f}", "years")
    card(c2, "Age Range", f"{int(deaths['Age'].min())}–{int(deaths['Age'].max())}", "years")
    card(c3, "Top Nationality", top_nat, "most deaths")
    card(c4, "Deadliest Year", str(peak_yr), f"{peak_cnt} deaths")

    st.markdown("---")
    cause_types = deaths["CauseType"].value_counts()
    for ct, cnt in cause_types.items():
        pct = cnt / len(deaths) * 100
        st.markdown(f"""<div style="display:flex;align-items:center;gap:1rem;
        background:{BG2};border-radius:8px;padding:.4rem .9rem;margin:.25rem 0;">
        <span style="color:{FG};font-weight:600;min-width:180px;">{ct}</span>
        <div style="flex:1;background:{BG3};border-radius:4px;height:10px;">
          <div style="width:{pct:.1f}%;background:{ACC1};border-radius:4px;height:10px;"></div>
        </div>
        <span style="color:{FG2};min-width:60px;text-align:right;">{cnt} ({pct:.1f}%)</span>
        </div>""", unsafe_allow_html=True)

    insight("<b>Key columns:</b> <code>Cause of death</code> — raw text, "
            "classified into External hazard / Physiological / Mixed / Unknown. "
            "<code>Nationality</code>, <code>Age</code>, <code>Date</code>.")



elif page == "Exploratory Plots":

    # ── Ascent dataset plots ──────────────────────────────────────────────
    badge("Dataset 1 · Ascent Records")
    st.markdown("## Number of ascents per year")
    by_year = ascents.groupby("Year").size().reset_index(name="Ascents")
    fig, ax = mfig(10, 4)
    ax.plot(by_year["Year"], by_year["Ascents"], color=ACC1, lw=2, marker="o", ms=3)
    ax.fill_between(by_year["Year"], by_year["Ascents"], alpha=0.15, color=ACC1)
    ax.set_title("Number of ascents on Everest", color=FG, fontsize=13)
    ax.set_xlabel("Year");
    ax.set_ylabel("Ascents");
    ax.grid(True, alpha=.3)
    st.pyplot(fig);
    plt.close()
    insight("Ascents grew sharply after commercial expeditions opened in the 1990s. "
            "Notable dips: 1996 disaster, 2014–15 earthquakes, 2020 COVID closure.")
    st.markdown("---")

    st.markdown("## Climbers by Sex")
    c1, c2 = st.columns(2)
    with c1:
        sex_c = ascents["Sex"].value_counts()
        fig, ax = mfig(5, 4)
        ax.bar(sex_c.index, sex_c.values, color=[ACC1, ACC3], edgecolor=PLT_BG)
        ax.set_title("Climbers by Sex", color=FG);
        ax.set_ylabel("Count")
        st.pyplot(fig);
        plt.close()
    with c2:
        sex_yr = ascents.groupby(["Year", "Sex"]).size().unstack(fill_value=0)
        fig, ax = mfig(7, 4)
        if "M" in sex_yr.columns:
            ax.plot(sex_yr.index, sex_yr["M"], color=ACC1, lw=2, label="Male")
        if "F" in sex_yr.columns:
            ax.plot(sex_yr.index, sex_yr["F"], color=ACC3, lw=2, label="Female")
        ax.set_title("Male vs Female climbers over time", color=FG)
        ax.set_xlabel("Year");
        ax.set_ylabel("Count")
        ax.legend(facecolor=PLT_AX, edgecolor=BORDER, labelcolor=PLT_TICK)
        st.pyplot(fig);
        plt.close()
    insight("Everest climbers are overwhelmingly male (~88%). Female participation "
            "has grown since the 1990s but remains a small minority.")
    st.markdown("---")

    st.markdown("## Age distribution of ascenders")
    fig, axes = mfig2(2, 13, 4)
    fig.suptitle("Age of all climbers vs fatalities", color=FG, fontsize=13)
    axes[0].hist(ascents["Age"], bins=15, color=ACC1, edgecolor=PLT_BG, alpha=.9)
    axes[0].set_title("All climbers", color=FG)
    axes[0].set_xlabel("Age");
    axes[0].set_ylabel("Count")
    axes[1].hist(deaths["Age"], bins=15, color=ACC3, edgecolor=PLT_BG, alpha=.9)
    axes[1].set_title("Fatalities", color=FG)
    axes[1].set_xlabel("Age");
    axes[1].set_ylabel("Count")
    plt.tight_layout()
    st.pyplot(fig);
    plt.close()
    insight("Both distributions peak at 30–40 years. Fatal cases skew slightly older "
            "— physiological causes (heart, altitude sickness) increase with age.")
    st.markdown("---")

    st.markdown("## Oxygen use over time")
    oxy_ts = ascents.groupby(["Year", "Oxy"]).size().unstack(fill_value=0)
    fig, ax = mfig(10, 4)
    if "Y" in oxy_ts.columns:
        ax.plot(oxy_ts.index, oxy_ts["Y"], color=ACC1, lw=2, marker="o", ms=2, label="With oxygen")
    if "No" in oxy_ts.columns:
        ax.plot(oxy_ts.index, oxy_ts["No"], color=ACC3, lw=2, marker="o", ms=2, label="Without oxygen")
    ax.set_title("Oxygen vs Non-Oxygen Ascents Over Time", color=FG)
    ax.set_xlabel("Year");
    ax.set_ylabel("Ascents")
    ax.legend(facecolor=PLT_AX, edgecolor=BORDER, labelcolor=PLT_TICK)
    ax.grid(True, alpha=.3)
    st.pyplot(fig);
    plt.close()
    insight("Oxygen use dominates since the mid-1980s. Non-oxygen ascents remain rare "
            "elite pursuits — but carry 5–7× higher mortality.")
    st.markdown("---")

    # ── Deaths dataset plots
    badge("Dataset 2 · Fatalities")
    st.markdown("## Deaths by year & nationality")
    c1, c2 = st.columns(2)
    with c1:
        dyr = deaths.groupby("Year").size().reset_index(name="Deaths")
        fig, ax = mfig(6, 4)
        ax.bar(dyr["Year"], dyr["Deaths"], color=ACC3, edgecolor=PLT_BG, width=0.8)
        ax.set_title("Recorded fatalities per year", color=FG)
        ax.set_xlabel("Year");
        ax.set_ylabel("Deaths");
        ax.grid(axis="y", alpha=.3)
        st.pyplot(fig);
        plt.close()
    with c2:
        nat = deaths["Nationality"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 6))
        fig.patch.set_facecolor(PLT_BG);
        ax.set_facecolor(PLT_BG)
        ax.pie(nat.values, labels=nat.index, autopct="%1.1f%%",
               colors=PINKS[:len(nat)], textprops={"color": PLT_TICK}, startangle=140)
        ax.set_title("Deaths by Nationality", color=FG)
        st.pyplot(fig);
        plt.close()
    insight("Nepal experienced the most deaths — Sherpa guides face disproportionate exposure. "
            "1996 remains the single deadliest season (8 deaths in one storm).")
    st.markdown("---")

    st.markdown("## Top causes of death")
    c1, c2 = st.columns(2)
    with c1:
        dc = deaths["Cause of death"].value_counts().head(8).sort_values()
        fig, ax = mfig(7, 5)
        ax.barh(dc.index, dc.values, color=ACC1, edgecolor=PLT_BG)
        for i, v in enumerate(dc.values):
            ax.text(v + .2, i, str(v), va="center", color=PLT_TICK)
        ax.set_title("Top 8 causes of death", color=FG)
        ax.grid(axis="x", alpha=.3)
        st.pyplot(fig);
        plt.close()
    with c2:
        ct = deaths["CauseType"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 5))
        fig.patch.set_facecolor(PLT_BG);
        ax.set_facecolor(PLT_BG)
        ax.pie(ct.values, labels=ct.index, autopct="%1.1f%%",
               colors=PINKS[:len(ct)], textprops={"color": PLT_TICK})
        ax.set_title("Deaths by cause category", color=FG)
        st.pyplot(fig);
        plt.close()
    insight("Falls and avalanches dominate — external hazards kill more climbers than "
            "physiological causes combined. Exhaustion and altitude sickness are close second.")
    st.markdown("---")

    st.markdown("## Top countries by ascents")
    top_c = ascents["Citizenship"].value_counts().head(10).sort_values()
    fig, ax = mfig(9, 5)
    ax.barh(top_c.index, top_c.values, color=ACC1, edgecolor=PLT_BG)
    ax.set_title("Top 10 countries by ascents", color=FG);
    ax.grid(axis="x", alpha=.3)
    st.pyplot(fig);
    plt.close()



elif page == "Hypotheses":

    hypo = st.selectbox("Select hypothesis", [
        "H1 · Older climbers benefit more from supplemental oxygen in terms of mortality reduction than younger climbers.",
        "H2 · Mortality fell while ascents rose (1950s–2010s)",
        "H3 · Younger climbers die from hazards, older from physiology",
        "H4 · Ascents from Nepal side have higher mortality rates",
    ])

    # H1
    if "H1" in hypo:
        st.markdown("## H1 · Oxygen and Mortality by Age Group")

        age_oxy = (ascents.groupby(["AgeGroup", "Oxy"], observed=True)["Dth_num"]
                   .mean().unstack(fill_value=0) * 100)
        for c in ["Y", "No"]:
            if c not in age_oxy.columns: age_oxy[c] = 0.0
        groups = list(age_oxy.index);
        x = np.arange(len(groups));
        w = .35
        fig, ax = mfig(9, 5)
        ax.bar(x - w / 2, age_oxy["Y"].values, w, label="With oxygen", color=ACC1)
        ax.bar(x + w / 2, age_oxy["No"].values, w, label="Without oxygen", color=ACC3)
        ax.set_xticks(x);
        ax.set_xticklabels(groups)
        ax.set_title("Mortality Rate (%) by Age Group and Oxygen Use", color=FG)
        ax.set_xlabel("Age Group");
        ax.set_ylabel("Mortality (%)")
        ax.legend(facecolor=PLT_AX, edgecolor=BORDER, labelcolor=PLT_TICK)
        plt.tight_layout();
        st.pyplot(fig);
        plt.close()

        c1, c2, c3 = st.columns(3)
        card(c1, "Mortality with O₂", f"{ascents[ascents['Oxy'] == 'Y']['Dth_num'].mean() * 100:.2f}%", "all ages")
        card(c2, "Mortality w/o O₂", f"{ascents[ascents['Oxy'] == 'No']['Dth_num'].mean() * 100:.2f}%", "all ages")
        card(c3, "Risk multiplier",
             f"{ascents[ascents['Oxy'] == 'No']['Dth_num'].mean() / max(ascents[ascents['Oxy'] == 'Y']['Dth_num'].mean(), 1e-9):.1f}×",
             "higher w/o oxygen")
        insight("<b>✅ Hypothesis SUPPORTED.</b> Oxygen reduces mortality across every age group. "
                "For climbers under 55 mortality drops from ~6–7% (no O₂) to under 1% (with O₂). "
                "The protective effect is consistent and large.")

    # H2
    elif "H2" in hypo:
        st.markdown("## H2 · Ascents (bars) vs Mortality rate % (line) by decade")
        import pandas as pd
        import numpy as np
        import plotly.graph_objects as go

        asc_d = ascents[ascents["Year"] >= 1953].groupby("Decade").size()
        dth_d = deaths[deaths["Year"] >= 1953].groupby("Decade").size()

        decades = sorted(set(asc_d.index) | set(dth_d.index))

        ap = asc_d.reindex(decades, fill_value=0)
        dp = dth_d.reindex(decades, fill_value=0)
        mr = (dp / ap * 100).replace([np.inf, -np.inf], np.nan).fillna(0)

        # Mortality rate (%)
        mortality = (
            (dp / ap * 100)
            .replace([np.inf, -np.inf], np.nan)
            .fillna(0)
        )
        overview = pd.DataFrame({
            "Decade": decades,
            "Ascents": ap.values,
            "Deaths": dp.values,
            "MortalityRate_%": mortality.round(2).values
        })
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=[str(d) for d in decades],
                y=overview["Ascents"],
                name="Ascents",
                marker_color=ACC1,
                opacity=0.7,
                yaxis="y"
            )
        )

        # Line: Mortality rate
        fig.add_trace(
            go.Scatter(
                x=[str(d) for d in decades],
                y=overview["MortalityRate_%"],
                mode="lines+markers+text",
                text=[f"{v:.1f}%" for v in overview["MortalityRate_%"]],
                textposition="top center",
                name="Mortality rate (%)",
                line=dict(
                    color=ACC2,
                    width=3
                ),
                marker=dict(size=8),
                yaxis="y2"
            )
        )

        # Average mortality line
        fig.add_hline(
            y=mortality.mean(),
            line_dash="dash",
            annotation_text=f"Average mortality: {mortality.mean():.1f}%",
            annotation_position="top left"
        )

        # Layout
        fig.update_layout(


            title={
                "text": "Ascents (bars) vs. Mortality Rate (line) by Decade",
                "x": 0.5
            },



            hovermode="x unified",

            xaxis=dict(
                title="Decade",
                gridcolor=PLT_GRID
            ),

            yaxis=dict(
                title="Number of Ascents",
                gridcolor=PLT_GRID
            ),

            yaxis2=dict(
                title="Mortality Rate (%)",
                overlaying="y",
                side="right"
            ),

            legend=dict(
                orientation="h",
                y=1.1,
                bgcolor=PLT_AX,
                bordercolor=BORDER
            ),

            margin=dict(
                l=60,
                r=60,
                t=80,
                b=60
            )
        )

        st.plotly_chart(fig, use_container_width=True)
        early = mr[mr.index < 1990].mean()
        late = mr[(mr.index >= 1990) & (mr.index < 2020)].mean()
        c1, c2, c3 = st.columns(3)
        card(c1, "Avg mortality pre-1990", f"{early:.2f}%", "3 decades")
        card(c2, "Avg mortality 1990–2019", f"{late:.2f}%", "3 decades")
        card(c3, "Reduction", f"{early - late:.2f}pp", "percentage points")
        insight("<b>✅ Hypothesis SUPPORTED.</b> Mortality peaked at ~17.6% in the 1980s and "
        "fell to ~2.8% by the 2010s — the decade with the highest absolute ascent count. "
        "Better gear, forecasting and commercial logistics drove this improvement.")

# H3
    elif "H3" in hypo:
        st.markdown("## H3 · Age by Cause-of-Death Type")
        sub = deaths[deaths["CauseType"].isin(["External hazard","Physiological"])]
        fig, ax = mfig(9, 5)
        for ct, col in [("External hazard", ACC1), ("Physiological", ACC3)]:
            ages = sub[sub["CauseType"]==ct]["Age"]
            ax.hist(ages, bins=12, alpha=.6, label=f"{ct} (n={len(ages)})",
                    color=col, edgecolor=PLT_BG)
            ax.axvline(ages.mean(), ls="--", color=col, lw=2,
                       label=f"mean = {ages.mean():.1f}")
        ax.set_title("Age distribution by cause-of-death type", color=FG)
        ax.set_xlabel("Age"); ax.set_ylabel("Count")
        ax.legend(facecolor=PLT_AX, edgecolor=BORDER, labelcolor=PLT_TICK)
        st.pyplot(fig); plt.close()
 
        stats = sub.groupby("CauseType")["Age"].agg(["mean","median","std","count"])
        c1,c2,c3,c4 = st.columns(4)
        card(c1,"Mean age — External",    f"{stats.loc['External hazard','mean']:.1f}","years")
        card(c2,"Mean age — Physiology",  f"{stats.loc['Physiological','mean']:.1f}","years")
        diff = stats.loc["Physiological","mean"]-stats.loc["External hazard","mean"]
        card(c3,"Age gap",                f"+{diff:.1f} yrs","physiology older")
        card(c4,"Std dev diff",           f"{stats.loc['Physiological','std']:.1f} vs {stats.loc['External hazard','std']:.1f}","wider for physiology")
        insight(f"<b>✅ Hypothesis SUPPORTED.</b> Climbers dying from external hazards were on "
                f"average <b>{diff:.1f} years younger</b>. Physiological deaths have wider age spread "
                f"(std {stats.loc['Physiological','std']:.1f} vs {stats.loc['External hazard','std']:.1f}) — "
                "altitude illness can strike predisposed younger climbers too.")
    elif "H4" in hypo:
        st.markdown("## H4 · Nepal vs China/Tibet: mortality & oxygen")
        hc = ascents.groupby("Host").agg(
            Mortality=("Dth_num", "mean"), Oxygen=("Oxy_num", "mean"),
            Ascents=("Dth_num", "size"), MeanAge=("Age", "mean"),
        )
        hc[["Mortality", "Oxygen"]] *= 100
        hosts = hc.index.tolist();
        x = np.arange(len(hosts));
        w = .35
        fig, axes = mfig2(2, 13, 5)
        axes[0].bar(x - w / 2, hc["Mortality"].values, w, label="Mortality %", color=ACC3)
        axes[0].bar(x + w / 2, hc["Oxygen"].values, w, label="Oxygen use %", color=ACC1)
        axes[0].set_xticks(x);
        axes[0].set_xticklabels(hosts)
        axes[0].set_title("Mortality & oxygen use by side", color=FG);
        axes[0].set_ylabel("%")
        axes[0].legend(facecolor=PLT_AX, edgecolor=BORDER, labelcolor=PLT_TICK)
        axes[1].pie(hc["Ascents"].values, labels=hosts, autopct="%1.1f%%",
                    colors=[ACC1, ACC3], textprops={"color": PLT_TICK})
        axes[1].set_title("Share of ascents by side", color=FG)
        plt.tight_layout();
        st.pyplot(fig);
        plt.close()

        side_d = ascents.groupby(["Decade", "Host"]).size().unstack(fill_value=0)
        fig, ax = mfig(10, 4)
        for i, h in enumerate(side_d.columns):
            ax.plot(side_d.index.astype(str), side_d[h], marker="o", ms=4, lw=2,
                    color=[ACC1, ACC3][i % 2], label=h)
        ax.set_title("Ascents by decade: Nepal vs China/Tibet", color=FG)
        ax.set_xlabel("Decade");
        ax.set_ylabel("Ascents")
        ax.legend(facecolor=PLT_AX, edgecolor=BORDER, labelcolor=PLT_TICK)
        ax.grid(True, alpha=.3)
        st.pyplot(fig);
        plt.close()

        c1, c2, c3, c4 = st.columns(4)
        for i, h in enumerate(hosts):
            (c1 if i == 0 else c2).markdown(f"""<div class="card">
            <div class="card-label">{h} mortality</div>
            <div class="card-value">{hc.loc[h, 'Mortality']:.2f}%</div>
            <div class="card-sub">{int(hc.loc[h, 'Ascents']):,} ascents</div></div>""",
                                            unsafe_allow_html=True)
        card(c3, "Oxygen use Nepal", f"{hc.loc[hosts[0], 'Oxygen']:.1f}%", "")
        card(c4, "Oxygen use China", f"{hc.loc[hosts[-1], 'Oxygen']:.1f}%", "")
        insight("<b>❌ Hypothesis NOT SUPPORTED.</b> Nepal mortality ~1.1% vs China/Tibet ~0.7% — "
                "a small difference. Oxygen use rates are almost identical (~97% vs ~98%). "
                "~78% of all ascents start from the Nepalese side, skewing absolute numbers.")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 4 — PERSONAL STATS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Personal Stats":

    st.markdown("## How do you compare to Everest climbers?")

    col_l, col_r = st.columns([1, 2])
    with col_l:
        user_age = st.slider("Your age", int(ascents["Age"].min()), int(ascents["Age"].max()), 32)
        user_sex = st.radio("Your sex", ["M", "F"], horizontal=True,
                            format_func=lambda x: "♂ Male" if x == "M" else "♀ Female")
        user_year = st.selectbox("Explore a specific year",
                                 sorted(ascents["Year"].unique()), index=40)

    with col_r:
        # Age histogram with user line
        fig, ax = mfig(8, 3.5)
        ax.hist(ascents["Age"], bins=25, color=ACC1, edgecolor=PLT_BG, alpha=.85)
        ax.axvline(user_age, color="#ffffff", lw=3, ls="--", label=f"You ({user_age})")
        ax.set_title("Your age vs all Everest climbers", color=FG)
        ax.set_xlabel("Age");
        ax.set_ylabel("Count")
        ax.legend(facecolor=PLT_AX, edgecolor=BORDER, labelcolor=PLT_TICK)
        st.pyplot(fig);
        plt.close()

    st.markdown("---")

    # Age stats cards
    window = ascents[(ascents["Age"] >= user_age - 5) & (ascents["Age"] <= user_age + 5)]
    mort_age = window["Dth_num"].mean() * 100 if len(window) else 0
    pct_age = (ascents["Age"] <= user_age).mean() * 100

    st.markdown("###You & your age group")
    c1, c2, c3, c4 = st.columns(4)
    card(c1, "Climbers within ±5 yrs", f"{len(window):,}", "of your age")
    card(c2, "Mortality at your age", f"{mort_age:.1f}%", "in your age window")
    card(c3, "You are older than", f"{pct_age:.0f}%", "of all climbers")
    card(c4, "Your age group",
         ascents[ascents["Age"].between(user_age - 5, user_age + 5)]["AgeGroup"].mode().iloc[0]
         if len(window) else "–",
         "bucket")

    st.markdown("---")

    # Gender stats
    sex_label = "Male ♂" if user_sex == "M" else "Female ♀"
    sg = ascents[ascents["Sex"] == user_sex]
    all_m = ascents["Dth_num"].mean() * 100
    sex_m = sg["Dth_num"].mean() * 100
    sex_pct = len(sg) / len(ascents) * 100

    st.markdown(f"### {sex_label} climbers")
    c1, c2, c3, c4 = st.columns(4)
    card(c1, f"{sex_label} ascents", f"{len(sg):,}", f"{sex_pct:.1f}% of total")
    card(c2, f"{sex_label} mortality", f"{sex_m:.2f}%", "")
    card(c3, "Overall mortality", f"{all_m:.2f}%", "all genders")
    card(c4, "Difference",
         f"{'+' if sex_m > all_m else ''}{sex_m - all_m:.2f}pp",
         "vs average")

    # Sex mortality bar
    sex_mort = ascents.groupby("Sex")["Dth_num"].mean() * 100
    fig, ax = mfig(5, 3)
    bars = ax.bar(["Male", "Female"], sex_mort[["M", "F"]].values,
                  color=[ACC1 if user_sex == "M" else "#555", ACC3 if user_sex == "F" else "#555"],
                  edgecolor=PLT_BG)
    ax.set_title("Mortality rate by sex", color=FG);
    ax.set_ylabel("Mortality %")
    ax.set_ylim(0, sex_mort.max() * 1.3)
    for bar, val in zip(bars, sex_mort[["M", "F"]].values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + .03, f"{val:.2f}%",
                ha="center", va="bottom", color=PLT_TICK, fontsize=10)
    st.pyplot(fig);
    plt.close()

    st.markdown("---")

    # Year snapshot
    st.markdown(f"### 📆 Year {user_year} snapshot")
    yr = ascents[ascents["Year"] == user_year]
    yrd = deaths[deaths["Year"] == user_year]

    if len(yr) == 0:
        st.info(f"No ascent records for {user_year}.")
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        card(c1, "Total ascents", f"{len(yr):,}", "")
        card(c2, "Deaths that year", f"{len(yrd):,}", "")
        card(c3, "With oxygen", f"{yr['Oxy_num'].mean() * 100:.0f}%", "")
        card(c4, "Avg age", f"{yr['Age'].mean():.1f}", "years")
        card(c5, "Mortality", f"{yr['Dth_num'].mean() * 100:.1f}%", "that year")

        # 3 small charts for the year
        c1, c2, c3 = st.columns(3)
        with c1:
            yc = yr["Sex"].value_counts()
            fig, ax = mfig(4, 3)
            ax.bar(["Male", "Female"],
                   [yc.get("M", 0), yc.get("F", 0)],
                   color=[ACC1, ACC3], edgecolor=PLT_BG)
            ax.set_title(f"Sex in {user_year}", color=FG)
            st.pyplot(fig);
            plt.close()
        with c2:
            fig, ax = mfig(4, 3)
            ax.hist(yr["Age"].dropna(), bins=12, color=ACC3, edgecolor=PLT_BG, alpha=.9)
            ax.axvline(user_age, color="#fff", lw=2.5, ls="--", label=f"You ({user_age})")
            ax.set_title(f"Ages in {user_year}", color=FG);
            ax.set_xlabel("Age")
            ax.legend(facecolor=PLT_AX, edgecolor=BORDER, labelcolor=PLT_TICK, fontsize=8)
            st.pyplot(fig);
            plt.close()
        with c3:
            oy = yr["Oxy"].value_counts()
            fig, ax = plt.subplots(figsize=(4, 3))
            fig.patch.set_facecolor(PLT_BG);
            ax.set_facecolor(PLT_BG)
            ax.pie([oy.get("Y", 0), oy.get("No", 0)],
                   labels=["With O₂", "Without O₂"], autopct="%1.0f%%",
                   colors=[ACC1, ACC3], textprops={"color": PLT_TICK})
            ax.set_title(f"Oxygen in {user_year}", color=FG)
            st.pyplot(fig);
            plt.close()

    st.markdown("---")

    # Oxygen personal choice
    st.markdown("### 🫁 If you climbed — with or without oxygen?")
    oxy_choice = st.radio("Supplemental oxygen?", ["Yes, with oxygen", "No, without oxygen"],
                          horizontal=True)
    ov = "Y" if "Yes" in oxy_choice else "No"
    so = ascents[ascents["Oxy"] == ov]
    so_age = so[(so["Age"] >= user_age - 5) & (so["Age"] <= user_age + 5)]

    c1, c2, c3 = st.columns(3)
    card(c1, f"Mortality ({oxy_choice})", f"{so['Dth_num'].mean() * 100:.2f}%", "overall")
    card(c2, f"Mortality at your age", f"{so_age['Dth_num'].mean() * 100:.2f}%" if len(so_age) else "–", "±5 yrs")
    other = "No" if ov == "Y" else "Y"
    card(c3, "vs other choice",
         f"{ascents[ascents['Oxy'] == other]['Dth_num'].mean() * 100:.2f}%",
         "other option mortality")

    # Oxygen bar comparison
    cmp = ascents.groupby("Oxy")["Dth_num"].mean() * 100
    fig, ax = mfig(5, 3)
    cols_bar = [ACC1 if ov == "Y" else "#555", ACC3 if ov == "No" else "#555"]
    ax.bar(["With O₂", "Without O₂"], [cmp.get("Y", 0), cmp.get("No", 0)],
           color=cols_bar, edgecolor=PLT_BG)
    ax.set_title("Mortality: with vs without oxygen", color=FG)
    ax.set_ylabel("Mortality %")
    for i, (lbl, val) in enumerate([("With O₂", cmp.get("Y", 0)), ("Without O₂", cmp.get("No", 0))]):
        ax.text(i, val + .05, f"{val:.2f}%", ha="center", va="bottom", color=PLT_TICK, fontsize=10)
    st.pyplot(fig);
    plt.close()

    insight(f"<b>Your scenario:</b> {'With' if ov == 'Y' else 'Without'} oxygen, "
            f"aged {user_age}, {sex_label}. Estimated mortality in your group: "
            f"<b>{so_age['Dth_num'].mean() * 100:.2f}%</b>. "
            f"{'Oxygen cuts risk dramatically — a wise choice.' if ov == 'Y' else 'Without oxygen the risk is 5–7× higher. Summit-or-alive!'}")
