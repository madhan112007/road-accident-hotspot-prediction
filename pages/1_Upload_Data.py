import streamlit as st
import pandas as pd
import numpy as np
from utils.data_processor import DataProcessor
import plotly.express as px
import base64

st.set_page_config(page_title="Upload Data", page_icon="", layout="wide")

# Custom CSS
def load_css():
    with open("assets/styles/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Header
st.markdown("""
<div class="hero-section" style="padding: 60px 0; margin-bottom: 40px;">
    <h1 style="text-align: center; margin: 0;"> Upload Accident Data</h1>
    <p style="text-align: center; margin: 10px 0 0 0; font-size: 1.2rem;">Upload your CSV file containing road accident data for analysis</p>
</div>
""", unsafe_allow_html=True)

# Initialize data processor
processor = DataProcessor()

# File upload section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
        <h3>📁 Upload Your Data</h3>
        <p>Upload a CSV file with the following columns:</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type="csv",
        help="Upload your accident data CSV file"
    )

with col2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%); color: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.2);">
        <h4> Required Columns</h4>
        <ul style="font-size: 0.9rem; line-height: 1.6;">
            <li>Latitude</li>
            <li>Longitude</li>
            <li>Severity (1-4)</li>
            <li>Date_Time</li>
            <li>Weather</li>
            <li>Road_Type</li>
            <li>Vehicles_Involved</li>
            <li>Light_Condition</li>
            <li>Speed_Limit</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Sample data download
st.markdown("---")
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("""
    <div style="text-align: center;">
        <h4> Don't have data?</h4>
        <p>Download our sample dataset to get started</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample data download
    sample_df = pd.read_csv("sample_data/sample.csv")
    csv = sample_df.to_csv(index=False)
    st.download_button(
        label=" Download Sample Data",
        data=csv,
        file_name="sample_accident_data.csv",
        mime="text/csv",
        help="Download sample accident data for testing"
    )

with col2:
    st.markdown("""
    <div style="background: #e8f4fd; padding: 20px; border-radius: 10px;">
        <h4> Data Format Tips</h4>
        <ul style="font-size: 0.9rem;">
            <li><strong>Latitude/Longitude:</strong> Should be within India coordinates (Lat: 8-37°, Lon: 68-97°)</li>
            <li><strong>Severity:</strong> Scale of 1 (minor) to 4 (severe)</li>
            <li><strong>Date_Time:</strong> Format as YYYY-MM-DD HH:MM:SS</li>
            <li><strong>Weather:</strong> Clear, Rain, Fog, Snow, Cloudy, Windy</li>
            <li><strong>Road Type:</strong> Highway, City Road, Rural Road, Residential Street</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Data preview and processing
if uploaded_file is not None:
    try:
        # Load and process data
        df = processor.load_data(uploaded_file)
        df = processor.validate_coordinates(df)
        
        # Add area information
        df['Area'] = df.apply(lambda row: processor.get_area_name(row['Latitude'], row['Longitude']), axis=1)
        
        # Store in session state
        st.session_state['accident_data'] = df
        st.session_state['data_uploaded'] = True
        
        # Display success message
        st.success(f" Data uploaded successfully! Loaded {len(df)} records.")
        
        # Data overview
        st.markdown("---")
        st.markdown("##  Data Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            st.metric("Data Columns", len(df.columns))
        with col3:
            avg_severity = df['Severity'].mean()
            st.metric("Average Severity", f"{avg_severity:.2f}")
        with col4:
            coimbatore_records = len(df[df['Area'] != 'Other Area'])
            st.metric("Coimbatore Records", coimbatore_records)
        
        # Data preview
        st.markdown("###  Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Area distribution
        st.markdown("###  Area Distribution")
        area_counts = df['Area'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=area_counts.values,
                names=area_counts.index,
                title="Accidents by Area",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Severity distribution
            severity_counts = df['Severity'].value_counts().sort_index()
            fig = px.bar(
                x=severity_counts.index,
                y=severity_counts.values,
                title="Accidents by Severity Level",
                labels={'x': 'Severity Level', 'y': 'Number of Accidents'},
                color=severity_counts.values,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Time distribution
        st.markdown("###  Time Patterns")
        col1, col2 = st.columns(2)
        
        with col1:
            hour_counts = df['Hour'].value_counts().sort_index()
            fig = px.line(
                x=hour_counts.index,
                y=hour_counts.values,
                title="Accidents by Hour of Day",
                labels={'x': 'Hour of Day', 'y': 'Number of Accidents'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            day_counts = df['DayOfWeek'].value_counts()
            fig = px.bar(
                x=day_counts.values,
                y=day_counts.index,
                orientation='h',
                title="Accidents by Day of Week",
                labels={'x': 'Number of Accidents', 'y': 'Day of Week'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("Please check your file format and try again.")

else:
    # Show sample data preview
    st.markdown("---")
    st.markdown("## Sample Data Preview")
    sample_df = pd.read_csv("sample_data/sample.csv")
    st.dataframe(sample_df, use_container_width=True)
    
    st.info(" Upload your CSV file above or download the sample data to get started!")

# Navigation guide
st.markdown("---")
st.markdown("""
<div style="text-align: center; background: #f8f9fa; padding: 20px; border-radius: 10px;">
    <h4>Next Steps</h4>
    <p>After uploading your data, proceed to <strong>Hotspot Detection</strong> to identify accident-prone areas!</p>
    <div style="margin-top: 15px;">
        <a href="/Hotspot_Detection" target="_self" style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 10px 20px; 
            border-radius: 25px; 
            text-decoration: none; 
            font-weight: bold;
            margin: 5px;
            display: inline-block;
        ">Go to Hotspot Detection</a>
    </div>
</div>
""", unsafe_allow_html=True)