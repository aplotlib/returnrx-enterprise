import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# App configuration
st.set_page_config(
    page_title="TariffSight: Import Cost Analyzer",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #1E88E5;
        margin-bottom: 15px;
    }
    .result-box {
        background-color: #E8F5E9;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #43A047;
        margin: 15px 0;
    }
    .warning-box {
        background-color: #FFF3E0;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #FF9800;
        margin-bottom: 15px;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #616161;
    }
    .sidebar .sidebar-content {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

# Utility functions
def calculate_landed_cost(msrp, cost_to_produce, tariff_rate, shipping_cost=0, storage_cost=0, customs_fee=0, 
                         broker_fee=0, other_costs=0, units_per_shipment=1):
    """Calculate the landed cost and profitability with given tariff rate"""
    
    # Calculate per unit costs
    if units_per_shipment <= 0:
        units_per_shipment = 1
    
    shipping_per_unit = shipping_cost / units_per_shipment
    storage_per_unit = storage_cost / units_per_shipment
    customs_per_unit = customs_fee / units_per_shipment
    broker_per_unit = broker_fee / units_per_shipment
    other_per_unit = other_costs / units_per_shipment
    
    # Calculate tariff amount
    tariff_amount = cost_to_produce * (tariff_rate / 100)
    
    # Calculate total landed cost per unit
    landed_cost = cost_to_produce + tariff_amount + shipping_per_unit + storage_per_unit + customs_per_unit + broker_per_unit + other_per_unit
    
    # Calculate profit and margin
    profit = msrp - landed_cost
    margin_percentage = (profit / msrp) * 100 if msrp > 0 else 0
    
    # Calculate minimum profitable MSRP
    min_profitable_msrp = landed_cost * 1.01  # Minimum 1% profit margin
    
    # Breakeven price
    breakeven_price = landed_cost
    
    return {
        "landed_cost": landed_cost,
        "tariff_amount": tariff_amount,
        "profit": profit,
        "margin_percentage": margin_percentage,
        "min_profitable_msrp": min_profitable_msrp,
        "breakeven_price": breakeven_price,
        "cost_breakdown": {
            "production": cost_to_produce,
            "tariff": tariff_amount,
            "shipping": shipping_per_unit,
            "storage": storage_per_unit,
            "customs": customs_per_unit,
            "broker": broker_per_unit,
            "other": other_per_unit
        }
    }

def generate_tariff_scenarios(base_msrp, cost_to_produce, min_tariff=0, max_tariff=100, steps=10, 
                             shipping_cost=0, storage_cost=0, customs_fee=0, broker_fee=0, 
                             other_costs=0, units_per_shipment=1):
    """Generate scenarios for different tariff rates"""
    
    tariff_rates = np.linspace(min_tariff, max_tariff, steps)
    scenarios = []
    
    for rate in tariff_rates:
        result = calculate_landed_cost(
            base_msrp, cost_to_produce, rate, shipping_cost, storage_cost, 
            customs_fee, broker_fee, other_costs, units_per_shipment
        )
        
        scenarios.append({
            "tariff_rate": rate,
            "landed_cost": result["landed_cost"],
            "profit": result["profit"],
            "margin": result["margin_percentage"],
            "breakeven_price": result["breakeven_price"]
        })
    
    return pd.DataFrame(scenarios)

def generate_price_scenarios(tariff_rate, cost_to_produce, min_price_factor=0.8, max_price_factor=2.0, steps=10,
                            shipping_cost=0, storage_cost=0, customs_fee=0, broker_fee=0, 
                            other_costs=0, units_per_shipment=1):
    """Generate scenarios for different price points at a fixed tariff rate"""
    
    # Calculate base landed cost without MSRP
    base_result = calculate_landed_cost(
        100, cost_to_produce, tariff_rate, shipping_cost, storage_cost, 
        customs_fee, broker_fee, other_costs, units_per_shipment
    )
    base_landed_cost = base_result["landed_cost"]
    
    # Generate price range from min_price_factor to max_price_factor of landed cost
    min_price = base_landed_cost * min_price_factor
    max_price = base_landed_cost * max_price_factor
    
    price_points = np.linspace(min_price, max_price, steps)
    scenarios = []
    
    for price in price_points:
        result = calculate_landed_cost(
            price, cost_to_produce, tariff_rate, shipping_cost, storage_cost, 
            customs_fee, broker_fee, other_costs, units_per_shipment
        )
        
        scenarios.append({
            "msrp": price,
            "profit": result["profit"],
            "margin": result["margin_percentage"],
            "landed_cost": result["landed_cost"]
        })
    
    return pd.DataFrame(scenarios)

# Main app function
def main():
    # Display header
    st.markdown("<h1 class='main-header'>TariffSight: Import Cost Analyzer Calculator</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='info-box'>
    Calculate how tariffs impact your product profitability. Model different scenarios to optimize your pricing strategy.
    </div>
    """, unsafe_allow_html=True)
    
    # Create main tabs
    tabs = st.tabs(["Calculator", "Scenario Modeling", "Tariff Resources"])
    
    # Session state for saving calculations
    if 'calculations' not in st.session_state:
        st.session_state.calculations = []
    
    # Calculator Tab
    with tabs[0]:
        st.markdown("<h2 class='sub-header'>Product Details</h2>", unsafe_allow_html=True)
        
        # Create two columns for basic product info
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name", value="")
            sku = st.text_input("Product SKU", value="")
            msrp = st.number_input("MSRP / Retail Price ($)", min_value=0.01, value=100.00, step=0.01)
        
        with col2:
            cost_to_produce = st.number_input("Manufacturing Cost per Unit ($)", min_value=0.01, value=50.00, step=0.01)
            tariff_rate = st.slider("Tariff Rate (%)", min_value=0, max_value=500, value=25, step=1)
            currency = st.selectbox("Currency", options=["USD", "EUR", "GBP", "CAD", "AUD"], index=0)
        
        # Optional import costs section with expander
        with st.expander("Additional Import Costs (Optional)", expanded=False):
            col3, col4 = st.columns(2)
            
            with col3:
                shipping_cost = st.number_input("Shipping Cost per Shipment ($)", min_value=0.0, value=1000.0, step=10.0)
                storage_cost = st.number_input("Storage/Warehousing Cost ($)", min_value=0.0, value=0.0, step=10.0)
                customs_fee = st.number_input("Customs Processing Fee ($)", min_value=0.0, value=250.0, step=10.0)
            
            with col4:
                broker_fee = st.number_input("Customs Broker Fee ($)", min_value=0.0, value=150.0, step=10.0)
                other_costs = st.number_input("Other Import Costs ($)", min_value=0.0, value=0.0, step=10.0)
                units_per_shipment = st.number_input("Units per Shipment", min_value=1, value=1000, step=10)
        
        # Calculate button
        if st.button("Calculate Import Costs"):
            with st.spinner("Calculating..."):
                # Perform calculation
                result = calculate_landed_cost(
                    msrp, cost_to_produce, tariff_rate, shipping_cost, storage_cost,
                    customs_fee, broker_fee, other_costs, units_per_shipment
                )
                
                # Display results
                st.markdown("<h2 class='sub-header'>Calculation Results</h2>", unsafe_allow_html=True)
                
                # Create metrics layout
                col5, col6, col7, col8 = st.columns(4)
                
                with col5:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <p class='metric-label'>Landed Cost</p>
                        <p class='metric-value'>${result['landed_cost']:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col6:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <p class='metric-label'>Tariff Amount</p>
                        <p class='metric-value'>${result['tariff_amount']:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col7:
                    profit_color = "green" if result['profit'] > 0 else "red"
                    st.markdown(f"""
                    <div class='metric-card'>
                        <p class='metric-label'>Profit per Unit</p>
                        <p class='metric-value' style='color: {profit_color}'>${result['profit']:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col8:
                    margin_color = "green" if result['margin_percentage'] > 15 else ("orange" if result['margin_percentage'] > 0 else "red")
                    st.markdown(f"""
                    <div class='metric-card'>
                        <p class='metric-label'>Profit Margin</p>
                        <p class='metric-value' style='color: {margin_color}'>{result['margin_percentage']:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display breakeven and profitability
                st.markdown("<br>", unsafe_allow_html=True)
                col9, col10 = st.columns(2)
                
                with col9:
                    st.markdown(f"""
                    <div class='result-box'>
                        <h3>Breakeven Price: ${result['breakeven_price']:.2f}</h3>
                        <p>At this selling price, you will neither make a profit nor a loss after all import costs.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col10:
                    st.markdown(f"""
                    <div class='result-box'>
                        <h3>Minimum Profitable Price: ${result['min_profitable_msrp']:.2f}</h3>
                        <p>We recommend a minimum price point of ${result['min_profitable_msrp']:.2f} to ensure profitability.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Cost breakdown visualization
                st.markdown("<h3>Cost Breakdown</h3>", unsafe_allow_html=True)
                
                # Extract cost components
                cost_items = list(result["cost_breakdown"].keys())
                cost_values = list(result["cost_breakdown"].values())
                
                # Create pie chart
                fig = px.pie(
                    names=cost_items,
                    values=cost_values,
                    title="Cost Breakdown per Unit",
                    color_discrete_sequence=px.colors.qualitative.Safe,
                )
                
                # Update layout
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15),
                    margin=dict(t=50, b=100)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add to saved calculations
                calculation_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "product": product_name if product_name else "Unnamed Product",
                    "sku": sku if sku else "No SKU",
                    "msrp": msrp,
                    "cost": cost_to_produce,
                    "tariff_rate": tariff_rate,
                    "landed_cost": result['landed_cost'],
                    "profit": result['profit'],
                    "margin": result['margin_percentage']
                }
                
                st.session_state.calculations.append(calculation_entry)
                
                # Display recommendation based on margin
                if result['margin_percentage'] < 0:
                    st.markdown("""
                    <div class='warning-box'>
                        <h3>⚠️ Warning: Negative Margin</h3>
                        <p>This product is not profitable at the current price and tariff rate. Consider increasing your selling price or finding ways to reduce costs.</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif result['margin_percentage'] < 15:
                    st.markdown(f"""
                    <div class='warning-box'>
                        <h3>⚠️ Low Profit Margin</h3>
                        <p>Your profit margin is below 15%, which may be risky. Consider adjusting your pricing strategy or finding ways to reduce costs.</p>
                        <p>To achieve a 20% profit margin, your selling price should be at least ${result['landed_cost'] / 0.8:.2f}.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='result-box'>
                        <h3>✅ Healthy Profit Margin</h3>
                        <p>Your profit margin of {result['margin_percentage']:.1f}% is healthy. This product should be profitable at the current price and tariff rate.</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Scenario Modeling Tab
    with tabs[1]:
        st.markdown("<h2 class='sub-header'>Scenario Modeling</h2>", unsafe_allow_html=True)
        
        scenario_type = st.radio(
            "Choose scenario type:",
            ["Varying Tariff Rates", "Varying Price Points"]
        )
        
        # Input fields for scenario modeling
        col1, col2 = st.columns(2)
        
        if scenario_type == "Varying Tariff Rates":
            with col1:
                base_msrp = st.number_input("Fixed MSRP ($)", min_value=0.01, value=100.00, step=0.01, key="scen_msrp")
                base_cost = st.number_input("Manufacturing Cost per Unit ($)", min_value=0.01, value=50.00, step=0.01, key="scen_cost")
            
            with col2:
                min_tariff = st.number_input("Minimum Tariff Rate (%)", min_value=0, value=0, step=5)
                max_tariff = st.number_input("Maximum Tariff Rate (%)", min_value=1, value=100, step=5)
                steps = st.slider("Number of Scenarios", min_value=5, max_value=50, value=10)
        
        else:  # Varying Price Points
            with col1:
                fixed_tariff = st.number_input("Fixed Tariff Rate (%)", min_value=0, value=25, step=5)
                base_cost = st.number_input("Manufacturing Cost per Unit ($)", min_value=0.01, value=50.00, step=0.01, key="scen_cost2")
            
            with col2:
                min_price_factor = st.slider("Minimum Price Factor", min_value=0.5, max_value=0.99, value=0.8, step=0.01, 
                                            help="Minimum price as a factor of landed cost")
                max_price_factor = st.slider("Maximum Price Factor", min_value=1.01, max_value=5.0, value=2.0, step=0.1,
                                           help="Maximum price as a factor of landed cost")
                steps = st.slider("Number of Price Points", min_value=5, max_value=50, value=10)
        
        # Optional import costs
        with st.expander("Additional Import Costs (Optional)", expanded=False):
            col3, col4 = st.columns(2)
            
            with col3:
                shipping_cost_scen = st.number_input("Shipping Cost per Shipment ($)", min_value=0.0, value=1000.0, step=10.0, key="scen_ship")
                storage_cost_scen = st.number_input("Storage/Warehousing Cost ($)", min_value=0.0, value=0.0, step=10.0, key="scen_store")
                customs_fee_scen = st.number_input("Customs Processing Fee ($)", min_value=0.0, value=250.0, step=10.0, key="scen_customs")
            
            with col4:
                broker_fee_scen = st.number_input("Customs Broker Fee ($)", min_value=0.0, value=150.0, step=10.0, key="scen_broker")
                other_costs_scen = st.number_input("Other Import Costs ($)", min_value=0.0, value=0.0, step=10.0, key="scen_other")
                units_scen = st.number_input("Units per Shipment", min_value=1, value=1000, step=10, key="scen_units")
        
        # Generate scenarios button
        if st.button("Generate Scenarios"):
            with st.spinner("Generating scenarios..."):
                if scenario_type == "Varying Tariff Rates":
                    # Generate tariff scenarios
                    scenarios_df = generate_tariff_scenarios(
                        base_msrp, base_cost, min_tariff, max_tariff, steps,
                        shipping_cost_scen, storage_cost_scen, customs_fee_scen,
                        broker_fee_scen, other_costs_scen, units_scen
                    )
                    
                    # Format the dataframe for display
                    display_df = scenarios_df.copy()
                    display_df["tariff_rate"] = display_df["tariff_rate"].round(1).astype(str) + "%"
                    display_df["landed_cost"] = display_df["landed_cost"].round(2).map("${:.2f}".format)
                    display_df["profit"] = display_df["profit"].round(2).map("${:.2f}".format)
                    display_df["margin"] = display_df["margin"].round(1).astype(str) + "%"
                    display_df["breakeven_price"] = display_df["breakeven_price"].round(2).map("${:.2f}".format)
                    
                    display_df.columns = ["Tariff Rate", "Landed Cost", "Profit", "Margin", "Breakeven Price"]
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Create visualization
                    fig = go.Figure()
                    
                    # Add profit line
                    fig.add_trace(go.Scatter(
                        x=scenarios_df["tariff_rate"],
                        y=scenarios_df["profit"],
                        mode='lines+markers',
                        name='Profit per Unit',
                        line=dict(color='#4CAF50', width=3),
                        yaxis='y1'
                    ))
                    
                    # Add margin line
                    fig.add_trace(go.Scatter(
                        x=scenarios_df["tariff_rate"],
                        y=scenarios_df["margin"],
                        mode='lines+markers',
                        name='Profit Margin (%)',
                        line=dict(color='#2196F3', width=3, dash='dot'),
                        yaxis='y2'
                    ))
                    
                    # Update layout with dual y-axes
                    fig.update_layout(
                        title='Profitability at Different Tariff Rates',
                        xaxis=dict(title='Tariff Rate (%)'),
                        yaxis=dict(
                            title='Profit per Unit ($)',
                            titlefont=dict(color='#4CAF50'),
                            tickfont=dict(color='#4CAF50')
                        ),
                        yaxis2=dict(
                            title='Profit Margin (%)',
                            titlefont=dict(color='#2196F3'),
                            tickfont=dict(color='#2196F3'),
                            anchor='x',
                            overlaying='y',
                            side='right'
                        ),
                        legend=dict(x=0.01, y=0.99),
                        margin=dict(t=50, b=50, l=50, r=50),
                        hovermode='x unified'
                    )
                    
                    # Add zero line for profit reference
                    fig.add_shape(
                        type="line",
                        x0=min_tariff,
                        y0=0,
                        x1=max_tariff,
                        y1=0,
                        line=dict(color="red", width=2, dash="dot"),
                        yref='y1'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Find breakeven tariff rate
                    breakeven_tariff = None
                    for i in range(len(scenarios_df)-1):
                        if (scenarios_df.iloc[i]["profit"] >= 0 and scenarios_df.iloc[i+1]["profit"] < 0) or \
                           (scenarios_df.iloc[i]["profit"] <= 0 and scenarios_df.iloc[i+1]["profit"] > 0):
                            # Simple linear interpolation
                            rate1 = scenarios_df.iloc[i]["tariff_rate"]
                            rate2 = scenarios_df.iloc[i+1]["tariff_rate"]
                            profit1 = scenarios_df.iloc[i]["profit"]
                            profit2 = scenarios_df.iloc[i+1]["profit"]
                            
                            if profit1 == profit2:
                                breakeven_tariff = rate1
                            else:
                                breakeven_tariff = rate1 + (0 - profit1) * (rate2 - rate1) / (profit2 - profit1)
                            break
                    
                    if breakeven_tariff is not None:
                        st.markdown(f"""
                        <div class='result-box'>
                            <h3>Breakeven Tariff Rate: {breakeven_tariff:.1f}%</h3>
                            <p>At this tariff rate, your product will break even at the current MSRP of ${base_msrp:.2f}.</p>
                            <p>To remain profitable with higher tariff rates, you'll need to increase your selling price or reduce other costs.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        if scenarios_df["profit"].min() > 0:
                            st.markdown(f"""
                            <div class='result-box'>
                                <h3>Profitable Across All Scenarios</h3>
                                <p>Your product remains profitable at all tariff rates from {min_tariff}% to {max_tariff}% at the current MSRP of ${base_msrp:.2f}.</p>
                            </div>
                            """, unsafe_allow_html=True)
                        elif scenarios_df["profit"].max() < 0:
                            st.markdown(f"""
                            <div class='warning-box'>
                                <h3>Unprofitable Across All Scenarios</h3>
                                <p>Your product is not profitable at any tariff rate from {min_tariff}% to {max_tariff}% at the current MSRP of ${base_msrp:.2f}.</p>
                                <p>You need to increase your selling price or reduce manufacturing costs to achieve profitability.</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                else:  # Varying Price Points
                    # Generate price scenarios
                    scenarios_df = generate_price_scenarios(
                        fixed_tariff, base_cost, min_price_factor, max_price_factor, steps,
                        shipping_cost_scen, storage_cost_scen, customs_fee_scen,
                        broker_fee_scen, other_costs_scen, units_scen
                    )
                    
                    # Format the dataframe for display
                    display_df = scenarios_df.copy()
                    display_df["msrp"] = display_df["msrp"].round(2).map("${:.2f}".format)
                    display_df["profit"] = display_df["profit"].round(2).map("${:.2f}".format)
                    display_df["margin"] = display_df["margin"].round(1).astype(str) + "%"
                    display_df["landed_cost"] = display_df["landed_cost"].round(2).map("${:.2f}".format)
                    
                    display_df.columns = ["Selling Price", "Profit", "Margin", "Landed Cost"]
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Create visualization
                    fig = go.Figure()
                    
                    # Add profit line
                    fig.add_trace(go.Scatter(
                        x=scenarios_df["msrp"],
                        y=scenarios_df["profit"],
                        mode='lines+markers',
                        name='Profit per Unit',
                        line=dict(color='#4CAF50', width=3),
                        yaxis='y1'
                    ))
                    
                    # Add margin line
                    fig.add_trace(go.Scatter(
                        x=scenarios_df["msrp"],
                        y=scenarios_df["margin"],
                        mode='lines+markers',
                        name='Profit Margin (%)',
                        line=dict(color='#2196F3', width=3, dash='dot'),
                        yaxis='y2'
                    ))
                    
                    # Update layout with dual y-axes
                    fig.update_layout(
                        title=f'Profitability at Different Price Points ({fixed_tariff}% Tariff)',
                        xaxis=dict(title='Selling Price ($)'),
                        yaxis=dict(
                            title='Profit per Unit ($)',
                            titlefont=dict(color='#4CAF50'),
                            tickfont=dict(color='#4CAF50')
                        ),
                        yaxis2=dict(
                            title='Profit Margin (%)',
                            titlefont=dict(color='#2196F3'),
                            tickfont=dict(color='#2196F3'),
                            anchor='x',
                            overlaying='y',
                            side='right'
                        ),
                        legend=dict(x=0.01, y=0.99),
                        margin=dict(t=50, b=50, l=50, r=50),
                        hovermode='x unified'
                    )
                    
                    # Add zero line for profit reference
                    fig.add_shape(
                        type="line",
                        x0=scenarios_df["msrp"].min(),
                        y0=0,
                        x1=scenarios_df["msrp"].max(),
                        y1=0,
                        line=dict(color="red", width=2, dash="dot"),
                        yref='y1'
                    )
                    
                    # Add breakeven price marker
                    breakeven_price = scenarios_df.iloc[0]["landed_cost"]
                    fig.add_trace(go.Scatter(
                        x=[breakeven_price],
                        y=[0],
                        mode='markers',
                        marker=dict(size=12, color='red', symbol='star'),
                        name='Breakeven Price',
                        hoverinfo='text',
                        hovertext=f'Breakeven: ${breakeven_price:.2f}'
                    ))
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Find the price needed for 20% margin
                    target_margin = 20.0
                    target_price = None
                    
                    for i in range(len(scenarios_df)-1):
                        if (scenarios_df.iloc[i]["margin"] <= target_margin and scenarios_df.iloc[i+1]["margin"] > target_margin):
                            # Simple linear interpolation
                            price1 = scenarios_df.iloc[i]["msrp"]
                            price2 = scenarios_df.iloc[i+1]["msrp"]
                            margin1 = scenarios_df.iloc[i]["margin"]
                            margin2 = scenarios_df.iloc[i+1]["margin"]
                            
                            target_price = price1 + (target_margin - margin1) * (price2 - price1) / (margin2 - margin1)
                            break
                    
                    landed_cost = scenarios_df.iloc[0]["landed_cost"]
                    
                    if target_price is not None:
                        st.markdown(f"""
                        <div class='result-box'>
                            <h3>Pricing Recommendations</h3>
                            <ul>
                                <li><strong>Breakeven Price:</strong> ${landed_cost:.2f}</li>
                                <li><strong>Minimum Recommended Price:</strong> ${landed_cost * 1.05:.2f} (5% margin)</li>
                                <li><strong>Price for 20% Margin:</strong> ${target_price:.2f}</li>
                            </ul>
                            <p>With a {fixed_tariff}% tariff rate and your current cost structure, these are the key price points to consider.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='result-box'>
                            <h3>Pricing Recommendations</h3>
                            <ul>
                                <li><strong>Breakeven Price:</strong> ${landed_cost:.2f}</li>
                                <li><strong>Minimum Recommended Price:</strong> ${landed_cost * 1.05:.2f} (5% margin)</li>
                            </ul>
                            <p>With a {fixed_tariff}% tariff rate and your current cost structure, these are the key price points to consider.</p>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Tariff Resources Tab
    with tabs[2]:
        st.markdown("<h2 class='sub-header'>Tariff Resources</h2>", unsafe_allow_html=True)
        
        # Information about tariffs
        st.markdown("""
        <div class='info-box'>
            <h3>Understanding TariffSight: Import Cost Analyzers</h3>
            <p>Tariffs are taxes imposed on imported goods and services. They are typically calculated as a percentage of the import's value.</p>
            <p>Tariff rates vary widely based on:</p>
            <ul>
                <li>Product category and harmonized system (HS) code</li>
                <li>Country of origin</li>
                <li>Trade agreements between countries</li>
                <li>Special trade statuses or exceptions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Create two columns for resources
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h3>Official Tariff Resources</h3>", unsafe_allow_html=True)
            st.markdown("""
            * [U.S. International Trade Commission Tariff Database](https://hts.usitc.gov/) - Official HTSUS tariff information
            * [U.S. Customs and Border Protection](https://www.cbp.gov/trade/programs-administration/entry-summary/tariff-resources)
            * [European Union Trade Tariff Database](https://taxation-customs.ec.europa.eu/eu-customs-tariff_en)
            * [World Trade Organization Tariff Database](https://tao.wto.org/)
            """)
            
            st.markdown("<h3>Product Classification</h3>", unsafe_allow_html=True)
            st.markdown("""
            * [Harmonized System (HS) Classification](https://www.trade.gov/harmonized-system-hs-codes)
            * [Schedule B Search Engine](https://uscensus.prod.3ceonline.com/) - Find export codes for your products
            * [CROSS Rulings Database](https://rulings.cbp.gov/home) - Search customs rulings
            """)
        
        with col2:
            st.markdown("<h3>Trade Agreements & Resources</h3>", unsafe_allow_html=True)
            st.markdown("""
            * [USTR Free Trade Agreements](https://ustr.gov/trade-agreements/free-trade-agreements)
            * [International Trade Administration](https://www.trade.gov/)
            * [Global Trade Helpdesk](https://globaltradehelpdesk.org/en)
            * [CBP Trade Relief Programs](https://www.cbp.gov/trade/programs-administration/trade-remedies)
            """)
            
            st.markdown("<h3>Tariff Calculators & Tools</h3>", unsafe_allow_html=True)
            st.markdown("""
            * [CBP Duty Calculator](https://dataweb.usitc.gov/tariff/calculate)
            * [Shipping Solutions Trade Wizards](https://www.shippingsolutions.com/trade-wizards)
            * [Flexport Duty Calculator](https://www.flexport.com/tools/duty-calculator/)
            * [DHL Customs Duty Calculator](https://dhlguide.co.uk/tools-and-services/customs-duty-calculator/)
            """)
        
        # Recent tariff news
        st.markdown("<h3>Finding Current Tariff Rates</h3>", unsafe_allow_html=True)
        st.markdown("""
        To find the most current tariff rates for your specific product:
        
        1. **Determine your product's HS code** - This 6-10 digit classification code determines which tariff rates apply
        2. **Check the official tariff database** for your importing country (links above)
        3. **Consider country of origin** - Rates vary based on trade relationships
        4. **Check for special programs** - Various duty reduction or elimination programs may apply
        5. **Consult with a customs broker** - For complex products or situations, professional advice is recommended
        
        Remember that tariff rates can change due to policy changes, trade disputes, or new trade agreements.
        """)
        
        st.markdown("""
        <div class='warning-box'>
            <h3>Disclaimer</h3>
            <p>This calculator provides estimates only and should not be considered tax, legal, or customs advice. Actual duties, taxes, and fees may vary. Always consult with qualified customs professionals for official guidance.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display saved calculations
        if len(st.session_state.calculations) > 0:
            st.markdown("<h3>Your Recent Calculations</h3>", unsafe_allow_html=True)
            
            # Create a dataframe of saved calculations
            saved_df = pd.DataFrame(st.session_state.calculations)
            
            # Format for display
            display_saved = saved_df.copy()
            display_saved["msrp"] = display_saved["msrp"].map("${:.2f}".format)
            display_saved["cost"] = display_saved["cost"].map("${:.2f}".format)
            display_saved["tariff_rate"] = display_saved["tariff_rate"].astype(str) + "%"
            display_saved["landed_cost"] = display_saved["landed_cost"].map("${:.2f}".format)
            display_saved["profit"] = display_saved["profit"].map("${:.2f}".format)
            display_saved["margin"] = display_saved["margin"].round(1).astype(str) + "%"
            
            # Rename columns
            display_saved.columns = ["Timestamp", "Product", "SKU", "MSRP", "Manufacturing Cost", 
                                    "Tariff Rate", "Landed Cost", "Profit", "Margin"]
            
            st.dataframe(display_saved, use_container_width=True)
            
            if st.button("Clear History"):
                st.session_state.calculations = []
                st.rerun()

if __name__ == "__main__":
    main()
