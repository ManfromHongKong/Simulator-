import streamlit as st
import random

# --- 1. CLASS DEFINITIONS ---
class Asset:
    def __init__(self, name, sector, resilience=100, repair_days=5, contribution=10):
        self.name = name
        self.sector = sector
        self.resilience = resilience
        self.repair_days = repair_days
        self.status = "Operational"
        self.dependencies = []
        self.dependents = []
        self.resources = {}
        self.water_reserve_days = None
        self.contribution = contribution

    def add_dependency(self, asset):
        self.dependencies.append(asset)
        asset.dependents.append(self)

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
        self.population_without_power = 0
        self.population_without_water = 0
        self.chip_output = 100
        self.port_capacity = 100
        self.gdp_loss = 0
        self.gdp_history = []

    def add_asset(self, asset):
        self.assets.append(asset)

    def calculate_gdp(self):
        return sum(asset.contribution for asset in self.assets if asset.status == "Operational")

# --- 2. INITIALIZATION (Saves your work across clicks) ---
if 'country' not in st.session_state:
    c = Country()
    assets_list = [
        Asset("Nuclear Plant", "Power", 100, 5, 20), Asset("Coal Plant", "Power", 100, 5, 15),
        Asset("Gas Plant", "Power", 100, 5, 15), Asset("Transformer", "Power", 100, 5, 10),
        Asset("Substation", "Power", 100, 5, 10), Asset("Reservoir", "Water", 100, 5, 5),
        Asset("Treatment Plant", "Water", 100, 5, 5), Asset("Pump Station", "Water", 100, 5, 5),
        Asset("Port", "Transport", 100, 5, 10), Asset("Airport", "Transport", 100, 5, 10),
        Asset("Rail Hub", "Transport", 100, 5, 5), Asset("Highway Junction", "Transport", 100, 5, 5),
        Asset("Radar Station", "Military", 100, 5, 5), Asset("Air Base", "Military", 100, 5, 10),
        Asset("Naval Base", "Military", 100, 5, 10), Asset("Army Brigade", "Military", 100, 5, 10),
        Asset("Bank", "Finance", 100, 5, 15), Asset("Stock Exchange", "Finance", 100, 5, 15),
        Asset("TSMC Fab", "Industry", 100, 5, 30), Asset("Hospital", "Health", 100, 5, 5),
        Asset("Supermarket", "Food", 100, 5, 5), Asset("Population Centre", "Society", 100, 5, 5)
    ]
    for a in assets_list: c.add_asset(a)
    
    def get_a(name): return next(a for a in c.assets if a.name == name)
    get_a("Transformer").add_dependency(get_a("Nuclear Plant"))
    get_a("Substation").add_dependency(get_a("Transformer"))
    get_a("TSMC Fab").add_dependency(get_a("Substation"))
    get_a("TSMC Fab").add_dependency(get_a("Pump Station"))
    get_a("Pump Station").add_dependency(get_a("Treatment Plant"))
    get_a("Treatment Plant").add_dependency(get_a("Substation"))
    
    get_a("TSMC Fab").water_reserve_days = 3
    
    st.session_state.country = c
    st.session_state.event_pool = [
        Event("Cyber-Sabotage", 3, "Technical Glitch", "Precision"),
        Event("Rogue Operator Strike", 8, "Rogue PLA Operative", "Precision"),
        Event("Preemptive Strike", 12, "Preemptive Military Strategy", "Saturation")
    ]

# --- 3. CORE LOGIC FUNCTIONS ---
def update_system():
    country = st.session_state.country
    tsmc = next(a for a in country.assets if a.name == "TSMC Fab")
    for asset in country.assets:
        if asset.resilience <= 0:
            asset.status = "Offline"
            continue
        if not asset.dependencies:
            asset.status = "Operational"
        elif any(dep.status == "Offline" for dep in asset.dependencies):
            if asset.name == "TSMC Fab" and tsmc.water_reserve_days > 0:
                tsmc.water_reserve_days -= 1
                asset.status = "Degraded"
            else:
                asset.status = "Offline"
        else:
            asset.status = "Operational"
    country.chip_output = 100 if tsmc.status == "Operational" else (50 if "Degraded" in tsmc.status else 0)
    country.gdp_loss = 100 - country.calculate_gdp()

# --- 4. INTERFACE ---
st.title("National Resilience Simulator")

# Sidebar
st.sidebar.header("Crisis Triggers")
selected_event = st.sidebar.selectbox("Select Event", [e.name for e in st.session_state.event_pool], key="evt_sel")
if st.sidebar.button("Trigger Selection"):
    ev = next(e for e in st.session_state.event_pool if e.name == selected_event)
    # Apply your apply_event logic here...
    update_system()
    st.success(f"Triggered: {ev.name}")

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("GDP Loss", f"{st.session_state.country.gdp_loss}%")
col2.metric("Power Outage", f"{st.session_state.country.population_without_power:,}")
col3.metric("Chip Output", f"{st.session_state.country.chip_output}%")
