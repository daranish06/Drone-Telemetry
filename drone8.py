import streamlit as st
import random
import time
import pandas as pd
from streamlit_echarts import st_echarts

# Page setup
st.set_page_config(page_title="Drone Telemetry", layout="wide")
st.title("🚁 Drone Telemetry Dashboard")

# Simulate telemetry data
def get_telemetry():
    return {
        "Battery": round(random.uniform(9.0, 12.0), 2),
        "Roll": round(random.uniform(-180, 180), 2),
        "Pitch": round(random.uniform(-90, 90), 2),
        "Yaw": round(random.uniform(-180, 180), 2),
        "Temp": round(random.uniform(20, 40), 1),
        "Altitude": round(random.uniform(0, 500), 1),
        "Lat": round(random.uniform(12.0, 13.0), 6),
        "Lon": round(random.uniform(77.0, 78.0), 6),
        "Connection": random.choice(["Excellent", "Poor", "No Signal"])
    }

# Controls
run = st.checkbox("▶️ Start Telemetry", value=True)
interval = st.slider("⏱️ Update Interval (seconds)", 1, 10, 2)
# Data history
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Time", "Battery", "Altitude", "Temp"])

# Placeholders
placeholder = st.empty()

# Loop while telemetry is running
while run:
    data = get_telemetry()
    now = pd.Timestamp.now().strftime("%H:%M:%S")

    # Update telemetry history
    new_row = pd.DataFrame({
        "Time": [now],
        "Battery": [data["Battery"]],
        "Altitude": [data["Altitude"]],
        "Temp": [data["Temp"]]
    })
    st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
    st.session_state.history = st.session_state.history.tail(50)

    with placeholder.container():
        tab1, tab2, tab3 = st.tabs(["📊 Live Metrics", "📈 Telemetry Charts", "🗺️ GPS Map"])

        with tab1:
            st.subheader("Live Drone Data")
            col1, col2, col3 = st.columns(3)

            col1.metric("🔋 Battery (V)", f"{data['Battery']}V")
            col1.metric("🌡️ Temperature", f"{data['Temp']}°C")

            col2.metric("🎛️ Roll", f"{data['Roll']}°")
            col2.metric("🎛️ Pitch", f"{data['Pitch']}°")
            col2.metric("🎛️ Yaw", f"{data['Yaw']}°")

            col3.metric("📍 Latitude", f"{data['Lat']}")
            col3.metric("📍 Longitude", f"{data['Lon']}")
            col3.metric("🛫 Altitude", f"{data['Altitude']}m")

            conn_status = {
                "Excellent": "🟢 Excellent",
                "Poor": "🟠 Poor",
                "No Signal": "🔴 No Signal"
            }
            st.markdown(f"**📶 Connection Health:** `{conn_status[data['Connection']]}`")

            st.subheader("🔋 Battery Gauge")
            option = {
                "series": [{
                    "type": 'gauge',
                    "progress": {"show": True},
                    "axisLine": {"lineStyle": {"width": 20}},
                    "detail": {"valueAnimation": True, "formatter": '{value}V'},
                    "data": [{"value": data["Battery"], "name": "Battery"}]
                }]
            }
            st_echarts(options=option, height="300px", key=f"battery_gauge_{time.time()}")

            # Warnings
            if data["Battery"] < 10.0:
                st.error("⚠️ Low Battery!")
            if data["Temp"] > 35:
                st.warning("🔥 High Temperature!")
            if data["Connection"] == "No Signal":
                st.error("🚨 No Signal Detected!")

        with tab2:
            st.subheader("📈 Battery / Altitude / Temperature Trends")
            st.line_chart(st.session_state.history.set_index("Time"))

        with tab3:
            st.subheader("🌍 Live Drone Location")
            st.map(pd.DataFrame({'lat': [data["Lat"]], 'lon': [data["Lon"]]}))

    time.sleep(interval)
    
