import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="Poker Tracker", layout="centered")

# 1. Header & Date Selection
st.title("🃏 Poker Night Tracker")
game_date = st.date_input("Game Date", datetime.now())
formatted_date = game_date.strftime("%B %d, %Y")

# Sidebar settings
buy_in_val = st.sidebar.number_input("Standard Buy-in ($)", value=20)

if 'players' not in st.session_state:
    st.session_state.players = []

# 2. Add Player UI
with st.container():
    col_add, col_btn = st.columns([3, 1])
    with col_add:
        name = st.text_input("Player Name:", placeholder="Enter name...", label_visibility="collapsed")
    with col_btn:
        if st.button("Add Player", use_container_width=True) and name:
            if name not in [p['name'] for p in st.session_state.players]:
                st.session_state.players.append({'name': name, 'buys': 1, 'chips': 0.0})
                st.rerun()

# 3. Game Log
if st.session_state.players:
    st.subheader(f"Game Log: {formatted_date}")
    updated_data = []
    
    for i, p in enumerate(st.session_state.players):
        with st.expander(f"👤 {p['name']}", expanded=True):
            cols = st.columns([2, 2, 1])
            with cols[0]:
                p['buys'] = st.number_input("Buy-ins", min_value=1, value=p['buys'], key=f"b{i}")
            with cols[1]:
                p['chips'] = st.number_input("End Chips ($)", min_value=0.0, value=float(p['chips']), key=f"c{i}")
            with cols[2]:
                st.write(" ") 
                if st.button("🗑️", key=f"del{i}"):
                    st.session_state.players.pop(i)
                    st.rerun()
        
        total_in = p['buys'] * buy_in_val
        net = p['chips'] - total_in
        updated_data.append({"Player": p['name'], "In": total_in, "Out": p['chips'], "Net": net})

    df = pd.DataFrame(updated_data)
    
    # 4. Totals & Balance Check
    st.divider()
    total_in_pot = df["In"].sum()
    total_out_pot = df["Out"].sum()
    diff = total_out_pot - total_in_pot

    c1, c2 = st.columns(2)
    c1.metric("Total Pot", f"${total_in_pot}")
    c2.metric("Balance Check", f"${diff}", delta_color="normal" if diff == 0 else "inverse")

    if diff != 0:
        st.warning(f"⚠️ Pot is off by ${diff}. Check chip counts!")

    # 5. Sharing Logic
    st.subheader("Share Summary")
    
    # Constructing the Message
    summary_msg = f"♠️ POKER RESULTS: {formatted_date} ♣️\n"
    summary_msg += f"Total Pot: ${total_in_pot}\n"
    summary_msg += "--------------------------\n"
    for _, row in df.iterrows():
        prefix = "📈 +" if row['Net'] > 0 else "📉 "
        summary_msg += f"{row['Player']}: {prefix}${row['Net']}\n"
    
    encoded_msg = urllib.parse.quote(summary_msg)
    
    col_wa, col_mail = st.columns(2)
    with col_wa:
        wa_url = f"https://wa.me/?text={encoded_msg}"
        st.link_button("📲 WhatsApp Group", wa_url, use_container_width=True)
    with col_mail:
        mail_url = f"mailto:?subject=Poker%20Results%20-{formatted_date}&body={encoded_msg}"
        st.link_button("✉️ Send Email", mail_url, use_container_width=True)

    if st.button("Show Raw Text"):
        st.code(summary_msg)
