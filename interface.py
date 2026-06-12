import streamlit as st
from main import Simulator # Import your engine here

# Initialize your engine
sim = Simulator()

st.title("National Resilience Engine")

# Sidebar for triggers
st.sidebar.header("Crisis Triggers")
event = st.sidebar.selectbox("Event", ["CCG Quarantine", "UNGA Vote", "DF-26"])
intensity = st.sidebar.slider("Intensity", 1, 10, 1)

# Logic execution
if st.sidebar.button("Execute Trigger"):
    # Call your existing logic from main.py
    results = sim.trigger_random_event(event, intensity) 
    st.write(results)
    st.success("Simulation Updated")
