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
        try:
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
        except Exception as e:
            st.error(f"Error adding scenario: {e}")

if "app" not in st.session_state:
    st.session_state.app = ReturnRxSimple()
app = st.session_state.app

st.title("📊 KaizenROI | Smart Return Optimization Suite")
st.caption("A continuous improvement tool for evaluating return reduction investments with precision.")

with st.sidebar:
    st.header("📘 Help & Formulas")
    st.markdown("""
    ### How to Use This Tool
    1. Enter your sales, return, cost, and solution data.
    2. Submit and view financial analytics with charts and margins.
    3. Click example button to test a realistic scenario.

    ### Key Formulas
    - Return Rate = Returns ÷ Sales
    - Avoided Returns = Returns × Reduction %
    - Net Benefit = (Returns Avoided × Savings Per Item) − Annual Extra Cost
    - ROI = Net Benefit ÷ Solution Cost
    - Break-even = Solution Cost ÷ Monthly Net Profit
    - Margin After Amortization = (Price − New Cost) − Solution ÷ Units
    """)
    if st.button("▶️ Run Example Scenario"):
        app.add_scenario("Example ROI Case", "SKU123", 400, 50, "Amazon", 40, "Better packaging", 2000, 2, 18, 25, 4800, 450)
        st.success("Example scenario added!")

with st.form("input_form"):
    st.subheader("➕ Add New Scenario")
    c1, c2 = st.columns(2)
    scenario_name = c1.text_input("Scenario Name")
    sku = c2.text_input("SKU")
    sales_30 = c1.number_input("30-day Sales", min_value=0.0)
    returns_30 = c2.number_input("30-day Returns", min_value=0.0)
    avg_sale_price = c1.number_input("Average Sale Price", min_value=0.0)
    current_unit_cost = c2.number_input("Current Unit Cost", min_value=0.0)
    additional_cost_per_item = c1.number_input("Additional Cost per Item", min_value=0.0)
    solution_cost = c2.number_input("Total Solution Cost", min_value=0.0)
    reduction_rate = c1.slider("Estimated Return Reduction (%)", 0, 100, 10)
    sales_channel = c2.text_input("Top Sales Channel")
    solution = c1.text_input("Proposed Solution")
    sales_365 = c1.number_input("365-day Sales (optional)", min_value=0.0)
    returns_365 = c2.number_input("365-day Returns (optional)", min_value=0.0)
    submit = st.form_submit_button("Add Scenario")
    if submit and sku:
        app.add_scenario(scenario_name, sku, sales_30, avg_sale_price, sales_channel, returns_30,
                         solution, solution_cost, additional_cost_per_item, current_unit_cost,
                         reduction_rate, sales_365, returns_365)
        st.success("Scenario added!")

if app.scenarios.empty:
    st.info("Add or generate a scenario to begin analysis.")
else:
    df = app.scenarios.copy()
    st.subheader("📊 Scenario Dashboard")
    st.dataframe(df, use_container_width=True)

    st.subheader("📈 ROI & Breakeven Charts")
    plot_df = df.dropna(subset=['roi', 'break_even_months'])
    if not plot_df.empty:
        fig = make_subplots(rows=1, cols=2, subplot_titles=("ROI", "Break-even (months)"))
        fig.add_trace(go.Bar(x=plot_df['scenario_name'], y=plot_df['roi'], name="ROI", marker_color='green'), row=1, col=1)
        fig.add_trace(go.Bar(x=plot_df['scenario_name'], y=plot_df['break_even_months'], name="Breakeven", marker_color='orange'), row=1, col=2)
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📉 Net Benefit & Amortized Margin")
    chart2 = go.Figure()
    chart2.add_trace(go.Bar(x=df['scenario_name'], y=df['net_benefit'], name="Net Benefit", marker_color='seagreen'))
    chart2.add_trace(go.Bar(x=df['scenario_name'], y=df['margin_after_amortized'], name="Amortized Margin", marker_color='indianred'))
    chart2.update_layout(barmode='group', height=400)
    st.plotly_chart(chart2, use_container_width=True)

    csv_data = df.to_csv(index=False).encode()
    st.download_button("📥 Download CSV", data=csv_data, file_name="kaizenroi_export.csv", mime="text/csv")

    excel_data = io.BytesIO()
    with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Scenarios')
    st.download_button("📊 Download Excel", data=excel_data.getvalue(), file_name="kaizenroi_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
