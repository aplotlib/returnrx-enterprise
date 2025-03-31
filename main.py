import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import io

st.set_page_config(page_title="KaizenCBA | Product Return Optimization Toolkit", layout="wide")

st.markdown("""
<style>
body, .stApp { background-color: #f2f2f2; font-family: 'Poppins', sans-serif; }
.stDataFrame thead tr th { background-color: #23b2be; color: white; }
.css-1d391kg { color: #004366; font-family: 'Montserrat'; font-weight: bold; }
.css-10trblm { font-family: 'Poppins'; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

class ReturnRxSimple:
    def __init__(self):
        self.scenarios = pd.DataFrame(columns=[
            'uid', 'scenario_name', 'sku', 'sales_30', 'avg_sale_price',
            'sales_channel', 'returns_30', 'return_rate', 'solution', 'solution_cost',
            'additional_cost_per_item', 'current_unit_cost', 'reduction_rate',
            'return_cost_30', 'return_cost_annual', 'revenue_impact_30',
            'revenue_impact_annual', 'new_unit_cost', 'savings_30',
            'annual_savings', 'break_even_days', 'break_even_months',
            'roi', 'score', 'timestamp', 'annual_additional_costs', 'net_benefit',
            'margin_before', 'margin_after', 'margin_after_amortized',
            'sales_365', 'returns_365'])

    def add_scenario(self, scenario_name, sku, sales_30, avg_sale_price, sales_channel,
                     returns_30, solution, solution_cost, additional_cost_per_item,
                     current_unit_cost, reduction_rate, sales_365, returns_365):
        if not scenario_name:
            scenario_name = f"Scenario {len(self.scenarios) + 1}"

        uid = str(uuid.uuid4())[:8]
        return_rate = returns_30 / sales_30 if sales_30 else 0
        amortized_solution_cost = solution_cost / (sales_30 * 12) if sales_30 else 0

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

        roi = break_even_days = break_even_months = score = None
        if solution_cost > 0 and net_benefit > 0:
            roi = net_benefit / solution_cost
            break_even_days = solution_cost / net_benefit
            break_even_months = break_even_days / 30
            score = roi * 100 - break_even_days

        margin_before = avg_sale_price - current_unit_cost
        margin_after = avg_sale_price - new_unit_cost
        margin_after_amortized = margin_after - amortized_solution_cost

        new_row = {
            'uid': uid,
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
            'margin_after_amortized': margin_after_amortized,
            'sales_365': sales_365,
            'returns_365': returns_365
        }

        self.scenarios = pd.concat([self.scenarios, pd.DataFrame([new_row])], ignore_index=True)

st.title("📊 KaizenCBA | Product Return Optimization Toolkit")
st.caption("A continuous improvement approach to financial decision making for returns management.")

if "app" not in st.session_state:
    st.session_state.app = ReturnRxSimple()
app = st.session_state.app

st.sidebar.header("📘 Help & Formulas")
st.sidebar.markdown("""
### How to Use This Tool
1. **Enter scenario details** such as SKU, sales data, return count, and proposed solution.
2. Input **costs associated** with the solution and any expected **return rate reduction**.
3. View the **automated financial impact analysis**, ROI, and breakeven projections.

---

### Field Guide:
- **30-day Sales / Returns**: Monthly product performance baseline.
- **365-day Sales / Returns** (optional): Full-year perspective.
- **Avg Sale Price**: Average revenue per item sold.
- **Current Unit Cost**: How much each item costs before the solution.
- **Extra Cost per Item**: Cost added per item with the solution.
- **Solution Cost**: Upfront or implementation cost for the solution.
- **Reduction %**: Estimated % improvement in return rates.

---

### Formulas Used:
- **Return Rate** = `30-day Returns ÷ 30-day Sales`
- **Avoided Returns** = `30-day Returns × (% Reduction)`
- **Savings** = `Avoided Returns × (Sale Price − New Unit Cost)`
- **Annual Savings** = `Savings × 12`
- **Annual Add-on Cost** = `Extra Cost × Sales × 12`
- **Net Benefit** = `Annual Savings − Annual Add-on Cost`
- **ROI** = `Net Benefit ÷ Solution Cost`
- **Breakeven (Months)** = `Solution Cost ÷ Monthly Net Benefit`
- **Margins** = `Sale Price − Cost (before/after/amortized)`

---

### Example
- Sales: 500, Returns: 50, Price: $40, Cost: $20
- Extra Cost: $2, Solution Cost: $5,000, Reduction: 20%
- See how avoided returns + added costs yield ROI and breakeven insight

👇 Or click below to generate an example scenario.
""")

if st.sidebar.button("▶️ Run Example Scenario"):
    app.add_scenario(
        scenario_name="Example ROI Positive",
        sku="DEMO-001",
        sales_30=500,
        avg_sale_price=40,
        sales_channel="Amazon",
        returns_30=50,
        solution="Premium Packaging",
        solution_cost=5000,
        additional_cost_per_item=2,
        current_unit_cost=20,
        reduction_rate=20,
        sales_365=6000,
        returns_365=600
    )
    st.success("Example scenario added! Scroll down to view analysis.")

if not app.scenarios.empty:
    df = app.scenarios.copy()
    latest = df.iloc[-1]
    days = list(range(0, 366))
    daily_costs = [(latest['solution_cost'] / 365) + (latest['additional_cost_per_item'] * latest['sales_30']) / 30] * 365
    daily_savings = [(latest['annual_savings'] / 365)] * 365
    cumulative_profit = [sum(daily_savings[:i+1]) - sum(daily_costs[:i+1]) for i in range(365)]

    st.subheader("📈 Breakeven and Net Benefit Over Time")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=days, y=cumulative_profit, mode='lines', name='Cumulative Net Benefit', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=days, y=[0]*365, mode='lines', name='Breakeven Line', line=dict(dash='dash', color='gray')))
    fig.update_layout(title="Projected Profit Over 12 Months", xaxis_title="Day", yaxis_title="Cumulative Net Profit ($)", height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.caption(f"📌 Based on scenario: {latest['scenario_name']} | ROI: {latest['roi']:.2f} | Breakeven: {latest['break_even_months']:.2f} months")
