
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Smart Resource Monitor",
    page_icon="💧",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #F4F7FB;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102A43, #183B5B);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 9px;
    border-radius: 8px;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero {
    background: linear-gradient(110deg, #123B62, #2375A8);
    padding: 30px 34px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 30px;
    font-weight: 800;
    margin-bottom: 8px;
}

.hero p {
    color: #E1EFFA;
    font-size: 14px;
    margin-bottom: 0;
}

.section-title {
    color: #183B5B;
    font-size: 21px;
    font-weight: 750;
    margin-top: 20px;
    margin-bottom: 12px;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #E5EAF1;
    box-shadow: 0 3px 12px rgba(20, 45, 78, 0.05);
    min-height: 125px;
}

.metric-label {
    color: #718096;
    font-size: 13px;
    font-weight: 600;
}

.metric-value {
    color: #183B5B;
    font-size: 27px;
    font-weight: 800;
    margin-top: 8px;
}

.metric-note {
    color: #718096;
    font-size: 12px;
    margin-top: 5px;
}

div[data-testid="stDataFrame"] {
    border-radius: 12px;
}

/* Keep normal dashboard text readable */
[data-testid="stAppViewContainer"] .stMarkdown,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] li {
    color: #243B53;
}

/* Plotly chart text: prevent pale labels on white backgrounds */
.js-plotly-plot,
.js-plotly-plot .plotly,
.js-plotly-plot .main-svg {
    color: #243B53 !important;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():

    water = pd.read_csv("objective1_normal_water_usage.csv")
    electricity = pd.read_csv("objective1_normal_electricity_usage.csv")

    water["date"] = pd.to_datetime(water["date"])
    electricity["date"] = pd.to_datetime(electricity["date"])

    return water, electricity


try:
    water_df, electricity_df = load_data()

except Exception as e:
    st.error("Unable to load the CSV files. Make sure both CSV files are in the same folder as app.py.")
    st.exception(e)
    st.stop()


# --------------------------------------------------
# ANOMALY DETECTION
# --------------------------------------------------

def detect_anomalies(df, consumption, minimum, maximum):

    df = df.copy()

    df["detected_status"] = "Normal"

    abnormal = (
        (df[consumption] < df[minimum]) |
        (df[consumption] > df[maximum])
    )

    df.loc[abnormal, "detected_status"] = "Abnormal"

    return df


water_df = detect_anomalies(
    water_df,
    "daily_total_liters",
    "normal_baseline_min_liters",
    "normal_baseline_max_liters"
)

electricity_df = detect_anomalies(
    electricity_df,
    "daily_total_kwh",
    "normal_baseline_min_kwh",
    "normal_baseline_max_kwh"
)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def metric_card(label, value, note, symbol):

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{symbol} &nbsp; {label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)


def style_chart(fig):
    """Apply consistent high-contrast styling to every Plotly chart."""
    fig.update_layout(
        template="plotly_white",
        font=dict(
            family="Inter, Arial, sans-serif",
            size=13,
            color="#243B53"
        ),
        title=dict(
            font=dict(size=17, color="#183B5B")
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        legend=dict(
            font=dict(size=12, color="#243B53"),
            title_font=dict(color="#243B53")
        ),
        xaxis=dict(
            title_font=dict(size=13, color="#243B53"),
            tickfont=dict(size=11, color="#526579"),
            gridcolor="#E5EBF2",
            zerolinecolor="#C8D3DF"
        ),
        yaxis=dict(
            title_font=dict(size=13, color="#243B53"),
            tickfont=dict(size=11, color="#526579"),
            gridcolor="#E5EBF2",
            zerolinecolor="#C8D3DF"
        ),
        hoverlabel=dict(
            bgcolor="#183B5B",
            bordercolor="#183B5B",
            font=dict(color="#FFFFFF", size=12)
        )
    )
    return fig


def donut_chart(df, title):

    counts = (
        df["detected_status"]
        .value_counts()
        .reindex(["Normal", "Abnormal"], fill_value=0)
        .reset_index()
    )

    counts.columns = ["Status", "Count"]

    fig = px.pie(
        counts,
        names="Status",
        values="Count",
        hole=0.65,
        color="Status",
        color_discrete_map={
            "Normal": "#20A779",
            "Abnormal": "#E45B65"
        }
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        marker=dict(line=dict(color="white", width=3))
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#183B5B")),
        showlegend=False,
        height=330,
        margin=dict(t=55, b=15, l=15, r=15),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return style_chart(fig)


def daily_bar_chart(df, consumption, title, y_title, color):

    daily = (
        df.groupby("date", as_index=False)[consumption]
        .sum()
        .sort_values("date")
    )

    fig = px.bar(
        daily,
        x="date",
        y=consumption,
        title=title,
        color_discrete_sequence=[color],
        labels={
            "date": "Date",
            consumption: y_title
        }
    )

    fig.update_layout(
        height=350,
        paper_bgcolor="white",
        plot_bgcolor="white",
        title_font=dict(size=16, color="#183B5B"),
        margin=dict(t=55, b=30, l=20, r=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#E9EEF5")
    )

    return style_chart(fig)


def location_chart(df, consumption, title, y_title, color):

    location = (
        df.groupby("site_name", as_index=False)[consumption]
        .mean()
        .sort_values(consumption, ascending=True)
    )

    fig = px.bar(
        location,
        x=consumption,
        y="site_name",
        orientation="h",
        title=title,
        color_discrete_sequence=[color],
        labels={
            "site_name": "Location",
            consumption: y_title
        }
    )

    fig.update_layout(
        height=350,
        paper_bgcolor="white",
        plot_bgcolor="white",
        title_font=dict(size=16, color="#183B5B"),
        margin=dict(t=55, b=25, l=20, r=20),
        yaxis=dict(showgrid=False),
        xaxis=dict(gridcolor="#E9EEF5")
    )

    return style_chart(fig)


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.markdown("# 💧 Smart Monitor")
st.sidebar.markdown("### Resource Management System")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "🏠 Overview",
        "💧 Water Monitoring",
        "⚡ Electricity Monitoring",
        "🚨 Anomaly Detection"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Smart Resource Monitoring System")
st.sidebar.caption("Water • Electricity • Anomaly Detection")


# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

if page == "🏠 Overview":

    st.markdown("""
    <div class="hero">
        <h1>Smart Resource Monitoring Dashboard</h1>
        <p>Monitor consumption, compare usage patterns and identify unusual resource consumption.</p>
    </div>
    """, unsafe_allow_html=True)

    total_water = water_df["daily_total_liters"].sum()
    total_electricity = electricity_df["daily_total_kwh"].sum()

    water_abnormal = (water_df["detected_status"] == "Abnormal").sum()
    electricity_abnormal = (electricity_df["detected_status"] == "Abnormal").sum()

    total_records = len(water_df) + len(electricity_df)
    total_abnormal = water_abnormal + electricity_abnormal
    total_normal = total_records - total_abnormal

    st.markdown('<div class="section-title">System Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Total Water Usage", f"{total_water:,.0f} L", "Across all recorded locations", "💧")

    with c2:
        metric_card("Total Electricity Usage", f"{total_electricity:,.1f} kWh", "Across all recorded locations", "⚡")

    with c3:
        metric_card("Normal Records", f"{total_normal}", "Consumption within expected range", "✅")

    with c4:
        metric_card("Abnormal Records", f"{total_abnormal}", "Records requiring investigation", "🚨")

    st.markdown('<div class="section-title">Daily Consumption Trends</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            daily_bar_chart(
                water_df,
                "daily_total_liters",
                "Daily Water Consumption",
                "Water (Litres)",
                "#2998D5"
            ),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            daily_bar_chart(
                electricity_df,
                "daily_total_kwh",
                "Daily Electricity Consumption",
                "Electricity (kWh)",
                "#E9A23B"
            ),
            use_container_width=True
        )

    st.markdown('<div class="section-title">Consumption Status</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            donut_chart(water_df, "Water Usage Status"),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            donut_chart(electricity_df, "Electricity Usage Status"),
            use_container_width=True
        )

    st.markdown('<div class="section-title">Location-wise Comparison</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            location_chart(
                water_df,
                "daily_total_liters",
                "Average Water Usage by Location",
                "Average Litres",
                "#2998D5"
            ),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            location_chart(
                electricity_df,
                "daily_total_kwh",
                "Average Electricity Usage by Location",
                "Average kWh",
                "#E9A23B"
            ),
            use_container_width=True
        )

    st.markdown('<div class="section-title">Recent Abnormal Records</div>', unsafe_allow_html=True)

    abnormal_water = water_df[
        water_df["detected_status"] == "Abnormal"
    ][["date", "site_name", "daily_total_liters", "detected_status"]]

    abnormal_electricity = electricity_df[
        electricity_df["detected_status"] == "Abnormal"
    ][["date", "site_name", "daily_total_kwh", "detected_status"]]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**💧 Water Alerts**")
        st.dataframe(abnormal_water, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**⚡ Electricity Alerts**")
        st.dataframe(abnormal_electricity, use_container_width=True, hide_index=True)


# --------------------------------------------------
# WATER MONITORING PAGE
# --------------------------------------------------

elif page == "💧 Water Monitoring":

    st.markdown("""
    <div class="hero">
        <h1>💧 Water Monitoring</h1>
        <p>Analyse water consumption patterns and identify unusual usage across locations.</p>
    </div>
    """, unsafe_allow_html=True)

    selected_site = st.selectbox(
        "Select Location",
        ["All Locations"] + sorted(water_df["site_name"].unique().tolist())
    )

    filtered = water_df.copy()

    if selected_site != "All Locations":
        filtered = filtered[filtered["site_name"] == selected_site]

    total = filtered["daily_total_liters"].sum()
    normal = (filtered["detected_status"] == "Normal").sum()
    abnormal = (filtered["detected_status"] == "Abnormal").sum()

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Total Water Usage", f"{total:,.0f} L", "For selected location and period", "💧")

    with c2:
        metric_card("Normal Records", str(normal), "Within expected range", "✅")

    with c3:
        metric_card("Abnormal Records", str(abnormal), "Outside expected range", "🚨")

    st.markdown('<div class="section-title">Water Consumption Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            daily_bar_chart(
                filtered,
                "daily_total_liters",
                "Daily Water Usage",
                "Litres",
                "#2998D5"
            ),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            donut_chart(filtered, "Water Usage Status"),
            use_container_width=True
        )

    st.markdown('<div class="section-title">Water Usage by Activity</div>', unsafe_allow_html=True)

    water_categories = [
        "drinking_cooking_1",
        "bathing_personal_care_1",
        "toilet_sanitation_1",
        "cleaning_1",
        "gardening_1",
        "process_cooling_1"
    ]

    water_categories = [
        c for c in water_categories if c in filtered.columns
    ]

    if water_categories:
        category_data = filtered[water_categories].sum().reset_index()
        category_data.columns = ["Activity", "Litres"]
        category_data["Activity"] = (
            category_data["Activity"]
            .str.replace("_1", "", regex=False)
            .str.replace("_", " ")
            .str.title()
        )

        fig = px.bar(
            category_data.sort_values("Litres"),
            x="Litres",
            y="Activity",
            orientation="h",
            color="Litres",
            color_continuous_scale="Blues",
            title="Water Consumption Breakdown"
        )

        fig.update_layout(
            height=380,
            paper_bgcolor="white",
            plot_bgcolor="white",
            coloraxis_showscale=False
        )

        fig = style_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Water Consumption Records</div>', unsafe_allow_html=True)

    st.dataframe(
        filtered.sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# ELECTRICITY MONITORING PAGE
# --------------------------------------------------

elif page == "⚡ Electricity Monitoring":

    st.markdown("""
    <div class="hero">
        <h1>⚡ Electricity Monitoring</h1>
        <p>Track electricity consumption and analyse usage across different locations and appliances.</p>
    </div>
    """, unsafe_allow_html=True)

    selected_site = st.selectbox(
        "Select Location",
        ["All Locations"] + sorted(electricity_df["site_name"].unique().tolist())
    )

    filtered = electricity_df.copy()

    if selected_site != "All Locations":
        filtered = filtered[filtered["site_name"] == selected_site]

    total = filtered["daily_total_kwh"].sum()
    normal = (filtered["detected_status"] == "Normal").sum()
    abnormal = (filtered["detected_status"] == "Abnormal").sum()

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Total Electricity Usage", f"{total:,.1f} kWh", "For selected location and period", "⚡")

    with c2:
        metric_card("Normal Records", str(normal), "Within expected range", "✅")

    with c3:
        metric_card("Abnormal Records", str(abnormal), "Outside expected range", "🚨")

    st.markdown('<div class="section-title">Electricity Consumption Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            daily_bar_chart(
                filtered,
                "daily_total_kwh",
                "Daily Electricity Usage",
                "kWh",
                "#E9A23B"
            ),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            donut_chart(filtered, "Electricity Usage Status"),
            use_container_width=True
        )

    st.markdown('<div class="section-title">Electricity Usage by Appliance</div>', unsafe_allow_html=True)

    electricity_categories = [
        "lighting_kwh",
        "fans_kwh",
        "refrigerator_kwh",
        "cooking_appliances_kwh",
        "washing_and_cleaning_kwh",
        "electronics_kwh",
        "air_conditioning_kwh",
        "other_kwh"
    ]

    electricity_categories = [
        c for c in electricity_categories if c in filtered.columns
    ]

    if electricity_categories:
        category_data = filtered[electricity_categories].sum().reset_index()
        category_data.columns = ["Appliance", "kWh"]
        category_data["Appliance"] = (
            category_data["Appliance"]
            .str.replace("_kwh", "", regex=False)
            .str.replace("_", " ")
            .str.title()
        )

        fig = px.bar(
            category_data.sort_values("kWh"),
            x="kWh",
            y="Appliance",
            orientation="h",
            color="kWh",
            color_continuous_scale="Oranges",
            title="Electricity Consumption Breakdown"
        )

        fig.update_layout(
            height=400,
            paper_bgcolor="white",
            plot_bgcolor="white",
            coloraxis_showscale=False
        )

        fig = style_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Electricity Consumption Records</div>', unsafe_allow_html=True)

    st.dataframe(
        filtered.sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# ANOMALY DETECTION PAGE
# --------------------------------------------------

elif page == "🚨 Anomaly Detection":

    st.markdown("""
    <div class="hero">
        <h1>🚨 Anomaly Detection Centre</h1>
        <p>Identify consumption records that fall outside their expected baseline ranges.</p>
    </div>
    """, unsafe_allow_html=True)

    water_abnormal = water_df[
        water_df["detected_status"] == "Abnormal"
    ].copy()

    electricity_abnormal = electricity_df[
        electricity_df["detected_status"] == "Abnormal"
    ].copy()

    total_alerts = len(water_abnormal) + len(electricity_abnormal)

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Total Alerts", str(total_alerts), "Water and electricity combined", "🚨")

    with c2:
        metric_card("Water Alerts", str(len(water_abnormal)), "Outside water baseline range", "💧")

    with c3:
        metric_card("Electricity Alerts", str(len(electricity_abnormal)), "Outside electricity baseline range", "⚡")

    st.markdown('<div class="section-title">Detected Abnormalities</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["💧 Water Alerts", "⚡ Electricity Alerts"])

    with tab1:

        if len(water_abnormal) > 0:

            st.warning(f"{len(water_abnormal)} abnormal water consumption records detected.")

            st.dataframe(
                water_abnormal[
                    [
                        "date",
                        "site_name",
                        "daily_total_liters",
                        "normal_baseline_min_liters",
                        "normal_baseline_max_liters",
                        "detected_status"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        else:
            st.success("No abnormal water consumption records detected.")

    with tab2:

        if len(electricity_abnormal) > 0:

            st.warning(f"{len(electricity_abnormal)} abnormal electricity consumption records detected.")

            st.dataframe(
                electricity_abnormal[
                    [
                        "date",
                        "site_name",
                        "daily_total_kwh",
                        "normal_baseline_min_kwh",
                        "normal_baseline_max_kwh",
                        "detected_status"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        else:
            st.success("No abnormal electricity consumption records detected.")

    st.info(
        "An abnormal record means consumption is outside the expected baseline range. "
        "It may indicate possible wastage or unusual activity, but further investigation "
        "is needed to identify the actual cause."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#8795A5;font-size:12px;'>"
    "Smart Resource Monitoring System | Water & Electricity Analytics"
    "</p>",
    unsafe_allow_html=True
)



