import json
import pandas as pd
import streamlit as st

from scenarios import get_scenario, SCENARIO_NAMES
from agent import EnergyDetectiveAgent
from energy_tools import calculate_energy_report

st.set_page_config(
    page_title="Energy Detective AI",
    page_icon="⚡",
    layout="wide",
)

st.markdown("""
<style>
.stApp { background: linear-gradient(145deg, #0b1220, #101d30); color: #edf6ff; }
.block-container { max-width: 1450px; padding-top: 2rem; }
.hero { padding: 28px; border-radius: 20px; background: linear-gradient(115deg, #123047, #087e83); margin-bottom: 22px; border: 1px solid #2c7180; }
.hero h1 { color: white; font-size: 40px; }
.hero p { color: #d7f5f4; font-size: 17px; }
div[data-testid="stMetric"] { background: #142438; border: 1px solid #29445b; padding: 14px; border-radius: 14px; }
div[data-testid="stMetricValue"] { color: #56e0bd; }
section[data-testid="stSidebar"] { background: #101a2b; }
</style>
""", unsafe_allow_html=True)

if "investigation" not in st.session_state:
    st.session_state.investigation = None
if "run_count" not in st.session_state:
    st.session_state.run_count = 0

st.markdown("""
<div class="hero">
  <h1>⚡ ENERGY DETECTIVE AI</h1>
  <p>Your smart-home energy investigator: detect waste, optimize appliance schedules, and explore savings.</p>
  <p>INVESTIGATE &nbsp; • &nbsp; OPTIMIZE &nbsp; • &nbsp; SAVE</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🎛️ Control Center")
    st.caption("Configure a simulated smart home.")
    scenario_name = st.selectbox("Choose an energy scenario", SCENARIO_NAMES, index=1)
    peak_multiplier = st.slider("Peak electricity price multiplier", 1.0, 5.0, 3.0, 0.5)
    solar_capacity = st.slider("Solar generation capacity (kW)", 0.0, 6.0, 3.0, 0.5)
    grid_limit = st.slider("Maximum grid load (kW)", 4.0, 10.0, 7.0, 0.5)
    carbon_weight = st.slider("Carbon reduction priority", 0.0, 1.0, 0.3, 0.1)
    st.divider()
    run_button = st.button("🔎 Run Energy Investigation", use_container_width=True, type="primary")
    st.caption("Educational simulation only. No real appliances are controlled.")

scenario = get_scenario(
    scenario_name=scenario_name,
    peak_multiplier=peak_multiplier,
    solar_capacity=solar_capacity,
    grid_limit=grid_limit,
    carbon_weight=carbon_weight,
)

if run_button:
    with st.spinner("Detective AI is investigating energy usage..."):
        agent = EnergyDetectiveAgent(scenario)
        result = agent.investigate()
        report = calculate_energy_report(scenario, result)
        st.session_state.investigation = {
            "scenario": scenario,
            "result": result,
            "report": report,
            "name": scenario_name,
        }
        st.session_state.run_count += 1

investigation = st.session_state.investigation
if investigation is None:
    st.info("👋 Welcome, Detective! Choose a scenario in the sidebar and click **Run Energy Investigation**.")
    st.subheader("🧠 What this agent does")
    c1, c2, c3 = st.columns(3)
    c1.markdown("### 💸 Detect energy waste\nFind appliances running during expensive hours.")
    c2.markdown("### 🗓️ Plan schedules\nMove flexible jobs to more affordable time slots.")
    c3.markdown("### 🌱 Reduce emissions\nEstimate grid emissions and explore lower-carbon schedules.")
    st.subheader("🏠 Simulated home appliances")
    st.dataframe(pd.DataFrame([
        {"Appliance": "Electric vehicle", "Power": "3.3 kW"},
        {"Appliance": "Water heater", "Power": "2.0 kW"},
        {"Appliance": "Air conditioner", "Power": "1.5 kW"},
        {"Appliance": "Dishwasher", "Power": "1.2 kW"},
        {"Appliance": "Washing machine", "Power": "0.8 kW"},
        {"Appliance": "Clothes dryer", "Power": "2.5 kW"},
    ]), use_container_width=True, hide_index=True)
else:
    scenario = investigation["scenario"]
    result = investigation["result"]
    report = investigation["report"]

    st.subheader("🕵️ Investigation Results")
    original_cost = report["original"]["total_cost"]
    optimized_cost = report["optimized"]["total_cost"]
    savings = original_cost - optimized_cost
    savings_percent = (savings / original_cost * 100) if original_cost > 0 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Original estimated bill", f"${original_cost:.2f}")
    m2.metric("Optimized estimated bill", f"${optimized_cost:.2f}")
    m3.metric("Estimated savings", f"${savings:.2f}", delta=f"{savings_percent:.1f}%")
    m4.metric("Agent decisions", str(len(result["decisions"])))
    st.caption("All figures are simulated estimates, not guaranteed real-world savings.")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Energy Dashboard", "🗓️ Smart Schedule", "🧠 Agent Investigation", "📥 Export Results"])
    with tab1:
        st.subheader("Hourly energy consumption")
        hourly = pd.DataFrame(report["hourly_comparison"])
        if not hourly.empty:
            st.line_chart(hourly.set_index("hour")[["original_load", "optimized_load"]])
            st.subheader("Electricity price by hour")
            st.bar_chart(hourly.set_index("hour")[["price"]])
            a, b, c = st.columns(3)
            a.metric("Original energy", f'{report["original"]["energy_kwh"]:.2f} kWh')
            b.metric("Optimized energy", f'{report["optimized"]["energy_kwh"]:.2f} kWh')
            c.metric("Optimized peak grid load", f'{report["optimized"]["peak_kw"]:.2f} kW')
    with tab2:
        st.subheader("Appliance scheduling plan")
        st.dataframe(pd.DataFrame(result["schedule"]), use_container_width=True, hide_index=True)
        if result["constraint_violations"]:
            st.warning("Some constraints need review.")
            for violation in result["constraint_violations"]:
                st.write(f"- {violation}")
        else:
            st.success("The proposed schedule passed the configured constraint checks.")
    with tab3:
        st.subheader("🔍 Detective's decision log")
        st.write("This educational agent follows a transparent rule-based workflow.")
        for index, decision in enumerate(result["decisions"], start=1):
            with st.expander(f"Step {index}: {decision['title']}", expanded=index == 1):
                st.write(decision["details"])
        st.subheader("Final recommendation")
        st.write(result["summary"])
    with tab4:
        st.subheader("Download the investigation")
        export = {
            "scenario": investigation["name"],
            "summary": result["summary"],
            "report": report,
            "decisions": result["decisions"],
            "schedule": result["schedule"],
        }
        st.download_button("⬇️ Download JSON report", data=json.dumps(export, indent=2), file_name="energy_detective_report.json", mime="application/json", use_container_width=True)
        st.download_button("⬇️ Download hourly CSV", data=pd.DataFrame(report["hourly_comparison"]).to_csv(index=False), file_name="energy_detective_hourly.csv", mime="text/csv", use_container_width=True)

    st.divider()
    if st.button("🔄 Clear results and start again"):
        st.session_state.investigation = None
        st.rerun()

st.divider()
st.caption("ENERGY DETECTIVE AI | Educational AI Agent Project | Python + Streamlit | Simulation")
