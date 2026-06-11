class Asset:
    def __init__(self, name, sector, resilience=100, repair_days=5):
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

    def add_asset(self, asset):
        self.assets.append(asset)

# ---------------------------------------------------
# CREATE COUNTRY
# ---------------------------------------------------
country = Country()

# POWER
nuclear_plant = Asset("Nuclear Plant", "Power")
coal_plant = Asset("Coal Plant", "Power")
gas_plant = Asset("Gas Plant", "Power")
transformer = Asset("Transformer", "Power")
substation = Asset("Substation", "Power")

# WATER
reservoir = Asset("Reservoir", "Water")
treatment_plant = Asset("Treatment Plant", "Water")
pump_station = Asset("Pump Station", "Water")

# TRANSPORT
port = Asset("Port", "Transport")
airport = Asset("Airport", "Transport")
rail_hub = Asset("Rail Hub", "Transport")
highway_junction = Asset("Highway Junction", "Transport")

# MILITARY
radar_station = Asset("Radar Station", "Military")
air_base = Asset("Air Base", "Military")
naval_base = Asset("Naval Base", "Military")
army_brigade = Asset("Army Brigade", "Military")

# ECONOMY
bank = Asset("Bank", "Finance")
stock_exchange = Asset("Stock Exchange", "Finance")
tsmc = Asset("TSMC Fab", "Industry")

# SOCIETY
hospital = Asset("Hospital", "Health")
supermarket = Asset("Supermarket", "Food")
population_centre = Asset("Population Centre", "Society")

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
# EVENTS
# ---------------------------------------------------
TYPHOON = Event("Typhoon", 8)
MISSILE_STRIKE = Event("Missile Strike", 10)

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
    report()

def run_simulation(days):
    for day in range(1, days + 1):
        country.day = day
        run_day()

# ---------------------------------------------------
# EXECUTION
# ---------------------------------------------------

