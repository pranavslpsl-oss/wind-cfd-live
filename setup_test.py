import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- PAGE SETUP ---
st.set_page_config(page_title="Wind CFD Engine", layout="wide")
st.markdown("## 🌪️ Real-Time Computational Fluid Dynamics (CFD)")
st.markdown("Adjust parameters to visualize aerodynamic flow around complex geometry.")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Design Parameters")
    wind_speed = st.slider("Wind Velocity (m/s)", 10, 100, 45)
    tower_twist = st.slider("Tower Twist (Radians)", 0.0, 3.0, 1.5)
    resolution = st.select_slider("Simulation Resolution", options=["Low", "High"], value="Low")
    
    st.divider()
    pressure = 0.613 * wind_speed**2
    st.metric("Dynamic Pressure", f"{int(pressure)} Pa", delta=f"{wind_speed} m/s")

# --- SIMULATION LOGIC ---
def generate_simulation(twist, velocity):
    # 1. Generate Building Geometry
    height = 100
    radius = 15
    z = np.linspace(0, height, 50)
    theta = np.linspace(0, twist, 50) 
    
    theta_grid, z_grid = np.meshgrid(np.linspace(0, 2*np.pi, 30), z)
    twist_matrix = z_grid * (twist / height)
    b_x = radius * np.cos(theta_grid + twist_matrix)
    b_y = radius * np.sin(theta_grid + twist_matrix)
    
    # 2. Generate Wind Field
    x_vals = np.linspace(-40, 40, 15)
    y_vals = np.linspace(-40, 40, 15)
    z_vals = np.linspace(10, 90, 8)
    
    y, z, x = np.meshgrid(y_vals, z_vals, x_vals)
    
    # Potential Flow Logic (Deflecting wind around cylinder)
    r = np.sqrt(x**2 + y**2)
    mask = r > radius # Only calculate outside building
    
    u = np.ones_like(x) * velocity
    v = np.zeros_like(x)
    w = np.zeros_like(x)
    
    # Apply Bernoulli Deflection
    u[mask] = velocity * (1 - (radius**2 / r[mask]**2) * np.cos(2 * np.arctan2(y[mask], x[mask])))
    v[mask] = -velocity * (1 + (radius**2 / r[mask]**2)) * np.sin(2 * np.arctan2(y[mask], x[mask]))
    w[mask] = (z[mask] / 100) * 5 * np.cos(x[mask] * 0.1) # Turbulence
    
    return b_x, b_y, z_grid, x[mask], y[mask], z[mask], u[mask], v[mask], w[mask]

# --- RENDERER ---
b_x, b_y, b_z, wx, wy, wz, wu, wv, ww = generate_simulation(tower_twist, wind_speed)

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(projection='3d')

# Plot Building
ax.plot_surface(b_x, b_y, b_z, color='#2c3e50', alpha=0.9, edgecolor='white', linewidth=0.2)

# Plot Wind Flow
velocity_mag = np.sqrt(wu**2 + wv**2 + ww**2)
ax.quiver(wx, wy, wz, wu, wv, ww, length=5, normalize=True, cmap='jet', array=velocity_mag, alpha=0.6)

# Styling
ax.set_facecolor('black') 
fig.patch.set_facecolor('black')
ax.axis('off')
ax.set_title(f"AERODYNAMIC INTERACTION | Re: {int(wind_speed*1000)}", color='white')

# Display
st.pyplot(fig)