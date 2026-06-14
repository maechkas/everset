
import time

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Everest Explorer",
    page_icon="🏔️",
    layout="wide"
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #E8F1F5 0%, #FFFFFF 60%);
    }
    h1, h2, h3 {
        color: #1B3A4B;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    ascents = pd.read_csv("Mt_Everest_Ascent_Data.csv")
    ascents.columns = ascents.columns.str.strip()

    ascents["Oxy_num"] = ascents["Oxy"].map({"Y": 1, "No": 0})
    ascents["Dth_num"] = ascents["Dth"].map({"Y": 1, ".": 0})

    ascents["Year"] = (
        ascents["Yr/Seas"]
        .str.extract(r"(\d{4})")
        .astype(int)
    )

    ascents["Season"] = ascents["Yr/Seas"].str.extract(r"\s(\w+)$")

    ascents = ascents.dropna(subset=["Time"])

    deaths = pd.read_csv("mount_everest_deaths.csv")
    deaths.columns = deaths.columns.str.strip()

    deaths["Year"] = deaths["Date"].str.extract(r"(\d{4})")
    deaths = deaths.dropna(subset=["Year"])

    deaths["Year"] = deaths["Year"].astype(int)

    deaths = deaths.dropna(
        subset=["Age", "Nationality", "Cause of death"]
    )

    return ascents, deaths


ascents, deaths = load_data()


st.title("🏔️ Everest Explorer")

st.caption(
    "An interactive analysis of Mount Everest ascent records "
    "and climber fatalities."
)

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

# Key metrics

st.markdown("## 📊 Key Statistics")

col1, col2, col3, col4 = st.columns(4)

placeholders = [
    col1.empty(),
    col2.empty(),
    col3.empty(),
    col4.empty()
]

targets = [
    ("Total Ascents", len(ascents), ""),
    ("Recorded Fatalities", len(deaths), ""),
    (
        "Years Covered",
        ascents["Year"].max() - ascents["Year"].min(),
        " years"
    ),
    (
        "Average Mortality Rate",
        round(ascents["Dth_num"].mean() * 100, 1),
        "%"
    ),
]

if "animated" not in st.session_state:
    for step in range(11):
        for ph, (label, value, suffix) in zip(placeholders, targets):

            current = value * step / 10

            if isinstance(value, int) and suffix == "":
                ph.metric(label, f"{int(current):,}")
            else:
                ph.metric(label, f"{current:.1f}{suffix}")

        time.sleep(0.03)

    st.session_state.animated = True

else:
    for ph, (label, value, suffix) in zip(placeholders, targets):

        if isinstance(value, int) and suffix == "":
            ph.metric(label, f"{value:,}")
        else:
            ph.metric(label, f"{value:.1f}{suffix}")

st.markdown("---")

# Age analysis


st.markdown("## Age Analysis")

st.write(
    "Select an age to compare it with the age distribution "
    "of Everest climbers."
)

age = st.slider("Your age", 16, 76, 30)

window = ascents[
    (ascents["Age"] >= age - 5)
    & (ascents["Age"] <= age + 5)
]

mortality = (
    window["Dth_num"].mean() * 100
    if len(window)
    else 0
)

percentile = (
    (ascents["Age"] <= age).mean() * 100
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Climbers within ±5 years",
    f"{len(window):,}"
)

c2.metric(
    "Mortality Rate",
    f"{mortality:.1f}%"
)

c3.metric(
    "Older than",
    f"{percentile:.0f}% of climbers"
)

fig = px.histogram(
    ascents,
    x="Age",
    nbins=25,
    title="Age Distribution of Everest Climbers",
    color_discrete_sequence=["#4C8FA8"]
)

fig.add_vline(
    x=age,
    line_color="#E8743B",
    line_width=4,
    annotation_text="Selected age",
    annotation_position="top"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("---")

# Bubble chart by country

st.markdown(
    "## 🌍 Leading Countries by Number of Ascents"
)

st.write(
    "Each bubble represents a country. "
    "Bubble size corresponds to the number of recorded ascents."
)

top_countries = (
    ascents["Citizenship"]
    .value_counts()
    .head(12)
    .reset_index()
)

top_countries.columns = [
    "Citizenship",
    "Count"
]

if "bubble_seed" not in st.session_state:
    st.session_state.bubble_seed = 0

if st.button("🔀 Shuffle Bubbles"):
    st.session_state.bubble_seed += 1

rng = np.random.default_rng(
    st.session_state.bubble_seed
)

top_countries["x"] = rng.uniform(
    0, 10, size=len(top_countries)
)

top_countries["y"] = rng.uniform(
    0, 10, size=len(top_countries)
)

fig_bubble = px.scatter(
    top_countries,
    x="x",
    y="y",
    size="Count",
    color="Citizenship",
    text="Citizenship",
    size_max=80,
    title="Top 12 Countries by Number of Ascents"
)

fig_bubble.update_traces(
    textposition="middle center",
    textfont_size=11
)

fig_bubble.update_xaxes(visible=False)
fig_bubble.update_yaxes(visible=False)

fig_bubble.update_layout(
    showlegend=False,
    height=500
)

st.plotly_chart(
    fig_bubble,
    use_container_width=True
)

st.markdown("---")


# Oxygen analysis

st.markdown(
    "## Supplemental Oxygen and Mortality"
)

oxy_choice = st.radio(
    "Select a climbing style:",
    [
        "With Oxygen (Y)",
        "Without Oxygen (No)"
    ],
    horizontal=True,
)

oxy_val = (
    "Y"
    if "With Oxygen" in oxy_choice
    else "No"
)

subset = ascents[
    ascents["Oxy"] == oxy_val
]

rate = (
    subset["Dth_num"].mean() * 100
)

c1, c2 = st.columns([1, 2])

with c1:
    st.metric(
        "Number of Ascents",
        f"{len(subset):,}"
    )

    st.metric(
        "Mortality Rate",
        f"{rate:.2f}%"
    )

with c2:
    compare = (
        ascents
        .groupby("Oxy")["Dth_num"]
        .mean()
        .reset_index()
    )

    compare["Dth_num"] *= 100

    compare["Highlight"] = compare["Oxy"].apply(
        lambda x:
        "Selected"
        if x == oxy_val
        else "Other"
    )

    fig_oxy = px.bar(
        compare,
        x="Oxy",
        y="Dth_num",
        color="Highlight",
        title="Mortality Rate (%) With vs Without Supplemental Oxygen",
        labels={
            "Dth_num": "Mortality Rate (%)",
            "Oxy": "Oxygen"
        },
        text_auto=".2f"
    )

    fig_oxy.update_layout(
        showlegend=False
    )

    st.plotly_chart(
        fig_oxy,
        use_container_width=True
    )

st.markdown("---")

# Animated chart by year

st.markdown("## Ascents Through Time")

by_year = (
    ascents
    .groupby(["Year", "Sex"])
    .size()
    .reset_index(name="Climbers")
)

fig_anim = px.bar(
    by_year,
    x="Sex",
    y="Climbers",
    color="Sex",
    animation_frame="Year",
    range_y=[
        0,
        by_year["Climbers"].max() + 2
    ],
    title="Male and Female Climbers by Year"
)

fig_anim.update_layout(
    showlegend=False
)

st.plotly_chart(
    fig_anim,
    use_container_width=True
)

st.markdown("---")

# Causes of death

st.markdown(
    "## Leading Causes of Death"
)

cause_counts = (
    deaths["Cause of death"]
    .value_counts()
    .head(7)
)

fig_pie = go.Figure(
    data=[
        go.Pie(
            labels=cause_counts.index,
            values=cause_counts.values,
            hole=0.45,
            pull=[0.05] * len(cause_counts),
        )
    ]
)

fig_pie.update_layout(
    title="Top 7 Causes of Death on Mount Everest"
)

st.plotly_chart(
    fig_pie,
    use_container_width=True
)

st.markdown(
    """
    <div style="
    background:#FFF6EF;
    border-left:4px solid #E8743B;
    border-radius:8px;
    padding:0.8rem 1.1rem;
    ">
    <b>Key Insight:</b>
    Falls and avalanches account for the largest share of fatalities,
    highlighting the impact of environmental hazards.
    Exhaustion, altitude sickness, and frostbite are also significant
    factors affecting climber survival.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")


