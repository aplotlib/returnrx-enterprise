"""
MedDevROI - Medical Device ROI & Risk Analysis Suite
A comprehensive analytics tool for evaluating medical device investments and risks.
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

# App configuration - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="MedDevROI | Medical Device ROI & Risk Analysis Suite",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define color scheme for medical device context
COLOR_SCHEME = {
    "primary": "#0055a5",    # Medical blue
    "secondary": "#00a3a3",  # Teal
    "background": "#f0f4f8",
    "positive": "#00796b",   # Dark teal
    "negative": "#c62828",   # Medical red
    "warning": "#ff8f00",    # Amber
    "neutral": "#1565c0",    # Darker blue
    "text_dark": "#263238",
    "text_light": "#ecf0f1",
    "regulatory": "#4527a0"  # Purple for regulatory elements
}

# Initialize app
if 'optimizer' not in st.session_state:
    st.session_state.optimizer = None
    
# Initialize page state
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"
    
# Initialize view state for scenario details
if 'view_scenario' not in st.session_state:
    st.session_state.view_scenario = False
    
# Initialize selected scenario
if 'selected_scenario' not in st.session_state:
    st.session_state.selected_scenario = None

# Initialize FMEA data structures
if 'design_fmea_data' not in st.session_state:
    st.session_state.design_fmea_data = pd.DataFrame(columns=[
        'id', 'item', 'function', 'failure_mode', 'effect', 'cause', 
        'current_controls', 'sev', 'occ', 'det', 'rpn', 'recommended_action',
        'action_responsibility', 'target_date', 'actions_taken', 
        'new_sev', 'new_occ', 'new_det', 'new_rpn', 'status', 'date_created',
        'date_updated', 'design_phase'
    ])

if 'problem_fmea_data' not in st.session_state:
    st.session_state.problem_fmea_data = pd.DataFrame(columns=[
        'id', 'item', 'problem_description', 'failure_mode', 'effect', 'cause', 
        'current_controls', 'sev', 'occ', 'det', 'rpn', 'recommended_action',
        'action_responsibility', 'target_date', 'actions_taken', 
        'new_sev', 'new_occ', 'new_det', 'new_rpn', 'status', 'date_created',
        'date_updated', 'problem_date'
    ])

# Custom CSS with medical focus
st.markdown("""
<style>
    /* Hide default Streamlit top bar buttons to avoid confusion with our custom nav */
    .stButton > button {
        margin-top: 0;
        visibility: visible;
        height: auto;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        background-color: #0055a5;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: 500;
    }
    
    div[data-testid="stHorizontalBlock"] .stButton > button {
        visibility: visible !important;
        height: auto !important;
        padding: 0.5rem 1rem !important;
        margin: 0.25rem !important;
        background-color: transparent;
        color: #0055a5;
        border: none;
        border-radius: 4px;
        font-weight: 500;
    }
    
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        background-color: rgba(0, 85, 165, 0.1);
        color: #003c75;
    }
    
    /* Main styling */
    body, .stApp {
        background-color: #f0f4f8;
        color: #263238;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        color: #0055a5;
    }
    
    /* Form styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 4px;
        border: 1px solid #bdc3c7;
    }
    
    /* Dataframe styling */
    .stDataFrame thead tr th {
        background-color: #0055a5;
        color: white;
        padding: 8px 12px;
        font-weight: 500;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background-color: rgba(236, 240, 241, 0.5);
    }
    .stDataFrame tbody tr:hover {
        background-color: rgba(0, 85, 165, 0.1);
    }
    
    /* Cards */
    .css-card {
        border-radius: 8px;
        padding: 1.5rem;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* Metric display */
    .metric-container {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
        border-color: #0055a5;
        border-bottom: 3px solid #0055a5;
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
        background-color: #263238;
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
    
    /* Medical/regulatory specific components */
    .regulatory-alert {
        background-color: #f3f3fd;
        border-left: 5px solid #4527a0;
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    
    .clinical-validation {
        background-color: #e8f5e9;
        border-left: 5px solid #00796b;
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    
    /* Risk indication styling */
    .high-risk {
        color: #c62828;
        font-weight: 500;
    }
    .moderate-risk {
        color: #ff8f00;
        font-weight: 500;
    }
    .low-risk {
        color: #00796b;
        font-weight: 500;
    }
    
    /* Standard components */
    .info-box {
        background-color: rgba(21, 101, 192, 0.1);
        border-left: 5px solid #1565c0;
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: rgba(255, 143, 0, 0.1);
        border-left: 5px solid #ff8f00;
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
        background-color: #0055a5;
    }
    .css-1d391kg .sidebar-content {
        padding: 1rem;
    }
    
    /* Charts */
    .js-plotly-plot {
        border-radius: 8px;
        background-color: white;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Top navigation bar */
    .topnav {
        background-color: #0055a5;
        overflow: hidden;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Dashboard cards */
    .dashboard-card {
        background-color: white;
        border-radius: 8px;
        padding: 1.25rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: all 0.3s;
    }
    .dashboard-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .dashboard-card-title {
        font-weight: 600;
        color: #0055a5;
        margin-bottom: 0.75rem;
    }
    
    /* Card grid layout */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        grid-gap: 1rem;
    }
    
    /* Nav page links */
    .nav-page {
        color: rgba(255, 255, 255, 0.85);
        padding: 8px 15px;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: 500;
        user-select: none;
    }
    .nav-page:hover {
        background-color: rgba(255, 255, 255, 0.15);
        color: white;
    }
    .nav-page.active {
        background-color: #00a3a3;
        color: white;
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

def get_device_risk_color(risk_level):
    """Get color based on medical device risk level"""
    if risk_level == "High Risk" or risk_level == "Class III":
        return "#c62828"  # Red
    elif risk_level == "Moderate Risk" or risk_level == "Class II":
        return "#ff8f00"  # Amber
    else:
        return "#00796b"  # Green
    
def get_regulatory_impact_color(impact):
    """Get color based on regulatory impact level"""
    if impact == "New submission":
        return "#c62828"  # Red
    elif impact == "Special 510(k)":
        return "#ff8f00"  # Amber
    elif impact == "Letter to File":
        return "#2196f3"  # Blue
    else:
        return "#00796b"  # Green

def navigate_to(page_name):
    """Function to navigate to a specific page"""
    st.session_state.page = page_name
    st.experimental_rerun()

# Monte Carlo simulation function
def run_monte_carlo_simulation(base_parameters, parameter_ranges, num_simulations=1000):
    """
    Run a Monte Carlo simulation for ROI analysis
    
    Args:
        base_parameters: Dictionary with base values
        parameter_ranges: Dictionary with min/max percent changes
        num_simulations: Number of simulations to run
    
    Returns:
        DataFrame with simulation results
    """
    results = []
    
    for _ in range(num_simulations):
        # Generate random values for each parameter within defined ranges
        params = {}
        for param, (min_pct, max_pct) in parameter_ranges.items():
            if param in base_parameters:
                # Apply random percentage change to base value
                pct_change = np.random.uniform(min_pct, max_pct) / 100.0
                params[param] = base_parameters[param] * (1 + pct_change)
            else:
                params[param] = np.random.uniform(min_pct, max_pct)
        
        # Calculate financial metrics
        monthly_sales = params['sales_30']
        return_rate = params['return_rate']
        monthly_returns = monthly_sales * return_rate / 100
        reduction_rate = params['reduction_rate']
        avoided_returns = monthly_returns * reduction_rate / 100
        
        solution_cost = params['solution_cost']
        regulatory_cost = params.get('regulatory_cost', 0)
        additional_cost = params['additional_cost_per_item']
        avg_price = params['avg_sale_price']
        current_unit_cost = params['current_unit_cost']
        new_unit_cost = current_unit_cost + additional_cost
        
        monthly_savings = avoided_returns * (avg_price - new_unit_cost)
        monthly_additional_costs = monthly_sales * additional_cost
        monthly_net = monthly_savings - monthly_additional_costs
        annual_net = monthly_net * 12
        
        total_investment = solution_cost + regulatory_cost
        
        # Calculate ROI and breakeven
        if total_investment > 0 and monthly_net > 0:
            roi = (annual_net / total_investment) * 100
            breakeven_months = total_investment / monthly_net
        else:
            roi = 0
            breakeven_months = float('inf')
        
        # Store results
        results.append({
            'monthly_net': monthly_net,
            'annual_net': annual_net,
            'roi': roi,
            'breakeven_months': breakeven_months
        })
    
    return pd.DataFrame(results)

# Data management class
class ReturnOptimizer:
    def __init__(self):
        self.load_data()
        self.default_examples = [
            {
                "scenario_name": "Premium Packaging",
                "sku": "DEVICE-123",
                "sales_30": 750,
                "avg_sale_price": 89.99,
                "sales_channel": "Hospital",
                "returns_30": 94,
                "solution": "Premium unboxing experience with clearer usage instructions",
                "solution_cost": 5000,
                "additional_cost_per_item": 1.25,
                "current_unit_cost": 32.50,
                "reduction_rate": 30,
                "sales_365": 9125,
                "returns_365": 1140,
                "device_class": "Class II",
                "regulatory_impact": "Letter to File",
                "adverse_events": 12,
                "tag": "Packaging"
            },
            {
                "scenario_name": "Improved Surgical Instructions",
                "sku": "IMPLANT-456",
                "sales_30": 420,
                "avg_sale_price": 129.99,
                "sales_channel": "Direct to Provider",
                "returns_30": 71,
                "solution": "Enhanced surgical technique guide and training videos",
                "solution_cost": 7500,
                "additional_cost_per_item": 0,
                "current_unit_cost": 45.75,
                "reduction_rate": 35,
                "sales_365": 5100,
                "returns_365": 860,
                "device_class": "Class III",
                "regulatory_impact": "Special 510(k)",
                "adverse_events": 25,
                "tag": "Instructions for Use"
            },
            {
                "scenario_name": "Product Design Improvement",
                "sku": "DIAGNOSTICS-789",
                "sales_30": 1250,
                "avg_sale_price": 49.99,
                "sales_channel": "Distributor",
                "returns_30": 138,
                "solution": "Redesigned interface with improved usability",
                "solution_cost": 12000,
                "additional_cost_per_item": 1.75,
                "current_unit_cost": 18.50,
                "reduction_rate": 42,
                "sales_365": 15200,
                "returns_365": 1675,
                "device_class": "Class II",
                "regulatory_impact": "Special 510(k)",
                "adverse_events": 18,
                "tag": "Design Improvement"
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
                'monthly_net_benefit', 'tag', 'device_class', 'regulatory_impact',
                'adverse_events', 'regulatory_cost'
            ])
            st.session_state['scenarios'] = self.scenarios
        else:
            self.scenarios = st.session_state['scenarios']
            
        # Initialize risk matrix data if not present
        if 'risk_matrix_data' not in st.session_state:
            st.session_state.risk_matrix_data = pd.DataFrame(columns=[
                'product_name', 'safety_score', 'compliance_score', 'logistics_score', 
                'weighted_risk', 'risk_level', 'risk_color'])
    
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
                     current_unit_cost, reduction_rate, sales_365=None, returns_365=None, 
                     tag=None, device_class="Class II", regulatory_impact="No impact", 
                     adverse_events=0, regulatory_cost=0):
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
            amortized_solution_cost = (solution_cost + regulatory_cost) / sales_365 if sales_365 > 0 else 0
            margin_after_amortized = margin_after - amortized_solution_cost
            
            # Calculate savings and ROI
            savings_per_avoided_return = avg_sale_price - new_unit_cost
            savings_30 = avoided_returns_30 * savings_per_avoided_return
            annual_savings = avoided_returns_365 * savings_per_avoided_return
            
            annual_additional_costs = additional_cost_per_item * sales_365
            net_benefit = annual_savings - annual_additional_costs
            monthly_net_benefit = net_benefit / 12
            
            # Calculate ROI metrics
            total_investment = solution_cost + regulatory_cost
            roi = break_even_days = break_even_months = score = None
            if total_investment > 0 and net_benefit > 0:
                roi = (net_benefit / total_investment) * 100  # as percentage
                break_even_days = (total_investment / net_benefit) * 365
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
                'tag': tag,
                'device_class': device_class,
                'regulatory_impact': regulatory_impact,
                'adverse_events': adverse_events,
                'regulatory_cost': regulatory_cost
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
        success, message = self.add_scenario
         # Add updated scenario
        success, message = self.add_scenario(
            current['scenario_name'], current['sku'], current['sales_30'],
            current['avg_sale_price'], current['sales_channel'], current['returns_30'],
            current['solution'], current['solution_cost'], current['additional_cost_per_item'],
            current['current_unit_cost'], current['reduction_rate'],
            current['sales_365'], current['returns_365'], current['tag'],
            current.get('device_class', 'Class II'),
            current.get('regulatory_impact', 'No impact'),
            current.get('adverse_events', 0),
            current.get('regulatory_cost', 0)
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
            scenario['sales_365'], scenario['returns_365'], scenario['tag'],
            scenario.get('device_class', 'Class II'),
            scenario.get('regulatory_impact', 'No impact'),
            scenario.get('adverse_events', 0),
            scenario.get('regulatory_cost', 0)
        )
        
        return success, message
def display_risk_matrix():
    """Display enhanced risk matrix for medical device analysis"""
    st.subheader("Medical Device Risk Analysis Matrix")
    
    # Create tabs for different risk analysis tools
    matrix_tab, classifier_tab, heatmap_tab = st.tabs(["Risk Matrix", "Device Classification", "Risk Heatmap"])
    
    with matrix_tab:
        # Create a dataframe to store risk entries if not already present
        if 'risk_matrix_data' not in st.session_state:
            st.session_state.risk_matrix_data = pd.DataFrame(columns=[
                'product_name', 'safety_score', 'compliance_score', 'logistics_score', 
                'weighted_risk', 'risk_level', 'risk_color', 'timestamp', 'notes'
            ])
        
        # Improved form with better layout and more detailed risk factors
        with st.form("risk_matrix_form"):
            st.markdown("### Add Product Risk Assessment")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                product_name = st.text_input("Product Name")
                product_id = st.text_input("Product/SKU ID")
                
                # Add date picker
                assessment_date = st.date_input("Assessment Date", datetime.now())
                
                # Add device class
                device_class = st.selectbox("Device Classification", 
                                          ["Class I", "Class II", "Class III"], 
                                          help="FDA medical device classification")
            
            with col2:
                st.markdown("##### Risk Scores (0-10)")
                st.markdown("Higher scores indicate higher risk")
                
                # Create more detailed risk categories
                safety_score = st.slider("Patient Safety Risk", 0, 10, 5, 
                                        help="Risk related to patient safety and potential harm")
                
                compliance_score = st.slider("Regulatory Compliance Risk", 0, 10, 5,
                                           help="Risk related to regulatory compliance issues (FDA, ISO, etc.)")
                
                logistics_score = st.slider("Supply Chain/Logistics Risk", 0, 10, 5,
                                          help="Risk related to supply chain, manufacturing, and distribution")
                
                # Additional risk categories
                financial_score = st.slider("Financial/Business Risk", 0, 10, 5,
                                          help="Risk related to financial impact and business concerns")
                
                # Notes field
                notes = st.text_area("Risk Notes & Mitigations", 
                                    help="Document risk assessment context and potential mitigation strategies")
            
            # Updated submit button with better styling
            submitted = st.form_submit_button("Add to Risk Matrix")
            
            if submitted:
                if not product_name:
                    st.error("Product name is required")
                else:
                    # Calculate weighted risk with updated formula including financial risk
                    weighted_risk = (
                        safety_score * 0.4 +  # Increased weight for safety
                        compliance_score * 0.3 + 
                        logistics_score * 0.15 + 
                        financial_score * 0.15
                    )
                    
                    # Determine risk level
                    if weighted_risk > 7:
                        risk_level = "High Risk"
                        risk_color = "#c62828"  # Red
                    elif weighted_risk > 4:
                        risk_level = "Moderate Risk"
                        risk_color = "#ff8f00"  # Amber
                    else:
                        risk_level = "Low Risk"
                        risk_color = "#00796b"  # Green
                    
                    new_row = {
                        'product_name': product_name,
                        'product_id': product_id,
                        'safety_score': safety_score,
                        'compliance_score': compliance_score,
                        'logistics_score': logistics_score,
                        'financial_score': financial_score,
                        'weighted_risk': weighted_risk,
                        'risk_level': risk_level,
                        'risk_color': risk_color,
                        'timestamp': assessment_date,
                        'notes': notes,
                        'device_class': device_class
                    }
                    
                    # Add to dataframe
                    st.session_state.risk_matrix_data = pd.concat([
                        st.session_state.risk_matrix_data, 
                        pd.DataFrame([new_row])
                    ], ignore_index=True)
                    
                    st.success(f"Added {product_name} to risk matrix")
        
        # Display risk matrix table
        if not st.session_state.risk_matrix_data.empty:
            st.markdown("### Risk Matrix Results")
            
            # Add filters
            col1, col2 = st.columns(2)
            
            with col1:
                risk_level_filter = st.multiselect(
                    "Filter by Risk Level",
                    options=sorted(st.session_state.risk_matrix_data['risk_level'].unique()),
                    default=[]
                )
            
            with col2:
                if 'device_class' in st.session_state.risk_matrix_data.columns:
                    device_class_filter = st.multiselect(
                        "Filter by Device Class",
                        options=sorted(st.session_state.risk_matrix_data['device_class'].unique()),
                        default=[]
                    )
                else:
                    device_class_filter = []
            
            # Apply filters
            filtered_df = st.session_state.risk_matrix_data.copy()
            
            if risk_level_filter:
                filtered_df = filtered_df[filtered_df['risk_level'].isin(risk_level_filter)]
            
            if device_class_filter and 'device_class' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['device_class'].isin(device_class_filter)]
            
            # Prepare display dataframe
            display_df = filtered_df.copy()
            
            # Format risk level with color
            def format_risk_level(row):
                return f"<span style='color: {row['risk_color']}; font-weight: bold;'>{row['risk_level']} ({row['weighted_risk']:.1f})</span>"
            
            display_df['formatted_risk'] = display_df.apply(format_risk_level, axis=1)
            
            # Format device class with color if available
            if 'device_class' in display_df.columns:
                def format_device_class(row):
                    color = get_device_risk_color(row['device_class'])
                    return f"<span style='color: {color}; font-weight: bold;'>{row['device_class']}</span>"
                
                display_df['formatted_class'] = display_df.apply(format_device_class, axis=1)
            
            # Display table with improved formatting
            display_columns = [
                'product_name', 'product_id', 'safety_score', 'compliance_score', 
                'logistics_score', 'financial_score', 'formatted_risk'
            ]
            
            # Add device class if available
            if 'device_class' in display_df.columns:
                display_columns.insert(2, 'formatted_class')
            
            # Create column config for better display
            column_config = {
                "product_name": "Product",
                "product_id": "SKU/ID",
                "formatted_class": "Device Class",
                "safety_score": st.column_config.NumberColumn("Safety", format="%.1f"),
                "compliance_score": st.column_config.NumberColumn("Compliance", format="%.1f"),
                "logistics_score": st.column_config.NumberColumn("Logistics", format="%.1f"),
                "financial_score": st.column_config.NumberColumn("Financial", format="%.1f"),
                "formatted_risk": "Risk Level",
            }
            
            # Display filtered dataframe
            if not filtered_df.empty:
                st.dataframe(
                    display_df[display_columns],
                    use_container_width=True,
                    column_config=column_config,
                    hide_index=True
                )
            else:
                st.info("No items match the selected filters.")
            
            # Export options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Clear All Risk Data"):
                    # Add confirmation dialog
                    confirm = st.checkbox("I understand this will delete all risk matrix data")
                    if confirm:
                        st.session_state.risk_matrix_data = pd.DataFrame(columns=[
                            'product_name', 'safety_score', 'compliance_score', 'logistics_score', 
                            'weighted_risk', 'risk_level', 'risk_color', 'timestamp', 'notes'
                        ])
                        st.success("Risk matrix data cleared")
                        st.experimental_rerun()
            
            with col2:
                # Export to CSV
                csv_data = st.session_state.risk_matrix_data.to_csv(index=False).encode()
                st.download_button(
                    "Export Risk Matrix (CSV)",
                    data=csv_data,
                    file_name="risk_matrix_export.csv",
                    mime="text/csv"
                )
            
            with col3:
                # Export to Excel
                excel_data = io.BytesIO()
                with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
                    st.session_state.risk_matrix_data.to_excel(writer, index=False, sheet_name="Risk_Matrix")
                
                st.download_button(
                    "Export to Excel",
                    data=excel_data.getvalue(),
                    file_name="risk_matrix_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            # Add risk visualization chart
            risk_chart_data = st.session_state.risk_matrix_data[['product_name', 'weighted_risk', 'risk_level', 'risk_color']]
            
            # Create custom color map from risk colors
            color_map = {row['risk_level']: row['risk_color'] for _, row in risk_chart_data.drop_duplicates('risk_level').iterrows()}
            
            fig = px.bar(
                risk_chart_data,
                x='product_name',
                y='weighted_risk',
                color='risk_level',
                color_discrete_map=color_map,
                title="Risk Assessment by Product"
            )
            fig.update_layout(xaxis_title="Product", yaxis_title="Risk Score")
            st.plotly_chart(fig, use_container_width=True)
            
    with heatmap_tab:
        st.markdown("### Risk Matrix Heatmap")
        
        # Create sample data for all combinations
        x_vals = ["Low", "Medium", "High"]
        y_vals = ["Low", "Medium", "High"]
        
        risk_data = []
        
        for i, x in enumerate(x_vals):
            for j, y in enumerate(y_vals):
                severity = i + 1
                probability = j + 1
                risk_value = severity * probability
                
                if risk_value >= 6:
                    risk_category = "High Risk"
                    risk_color = "#c62828"
                elif risk_value >= 3:
                    risk_category = "Moderate Risk"
                    risk_color = "#ff8f00"
                else:
                    risk_category = "Low Risk" 
                    risk_color = "#00796b"
                    
                risk_data.append({
                    "Severity": x,
                    "Probability": y,
                    "Risk Value": risk_value,
                    "Risk Category": risk_category,
                    "Color": risk_color
                })
        
        risk_heatmap_df = pd.DataFrame(risk_data)
        
        fig_heatmap = px.density_heatmap(
            risk_heatmap_df,
            x="Severity",
            y="Probability",
            z="Risk Value",
            labels={"color": "Risk Level"},
            category_orders={"Severity": ["Low", "Medium", "High"], "Probability": ["Low", "Medium", "High"]},
            color_continuous_scale=[[0, "#00796b"], [0.4, "#ff8f00"], [0.7, "#c62828"]]
        )
        
        # Add product placements if products exist
        if not st.session_state.risk_matrix_data.empty:
            for _, row in st.session_state.risk_matrix_data.iterrows():
                # Map scores to matrix positions
                if row['safety_score'] <= 3:
                    severity = "Low"
                elif row['safety_score'] <= 7:
                    severity = "Medium"
                else:
                    severity = "High"
                    
                if row['compliance_score'] <= 3:
                    probability = "Low"
                elif row['compliance_score'] <= 7:
                    probability = "Medium"
                else:
                    probability = "High"
                
                fig_heatmap.add_annotation(
                    x=severity,
                    y=probability,
                    text=row['product_name'],
                    showarrow=True,
                    arrowhead=1,
                    bgcolor="white",
                    bordercolor=row['risk_color'],
                    font=dict(color=row['risk_color'])
                )
        
        fig_heatmap.update_layout(
            title="Risk Matrix Heatmap with Product Placement",
            height=500
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Add risk explanation
        st.markdown("""
        <div class="info-box">
            <h4>Risk Matrix Interpretation</h4>
            <p>The risk matrix visualizes each product based on severity (safety impact) and probability 
            (likelihood of occurrence). Products in the red zone require immediate attention and mitigation strategies.</p>
            <ul>
                <li><span style="color:#c62828; font-weight:bold;">High Risk (>7):</span> Significant safety or compliance concerns that require immediate mitigation</li>
                <li><span style="color:#ff8f00; font-weight:bold;">Moderate Risk (4-7):</span> Important issues that should be monitored and addressed with controls</li>
                <li><span style="color:#00796b; font-weight:bold;">Low Risk (<4):</span> Acceptable risk level with routine monitoring</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Add information about regulatory implications
        st.markdown("""
        <div class="regulatory-alert">
            <h4>Regulatory Considerations</h4>
            <p>For medical devices, risk management is required throughout the product lifecycle:</p>
            <ul>
                <li><strong>FDA:</strong> 21 CFR 820.30 Design Controls requires risk analysis</li>
                <li><strong>ISO 14971:</strong> Application of risk management to medical devices</li>
                <li><strong>ISO 13485:</strong> Quality management system requirements</li>
            </ul>
            <p>High-risk items should be documented in your risk management file with appropriate mitigations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with classifier_tab:
        st.markdown("### Medical Device Classification Tool")
        
        # Create two columns for form and results
        form_col, result_col = st.columns(2)
        
        with form_col:
            st.markdown("##### Device Information")
            device_name = st.text_input("Device Name", key="device_name_classifier")
            
            # More comprehensive classification factors
            intended_use = st.selectbox("Intended Use Category", 
                                     ["Diagnostic", "Therapeutic", "Monitoring", "Life-supporting/sustaining", "Other"])
            
            contact_type = st.selectbox("Contact Type", 
                                       ["Surface Contact", "External Communicating", "Implantable", "None"])
            
            invasiveness = st.selectbox("Invasiveness", 
                                       ["Non-Invasive", "Minimally Invasive", "Invasive", "Implantable"])
            
            # Additional fields for more comprehensive classification
            duration = st.selectbox("Duration of Use",
                                  ["Transient (<60 min)", "Short-term (<30 days)", "Long-term (>30 days)"])
            
            active_device = st.checkbox("Active Device (Requires Energy Source)")
            
            # Add additional risk factors
            sterile_device = st.checkbox("Sterile Device")
            combination_product = st.checkbox("Contains Drug/Biologic Component")
            software = st.checkbox("Contains Software/Firmware")
            
            if st.button("Classify Device"):
                # Enhanced classification logic based on FDA guidelines
                if implantable_or_life_sustaining():
                    risk_class = "Class III - Highest Risk"
                    risk_color = "#c62828"  # Red
                    submission_path = "PMA (Premarket Approval)"
                    explanation = "Implantable or life-sustaining/supporting devices generally require PMA submission with clinical evidence."
                elif invasiveness == "Invasive" and duration == "Long-term (>30 days)":
                    risk_class = "Class III - Highest Risk"
                    risk_color = "#c62828"  # Red
                    submission_path = "PMA or De Novo"
                    explanation = "Long-term invasive devices pose significant risks to patients and typically require PMA or De Novo pathway."
                elif contact_type == "External Communicating" or invasiveness == "Invasive":
                    if active_device or sterile_device:
                        risk_class = "Class II - Medium/High Risk"
                        risk_color = "#ff8f00"  # Amber
                        submission_path = "510(k) or De Novo"
                        explanation = "Invasive or external communicating devices with active components typically require 510(k) clearance."
                    else:
                        risk_class = "Class II - Medium Risk"
                        risk_color = "#ff8f00"  # Amber
                        submission_path = "510(k)"
                        explanation = "Invasive or external communicating devices usually require 510(k) clearance with substantial equivalence."
                elif active_device or software:
                    risk_class = "Class II - Medium Risk"
                    risk_color = "#ff8f00"  # Amber
                    submission_path = "510(k)"
                    explanation = "Active devices and software generally require 510(k) clearance with appropriate software documentation."
                else:
                    risk_class = "Class I - Low Risk"
                    risk_color = "#00796b"  # Green
                    submission_path = "Exempt or 510(k)"
                    explanation = "Low-risk, non-invasive, surface contact devices may be exempt from premarket notification, but still require registration and listing."
                
                # Add combination product adjustment
                if combination_product:
                    if risk_class != "Class III - Highest Risk":
                        risk_class = "Class III - Highest Risk"
                        risk_color = "#c62828"  # Red
                        submission_path = "Combination Product Pathway"
                        explanation += " As a combination product containing a drug/biologic component, additional regulatory requirements apply."
                
                # Store result in session state
                st.session_state.device_classification = {
                    "name": device_name,
                    "class": risk_class,
                    "color": risk_color,
                    "explanation": explanation,
                    "submission_path": submission_path,
                    "active": active_device,
                    "sterile": sterile_device,
                    "software": software,
                    "combination": combination_product,
                    "duration": duration,
                    "invasiveness": invasiveness,
                    "intended_use": intended_use
                }
                
                # Function to determine if device is implantable or life-sustaining
                def implantable_or_life_sustaining():
                    """Determine if device is implantable or life-sustaining"""
                    if invasiveness == "Implantable":
                        return True
                    
                    if intended_use == "Life-supporting/sustaining":
                        return True
                    
                    return False
        
        with result_col:
            st.markdown("##### Classification Results")
            
            if "device_classification" in st.session_state:
                result = st.session_state.device_classification
                st.markdown(f"""
                <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);">
                    <h4 style="font-weight: bold; margin-bottom: 0.5rem;">Device: {result['name']}</h4>
                    <p style="font-size: 1.5rem; font-weight: 600; color: {result['color']};">{result['class']}</p>
                    <div style="background-color: #f8f9fa; padding: 0.75rem; border-radius: 0.25rem; margin: 0.75rem 0;">
                        <strong>Submission Pathway:</strong> {result['submission_path']}
                    </div>
                    <p style="margin-top: 1rem;">{result['explanation']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Add regulatory pathway information with more details
                if "Class III" in result['class']:
                    st.markdown("""
                    <div class="regulatory-alert">
                        <strong>Regulatory Pathway:</strong> Premarket Approval (PMA)<br>
                        <strong>Requirements:</strong>
                        <ul>
                            <li>Clinical trials demonstrating safety and effectiveness</li>
                            <li>Extensive non-clinical testing (bench, animal, biocompatibility)</li>
                            <li>Manufacturing facility inspection</li>
                            <li>Post-market surveillance studies may be required</li>
                            <li>Design controls and risk management documentation</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                elif "Class II" in result['class']:
                    st.markdown("""
                    <div class="regulatory-alert">
                        <strong>Regulatory Pathway:</strong> 510(k) Premarket Notification<br>
                        <strong>Requirements:</strong>
                        <ul>
                            <li>Demonstration of substantial equivalence to legally marketed device</li>
                            <li>Performance testing and verification/validation</li>
                            <li>Software documentation (if applicable)</li>
                            <li>Special controls compliance</li>
                            <li>Design controls and risk management documentation</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="regulatory-alert">
                        <strong>Regulatory Pathway:</strong> Most exempt from 510(k), registration and listing required<br>
                        <strong>Requirements:</strong>
                        <ul>
                            <li>General controls</li>
                            <li>Good Manufacturing Practice (GMP) compliance</li>
                            <li>Device listing and establishment registration</li>
                            <li>Medical Device Reporting (MDR)</li>
                            <li>Quality System Regulation (QSR) compliance</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add button to save this classification to the risk matrix
                if st.button("Add to Risk Matrix"):
                    # Calculate risk scores based on classification
                    if "Class III" in result['class']:
                        safety_score = 8
                        compliance_score = 9
                    elif "Class II" in result['class']:
                        safety_score = 5
                        compliance_score = 6
                    else:
                        safety_score = 3
                        compliance_score = 4
                    
                    # Adjust for additional risk factors
                    if result['sterile']:
                        safety_score += 1
                    
                    if result['software']:
                        safety_score += 1
                        
                    if result['active']:
                        safety_score += 1
                        
                    if result['combination']:
                        compliance_score += 2
                        
                    # Cap at 10
                    safety_score = min(10, safety_score)
                    compliance_score = min(10, compliance_score)
                    
                    # Add to risk matrix
                    weighted_risk = safety_score * 0.5 + compliance_score * 0.35 + 5 * 0.15  # Default logistics score of 5
                    
                    # Determine risk level
                    if weighted_risk > 7:
                        risk_level = "High Risk"
                        risk_color = "#c62828"  # Red
                    elif weighted_risk > 4:
                        risk_level = "Moderate Risk"
                        risk_color = "#ff8f00"  # Amber
                    else:
                        risk_level = "Low Risk"
                        risk_color = "#00796b"  # Green
                    
                    # Create risk matrix entry
                    new_row = {
                        'product_name': result['name'],
                        'safety_score': safety_score,
                        'compliance_score': compliance_score,
                        'logistics_score': 5,  # Default to middle value
                        'financial_score': 5,  # Default to middle value
                        'weighted_risk': weighted_risk,
                        'risk_level': risk_level,
                        'risk_color': risk_color,
                        'timestamp': datetime.now(),
                        'notes': f"Auto-classified as {result['class']} via the classification tool",
                        'device_class': result['class'].split(' ')[0]  # Extract just the class part
                    }
                    
                    # Add to dataframe if it exists
                    if 'risk_matrix_data' in st.session_state:
                        st.session_state.risk_matrix_data = pd.concat([
                            st.session_state.risk_matrix_data, 
                            pd.DataFrame([new_row])
                        ], ignore_index=True)
                        
                        st.success(f"Added {result['name']} to risk matrix!")
                        st.info("Switch to the 'Risk Matrix' tab to view your updated risk matrix")
            else:
                st.markdown("""
                <div style="text-align: center; color: #6b7280; padding: 2rem 0;">
                    Complete the form to see classification results
                </div>
                """, unsafe_allow_html=True)
        
        # Add guidance information
        st.markdown("### Classification Guidance")
        st.markdown("""
        <div class="info-box">
            <h4>Device Classification Information</h4>
            <p>The FDA classifies medical devices based on the risks they pose to patients and users:</p>
            <ul>
                <li><strong>Class I (Low Risk):</strong> General controls, generally exempt from premarket notification</li>
                <li><strong>Class II (Medium Risk):</strong> Special controls and 510(k) premarket notification</li>
                <li><strong>Class III (High Risk):</strong> Premarket approval (PMA) required</li>
            </ul>
            <p>Key factors that influence classification include:</p>
            <ul>
                <li>Invasiveness (non-invasive, invasive, implantable)</li>
                <li>Contact type (surface, external communicating, implantable)</li>
                <li>Duration of use (transient, short-term, long-term)</li>
                <li>Active vs. passive function</li>
                <li>Intended use (diagnostic, therapeutic, life-sustaining)</li>
                <li>Combination with drugs or biologics</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)"""
MedDevROI - Medical Device ROI & Risk Analysis Suite
A comprehensive analytics tool for evaluating medical device investments and risks.
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

# App configuration - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="MedDevROI | Medical Device ROI & Risk Analysis Suite",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define color scheme for medical device context
COLOR_SCHEME = {
    "primary": "#0055a5",    # Medical blue
    "secondary": "#00a3a3",  # Teal
    "background": "#f0f4f8",
    "positive": "#00796b",   # Dark teal
    "negative": "#c62828",   # Medical red
    "warning": "#ff8f00",    # Amber
    "neutral": "#1565c0",    # Darker blue
    "text_dark": "#263238",
    "text_light": "#ecf0f1",
    "regulatory": "#4527a0"  # Purple for regulatory elements
}

# Initialize app
if 'optimizer' not in st.session_state:
    st.session_state.optimizer = None
    
# Initialize page state
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"
    
# Initialize view state for scenario details
if 'view_scenario' not in st.session_state:
    st.session_state.view_scenario = False
    
# Initialize selected scenario
if 'selected_scenario' not in st.session_state:
    st.session_state.selected_scenario = None

# Initialize FMEA data structures
if 'design_fmea_data' not in st.session_state:
    st.session_state.design_fmea_data = pd.DataFrame(columns=[
        'id', 'item', 'function', 'failure_mode', 'effect', 'cause', 
        'current_controls', 'sev', 'occ', 'det', 'rpn', 'recommended_action',
        'action_responsibility', 'target_date', 'actions_taken', 
        'new_sev', 'new_occ', 'new_det', 'new_rpn', 'status', 'date_created',
        'date_updated', 'design_phase'
    ])

if 'problem_fmea_data' not in st.session_state:
    st.session_state.problem_fmea_data = pd.DataFrame(columns=[
        'id', 'item', 'problem_description', 'failure_mode', 'effect', 'cause', 
        'current_controls', 'sev', 'occ', 'det', 'rpn', 'recommended_action',
        'action_responsibility', 'target_date', 'actions_taken', 
        'new_sev', 'new_occ', 'new_det', 'new_rpn', 'status', 'date_created',
        'date_updated', 'problem_date'
    ])

# Custom CSS with medical focus
st.markdown("""
<style>
    /* Hide default Streamlit top bar buttons to avoid confusion with our custom nav */
    .stButton > button {
        margin-top: 0;
        visibility: visible;
        height: auto;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        background-color: #0055a5;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: 500;
    }
    
    div[data-testid="stHorizontalBlock"] .stButton > button {
        visibility: visible !important;
        height: auto !important;
        padding: 0.5rem 1rem !important;
        margin: 0.25rem !important;
        background-color: transparent;
        color: #0055a5;
        border: none;
        border-radius: 4px;
        font-weight: 500;
    }
    
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        background-color: rgba(0, 85, 165, 0.1);
        color: #003c75;
    }
    
    /* Main styling */
    body, .stApp {
        background-color: #f0f4f8;
        color: #263238;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        color: #0055a5;
    }
    
    /* Form styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 4px;
        border: 1px solid #bdc3c7;
    }
    
    /* Dataframe styling */
    .stDataFrame thead tr th {
        background-color: #0055a5;
        color: white;
        padding: 8px 12px;
        font-weight: 500;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background-color: rgba(236, 240, 241, 0.5);
    }
    .stDataFrame tbody tr:hover {
        background-color: rgba(0, 85, 165, 0.1);
    }
    
    /* Cards */
    .css-card {
        border-radius: 8px;
        padding: 1.5rem;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* Metric display */
    .metric-container {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
        border-color: #0055a5;
        border-bottom: 3px solid #0055a5;
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
        background-color: #263238;
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
    
    /* Medical/regulatory specific components */
    .regulatory-alert {
        background-color: #f3f3fd;
        border-left: 5px solid #4527a0;
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    
    .clinical-validation {
        background-color: #e8f5e9;
        border-left: 5px solid #00796b;
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    
    /* Risk indication styling */
    .high-risk {
        color: #c62828;
        font-weight: 500;
    }
    .moderate-risk {
        color: #ff8f00;
        font-weight: 500;
    }
    .low-risk {
        color: #00796b;
        font-weight: 500;
    }
    
    /* Standard components */
    .info-box {
        background-color: rgba(21, 101, 192, 0.1);
        border-left: 5px solid #1565c0;
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: rgba(255, 143, 0, 0.1);
        border-left: 5px solid #ff8f00;
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
        background-color: #0055a5;
    }
    .css-1d391kg .sidebar-content {
        padding: 1rem;
    }
    
    /* Charts */
    .js-plotly-plot {
        border-radius: 8px;
        background-color: white;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Top navigation bar */
    .topnav {
        background-color: #0055a5;
        overflow: hidden;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Dashboard cards */
    .dashboard-card {
        background-color: white;
        border-radius: 8px;
        padding: 1.25rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: all 0.3s;
    }
    .dashboard-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .dashboard-card-title {
        font-weight: 600;
        color: #0055a5;
        margin-bottom: 0.75rem;
    }
    
    /* Card grid layout */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        grid-gap: 1rem;
    }
    
    /* Nav page links */
    .nav-page {
        color: rgba(255, 255, 255, 0.85);
        padding: 8px 15px;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: 500;
        user-select: none;
    }
    .nav-page:hover {
        background-color: rgba(255, 255, 255, 0.15);
        color: white;
    }
    .nav-page.active {
        background-color: #00a3a3;
        color: white;
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

def get_device_risk_color(risk_level):
    """Get color based on medical device risk level"""
    if risk_level == "High Risk" or risk_level == "Class III":
        return "#c62828"  # Red
    elif risk_level == "Moderate Risk" or risk_level == "Class II":
        return "#ff8f00"  # Amber
    else:
        return "#00796b"  # Green
    
def get_regulatory_impact_color(impact):
    """Get color based on regulatory impact level"""
    if impact == "New submission":
        return "#c62828"  # Red
    elif impact == "Special 510(k)":
        return "#ff8f00"  # Amber
    elif impact == "Letter to File":
        return "#2196f3"  # Blue
    else:
        return "#00796b"  # Green

def navigate_to(page_name):
    """Function to navigate to a specific page"""
    st.session_state.page = page_name
    st.experimental_rerun()

# Monte Carlo simulation function
def run_monte_carlo_simulation(base_parameters, parameter_ranges, num_simulations=1000):
    """
    Run a Monte Carlo simulation for ROI analysis
    
    Args:
        base_parameters: Dictionary with base values
        parameter_ranges: Dictionary with min/max percent changes
        num_simulations: Number of simulations to run
    
    Returns:
        DataFrame with simulation results
    """
    results = []
    
    for _ in range(num_simulations):
        # Generate random values for each parameter within defined ranges
        params = {}
        for param, (min_pct, max_pct) in parameter_ranges.items():
            if param in base_parameters:
                # Apply random percentage change to base value
                pct_change = np.random.uniform(min_pct, max_pct) / 100.0
                params[param] = base_parameters[param] * (1 + pct_change)
            else:
                params[param] = np.random.uniform(min_pct, max_pct)
        
        # Calculate financial metrics
        monthly_sales = params['sales_30']
        return_rate = params['return_rate']
        monthly_returns = monthly_sales * return_rate / 100
        reduction_rate = params['reduction_rate']
        avoided_returns = monthly_returns * reduction_rate / 100
        
        solution_cost = params['solution_cost']
        regulatory_cost = params.get('regulatory_cost', 0)
        additional_cost = params['additional_cost_per_item']
        avg_price = params['avg_sale_price']
        current_unit_cost = params['current_unit_cost']
        new_unit_cost = current_unit_cost + additional_cost
        
        monthly_savings = avoided_returns * (avg_price - new_unit_cost)
        monthly_additional_costs = monthly_sales * additional_cost
        monthly_net = monthly_savings - monthly_additional_costs
        annual_net = monthly_net * 12
        
        total_investment = solution_cost + regulatory_cost
        
        # Calculate ROI and breakeven
        if total_investment > 0 and monthly_net > 0:
            roi = (annual_net / total_investment) * 100
            breakeven_months = total_investment / monthly_net
        else:
            roi = 0
            breakeven_months = float('inf')
        
        # Store results
        results.append({
            'monthly_net': monthly_net,
            'annual_net': annual_net,
            'roi': roi,
            'breakeven_months': breakeven_months
        })
    
    return pd.DataFrame(results)

# Data management class
class ReturnOptimizer:
    def __init__(self):
        self.load_data()
        self.default_examples = [
            {
                "scenario_name": "Premium Packaging",
                "sku": "DEVICE-123",
                "sales_30": 750,
                "avg_sale_price": 89.99,
                "sales_channel": "Hospital",
                "returns_30": 94,
                "solution": "Premium unboxing experience with clearer usage instructions",
                "solution_cost": 5000,
                "additional_cost_per_item": 1.25,
                "current_unit_cost": 32.50,
                "reduction_rate": 30,
                "sales_365": 9125,
                "returns_365": 1140,
                "device_class": "Class II",
                "regulatory_impact": "Letter to File",
                "adverse_events": 12,
                "tag": "Packaging"
            },
            {
                "scenario_name": "Improved Surgical Instructions",
                "sku": "IMPLANT-456",
                "sales_30": 420,
                "avg_sale_price": 129.99,
                "sales_channel": "Direct to Provider",
                "returns_30": 71,
                "solution": "Enhanced surgical technique guide and training videos",
                "solution_cost": 7500,
                "additional_cost_per_item": 0,
                "current_unit_cost": 45.75,
                "reduction_rate": 35,
                "sales_365": 5100,
                "returns_365": 860,
                "device_class": "Class III",
                "regulatory_impact": "Special 510(k)",
                "adverse_events": 25,
                "tag": "Instructions for Use"
            },
            {
                "scenario_name": "Product Design Improvement",
                "sku": "DIAGNOSTICS-789",
                "sales_30": 1250,
                "avg_sale_price": 49.99,
                "sales_channel": "Distributor",
                "returns_30": 138,
                "solution": "Redesigned interface with improved usability",
                "solution_cost": 12000,
                "additional_cost_per_item": 1.75,
                "current_unit_cost": 18.50,
                "reduction_rate": 42,
                "sales_365": 15200,
                "returns_365": 1675,
                "device_class": "Class II",
                "regulatory_impact": "Special 510(k)",
                "adverse_events": 18,
                "tag": "Design Improvement"
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
                'monthly_net_benefit', 'tag', 'device_class', 'regulatory_impact',
                'adverse_events', 'regulatory_cost'
            ])
            st.session_state['scenarios'] = self.scenarios
        else:
            self.scenarios = st.session_state['scenarios']
            
        # Initialize risk matrix data if not present
        if 'risk_matrix_data' not in st.session_state:
            st.session_state.risk_matrix_data = pd.DataFrame(columns=[
                'product_name', 'safety_score', 'compliance_score', 'logistics_score', 
                'weighted_risk', 'risk_level', 'risk_color'])
    
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
                     current_unit_cost, reduction_rate, sales_365=None, returns_365=None, 
                     tag=None, device_class="Class II", regulatory_impact="No impact", 
                     adverse_events=0, regulatory_cost=0):
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
            amortized_solution_cost = (solution_cost + regulatory_cost) / sales_365 if sales_365 > 0 else 0
            margin_after_amortized = margin_after - amortized_solution_cost
            
            # Calculate savings and ROI
            savings_per_avoided_return = avg_sale_price - new_unit_cost
            savings_30 = avoided_returns_30 * savings_per_avoided_return
            annual_savings = avoided_returns_365 * savings_per_avoided_return
            
            annual_additional_costs = additional_cost_per_item * sales_365
            net_benefit = annual_savings - annual_additional_costs
            monthly_net_benefit = net_benefit / 12
            
            # Calculate ROI metrics
            total_investment = solution_cost + regulatory_cost
            roi = break_even_days = break_even_months = score = None
            if total_investment > 0 and net_benefit > 0:
                roi = (net_benefit / total_investment) * 100  # as percentage
                break_even_days = (total_investment / net_benefit) * 365
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
                'tag': tag,
                'device_class': device_class,
                'regulatory_impact': regulatory_impact,
                'adverse_events': adverse_events,
                'regulatory_cost': regulatory_cost
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
            current['sales_365'], current['returns_365'], current['tag'],
            current.get('device_class', 'Class II'),
            current.get('regulatory_impact', 'No impact'),
            current.get('adverse_events', 0),
            current.get('regulatory_cost', 0)
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
            scenario['sales_365'], scenario['returns_365'], scenario['tag'],
            scenario.get('device_class', 'Class II'),
            scenario.get('regulatory_impact', 'No impact'),
            scenario.get('adverse_events', 0),
            scenario.get('regulatory_cost', 0)
        )
        
        return success, message
