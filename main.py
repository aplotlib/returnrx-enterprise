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

st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Vive_Health_Logo.svg/2560px-Vive_Health_Logo.svg.png", width=200)
st.title("📊 VIVE-RX | Returns Intelligence Toolkit")
st.caption("Analyze return reduction strategies and financial impact for Vive Health")

if "app" not in st.session_state:
    st.session_state.app = ReturnRxSimple()
app = st.session_state.app

with st.form("scenario_form"):
    st.subheader("Add New Scenario")
    col1, col2 = st.columns(2)
    scenario_name = col1.text_input("Scenario Name")
    sku = col2.text_input("SKU")
    sales_30 = col1.number_input("30-day Sales", min_value=0.0)
    avg_sale_price = col2.number_input("Avg Sale Price", min_value=0.0)
    returns_30 = col1.number_input("30-day Returns", min_value=0.0)
    current_unit_cost = col2.number_input("Current Unit Cost", min_value=0.0)
    additional_cost_per_item = col1.number_input("Extra Cost per Item", min_value=0.0)
    solution_cost = col2.number_input("Solution Cost", min_value=0.0)
    reduction_rate = col1.slider("Estimated Return Reduction (%)", 0, 100, 10)
    sales_channel = col2.text_input("Top Sales Channel")
    solution = col1.text_input("Proposed Solution")
    submitted = st.form_submit_button("Add Scenario")
    if submitted and sku:
        app.add_scenario(scenario_name, sku, sales_30, avg_sale_price, sales_channel,
                         returns_30, solution, solution_cost, additional_cost_per_item,
                         current_unit_cost, reduction_rate)
        st.success("Scenario added.")

st.header("Scenario Dashboard")
if app.scenarios.empty:
    st.info("No scenarios added yet.")
else:
    df = app.scenarios.copy()
    selected = st.selectbox("Filter by SKU", ["All"] + sorted(df['sku'].unique()))
    if selected != "All":
        df = df[df['sku'] == selected]

    st.dataframe(df.style.format({
        'return_rate': '{:.2%}',
        'roi': '{:.2f}',
        'break_even_months': '{:.2f}',
        'net_benefit': '${:,.2f}',
        'annual_savings': '${:,.2f}',
        'annual_additional_costs': '${:,.2f}'
    }), use_container_width=True)

    st.subheader("ROI & Breakeven Charts")
    plot_df = df.dropna(subset=['roi', 'break_even_months'])
    if not plot_df.empty:
        fig = make_subplots(rows=1, cols=2, subplot_titles=("ROI", "Breakeven (months)"))
        fig.add_trace(go.Bar(x=plot_df['scenario_name'], y=plot_df['roi'], name="ROI", marker_color='#23b2be'), row=1, col=1)
        fig.add_trace(go.Bar(x=plot_df['scenario_name'], y=plot_df['break_even_months'], name="Breakeven", marker_color='#F0B323'), row=1, col=2)
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.download_button("📥 Download CSV", data=df.to_csv(index=False).encode(), file_name="vive_rx_export.csv", mime="text/csv")
