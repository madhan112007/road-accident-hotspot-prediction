import streamlit as st
import base64
from pathlib import Path


st.set_page_config(
    page_title="Road Accident Hotspot Predictor",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_css():
    """Load custom CSS from assets/styles/custom.css, or use fallback inline CSS."""
    try:
        with open("assets/styles/custom.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("""
        <style>
        .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        
        /* Feature Cards */
        .feature-card {
            background: white;
            padding: 30px 20px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            border-left: 5px solid #FF4B4B;
            margin: 10px;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }

        .feature-icon {
            font-size: 3.5rem;
            margin-bottom: 20px;
        }

        /* Buttons */
        .stButton button {
            border-radius: 10px !important;
            border: none !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            font-weight: bold !important;
            padding: 10px 20px !important;
            transition: all 0.3s ease !important;
        }

        .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4) !important;
        }
        </style>
        """, unsafe_allow_html=True)


def set_background(image_file):
    """Set a background image for the app."""
    image_path = Path(__file__).parent / "assets/images" / image_file
    if image_path.exists():
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background: url("data:image/png;base64,{encoded}") no-repeat center center fixed;
                background-size: cover;
            }}
            </style>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Background image '{image_file}' not found in assets/images/")


def create_hero_section():
    hero_html = """
    <div style="
        position: relative;
        background: linear-gradient(135deg, rgba(102,126,234,0.9) 0%, rgba(118,75,162,0.9) 100%);
        padding: 100px 0;
        text-align: center;
        color: white;
        border-radius: 20px;
        margin-bottom: 40px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    ">
        <h1 style="font-size: 4rem; margin-bottom: 20px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            🚦 Road Accident Hotspot Predictor
        </h1>
        <p style="font-size: 1.5rem; margin-bottom: 30px; opacity: 0.9;">
            Making Indian Roads Safer Through Data Intelligence
        </p>
        <div style="display: inline-block; background: #FF6B6B; padding: 15px 30px;
                    border-radius: 50px; font-weight: bold; font-size: 1.2rem;
                    box-shadow: 0 5px 15px rgba(255,107,107,0.4);">
             Focus Areas: Kovaipudur, Gandhipuram, Ukkadam, Kuniyamuthur
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)


def create_feature_cards():
    st.markdown("""
    <div style="margin: 50px 0;">
        <h2 style="text-align: center; color: #2c3e50; margin-bottom: 40px;"> Key Features</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    features = [
        ("📤 Upload Data", "Upload your accident data in CSV format with location details"),
        ("🔥 Hotspot Detection", "AI-powered clustering to identify high-risk accident zones"),
        ("🗺️ Interactive Maps", "Visualize accident hotspots on interactive maps"),
        ("📊 Data Insights", "Detailed analysis of accident patterns and trends")
    ]
    
    for col, (title, desc) in zip([col1, col2, col3, col4], features):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon"></div>
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)


def create_coimbatore_section():
    st.markdown("""
    <div style="background: white; padding: 40px; border-radius: 20px;
                margin: 30px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
        <h2> Special Focus: Coimbatore Areas</h2>
        <p style="text-align: center; margin-bottom: 30px; color: #666;">
        Our analysis specifically targets these key areas in Coimbatore</p>
    </div>
    """, unsafe_allow_html=True)
    
    areas = [
        ("🏘️ Kovaipudur", "Residential area with mixed traffic patterns", "#FF6B6B"),
        ("🏙️ Gandhipuram", "Commercial hub with high traffic density", "#4ECDC4"),
        ("🛣️ Ukkadam", "Major junction with complex traffic flow", "#45B7D1"),
        ("🏡 Kuniyamuthur", "Developing residential and commercial zone", "#F093FB")
    ]
    
    cols = st.columns(4)
    for idx, (area, desc, color) in enumerate(areas):
        with cols[idx]:
            st.markdown(f"""
            <div style="background: {color}; color: white; padding: 25px 20px;
                        border-radius: 15px; text-align: center;
                        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                        height: 140px; display: flex; flex-direction: column;
                        justify-content: center;">
                <h4 style="margin-bottom: 12px; font-size: 1.2rem;">{area}</h4>
                <p style="font-size: 0.85rem; opacity: 0.95; line-height: 1.3;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)


def main():
    load_css()
    set_background("hero-bg.jpg")  
    
    
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 25px 20px; border-radius: 15px; color: white;
                margin-bottom: 25px;">
        <h2>🚦 Navigation</h2>
        <p>Explore different sections of the application</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.info("""
    **Quick Start Guide:**
    1️⃣ Upload your accident data  
    2️⃣ Run hotspot detection  
    3️⃣ View on interactive maps  
    4️⃣ Analyze insights  
    """)
    
    
    create_hero_section()
    
    
    st.markdown("""
    <h2 style="color:#0078D7;">About This Project</h2>
    <p style="font-size:16px; line-height:1.6;">
        This innovative web application leverages <strong>Machine Learning</strong> and 
        <strong>Geospatial Analysis</strong> to predict and visualize 
        <strong>road accident hotspots</strong> across Coimbatore and other Indian cities. 
        By analyzing historical accident data, the system identifies locations with a higher 
        likelihood of accidents, helping authorities and citizens take proactive safety measures. 
        The platform provides interactive visualizations and insightful analytics that make 
        road safety planning more efficient and data-driven.
    </p>
    <div style="background: #e8f4fd; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h4 style="color:#005A9E;">Mission Statement</h4>
        <p style="font-size:15px; line-height:1.6;">
            To reduce road accidents by identifying high-risk zones and providing 
            <strong>actionable insights</strong> for better traffic management, 
            infrastructure planning, and public awareness initiatives.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    
    create_feature_cards()
    create_coimbatore_section()

    
    st.markdown("---")
    st.markdown("## Next Steps")
    st.markdown("After detecting hotspots, explore them on interactive maps or analyze detailed insights!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(" View Interactive Map", use_container_width=True):
            st.switch_page("pages/3_Interactive_Map.py")
    with col2:
        if st.button(" Analyze Insights", use_container_width=True):
            st.switch_page("pages/4_Insights_Analysis.py")

    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; padding: 20px; color: #666;">
        <hr>
        <p>🚦 Road Accident Hotspot Predictor | Made with ❤️ for Safer Indian Roads</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
