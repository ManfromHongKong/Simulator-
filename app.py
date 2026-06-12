import streamlit as st
import pandas as pd
# Import your new engine components
from main import (country, run_day, trigger_random_event, 
                  trigger_specific_event, event_pool)

# 1. Set the Title
st.title("National Resilience Simulator")

# --- NEW: INTEGRATED CONTROL PANEL ---
st.header("Simulation Control")

# Random Trigger
if st.button("Trigger Random Event"):
    event = trigger_random_event()
    run_day()
    st.success(f"Event Triggered: {event.name} ({event.cause})")
    st.rerun()

# Scenario Selector
options = [f"{i+1}: {e.name} ({e.cause})" for i, e in enumerate(event_pool)]
selected_option = st.selectbox("Or select a specific scenario:", options)

if st.button("Run Selected Scenario"):
    index = int(selected_option.split(":")[0]) - 1
    trigger_specific_event(index)
    run_day()
    st.warning(f"Simulating: {event_pool[index].name}")
    st.rerun()

st.divider()

# 3. Add a button to progress the simulation
if st.button("Run Next Day"):
    country.day += 1
    run_day()
    st.rerun()

# 4. Create a Dataframe for the table
data = [{"Asset": a.name, "Status": a.status, "Resilience": a.resilience} for a in country.assets]

# 5. Display the data as a table
st.subheader(f"Current Status - Day {country.day}")
st.table(pd.DataFrame(data))

# 6. Display key metrics
col1, col2 = st.columns(2)
col1.metric("GDP Loss", f"{country.gdp_loss}%")
col2.metric("Power Outage (People)", f"{country.population_without_power:,}")
