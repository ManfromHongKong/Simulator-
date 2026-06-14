import streamlit as st
import random

# --- 1. CLASS DEFINITIONS ---
class Asset:
    def __init__(self, name, sector, resilience=100, contribution=10):
        self.name = name
        self.sector = sector
        self.resilience = resilience
        self.status = "Operational"
        self.dependencies = []
        self.contribution = contribution
        self.water_reserve_days = 0

class Event:
    def __init__(self, name, severity, cause, scope):
        self.name = name
        self.severity = severity
        self.cause = cause
        self.scope = scope

class Country:
    def __init__(self):
        self.assets = []
        self.day = 0
        self.gdp_loss = 0

    def add_asset(self, asset):
        self.assets.append(asset)

# --- 2. INITIALIZATION (Session State) ---
if 'country' not in st.session_state:
    c = Country()
    c.add_asset(Asset("TSMC Fab", "Industry", 100, 30))
    c.add_asset(Asset("Substation", "Power", 100, 10))
    c.add_asset(Asset("Pump Station", "Water", 100, 5))
    st.session_state.country = c
    st.session_state.event_pool = [
        Event("Cyber-Sabotage", 3, "Technical Glitch", "Precision"),
        Event("Rogue Operator Strike", 8, "Rogue PLA Operative", "Precision"),
        Event("Preemptive Strike", 12, "Preemptive Military Strategy", "Saturation")
    ]

# --- 3. LOGIC FUNCTIONS ---
def apply_event(event):
    for asset in st.session_state.country.assets:
        if event.scope == "Precision" and asset.name == "TSMC Fab":
            asset.resilience -= (event.severity * 15)
        elif event.scope == "Saturation" and asset.sector in ["Power", "Industry"]:
            asset.resilience -= (event.severity * 2)
        asset.resilience = max(0, asset.resilience)
        if asset.resilience == 0: asset.status = "Offline"

# --- 4. INTERFACE ---
st.title("National Resilience Simulator")

# Sidebar Controls
st.sidebar.header("Crisis Triggers")
selected_event_name = st.sidebar.selectbox("Select Trigger Event", [e.name for e in st.session_state.event_pool])
if st.sidebar.button("Apply Crisis Scenario"):
    ev = next(e for e in st.session_state.event_pool if e.name == selected_event_name)
    apply_event(ev)
    st.success(f"Triggered: {ev.name}")

# Display Metrics
col1, col2 = st.columns(2)
col1.metric("GDP Loss", f"{st.session_state.country.gdp_loss}%")

st.subheader("Infrastructure Integrity")
for asset in st.session_state.country.assets:
    st.write(f"{asset.name}: {asset.status} ({asset.resilience}%)")
    st.progress(asset.resilience / 100)
