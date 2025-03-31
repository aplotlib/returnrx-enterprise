import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(page_title="VIVE-RX | Returns Intelligence Toolkit", layout="wide")

st.markdown("""
<style>
body, .stApp { background-color: #f7f9fc; font-family: 'Poppins', sans-serif; }
.stDataFrame thead tr th { background-color: #23b2be; color: white; }
.css-1d391kg { color: #004366; font-family: 'Montserrat'; font-weight: bold; }
.css-10trblm { font-family: 'Poppins'; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

class ReturnRxSimple:
    def __init__(self):
        self.scenarios = pd.DataFrame(columns=[
            'scenario_name', 'sku', 'sales_30', 'avg_sale_price',
            'sales_channel', 'returns_30', 'return_rate', 'solution', 'solution_cost',
            'additional_cost_per_item', 'current_unit_cost', 'reduction_rate',
            'return_cost_30', 'return_cost_annual', 'revenue_impact_30',
            'revenue_impact_annual', 'new_unit_cost', 'savings_30',
            'annual_savings', 'break_even_days', 'break_even_months',
            'roi', 'score', 'timestamp', 'annual_additional_costs', 'net_benefit',
            'margin_before', 'margin_after', 'margin_after_amortized'])

    def add_scenario(self, scenario_name, sku, sales_30, avg_sale_price, sales_channel,
                     returns_30, solution, solution_cost, additional_cost_per_item,
                     current_unit_cost, reduction_rate):
        if not scenario_name:
            scenario_name = f"Scenario {len(self.scenarios) + 1}"

        if sales_30 <= 0:
            return_rate = 0
            amortized_solution_cost = 0
        else:
            return_rate = returns_30 / sales_30
            amortized_solution_cost = solution_cost / (sales_30 * 12)

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

        margin_before = avg_sale_price - current_unit_cost
        margin_after = avg_sale_price - new_unit_cost
        margin_after_amortized = margin_after - amortized_solution_cost

        new_row = {
            'scenario_name': scenario_name,
            'sku': sku,
            'sales_30': sales_30,
            'avg_sale_price': avg_sale_price,
            'sales_channel': sales_channel,
            'returns_30': returns_30,
            'return_rate': return_rate,
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
            'net_benefit': net_benefit,
            'margin_before': margin_before,
            'margin_after': margin_after,
            'margin_after_amortized': margin_after_amortized
        }

        self.scenarios = pd.concat([self.scenarios, pd.DataFrame([new_row])], ignore_index=True)

st.title("📊 VIVE-RX | Returns Intelligence Toolkit")
st.caption("Analyze return reduction strategies and financial impact for Vive Health")

with st.sidebar:
    st.header("📘 Help & Formulas")
    st.markdown("""
    **Input Field Explanations:**

    - **Scenario Name**: Custom name for your analysis.
    - **SKU**: The product identifier.
    - **30-day Sales**: Total units sold over the last 30 days.
    - **Avg Sale Price**: Average selling price per unit.
    - **30-day Returns**: Units returned in the past 30 days.
    - **Current Unit Cost**: Current production/purchase cost per unit.
    - **Extra Cost per Item**: Any added cost from the proposed solution (e.g., better packaging, quality material).
    - **Solution Cost**: One-time or fixed cost to implement the solution (e.g., software, redesign project).
    - **Estimated Return Reduction (%)**: Expected percentage drop in return rate due to the solution.
    - **Top Sales Channel**: Main source of sales (e.g., Amazon, DTC site).
    - **Proposed Solution**: Description of the intervention being evaluated.

    **Formulas Used:**

    - **Return Rate** = Returns / Sales
    - **Avoided Returns** = Returns × (% Reduction)
    - **Savings** = Avoided Returns × (Avg Price − New Unit Cost)
    - **Annual Savings** = Savings × 12
    - **Annual Add-On Cost** = Extra Cost per Item × Sales × 12
    - **Net Benefit** = Annual Savings − Annual Add-On Cost
    - **ROI** = Net Benefit / Solution Cost
    - **Breakeven** = Months to recover solution cost from net benefit
    - **Profit Margin (Before)** = Avg Sale Price − Current Unit Cost
    - **Profit Margin (After)** = Avg Sale Price − (Current Unit Cost + Extra Cost)
    - **Profit Margin (Amortized)** = Margin After − (Solution Cost ÷ Annual Sales)
    """)
