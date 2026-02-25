import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- Setup the Page ---
st.set_page_config(page_title="Sentinel Overmind Dashboard", layout="wide")
st.title("🏛️ Sentinel Boardroom: Synthetic Consensus Engine")

# --- Board Members (Simulated Data for Dashboard) ---
agents = {
    "Alpha (Technician)": {"Bull": 0.08, "Base": 0.02, "Bear": -0.05, "Prob": [0.3, 0.5, 0.2]},
    "Beta (Historian)": {"Bull": 0.04, "Base": 0.01, "Bear": -0.02, "Prob": [0.2, 0.6, 0.2]},
    "Gamma (Philosopher)": {"Bull": 0.12, "Base": 0.03, "Bear": -0.10, "Prob": [0.4, 0.3, 0.3]}
}

# --- Sidebar: Market Controls ---
st.sidebar.header("Command Center")
target_asset = st.sidebar.selectbox("Focus Asset", ["NVDA", "AAPL", "BTC-USD", "SPY"])
run_analysis = st.sidebar.button("Initiate Consensus Cycle")

if run_analysis:
    cols = st.columns(len(agents))
    
    # --- Step 1: Individual Agent Visualizations ---
    for i, (name, views) in enumerate(agents.items()):
        with cols[i]:
            st.subheader(name)
            
            # Create a bar chart of the 3 possibilities
            fig = go.Figure(data=[
                go.Bar(name='Scenarios', x=['Bear', 'Base', 'Bull'], 
                       y=[views['Bear'], views['Base'], views['Bull']],
                       marker_color=['#ef5350', '#ffa726', '#66bb6a'])
            ])
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            st.write(f"**Confidence:** {max(views['Prob'])*100}% in Base Case")

    # --- Step 2: The Chairperson's Analysis of Possibilities ---
    st.divider()
    st.header("🧠 Chairperson's Meta-Analysis")
    
    # Calculate Expected Value (Weighted Probability)
    all_evs = []
    for name, views in agents.items():
        ev = (views['Bull'] * views['Prob'][0]) + (views['Base'] * views['Prob'][1]) + (views['Bear'] * views['Prob'][2])
        all_evs.append(ev)
    
    final_consensus = np.mean(all_evs)
    conviction_score = 1 - np.std(all_evs) # Higher when agents agree
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Synthesized Target", f"{final_consensus:+.2%}")
    m2.metric("Consensus Conviction", f"{conviction_score:.2f}/1.00")
    m3.metric("Market State", "STABLE" if final_consensus > 0 else "CAUTION")

    # --- Step 3: Probability Distribution Visualization ---
    st.subheader("Global Probability Matrix")
    # This chart shows the 'Analysis of Opinions' – overlapping density of all possible futures
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['Alpha', 'Beta', 'Gamma'])
    st.line_chart(chart_data)
    
    st.success(f"Directive Issued: {'ACCUMULATE' if final_consensus > 0.01 else 'HOLD'}")

else:
    st.info("System Standby. Initiate a 'Consensus Cycle' from the sidebar to wake the agents.")
