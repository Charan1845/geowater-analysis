from pathlib import Path

import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import plotly.express as px
import json

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------

st.set_page_config(
    page_title="GeoWater Analytics",
    page_icon="🌍",
    layout="wide"
)

# ----------------------------------------------------
# CUSTOM CSS
# ----------------------------------------------------

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
}

[data-testid="metric-container"]{
    background:#ffffff;
    border-radius:16px;
    padding:20px;
    border:1px solid #E5E7EB;
    box-shadow:0px 6px 18px rgba(0,0,0,0.12);
}

[data-testid="stMetricLabel"]{
    font-size:17px;
    font-weight:600;
}

[data-testid="stMetricValue"]{
    font-size:30px;
    font-weight:bold;
    color:#1565C0;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# TITLE
# ----------------------------------------------------

st.markdown("""
<h1 style='text-align:center;color:#1565C0;margin-bottom:0px;'>
🌍 GeoWater Analytics Dashboard
</h1>

<h4 style='text-align:center;color:#666666;margin-top:0px;'>
Geospatial Water Resource Monitoring System for Telangana
</h4>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# LOAD DATA
# ----------------------------------------------------

@st.cache_data
def load_excel():
    return pd.read_excel(
        DATA_DIR / "drought_Output.xlsx"
    )

@st.cache_data
def load_geo():
    return gpd.read_file(
        DATA_DIR / "Telangana.geojson"
    )

# Andhra Pradesh outline (optional)
df = load_excel()
gdf = load_geo()

# ----------------------------------------------------
# DISTRICT NAME FIX
# ----------------------------------------------------

df["District"] = df["District"].replace({
    "Hanumakonda": "Warangal Urban",
    "Warangal": "Warangal Rural",
    "Kumaram Bheem Asifabad": "Komarambheem Asifabad",
    "Medchal-Malkajgiri": "Medchal Malkajgiri",
    "Ranga Reddy": "Rangareddy"
})

# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------

# ----------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------

st.sidebar.header("📌 Filters")

year = st.sidebar.selectbox(
    "Select Year",
    sorted(df["Year"].unique())
)

filtered = df[df["Year"] == year]

district = st.sidebar.selectbox(
    "Select District",
    ["All"] + sorted(filtered["District"].unique())
)

if district != "All":
    filtered = filtered[filtered["District"] == district]

# ----------------------------------------------------
# KPI CARDS
# ----------------------------------------------------

highest_drought = filtered.loc[
    filtered["Drought Percentage"].idxmax()
]

best_water = filtered.loc[
    filtered["Water Availability"].idxmax()
]

total_capacity = filtered["Dam Water Capacity (MCM)"].sum()

critical = (
    filtered["Drought Percentage"] >= 50
).sum()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "🚨 Highest Drought",
        highest_drought["District"]
    )
    st.markdown(
        f"<p style='color:red;font-weight:bold;'>"
        f"{highest_drought['Drought Percentage']:.1f}%</p>",
        unsafe_allow_html=True
    )

with c2:
    st.metric(
        "💧 Best Water Availability",
        best_water["District"]
    )
    st.markdown(
        f"<p style='color:green;font-weight:bold;'>"
        f"{best_water['Water Availability']:.1f}%</p>",
        unsafe_allow_html=True
    )

with c3:
    st.metric(
        "🏞 Reservoir Capacity",
        f"{total_capacity:,.0f} MCM"
    )
    st.caption("Total Reservoir Storage")

with c4:
    st.metric(
        "⚠ Critical Districts",
        critical
    )
    st.caption(f"{critical} of {len(filtered)} districts")

st.divider()

    
# ----------------------------------------------------
# MAP
# ----------------------------------------------------
# ----------------------------------------------------
# WATER AVAILABILITY MAP
# ----------------------------------------------------

# ----------------------------------------------------
# MAP + TOP 10 PANEL
# ----------------------------------------------------

left, right = st.columns([2.3, 1])

# ====================================================
# LEFT : TELANGANA MAP
# ====================================================

with left:

    st.subheader("🗺 Telangana Water Availability Map")

    merged = gdf.merge(
        filtered,
        left_on="D_NAME",
        right_on="District",
        how="left"
    )

    def category(x):
        if pd.isna(x):
            return 0
        elif x < 50:
            return 1
        elif x < 70:
            return 2
        else:
            return 3

    merged["Category"] = merged["Water Availability"].apply(category)
    def drought_category(x):
        if pd.isna(x):
            return 0
        elif x < 50:
            return 1
        else:
            return 2

    merged["DroughtCategory"] = merged["Drought Percentage"].apply(drought_category)
    with open(
        DATA_DIR / "Telangana.geojson",
        "r"
    ) as f:
        geojson = json.load(f)

    fig = go.Figure()

# --------------------------
# Andhra Pradesh Background
# --------------------------

    # -------------------------------------------------
    # Telangana Layer
    # -------------------------------------------------

    fig.add_trace(
        go.Choropleth(
            geojson=geojson,
            featureidkey="properties.D_NAME",
            locations=merged["D_NAME"],
            z=merged["Category"],
            zmin=1,
            zmax=3,

            colorscale=[
                [0.00, "#FFFFFF"],
                [0.33, "#FFFFFF"],
                [0.34, "#BFE9FF"],
                [0.66, "#BFE9FF"],
                [0.67, "#1565C0"],
                [1.00, "#1565C0"]
            ],

            marker_line_color="black",
            marker_line_width=1,

            customdata=merged[
                [
                    "District",
                    "Water Availability",
                    "Rainfall (mm)",
                    "Dam Water Capacity (MCM)",
                    "Drought Percentage"
                ]
            ],

            hovertemplate=
                "<b>%{customdata[0]}</b><br><br>"
                "💧 Water Availability : %{customdata[1]:.2f}%<br>"
                "🌧 Rainfall : %{customdata[2]:.2f} mm<br>"
                "🏞 Dam Capacity : %{customdata[3]:.2f} MCM<br>"
                "🚨 Drought : %{customdata[4]:.2f}%<extra></extra>",

            showscale=False
        )
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(
    height=820,
    paper_bgcolor="white",
    plot_bgcolor="white",

    hoverlabel=dict(
        bgcolor="rgba(0,0,0,0.4)",
        font=dict(color="white", size=13)
    ),

    margin=dict(l=0,r=0,t=5,b=5),

    geo=dict(
        bgcolor="white",
        showframe=False,
        showcountries=False,
        showcoastlines=False
    )
)
     
    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.divider()

st.subheader("🌵 Telangana Drought Percentage Map")

fig2 = go.Figure()

fig2.add_trace(
    go.Choropleth(
        geojson=geojson,
        featureidkey="properties.D_NAME",
        locations=merged["D_NAME"],
        z=merged["DroughtCategory"],
        zmin=1,
        zmax=2,

      colorscale=[
    [0.00, "#BFE9FF"],   # Light Blue (<50%)
    [0.50, "#BFE9FF"],
    [0.51, "#E53935"],   # Red (≥50%)
    [1.00, "#E53935"]
],

        marker_line_color="black",
        marker_line_width=1,

        customdata=merged[
            [
                "District",
                "Drought Percentage",
                "Rainfall (mm)",
                "Dam Water Capacity (MCM)"
            ]
        ],

        hovertemplate=
        "<b>%{customdata[0]}</b><br><br>"
        "🌵 Drought : %{customdata[1]:.2f}%<br>"
        "🌧 Rainfall : %{customdata[2]:.2f} mm<br>"
        "🏞 Dam Capacity : %{customdata[3]:.2f} MCM<extra></extra>",

        showscale=False
    )
)

fig2.update_geos(
    fitbounds="locations",
    visible=False
)

fig2.update_layout(
    height=820,
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=0,r=0,t=5,b=5),
    geo=dict(
        bgcolor="white",
        showframe=False,
        showcountries=False,
        showcoastlines=False
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

c1, c2 = st.columns(2)

with c1:
    st.success("🔵 Drought < 50%")

with c2:
    st.error("🔴 Drought ≥ 50%")

st.divider()

# ----------------------------------------------------
# LEGEND
# ----------------------------------------------------

# ----------------------------------------------------
# LEGEND
# ----------------------------------------------------

c1, c2, c3 = st.columns(3)

with c1:
    st.error("🔴 Low Water Availability (<50%)")

with c2:
    st.warning("🟡 Medium Water Availability (50–69%)")

with c3:
    st.success("🟢 High Water Availability (≥70%)")

st.divider()
# ----------------------------------------------------
# DATA TABLE
# ----------------------------------------------------

st.subheader("📋 District Dataset")

st.dataframe(
    filtered[
        [
            "District",
            "Rainfall (mm)",
            "Dam Water Capacity (MCM)",
            "Water Availability",
            "Drought Percentage"
        ]
    ].sort_values("District"),
    use_container_width=True,
    hide_index=True
)

# ----------------------------------------------------
# DOWNLOAD
# ----------------------------------------------------

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download Filtered Dataset",
    csv,
    file_name=f"GeoWater_{year}.csv",
    mime="text/csv"
)

st.markdown("---")

st.caption(
    "🌍 GeoWater Analytics • Telangana Water Resource Monitoring Dashboard"
)