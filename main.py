# meddevroi_app.py

import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import io
import plotly.express as px

# --- App Setup ---
st.set_page_config(page_title="MedDevROI", layout="wide")
st.title("🏥 MedDevROI - Device Investment & Risk Analysis Suite")

# --- Session Init ---
if "scenarios" not in st.session_state:
    st.session_state.scenarios = pd.DataFrame()
if "step" not in st.session_state:
    st.session_state.step = 1

# --- Progress Bar UI ---
steps = ["Device Classification", "Risk Assessment", "ROI Analysis"]
st.markdown("### 📊 Progress Tracker")
cols = st.columns(len(steps))
for i, s in enumerate(steps):
    style = "✅" if i + 1 < st.session_state.step else "➡️" if i + 1 == st.session_state.step else "⚪"
    cols[i].markdown(f"{style} **Step {i+1}: {s}**")

# --- Step Navigation Buttons ---
st.markdown("---")
nav1, nav2, nav3 = st.columns(3)
if nav1.button("Step 1: Classification"): st.session_state.step = 1
if nav2.button("Step 2: Risk"): st.session_state.step = 2
if nav3.button("Step 3: ROI"): st.session_state.step = 3

# --- Classification ---
if st.session_state.step == 1:
    st.header("📦 Step 1: Device Classification")
    with st.form("classification_form"):
        scenario_id = st.text_input("Scenario Name (e.g., MOB1027 Upgrade #01)", "")
        intended_use = st.selectbox("Intended Use", ["Diagnostic", "Therapeutic", "Monitoring", "Life-supporting"])
        contact_type = st.selectbox("Contact Type", ["Surface", "External", "Implantable"])
        invasiveness = st.selectbox("Invasiveness", ["Non-invasive", "Minimally", "Invasive", "Implantable"])
        duration = st.selectbox("Use Duration", ["<60min", "<30d", ">30d"])
        submit = st.form_submit_button("Save Classification")

        if submit and scenario_id:
            risk_class = "Class I"
            if invasiveness in ["Implantable"] or intended_use == "Life-supporting":
                risk_class = "Class III"
            elif invasiveness == "Invasive":
                risk_class = "Class II"

            new = pd.DataFrame([{
                "Scenario": scenario_id,
                "Step": "Classification",
                "Use": intended_use,
                "Contact": contact_type,
                "Invasiveness": invasiveness,
                "Duration": duration,
                "Risk Class": risk_class,
                "Timestamp": datetime.now()
            }])
            st.session_state.scenarios = pd.concat([st.session_state.scenarios, new], ignore_index=True)
            st.success("Classification Saved ✅")

# --- Risk Assessment ---
if st.session_state.step == 2:
    st.header("⚠️ Step 2: Risk Assessment")
    with st.form("risk_form"):
        scenario_id = st.selectbox("Choose Scenario", st.session_state.scenarios["Scenario"].unique())
        safety = st.slider("Safety Risk", 0, 10, 5)
        compliance = st.slider("Compliance Risk", 0, 10, 5)
        logistics = st.slider("Logistics Risk", 0, 10, 5)
        financial = st.slider("Financial Risk", 0, 10, 5)
        submit_risk = st.form_submit_button("Save Risk")

        if submit_risk:
            weighted = safety*0.4 + compliance*0.3 + logistics*0.15 + financial*0.15
            level = "High" if weighted > 7 else "Moderate" if weighted > 4 else "Low"
            new = pd.DataFrame([{
                "Scenario": scenario_id,
                "Step": "Risk",
                "Safety": safety,
                "Compliance": compliance,
                "Logistics": logistics,
                "Financial": financial,
                "Risk Score": weighted,
                "Risk Level": level,
                "Timestamp": datetime.now()
            }])
            st.session_state.scenarios = pd.concat([st.session_state.scenarios, new], ignore_index=True)
            st.success("Risk Assessment Saved ✅")

