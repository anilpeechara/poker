import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# 1. Page Configuration for Mobile
st.set_page_config(
    page_title="Poker Tracker",
    page_icon="🃏",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS to make buttons and inputs larger for thumbs
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3em; font-size: 1.1em; border-radius: 10px; }
    .stNumberInput input { font-size: 1.2em !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Session Initialization
if 'players' not in st.session_state:
    st.session_state.players = []
if 'buy_in_val' not in st.session_state:
    st.session_state.buy_in_val = 20

# 3. Header & Date
st.title("🃏 Poker Night")
game_date = st.date_input("Game Date", datetime.now())
formatted_date = game_date.strftime("%b %d, %Y")

# Buy-in Setting
st.session_state.buy_in_val = st.number_input("Standard Buy-in ($)", value=st.session_state.buy_in_val, step=5)

# 4. Add Player (Mobile Optimized)
with st.container():
    name = st.text_input("Player Name:", placeholder="Who is playing?", label_visibility="collapsed")
    if st.button("➕ Add Player") and name:
        if name not in [p['name'] for p in st.session_state.players]:
            st.session_state.players.append({'name': name, 'buys': 1, 'chips': 0.0})
            st.rerun()

# 5. Game Log (Card-style for mobile)
if st.session_state.players:
    st.subheader("Players & Chips")
    updated_data = []
    
    for i, p in enumerate(st.session_state.players):
        # Using Expanders as "Cards"
        with st.expander(f"👤 {p['name'].upper()}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                p['buys'] = st.number_input(f"Buy-ins", min_value=1, value=p['buys'], key=f"buys_{i}")
            with col2:
                p['chips'] = st.number_input(f"End Chips ($)", min_value=0.0, value=float(p['chips']), key=f"chips_{i}", step=5.0)
            
            if st.button(f"🗑️ Remove {p['name']}", key=f"del_{i}"):
                st.session_state.players.pop(i)
                st.rerun()
        
        total_in = p['buys'] * st.session_state.buy_in_val
        net = p['chips'] - total_in
        updated_data.append({"Player": p['name'], "In": total_in, "Out": p['chips'], "Net": net})

    # 6. Summary & Totals
    df = pd.DataFrame(updated_data)
    st.divider()
    
    total_in_pot = df["In"].sum()
    total_out_pot = df["Out"].sum()
    diff = total_out_pot - total_in_pot

    # Metrics Layout
    m1, m2 = st.columns(2)
    m1.metric("Total Pot", f"${total_in_pot}")
    m2.metric("Balance", f"${diff}", delta=diff, delta_color="normal" if diff == 0 else "inverse")

    if diff != 0:
        st.error(f"⚠️ Pot mismatch: ${diff}")
    else:
        st.success("✅ Books are balanced")

    # 7. Share Logic
    st.subheader("Share Results")
    
    msg = f"♠️ POKER: {formatted_date} ♣️\nPot: ${total_in_pot}\n"
    msg += "------------------\n"
    for _, row in df.iterrows():
        status = "📈 +" if row['Net'] > 0 else "📉 "
        msg += f"{row['Player']}: {status}${row['Net']}\n"
    
    encoded_msg = urllib.parse.quote(msg)
    
    # WhatsApp & Email buttons
    st.link_button("📲 Send to WhatsApp Group", f"https://wa.me/?text={encoded_msg}")
    st.link_button("✉️ Send Results via Email", f"mailto:?subject=Poker%20Results%20{formatted_date}&body={encoded_msg}")

    if st.button("Reset Game"):
        st.session_state.players = []
        st.rerun()
