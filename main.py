class Asset:
    def __init__(self, name, sector, resilience=100, repair_days=5, contribution=10):
        self.name = name
        self.sector = sector
        self.resilience = resilience
        self.repair_days = repair_days
        self.status = "Operational"
        self.dependencies = []
        self.dependents = []
        self.days_offline = 0
        self.resources = {}
        # TSMC specific
        self.water_reserve_days = None
        # Added for GDP calculation
        self.contribution = contribution

    def add_dependency(self, asset):
        self.dependencies.append(asset)
        asset.dependents.append(self)

    def __str__(self):
        return f"{self.name:<20} | {self.status:<11} | Resilience: {self.resilience}"

class Event:
    def __init__(self, name, severity):
        self.name = name
        self.severity = severity

class Country:
    def __init__(self):
        self.assets = []
        self.day = 0
        self.population_without_power = 0
        self.population_without_water = 0
        self.hospital_capacity = 100
        self.port_capacity = 100
        self.chip_output = 100
        self.gdp_loss = 0

    def calculate_gdp(self):
        # Calculate sum of contributions for all operational assets
        # Only assets with status "Operational" contribute to GDP
        total_gdp = sum(asset.contribution for asset in self.assets if asset.status == "Operational")
        return total_gdp

    def add_asset(self, asset):
        self.assets.append(asset)

# ---------------------------------------------------
# CREATE COUNTRY
# ---------------------------------------------------
# ---------------------------------------------------
# CREATE COUNTRY AND ASSETS
# ---------------------------------------------------
country = Country()

# POWER (Weight 10-20)
nuclear_plant = Asset("Nuclear Plant", "Power", 100, 5, 20)
coal_plant = Asset("Coal Plant", "Power", 100, 5, 15)
gas_plant = Asset("Gas Plant", "Power", 100, 5, 15)
transformer = Asset("Transformer", "Power", 100, 5, 10)
substation = Asset("Substation", "Power", 100, 5, 10)

# WATER (Weight 5)
reservoir = Asset("Reservoir", "Water", 100, 5, 5)
treatment_plant = Asset("Treatment Plant", "Water", 100, 5, 5)
pump_station = Asset("Pump Station", "Water", 100, 5, 5)

# TRANSPORT (Weight 5-10)
port = Asset("Port", "Transport", 100, 5, 10)
airport = Asset("Airport", "Transport", 100, 5, 10)
rail_hub = Asset("Rail Hub", "Transport", 100, 5, 5)
highway_junction = Asset("Highway Junction", "Transport", 100, 5, 5)

# MILITARY (Weight 5-10)
radar_station = Asset("Radar Station", "Military", 100, 5, 5)
air_base = Asset("Air Base", "Military", 100, 5, 10)
naval_base = Asset("Naval Base", "Military", 100, 5, 10)
army_brigade = Asset("Army Brigade", "Military", 100, 5, 10)

# ECONOMY (Weight 15-30)
bank = Asset("Bank", "Finance", 100, 5, 15)
stock_exchange = Asset("Stock Exchange", "Finance", 100, 5, 15)
tsmc = Asset("TSMC Fab", "Industry", 100, 5, 30)

# SOCIETY (Weight 5)
hospital = Asset("Hospital", "Health", 100, 5, 5)
supermarket = Asset("Supermarket", "Food", 100, 5, 5)
population_centre = Asset("Population Centre", "Society", 100, 5, 5)

all_assets = [
    nuclear_plant, coal_plant, gas_plant, transformer, substation,
    reservoir, treatment_plant, pump_station,
    port, airport, rail_hub, highway_junction,
    radar_station, air_base, naval_base, army_brigade,
    bank, stock_exchange, tsmc,
    hospital, supermarket, population_centre
]

for asset in all_assets:
    country.add_asset(asset)
# ---------------------------------------------------
# RESOURCES & RESERVES
# ---------------------------------------------------
tsmc.water_reserve_days = 3
hospital.resources = {"diesel_days": 7}
radar_station.resources = {"fuel_days": 10}

# ---------------------------------------------------
# DEPENDENCIES
# ---------------------------------------------------
# Power chain
transformer.add_dependency(nuclear_plant)
transformer.add_dependency(coal_plant)
transformer.add_dependency(gas_plant)
substation.add_dependency(transformer)

# Water chain
treatment_plant.add_dependency(substation)
reservoir.add_dependency(substation)
pump_station.add_dependency(treatment_plant)

# Transport
port.add_dependency(substation)
airport.add_dependency(substation)
rail_hub.add_dependency(substation)
highway_junction.add_dependency(substation)

# Military
radar_station.add_dependency(substation)
air_base.add_dependency(substation)
naval_base.add_dependency(substation)
army_brigade.add_dependency(substation)

