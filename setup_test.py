import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Wind Chisel 3D", layout="wide", page_icon="🏗️")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🎛️ Parametric Controls")
    
    # 1. The Force (Wind)
    wind_velocity = st.slider("💨 Wind Velocity (m/s)", 10, 100, 45)
    
    # 2. The Resistance (Structure)
    material_strength = st.slider("🧱 Panel Resistance", 1000, 5000, 3000)
    
    st.divider()
    
    # Real-Time Math
    pressure = 0.613 * wind_velocity**2
    st.metric("Dynamic Wind Pressure", f"{int(pressure)} Pa")
    
    if pressure > material_strength:
        st.error("⚠️ CRITICAL FAILURE: EROSION ACTIVE")
    else:
        st.success("✅ SYSTEM STABLE")

# --- MAIN 3D VIEW ---
st.title("🏗️ THE WIND CHISEL: Real-Time Form Finding")
st.markdown("This tool **removes** facade panels that exceed their structural capacity, automatically sculpting an aerodynamic form.")

# --- GENERATE THE BUILDING (VOXELS) ---
def generate_tower(velocity, strength):
    # 1. Create a 3D Grid of Points (10x10x20 tower)
    x, y, z = np.indices((10, 10, 20))
    
    # Flatten the grid to arrays
    x = x.flatten()
    y = y.flatten()
    z = z.flatten()
    
    # 2. Calculate Wind Load on EACH Panel (Physics)
    # Wind gets stronger with height (Power Law)
    height_factor = (z / 20) ** 0.5
    local_pressure = (0.613 * velocity**2) * height_factor * 1.5
    
    # 3. The "Chisel" Logic (Erosion)
    # Only keep panels where Pressure < Strength
    # (Or keep the core structure so it doesn't vanish completely)
    core_structure = (x > 3) & (x < 6) & (y > 3) & (y < 6) # The concrete core
    surviving_panels = (local_pressure < strength) | core_structure
    
    return x[surviving_panels], y[surviving_panels], z[surviving_panels], local_pressure[surviving_panels]

# Get the data based on YOUR sliders
x, y, z, pressure_data = generate_tower(wind_velocity, material_strength)

# --- PLOTLY 3D RENDERER ---
fig = go.Figure(data=[go.Scatter3d(
    x=x, y=y, z=z,
    mode='markers',
    marker=dict(
        size=6,
        color=pressure_data,       # Color by Wind Pressure
        colorscale='Jet',          # Red = High Stress, Blue = Low
        opacity=0.8,
        symbol='square'            # Looks like facade panels
    )
)])

# Styling to make it look like Engineering Software
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data'
    ),
    margin=dict(l=0, r=0, b=0, t=0),
    height=700,
    paper_bgcolor='black' # Dark Mode
)

st.plotly_chart(fig, use_container_width=True)