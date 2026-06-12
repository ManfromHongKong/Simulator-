import streamlit as st
import main  # Imports your script

st.title("National Resilience Engine")

# Sidebar for triggers
st.sidebar.header("Crisis Triggers")
event = st.sidebar.selectbox("Event", ["CCG Quarantine", "UNGA Vote", "DF-26"])
intensity = st.sidebar.slider("Intensity", 1, 10, 1)

if st.sidebar.button("Execute Trigger"):
    # If you have a function named trigger_random_event in main.py, call it directly:
    main.trigger_random_event(event, intensity) 
    
    st.write("Trigger applied.")
    st.success("Simulation Updated")
    
    # Show current stats
    st.write(f"Chip Output: {main.country.chip_output}%")
    st.write(f"Port Capacity: {main.country.port_capacity}%")
