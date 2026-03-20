"""
Python to Browser App - Construction Data Tool
A Streamlit application that reads Excel construction data and displays interactive charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Precast Production Tracking",
    layout="wide"
)

# App title
st.title("PRECAST PRODUCTION TRACKING 🏗️")
st.markdown("---")

# File path
excel_file = Path("data.xlsx")

# Function to load data
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name="Sheet1")
        df.columns = df.columns.str.strip()
        df["TARGET START OF PRODUCTION"] = pd.to_datetime(df["TARGET START OF PRODUCTION"], errors="coerce")
        return df, None
    except FileNotFoundError:
        return None, "❌ Error: data.xlsx not found!"
    except Exception as e:
        return None, f"❌ Error loading file: {str(e)}"

# Reload button
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("🔄 Reload Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Load the data
df, error = load_data(excel_file)

if error:
    st.error(error)
    st.stop()

# Sidebar
with st.sidebar:
    st.header("🔍 Filters")
    level = st.selectbox("FLOOR LEVEL", ["All"] + list(df["LEVEL"].unique()))
    type = st.selectbox("ELEMENT TYPE", ["All"] + list(df["TYPE"].unique()))
    date = st.selectbox("PRODUCTION DATE", ["All"] + list(df["TARGET START OF PRODUCTION"].dt.strftime("%d-%b-%Y").unique()))
    status = st.selectbox("PRODUCTION STATUS", ["All"] + list(df["STATUS"].unique()))

# Apply filters
filtered_df = df.copy()
if level != "All":
    filtered_df = filtered_df[filtered_df["LEVEL"] == level]
if type != "All":
    filtered_df = filtered_df[filtered_df["TYPE"] == type]
if date != "All":
    selected_date = pd.to_datetime(date).date()

    filtered_df["TARGET START OF PRODUCTION"] = pd.to_datetime(
        filtered_df["TARGET START OF PRODUCTION"], errors="coerce")

    filtered_df = filtered_df[
        filtered_df["TARGET START OF PRODUCTION"].dt.date == selected_date]
if status != "All":
    filtered_df = filtered_df[filtered_df["STATUS"] == status]

# Total volume from filtered data
total_volume = filtered_df["VOLUME (CU. M)"].sum()
completed_volume = filtered_df[filtered_df["STATUS"] == "Completed"]["VOLUME (CU. M)"].sum()
pending_volume = filtered_df[filtered_df["STATUS"] == "Pending"]["VOLUME (CU. M)"].sum()

# Volume summary
st.subheader("📈 Volume Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("✅ % Completed", f"{round((completed_volume / total_volume) * 100, 1) if total_volume > 0 else 0}%")
col2.metric("📊 Total Volume", f"{total_volume:,.1f} cu.m")
col3.metric("✔ Completed Volume", f"{completed_volume:,.1f} cu.m")
col4.metric("⏳ Pending Volume", f"{pending_volume:,.1f} cu.m")
st.markdown("---")

# Display data info
st.subheader("📋 Data Preview")
st.dataframe(filtered_df,use_container_width=True, height=200)
st.markdown("---")

# Chart: Grouped bar chart with production date as category
st.subheader("📊 Production Forecast")
fig_grouped = px.bar(
    df,
    x="TARGET START OF PRODUCTION",
    y="VOLUME (CU. M)",
    color="TYPE",
    title="Element Types by Production Date",
    labels={
        "TARGET START OF PRODUCTION": "Production Start Date",
        "VOLUME (CU. M)": "Volume (cu. m)",
        "TYPE": "Element Type"
    },
    barmode="group",
    hover_data=["LEVEL", "ELEMENT"],
    template="plotly_white"
)

fig_grouped.update_layout(
    height=500,
    xaxis=dict(title="Production Start Date", tickformat="%d-%b-%Y"),
    yaxis=dict(title="Volume (cu. m)"),
    legend_title="Element Type",
    barmode="group",
    bargap=0.01,       # space between bars
    bargroupgap=0.01,   # space between groups
)

# Set y-axis range for better visualization
fig_grouped.update_yaxes(range=[0, 7])  

st.plotly_chart(fig_grouped, use_container_width=True)

# Area chart: Cumulative volume over time
st.subheader("📈 Cumulative Volume Over Time")
fig_area = px.area(
    filtered_df, 
    x="TARGET START OF PRODUCTION", 
    y="VOLUME (CU. M)",
    title="Forecasted Volume Over Time",
    labels={
        "TARGET START OF_PRODUCTION": "Production Date",
        "VOLUME (CU. M)": "Volume (cu. m)"
    },
    template="plotly_white"
)

# Format x-axis and y-axis
fig_area.update_layout(
    xaxis=dict(title="Production Start Date", tickformat="%d-%b-%Y"),
    yaxis=dict(title="Volume (cu. m)", tickformat=",", ticksuffix=" cu.m"),
    height=500
)

st.plotly_chart(fig_area, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with Streamlit 🎈 | Modify data.xlsx and reload to see changes</p>
</div>
""", unsafe_allow_html=True)