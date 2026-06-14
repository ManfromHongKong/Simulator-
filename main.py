import random

# 1. CONSOLIDATED CLASS DEFINITIONS
class Event:
    def __init__(self, name, severity, cause, scope):
        self.name = name
        self.severity = severity
        self.cause = cause
        self.scope = scope

class Asset:
    def __init__(self, name, sector, resilience=100, repair_days=5, contribution=10):
        self.name = name
        self.sector = sector
        self.resilience = resilience
        self.repair_days = repair_days
        self.contribution = contribution
        self.status = "Operational"
        self.dependencies = []
        self.dependents = []
        self.days_offline = 0
        self.resources = {}
        self.water_reserve_days = None

    def add_dependency(self, asset):
        self.dependencies.append(asset)
        asset.dependents.append(self)

    def __str__(self):
        return f"{self.name:<20} | {self.status:<11} | Resilience: {self.resilience}"

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

    def calculate_gdp(self):
        return sum(asset.contribution for asset in self.assets if asset.status == "Operational")

    def add_asset(self, asset):
        self.assets.append(asset)

# 2. INITIALIZATION
country = Country()
# ... [Insert your asset creation block here: nuclear_plant, coal_plant, etc.]
# ... [Insert your dependencies block here: transformer.add_dependency, etc.]

# 3. EVENT POOL
# Defined AFTER the class Event is finalized
event_pool = [
    Event("Cyber-Sabotage", 3, "Technical Glitch", "Precision"),
    Event("Rogue Operator Strike", 8, "Rogue PLA Operative", "Precision"),
    Event("Accidental Escalation", 10, "Political Incident", "Saturation"),
    Event("Preemptive Strike", 12, "Preemptive Military Strategy", "Saturation"),
    Event("Demonstrative Strike", 5, "Political Signaling", "Precision")
]

# 4. CORE ENGINE FUNCTIONS
def apply_event(event, target_assets):
    print(f"\n[!] STRATEGIC EVENT TRIGGERED: {event.name}")
    for asset in target_assets:
        asset.resilience -= (event.severity * 15)
        if asset.resilience <= 0:
            asset.resilience = 0
            asset.status = "Offline"

def update_dependencies():
    for asset in country.assets:
        if asset.resilience <= 0:
            asset.status = "Offline"
            continue
        if not asset.dependencies:
            asset.status = "Operational"
            continue
        offline_deps = sum(1 for dep in asset.dependencies if dep.status == "Offline")
        if offline_deps == 0:
            asset.status = "Operational"
        elif offline_deps >= len(asset.dependencies):
            asset.status = "Offline"
        else:
            asset.status = "Degraded"

def run_day():
    update_dependencies()
    # ... [Rest of your update logic: update_tsmc_water, update_resources, update_outcomes]
    country.gdp_loss = 100 - country.calculate_gdp()
    country.gdp_history.append(country.gdp_loss)
