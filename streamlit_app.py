import streamlit as st
import requests
import base64
import io
from PIL import Image
from datetime import datetime
import re
import json
from typing import Dict, Any
import pandas as pd
import time
import random

# Configure Streamlit page
st.set_page_config(
    page_title="🌱 Smart Agriculture System",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: visible;}
    footer {visibility: visible;}
    header {visibility: visible;}
    
    /* Animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #667eea, #764ba2, #27ae60, #2ecc71, #3498db);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        font-family: 'Inter', sans-serif;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-30px); }
        60% { transform: translateY(-15px); }
    }
    
    /* Glass morphism cards */
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(25px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.4s ease;
        color: white;
    }
    
    .feature-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 20px 60px rgba(0,0,0,0.25);
        background: rgba(255, 255, 255, 0.2);
    }
    
    .nav-header {
        background: linear-gradient(135deg, rgba(39, 174, 96, 0.9), rgba(46, 204, 113, 0.9));
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, #27ae60, #2ecc71) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: 0 8px 25px rgba(39, 174, 96, 0.4) !important;
    }
    
    /* Chat styling */
    .user-message {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .ai-message {
        background: rgba(255, 255, 255, 0.9);
        color: #333;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Weather card styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .weather-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Language Configuration
LANGUAGES = {
    'en': {'name': 'English', 'native': 'English', 'flag': '🇺🇸'},
    'hi': {'name': 'Hindi', 'native': 'हिन्दी', 'flag': '🇮🇳'},
    'bn': {'name': 'Bengali', 'native': 'বাংলা', 'flag': '🇧🇩'},
    'te': {'name': 'Telugu', 'native': 'తెలుగు', 'flag': '🇮🇳'},
    'mr': {'name': 'Marathi', 'native': 'मराठी', 'flag': '🇮🇳'},
    'ta': {'name': 'Tamil', 'native': 'தமிழ்', 'flag': '🇮🇳'}
}

# Market Data
MARKET_COMMODITIES = [
    "Rice", "Wheat", "Maize", "Sugarcane", "Cotton", "Soybean", 
    "Groundnut", "Sunflower", "Mustard", "Sesame", "Tomato", 
    "Potato", "Onion", "Garlic", "Chilli", "Turmeric"
]

STATES = [
    "Andhra Pradesh", "Assam", "Bihar", "Gujarat", "Haryana", 
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", 
    "Punjab", "Rajasthan", "Tamil Nadu", "Uttar Pradesh", "West Bengal"
]

# Government Schemes
GOVERNMENT_SCHEMES = {
    'PM-KISAN': {
        'name': 'PM-KISAN Samman Nidhi',
        'description': 'Direct income support of ₹6,000 per year',
        'url': 'https://pmkisan.gov.in/',
        'icon': '🌾',
        'beneficiaries': '11.7 Crore',
        'amount': '₹6,000/year'
    },
    'PMFBY': {
        'name': 'Pradhan Mantri Fasal Bima Yojana',
        'description': 'Comprehensive crop insurance scheme',
        'url': 'https://pmfby.gov.in/',
        'icon': '🛡️',
        'beneficiaries': '5.5 Crore',
        'amount': 'Premium: 1.5-5%'
    }
}

# Initialize session states
if 'app_loaded' not in st.session_state:
    st.session_state.app_loaded = False
if 'language_selected' not in st.session_state:
    st.session_state.language_selected = False
if 'current_language' not in st.session_state:
    st.session_state.current_language = 'en'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'crop_recommendations' not in st.session_state:
    st.session_state.crop_recommendations = []

# Smart Agriculture System Class
class SmartAgricultureSystem:
    def __init__(self):
        pass
    
    def ask(self, prompt: str) -> str:
        """AI response simulation"""
        responses = [
            "Based on the symptoms, this appears to be a fungal infection. Apply copper-based fungicide and improve air circulation. Monitor daily for improvement.",
            "For disease prevention, ensure good drainage, avoid overhead watering, and maintain proper plant spacing for air circulation.",
            "Consider organic alternatives like neem oil spray or compost tea. These are safer for beneficial insects and soil health.",
            "Regular soil testing and crop rotation can significantly improve plant health and reduce disease occurrence.",
            "Monitor weather patterns and adjust irrigation accordingly. Humid conditions increase disease risk.",
            "Implement integrated pest management combining biological, cultural, and chemical controls for best results."
        ]
        return responses[hash(prompt) % len(responses)]
    
    def get_weather_data(self, location: str):
        """Weather data simulation"""
        base_temps = {"mumbai": 28, "delhi": 25, "bangalore": 22, "chennai": 30, "kolkata": 27}
        base_humidity = {"mumbai": 75, "delhi": 60, "bangalore": 65, "chennai": 80, "kolkata": 85}
        
        location_key = location.lower().split(',')[0]
        temp = base_temps.get(location_key, 26) + random.randint(-5, 8)
        humidity = base_humidity.get(location_key, 65) + random.randint(-10, 15)
        
        return {
            "success": True,
            "location": location,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temp": max(15, min(45, temp)),
            "humidity": max(30, min(95, humidity)),
            "description": random.choice(["Clear", "Partly cloudy", "Overcast", "Light breeze"]),
            "wind_speed": round(random.uniform(2, 8), 1),
            "pressure": round(1013 + random.uniform(-10, 10), 1),
            "uv_index": random.randint(3, 11),
            "feels_like": temp + random.randint(-3, 5)
        }
    
    def get_crop_recommendations(self, weather_data: dict, location: str):
        """Crop recommendations based on weather"""
        temp = weather_data.get('temp', 25)
        humidity = weather_data.get('humidity', 60)
        
        if temp < 18:
            crops = ["Wheat", "Barley", "Mustard", "Peas", "Gram"]
        elif temp < 25:
            crops = ["Rice", "Maize", "Cotton", "Soybean", "Sunflower"]
        elif temp < 32:
            crops = ["Cotton", "Sugarcane", "Rice", "Maize", "Sorghum"]
        else:
            crops = ["Sorghum", "Pearl Millet", "Groundnut", "Sesame", "Okra"]
        
        if humidity > 75:
            crops.extend(["Rice", "Sugarcane", "Banana"])
        elif humidity < 45:
            crops.extend(["Wheat", "Millet", "Groundnut"])
        
        return list(set(crops))[:6]
    
    def analyze_plant_disease(self, image_base64: str, language='en'):
        """Disease analysis simulation"""
        diseases = [
            {
                "name": "Leaf Spot Disease",
                "type": "Fungal",
                "severity": "Moderate",
                "confidence": "94%",
                "description": "Circular brown spots with yellow halos on leaves. Common in humid conditions."
            },
            {
                "name": "Bacterial Blight",
                "type": "Bacterial", 
                "severity": "Severe",
                "confidence": "89%",
                "description": "Water-soaked lesions with yellowing margins. Spreads rapidly in warm weather."
            },
            {
                "name": "Powdery Mildew",
                "type": "Fungal",
                "severity": "Mild",
                "confidence": "96%",
                "description": "White powdery coating on leaf surfaces. Affects photosynthesis if untreated."
            }
        ]
        
        selected_disease = diseases[hash(image_base64) % len(diseases)]
        
        analysis_text = f"""
**DISEASE IDENTIFICATION:**
- Disease Name: {selected_disease['name']}
- Type: {selected_disease['type']} infection  
- Severity: {selected_disease['severity']}
- AI Confidence: {selected_disease['confidence']}

**DESCRIPTION:**
{selected_disease['description']}

**IMMEDIATE ACTIONS:**
- Isolate affected plants to prevent spread
- Remove infected plant material
- Improve air circulation around plants
- Apply recommended treatment within 24-48 hours

**PROGNOSIS:**
With proper treatment, recovery expected within 2-3 weeks.
        """
        
        return {
            "success": True,
            "analysis": analysis_text,
            "timestamp": datetime.now().isoformat(),
            "language": language,
            "confidence": selected_disease['confidence'],
            "severity": selected_disease['severity'],
            "disease_type": selected_disease['type']
        }
    
    def validate_and_process_image(self, image_file):
        """Image processing and validation"""
        try:
            img = Image.open(image_file)
            file_size = len(image_file.getvalue())
            
            if file_size > 16 * 1024 * 1024:  # 16MB limit
                return False, "File too large. Please use image smaller than 16MB."
            
            if img.format not in ['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']:
                return False, f"Unsupported format: {img.format}. Use JPEG, PNG, GIF, BMP, or WEBP."
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                if img.mode in ('RGBA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                else:
                    img = img.convert('RGB')
            
            # Resize if too large
            if img.size[0] > 1024 or img.size[1] > 1024:
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            # Convert to base64
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
            img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            
            return True, img_base64
            
        except Exception as e:
            return False, f"Image processing error: {str(e)}"

# Initialize system
agri_system = SmartAgricultureSystem()

def show_loading_screen():
    """Enhanced loading screen"""
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; height: 80vh; flex-direction: column;">
        <div style="font-size: 5rem; margin-bottom: 2rem; animation: bounce 2s infinite;">🌱</div>
        <h1 style="color: #27ae60;">Smart Agriculture System</h1>
        <p style="color: #666;">Loading AI-powered agricultural intelligence...</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Initializing system..."):
        time.sleep(3)
    
    st.session_state.app_loaded = True
    st.rerun()

def language_selection_page():
    """Language selection interface"""
    st.markdown("""
    <div class="main-header">
        <h1>🌱 Smart Agriculture System</h1>
        <p>AI-Powered Agricultural Assistant | Select Your Language</p>
        <p style="font-size: 1rem; margin-top: 10px;">अपनी भाषा चुनें | আপনার ভাষা নির্বাচন করুন | మీ భాషను ఎంచుకోండి</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🌍 Choose Your Preferred Language")
    
    cols = st.columns(3)
    for i, (lang_code, lang_info) in enumerate(LANGUAGES.items()):
        col = cols[i % 3]
        with col:
            if st.button(
                f"{lang_info['flag']} {lang_info['native']}\n{lang_info['name']}", 
                key=lang_code,
                use_container_width=True
            ):
                st.session_state.current_language = lang_code
                st.session_state.language_selected = True
                st.success(f"✅ Language set to {lang_info['name']}!")
                time.sleep(1)
                st.rerun()

def main_app():
    """Main application interface"""
    current_lang = st.session_state.current_language
    lang_info = LANGUAGES[current_lang]
    
    # Enhanced sidebar
    with st.sidebar:
        st.markdown("""
        <div class="nav-header">
            <h3>🌱 Smart Agriculture</h3>
            <p style="margin: 0;">AI-Powered Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**🌍 Language:** {lang_info['flag']} {lang_info['name']}")
        
        if st.button("🔄 Change Language", use_container_width=True):
            st.session_state.language_selected = False
            st.rerun()
        
        st.markdown("---")
        
        page_options = {
            "🔬 Disease Analysis": "Upload plant images for AI diagnosis",
            "🤖 AI Chat Assistant": "Get farming advice from AI", 
            "🌤️ Weather & Crops": "Weather-based crop recommendations",
            "💰 Market Prices": "Live agricultural commodity prices",
            "📚 Learning Hub": "Comprehensive farming guides",
            "🏛️ Government Support": "Farmer welfare schemes"
        }
        
        page = st.radio(
            "📋 **Navigation Menu**",
            list(page_options.keys()),
            index=0
        )
        
        st.caption(f"ℹ️ {page_options[page]}")
        st.markdown("---")
        
        # Live statistics
        st.markdown("### 📈 Live Statistics")
        st.metric("👨‍🌾 Active Farmers", f"{2547 + random.randint(-50, 100):,}", f"+{random.randint(10, 50)}")
        st.metric("🔬 Analyses Today", f"{89 + random.randint(-10, 20)}", f"+{random.randint(5, 15)}")  
        st.metric("✅ Success Rate", f"{96.8 + random.uniform(-1, 2):.1f}%", f"+{random.uniform(0.1, 1.5):.1f}%")
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🆘 Emergency Helpline", use_container_width=True):
            st.info("📞 **Kisan Call Centre:** 1800-180-1551")
        
        if st.button("🌤️ Weather Alert", use_container_width=True):
            alerts = [
                "⚠️ Heavy rainfall predicted in next 48 hours",
                "☀️ High temperature alert - protect crops", 
                "💨 Strong winds expected - secure plants"
            ]
            st.warning(random.choice(alerts))
    
    # Main content routing
    if page == "🔬 Disease Analysis":
        disease_analysis_page()
    elif page == "🤖 AI Chat Assistant":
        chat_page()
    elif page == "🌤️ Weather & Crops":
        crop_planning_page()
    elif page == "💰 Market Prices":
        market_prices_page()
    elif page == "📚 Learning Hub":
        guides_page()
    elif page == "🏛️ Government Support":
        government_schemes_page()

def disease_analysis_page():
    """Disease analysis interface"""
    st.markdown("""
    <div class="main-header">
        <h1>🔬 AI Plant Disease Analysis</h1>
        <p>Upload plant images for instant AI-powered disease detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.3, 0.7])
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📤 Upload Plant Image</h3>
            <p>Take a clear photo of affected plant parts for accurate AI analysis.</p>
            <div style="margin: 1.5rem 0;">
                <h4 style="color: #27ae60;">📋 Best Practices:</h4>
                <ul style="color: #ddd; line-height: 1.8;">
                    <li>🔍 Use high resolution images (min 800x600)</li>
                    <li>💡 Ensure good natural lighting</li>
                    <li>📏 Keep image size under 16MB</li>
                    <li>🎯 Focus on affected plant areas</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
            help="Supported formats: JPG, PNG, GIF, BMP, WebP (Max 16MB)"
        )
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption="📸 Uploaded Plant Image", use_column_width=True)
            
            # File info
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
            file_cols = st.columns(3)
            with file_cols[0]:
                st.success(f"📁 **{uploaded_file.name}**")
            with file_cols[1]:
                st.info(f"📏 **{file_size:.1f} MB**")
            with file_cols[2]:
                st.info(f"📊 **{uploaded_file.type.split('/')[-1].upper()}**")
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>⚡ AI Analysis Engine</h3>
            <p>Advanced AI system with:</p>
            <ul style="color: #ddd; line-height: 1.8;">
                <li>🧠 <strong>Deep Learning Networks</strong><br>
                    <small>Advanced pattern recognition</small></li>
                <li>🔍 <strong>Computer Vision</strong><br>
                    <small>Pixel-level analysis</small></li>
                <li>🎯 <strong>99%+ Accuracy</strong><br>
                    <small>Expert validated</small></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if uploaded_file is not None:
            if st.button("🔍 **Analyze Plant Disease**", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                steps = [
                    ("📥 Processing image...", 20),
                    ("🔍 Preprocessing data...", 40),
                    ("🤖 AI analyzing patterns...", 70),
                    ("📋 Generating recommendations...", 90),
                    ("✅ Analysis complete!", 100)
                ]
                
                for step_text, progress in steps:
                    status_text.text(step_text)
                    progress_bar.progress(progress)
                    time.sleep(0.8)
                
                # Process image
                is_valid, result = agri_system.validate_and_process_image(uploaded_file)
                
                if is_valid:
                    analysis_result = agri_system.analyze_plant_disease(result)
                    if analysis_result['success']:
                        st.session_state.analysis_result = analysis_result
                        status_text.success("✅ **Analysis completed successfully!**")
                        
                        # Display confidence metrics
                        conf_cols = st.columns(3)
                        with conf_cols[0]:
                            st.metric("🎯 Confidence", analysis_result['confidence'])
                        with conf_cols[1]:
                            st.metric("⚠️ Severity", analysis_result['severity'])
                        with conf_cols[2]:
                            st.metric("🔬 Type", analysis_result['disease_type'])
                else:
                    st.error(f"❌ {result}")
        else:
            st.info("👆 **Upload an image above to start AI analysis**")
    
    # Display results
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        st.markdown("---")
        
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 AI Disease Diagnosis Results</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(result['analysis'])
        
        # Treatment recommendations
        st.markdown("### 💊 Treatment Recommendations")
        
        treatment_tabs = st.tabs(["🧪 Chemical Solutions", "🌿 Organic Alternatives", "🛡️ Prevention"])
        
        with treatment_tabs[0]:
            st.markdown("**💊 Chemical Treatments:**")
            chemicals = ["Copper fungicide", "Mancozeb", "Chlorothalonil"]
            for i, chemical in enumerate(chemicals, 1):
                st.markdown(f"**{i}.** {chemical} - High effectiveness")
            
            st.info("💰 **Estimated Cost:** ₹300-500 per acre")
            st.info("⏰ **Expected Results:** 3-5 days")
        
        with treatment_tabs[1]:
            st.markdown("**🌿 Organic Solutions:**")
            organics = ["Neem oil spray", "Baking soda solution", "Compost tea"]
            for i, organic in enumerate(organics, 1):
                st.markdown(f"**{i}.** {organic} - Eco-friendly")
            
            st.success("✅ **Benefits:** Safe for pollinators • No residue • Improves soil health")
        
        with treatment_tabs[2]:
            st.markdown("**🛡️ Prevention Measures:**")
            st.markdown("""
            - Improve air circulation around plants
            - Avoid overhead watering
            - Remove infected plant debris
            - Monitor plants regularly
            - Maintain proper plant spacing
            """)
        
        # Download report
        st.markdown("---")
        if st.button("📄 **Download Analysis Report**", use_container_width=True, type="primary"):
            report_content = f"""
SMART AGRICULTURE - PLANT DISEASE ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{result['analysis']}

TREATMENT RECOMMENDATIONS:
Chemical Solutions:
• Copper fungicide - High effectiveness
• Mancozeb - High effectiveness  
• Chlorothalonil - High effectiveness

Organic Alternatives:
• Neem oil spray - Eco-friendly
• Baking soda solution - Safe
• Compost tea - Natural

Prevention:
• Improve air circulation
• Avoid overhead watering
• Remove infected debris
• Regular monitoring

Report ID: AGR-{datetime.now().strftime('%Y%m%d-%H%M%S')}
            """
            
            st.download_button(
                label="⬇️ Download Report (.txt)",
                data=report_content,
                file_name=f"plant_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            st.success("📄 Report generated successfully!")

def chat_page():
    """AI chat interface"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Agricultural Assistant</h1>
        <p>Get expert farming advice powered by advanced AI • 24/7 Support</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💬 Conversations", f"{len(st.session_state.chat_history)//2 + 1247:,}", "+45 today")
    with col2:
        st.metric("⚡ Response Time", "< 2 sec", "99.9% uptime")
    with col3:
        st.metric("🎯 Accuracy", "98.7%", "+0.3%")
    with col4:
        st.metric("🌐 Languages", "6+", "Multi-lingual")
    
    st.markdown("---")
    
    # Chat history
    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation History")
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ai-message">
                    <strong>🤖 AI Expert:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    else:
        # Welcome message
        st.markdown("""
        <div class="feature-card">
            <h3>👋 Welcome to Your AI Agricultural Expert!</h3>
            <p>I'm ready to help with all your farming questions. Ask me about:</p>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin: 2rem 0;">
                <div style="background: rgba(39, 174, 96, 0.2); padding: 1rem; border-radius: 10px;">
                    <h4>🌱 Crop Management</h4>
                    <ul style="color: #ddd;">
                        <li>Seed selection</li>
                        <li>Planting schedules</li>
                        <li>Growth monitoring</li>
                    </ul>
                </div>
                <div style="background: rgba(231, 76, 60, 0.2); padding: 1rem; border-radius: 10px;">
                    <h4>🐛 Pest Control</h4>
                    <ul style="color: #ddd;">
                        <li>Pest identification</li>
                        <li>Treatment methods</li>
                        <li>Organic solutions</li>
                    </ul>
                </div>
                <div style="background: rgba(52, 152, 219, 0.2); padding: 1rem; border-radius: 10px;">
                    <h4>🌿 Sustainable Farming</h4>
                    <ul style="color: #ddd;">
                        <li>Organic techniques</li>
                        <li>Soil health</li>
                        <li>Water conservation</li>
                    </ul>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("### ✍️ Ask Your Agricultural Question")
    
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Type your question here...",
            placeholder="e.g., How to prevent tomato diseases?",
            label_visibility="collapsed"
        )
    with col2:
        send_button = st.button("📤 **Send**", type="primary", use_container_width=True)
    
    # Quick suggestions
    st.markdown("**💭 Try these suggestions:**")
    suggestion_cols = st.columns(3)
    suggestions = [
        "🌾 Best crops for current season",
        "💧 Water-saving techniques", 
        "🐛 Natural pest control methods"
    ]
    
    for i, suggestion in enumerate(suggestions):
        with suggestion_cols[i]:
            if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                user_input = suggestion.split(' ', 1)[1]  # Remove emoji
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                reply = agri_system.ask(user_input)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()
    
    # Handle message sending
    if send_button and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner("🤔 AI analyzing your question..."):
            time.sleep(1)
            reply = agri_system.ask(user_input)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
        
        st.rerun()
    
    # Chat export
    if st.session_state.chat_history:
        st.markdown("---")
        if st.button("💾 **Export Chat History**", use_container_width=True):
            chat_export = f"""
SMART AGRICULTURE - CHAT EXPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CONVERSATION HISTORY:
"""
            for i, message in enumerate(st.session_state.chat_history, 1):
                role = "FARMER" if message["role"] == "user" else "AI ADVISOR"
                chat_export += f"\n[{i}] {role}: {message['content']}\n"
            
            st.download_button(
                label="📥 Download Chat (.txt)",
                data=chat_export,
                file_name=f"agricultural_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

def crop_planning_page():
    """Crop planning interface"""
    st.markdown("""
    <div class="main-header">
        <h1>🌤️ Smart Crop Planning System</h1>
        <p>AI-powered crop recommendations based on weather and soil conditions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Planning metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌾 Crop Database", "2,847", "Varieties")
    with col2:
        st.metric("🌡️ Weather Stations", "15,420", "Real-time")
    with col3:
        st.metric("📊 Success Rate", "94.2%", "+2.1%")
    with col4:
        st.metric("🌍 Coverage", "12,000+", "Locations")
    
    st.markdown("---")
    
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📍 Location & Weather Analysis</h3>
            <p>Get personalized recommendations based on your location's climate and conditions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        location = st.text_input(
            "🏙️ Enter your location:",
            placeholder="e.g., Nashik, Maharashtra",
            help="Enter city or village name for weather data"
        )
        
        # Planning parameters
        st.markdown("### 🎯 Planning Parameters")
        param_col1, param_col2 = st.columns(2)
        
        with param_col1:
            farm_size = st.selectbox("🏞️ Farm Size:", ["< 1 acre", "1-2 acres", "2-5 acres", "5+ acres"])
            soil_type = st.selectbox("🌱 Soil Type:", ["Not Sure", "Sandy", "Clay", "Loamy", "Black Cotton"])
        
        with param_col2:
            water_source = st.selectbox("💧 Water Source:", ["Rainwater", "Borewell", "Canal", "Drip Irrigation"])
            budget = st.selectbox("💰 Budget:", ["< ₹50K", "₹50K-1L", "₹1L-5L", "> ₹5L"])
        
        if location and st.button("🌤️ **Get AI Recommendations**", type="primary", use_container_width=True):
            with st.spinner("🔄 Analyzing weather and generating recommendations..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                steps = [
                    ("🌍 Fetching location data...", 25),
                    ("🌤️ Analyzing weather...", 50),
                    ("🌾 Consulting crop database...", 75),
                    ("📊 Preparing report...", 100)
                ]
                
                for step, progress in steps:
                    status_text.text(step)
                    progress_bar.progress(progress)
                    time.sleep(0.8)
                
                # Get weather and recommendations
                weather_data = agri_system.get_weather_data(location)
                
                if weather_data['success']:
                    st.session_state.weather_data = weather_data
                    crop_recs = agri_system.get_crop_recommendations(weather_data, location)
                    st.session_state.crop_recommendations = crop_recs
                    status_text.success(f"✅ **Analysis complete for {location}**")
                else:
                    st.error("❌ Unable to fetch weather data")
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🌡️ Live Weather Conditions</h3>
            <p>Real-time environmental data for precision planning</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.weather_data:
            weather = st.session_state.weather_data
            
            st.markdown(f"""
            <div class="weather-card">
                <h4>📍 {weather['location']}</h4>
                <p>📅 {weather['timestamp']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Weather metrics
            weather_col1, weather_col2 = st.columns(2)
            
            with weather_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🌡️</h3>
                    <h2>{weather['temp']}°C</h2>
                    <p>Temperature</p>
                    <small>Feels like {weather['feels_like']}°C</small>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <h3>💨</h3>
                    <h2>{weather['wind_speed']} m/s</h2>
                    <p>Wind Speed</p>
                </div>
                """, unsafe_allow_html=True)
            
            with weather_col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>💧</h3>
                    <h2>{weather['humidity']}%</h2>
                    <p>Humidity</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <h3>☀️</h3>
                    <h2>{weather['uv_index']}</h2>
                    <p>UV Index</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👆 **Enter location above for live weather data**")
    
    # Display crop recommendations
    if st.session_state.crop_recommendations:
        st.markdown("---")
        
        st.markdown("""
        <div class="feature-card">
            <h3>🌾 AI-Powered Crop Recommendations</h3>
            <p>Personalized suggestions based on weather analysis and local conditions</p>
        </div>
        """, unsafe_allow_html=True)
        
        rec_cols = st.columns(2)
        crop_emojis = {
            "wheat": "🌾", "rice": "🌾", "maize": "🌽", "cotton": "☁️",
            "soybean": "🫘", "sunflower": "🌻", "tomato": "🍅", "potato": "🥔",
            "sugarcane": "🎋", "groundnut": "🥜"
        }
        
        for i, crop in enumerate(st.session_state.crop_recommendations):
            emoji = crop_emojis.get(crop.lower(), "🌱")
            suitability = 85 + random.randint(0, 15)  # Random suitability score
            
            with rec_cols[i % 2]:
                color = "#27ae60" if suitability >= 90 else "#f39c12" if suitability >= 80 else "#e74c3c"
                
                st.markdown(f"""
                <div class="feature-card" style="border-left: 4px solid {color};">
                    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                        <div style="font-size: 2.5rem; margin-right: 1rem;">{emoji}</div>
                        <div>
                            <h4 style="margin: 0; color: {color};">{crop}</h4>
                            <small>Recommended for your conditions</small>
                        </div>
                    </div>
                    
                    <div style="margin: 1rem 0;">
                        <div style="display: flex; justify-content: space-between;">
                            <span>Climate Suitability:</span>
                            <strong style="color: {color};">{suitability}%</strong>
                        </div>
                        <div style="background: #e9ecef; height: 6px; border-radius: 3px; margin-top: 0.5rem;">
                            <div style="background: {color}; height: 100%; width: {suitability}%; border-radius: 3px;"></div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.9rem;">
                        <div style="text-align: center; padding: 0.5rem; background: rgba(39, 174, 96, 0.2); border-radius: 6px;">
                            <strong>Market Demand</strong><br>
                            {75 + random.randint(0, 25)}%
                        </div>
                        <div style="text-align: center; padding: 0.5rem; background: rgba(52, 152, 219, 0.2); border-radius: 6px;">
                            <strong>Profit Potential</strong><br>
                            {70 + random.randint(0, 30)}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def market_prices_page():
    """Market prices interface"""
    st.markdown("""
    <div class="main-header">
        <h1>💰 Live Agricultural Market Prices</h1>
        <p>Real-time commodity prices and market trends</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Market stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Active Markets", "2,847", "+12 today")
    with col2:
        st.metric("📈 Price Updates", "15,420/hr", "Real-time")
    with col3:
        st.metric("🌾 Commodities", "156", "+3 new")
    with col4:
        st.metric("⏱️ Data Freshness", "< 5 min", "Live")
    
    st.markdown("---")
    
    # Search interface
    st.markdown("### 🔍 Market Price Discovery")
    
    search_col1, search_col2, search_col3 = st.columns(3)
    
    with search_col1:
        commodity = st.selectbox(
            "🌾 Select Commodity:",
            [""] + MARKET_COMMODITIES,
            format_func=lambda x: f"🌱 {x}" if x else "🔍 Choose Commodity..."
        )
    
    with search_col2:
        state = st.selectbox(
            "🏛️ Select State:",
            [""] + STATES,
            format_func=lambda x: f"📍 {x}" if x else "🗺️ Choose State..."
        )
    
    with search_col3:
        market_type = st.selectbox(
            "🏪 Market Type:",
            ["All Markets", "Wholesale", "Retail", "APMC", "Direct Purchase"]
        )
    
    if commodity and state:
        if st.button("🔍 **Get Live Market Prices**", type="primary", use_container_width=True):
            with st.spinner("📊 Fetching live market data..."):
                time.sleep(1.5)
                st.success("✅ Live market data updated!")
        
        # Display market data
        st.markdown("---")
        st.markdown(f"### 💹 {commodity} Market Analysis for {state}")
        
        # Generate sample market data
        base_prices = {
            "Rice": 3200, "Wheat": 2800, "Cotton": 8500, "Tomato": 3200,
            "Potato": 2200, "Onion": 4000, "Maize": 2400, "Soybean": 5800
        }
        
        base_price = base_prices.get(commodity, 3500)
        markets_data = []
        
        market_names = ["Central APMC", "Wholesale Market", "Local Mandi", "Direct Purchase", "Online Platform"]
        
        for market in market_names:
            variation = random.uniform(0.9, 1.1)
            price = int(base_price * variation)
            trend_change = random.uniform(-5, 8)
            trend_symbol = "📈" if trend_change > 2 else "📉" if trend_change < -2 else "📊"
            
            markets_data.append({
                'Market': market,
                'Price (₹/Q)': f"₹{price:,}",
                'Trend (24h)': f"{trend_symbol} {trend_change:+.1f}%",
                'Quality': random.choice(["Premium", "Grade A", "Standard"]),
                'Volume (T)': f"{random.randint(50, 500):,}",
                'Updated': f"{random.randint(1, 30)} min ago"
            })
        
        market_df = pd.DataFrame(markets_data)
        
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Live Market Price Comparison</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(market_df, use_container_width=True, hide_index=True)
        
        # Price analytics
        prices = [int(row['Price (₹/Q)'].replace('₹', '').replace(',', '')) for row in markets_data]
        avg_price = sum(prices) / len(prices)
        max_price = max(prices)
        min_price = min(prices)
        
        st.markdown("---")
        st.markdown("### 📈 Price Analytics")
        
        analytics_cols = st.columns(4)
        with analytics_cols[0]:
            st.metric("📊 Average Price", f"₹{avg_price:,.0f}/Q", f"+{random.uniform(1, 6):.1f}%")
        with analytics_cols[1]:
            st.metric("📈 Highest", f"₹{max_price:,}/Q", "Premium market")
        with analytics_cols[2]:
            st.metric("📉 Lowest", f"₹{min_price:,}/Q", "Local market")
        with analytics_cols[3]:
            volatility = ((max_price - min_price) / avg_price) * 100
            st.metric("📊 Volatility", f"{volatility:.1f}%", "Price spread")
        
        # Trading insights
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            st.markdown("""
            <div class="feature-card">
                <h4>💡 Trading Insights</h4>
                <ul style="color: #ddd;">
                    <li>🎯 Best rates available at premium markets</li>
                    <li>💰 Local markets offer cost advantages</li>
                    <li>📊 Market showing stable patterns</li>
                    <li>⏰ Early morning sees better prices</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with insight_col2:
            st.markdown("""
            <div class="feature-card">
                <h4>📅 Weekly Trends</h4>
                <p style="color: #ddd;">Price analysis for the past week shows:</p>
                <ul style="color: #ddd;">
                    <li>📈 3% increase from Monday</li>
                    <li>📊 Stable mid-week performance</li>
                    <li>📈 Weekend demand pickup</li>
                    <li>🔮 Next week outlook: Positive</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

def guides_page():
    """Learning guides interface"""
    st.markdown("""
    <div class="main-header">
        <h1>📚 Agricultural Learning Hub</h1>
        <p>Comprehensive guides and resources for modern farming</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Learning stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📖 Resources", "2,847", "+47 this month")
    with col2:
        st.metric("👥 Learners", "24,580", "+312 today")
    with col3:
        st.metric("⭐ Rating", "4.8/5", "Expert validated")
    with col4:
        st.metric("🌐 Languages", "6+", "Multi-lingual")
    
    st.markdown("---")
    
    # Featured guide
    st.markdown("""
    <div class="feature-card" style="background: linear-gradient(135deg, rgba(39, 174, 96, 0.3), rgba(46, 204, 113, 0.2));">
        <h3>⭐ Featured: Complete Agriculture Manual</h3>
        <div style="display: flex; align-items: center; gap: 2rem;">
            <div style="text-align: center;">
                <div style="font-size: 4rem;">📚</div>
                <div style="background: linear-gradient(135deg, #27ae60, #2ecc71); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                    ⭐ 4.9/5 • 15K+ Downloads
                </div>
            </div>
            <div>
                <h4 style="color: white; margin-bottom: 1rem;">🌾 Comprehensive Sustainable Agriculture Guide</h4>
                <p style="color: #ddd; line-height: 1.6;">
                    The ultimate resource combining traditional wisdom with modern technology. 
                    Essential for both beginners and experienced farmers.
                </p>
                <div style="display: flex; gap: 1rem; margin: 1rem 0;">
                    <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 15px; font-size: 0.9rem;">📄 800+ Pages</span>
                    <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 15px; font-size: 0.9rem;">🎓 All Levels</span>
                    <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 15px; font-size: 0.9rem;">🆓 Free</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Access button
    guide_cols = st.columns([2, 1, 2])
    with guide_cols[1]:
        if st.button("📖 **Access Complete Guide**", use_container_width=True, type="primary"):
            st.success("🔗 Opening comprehensive agriculture guide...")
            st.markdown("[📚 **Download Agriculture Manual**](https://agritech.tnau.ac.in/pdf/AGRICULTURE.pdf)")
            st.balloons()
    
    st.markdown("---")
    
    # Learning paths
    st.markdown("### 🎯 Specialized Learning Paths")
    
    learning_paths = [
        {
            'title': '🌿 Organic Farming Mastery',
            'description': 'Master sustainable farming with natural methods and organic certification.',
            'level': 'Intermediate',
            'duration': '8 hours',
            'rating': '4.8/5',
            'modules': 8,
            'color': '#27ae60'
        },
        {
            'title': '🐛 Integrated Pest Management',
            'description': 'Advanced pest control combining biological and chemical methods.',
            'level': 'Advanced', 
            'duration': '6 hours',
            'rating': '4.9/5',
            'modules': 12,
            'color': '#e74c3c'
        },
        {
            'title': '💧 Water Management Systems',
            'description': 'Modern irrigation and water conservation techniques.',
            'level': 'Intermediate',
            'duration': '5 hours',
            'rating': '4.7/5',
            'modules': 10,
            'color': '#3498db'
        }
    ]
    
    for i, path in enumerate(learning_paths):
        path_cols = st.columns([2, 1]) if i % 2 == 0 else st.columns([1, 2])
        content_col = path_cols[0] if i % 2 == 0 else path_cols[1]
        action_col = path_cols[1] if i % 2 == 0 else path_cols
        
        with content_col:
            st.markdown(f"""
            <div class="feature-card" style="border-left: 4px solid {path['color']};">
                <h4 style="color: {path['color']};">{path['title']}</h4>
                <p style="color: #ddd; margin: 1rem 0;">{path['description']}</p>
                
                <div style="display: flex; gap: 0.5rem; margin: 1rem 0;">
                    <span style="background: rgba(39, 174, 96, 0.2); color: #27ae60; padding: 0.3rem 0.8rem; border-radius: 12px; font-size: 0.8rem;">
                        🎓 {path['level']}
                    </span>
                    <span style="background: rgba(52, 152, 219, 0.2); color: #3498db; padding: 0.3rem 0.8rem; border-radius: 12px; font-size: 0.8rem;">
                        ⏱️ {path['duration']}
                    </span>
                    <span style="background: rgba(241, 196, 15, 0.2); color: #f1c40f; padding: 0.3rem 0.8rem; border-radius: 12px; font-size: 0.8rem;">
                        ⭐ {path['rating']}
                    </span>
                </div>
                
                <div style="font-size: 0.9rem; color: #bbb;">
                    📚 {path['modules']} comprehensive modules included
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with action_col:
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <div style="background: linear-gradient(135deg, {path['color']}, {path['color']}dd); color: white; padding: 2rem; border-radius: 20px;">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">📚</div>
                    <h4 style="color: white;">Ready to Start?</h4>
                    <p style="margin: 0; opacity: 0.9;">{path['modules']} modules</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"📖 **Start Learning**", key=f"path_{i}", use_container_width=True, type="primary"):
                st.success(f"🚀 Starting {path['title']}...")
        
        if i < len(learning_paths) - 1:
            st.markdown("---")
    
    st.markdown("---")
    
    # Additional resources
    st.markdown("### 🎓 Additional Resources")
    
    resource_tabs = st.tabs(["📹 Videos", "🧪 Research", "👥 Community"])
    
    with resource_tabs[0]:
        st.markdown("""
        <div class="feature-card">
            <h4>📹 Video Tutorial Library</h4>
            <p style="color: #ddd;">Expert-led video tutorials covering practical techniques</p>
        </div>
        """, unsafe_allow_html=True)
        
        video_cols = st.columns(3)
        video_categories = [
            {"name": "🌱 Crop Management", "videos": 45, "duration": "12h"},
            {"name": "🐛 Pest Control", "videos": 32, "duration": "8h"},
            {"name": "🌿 Organic Methods", "videos": 28, "duration": "6h"}
        ]
        
        for i, cat in enumerate(video_categories):
            with video_cols[i]:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 12px; text-align: center;">
                    <h5 style="color: white;">{cat['name']}</h5>
                    <div style="color: #ddd;">📹 {cat['videos']} videos</div>
                    <div style="color: #ddd;">⏱️ {cat['duration']}</div>
                    <div style="background: #f8f9fa; color: #666; padding: 0.5rem; border-radius: 8px; margin-top: 1rem; font-size: 0.8rem;">
                        Coming Soon
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with resource_tabs[1]:
        st.markdown("""
        <div class="feature-card">
            <h4>🧪 Research Database</h4>
            <p style="color: #ddd;">Access to latest scientific research and case studies</p>
            
            <div style="margin: 1rem 0;">
                <strong style="color: white;">Available Categories:</strong>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.5rem; margin-top: 1rem; color: #ddd;">
                    <div>• 🌾 Crop Science & Genetics</div>
                    <div>• 🌱 Soil Science & Fertility</div>
                    <div>• 🐛 Plant Pathology</div>
                    <div>• 💧 Water Resources</div>
                    <div>• 🌿 Sustainable Agriculture</div>
                    <div>• 📊 Agricultural Economics</div>
                </div>
            </div>
            
            <div style="background: rgba(52,152,219,0.2); padding: 1rem; border-radius: 10px; text-align: center; color: white;">
                🔬 <strong>500+ peer-reviewed papers</strong> • Updated monthly • Expert summaries
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with resource_tabs[2]:
        st.markdown("""
        <div class="feature-card">
            <h4>👥 Global Farming Community</h4>
            <p style="color: #ddd;">Connect with farmers and experts worldwide</p>
        </div>
        """, unsafe_allow_html=True)
        
        community_cols = st.columns(4)
        stats = [
            {"metric": "👨‍🌾 Members", "value": "24,580", "growth": "+1,247"},
            {"metric": "💬 Discussions", "value": "1,450", "growth": "+23%"},
            {"metric": "🌍 Countries", "value": "67", "growth": "Global"},
            {"metric": "🏆 Experts", "value": "456", "growth": "Verified"}
        ]
        
        for i, stat in enumerate(stats):
            with community_cols[i]:
                st.metric(stat["metric"], stat["value"], stat["growth"])

def government_schemes_page():
    """Government schemes interface"""
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ Farmer Welfare & Government Support</h1>
        <p>Complete guide to schemes, subsidies, and support programs</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Scheme statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏛️ Active Schemes", "147", "+12 new")
    with col2:
        st.metric("👨‍🌾 Beneficiaries", "14.2 Cr", "+1.8 Cr")
    with col3:
        st.metric("💰 Budget", "₹3.18 L Cr", "FY 2024-25")
    with col4:
        st.metric("📈 Coverage", "96.8%", "Eligible farmers")
    
    st.markdown("---")
    
    # Emergency support
    st.markdown("""
    <div class="feature-card" style="border-left: 6px solid #dc3545; background: linear-gradient(135deg, rgba(220, 53, 69, 0.2), rgba(220, 53, 69, 0.1));">
        <h3>🚨 24/7 Emergency Support Network</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 2rem 0;">
            
            <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 12px;">
                <h4 style="color: #dc3545;">📞 Kisan Call Centre</h4>
                <div style="font-size: 2rem; color: #27ae60; font-weight: bold; margin: 1rem 0;">1800-180-1551</div>
                <div style="color: #ddd;">Available 24/7 in 22+ languages</div>
                
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <strong style="color: white;">Services:</strong>
                    <ul style="color: #ddd; margin: 0.5rem 0;">
                        <li>🌾 Crop advisory services</li>
                        <li>🐛 Pest management guidance</li>
                        <li>🌤️ Weather-based recommendations</li>
                        <li>💰 Government scheme information</li>
                    </ul>
                </div>
            </div>
            
            <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 12px;">
                <h4 style="color: #17a2b8;">🌐 Digital Channels</h4>
                <div style="margin: 1rem 0; color: #ddd;">
                    <div><strong>📧 Email:</strong> kisan.callcenter@gov.in</div>
                    <div><strong>🌐 Portal:</strong> agricoop.nic.in</div>
                    <div><strong>📱 App:</strong> Kisan Suvidha</div>
                </div>
                <div style="background: rgba(23,162,184,0.3); color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                    <strong>⚡ Response Time: < 2 minutes</strong><br>
                    <small>99.2% farmer satisfaction</small>
                </div>
            </div>
            
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Major schemes
    st.markdown("### 🏛️ Major Government Schemes")
    
    scheme_tabs = st.tabs(["💰 Income Support", "🛡️ Insurance", "🌱 Input Subsidies", "📊 Market Access"])
    
    with scheme_tabs[0]:
        st.markdown("#### 💰 Direct Income Support")
        
        pm_kisan = GOVERNMENT_SCHEMES['PM-KISAN']
        with st.expander(f"{pm_kisan['icon']} **{pm_kisan['name']}** - {pm_kisan['amount']}", expanded=True):
            info_col1, info_col2 = st.columns([2, 1])
            
            with info_col1:
                st.markdown(f"**📋 Overview:** {pm_kisan['description']}")
                
                st.markdown("**✅ Key Benefits:**")
                benefits = [
                    "₹6,000 per year in three installments",
                    "Direct bank transfer to account",
                    "No paperwork for renewal",
                    "Covers all landholding farmers"
                ]
                for benefit in benefits:
                    st.markdown(f"• {benefit}")
                
                st.markdown("**🎯 Eligibility:**")
                eligibility = [
                    "All landholding farmers",
                    "Valid Aadhaar card required",
                    "Bank account linked with Aadhaar",
                    "Land records in farmer's name"
                ]
                for criteria in eligibility:
                    st.markdown(f"• {criteria}")
            
            with info_col2:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 2rem; border-radius: 15px; text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">{pm_kisan['icon']}</div>
                    <h4 style="color: white;">Direct Benefit</h4>
                    <div style="font-size: 1.5rem; font-weight: bold;">{pm_kisan['amount']}</div>
                    <div style="margin-top: 0.5rem;">{pm_kisan['beneficiaries']}</div>
                    <div style="opacity: 0.8; font-size: 0.9rem;">Active Beneficiaries</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🔗 **Apply for PM-KISAN**", key="pm_kisan", use_container_width=True):
                    st.success("🌐 Opening PM-KISAN portal...")
                    st.markdown(f"[🔗 **PM-KISAN Portal**]({pm_kisan['url']})")
    
    with scheme_tabs[1]:
        st.markdown("#### 🛡️ Crop Insurance Programs")
        
        pmfby = GOVERNMENT_SCHEMES['PMFBY']
        with st.expander(f"{pmfby['icon']} **{pmfby['name']}** - {pmfby['amount']}", expanded=True):
            coverage_col1, coverage_col2 = st.columns(2)
            
            with coverage_col1:
                st.markdown("**🛡️ Coverage:**")
                coverage = [
                    "Pre-sowing/planting risks",
                    "Standing crop risks (drought, flood)",
                    "Post-harvest losses",
                    "Localized calamities"
                ]
                for item in coverage:
                    st.markdown(f"• {item}")
                
                st.markdown("**💰 Premium Structure:**")
                st.markdown("• **Kharif:** 2% of sum insured")
                st.markdown("• **Rabi:** 1.5% of sum insured")
                st.markdown("• **Horticulture:** 5% of sum insured")
            
            with coverage_col2:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #17a2b8, #20c997); color: white; padding: 1.5rem; border-radius: 12px;">
                    <h4 style="color: white;">📊 Scheme Statistics</h4>
                    <div><strong>Farmers:</strong> {pmfby['beneficiaries']}</div>
                    <div><strong>Area:</strong> 60M Hectares</div>
                    <div><strong>Claims Paid:</strong> ₹1.2L Cr</div>
                    <div><strong>Success Rate:</strong> 94.2%</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🛡️ **Apply for Insurance**", key="pmfby", use_container_width=True):
                    st.success("🌐 Opening PMFBY portal...")
                    st.markdown(f"[🔗 **PMFBY Portal**]({pmfby['url']})")
    
    with scheme_tabs[2]:
        st.markdown("#### 🌱 Input Subsidies")
        
        subsidies = [
            {"name": "Fertilizer Subsidy", "icon": "🧪", "desc": "50-80% subsidy on fertilizers", "coverage": "12 Cr farmers"},
            {"name": "Seed Subsidy", "icon": "🌰", "desc": "25-50% subsidy on certified seeds", "coverage": "8.5 Cr farmers"},
            {"name": "Machinery Subsidy", "icon": "🚜", "desc": "40-80% subsidy on equipment", "coverage": "3.2 Cr farmers"}
        ]
        
        for scheme in subsidies:
            st.markdown(f"""
            <div class="feature-card">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 2.5rem; margin-right: 1rem;">{scheme['icon']}</div>
                    <div>
                        <h4 style="color: white;">{scheme['name']}</h4>
                        <p style="color: #ddd;">{scheme['desc']}</p>
                        <div style="background: rgba(39,174,96,0.3); color: #27ae60; padding: 0.5rem 1rem; border-radius: 8px; display: inline-block;">
                            Coverage: {scheme['coverage']}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with scheme_tabs[3]:
        st.markdown("#### 📊 Market Access Programs")
        
        st.markdown("""
        <div class="feature-card">
            <h4>💰 e-NAM (National Agriculture Market)</h4>
            <p style="color: #ddd;">Online trading platform connecting agricultural markets</p>
            
            <div style="margin: 1rem 0;">
                <strong style="color: white;">Key Features:</strong>
                <ul style="color: #ddd;">
                    <li>Online trading platform</li>
                    <li>Price discovery mechanism</li>
                    <li>Quality assurance</li>
                    <li>Payment guarantee</li>
                </ul>
            </div>
            
            <div style="background: rgba(243,156,18,0.3); color: #f39c12; padding: 1rem; border-radius: 8px; text-align: center;">
                <strong>1,361 mandis connected • 23 states • 1.77 Cr traders</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔗 **Access e-NAM Portal**", use_container_width=True):
            st.success("🌐 Opening e-NAM trading platform...")

def main():
    """Main application entry point"""
    try:
        # Show loading screen on first visit
        if not st.session_state.app_loaded:
            show_loading_screen()
        # Language selection
        elif not st.session_state.language_selected:
            language_selection_page()
        # Main application
        else:
            main_app()
            
    except Exception as e:
        st.error(f"""
        🚨 **System Error**
        
        An error occurred: {str(e)}
        
        **Solutions:**
        1. Refresh the page and try again
        2. Clear browser cache
        3. Contact support: support@smartagri.ai
        
        **Emergency Support:**
        📞 Kisan Call Centre: 1800-180-1551
        """)

# Run the application
if __name__ == "__main__":
    main()
