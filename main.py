import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(page_title="ReturnRx Enterprise", layout="wide")

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

        return_cost_30 = returns_30 * current_unit_cost
        return_cost_annual = return_cost_30 * 12
        revenue_impact_30 = returns_30 * avg_sale_price
        revenue_impact_annual = revenue_impact_30 * 12
        new_unit_cost = current_unit_cost + additional_cost_per_item

        avoided_returns = returns_30 * (reduction_rate / 100)
        savings_30 = avoided_returns * (avg_sale_price - new_unit_cost)
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

# UI starts here
st.markdown("""
    <style>
    .main {
        background-color: #f7f9fc;
    }
    .stApp {
        background-color: #ffffff;
    }
    .stDataFrame thead tr th {
        background-color: #e3efff;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 ReturnRx Enterprise")
st.caption("A decision-support tool for evaluating return reduction strategies.")

if "app" not in st.session_state:
    st.session_state.app = ReturnRxSimple()
app = st.session_state.app

with st.sidebar:
    st.header("📘 Help & Formulas")
    st.markdown("""
    **Avoided Returns** = Returns × (% Reduction)
    
    **Savings** = Avoided Returns × (Avg Price − New Unit Cost)

    **Annual Savings** = Savings × 12

    **Annual Add-On Cost** = Extra Cost per Item × Sales × 12

    **Net Benefit** = Annual Savings − Annual Add-On Cost

    **ROI** = Net Benefit / Solution Cost

    **Breakeven** = Months to recover solution cost from net benefit
    """)

st.header("➕ Add Scenario")
with st.form("scenario_form"):
    cols = st.columns(2)
    scenario_name = cols[0].text_input("Scenario Name")
    sku = cols[1].text_input("SKU")
    sales_30 = cols[0].number_input("30-day Sales", min_value=0.0)
    avg_sale_price = cols[1].number_input("Avg Sale Price", min_value=0.0)
    returns_30 = cols[0].number_input("30-day Returns", min_value=0.0)
    current_unit_cost = cols[1].number_input("Current Unit Cost", min_value=0.0)
    additional_cost_per_item = cols[0].number_input("Extra Cost per Item", value=0.0)
    solution_cost = cols[1].number_input("Solution Cost", value=0.0)
    reduction_rate = cols[0].slider("Estimated Return Reduction (%)", 0, 100, 10)
    sales_channel = cols[1].text_input("Top Sales Channel")
    solution = cols[0].text_input("Proposed Solution")
    submitted = st.form_submit_button("Add Scenario")
    if submitted and sku:
        app.add_scenario(scenario_name, sku, sales_30, avg_sale_price, sales_channel, returns_30, solution, solution_cost, additional_cost_per_item, current_unit_cost, reduction_rate)
        st.success("Scenario added!")

# Display Section
st.header("📊 Scenario Dashboard")
if app.scenarios.empty:
    st.info("Add a scenario to get started.")
else:
    df = app.scenarios.copy()
    selected = st.selectbox("Filter by SKU", ["All"] + sorted(df['sku'].unique()))
    if selected != "All":
        df = df[df['sku'] == selected]

    st.dataframe(df.style.format({
        'roi': '{:.2f}',
        'break_even_months': '{:.2f}',
        'net_benefit': '${:,.2f}',
        'annual_savings': '${:,.2f}',
        'annual_additional_costs': '${:,.2f}'
    }), use_container_width=True)

    st.subheader("📈 ROI and Breakeven Chart")
    plot_df = df.dropna(subset=['roi', 'break_even_months'])
    if not plot_df.empty:
        fig = make_subplots(rows=1, cols=2, subplot_titles=("ROI", "Breakeven (months)"))
        fig.add_trace(go.Bar(x=plot_df['scenario_name'], y=plot_df['roi'], name="ROI", marker_color='seagreen'), row=1, col=1)
        fig.add_trace(go.Bar(x=plot_df['scenario_name'], y=plot_df['break_even_months'], name="Breakeven", marker_color='indianred'), row=1, col=2)
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.download_button("📥 Download Data as CSV", data=df.to_csv(index=False).encode(), file_name="returnrx_export.csv", mime="text/csv")