# Economy
bank.add_dependency(substation)
stock_exchange.add_dependency(bank)
tsmc.add_dependency(substation)
tsmc.add_dependency(pump_station)

# Society
hospital.add_dependency(substation)
supermarket.add_dependency(substation)
population_centre.add_dependency(substation)

# ---------------------------------------------------
# ---------------------------------------------------
# EVENT POOL (The "Causality Engine")
# ---------------------------------------------------
event_pool = [
    Event("Cyber-Sabotage", 3, "Technical Glitch", "Precision"),
    Event("Rogue Operator Strike", 8, "Rogue PLA Operative", "Precision"),
    Event("Accidental Escalation", 10, "Political Incident", "Saturation"),
    Event("Preemptive Strike", 12, "Preemptive Military Strategy", "Saturation"),
    Event("Demonstrative Strike", 5, "Political Signaling", "Precision")
]

# ---------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------
def damage_asset(asset, amount):
    asset.resilience -= amount
    if asset.resilience <= 0:
        asset.resilience = 0
        asset.status = "Offline"

def apply_event(event, target_assets):
    print(f"\n[!] STRATEGIC EVENT TRIGGERED: {event.name}")
    for asset in target_assets:
        damage_asset(asset, event.severity * 15)
        print(f"Direct structural impact on {asset.name}. Resilience dropped to {asset.resilience}%")

def update_dependencies():
    for asset in country.assets:
        # If physically destroyed or structural failure, it cannot recover via dependencies
        if asset.resilience <= 0:
            asset.status = "Offline"
            continue
            
        if not asset.dependencies:
            asset.status = "Operational"
            continue

        offline_dependencies = sum(1 for dep in asset.dependencies if dep.status == "Offline")
        
        if offline_dependencies == 0:
            asset.status = "Operational"
        elif offline_dependencies >= len(asset.dependencies):
            # Special bypass for TSMC water reserve rule
            if asset.name == "TSMC Fab" and tsmc.water_reserve_days > 0:
                continue
            asset.status = "Offline"
        else:
            asset.status = "Degraded"

def update_tsmc_water():
    # TSMC depends on substation (Power) and pump_station (Water)
    water_offline = (pump_station.status == "Offline")
    
    if water_offline and tsmc.resilience > 0:
        if tsmc.water_reserve_days > 0:
            tsmc.status = f"Reserves ({tsmc.water_reserve_days}D)"
            tsmc.water_reserve_days -= 1
        else:
            tsmc.status = "Offline"
            print("[!] TSMC Alert: Water reserves completely exhausted. Production halted.")
    elif not water_offline and tsmc.resilience > 0 and substation.status != "Offline":
        tsmc.status = "Operational"

def update_resources():
    for asset in country.assets:
        if asset.status != "Operational" or not asset.resources:
            continue
        for resource_name in list(asset.resources.keys()):
            asset.resources[resource_name] -= 1
            if asset.resources[resource_name] <= 0:
                asset.status = "Offline"
                print(f"[!] Logistics Alert: {asset.name} exhausted all {resource_name} reserves.")

def update_outcomes():
    if substation.status == "Offline":
        country.population_without_power = 23000000
    else:
        country.population_without_power = 0

    if pump_station.status == "Offline":
        country.population_without_water = 5000000
    else:
        country.population_without_water = 0

    country.chip_output = 100 if tsmc.status == "Operational" else (50 if "Reserves" in tsmc.status else 0)
    country.port_capacity = 100 if port.status == "Operational" else (50 if port.status == "Degraded" else 0)
    country.gdp_loss = 100 - country.chip_output

def report():
    print("\n" + "=" * 65)
    print(f"NATIONAL RESILIENCE SIMULATOR - REPORT DAY {country.day}")
    print("=" * 65)
    for asset in country.assets:
        print(asset)
    print("\nSYSTEMIC IMPACT METRICS")
    print("-" * 65)
    print(f"Population Affected (Power Outage): {country.population_without_power:,}")
    print(f"Population Affected (Water Cut):   {country.population_without_water:,}")
    print(f"Critical Semiconductor Output:      {country.chip_output}%")
    print(f"Operational Seaport Capacity:       {country.port_capacity}%")
    print(f"Projected Immediate GDP Shock:      {country.gdp_loss}%")

def run_day():
    update_dependencies()
    update_tsmc_water()
    update_resources()
    update_outcomes()
    
    # Add this line to update the GDP loss at the end of every day:
    country.gdp_loss = 100 - country.calculate_gdp()
    
    report()

# ---------------------------------------------------
# EXECUTION
# ---------------------------------------------------

