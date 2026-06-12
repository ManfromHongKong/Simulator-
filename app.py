import streamlit as st
import pandas as pd
from main import (country, run_day, trigger_random_event, 
                  trigger_specific_event, event_pool)

# --- 1. INITIALIZATION (Required for the log to work) ---
if 'event_log' not in st.session_state:
    st.session_state.event_log = []

# 2. Set the Title
st.title("National Resilience Simulator")

# --- 3. INTEGRATED CONTROL PANEL ---
st.header("Simulation Control")

# Random Trigger
if st.button("Trigger Random Event"):
    event = trigger_random_event()
    run_day()
    # Add to log
    st.session_state.event_log.append(f"Day {country.day}: {event.name}")
    st.success(f"Event Triggered: {event.name} ({event.cause})")
    st.rerun()

# Scenario Selector
options = [f"{i+1}: {e.name} ({e.cause})" for i, e in enumerate(event_pool)]
selected_option = st.selectbox("Or select a specific scenario:", options)

if st.button("Run Selected Scenario"):
    index = int(selected_option.split(":")[0]) - 1
    event = trigger_specific_event(index)
    run_day()
    # Add to log
    st.session_state.event_log.append(f"Day {country.day}: {event.name}")
    st.warning(f"Simulating: {event.name}")
    st.rerun()

st.divider()

# 4. Add a button to progress the simulation
if st.button("Run Next Day"):
    country.day += 1
    run_day()
    st.rerun()

# 5. Display the data
st.subheader(f"Current Status - Day {country.day}")
data = [{"Asset": a.name, "Status": a.status, "Resilience": a.resilience} for a in country.assets]
st.table(pd.DataFrame(data))

# 6. Display key metrics
col1, col2 = st.columns(2)
col1.metric("GDP Loss", f"{country.gdp_loss}%")
col2.metric("Power Outage (People)", f"{country.population_without_power:,}")

# 7. EVENT HISTORY (The bonus feature)
st.subheader("Event History")
for log in reversed(st.session_state.event_log):
    st.text(log)
