import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import os
from PIL import Image

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="GreenSim | The Science of Photosynthesis",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Advanced Global CSS Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Metric Cards Styling */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        transition: transform 0.3s ease;
    }
    .stMetric:hover {
        transform: translateY(-5px);
        border-color: rgba(16, 185, 129, 0.4) !important;
    }
    
    /* Custom Info Cards */
    .status-banner {
        background: rgba(16, 185, 129, 0.1);
        padding: 24px;
        border-radius: 20px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    .equation-box {
        background: rgba(0,0,0,0.3);
        padding: 20px;
        border-radius: 16px;
        border: 1px dashed rgba(255, 255, 255, 0.2);
        font-family: 'Courier New', monospace;
        text-align: center;
        margin-top: 15px;
    }

    .challenge-card {
        background: rgba(245, 158, 11, 0.1);
        padding: 12px;
        border-radius: 12px;
        border-left: 5px solid #f59e0b;
        margin-bottom: 12px;
        font-size: 0.95rem;
    }

    /* Sidebar Image */
    .sidebar .sidebar-content {
        background-color: #0f172a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Persistent State Management ---
if 'init' not in st.session_state:
    st.session_state.init = True
    st.session_state.growth = 0
    st.session_state.health = 100
    st.session_state.history = {'time': [], 'o2': [], 'co2_abs': []}
    st.session_state.running = True
    st.session_state.co2_input = 400
    st.session_state.temp_input = 24
    st.session_state.light_input = 70

# --- 4. Sidebar: Lab Controls & Presets ---
try:
    banner_path = os.path.join(os.getcwd(), "greensim_assets", "banner.png")
    if os.path.exists(banner_path):
        st.sidebar.image(banner_path, use_container_width=True)
    else:
        st.sidebar.title("🌲 GreenSim Lab")
except Exception:
    st.sidebar.title("🌲 GreenSim Lab")

st.sidebar.markdown("### 🌎 Environmental Presets")
c1, c2 = st.sidebar.columns(2)

def set_preset(co2, temp, light):
    st.session_state.co2_input = co2
    st.session_state.temp_input = temp
    st.session_state.light_input = light
    st.rerun()

if c1.button("🍀 Tropical", use_container_width=True): set_preset(450, 28, 90)
if c2.button("🏜️ Desert", use_container_width=True): set_preset(320, 42, 100)
if c1.button("🚀 Mars", use_container_width=True): set_preset(1800, 8, 45)
if c2.button("🏠 Office", use_container_width=True): set_preset(650, 22, 15)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏆 Learning Challenges")
st.sidebar.markdown("""
<div class='challenge-card'>💎 <b>Quest:</b> Achieve 100% Photosynthesis efficiency.</div>
<div class='challenge-card'>🌳 <b>Quest:</b> Grow a mature tree in under 60 seconds.</div>
<div class='challenge-card'>🌍 <b>Quest:</b> Reverse a 'Suffocating' atmosphere.</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ manual adjustment")
co2_val = st.sidebar.slider("Ambient CO₂ (ppm)", 100, 2500, st.session_state.co2_input)
temp_val = st.sidebar.slider("Temperature (°C)", -5, 55, st.session_state.temp_input)
light_val = st.sidebar.slider("Sunlight Intensity (%)", 0, 100, st.session_state.light_input)

# Side Control Row
col_ctrl1, col_ctrl2 = st.sidebar.columns(2)
if col_ctrl1.button("⏹️ Stop" if st.session_state.running else "▶️ Start", use_container_width=True):
    st.session_state.running = not st.session_state.running
    st.rerun()

if col_ctrl2.button("🔄 Reset", use_container_width=True):
    st.session_state.growth = 0
    st.session_state.health = 100
    st.session_state.history = {'time': [], 'o2': [], 'co2_abs': []}
    st.rerun()

# --- 5. Simulation Logic Engine ---
def run_photosynthesis_model(co2, temp, light):
    # Normalized efficiency factors
    # 1. Light: Sine curve (reaches peak at 80-90%)
    f_light = np.sin((light / 100) * (np.pi / 2))
    # 2. CO2: Logarithmic saturation
    f_co2 = min(co2 / 900, 1.5)
    # 3. Temp: Bell curve (peak at 25C)
    f_temp = np.exp(-((temp - 25)**2) / (2 * 12**2))
    
    total_efficiency = f_light * f_co2 * f_temp
    
    # Outputs
    growth_rate = total_efficiency * 1.8
    o2_out = total_efficiency * 9.5
    carbon_in = total_efficiency * 8.2
    
    # Qualitative Description
    if temp > 38: status = "Heat Stress! Plant pores (stomata) are closing. 🥵"
    elif temp < 5: status = "Cold Stress! Chemical reactions have frozen. 🥶"
    elif light < 15: status = "Light Deprivation! The plant is in dormant mode. 🌑"
    elif co2 < 250: status = "Carbon Starvation! The plant cannot build sugar. 🍽️"
    else: status = "Optimal Balance! High-velocity carbon sequestration. ✨"
    
    return growth_rate, o2_out, carbon_in, status, total_efficiency

# Calculate current frame
g_rate, o2, carbon, status_text, efficiency = run_photosynthesis_model(co2_val, temp_val, light_val)

# Update Persistent Data
if st.session_state.running:
    st.session_state.growth = min(100, st.session_state.growth + g_rate * 0.4)
    # Health logic
    if temp_val > 45 or temp_val < 0 or co2_val < 150:
        st.session_state.health = max(0, st.session_state.health - 1.5)
    else:
        st.session_state.health = min(100, st.session_state.health + 0.3)
    
    # History tracking
    t_step = len(st.session_state.history['time'])
    st.session_state.history['time'].append(t_step)
    st.session_state.history['o2'].append(float(o2))
    st.session_state.history['co2_abs'].append(float(carbon))
    
    if len(st.session_state.history['time']) > 50:
        for k in st.session_state.history:
            st.session_state.history[k] = st.session_state.history[k][-50:]

# --- 6. Main Dashboard Assembly ---
st.title("🧪 GreenSim: The Life Cycle Dashboard")
st.markdown(f"<div class='status-banner'><h2 style='margin:0; color:#10b981;'>{status_text}</h2></div>", unsafe_allow_html=True)

# Row 1: Key Metrics
met1, met2, met3, met4 = st.columns(4)
met1.metric("💚 Vitality", f"{st.session_state.health:.0f}%", help="Overall plant survival health.")
met2.metric("🌱 Maturity", f"{st.session_state.growth:.1f}%", help="Genetic growth toward maturity.")
met3.metric("💎 O₂ Yield", f"{o2:.1f}", help="Oxygen output in units/sec.")
met4.metric("🌪️ CO₂ Capture", f"{carbon:.1f}", help="Carbon absorbed from the air.")

st.write("---")

# Row 2: Visualizations
vis_col, info_col = st.columns([2, 1])

with vis_col:
    # A. The Gauge
    gauge_sub1, gauge_sub2 = st.columns(2)
    with gauge_sub1:
        fig_g = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = efficiency * 100,
            title = {'text': "Efficiency %", 'font': {'size': 20}},
            gauge = {
                'axis': {'range': [0, 150]},
                'bar': {'color': "#10b981"},
                'steps': [
                    {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.1)"},
                    {'range': [50, 100], 'color': "rgba(245, 158, 11, 0.1)"},
                    {'range': [100, 150], 'color': "rgba(16, 185, 129, 0.1)"}
                ]
            }
        ))
        fig_g.update_layout(height=220, margin=dict(t=50, b=0, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_g, use_container_width=True)
    
    with gauge_sub2:
        # Mini State Indicator
        h_color = "#10b981" if st.session_state.health > 70 else "#f59e0b" if st.session_state.health > 30 else "#ef4444"
        st.markdown(f"""
            <div style='background:rgba(255,255,255,0.05); border-radius:15px; height:180px; text-align:center; padding-top:30px; border:1px solid rgba(255,255,255,0.1);'>
                <p style='color:#a0a0a0; margin:0;'>Ecosystem Stability</p>
                <h1 style='color:{h_color}; font-size:4rem; margin:0;'>{st.session_state.health:.0f}</h1>
                <p style='color:#60a5fa;'>Sustainability Score</p>
            </div>
        """, unsafe_allow_html=True)

    # B. The Pipeline Graph
    fig_main = go.Figure()
    fig_main.add_trace(go.Scatter(x=st.session_state.history['time'], y=st.session_state.history['o2'], name="O₂ Output", fill='tozeroy', line=dict(color='#10b981', width=4)))
    fig_main.add_trace(go.Scatter(x=st.session_state.history['time'], y=st.session_state.history['co2_abs'], name="CO₂ Input", line=dict(color='#8b5cf6', width=3, dash='dot')))
    
    fig_main.update_layout(
        title="<b>Atmospheric Exchange Timeline</b>",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        margin=dict(l=0, r=0, t=60, b=0),
        legend=dict(orientation="h", y=1.2)
    )
    st.plotly_chart(fig_main, use_container_width=True)

with info_col:
    st.subheader("👨‍🔬 Scientist's Corner")
    st.markdown("""
    <div class='equation-box'>
    <b>Formula:</b><br>
    CO₂ + H₂O + Light ☀️<br>
    ➡️<br>
    Sugar + <b>O₂</b> 💎
    </div>
    """, unsafe_allow_html=True)
    
    st.info("**Research Tip:** Plants absorb the most Carbon when the temperature is around 25°C and CO₂ is over 600ppm.")
    
    # Visual Growth
    p_stage = int(st.session_state.growth // 10)
    p_icon = "🌱" if p_stage < 3 else "🌿" if p_stage < 6 else "🌳" if p_stage < 9 else "🌲"
    st.markdown(f"<div style='font-size: 110px; text-align:center;'>{p_icon}</div>", unsafe_allow_html=True)
    st.progress(int(st.session_state.growth))
    st.caption(f"Plant is in stage: **{'Seedling' if p_stage < 3 else 'Vegetative' if p_stage < 6 else 'Flowering' if p_stage < 9 else 'Mature'}**")

# --- 7. Footer: Atmosphere Watch ---
st.write("---")
st.subheader("🌍 Planetary Health Watch")
# Dynamic Impact Logic
i_score = (o2 * 15) - (co2_val / 12)
i_status = "💚 ATMOSPHERE IS HEALING" if i_score > 0 else "🚨 ATMOSPHERE IS SUFFOCATING"
i_color = "#10b981" if i_score > 0 else "#ef4444"

st.markdown(f"<h3 style='color:{i_color};'>{i_status}</h3>", unsafe_allow_html=True)
st.progress(int(min(100, max(0, 50 + i_score))))

# Trivia Cycle
trivias = [
    "A single tree can absorb 48 lbs of CO2 per year.",
    "Phytoplankton in the ocean produce 50% of Earth's oxygen!",
    "Plants only use green light's frequency the least, reflecting it back to our eyes.",
    "The Amazon Rainforest is often called the 'Lungs of the Planet'."
]
st.write(f"💡 **Did you know?** {trivias[int(time.time() % 4)]}")

# Loop
if st.session_state.running:
    time.sleep(0.45)
    st.rerun()
