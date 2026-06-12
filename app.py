import random
import streamlit as st

# ---------------------------------------------------
# 1. CLASS DEFINITIONS
# ---------------------------------------------------
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

    def __str__(self):
        return f"{self.name:<20} | {self.status:<11} | Resilience: {self.resilience}"

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

# ---------------------------------------------------
# 2. INITIALIZATION
# ---------------------------------------------------
country = Country()

# Define all Assets
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

for a in assets_list: country.add_asset(a)

# Helper to find assets by name
def get_asset(name):
    return next(a for a in country.assets if a.name == name)

# Dependencies
get_asset("Transformer").add_dependency(get_asset("Nuclear Plant"))
get_asset("Substation").add_dependency(get_asset("Transformer"))
get_asset("TSMC Fab").add_dependency(get_asset("Substation"))
get_asset("TSMC Fab").add_dependency(get_asset("Pump Station"))
get_asset("Pump Station").add_dependency(get_asset("Treatment Plant"))
get_asset("Treatment Plant").add_dependency(get_asset("Substation"))

# TSMC specific
tsmc = get_asset("TSMC Fab")
tsmc.water_reserve_days = 3

event_pool = [
    Event("Cyber-Sabotage", 3, "Technical Glitch", "Precision"),
    Event("Rogue Operator Strike", 8, "Rogue PLA Operative", "Precision"),
    Event("Preemptive Strike", 12, "Preemptive Military Strategy", "Saturation")
]

# ---------------------------------------------------
# 3. CORE LOGIC
# ---------------------------------------------------
def apply_event(event):
    for asset in country.assets:
        if event.scope == "Precision" and asset == tsmc:
            asset.resilience -= (event.severity * 15)
        elif event.scope == "Saturation" and asset.sector in ["Power", "Industry"]:
            asset.resilience -= (event.severity * 2)
        if asset.resilience <= 0:
            asset.resilience = 0
            asset.status = "Offline"

def update_system():
    # Dependency check
    for asset in country.assets:
        if asset.resilience <= 0:
            asset.status = "Offline"
            continue
        
        # Simple dependency logic
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

    # Metrics
    country.chip_output = 100 if tsmc.status == "Operational" else (50 if "Degraded" in tsmc.status else 0)
    country.gdp_loss = 100 - country.calculate_gdp()

# Streamlit Interface
st.title("National Resilience Simulator")
ev = random.choice(event_pool)
apply_event(ev)
update_system()
st.write(f"Triggered: {ev.name}")

update_system()
st.write(f"Current GDP Loss: {country.gdp_loss}%")
# --- DASHBOARD LAYOUT ---
st.title("National Resilience Simulator")

# 1. TOP: KPI METRICS
col1, col2, col3 = st.columns(3)
col1.metric("GDP Loss", f"{country.gdp_loss}%")
col2.metric("Power Outage", f"{country.population_without_power:,}")
col3.metric("Chip Output", f"{country.chip_output}%")

# 2. MIDDLE: EVENT CONTROLS
st.subheader("Crisis Management")
if st.button("Trigger Random Event"):
    ev = random.choice(event_pool)
    apply_event(ev)
    update_system()
    st.warning(f"🚨 **Incident Reported:** {ev.name} ({ev.cause})")

# 3. BOTTOM: ASSET HEALTH & DATA
st.subheader("Infrastructure Integrity")
# Create a layout for visual bars
for asset in country.assets:
    # Color-code the progress bar based on resilience
    bar_color = "green" if asset.resilience > 50 else "red"
    st.write(f"{asset.name}")
    st.progress(asset.resilience / 100)

# Optional: Interactive table for detailed view
st.subheader("Asset Details")
st.dataframe(
    [{"Name": a.name, "Status": a.status, "Resilience": a.resilience} for a in country.assets]
)
for a in country.assets:
    st.text(str(a))
