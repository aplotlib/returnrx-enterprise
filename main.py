"""
KaizenROI - Smart Return Optimization Suite
A comprehensive analytics tool for evaluating e-commerce return reduction investments.

This application helps businesses analyze and optimize return reduction strategies
with precise ROI calculations, scenario planning, and interactive visualizations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timedelta
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import io
import json
import os
import time
import base64
from PIL import Image
from io import BytesIO

# App configuration
st.set_page_config(
    page_title="KaizenROI | Smart Return Optimization Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define color scheme
COLOR_SCHEME = {
    "primary": "#004366",
    "secondary": "#23b2be",
    "background": "#e6eff3",
    "positive": "#1e8449",
    "negative": "#922b21",
    "warning": "#f39c12",
    "neutral": "#3498db",
    "text_dark": "#2c3e50",
    "text_light": "#ecf0f1"
}

# Custom CSS
st.markdown("""
<style>
    /* Main styling */
    body, .stApp {
        background-color: #e6eff3;
        color: #2c3e50;
        font-family: 'Poppins', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        color: #004366;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #23b2be;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #004366;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Form styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 5px;
        border: 1px solid #bdc3c7;
    }
    
    /* Dataframe styling */
    .stDataFrame thead tr th {
        background-color: #23b2be;
        color: white;
        padding: 8px 12px;
        font-weight: 500;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background-color: rgba(236, 240, 241, 0.5);
    }
    .stDataFrame tbody tr:hover {
        background-color: rgba(52, 152, 219, 0.1);
    }
    
    /* Cards */
    .css-card {
        border-radius: 10px;
        padding: 1.5rem;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* Metric display */
    .metric-container {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 600;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0px 0px;
        padding: 8px 16px;
        background-color: #ecf0f1;
    }
    .stTabs [aria-selected="true"] {
        background-color: white;
        border-color: #23b2be;
        border-bottom: 3px solid #23b2be;
    }
    
    /* Tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #2c3e50;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Custom components */
    .info-box {
        background-color: rgba(52, 152, 219, 0.1);
        border-left: 5px solid #3498db;
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: rgba(243, 156, 18, 0.1);
        border-left: 5px solid #f39c12;
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    .loading-spinner {
        text-align: center;
        margin: 20px 0;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #004366;
    }
    .css-1d391kg .sidebar-content {
        padding: 1rem;
    }
    
    /* Charts */
    .js-plotly-plot {
        border-radius: 10px;
        background-color: white;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def format_currency(value):
    if pd.isna(value) or value is None:
        return "-"
    return f"${value:,.2f}"

def format_percent(value):
    if pd.isna(value) or value is None:
        return "-"
    return f"{value:.2f}%"

def format_number(value):
    if pd.isna(value) or value is None:
        return "-"
    return f"{value:,.2f}"

def get_icon(value, threshold=0, positive_is_good=True):
    if pd.isna(value) or value is None:
        return "❓"
    
    if positive_is_good:
        return "✅" if value >= threshold else "⚠️"
    else:
        return "✅" if value <= threshold else "⚠️"

def calculate_roi_score(roi, breakeven_days, reduction_rate):
    """Calculate a weighted ROI score with multiple factors"""
    if pd.isna(roi) or pd.isna(breakeven_days) or pd.isna(reduction_rate):
        return None
    
    # Lower breakeven days is better, normalize to 0-1 scale (max 365 days)
    breakeven_score = max(0, 1 - (breakeven_days / 365))
    
    # Higher ROI is better
    roi_score = min(1, roi / 5)  # Cap at 500% ROI
    
    # Higher reduction rate is better
    reduction_score = reduction_rate / 100
    
    # Weighted scoring (emphasize ROI and breakeven time)
    weighted_score = (roi_score * 0.5) + (breakeven_score * 0.35) + (reduction_score * 0.15)
    return weighted_score * 100  # Convert to 0-100 scale

def get_color_scale(value, min_val, max_val, reverse=False):
    """Get color from a green-yellow-red scale based on value"""
    if pd.isna(value) or value is None:
        return "#cccccc"  # Gray for null values
    
    # Normalize value to 0-1 range
    if max_val == min_val:
        normalized = 0.5
    else:
        normalized = (value - min_val) / (max_val - min_val)
    
    if reverse:
        normalized = 1 - normalized
    
    # Color scale: green (good) -> yellow (medium) -> red (poor)
    if normalized <= 0.33:
        color = "#e74c3c" if not reverse else "#2ecc71"  # Red / Green
    elif normalized <= 0.66:
        color = "#f39c12"  # Yellow/Orange
    else:
        color = "#2ecc71" if not reverse else "#e74c3c"  # Green / Red
    
    return color

# Data management
class ReturnOptimizer:
    def __init__(self):
        self.load_data()
        self.default_examples = [
            {
                "scenario_name": "Premium Packaging",
                "sku": "APPAREL-123",
                "sales_30": 750,
                "avg_sale_price": 89.99,
                "sales_channel": "Direct to Consumer",
                "returns_30": 94,
                "solution": "Premium unboxing experience with clearer sizing guide",
                "solution_cost": 5000,
                "additional_cost_per_item": 1.25,
                "current_unit_cost": 32.50,
                "reduction_rate": 30,
                "sales_365": 9125,
                "returns_365": 1140
            },
            {
                "scenario_name": "Size Verification Tool",
                "sku": "SHOES-456",
                "sales_30": 420,
                "avg_sale_price": 129.99,
                "sales_channel": "Shopify",
                "returns_30": 71,
                "solution": "Interactive size verification tool",
                "solution_cost": 7500,
                "additional_cost_per_item": 0,
                "current_unit_cost": 45.75,
                "reduction_rate": 35,
                "sales_365": 5100,
                "returns_365": 860
            },
            {
                "scenario_name": "Better Product Images",
                "sku": "HOME-789",
                "sales_30": 1250,
                "avg_sale_price": 49.99,
                "sales_channel": "Amazon",
                "returns_30": 138,
                "solution": "360° product views and improved images",
                "solution_cost": 3200,
                "additional_cost_per_item": 0,
                "current_unit_cost": 18.50,
                "reduction_rate": 25,
                "sales_365": 15200,
                "returns_365": 1675
            }
        ]

    def load_data(self):
        """Load data from session state or initialize empty dataframe"""
        if 'scenarios' not in st.session_state:
            self.scenarios = pd.DataFrame(columns=[
                'uid', 'scenario_name', 'sku', 'sales_30', 'avg_sale_price',
                'sales_channel', 'returns_30', 'return_rate', 'solution', 'solution_cost',
                'additional_cost_per_item', 'current_unit_cost', 'reduction_rate',
                'return_cost_30', 'return_cost_annual', 'revenue_impact_30',
                'revenue_impact_annual', 'new_unit_cost', 'savings_30',
                'annual_savings', 'break_even_days', 'break_even_months',
                'roi', 'score', 'timestamp', 'annual_additional_costs', 'net_benefit',
                'margin_before', 'margin_after', 'margin_after_amortized',
                'sales_365', 'returns_365', 'avoided_returns_30', 'avoided_returns_365',
                'monthly_net_benefit', 'tag'
            ])
            st.session_state['scenarios'] = self.scenarios
        else:
            self.scenarios = st.session_state['scenarios']
    
    def save_data(self):
        """Save data to session state"""
        st.session_state['scenarios'] = self.scenarios
    
    def download_json(self):
        """Get scenarios data as JSON string"""
        return self.scenarios.to_json(orient='records', date_format='iso')
    
    def upload_json(self, json_str):
        """Load scenarios from JSON string"""
        try:
            data = pd.read_json(json_str, orient='records')
            if not data.empty:
                # Ensure all required columns exist
                for col in self.scenarios.columns:
                    if col not in data.columns:
                        data[col] = None
                
                # Remove any extra columns
                data = data[self.scenarios.columns]
                
                self.scenarios = data
                self.save_data()
                return True
            return False
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False

    def add_scenario(self, scenario_name, sku, sales_30, avg_sale_price, sales_channel,
                     returns_30, solution, solution_cost, additional_cost_per_item,
                     current_unit_cost, reduction_rate, sales_365=None, returns_365=None, tag=None):
        """Add a new scenario with calculations"""
        try:
            # Validate inputs
            if not sku or not scenario_name:
                return False, "SKU and Scenario Name are required"
            
            if sales_30 <= 0:
                return False, "Sales must be greater than zero"
            
            if returns_30 > sales_30:
                return False, "Returns cannot exceed sales"
            
            if current_unit_cost <= 0 or avg_sale_price <= 0:
                return False, "Unit cost and sale price must be greater than zero"
            
            if avg_sale_price <= current_unit_cost:
                return False, "Sale price must be greater than unit cost"
            
            # Use defaults if not provided
            if not scenario_name:
                scenario_name = f"Scenario {len(self.scenarios) + 1}"
            
            # Fill in calculations
            uid = str(uuid.uuid4())[:8]
            return_rate = (returns_30 / sales_30) * 100 if sales_30 else 0
            
            # If 365-day data not provided, extrapolate from 30-day
            if sales_365 is None or sales_365 <= 0:
                sales_365 = sales_30 * 12
            
            if returns_365 is None or returns_365 <= 0:
                returns_365 = returns_30 * 12
            
            # Calculate avoided returns
            avoided_returns_30 = returns_30 * (reduction_rate / 100)
            avoided_returns_365 = returns_365 * (reduction_rate / 100)
            
            # Calculate costs and benefits
            return_cost_30 = returns_30 * current_unit_cost
            return_cost_annual = returns_365 * current_unit_cost
            revenue_impact_30 = returns_30 * avg_sale_price
            revenue_impact_annual = returns_365 * avg_sale_price
            new_unit_cost = current_unit_cost + additional_cost_per_item

            # Calculate margins
            margin_before = avg_sale_price - current_unit_cost
            margin_after = avg_sale_price - new_unit_cost
            
            # Calculate amortized cost per unit
            amortized_solution_cost = solution_cost / sales_365 if sales_365 > 0 else 0
            margin_after_amortized = margin_after - amortized_solution_cost
            
            # Calculate savings and ROI
            savings_per_avoided_return = avg_sale_price - new_unit_cost
            savings_30 = avoided_returns_30 * savings_per_avoided_return
            annual_savings = avoided_returns_365 * savings_per_avoided_return
            
            annual_additional_costs = additional_cost_per_item * sales_365
            net_benefit = annual_savings - annual_additional_costs
            monthly_net_benefit = net_benefit / 12
            
            # Calculate ROI metrics
            roi = break_even_days = break_even_months = score = None
            if solution_cost > 0 and net_benefit > 0:
                roi = (net_benefit / solution_cost) * 100  # as percentage
                break_even_days = (solution_cost / net_benefit) * 365
                break_even_months = break_even_days / 30
                score = calculate_roi_score(roi/100, break_even_days, reduction_rate)
            
            # Create new row
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
                'returns_365': returns_365,
                'avoided_returns_30': avoided_returns_30,
                'avoided_returns_365': avoided_returns_365,
                'monthly_net_benefit': monthly_net_benefit,
                'tag': tag
            }

            # Add to dataframe
            self.scenarios = pd.concat([self.scenarios, pd.DataFrame([new_row])], ignore_index=True)
            self.save_data()
            return True, "Scenario added successfully!"
        except Exception as e:
            return False, f"Error adding scenario: {str(e)}"
    
    def get_scenario(self, uid):
        """Get a scenario by UID"""
        if uid in self.scenarios['uid'].values:
            return self.scenarios[self.scenarios['uid'] == uid].iloc[0].to_dict()
        return None
    
    def delete_scenario(self, uid):
        """Delete a scenario by UID"""
        if uid in self.scenarios['uid'].values:
            self.scenarios = self.scenarios[self.scenarios['uid'] != uid]
            self.save_data()
            return True
        return False
    
    def update_scenario(self, uid, **kwargs):
        """Update a scenario and recalculate values"""
        if uid not in self.scenarios['uid'].values:
            return False, "Scenario not found"
        
        # Get current values
        current = self.get_scenario(uid)
        if not current:
            return False, "Failed to retrieve scenario data"
        
        # Update with new values
        for key, value in kwargs.items():
            if key in current:
                current[key] = value
        
        # Delete current scenario
        self.delete_scenario(uid)
        
        # Add updated scenario
        success, message = self.add_scenario(
            current['scenario_name'], current['sku'], current['sales_30'],
            current['avg_sale_price'], current['sales_channel'], current['returns_30'],
            current['solution'], current['solution_cost'], current['additional_cost_per_item'],
            current['current_unit_cost'], current['reduction_rate'],
            current['sales_365'], current['returns_365'], current['tag']
        )
        
        return success, message
    
    def add_example_scenarios(self):
        """Add example scenarios for demonstration"""
        added = 0
        for example in self.default_examples:
            success, _ = self.add_scenario(**example)
            if success:
                added += 1
        return added

    def clone_scenario(self, uid, new_name=None):
        """Clone an existing scenario"""
        if uid not in self.scenarios['uid'].values:
            return False, "Scenario not found"
        
        scenario = self.get_scenario(uid)
        if not scenario:
            return False, "Failed to retrieve scenario data"
        
        # Create new name if not provided
        if not new_name:
            new_name = f"{scenario['scenario_name']} (Clone)"
        
        # Clone scenario
        success, message = self.add_scenario(
            new_name, scenario['sku'], scenario['sales_30'],
            scenario['avg_sale_price'], scenario['sales_channel'], scenario['returns_30'],
            scenario['solution'], scenario['solution_cost'], scenario['additional_cost_per_item'],
            scenario['current_unit_cost'], scenario['reduction_rate'],
            scenario['sales_365'], scenario['returns_365'], scenario['tag']
        )
        
        return success, message

# Initialize app
if 'optimizer' not in st.session_state:
    st.session_state.optimizer = ReturnOptimizer()
optimizer = st.session_state.optimizer

# App functions
def display_header():
    """Display app header with logo and navigation"""
    col1, col2 = st.columns([1, 5])
    
    # Logo (placeholder - in a real app, replace with actual logo)
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 10px">
            <h1 style="font-size: 32px; margin: 0; color: #004366;">🔄</h1>
            <p style="margin: 0; font-weight: 600; color: #23b2be;">KaizenROI</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Title and description
    with col2:
        st.title("Smart Return Optimization Suite")
        st.caption("Evaluate return reduction investments with precision to improve bottom-line performance.")

def display_metrics_overview(df):
    """Display key metrics overview cards"""
    if df.empty:
        st.info("Add or generate scenarios to see metrics.")
        return
    
    # Calculate aggregate metrics
    total_scenarios = len(df)
    avg_roi = df['roi'].mean()
    avg_break_even = df['break_even_months'].mean()
    total_net_benefit = df['net_benefit'].sum()
    total_investment = df['solution_cost'].sum()
    portfolio_roi = (total_net_benefit / total_investment * 100) if total_investment > 0 else 0
    
    # Display metrics in cards
    st.subheader("Portfolio Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Total Scenarios</p>
            <p class="metric-value" style="color: {COLOR_SCHEME['primary']};">{total_scenarios}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Portfolio ROI</p>
            <p class="metric-value" style="color: {get_color_scale(portfolio_roi, 0, 300)};">{format_percent(portfolio_roi)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Total Net Benefit</p>
            <p class="metric-value" style="color: {get_color_scale(total_net_benefit, 0, total_net_benefit*1.5)};">{format_currency(total_net_benefit)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Avg. Break-even</p>
            <p class="metric-value" style="color: {get_color_scale(avg_break_even, 0, 12, reverse=True)};">{format_number(avg_break_even)} months</p>
        </div>
        """, unsafe_allow_html=True)

def create_scenario_form():
    """Create form for adding a new scenario"""
    with st.form(key="scenario_form"):
        st.subheader("Add New Scenario")
        
        col1, col2 = st.columns(2)
        with col1:
            scenario_name = st.text_input("Scenario Name", help="A memorable name for this return reduction scenario")
            sku = st.text_input("SKU/Product ID", help="Product identifier")
            sales_channel = st.text_input("Sales Channel", help="Main platform where product is sold")
            solution = st.text_input("Proposed Solution", help="Description of the return reduction strategy")
            tag = st.selectbox("Category Tag", 
                              ["Packaging", "Product Description", "Size/Fit", "Quality", "Customer Education", "Other"],
                              help="Category of return reduction strategy")
        
        with col2:
            sales_30 = st.number_input("30-day Sales (units)", min_value=0, help="Units sold in the last 30 days")
            returns_30 = st.number_input("30-day Returns (units)", min_value=0, help="Units returned in the last 30 days")
            avg_sale_price = st.number_input("Average Sale Price ($)", min_value=0.0, format="%.2f", help="Average selling price per unit")
            current_unit_cost = st.number_input("Current Unit Cost ($)", min_value=0.0, format="%.2f", help="Cost to produce/acquire each unit")
            
        st.markdown("---")
        col3, col4 = st.columns(2)
        
        with col3:
            solution_cost = st.number_input("Total Solution Cost ($)", min_value=0.0, format="%.2f", 
                                          help="One-time investment required for the solution")
            additional_cost_per_item = st.number_input("Additional Cost per Item ($)", min_value=0.0, format="%.2f", 
                                                   help="Any additional per-unit cost from implementing the solution")
        
        with col4:
            reduction_rate = st.slider("Estimated Return Reduction (%)", 0, 100, 20, 
                                    help="Expected percentage reduction in returns after implementing the solution")
            
            # Optional annual data
            st.markdown("##### Annual Data (Optional)")
            annual_data = st.checkbox("Use custom annual data", help="By default, 30-day data is multiplied by 12")
            
            if annual_data:
                sales_365 = st.number_input("365-day Sales (units)", min_value=0, 
                                        help="Total units sold in a year (defaults to 30-day * 12)")
                returns_365 = st.number_input("365-day Returns (units)", min_value=0, 
                                           help="Total units returned in a year (defaults to 30-day * 12)")
            else:
                sales_365 = sales_30 * 12
                returns_365 = returns_30 * 12
        
        # Calculate and preview stats
        if sales_30 > 0 and returns_30 > 0:
            return_rate = (returns_30 / sales_30) * 100
            avoided_returns = returns_30 * (reduction_rate / 100)
            
            st.markdown("### Preview Calculations")
            preview_col1, preview_col2, preview_col3 = st.columns(3)
            
            with preview_col1:
                st.metric("Current Return Rate", f"{return_rate:.2f}%")
                st.metric("Monthly Returns Value", f"${returns_30 * avg_sale_price:,.2f}")
            
            with preview_col2:
                st.metric("Avoided Returns (Monthly)", f"{avoided_returns:.1f} units")
                st.metric("New Return Rate", f"{return_rate * (1 - reduction_rate/100):.2f}%")
            
            with preview_col3:
                # Simple ROI calculation for preview
                monthly_cost = additional_cost_per_item * sales_30
                monthly_savings = avoided_returns * (avg_sale_price - (current_unit_cost + additional_cost_per_item))
                monthly_net = monthly_savings - monthly_cost
                
                if solution_cost > 0 and monthly_net > 0:
                    breakeven_months = solution_cost / monthly_net
                    st.metric("Estimated Breakeven", f"{breakeven_months:.1f} months")
                    st.metric("Est. Annual ROI", f"{(monthly_net * 12 / solution_cost) * 100:.1f}%")
                else:
                    st.metric("Estimated Breakeven", "N/A")
                    st.metric("Est. Annual ROI", "N/A")
        
        # Submit button
        submitted = st.form_submit_button("Save Scenario")
        
        if submitted:
            success, message = optimizer.add_scenario(
                scenario_name, sku, sales_30, avg_sale_price, sales_channel,
                returns_30, solution, solution_cost, additional_cost_per_item,
                current_unit_cost, reduction_rate, sales_365, returns_365, tag
            )
            
            if success:
                st.success(message)
                return True
            else:
                st.error(message)
                return False
    
    return False

def display_scenario_table(df):
    """Display scenario table with filtering and sorting"""
    if df.empty:
        st.info("No scenarios found. Add a new scenario or load example scenarios.")
        return
    
    # Add filters
    st.subheader("Scenario Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sku_filter = st.multiselect("Filter by SKU", 
                                   options=sorted(df['sku'].unique()),
                                   default=[])
    
    with col2:
        channel_filter = st.multiselect("Filter by Sales Channel", 
                                      options=sorted(df['sales_channel'].unique()),
                                      default=[])
    
    with col3:
        tag_filter = st.multiselect("Filter by Category", 
                                  options=sorted(df['tag'].dropna().unique()),
                                  default=[])
    
    # Apply filters
    filtered_df = df.copy()
    
    if sku_filter:
        filtered_df = filtered_df[filtered_df['sku'].isin(sku_filter)]
    
    if channel_filter:
        filtered_df = filtered_df[filtered_df['sales_channel'].isin(channel_filter)]
    
    if tag_filter:
        filtered_df = filtered_df[filtered_df['tag'].isin(tag_filter)]
    
    # Display table
    if filtered_df.empty:
        st.warning("No scenarios match your filters. Try adjusting your criteria.")
        return
    
    # Prepare display columns
    display_df = filtered_df[[
        'uid', 'scenario_name', 'sku', 'sales_channel', 'return_rate',
        'solution_cost', 'reduction_rate', 'roi', 'break_even_months',
        'net_benefit', 'score'
    ]].copy()
    
    # Format columns for display
    display_df['return_rate'] = display_df['return_rate'].apply(lambda x: f"{x:.1f}%")
    display_df['solution_cost'] = display_df['solution_cost'].apply(lambda x: f"${x:,.2f}")
    display_df['reduction_rate'] = display_df['reduction_rate'].apply(lambda x: f"{x:.0f}%")
    display_df['roi'] = display_df['roi'].apply(lambda x: f"{x:.1f}%" if not pd.isna(x) else "N/A")
    display_df['break_even_months'] = display_df['break_even_months'].apply(lambda x: f"{x:.1f}" if not pd.isna(x) else "N/A")
    display_df['net_benefit'] = display_df['net_benefit'].apply(lambda x: f"${x:,.2f}")
    
    # Add color-coded score column
    def format_score(row):
        score = row['score']
        if pd.isna(score):
            return "N/A"
        
        color = get_color_scale(score, 0, 100)
        return f"<span style='color: {color}; font-weight: bold;'>{score:.1f}</span>"
    
    display_df['score'] = filtered_df.apply(format_score, axis=1)
    
    # Rename columns for display
    display_df = display_df.rename(columns={
        'scenario_name': 'Scenario',
        'sku': 'SKU',
        'sales_channel': 'Channel',
        'return_rate': 'Return Rate',
        'solution_cost': 'Investment',
        'reduction_rate': 'Reduction',
        'roi': 'ROI',
        'break_even_months': 'Break-even',
        'net_benefit': 'Net Benefit',
        'score': 'ROI Score'
    })
    
    # Hide UID column
    display_df = display_df.drop('uid', axis=1)
    
    # Display interactive table
    st.dataframe(display_df.reset_index(drop=True), use_container_width=True, 
               column_config={
                   "ROI Score": st.column_config.Column(
                       "ROI Score",
                       help="Combined score based on ROI, breakeven time, and reduction rate",
                       width="medium"
                   )
               },
               hide_index=True)
    
    # Action buttons for selected scenario
    if not filtered_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            selected_scenario = st.selectbox("Select scenario for actions:", 
                                         filtered_df['scenario_name'].tolist())
        
        selected_uid = filtered_df[filtered_df['scenario_name'] == selected_scenario]['uid'].iloc[0]
        
        with col2:
            if st.button("View Details", key="view_btn"):
                st.session_state['selected_scenario'] = selected_uid
                st.session_state['view_scenario'] = True
        
        with col3:
            if st.button("Clone", key="clone_btn"):
                success, message = optimizer.clone_scenario(selected_uid)
                if success:
                    st.success(f"Scenario cloned successfully!")
                else:
                    st.error(message)
        
        with col4:
            if st.button("Delete", key="delete_btn"):
                if optimizer.delete_scenario(selected_uid):
                    st.success(f"Scenario '{selected_scenario}' deleted successfully.")
                else:
                    st.error("Failed to delete scenario.")

def display_scenario_details(uid):
    """Display detailed view of a scenario"""
    scenario = optimizer.get_scenario(uid)
    if not scenario:
        st.error("Scenario not found")
        return
    
    st.subheader(f"Scenario Details: {scenario['scenario_name']}")
    
    # Basic info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**SKU:** {scenario['sku']}")
        st.markdown(f"**Sales Channel:** {scenario['sales_channel']}")
        st.markdown(f"**Category:** {scenario['tag'] or 'Not categorized'}")
    
    with col2:
        st.markdown(f"**Monthly Sales:** {scenario['sales_30']} units")
        st.markdown(f"**Monthly Returns:** {scenario['returns_30']} units")
        st.markdown(f"**Return Rate:** {scenario['return_rate']:.2f}%")
    
    with col3:
        st.markdown(f"**Average Sale Price:** ${scenario['avg_sale_price']:.2f}")
        st.markdown(f"**Current Unit Cost:** ${scenario['current_unit_cost']:.2f}")
        st.markdown(f"**Current Margin:** ${scenario['margin_before']:.2f} ({(scenario['margin_before']/scenario['avg_sale_price']*100):.1f}%)")
    
    # Solution details
    st.markdown("---")
    st.markdown("### Solution Details")
    
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown(f"**Proposed Solution:** {scenario['solution']}")
        st.markdown(f"**Expected Reduction:** {scenario['reduction_rate']:.1f}%")
        st.markdown(f"**Additional Cost/Item:** ${scenario['additional_cost_per_item']:.2f}")
    
    with col5:
        st.markdown(f"**Solution Investment:** ${scenario['solution_cost']:.2f}")
        st.markdown(f"**New Unit Cost:** ${scenario['new_unit_cost']:.2f}")
        st.markdown(f"**New Margin:** ${scenario['margin_after']:.2f} ({(scenario['margin_after']/scenario['avg_sale_price']*100):.1f}%)")
    
    # Financial impacts
    st.markdown("---")
    st.markdown("### Financial Impact")
    
    # Create metrics cards for key financial data
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        st.metric(
            "Monthly Savings",
            f"${scenario['savings_30']:.2f}",
            delta=None
        )
    
    with metrics_col2:
        st.metric(
            "Annual Net Benefit",
            f"${scenario['net_benefit']:.2f}",
            delta=None
        )
    
    with metrics_col3:
        if pd.notna(scenario['roi']):
            st.metric(
                "Return on Investment",
                f"{scenario['roi']:.1f}%",
                delta=None
            )
        else:
            st.metric("Return on Investment", "N/A", delta=None)
    
    with metrics_col4:
        if pd.notna(scenario['break_even_months']):
            st.metric(
                "Break-even Time",
                f"{scenario['break_even_months']:.1f} months",
                delta=None
            )
        else:
            st.metric("Break-even Time", "N/A", delta=None)
    
    # Cost breakdown
    st.markdown("### Cost-Benefit Analysis")
    cost_col1, cost_col2 = st.columns(2)
    
    with cost_col1:
        # Cost breakdown
        cost_data = [
            {"Category": "Solution Investment", "Amount": scenario['solution_cost']},
            {"Category": "Annual Additional Costs", "Amount": scenario['annual_additional_costs']}
        ]
        cost_df = pd.DataFrame(cost_data)
        
        fig_cost = px.bar(
            cost_df, 
            x="Category", 
            y="Amount",
            title="Costs",
            color="Category",
            color_discrete_map={
                "Solution Investment": COLOR_SCHEME["warning"],
                "Annual Additional Costs": COLOR_SCHEME["negative"]
            }
        )
        fig_cost.update_layout(
            xaxis_title="",
            yaxis_title="Amount ($)",
            showlegend=False
        )
        st.plotly_chart(fig_cost, use_container_width=True)
    
    with cost_col2:
        # Benefit breakdown
        benefit_data = [
            {"Category": "Annual Savings", "Amount": scenario['annual_savings']},
            {"Category": "Net Benefit", "Amount": scenario['net_benefit']}
        ]
        benefit_df = pd.DataFrame(benefit_data)
        
        fig_benefit = px.bar(
            benefit_df, 
            x="Category", 
            y="Amount",
            title="Benefits",
            color="Category",
            color_discrete_map={
                "Annual Savings": COLOR_SCHEME["positive"],
                "Net Benefit": COLOR_SCHEME["neutral"]
            }
        )
        fig_benefit.update_layout(
            xaxis_title="",
            yaxis_title="Amount ($)",
            showlegend=False
        )
        st.plotly_chart(fig_benefit, use_container_width=True)
    
    # Return reduction impact
    st.markdown("### Return Reduction Impact")
    
    # Create data for before/after comparison
    before_after_data = {
        "State": ["Before", "After"],
        "Returns": [scenario['returns_365'], scenario['returns_365'] - scenario['avoided_returns_365']],
        "Return Rate": [scenario['return_rate'], scenario['return_rate'] * (1 - scenario['reduction_rate']/100)]
    }
    before_after_df = pd.DataFrame(before_after_data)
    
    fig_returns = make_subplots(rows=1, cols=2, subplot_titles=["Annual Returns", "Return Rate"])
    
    # Annual returns chart
    fig_returns.add_trace(
        go.Bar(
            x=before_after_df["State"],
            y=before_after_df["Returns"],
            marker_color=[COLOR_SCHEME["negative"], COLOR_SCHEME["positive"]],
            text=before_after_df["Returns"].apply(lambda x: f"{x:.0f}"),
            textposition="auto"
        ),
        row=1, col=1
    )
    
    # Return rate chart
    fig_returns.add_trace(
        go.Bar(
            x=before_after_df["State"],
            y=before_after_df["Return Rate"],
            marker_color=[COLOR_SCHEME["negative"], COLOR_SCHEME["positive"]],
            text=before_after_df["Return Rate"].apply(lambda x: f"{x:.1f}%"),
            textposition="auto"
        ),
        row=1, col=2
    )
    
    fig_returns.update_layout(
        height=400,
        showlegend=False,
        title_text="Before vs After Implementation"
    )
    
    fig_returns.update_yaxes(title_text="Units", row=1, col=1)
    fig_returns.update_yaxes(title_text="Percentage", row=1, col=2)
    
    st.plotly_chart(fig_returns, use_container_width=True)
    
    # Margin impact
    st.markdown("### Margin Impact")
    
    # Create data for margin comparison
    margin_data = {
        "Type": ["Current Margin", "New Margin", "Margin After Amortization"],
        "Margin": [
            scenario['margin_before'],
            scenario['margin_after'],
            scenario['margin_after_amortized']
        ],
        "Margin %": [
            (scenario['margin_before'] / scenario['avg_sale_price']) * 100,
            (scenario['margin_after'] / scenario['avg_sale_price']) * 100,
            (scenario['margin_after_amortized'] / scenario['avg_sale_price']) * 100
        ]
    }
    margin_df = pd.DataFrame(margin_data)
    
    fig_margin = make_subplots(rows=1, cols=2, subplot_titles=["Margin ($)", "Margin (%)"])
    
    # Margin $ chart
    fig_margin.add_trace(
        go.Bar(
            x=margin_df["Type"],
            y=margin_df["Margin"],
            marker_color=[
                COLOR_SCHEME["neutral"],
                COLOR_SCHEME["secondary"],
                COLOR_SCHEME["primary"]
            ],
            text=margin_df["Margin"].apply(lambda x: f"${x:.2f}"),
            textposition="auto"
        ),
        row=1, col=1
    )
    
    # Margin % chart
    fig_margin.add_trace(
        go.Bar(
            x=margin_df["Type"],
            y=margin_df["Margin %"],
            marker_color=[
                COLOR_SCHEME["neutral"],
                COLOR_SCHEME["secondary"],
                COLOR_SCHEME["primary"]
            ],
            text=margin_df["Margin %"].apply(lambda x: f"{x:.1f}%"),
            textposition="auto"
        ),
        row=1, col=2
    )
    
    fig_margin.update_layout(
        height=400,
        showlegend=False,
        title_text="Margin Comparison"
    )
    
    fig_margin.update_yaxes(title_text="Amount ($)", row=1, col=1)
    fig_margin.update_yaxes(title_text="Percentage", row=1, col=2)
    
    st.plotly_chart(fig_margin, use_container_width=True)
    
    # Return to dashboard button
    if st.button("← Return to Dashboard"):
        st.session_state['view_scenario'] = False
        st.session_state['selected_scenario'] = None
        st.experimental_rerun()

def display_portfolio_analysis(df):
    """Display portfolio-level analysis and visualizations"""
    if df.empty:
        st.info("Add scenarios to see portfolio analysis.")
        return
    
    st.subheader("Portfolio Analysis")
    
    # ROI bubble chart
    st.markdown("### Investment ROI Analysis")
    
    # Prepare data
    plot_df = df.dropna(subset=['roi', 'break_even_months', 'net_benefit']).copy()
    
    if plot_df.empty:
        st.warning("No scenarios with complete ROI data available.")
        return
    
    # Size is proportional to net benefit
    size_max = 50
    plot_df['bubble_size'] = size_max * (plot_df['net_benefit'] / plot_df['net_benefit'].max())
    plot_df['bubble_size'] = plot_df['bubble_size'].apply(lambda x: max(10, x))  # Minimum size
    
    # Create the bubble chart
    fig_bubble = px.scatter(
        plot_df,
        x="break_even_months",
        y="roi",
        size="bubble_size",
        color="score",
        color_continuous_scale=px.colors.sequential.Viridis,
        hover_name="scenario_name",
        text="scenario_name",
        size_max=size_max,
        labels={
            "break_even_months": "Break-even Time (months)",
            "roi": "Return on Investment (%)",
            "score": "ROI Score"
        },
        title="Investment ROI vs. Break-even Time"
    )
    
    # Quadrant lines (12 month breakeven, 100% ROI)
    fig_bubble.add_shape(
        type="line",
        x0=12, y0=0,
        x1=12, y1=plot_df['roi'].max() * 1.1,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    fig_bubble.add_shape(
        type="line",
        x0=0, y0=100,
        x1=plot_df['break_even_months'].max() * 1.1, y1=100,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    # Add quadrant labels
    avg_x = plot_df['break_even_months'].max() * 0.75
    avg_y = plot_df['roi'].max() * 0.75
    
    fig_bubble.add_annotation(
        x=6, y=avg_y,
        text="IDEAL: High ROI, Fast Payback",
        showarrow=False,
        font=dict(color="green", size=10)
    )
    
    fig_bubble.add_annotation(
        x=avg_x, y=avg_y,
        text="GOOD: High ROI, Slow Payback",
        showarrow=False,
        font=dict(color="blue", size=10)
    )
    
    fig_bubble.add_annotation(
        x=6, y=50,
        text="CONSIDER: Low ROI, Fast Payback",
        showarrow=False,
        font=dict(color="orange", size=10)
    )
    
    fig_bubble.add_annotation(
        x=avg_x, y=50,
        text="AVOID: Low ROI, Slow Payback",
        showarrow=False,
        font=dict(color="red", size=10)
    )
    
    fig_bubble.update_traces(textposition='top center')
    fig_bubble.update_layout(height=600)
    
    st.plotly_chart(fig_bubble, use_container_width=True)
    
    # Return rate by category analysis
    if 'tag' in df.columns and not df['tag'].isna().all():
        st.markdown("### Return Rate by Category")
        
        # Group by tag
        tag_group = df.groupby('tag').agg({
            'returns_30': 'sum',
            'sales_30': 'sum',
            'solution_cost': 'sum',
            'net_benefit': 'sum'
        }).reset_index()
        
        # Calculate return rate
        tag_group['return_rate'] = (tag_group['returns_30'] / tag_group['sales_30']) * 100
        
        # Create the bar chart
        fig_tags = px.bar(
            tag_group,
            x="tag",
            y="return_rate",
            color="net_benefit",
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={
                "tag": "Category",
                "return_rate": "Return Rate (%)",
                "net_benefit": "Net Benefit ($)"
            },
            title="Return Rate by Category with Net Benefit Overlay"
        )
        
        fig_tags.update_layout(height=400)
        st.plotly_chart(fig_tags, use_container_width=True)
    
    # Comparative analysis
    st.markdown("### Comparative ROI Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # ROI by solution type
        solution_group = df.groupby('solution').agg({
            'roi': 'mean',
            'solution_cost': 'sum',
            'net_benefit': 'sum'
        }).reset_index()
        
        fig_solution = px.bar(
            solution_group,
            x="solution",
            y="roi",
            color="net_benefit",
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={
                "solution": "Solution",
                "roi": "Average ROI (%)",
                "net_benefit": "Net Benefit ($)"
            },
            title="ROI by Solution Type"
        )
        
        fig_solution.update_layout(height=400)
        st.plotly_chart(fig_solution, use_container_width=True)
    
    with col2:
        # ROI by sales channel
        channel_group = df.groupby('sales_channel').agg({
            'roi': 'mean',
            'solution_cost': 'sum',
            'net_benefit': 'sum'
        }).reset_index()
        
        fig_channel = px.bar(
            channel_group,
            x="sales_channel",
            y="roi",
            color="net_benefit",
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={
                "sales_channel": "Sales Channel",
                "roi": "Average ROI (%)",
                "net_benefit": "Net Benefit ($)"
            },
            title="ROI by Sales Channel"
        )
        
        fig_channel.update_layout(height=400)
        st.plotly_chart(fig_channel, use_container_width=True)

def display_what_if_analysis():
    """Interactive what-if scenario analysis"""
    st.subheader("What-If Analysis")
    
    # Get base scenario
    if not optimizer.scenarios.empty:
        # Let user select a base scenario
        scenario_names = optimizer.scenarios['scenario_name'].tolist()
        base_scenario_name = st.selectbox("Select base scenario for what-if analysis", scenario_names)
        
        # Get the selected scenario
        base_scenario = optimizer.scenarios[optimizer.scenarios['scenario_name'] == base_scenario_name].iloc[0]
        
        # Set up what-if parameters
        st.markdown("### Adjust Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sales volume change
            sales_change = st.slider(
                "Sales Volume Change (%)", 
                min_value=-50, 
                max_value=100, 
                value=0,
                help="Adjust projected monthly sales volume. For example, +20% means monthly sales will increase by 20% compared to the base scenario. This affects both revenue and per-unit cost allocation."
            )
            
            # Return rate change
            return_rate_change = st.slider(
                "Return Rate Change (%)", 
                min_value=-50, 
                max_value=50, 
                value=0,
                help="Adjust the projected return rate relative to current rate. For example, if current return rate is 10%, a +20% change means the new return rate would be 12% (10% × 1.2)."
            )
            
            # Solution cost change
            solution_cost_change = st.slider(
                "Solution Cost Change (%)", 
                min_value=-50, 
                max_value=100, 
                value=0,
                help="Adjust the one-time implementation cost of the solution. For example, -20% means the solution will cost 20% less than the original estimate."
            )
        
        with col2:
            # Reduction effectiveness change
            reduction_effectiveness = st.slider(
                "Return Reduction Effectiveness (%)", 
                min_value=-50, 
                max_value=50, 
                value=0,
                help="Adjust how effective the solution is at reducing returns compared to the initial estimate. For example, if you originally estimated a 30% reduction in returns, a +20% effectiveness change means the actual reduction would be 36% (30% × 1.2)."
            )
            
            # Additional cost change
            additional_cost_change = st.slider(
                "Additional Cost per Item Change (%)", 
                min_value=-50, 
                max_value=100, 
                value=0,
                help="Adjust the ongoing additional cost per unit that results from implementing the solution. For example, if the original additional cost was $1.00 per unit, a +10% change would mean $1.10 per unit."
            )
            
            # Average sale price change
            price_change = st.slider(
                "Average Sale Price Change (%)", 
                min_value=-25, 
                max_value=25, 
                value=0,
                help="Adjust the average selling price of the product. This affects both revenue from sales and the value recovered from avoided returns. For example, a +5% change means products will sell for 5% more than in the base scenario."
            )
        
        # Calculate new values
        new_sales_30 = base_scenario['sales_30'] * (1 + sales_change/100)
        new_return_rate = base_scenario['return_rate'] * (1 + return_rate_change/100)
        new_returns_30 = (new_sales_30 * new_return_rate / 100)
        new_solution_cost = base_scenario['solution_cost'] * (1 + solution_cost_change/100)
        new_reduction_rate = base_scenario['reduction_rate'] * (1 + reduction_effectiveness/100)
        new_additional_cost = base_scenario['additional_cost_per_item'] * (1 + additional_cost_change/100)
        new_avg_price = base_scenario['avg_sale_price'] * (1 + price_change/100)
        
        # Ensure values are within logical bounds
        new_reduction_rate = min(100, max(0, new_reduction_rate))
        new_return_rate = min(100, max(0, new_return_rate))
        
        # Create comparison dataframes
        comparison_data = {
            "Metric": [
                "Monthly Sales (units)",
                "Return Rate (%)",
                "Monthly Returns (units)",
                "Solution Cost ($)",
                "Return Reduction (%)",
                "Additional Cost/Item ($)",
                "Average Sale Price ($)"
            ],
            "Original": [
                base_scenario['sales_30'],
                base_scenario['return_rate'],
                base_scenario['returns_30'],
                base_scenario['solution_cost'],
                base_scenario['reduction_rate'],
                base_scenario['additional_cost_per_item'],
                base_scenario['avg_sale_price']
            ],
            "New": [
                new_sales_30,
                new_return_rate,
                new_returns_30,
                new_solution_cost,
                new_reduction_rate,
                new_additional_cost,
                new_avg_price
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Calculate financial impact for original scenario
        original_avoided_returns = base_scenario['returns_30'] * (base_scenario['reduction_rate'] / 100)
        original_monthly_savings = original_avoided_returns * (base_scenario['avg_sale_price'] - base_scenario['new_unit_cost'])
        original_monthly_cost = base_scenario['sales_30'] * base_scenario['additional_cost_per_item']
        original_monthly_net = original_monthly_savings - original_monthly_cost
        original_annual_net = original_monthly_net * 12
        
        if base_scenario['solution_cost'] > 0 and original_annual_net > 0:
            original_roi = (original_annual_net / base_scenario['solution_cost']) * 100
            original_breakeven = base_scenario['solution_cost'] / original_monthly_net
        else:
            original_roi = None
            original_breakeven = None
        
        # Calculate financial impact for new scenario
        new_unit_cost = base_scenario['current_unit_cost'] + new_additional_cost
        new_avoided_returns = new_returns_30 * (new_reduction_rate / 100)
        new_monthly_savings = new_avoided_returns * (new_avg_price - new_unit_cost)
        new_monthly_cost = new_sales_30 * new_additional_cost
        new_monthly_net = new_monthly_savings - new_monthly_cost
        new_annual_net = new_monthly_net * 12
        
        if new_solution_cost > 0 and new_annual_net > 0:
            new_roi = (new_annual_net / new_solution_cost) * 100
            new_breakeven = new_solution_cost / new_monthly_net
        else:
            new_roi = None
            new_breakeven = None
        
        # Create financial impact comparison
        financial_data = {
            "Metric": [
                "Monthly Savings ($)",
                "Monthly Additional Costs ($)",
                "Monthly Net Benefit ($)",
                "Annual Net Benefit ($)",
                "Return on Investment (%)",
                "Break-even (months)"
            ],
            "Original": [
                original_monthly_savings,
                original_monthly_cost,
                original_monthly_net,
                original_annual_net,
                original_roi,
                original_breakeven
            ],
            "New": [
                new_monthly_savings,
                new_monthly_cost,
                new_monthly_net,
                new_annual_net,
                new_roi,
                new_breakeven
            ]
        }
        
        financial_df = pd.DataFrame(financial_data)
        
        # Display comparison tables
        st.markdown("### Parameter Comparison")
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        st.markdown("### Financial Impact Comparison")
        st.dataframe(financial_df, use_container_width=True, hide_index=True)
        
        # Calculate percent changes for visualization
        if original_annual_net > 0 and new_annual_net > 0:
            net_benefit_change = ((new_annual_net / original_annual_net) - 1) * 100
        else:
            net_benefit_change = 0
        
        if original_roi and new_roi:
            roi_change = ((new_roi / original_roi) - 1) * 100
        else:
            roi_change = 0
        
        if original_breakeven and new_breakeven:
            breakeven_change = ((new_breakeven / original_breakeven) - 1) * 100
        else:
            breakeven_change = 0
        
        # Display impact visualization
        st.markdown("### Impact Visualization")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Annual Net Benefit",
                f"${new_annual_net:.2f}",
                f"{net_benefit_change:.1f}%",
                delta_color="normal" if net_benefit_change >= 0 else "inverse"
            )
        
        with col2:
            if new_roi:
                st.metric(
                    "Return on Investment",
                    f"{new_roi:.1f}%",
                    f"{roi_change:.1f}%",
                    delta_color="normal" if roi_change >= 0 else "inverse"
                )
            else:
                st.metric("Return on Investment", "N/A", delta=None)
        
        with col3:
            if new_breakeven:
                st.metric(
                    "Break-even Time",
                    f"{new_breakeven:.1f} months",
                    f"{-breakeven_change:.1f}%",  # Negative because shorter is better
                    delta_color="normal" if breakeven_change <= 0 else "inverse"
                )
            else:
                st.metric("Break-even Time", "N/A", delta=None)
        
        # Waterfall chart for net benefit change factors
        st.markdown("### Net Benefit Drivers")
        
        # Calculate impact of each factor (simplified model)
        base_avoided_returns = base_scenario['returns_30'] * (base_scenario['reduction_rate'] / 100)
        base_monthly_savings = base_avoided_returns * (base_scenario['avg_sale_price'] - base_scenario['new_unit_cost'])
        base_monthly_cost = base_scenario['sales_30'] * base_scenario['additional_cost_per_item']
        base_monthly_net = base_monthly_savings - base_monthly_cost
        
        # Calculate individual impacts (simplified)
        # This is a simplified model - a more accurate model would account for interactions
        sales_impact = (new_sales_30 - base_scenario['sales_30']) * base_scenario['additional_cost_per_item'] * -1  # Cost increase
        return_rate_impact = (new_return_rate - base_scenario['return_rate']) / 100 * new_sales_30 * base_scenario['reduction_rate'] / 100 * (base_scenario['avg_sale_price'] - base_scenario['new_unit_cost'])
        reduction_impact = (new_reduction_rate - base_scenario['reduction_rate']) / 100 * new_returns_30 * (base_scenario['avg_sale_price'] - base_scenario['new_unit_cost'])
        additional_cost_impact = (new_additional_cost - base_scenario['additional_cost_per_item']) * new_sales_30 * -1
        price_impact = (new_avg_price - base_scenario['avg_sale_price']) * new_avoided_returns
        
        # Create waterfall chart data
        waterfall_data = [
            {"Factor": "Original Monthly Net", "Impact": base_monthly_net, "Type": "Total"},
            {"Factor": "Sales Volume", "Impact": sales_impact, "Type": "Increase" if sales_impact > 0 else "Decrease"},
            {"Factor": "Return Rate", "Impact": return_rate_impact, "Type": "Increase" if return_rate_impact > 0 else "Decrease"},
            {"Factor": "Reduction Rate", "Impact": reduction_impact, "Type": "Increase" if reduction_impact > 0 else "Decrease"},
            {"Factor": "Additional Cost", "Impact": additional_cost_impact, "Type": "Increase" if additional_cost_impact > 0 else "Decrease"},
            {"Factor": "Sale Price", "Impact": price_impact, "Type": "Increase" if price_impact > 0 else "Decrease"},
            {"Factor": "New Monthly Net", "Impact": new_monthly_net, "Type": "Total"}
        ]
        
        waterfall_df = pd.DataFrame(waterfall_data)
        
        # Create the waterfall chart
        fig_waterfall = go.Figure(go.Waterfall(
            name="Monthly Net Benefit Changes",
            orientation="v",
            measure=["absolute"] + ["relative"] * 5 + ["total"],
            x=waterfall_df["Factor"],
            y=waterfall_df["Impact"],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": COLOR_SCHEME["negative"]}},
            increasing={"marker": {"color": COLOR_SCHEME["positive"]}},
            totals={"marker": {"color": COLOR_SCHEME["primary"]}}
        ))
        
        fig_waterfall.update_layout(
            title="Waterfall Chart: Monthly Net Benefit Drivers",
            showlegend=False,
            height=500
        )
        
        st.plotly_chart(fig_waterfall, use_container_width=True)
        
        # Sensitivity analysis
        st.markdown("### Sensitivity Analysis")
        st.caption("This chart shows how ROI changes with different reduction rates and additional costs")
        
        # Create data for sensitivity analysis
        reduction_range = np.linspace(max(0, new_reduction_rate - 20), min(100, new_reduction_rate + 20), 5)
        cost_range = np.linspace(max(0, new_additional_cost - 1), new_additional_cost + 1, 5)
        
        sensitivity_data = []
        
        for red in reduction_range:
            for cost in cost_range:
                # Calculate ROI for this combination
                avoided = new_returns_30 * (red / 100)
                new_cost = base_scenario['current_unit_cost'] + cost
                savings = avoided * (new_avg_price - new_cost)
                add_costs = new_sales_30 * cost
                net = savings - add_costs
                annual = net * 12
                
                if new_solution_cost > 0 and annual > 0:
                    sens_roi = (annual / new_solution_cost) * 100
                else:
                    sens_roi = 0
                
                sensitivity_data.append({
                    "Reduction Rate": red,
                    "Additional Cost": cost,
                    "ROI": sens_roi
                })
        
        sensitivity_df = pd.DataFrame(sensitivity_data)
        
        # Create heatmap
        fig_heatmap = px.density_heatmap(
            sensitivity_df,
            x="Reduction Rate",
            y="Additional Cost",
            z="ROI",
            labels={
                "Reduction Rate": "Return Reduction Rate (%)",
                "Additional Cost": "Additional Cost per Item ($)",
                "ROI": "Return on Investment (%)"
            },
            title="ROI Sensitivity Analysis"
        )
        
        fig_heatmap.update_layout(height=500)
        st.plotly_chart(fig_heatmap, use_container_width=True)

# Add this to the display_what_if_analysis() function, right after the sensitivity heatmap section

# Monte Carlo simulation
st.markdown("---")
st.markdown("### Monte Carlo Risk Simulation")
st.caption("Simulate thousands of scenarios with random variations to understand risk and confidence intervals")

with st.expander("Configure and Run Monte Carlo Simulation", expanded=True):
    # Simulation parameters
    st.markdown("#### Configure Uncertainty Parameters")
    st.caption("Set the standard deviation for each parameter as a percentage of its value")
    
    param_col1, param_col2 = st.columns(2)
    
    with param_col1:
        sim_sales_std = st.slider("Sales Volume Variability (%)", 
                                min_value=1, max_value=30, value=10,
                                help="Higher values indicate more uncertainty in monthly sales volume")
        
        sim_return_std = st.slider("Return Rate Variability (%)", 
                                min_value=1, max_value=30, value=15,
                                help="Higher values indicate more uncertainty in return rates")
        
        sim_reduction_std = st.slider("Reduction Rate Variability (%)", 
                                    min_value=1, max_value=40, value=20,
                                    help="Higher values indicate more uncertainty in how effective the solution will be")
    
    with param_col2:
        sim_price_std = st.slider("Price Variability (%)", 
                                min_value=1, max_value=20, value=5,
                                help="Higher values indicate more uncertainty in product pricing")
        
        sim_cost_std = st.slider("Additional Cost Variability (%)", 
                                min_value=1, max_value=30, value=10,
                                help="Higher values indicate more uncertainty in additional costs")
        
        sim_iterations = st.slider("Number of Simulations", 
                                min_value=100, max_value=10000, value=1000, step=100,
                                help="More simulations provide more accurate results but take longer to compute")
    
    # Create scenario dict for simulation
    simulation_scenario = {
        'sales_30': new_sales_30,
        'return_rate': new_return_rate,
        'reduction_rate': new_reduction_rate,
        'avg_sale_price': new_avg_price,
        'solution_cost': new_solution_cost,
        'additional_cost_per_item': new_additional_cost,
        'current_unit_cost': base_scenario['current_unit_cost']
    }
    
    # Run simulation button
    if st.button("Run Monte Carlo Simulation"):
        with st.spinner("Running simulation..."):
            # Convert percentages to decimals for the function
            sim_results = run_monte_carlo_simulation(
                simulation_scenario, 
                iterations=sim_iterations,
                sales_std=sim_sales_std/100,
                return_rate_std=sim_return_std/100,
                reduction_rate_std=sim_reduction_std/100,
                price_std=sim_price_std/100,
                additional_cost_std=sim_cost_std/100
            )
            
            # Display results
            display_monte_carlo_results(sim_results)
            
            # Allow saving the scenario with risk assessment
            st.markdown("---")
            if st.button("Save What-If Scenario with Risk Assessment"):
                # Create a new scenario name
                risk_level = "Low Risk"
                if sim_results['probability_positive_roi'] < 0.7:
                    risk_level = "High Risk"
                elif sim_results['probability_positive_roi'] < 0.85:
                    risk_level = "Medium Risk"
                
                new_name = f"{base_scenario_name} ({risk_level})"
                
                # Calculate confidence intervals for description
                roi_ci = (
                    sim_results['roi']['percentiles'][5],
                    sim_results['roi']['percentiles'][95]
                )
                
                # Add risk info to solution description
                risk_description = (
                    f"{base_scenario['solution']} | Risk: {risk_level} | "
                    f"ROI: {sim_results['roi']['mean']:.1f}% (90% CI: {roi_ci[0]:.1f}%-{roi_ci[1]:.1f}%) | "
                    f"POI: {sim_results['probability_positive_roi']*100:.1f}%"
                )
                
                success, message = optimizer.add_scenario(
                    new_name, base_scenario['sku'], new_sales_30, new_avg_price,
                    base_scenario['sales_channel'], new_returns_30, risk_description,
                    new_solution_cost, new_additional_cost, base_scenario['current_unit_cost'],
                    new_reduction_rate, new_sales_30 * 12, new_returns_30 * 12, base_scenario['tag']
                )
                
                if success:
                    st.success(f"What-if scenario with risk assessment saved as '{new_name}'!")
                else:
                    st.error(message)
        
        # Option to save as new scenario
        if st.button("Save as New Scenario"):
            # Create a new scenario name
            new_name = f"{base_scenario_name} (What-If)"
            
            success, message = optimizer.add_scenario(
                new_name, base_scenario['sku'], new_sales_30, new_avg_price,
                base_scenario['sales_channel'], new_returns_30, base_scenario['solution'],
                new_solution_cost, new_additional_cost, base_scenario['current_unit_cost'],
                new_reduction_rate, new_sales_30 * 12, new_returns_30 * 12, base_scenario['tag']
            )
            
            if success:
                st.success(f"What-if scenario saved as '{new_name}'!")
            else:
                st.error(message)
    else:
        st.info("Add scenarios first to use the what-if analysis tool.")

def display_settings():
    """Display app settings and data management options"""
    st.subheader("Settings & Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Import/Export Data")
        
        # Export current data
        if not optimizer.scenarios.empty:
            json_data = optimizer.download_json()
            st.download_button(
                "Export All Scenarios (JSON)",
                data=json_data,
                file_name="kaizenroi_scenarios.json",
                mime="application/json"
            )
            
            # Export as Excel
            excel_data = io.BytesIO()
            with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
                optimizer.scenarios.to_excel(writer, index=False, sheet_name='Scenarios')
            
            st.download_button(
                "Export as Excel Spreadsheet",
                data=excel_data.getvalue(),
                file_name="kaizenroi_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Export as CSV
            csv_data = optimizer.scenarios.to_csv(index=False).encode()
            st.download_button(
                "Export as CSV",
                data=csv_data,
                file_name="kaizenroi_export.csv",
                mime="text/csv"
            )
        
        # Import data
        st.markdown("#### Import Data")
        uploaded_file = st.file_uploader("Upload scenario data (JSON)", type=["json"])
        
        if uploaded_file is not None:
            json_str = uploaded_file.read().decode("utf-8")
            if optimizer.upload_json(json_str):
                st.success("Data imported successfully!")
            else:
                st.error("Failed to import data. Please check the file format.")
    
    with col2:
        st.markdown("### App Settings")
        
        # Reset data
        st.markdown("#### Data Management")
        if st.button("Add Example Scenarios"):
            count = optimizer.add_example_scenarios()
            st.success(f"Added {count} example scenarios!")
        
        if st.button("Clear All Data"):
            confirm = st.checkbox("I understand this will delete all scenarios")
            if confirm:
                optimizer.scenarios = pd.DataFrame(columns=optimizer.scenarios.columns)
                optimizer.save_data()
                st.success("All data cleared!")
                st.experimental_rerun()
        
        # Theme settings (placeholder for future customization)
        st.markdown("#### Theme Preference")
        theme = st.selectbox("Color Theme", ["Blue (Default)", "Green", "Purple", "Orange"])
        st.info("Theme customization will be available in a future update.")

# Sidebar Navigation
with st.sidebar:
    st.image("https://via.placeholder.com/150x60?text=KaizenROI", width=150)
    st.markdown("## Navigation")
    
    # Navigation options
    nav_option = st.radio(
        "Go to:",
        ["Dashboard", "Add New Scenario", "Portfolio Analysis", "What-If Analysis", "Settings"],
        index=0
    )
    
    st.markdown("---")
    
    # Help section
    with st.expander("📘 Help & Formulas"):
        st.markdown("""
        ### Key Terms
        - **Return Rate**: Percentage of products returned
        - **Return Reduction**: Estimated reduction in returns after solution
        - **Break-even**: Time to recover the solution investment
        - **ROI**: Return on investment (net benefit / solution cost)
        - **Net Benefit**: Annual savings minus additional costs
        
        ### Key Formulas
        - Return Rate = (Returns / Sales) × 100%
        - Avoided Returns = Returns × Reduction Rate
        - Net Benefit = Annual Savings - Annual Additional Costs
        - Annual Savings = Avoided Returns × Savings Per Item
        - ROI = (Net Benefit / Solution Cost) × 100%
        - Break-even Time = Solution Cost / Monthly Net Benefit
        - Margin After = Price - (Unit Cost + Additional Cost)
        """)
    
    with st.expander("🔎 Understanding ROI Score"):
        st.markdown("""
        ### ROI Score Explained
        The ROI score is a weighted metric that combines:
        - ROI percentage (50% weight)
        - Break-even speed (35% weight)
        - Reduction rate (15% weight)
        
        Higher scores indicate better investment opportunities with faster returns and higher impact.
        
        ### Score Ranges
        - **80-100**: Excellent investment
        - **60-80**: Very good investment
        - **40-60**: Good investment
        - **20-40**: Acceptable investment
        - **0-20**: Marginal investment
        """)
    
    # Footer
    st.markdown("---")
    st.caption("KaizenROI v2.0 | Continuous Improvement Suite")
    st.caption("© 2025 KaizenROI Analytics")

# Main content
display_header()

# Handle view scenario details if selected
if 'view_scenario' in st.session_state and st.session_state['view_scenario'] and 'selected_scenario' in st.session_state:
    display_scenario_details(st.session_state['selected_scenario'])
else:
    # Regular navigation
    if nav_option == "Dashboard":
        display_metrics_overview(optimizer.scenarios)
        display_scenario_table(optimizer.scenarios)
    
    elif nav_option == "Add New Scenario":
        create_scenario_form()
    
    elif nav_option == "Portfolio Analysis":
        display_portfolio_analysis(optimizer.scenarios)
    
    elif nav_option == "What-If Analysis":
        display_what_if_analysis()
    
    elif nav_option == "Settings":
        display_settings()

# Entry point for setup.py
def main():
    """Entry point for the application."""
    # The Streamlit script is already executing, so this function is just a noop when run directly
    pass

if __name__ == "__main__":
    main()
