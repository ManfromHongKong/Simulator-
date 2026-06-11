import streamlit as st
import pandas as pd
# This imports your simulation engine
from main import country, apply_event, MISSILE_STRIKE, run_day, all_assets

# 1. Set the Title
st.title("National Resilience Simulator")

# 2. Add an interactive button
if st.button("Trigger Missile Strike"):
    # Trigger the event defined in your main.py
    apply_event(MISSILE_STRIKE, [all_assets[0], all_assets[1], all_assets[2]])
    # Update logic after the event
    run_day()

# 3. Add a button to progress the simulation
if st.button("Run Next Day"):
    country.day += 1
    run_day()

# 4. Create a Dataframe for the table
# This turns your 'Asset' objects into a format Streamlit can draw
data = []
for asset in country.assets:
    data.append({
        "Asset": asset.name,
        "Status": asset.status,
        "Resilience": asset.resilience
    })

# 5. Display the data as a table
st.subheader(f"Current Status - Day {country.day}")
st.table(pd.DataFrame(data))

# 6. Display key metrics
col1, col2 = st.columns(2)
col1.metric("GDP Loss", f"{country.gdp_loss}%")
col2.metric("Power Outage (People)", f"{country.population_without_power:,}")