# --- ROI Analysis ---
if st.session_state.step == 3:
    st.header("📈 Step 3: ROI Calculator")

    tab1, tab2 = st.tabs(["Product ROI", "Non-Product ROI"])

    with tab1:
        with st.form("product_roi"):
            scenario_id = st.text_input("Scenario Name (e.g., MOB1027 Upgrade #02)")
            sales = st.number_input("Monthly Sales Units", min_value=0)
            return_rate = st.number_input("Return Rate (%)", min_value=0.0, max_value=100.0)
            improvement = st.number_input("Expected Reduction in Returns (%)", min_value=0.0, max_value=100.0)
            avg_price = st.number_input("Average Price per Unit ($)", min_value=0.0)
            cost_before = st.number_input("Original Unit Cost ($)", min_value=0.0)
            cost_change = st.number_input("Change in Cost per Unit ($)", value=0.0, format="%.2f")
            solution_cost = st.number_input("Upfront Improvement Cost ($)", min_value=0.0)
            submit_prod = st.form_submit_button("Calculate ROI")

            if submit_prod:
                avoided = sales * return_rate/100 * improvement/100
                unit_cost = cost_before + cost_change
                savings = avoided * (avg_price - unit_cost)
                net_annual = (savings - (cost_change * sales)) * 12
                roi = (net_annual / solution_cost) * 100 if solution_cost else 0
                breakeven = solution_cost / (net_annual/12) if net_annual > 0 else float("inf")

                new = pd.DataFrame([{
                    "Scenario": scenario_id,
                    "Step": "Product ROI",
                    "ROI %": roi,
                    "Breakeven Months": breakeven,
                    "Annual Net Benefit": net_annual,
                    "Timestamp": datetime.now()
                }])
                st.session_state.scenarios = pd.concat([st.session_state.scenarios, new], ignore_index=True)
                st.success("Product ROI Saved ✅")

    with tab2:
        with st.form("nonprod_roi"):
            scenario_id = st.text_input("Non-Product Scenario Name")
            invest = st.number_input("Initial Investment ($)", min_value=0.0)
            recurring = st.number_input("Monthly/Annual Cost ($)", min_value=0.0)
            benefit = st.number_input("Expected Annual Benefit ($)", min_value=0.0)
            confidence = st.slider("Confidence in Estimate (%)", 0, 100, 80)
            submit_np = st.form_submit_button("Calculate Non-Product ROI")

            if submit_np:
                adj_benefit = benefit * (confidence / 100)
                net = adj_benefit - recurring
                roi = ((net - invest) / invest) * 100 if invest else 0
                breakeven = invest / (net / 12) if net > 0 else float("inf")

                new = pd.DataFrame([{
                    "Scenario": scenario_id,
                    "Step": "Non-Product ROI",
                    "ROI %": roi,
                    "Breakeven Months": breakeven,
                    "Annual Net Benefit": net,
                    "Timestamp": datetime.now()
                }])
                st.session_state.scenarios = pd.concat([st.session_state.scenarios, new], ignore_index=True)
                st.success("Non-Product ROI Saved ✅")

# --- Comparison Tool ---
st.markdown("---")
st.header("📊 Compare Scenarios")
df_compare = st.session_state.scenarios.pivot_table(
    index="Scenario", columns="Step", values=["ROI %", "Risk Score"], aggfunc="first"
).reset_index()
st.dataframe(df_compare, use_container_width=True)

if not df_compare.empty:
    fig = px.scatter(
        df_compare, 
        x=("Risk Score", "Risk"), 
        y=("ROI %", "Product ROI"), 
        text="Scenario",
        labels={"x": "Risk Score", "y": "ROI %"},
        title="Risk vs ROI (Product ROI only)"
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Export Section ---
st.markdown("---")
st.header("📤 Export All Data")
if not st.session_state.scenarios.empty:
    df_export = st.session_state.scenarios.copy()
    df_export["Timestamp"] = df_export["Timestamp"].astype(str)
    csv = df_export.to_csv(index=False).encode()
    excel = io.BytesIO()
    with pd.ExcelWriter(excel, engine="xlsxwriter") as writer:
        df_export.to_excel(writer, index=False, sheet_name="MedDevROI")

    st.download_button("Download CSV", csv, "meddevroi_export.csv", mime="text/csv")
    st.download_button("Download Excel", excel.getvalue(), "meddevroi_export.xlsx")
else:
    st.info("No scenarios recorded yet.")
