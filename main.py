import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(page_title="ReturnRx Enterprise", layout="wide")
sns.set(style="whitegrid")  # Apply a clean style globally

class ReturnRxSimple:
    def __init__(self):
        self.scenarios = pd.DataFrame(columns=[
            'scenario_name', 'sku', 'sales_30', 'avg_sale_price', 
            'sales_channel', 'returns_30', 'solution', 'solution_cost',
            'additional_cost_per_item', 'current_unit_cost', 'reduction_rate',
            'return_cost_30', 'return_cost_annual', 'revenue_impact_30',
            'revenue_impact_annual', 'new_unit_cost', 'savings_30',
            'annual_savings', 'break_even_days', 'break_even_months',
            'roi', 'score', 'timestamp', 'annual_additional_costs', 'net_benefit'])

    def add_scenario(self, scenario_name, sku, sales_30, avg_sale_price, sales_channel, 
                     returns_30, solution, solution_cost, additional_cost_per_item, 
                     current_unit_cost, reduction_rate):
        if not scenario_name:
            scenario_name = f"Scenario {len(self.scenarios) + 1}"

        # Refined: avoid rounding errors
        return_cost_30 = returns_30 * current_unit_cost
        return_cost_annual = return_cost_30 * 12
        revenue_impact_30 = returns_30 * avg_sale_price
        revenue_impact_annual = revenue_impact_30 * 12
        new_unit_cost = current_unit_cost + additional_cost_per_item

        avoided_returns = returns_30 * (reduction_rate / 100)
        savings_30 = avoided_returns * (avg_sale_price - current_unit_cost)
        annual_savings = savings_30 * 12

        annual_additional_costs = additional_cost_per_item * sales_30 * 12
        net_benefit = annual_savings - annual_additional_costs

        roi = None
        break_even_days = None
        break_even_months = None
        score = None

        if solution_cost > 0 and net_benefit > 0:
            roi = net_benefit / solution_cost
            break_even_days = solution_cost / net_benefit
            break_even_months = break_even_days / 30
            score = roi * 100 - break_even_days

        new_row = {
            'scenario_name': scenario_name,
            'sku': sku,
            'sales_30': sales_30,
            'avg_sale_price': avg_sale_price,
            'sales_channel': sales_channel,
            'returns_30': returns_30,
            'solution': solution,
            'solution_cost': solution_cost,
            'additional_cost_per_item': additional_cost_per_item,
            'current_unit_cost': current_unit_cost,
            'reduction_rate': reduction_rate,
            'return_cost_30': return_cost_30,
            'return_cost_annual': return_cost_annual,
            'revenue_impact_30': revenue_impact_30,
            'revenue_impact_annual': revenue_impact_annual,
            'new_unit_cost': new_unit_cost,
            'savings_30': savings_30,
            'annual_savings': annual_savings,
            'break_even_days': break_even_days,
            'break_even_months': break_even_months,
            'roi': roi,
            'score': score,
            'timestamp': datetime.now(),
            'annual_additional_costs': annual_additional_costs,
            'net_benefit': net_benefit
        }

        self.scenarios = pd.concat([self.scenarios, pd.DataFrame([new_row])], ignore_index=True)

# Initialize App
st.title("📦 ReturnRx Enterprise - Product Return Optimizer")
if "app" not in st.session_state:
    st.session_state.app = ReturnRxSimple()
app = st.session_state.app

# Help Sidebar
with st.sidebar:
    st.header("ℹ️ Help & Info")
    st.markdown("""
    **Formulas Used:**
    - **Avoided Returns** = Returns × (% Reduction / 100)
    - **Savings (30 days)** = Avoided Returns × (Avg Sale Price − Unit Cost)
    - **Annual Savings** = Savings × 12
    - **Annual Extra Cost** = Add-On Cost per Item × Sales × 12
    - **Net Benefit** = Annual Savings − Annual Cost
    - **ROI** = Net Benefit ÷ Solution Cost
    - **Breakeven** = Months until Net Benefit covers Cost
    """)

# Input form
st.subheader("➕ Add New Scenario")
with st.form("scenario_form"):
    scenario_name = st.text_input("Scenario Name")
    sku = st.text_input("SKU")
    sales_30 = st.number_input("Sales (Last 30 Days)", min_value=0.0)
    avg_sale_price = st.number_input("Average Sale Price", min_value=0.0)
    sales_channel = st.text_input("Top Sales Channel")
    returns_30 = st.number_input("Returns (Last 30 Days)", min_value=0.0)
    solution = st.text_input("Suggested Solution")
    solution_cost = st.number_input("Total Solution Cost", min_value=0.0)
    additional_cost_per_item = st.number_input("Additional Cost per Item", value=0.0)
    current_unit_cost = st.number_input("Current Unit Cost", min_value=0.0)
    reduction_rate = st.slider("Est. Return Rate Reduction (%)", 0, 100)

    submitted = st.form_submit_button("Add Scenario")
    if submitted and sku.strip():
        app.add_scenario(
            scenario_name, sku, sales_30, avg_sale_price, sales_channel,
            returns_30, solution, solution_cost, additional_cost_per_item,
            current_unit_cost, reduction_rate
        )
        st.success(f"✅ Scenario '{scenario_name or 'Default'}' added.")
    elif submitted:
        st.warning("⚠️ SKU is required.")

# Scenario Display
st.markdown("""---""")
st.subheader("📊 Scenario Overview")

if app.scenarios.empty:
    st.info("No scenarios yet. Add one above to get started.")
else:
    selected_sku = st.selectbox("Filter by SKU", ["All"] + sorted(app.scenarios['sku'].unique()))
    filtered_df = app.scenarios if selected_sku == "All" else app.scenarios[app.scenarios['sku'] == selected_sku]

    st.dataframe(filtered_df, use_container_width=True)

    # Summary Cards
    for _, row in filtered_df.iterrows():
        with st.expander(f"📦 Scenario: {row['scenario_name']}"):
            st.metric("ROI", f"{row['roi']:.2f}" if pd.notnull(row['roi']) else "N/A")
            st.metric("Breakeven (months)", f"{row['break_even_months']:.2f}" if pd.notnull(row['break_even_months']) else "N/A")
            st.markdown(f"**💰 Net Benefit:** ${row['net_benefit']:,.2f}")
            st.markdown(f"**💸 Annual Savings:** ${row['annual_savings']:,.2f}")
            st.markdown(f"**📦 Extra Annual Cost:** ${row['annual_additional_costs']:,.2f}")
            st.markdown(f"**💡 Solution Cost:** ${row['solution_cost']:,.2f}")

    # Visuals
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 ROI per Scenario")
        if not filtered_df.dropna(subset=['roi']).empty:
            fig = px.bar(filtered_df, x='scenario_name', y='roi', color='roi', title="ROI")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No ROI data to visualize.")

    with col2:
        st.subheader("⏳ Breakeven Time")
        if not filtered_df.dropna(subset=['break_even_months']).empty:
            fig2 = px.bar(filtered_df, x='scenario_name', y='break_even_months', color='break_even_months', title="Breakeven (months)")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Not enough breakeven data.")

    # CSV Download
    st.download_button("📥 Download CSV", data=filtered_df.to_csv(index=False).encode(), file_name="returnrx_data.csv", mime="text/csv")
