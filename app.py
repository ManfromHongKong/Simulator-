import streamlit as st
import main

# --- UI Setup ---
st.sidebar.header("Crisis Triggers")
event = st.sidebar.selectbox("Select Trigger Event", ["CCG Quarantine", "UNGA Vote", "DF-26"])
intensity = st.sidebar.slider("Select Intensity (1-10)", 1, 10, 1)

# --- Button Logic ---
if st.sidebar.button("Apply Crisis Scenario"):
    main.trigger_random_event(event, intensity)
    st.success(f"Simulation Updated for {event}")
    st.rerun() # Refresh to update the screen
