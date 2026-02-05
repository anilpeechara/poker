import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="Poker Tracker", page_icon="🃏", layout="centered")

# Custom CSS for mobile buttons and inputs
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.5em; border-radius: 12px; font-weight: bold; }
    .stNumberInput input { font-size: 1.3em !important; }
    div[data-testid="stExpander"] { border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Session Initialization
if 'players' not in st.session_state:
    st.session_state.players = []

# 3. Header & Date
st.title("🃏 Poker Night Log")
game_date = st.date_input("Game Date", datetime.now())
formatted_date = game_date.strftime("%B %d, %Y")
buy_in_val = st.number_input("Buy-in Amount ($)", value=20, step=5)

# 4. Add Player (Clears on Submit)
with st.form("add_player_form", clear_on_submit=True):
    new_name = st.text_input("Enter Player Name", placeholder="e.g., Mike")
    submit = st.form_submit_button("➕ Add to Game")
    if submit and new_name:
        if new_name not in [p['name'] for p in st.session_state.players]:
            st.session_state.players.append({'name': new_name, 'buys': 1, 'chips': 0})
            st.rerun()

# 5. Game Tracking
if st.session_state.players:
    st.subheader("Player Inputs")
    summary_data = []
    
    for i, p in enumerate(st.session_state.players):
        with st.expander(f"👤 {p['name'].upper()}", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                p['buys'] = st.number_input("Buy-ins", min_value=1, value=p['buys'], key=f"b_{i}")
            with c2:
                # Enforcing $5 denominations and NO decimals
                p['chips'] = st.number_input("End Chips ($)", min_value=0, value=int(p['chips']), 
                                           step=5, format="%d", key=f"c_{i}")
            
            if st.button(f"🗑️ Remove {p['name']}", key=f"del_{i}"):
                st.session_state.players.pop(i)
                st.rerun()
        
        cost = p['buys'] * buy_in_val
        profit = p['chips'] - cost
        summary_data.append({"Player": p['name'], "In": cost, "Out": p['chips'], "Net": profit})

    df = pd.DataFrame(summary_data)

    # 6. Totals & Balance Check
    st.divider()
    pot_in = df["In"].sum()
    pot_out = df["Out"].sum()
    balance = pot_out - pot_in

    m1, m2 = st.columns(2)
    m1.metric("Total Pot", f"${pot_in}")
    m2.metric("Balance Check", f"${balance}", delta=balance, delta_color="normal" if balance == 0 else "inverse")

    if balance != 0:
        st.warning(f"⚠️ Warning: The table is off by ${balance}")
    else:
        st.success("✅ The books are perfectly balanced!")

    # 7. Visual Graph (Performance)
    st.subheader("Profit / Loss Chart")
    if not df.empty:
        # Simple bar chart: Colors usually default to blue, but it clearly shows +/-
        st.bar_chart(df.set_index("Player")["Net"])

    # 8. Share Results
    st.subheader("Share with Group")
    msg = f"♠️ POKER: {formatted_date} ♣️\nPot: ${pot_in}\n"
    msg += "------------------\n"
    for _, row in df.iterrows():
        emoji = "📈 +" if row['Net'] >= 0 else "📉 "
        msg += f"{row['Player']}: {emoji}${row['Net']}\n"
    
    encoded_msg = urllib.parse.quote(msg)
    
    st.link_button("📲 Send to WhatsApp Group", f"https://wa.me/?text={encoded_msg}")
    st.link_button("✉️ Send via Email", f"mailto:?subject=Poker%20Results%20{formatted_date}&body={encoded_msg}")

    if st.button("Reset Session"):
        st.session_state.players = []
        st.rerun()
