import streamlit as st
import pandas as pd

st.set_page_config(page_title="Poker Log", layout="centered")
st.title("🃏 Poker Night Tracker")

# Sidebar settings
buy_in_val = st.sidebar.number_input("Standard Buy-in ($)", value=20)

if 'players' not in st.session_state:
    st.session_state.players = []

# 1. Add Players
name = st.text_input("Enter Player Name:")
if st.button("Add Player") and name:
    if name not in [p['name'] for p in st.session_state.players]:
        st.session_state.players.append({'name': name, 'buys': 1, 'chips': 0.0})

# 2. Update Data
if st.session_state.players:
    st.subheader("Live Game Log")
    updated_data = []
    
    for i, p in enumerate(st.session_state.players):
        cols = st.columns([2, 2, 2])
        with cols[0]:
            st.write(f"**{p['name']}**")
        with cols[1]:
            p['buys'] = st.number_input("Buy-ins", min_value=1, value=p['buys'], key=f"b{i}")
        with cols[2]:
            p['chips'] = st.number_input("End Chips", min_value=0.0, value=p['chips'], key=f"c{i}")
        
        total_in = p['buys'] * buy_in_val
        net = p['chips'] - total_in
        updated_data.append({
            "Player": p['name'], "Total In ($)": total_in, 
            "End Chips ($)": p['chips'], "Net ($)": net
        })

    # 3. Final Calculations
    df = pd.DataFrame(updated_data)
    st.divider()
    st.dataframe(df, use_container_width=True)

    total_in_pot = df["Total In ($)"].sum()
    total_out_pot = df["End Chips ($)"].sum()
    diff = total_out_pot - total_in_pot

    c1, c2 = st.columns(2)
    c1.metric("Total Pot", f"${total_in_pot}")
    c2.metric("Balance Check", f"${diff}", delta_color="normal" if diff == 0 else "inverse")

    if diff != 0:
        st.error(f"⚠️ Error: The pot is off by ${diff}. Check the chip counts!")
    else:
        st.success("✅ The books are balanced!")
