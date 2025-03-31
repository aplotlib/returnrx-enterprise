import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import io

st.set_page_config(page_title="KaizenROI | Smart Return Optimization Suite", layout="wide")

st.markdown("""
<style>
body, .stApp { background-color: #e6eff3; font-family: 'Poppins', sans-serif; }
.stDataFrame thead tr th { background-color: #23b2be; color: white; }
.css-1d391kg { color: #004366; font-family: 'Montserrat'; font-weight: bold; }
.css-10trblm { font-family: 'Poppins'; font-size: 16px; }
input, textarea, .stTextInput > div > div > input {
    background-color: #ffffff !important;
    border-radius: 8px;
    padding: 8px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    with st.expander("📘 KaizenROI Help & Formulas", expanded=False):
        st.markdown("""
        ## How to Use KaizenROI
        1. Input real or sample product and return data.
        2. Add a proposed solution with its cost and expected return reduction.
        3. Click **Add Scenario** or run the **Example Scenario**.
        4. View ROI, margins, and breakeven metrics with visual charts.
        5. Export data to CSV or Excel.

        ## What This Tool Helps You Understand:
        - Will your return-reducing solution pay off?
        - How long will it take to recover costs?
        - How does the margin shift based on cost and ROI?

        ## Key Metrics Explained
        - **Return Rate** = Returns / Sales (30-day)
        - **Avoided Returns** = Returns * (Estimated Return Reduction %)
        - **Savings per Avoided Return** = Sale Price − New Unit Cost
        - **Net Benefit** = (Annual Savings − Added Costs − Solution Cost)
        - **ROI** = Net Benefit / Solution Cost
        - **Break-even** = Time required to recoup cost from savings (in days/months)
        - **Score** = ROI scaled by how quickly it pays off (higher = better)
        - **Amortized Margin** = Margin after extra cost minus annualized solution cost per unit

        ## Tips
        - Enter realistic 30-day sales and return data.
        - Start with the example scenario to learn.
        - Adjust % reduction to simulate low or high impact cases.
        - Use ROI and score to prioritize ideas.
        - Export to Excel to share or run what-if analysis.
        """)

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
        try:
            if not scenario_name:
                scenario_name = f"Scenario {len(self.scenarios) + 1}"

            uid = str(uuid.uuid4())[:8]
            return_rate = returns_30 / sales_30 if sales_30 else 0
            new_unit_cost = current_unit_cost + additional_cost_per_item
            amortized_solution_cost_per_unit = solution_cost / (sales_30 * 12) if sales_30 and sales_30 * 12 != 0 else 0

            return_cost_30 = returns_30 * current_unit_cost
            return_cost_annual = return_cost_30 * 12
            revenue_impact_30 = returns_30 * avg_sale_price
            revenue_impact_annual = revenue_impact_30 * 12

            avoided_returns = returns_30 * (reduction_rate / 100)
            savings_per_item = avg_sale_price - new_unit_cost
            savings_30 = avoided_returns * savings_per_item
            annual_savings = savings_30 * 12

            annual_additional_costs = additional_cost_per_item * sales_30 * 12
            annual_amortized_solution_cost = solution_cost
            net_benefit = annual_savings - annual_additional_costs - annual_amortized_solution_cost

            roi = break_even_days = break_even_months = score = None
            if solution_cost > 0 and net_benefit > 0:
                roi = net_benefit / solution_cost
                break_even_days = solution_cost / (net_benefit / 12)
                break_even_months = break_even_days / 30
                score = roi * 100 - break_even_days

            margin_before = avg_sale_price - current_unit_cost
            margin_after = avg_sale_price - new_unit_cost
            margin_after_amortized = margin_after - amortized_solution_cost_per_unit

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
        except Exception as e:
            st.error(f"Error adding scenario: {e}")

app = ReturnRxSimple()

st.title("📊 KaizenROI | Smart Return Optimization Suite")
st.caption("Analyze ROI, margin, and breakeven to inform smarter product improvements.")

with st.form("scenario_form"):
    st.subheader("➕ Add New Scenario")
    col1, col2 = st.columns(2)
    scenario_name = col1.text_input("Scenario Name")
    sku = col2.text_input("SKU")
    sales_30 = col1.number_input("30-day Sales", min_value=0.0)
    returns_30 = col2.number_input("30-day Returns", min_value=0.0)
    avg_sale_price = col1.number_input("Average Sale Price", min_value=0.0)
    current_unit_cost = col2.number_input("Current Unit Cost", min_value=0.0)
    additional_cost_per_item = col1.number_input("Additional Cost per Item (can be negative)", value=0.0)
    solution_cost = col2.number_input("Total Solution Cost", min_value=0.0)
    reduction_rate = col1.slider("Estimated Return Reduction (%)", 0, 100, 20)
    sales_channel = col2.text_input("Top Sales Channel")
    solution = col1.text_input("Proposed Solution")
    sales_365 = col1.number_input("365-day Sales (optional)", min_value=0.0)
    returns_365 = col2.number_input("365-day Returns (optional)", min_value=0.0)
    submitted = st.form_submit_button("Add Scenario")
    if submitted and sku:
        app.add_scenario(scenario_name, sku, sales_30, avg_sale_price, sales_channel,
                         returns_30, solution, solution_cost, additional_cost_per_item,
                         current_unit_cost, reduction_rate, sales_365, returns_365)
        st.success("Scenario added.")

if app.scenarios.empty:
    st.info("No scenarios added yet.")
else:
    df = app.scenarios.copy()
    st.subheader("📊 Scenario Dashboard")
    st.dataframe(df, use_container_width=True)

    st.subheader("📉 Net Benefit & Amortized Margin")
    chart = go.Figure()
    chart.add_trace(go.Bar(x=df['scenario_name'], y=df['net_benefit'], name="Net Benefit", marker_color='green'))
    chart.add_trace(go.Scatter(x=df['scenario_name'], y=df['margin_after_amortized'],
                               name="Amortized Margin", mode='lines+markers', line=dict(color='firebrick')))
    chart.update_layout(title="Profit & Margin Overview", height=400, legend_title_text='Metrics')
    st.plotly_chart(chart, use_container_width=True)

    csv_data = df.to_csv(index=False).encode()
    st.download_button("📥 Download CSV", data=csv_data, file_name="kaizenroi_export.csv", mime="text/csv")

    excel_data = io.BytesIO()
    with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Scenarios')
    st.download_button("📊 Download Excel", data=excel_data.getvalue(), file_name="kaizenroi_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
