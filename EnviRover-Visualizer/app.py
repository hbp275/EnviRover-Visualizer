import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime, timedelta
import os
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(layout="wide")
DATA_FILE = "data/sample_data.csv"

st.title("📡 EnviRover Live Sensor Dashboard")

# ---------- Data loader ----------
@st.cache_data(ttl=60)
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("No data available yet. Waiting for EnviRover to send data…")
    st.stop()

# ---------- Time‑range filter ----------
time_map = {
    "All Time": None,
    "Last 7 Days": timedelta(days=7),
    "Today": timedelta(days=0),
    "Last 1 Hour": timedelta(hours=1)
}
time_col = st.columns([1, 4, 1])[1]
selected_range = time_col.selectbox("📅 Time Range", list(time_map.keys()), index=0)

if time_map[selected_range] is not None:
    now = datetime.now()
    if selected_range == "Today":
        df = df[df["timestamp"].dt.date == now.date()]
    else:
        df = df[df["timestamp"] >= now - time_map[selected_range]]

if df.empty:
    st.warning("No data to show in the selected time range.")
    st.stop()

# ---------- UI controls ----------
enable_prediction = st.checkbox("🔮 Enable Prediction")

sensor_options = ["temperature", "humidity", "distance"]
display_labels = {
    "temperature": "Temperature (°C)",
    "humidity": "Humidity (%)",
    "distance":  "Distance (cm)"
}

st.subheader("Sensor Visualizations")

# ---------- Graphs (first row) ----------
graph_rows = [st.columns(2), st.columns(2)]

for j in range(2):
    idx = j
    with graph_rows[0][j]:
        sensor = st.selectbox(
            f"Sensor {idx+1}", sensor_options,
            index=idx % len(sensor_options),
            key=f"sensor_{idx}", label_visibility="collapsed"
        )

        data = df[["timestamp", sensor]].dropna()
        if data.empty:
            st.write(f"No data for {display_labels[sensor]}")
            continue

        fig, ax = plt.subplots()
        data["timestamp"] = pd.to_datetime(data["timestamp"])
        ax.plot(data["timestamp"], data[sensor], marker='o', label="Actual", color='blue')

        # ----- Prediction -----
        if enable_prediction and len(data) >= 2:
            try:
                start_time = data["timestamp"].min()
                X = (data["timestamp"] - start_time).dt.total_seconds().values.reshape(-1, 1)
                y = data[sensor].values

                model = LinearRegression().fit(X, y)

                last_date = data["timestamp"].max()
                freq = data["timestamp"].diff().mode()[0] if not data["timestamp"].diff().mode().empty else timedelta(minutes=5)
                future_dates = [last_date + freq * (i + 1) for i in range(10)]
                future_seconds = np.array([(fd - start_time).total_seconds() for fd in future_dates]).reshape(-1, 1)
                y_future = model.predict(future_seconds)

                ax.plot(future_dates, y_future, 'r--', marker='x', label="Predicted", linewidth=2)
            except Exception as e:
                st.warning(f"Prediction failed: {e}")

        # ----- Formatting -----
        ax.xaxis.set_major_formatter(DateFormatter('%d %b %I:%M %p'))
        ax.set_xlabel("Time")
        ax.set_ylabel(display_labels[sensor])
        ax.set_title(display_labels[sensor])
        ax.legend()
        fig.autofmt_xdate(rotation=30)
        ax.tick_params(axis='x', labelsize=8)
        st.pyplot(fig)

# ---------- Spacer between rows ----------
st.markdown("<br><br>", unsafe_allow_html=True)

# ---------- Graphs (second row) ----------
for j in range(2):
    idx = 2 + j
    with graph_rows[1][j]:
        sensor = st.selectbox(
            f"Sensor {idx+1}", sensor_options,
            index=idx % len(sensor_options),
            key=f"sensor_{idx}", label_visibility="collapsed"
        )

        data = df[["timestamp", sensor]].dropna()
        if data.empty:
            st.write(f"No data for {display_labels[sensor]}")
            continue

        fig, ax = plt.subplots()
        data["timestamp"] = pd.to_datetime(data["timestamp"])
        ax.plot(data["timestamp"], data[sensor], marker='o', label="Actual", color='blue')

        if enable_prediction and len(data) >= 2:
            try:
                start_time = data["timestamp"].min()
                X = (data["timestamp"] - start_time).dt.total_seconds().values.reshape(-1, 1)
                y = data[sensor].values

                model = LinearRegression().fit(X, y)

                last_date = data["timestamp"].max()
                freq = data["timestamp"].diff().mode()[0] if not data["timestamp"].diff().mode().empty else timedelta(minutes=5)
                future_dates = [last_date + freq * (i + 1) for i in range(10)]
                future_seconds = np.array([(fd - start_time).total_seconds() for fd in future_dates]).reshape(-1, 1)
                y_future = model.predict(future_seconds)

                ax.plot(future_dates, y_future, 'r--', marker='x', label="Predicted", linewidth=2)
            except Exception as e:
                st.warning(f"Prediction failed: {e}")

        
        ax.xaxis.set_major_formatter(DateFormatter('%d %b %I:%M %p'))
        ax.set_xlabel("Time", labelpad=10)
        ax.set_ylabel(display_labels[sensor], labelpad=10)
        ax.set_title(display_labels[sensor])
        ax.legend()
        fig.autofmt_xdate(rotation=30)
        ax.tick_params(axis='x', labelsize=8)
        st.pyplot(fig)

