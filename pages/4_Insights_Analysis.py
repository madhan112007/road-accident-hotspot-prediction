import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.data_processor import DataProcessor

st.set_page_config(page_title="Insights Analysis", page_icon="", layout="wide")

# Custom CSS
def load_css():
    try:
        with open("assets/styles/custom.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("""
        <style>
        .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        </style>
        """, unsafe_allow_html=True)

load_css()

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 60px 0; text-align: center; color: white; border-radius: 20px; margin-bottom: 40px;">
    <h1 style="margin: 0;"> Insights & Analysis</h1>
    <p style="margin: 10px 0 0 0; font-size: 1.2rem;">Deep dive into accident patterns and risk factors</p>
</div>
""", unsafe_allow_html=True)

# Check if data is available
if 'accident_data' not in st.session_state:
    st.error(" Please upload your data first in the 'Upload Data' page!")
    st.markdown("""
    <div style="text-align: center; margin: 30px 0;">
        <a href="/Upload_Data" target="_self" style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 15px 30px; 
            border-radius: 25px; 
            text-decoration: none; 
            font-weight: bold;
            display: inline-block;
        "> Go to Upload Data</a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Load data
df = st.session_state['accident_data']
processor = DataProcessor()

# Overview metrics
st.markdown("##  Overview Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_accidents = len(df)
    st.metric("Total Accidents", total_accidents)

with col2:
    avg_severity = df['Severity'].mean()
    st.metric("Average Severity", f"{avg_severity:.2f}")

with col3:
    fatal_accidents = len(df[df['Severity'] == 4])
    st.metric("High Severity (4)", fatal_accidents)

with col4:
    avg_vehicles = df['Vehicles_Involved'].mean()
    st.metric("Avg Vehicles Involved", f"{avg_vehicles:.1f}")

# Time-based Analysis
st.markdown("##  Time-based Patterns")

col1, col2 = st.columns(2)

with col1:
    # Hourly distribution
    hourly = df['Hour'].value_counts().sort_index()
    fig = px.area(
        x=hourly.index,
        y=hourly.values,
        title="Accidents by Hour of Day",
        labels={'x': 'Hour of Day', 'y': 'Number of Accidents'}
    )
    fig.update_traces(fill='tozeroy', line=dict(color='#FF6B6B'))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Day of week distribution
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily = df['DayOfWeek'].value_counts().reindex(day_order, fill_value=0)
    fig = px.bar(
        x=daily.index,
        y=daily.values,
        title="Accidents by Day of Week",
        labels={'x': 'Day of Week', 'y': 'Number of Accidents'},
        color=daily.values,
        color_continuous_scale='viridis'
    )
    st.plotly_chart(fig, use_container_width=True)

# Weather and Road Conditions - FIXED VERSION
st.markdown("##  Weather & Road Conditions")

col1, col2 = st.columns(2)

with col1:
    # Weather impact - FIXED
    weather_counts = df['Weather'].value_counts()
    fig = px.bar(
        x=weather_counts.values,
        y=weather_counts.index,
        orientation='h',
        title="Accidents by Weather Condition",
        labels={'x': 'Number of Accidents', 'y': 'Weather Condition'},
        color=weather_counts.values,
        color_continuous_scale='blues'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Road type analysis - FIXED (no more color_continuous_scale error)
    road_counts = df['Road_Type'].value_counts()
    fig = px.pie(
        values=road_counts.values,
        names=road_counts.index,
        title="Accident Distribution by Road Type"
    )
    st.plotly_chart(fig, use_container_width=True)

# Severity Analysis
st.markdown("##  Severity Analysis")

col1, col2 = st.columns(2)

with col1:
    # Severity distribution
    severity_counts = df['Severity'].value_counts().sort_index()
    fig = px.bar(
        x=severity_counts.index,
        y=severity_counts.values,
        title="Accident Severity Distribution",
        labels={'x': 'Severity Level', 'y': 'Number of Accidents'},
        color=severity_counts.values,
        color_continuous_scale='reds'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Severity by factors
    factors = st.selectbox(
        "Analyze severity by:",
        ['Weather', 'Road_Type', 'Light_Condition', 'Speed_Limit']
    )
    
    severity_by_factor = df.groupby(factors)['Severity'].mean().sort_values(ascending=False)
    fig = px.bar(
        x=severity_by_factor.index,
        y=severity_by_factor.values,
        title=f"Average Severity by {factors}",
        labels={'x': factors, 'y': 'Average Severity'},
        color=severity_by_factor.values,
        color_continuous_scale='reds'
    )
    st.plotly_chart(fig, use_container_width=True)

# Correlation Analysis
st.markdown("##  Correlation Analysis")

# Create correlation matrix
numeric_cols = ['Severity', 'Vehicles_Involved', 'Speed_Limit', 'Hour']
if all(col in df.columns for col in numeric_cols):
    corr_matrix = df[numeric_cols].corr()
    
    fig = px.imshow(
        corr_matrix,
        title="Correlation Matrix of Numerical Features",
        color_continuous_scale='rdbu_r',
        aspect='auto'
    )
    st.plotly_chart(fig, use_container_width=True)

# Risk Factor Analysis
st.markdown("##  Risk Factor Analysis")

col1, col2 = st.columns(2)

with col1:
    # High severity accidents analysis
    high_severity = df[df['Severity'] >= 3]
    
    if not high_severity.empty:
        risk_factors = high_severity['Weather'].value_counts().head(5)
        fig = px.bar(
            x=risk_factors.values,
            y=risk_factors.index,
            orientation='h',
            title="Top Weather Conditions in High Severity Accidents",
            labels={'x': 'Number of Accidents', 'y': 'Weather Condition'},
            color=risk_factors.values,
            color_continuous_scale='reds'
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Speed limit vs severity
    if not high_severity.empty:
        speed_severity = df.groupby('Speed_Limit')['Severity'].mean()
        fig = px.scatter(
            x=speed_severity.index,
            y=speed_severity.values,
            title="Speed Limit vs Average Severity",
            labels={'x': 'Speed Limit (km/h)', 'y': 'Average Severity'},
            size=[10] * len(speed_severity),
            color=speed_severity.values,
            color_continuous_scale='reds'
        )
        st.plotly_chart(fig, use_container_width=True)

# Coimbatore Specific Analysis
st.markdown("##  Coimbatore Area Analysis")

# Add area information if not already present
if 'Area' not in df.columns:
    df['Area'] = df.apply(lambda row: processor.get_area_name(row['Latitude'], row['Longitude']), axis=1)

coimbatore_areas = ['Kovaipudur', 'Gandhipuram', 'Ukkadam', 'Kuniyamuthur']
coimbatore_data = df[df['Area'].isin(coimbatore_areas)]

if not coimbatore_data.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        area_counts = coimbatore_data['Area'].value_counts()
        fig = px.bar(
            x=area_counts.values,
            y=area_counts.index,
            orientation='h',
            title="Accidents in Coimbatore Areas",
            labels={'x': 'Number of Accidents', 'y': 'Area'},
            color=area_counts.values,
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        area_severity = coimbatore_data.groupby('Area')['Severity'].mean().sort_values(ascending=False)
        fig = px.bar(
            x=area_severity.index,
            y=area_severity.values,
            title="Average Severity by Coimbatore Area",
            labels={'x': 'Area', 'y': 'Average Severity'},
            color=area_severity.values,
            color_continuous_scale='reds'
        )
        st.plotly_chart(fig, use_container_width=True)

# Export Insights
st.markdown("---")
st.markdown("##  Export Analysis")

col1, col2 = st.columns(2)

with col1:
    # Download summary report
    summary_report = f"""
    Road Accident Analysis Summary Report
    ====================================
    
    Total Accidents: {len(df)}
    Average Severity: {df['Severity'].mean():.2f}
    High Severity Accidents (4): {len(df[df['Severity'] == 4])}
    
    Time Patterns:
    - Peak Hour: {df['Hour'].value_counts().idxmax()}:00
    - Most Common Day: {df['DayOfWeek'].value_counts().idxmax()}
    
    Risk Factors:
    - Most Dangerous Weather: {df.groupby('Weather')['Severity'].mean().idxmax()}
    - Most Dangerous Road Type: {df.groupby('Road_Type')['Severity'].mean().idxmax()}
    """
    
    st.download_button(
        label=" Download Summary Report",
        data=summary_report,
        file_name="accident_analysis_report.txt",
        mime="text/plain"
    )

with col2:
    # Download detailed data
    analysis_data = df.copy()
    if 'clusters' in st.session_state:
        analysis_data['Cluster'] = st.session_state['clusters']
    
    csv = analysis_data.to_csv(index=False)
    st.download_button(
        label=" Download Analysis Data",
        data=csv,
        file_name="detailed_analysis_data.csv",
        mime="text/csv"
    )

# Recommendations
st.markdown("---")
st.markdown("##  Safety Recommendations")

recommendations = {
    " Time-based": [
        "Increase patrols during peak accident hours",
        "Install better lighting in high-accident night zones",
        "Implement variable speed limits based on time of day"
    ],
    " Weather-based": [
        "Improve drainage systems in rainy areas",
        "Install weather-adaptive traffic signals",
        "Enhance road markings for low-visibility conditions"
    ],
    " Infrastructure": [
        "Install speed cameras in high-risk zones",
        "Improve road maintenance in problematic areas",
        "Add traffic calming measures in residential zones"
    ],
    " Coimbatore-specific": [
        "Focus on Gandhipuram traffic management during peak hours",
        "Improve Ukkadam junction signaling",
        "Enhance Kovaipudur residential area safety measures"
    ]
}

for category, items in recommendations.items():
    with st.expander(f"{category} Recommendations"):
        for item in items:
            st.write(f"• {item}")

st.markdown("""
<div style="text-align: center; margin-top: 40px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px;">
    <h3>🚦 Drive Safe, Save Lives!</h3>
    <p>Use these insights to make data-driven decisions for road safety improvements</p>
</div>
""", unsafe_allow_html=True)