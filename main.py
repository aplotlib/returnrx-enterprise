"""
MedDevROI - Medical Device ROI & Risk Analysis Suite
A comprehensive analytics tool for evaluating medical device investments and risks.

This application helps medical device companies analyze and optimize:
- Return reduction strategies with precise ROI calculations
- Risk analysis for medical device classification
- Scenario planning and interactive visualizations
- Regulatory impact assessment
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
    "text_light": "#eceff1",
    "regulatory": "#4527a0"  # Purple for regulatory elements
}

# Custom CSS with medical focus
st.markdown("""
<style>
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
    
    /* Button styling */
    .stButton>button {
        background-color: #0055a5;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #003c75;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
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

# Data management
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

# App functions
def display_header():
    """Display app header with logo and navigation"""
    col1, col2 = st.columns([1, 5])
    
    # Logo (placeholder - in a real app, replace with actual logo)
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 10px">
            <h1 style="font-size: 32px; margin: 0; color: #0055a5;">🏥</h1>
            <p style="margin: 0; font-weight: 600; color: #00a3a3;">MedDevROI</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Title and description
    with col2:
        st.title("Medical Device ROI & Risk Analysis Suite")
        st.caption("Evaluate medical device investments with precision to improve patient outcomes and bottom-line performance.")

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
    total_investment = df['solution_cost'].sum() + df['regulatory_cost'].sum()
    portfolio_roi = (total_net_benefit / total_investment * 100) if total_investment > 0 else 0
    
    # Additional medical device metrics
    total_adverse_events = df['adverse_events'].sum() if 'adverse_events' in df.columns else 0
    potential_adverse_reduction = df.apply(lambda x: x['adverse_events'] * (x['reduction_rate']/100), axis=1).sum() if 'adverse_events' in df.columns else 0
    
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
    
    # Add patient safety metrics row
    st.markdown("##### Patient Safety Impact")
    safety_col1, safety_col2 = st.columns(2)
    
    with safety_col1:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Total Related Adverse Events</p>
            <p class="metric-value" style="color: {COLOR_SCHEME['negative']};">{total_adverse_events}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with safety_col2:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Potential Reduction in Adverse Events</p>
            <p class="metric-value" style="color: {COLOR_SCHEME['positive']};">{potential_adverse_reduction:.1f}</p>
        </div>
        """, unsafe_allow_html=True)

def create_scenario_form():
    """Create form for adding a new scenario with medical device context"""
    with st.form(key="scenario_form"):
        st.subheader("Add New Scenario")
        
        col1, col2 = st.columns(2)
        with col1:
            scenario_name = st.text_input("Scenario Name", help="A memorable name for this investment scenario")
            sku = st.text_input("Product/Device ID", help="Medical device identifier")
            
            # Add medical device specific fields
            device_class = st.selectbox("Device Classification", 
                                      ["Class I", "Class II", "Class III"], 
                                      help="Medical device risk classification")
            
            regulatory_impact = st.selectbox("Regulatory Impact",
                                           ["No impact", "Letter to File", "Special 510(k)", "New submission"],
                                           help="Level of regulatory submission required")
            
            sales_channel = st.selectbox("Distribution Channel", 
                                       ["Hospital", "Clinic", "Direct to Provider", "Distributor", "Other"],
                                       help="Primary distribution channel")
            
            solution = st.text_input("Proposed Solution", help="Description of the return reduction or improvement strategy")
        
        with col2:
            # More specific tags for medical devices
            tag = st.selectbox("Category", 
                             ["Design Improvement", "Packaging", "Instructions for Use", 
                              "Training Material", "Quality System", "Supply Chain", "Other"],
                             help="Category of improvement strategy")
            
            adverse_events = st.number_input("Related Adverse Events", min_value=0, 
                                           help="Number of related adverse events in past 12 months")
            
            sales_30 = st.number_input("30-day Sales (units)", min_value=0, help="Units sold in the last 30 days")
            returns_30 = st.number_input("30-day Returns/Complaints (units)", min_value=0, 
                                        help="Units returned in the last 30 days")
            
            avg_sale_price = st.number_input("Average Sale Price ($)", min_value=0.0, format="%.2f", 
                                           help="Average selling price per unit")
            
            current_unit_cost = st.number_input("Current Unit Cost ($)", min_value=0.0, format="%.2f", 
                                              help="Cost to produce/acquire each unit")
            
        st.markdown("---")
        col3, col4 = st.columns(2)
        
        with col3:
            solution_cost = st.number_input("Implementation Cost ($)", min_value=0.0, format="%.2f", 
                                          help="One-time investment required for the solution")
            
            # Add regulatory cost field
            if regulatory_impact != "No impact":
                regulatory_cost = st.number_input("Regulatory Submission Cost ($)", min_value=0.0, format="%.2f",
                                                help="Cost associated with regulatory submissions")
            else:
                regulatory_cost = 0.0
            
            additional_cost_per_item = st.number_input("Additional Cost per Item ($)", min_value=0.0, format="%.2f", 
                                                     help="Any additional per-unit cost from implementing the solution")
        
        with col4:
            reduction_rate = st.slider("Estimated Return/Complaint Reduction (%)", 0, 100, 20, 
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
                
                if adverse_events > 0:
                    avoided_adverse = adverse_events * (reduction_rate/100) / 12  # Monthly reduction
                    st.metric("Potential Monthly Adverse Event Reduction", f"{avoided_adverse:.2f}")
            
            with preview_col3:
                # Simple ROI calculation for preview
                total_cost = solution_cost + regulatory_cost
                monthly_cost = additional_cost_per_item * sales_30
                monthly_savings = avoided_returns * (avg_sale_price - (current_unit_cost + additional_cost_per_item))
                monthly_net = monthly_savings - monthly_cost
                
                if total_cost > 0 and monthly_net > 0:
                    breakeven_months = total_cost / monthly_net
                    st.metric("Estimated Breakeven", f"{breakeven_months:.1f} months")
                    st.metric("Est. Annual ROI", f"{(monthly_net * 12 / total_cost) * 100:.1f}%")
                else:
                    st.metric("Estimated Breakeven", "N/A")
                    st.metric("Est. Annual ROI", "N/A")
        
        # If this is a regulatory impactful change, show regulatory alert
        if regulatory_impact in ["Special 510(k)", "New submission"]:
            st.markdown("""
            <div class="regulatory-alert">
                <strong>Regulatory Alert:</strong> This change may require significant regulatory submission. 
                Ensure your Quality Management System is updated accordingly and all design controls are documented.
            </div>
            """, unsafe_allow_html=True)
        
        # Submit button
        submitted = st.form_submit_button("Save Scenario")
        
        if submitted:
            success, message = optimizer.add_scenario(
                scenario_name, sku, sales_30, avg_sale_price, sales_channel,
                returns_30, solution, solution_cost, additional_cost_per_item,
                current_unit_cost, reduction_rate, sales_365, returns_365, tag,
                device_class, regulatory_impact, adverse_events, regulatory_cost
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
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sku_filter = st.multiselect("Filter by SKU", 
                                   options=sorted(df['sku'].unique()),
                                   default=[])
    
    with col2:
        channel_filter = st.multiselect("Filter by Channel", 
                                      options=sorted(df['sales_channel'].unique()),
                                      default=[])
    
    with col3:
        tag_filter = st.multiselect("Filter by Category", 
                                  options=sorted(df['tag'].dropna().unique()),
                                  default=[])
    
    with col4:
        # Add medical device class filter
        device_class_filter = st.multiselect("Filter by Device Class",
                                           options=sorted(df['device_class'].dropna().unique()),
                                           default=[])
    
    # Apply filters
    filtered_df = df.copy()
    
    if sku_filter:
        filtered_df = filtered_df[filtered_df['sku'].isin(sku_filter)]
    
    if channel_filter:
        filtered_df = filtered_df[filtered_df['sales_channel'].isin(channel_filter)]
    
    if tag_filter:
        filtered_df = filtered_df[filtered_df['tag'].isin(tag_filter)]
        
    if device_class_filter:
        filtered_df = filtered_df[filtered_df['device_class'].isin(device_class_filter)]
    
    # Display table
    if filtered_df.empty:
        st.warning("No scenarios match your filters. Try adjusting your criteria.")
        return
    
    # Prepare display columns
    display_df = filtered_df[[
        'uid', 'scenario_name', 'sku', 'device_class', 'regulatory_impact',
        'return_rate', 'reduction_rate', 'solution_cost', 'regulatory_cost',
        'roi', 'break_even_months', 'net_benefit', 'score'
    ]].copy()
    
    # Format columns for display
    display_df['return_rate'] = display_df['return_rate'].apply(lambda x: f"{x:.1f}%")
    display_df['reduction_rate'] = display_df['reduction_rate'].apply(lambda x: f"{x:.0f}%")
    display_df['solution_cost'] = display_df['solution_cost'].apply(lambda x: f"${x:,.2f}")
    display_df['regulatory_cost'] = display_df['regulatory_cost'].apply(lambda x: f"${x:,.2f}")
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
    
    # Format device class with appropriate coloring
    def format_device_class(row):
        device_class = row['device_class']
        color = get_device_risk_color(device_class)
        return f"<span style='color: {color}; font-weight: bold;'>{device_class}</span>"
    
    display_df['device_class'] = filtered_df.apply(format_device_class, axis=1)
    
    # Format regulatory impact with appropriate coloring
    def format_regulatory_impact(row):
        impact = row['regulatory_impact']
        color = get_regulatory_impact_color(impact)
        return f"<span style='color: {color}; font-weight: bold;'>{impact}</span>"
    
    display_df['regulatory_impact'] = filtered_df.apply(format_regulatory_impact, axis=1)
    
    # Rename columns for display
    display_df = display_df.rename(columns={
        'scenario_name': 'Scenario',
        'sku': 'SKU',
        'device_class': 'Class',
        'regulatory_impact': 'Reg. Impact',
        'return_rate': 'Return Rate',
        'reduction_rate': 'Reduction',
        'solution_cost': 'Implementation',
        'regulatory_cost': 'Reg. Cost',
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
                   ),
                   "Class": st.column_config.Column(
                       "Class",
                       help="FDA medical device classification",
                       width="small"
                   ),
                   "Reg. Impact": st.column_config.Column(
                       "Reg. Impact",
                       help="Regulatory submission impact",
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
        
        # Format device class with color
        device_class = scenario.get('device_class', 'Class II')
        device_color = get_device_risk_color(device_class)
        st.markdown(f"""
        **Device Class:** <span style='color: {device_color}; font-weight: bold;'>{device_class}</span>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Sales Channel:** {scenario['sales_channel']}")
        st.markdown(f"**Category:** {scenario['tag'] or 'Not categorized'}")
    
    with col2:
        st.markdown(f"**Monthly Sales:** {scenario['sales_30']} units")
        st.markdown(f"**Monthly Returns:** {scenario['returns_30']} units")
        st.markdown(f"**Return Rate:** {scenario['return_rate']:.2f}%")
        
        # Add adverse events if available
        if 'adverse_events' in scenario and scenario['adverse_events'] > 0:
            st.markdown(f"**Related Adverse Events (Annual):** {scenario['adverse_events']}")
    
    with col3:
        st.markdown(f"**Average Sale Price:** ${scenario['avg_sale_price']:.2f}")
        st.markdown(f"**Current Unit Cost:** ${scenario['current_unit_cost']:.2f}")
        st.markdown(f"**Current Margin:** ${scenario['margin_before']:.2f} ({(scenario['margin_before']/scenario['avg_sale_price']*100):.1f}%)")
        
        # Format regulatory impact with color
        reg_impact = scenario.get('regulatory_impact', 'No impact')
        reg_color = get_regulatory_impact_color(reg_impact)
        st.markdown(f"""
        **Regulatory Impact:** <span style='color: {reg_color}; font-weight: bold;'>{reg_impact}</span>
        """, unsafe_allow_html=True)
    
    # Solution details
    st.markdown("---")
    st.markdown("### Solution Details")
    
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown(f"**Proposed Solution:** {scenario['solution']}")
        st.markdown(f"**Expected Reduction:** {scenario['reduction_rate']:.1f}%")
        st.markdown(f"**Additional Cost/Item:** ${scenario['additional_cost_per_item']:.2f}")
        
        # Show regulatory cost if applicable
        if 'regulatory_cost' in scenario and scenario['regulatory_cost'] > 0:
            st.markdown(f"**Regulatory Cost:** ${scenario['regulatory_cost']:.2f}")
    
    with col5:
        st.markdown(f"**Implementation Cost:** ${scenario['solution_cost']:.2f}")
        
        # Show total investment including regulatory costs
        total_investment = scenario['solution_cost']
        if 'regulatory_cost' in scenario:
            total_investment += scenario['regulatory_cost']
        st.markdown(f"**Total Investment:** ${total_investment:.2f}")
        
        st.markdown(f"**New Unit Cost:** ${scenario['new_unit_cost']:.2f}")
        st.markdown(f"**New Margin:** ${scenario['margin_after']:.2f} ({(scenario['margin_after']/scenario['avg_sale_price']*100):.1f}%)")
    
    # Add regulatory alert if significant impact
    if scenario.get('regulatory_impact') in ["Special 510(k)", "New submission"]:
        st.markdown("""
        <div class="regulatory-alert">
            <strong>Regulatory Consideration:</strong> This change requires significant regulatory submission. 
            Ensure all design controls are documented and verification/validation is completed.
        </div>
        """, unsafe_allow_html=True)
    
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
    
    # Add patient safety metrics if applicable
    if 'adverse_events' in scenario and scenario['adverse_events'] > 0:
        st.markdown("##### Patient Safety Impact")
        safety_col1, safety_col2 = st.columns(2)
        
        with safety_col1:
            annual_avoided_events = scenario['adverse_events'] * (scenario['reduction_rate']/100)
            st.metric(
                "Potential Annual Reduction in Adverse Events",
                f"{annual_avoided_events:.1f}",
                delta=None
            )
        
        with safety_col2:
            st.metric(
                "Potential Reduction Rate",
                f"{scenario['reduction_rate']:.1f}%",
                delta=None
            )
    
    # Cost breakdown
    st.markdown("### Cost-Benefit Analysis")
    cost_col1, cost_col2 = st.columns(2)
    
    with cost_col1:
        # Cost breakdown
        cost_data = [
            {"Category": "Implementation Cost", "Amount": scenario['solution_cost']}
        ]
        
        if 'regulatory_cost' in scenario and scenario['regulatory_cost'] > 0:
            cost_data.append({"Category": "Regulatory Cost", "Amount": scenario['regulatory_cost']})
            
        cost_data.append({"Category": "Annual Additional Costs", "Amount": scenario['annual_additional_costs']})
        
        cost_df = pd.DataFrame(cost_data)
        
        fig_cost = px.bar(
            cost_df, 
            x="Category", 
            y="Amount",
            title="Costs",
            color="Category",
            color_discrete_map={
                "Implementation Cost": COLOR_SCHEME["warning"],
                "Regulatory Cost": COLOR_SCHEME["regulatory"],
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
    
    # Add adverse events if applicable
    if 'adverse_events' in scenario and scenario['adverse_events'] > 0:
        before_after_data["Adverse Events"] = [
            scenario['adverse_events'],
            scenario['adverse_events'] * (1 - scenario['reduction_rate']/100)
        ]
    
    before_after_df = pd.DataFrame(before_after_data)
    
    # Determine number of subplots based on whether adverse events exist
    n_plots = 3 if 'Adverse Events' in before_after_data else 2
    fig_returns = make_subplots(rows=1, cols=n_plots, 
                               subplot_titles=["Annual Returns", "Return Rate"] + 
                                             (["Adverse Events"] if 'Adverse Events' in before_after_data else []))
    
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
    
    # Add adverse events chart if applicable
    if 'Adverse Events' in before_after_data:
        fig_returns.add_trace(
            go.Bar(
                x=before_after_df["State"],
                y=before_after_df["Adverse Events"],
                marker_color=[COLOR_SCHEME["negative"], COLOR_SCHEME["positive"]],
                text=before_after_df["Adverse Events"].apply(lambda x: f"{x:.1f}"),
                textposition="auto"
            ),
            row=1, col=3
        )
    
    fig_returns.update_layout(
        height=400,
        showlegend=False,
        title_text="Before vs After Implementation"
    )
    
    fig_returns.update_yaxes(title_text="Units", row=1, col=1)
    fig_returns.update_yaxes(title_text="Percentage", row=1, col=2)
    if 'Adverse Events' in before_after_data:
        fig_returns.update_yaxes(title_text="Events", row=1, col=3)
    
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
        color="device_class" if "device_class" in plot_df.columns else "score",
        hover_name="scenario_name",
        text="scenario_name",
        size_max=size_max,
        labels={
            "break_even_months": "Break-even Time (months)",
            "roi": "Return on Investment (%)",
            "device_class": "Device Class",
            "score": "ROI Score"
        },
        title="Investment ROI vs. Break-even Time",
        color_discrete_map={
            "Class I": "#00796b",
            "Class II": "#ff8f00",
            "Class III": "#c62828"
        } if "device_class" in plot_df.columns else None
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
    
    # Add regulatory impact analysis
    if 'regulatory_impact' in df.columns:
        st.markdown("### Regulatory Impact Analysis")
        
        # Group by regulatory impact
        reg_group = df.groupby('regulatory_impact').agg({
            'solution_cost': 'sum',
            'regulatory_cost': 'sum',
            'roi': 'mean',
            'net_benefit': 'sum',
            'scenario_name': 'count'
        }).reset_index()
        
        reg_group['total_cost'] = reg_group['solution_cost'] + reg_group['regulatory_cost']
        reg_group['count'] = reg_group['scenario_name']
        
        # Create a scatter plot
        fig_reg = px.scatter(
            reg_group,
            x="total_cost",
            y="roi",
            size="net_benefit",
            color="regulatory_impact",
            size_max=60,
            hover_data=["count"],
            labels={
                "total_cost": "Total Investment ($)",
                "roi": "Average ROI (%)",
                "net_benefit": "Net Benefit ($)",
                "count": "Number of Scenarios"
            },
            title="ROI vs. Investment by Regulatory Impact",
            color_discrete_map={
                "No impact": "#00796b",
                "Letter to File": "#2196f3",
                "Special 510(k)": "#ff8f00",
                "New submission": "#c62828"
            }
        )
        
        st.plotly_chart(fig_reg, use_container_width=True)
    
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
    
    # Add patient safety impact visualization
    if 'adverse_events' in df.columns and 'reduction_rate' in df.columns:
        st.markdown("### Patient Safety Impact")
        
        # Calculate potential adverse event reduction
        df['adverse_events_reduction'] = df['adverse_events'] * (df['reduction_rate'] / 100)
        
        # Only show if there are any adverse events
        if df['adverse_events'].sum() > 0:
            # Create visualization
            fig_safety = px.bar(
                df.sort_values('adverse_events_reduction', ascending=False).head(10),
                x="scenario_name",
                y="adverse_events_reduction",
                color="device_class",
                labels={
                    "scenario_name": "Improvement Scenario",
                    "adverse_events_reduction": "Potential Adverse Event Reduction",
                    "device_class": "Device Class"
                },
                title="Patient Safety Impact by Improvement Scenario",
                color_discrete_map={
                    "Class I": "#00796b",
                    "Class II": "#ff8f00",
                    "Class III": "#c62828"
                }
            )
            
            st.plotly_chart(fig_safety, use_container_width=True)
        else:
            st.info("No adverse events data available for analysis.")
    
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

def display_risk_matrix():
    """Display risk matrix for medical device analysis"""
    st.subheader("Medical Device Risk Analysis Matrix")
    
    # Create tabs for Risk Matrix and Device Classification
    matrix_tab, classifier_tab = st.tabs(["Risk Matrix", "Device Classification"])
    
    with matrix_tab:
        # Create a dataframe to store risk entries if not already present
        if 'risk_matrix_data' not in st.session_state:
            st.session_state.risk_matrix_data = pd.DataFrame(columns=[
                'product_name', 'safety_score', 'compliance_score', 'logistics_score', 
                'weighted_risk', 'risk_level', 'risk_color'])
        
        with st.form("risk_matrix_form"):
            col1, col2 = st.columns(2)
            with col1:
                product_name = st.text_input("Product Name")
            
            with col2:
                st.markdown("##### Risk Scores (0-10)")
                safety_score = st.slider("Safety Score", 0, 10, 5, 
                                        help="Higher scores indicate higher risk")
                compliance_score = st.slider("Compliance Score", 0, 10, 5,
                                           help="Higher scores indicate higher compliance risk")
                logistics_score = st.slider("Logistics Score", 0, 10, 5,
                                          help="Higher scores indicate higher logistics/supply chain risk")
            
            submitted = st.form_submit_button("Add to Risk Matrix")
            
            if submitted:
                if not product_name:
                    st.error("Product name is required")
                else:
                    # Calculate weighted risk based on the example HTML tool
                    weighted_risk = safety_score * 0.5 + compliance_score * 0.35 + logistics_score * 0.15
                    
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
                        'safety_score': safety_score,
                        'compliance_score': compliance_score,
                        'logistics_score': logistics_score,
                        'weighted_risk': weighted_risk,
                        'risk_level': risk_level,
                        'risk_color': risk_color
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
            
            # Prepare display dataframe
            display_df = st.session_state.risk_matrix_data.copy()
            
            # Format risk level with color
            def format_risk_level(row):
                return f"<span style='color: {row['risk_color']}; font-weight: bold;'>{row['risk_level']} ({row['weighted_risk']:.1f})</span>"
            
            display_df['formatted_risk'] = display_df.apply(format_risk_level, axis=1)
            
            # Display table
            st.dataframe(
                display_df[['product_name', 'safety_score', 'compliance_score', 
                            'logistics_score', 'formatted_risk']],
                use_container_width=True,
                column_config={
                    "product_name": "Product",
                    "safety_score": "Safety",
                    "compliance_score": "Compliance",
                    "logistics_score": "Logistics",
                    "formatted_risk": "Risk Level"
                },
                hide_index=True
            )
            
            # Add export options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear All Risk Data"):
                    st.session_state.risk_matrix_data = pd.DataFrame(columns=[
                        'product_name', 'safety_score', 'compliance_score', 'logistics_score', 
                        'weighted_risk', 'risk_level', 'risk_color'])
                    st.success("Risk matrix data cleared")
                    st.experimental_rerun()
            
            with col2:
                # Export as CSV
                csv_data = st.session_state.risk_matrix_data.to_csv(index=False).encode()
                st.download_button(
                    "Export Risk Matrix (CSV)",
                    data=csv_data,
                    file_name="risk_matrix_export.csv",
                    mime="text/csv"
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
            
            # Risk matrix heatmap
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
            
            # Add product placements
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
                    <li><span style="color:#c62828; font-weight:bold;">High Risk (>7):</span> Significant safety or compliance concerns</li>
                    <li><span style="color:#ff8f00; font-weight:bold;">Moderate Risk (4-7):</span> Monitor and implement controls</li>
                    <li><span style="color:#00796b; font-weight:bold;">Low Risk (<4):</span> Acceptable risk level</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
    with classifier_tab:
        st.markdown("### Medical Device Classification Tool")
        
        # Create two columns for form and results
        form_col, result_col = st.columns(2)
        
        with form_col:
            st.markdown("##### Device Information")
            device_name = st.text_input("Device Name", key="device_name_classifier")
            contact_type = st.selectbox("Contact Type", 
                                       ["Surface Contact", "Internal Contact"])
            invasiveness = st.selectbox("Invasiveness", 
                                       ["Non-Invasive", "Invasive", "Implantable"])
            
            # Additional fields for more comprehensive classification
            duration = st.selectbox("Duration of Use",
                                  ["Transient (<60 min)", "Short-term (<30 days)", "Long-term (>30 days)"])
            
            active_device = st.checkbox("Active Device (Requires Energy Source)")
            
            if st.button("Classify Device"):
                # Classification logic based on the HTML example and expanded for more nuance
                if invasiveness == "Implantable":
                    risk_class = "Class III - Highest Risk"
                    risk_color = "#c62828"  # Red
                    explanation = "Implantable devices pose significant risks and require PMA submission."
                elif invasiveness == "Invasive" and duration == "Long-term (>30 days)":
                    risk_class = "Class III - Highest Risk"
                    risk_color = "#c62828"  # Red
                    explanation = "Long-term invasive devices pose significant risks to patients."
                elif contact_type == "Internal Contact" or invasiveness == "Invasive":
                    if active_device:
                        risk_class = "Class III - Highest Risk"
                        risk_color = "#c62828"  # Red
                        explanation = "Active devices with internal contact present significant risks."
                    else:
                        risk_class = "Class IIb - High Risk"
                        risk_color = "#ff8f00"  # Amber
                        explanation = "Internal contact or invasive devices require special controls."
                elif active_device:
                    risk_class = "Class II - Medium Risk"
                    risk_color = "#ff8f00"  # Amber
                    explanation = "Active devices generally require 510(k) clearance."
                else:
                    risk_class = "Class I - Low Risk"
                    risk_color = "#00796b"  # Green
                    explanation = "Non-invasive, surface contact devices with minimal risk."
                
                # Store result in session state
                st.session_state.device_classification = {
                    "name": device_name,
                    "class": risk_class,
                    "color": risk_color,
                    "explanation": explanation
                }
        
        with result_col:
            st.markdown("##### Classification Results")
            
            if "device_classification" in st.session_state:
                result = st.session_state.device_classification
                st.markdown(f"""
                <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);">
                    <h4 style="font-weight: bold; margin-bottom: 0.5rem;">Device: {result['name']}</h4>
                    <p style="font-size: 1.5rem; font-weight: 600; color: {result['color']};">{result['class']}</p>
                    <p style="margin-top: 1rem;">{result['explanation']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Add regulatory pathway information
                if "Class III" in result['class']:
                    st.markdown("""
                    <div class="regulatory-alert">
                        <strong>Regulatory Pathway:</strong> Premarket Approval (PMA)<br>
                        <strong>Requirements:</strong> Clinical trials, extensive safety and efficacy data,
                        manufacturing inspection
                    </div>
                    """, unsafe_allow_html=True)
                elif "Class II" in result['class']:
                    st.markdown("""
                    <div class="regulatory-alert">
                        <strong>Regulatory Pathway:</strong> 510(k) Premarket Notification<br>
                        <strong>Requirements:</strong> Demonstration of substantial equivalence to legally marketed device,
                        performance testing
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="regulatory-alert">
                        <strong>Regulatory Pathway:</strong> Most exempt from 510(k), registration and listing required<br>
                        <strong>Requirements:</strong> General controls, GMP compliance
                    </div>
                    """, unsafe_allow_html=True)
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
                <li>Contact type (surface, internal)</li>
                <li>Duration of use (transient, short-term, long-term)</li>
                <li>Active vs. passive function</li>
                <li>Intended use</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

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
                "Implementation Cost Change (%)", 
                min_value=-50, 
                max_value=100, 
                value=0,
                help="Adjust the one-time implementation cost of the solution. For example, -20% means the solution will cost 20% less than the original estimate."
            )
            
            # Regulatory cost change (if applicable)
            if 'regulatory_cost' in base_scenario and base_scenario['regulatory_cost'] > 0:
                regulatory_cost_change = st.slider(
                    "Regulatory Cost Change (%)",
                    min_value=-50,
                    max_value=100,
                    value=0,
                    help="Adjust the regulatory submission and compliance costs. For example, +30% means the regulatory costs will be 30% higher than the original estimate."
                )
            else:
                regulatory_cost_change = 0
        
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
            
            # Adverse events (if applicable)
            if 'adverse_events' in base_scenario and base_scenario['adverse_events'] > 0:
                adverse_events_change = st.slider(
                    "Adverse Events Change (%)",
                    min_value=-50,
                    max_value=100,
                    value=0,
                    help="Adjust the projected number of adverse events. For example, -20% means there will be 20% fewer adverse events than originally estimated."
                )
            else:
                adverse_events_change = 0
        
        # Calculate new values
        new_sales_30 = base_scenario['sales_30'] * (1 + sales_change/100)
        new_return_rate = base_scenario['return_rate'] * (1 + return_rate_change/100)
        new_returns_30 = (new_sales_30 * new_return_rate / 100)
        new_solution_cost = base_scenario['solution_cost'] * (1 + solution_cost_change/100)
        
        if 'regulatory_cost' in base_scenario:
            new_regulatory_cost = base_scenario['regulatory_cost'] * (1 + regulatory_cost_change/100)
        else:
            new_regulatory_cost = 0
            
        new_reduction_rate = base_scenario['reduction_rate'] * (1 + reduction_effectiveness/100)
        new_additional_cost = base_scenario['additional_cost_per_item'] * (1 + additional_cost_change/100)
        new_avg_price = base_scenario['avg_sale_price'] * (1 + price_change/100)
        
        if 'adverse_events' in base_scenario:
            new_adverse_events = base_scenario['adverse_events'] * (1 + adverse_events_change/100)
        else:
            new_adverse_events = 0
        
        # Ensure values are within logical bounds
        new_reduction_rate = min(100, max(0, new_reduction_rate))
        new_return_rate = min(100, max(0, new_return_rate))
        
        # Create comparison dataframes
        comparison_data = {
            "Metric": [
                "Monthly Sales (units)",
                "Return Rate (%)",
                "Monthly Returns (units)",
                "Implementation Cost ($)",
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
        
        # Add regulatory costs if applicable
        if 'regulatory_cost' in base_scenario and base_scenario['regulatory_cost'] > 0:
            comparison_data["Metric"].append("Regulatory Cost ($)")
            comparison_data["Original"].append(base_scenario['regulatory_cost'])
            comparison_data["New"].append(new_regulatory_cost)
            
        # Add adverse events if applicable
        if 'adverse_events' in base_scenario and base_scenario['adverse_events'] > 0:
            comparison_data["Metric"].append("Annual Adverse Events")
            comparison_data["Original"].append(base_scenario['adverse_events'])
            comparison_data["New"].append(new_adverse_events)
            
        comparison_df = pd.DataFrame(comparison_data)
        
        # Calculate financial impact for original scenario
        original_avoided_returns = base_scenario['returns_30'] * (base_scenario['reduction_rate'] / 100)
        original_monthly_savings = original_avoided_returns * (base_scenario['avg_sale_price'] - base_scenario['new_unit_cost'])
        original_monthly_cost = base_scenario['sales_30'] * base_scenario['additional_cost_per_item']
        original_monthly_net = original_monthly_savings - original_monthly_cost
        original_annual_net = original_monthly_net * 12
        
        total_investment = base_scenario['solution_cost']
        if 'regulatory_cost' in base_scenario:
            total_investment += base_scenario['regulatory_cost']
            
        if total_investment > 0 and original_annual_net > 0:
            original_roi = (original_annual_net / total_investment) * 100
            original_breakeven = total_investment / original_monthly_net
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
        
        new_total_investment = new_solution_cost + new_regulatory_cost
        
        if new_total_investment > 0 and new_annual_net > 0:
            new_roi = (new_annual_net / new_total_investment) * 100
            new_breakeven = new_total_investment / new_monthly_net
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
        
        # Add adverse events impact if applicable
        if 'adverse_events' in base_scenario and base_scenario['adverse_events'] > 0:
            original_avoided_adverse = base_scenario['adverse_events'] * (base_scenario['reduction_rate'] / 100)
            new_avoided_adverse = new_adverse_events * (new_reduction_rate / 100)
            
            financial_data["Metric"].append("Avoided Adverse Events")
            financial_data["Original"].append(original_avoided_adverse)
            financial_data["New"].append(new_avoided_adverse)
        
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
        
        # Add patient safety impact if applicable
        if 'adverse_events' in base_scenario and base_scenario['adverse_events'] > 0:
            st.markdown("##### Patient Safety Impact")
            st.metric(
                "Reduction in Adverse Events",
                f"{new_avoided_adverse:.1f}",
                f"{((new_avoided_adverse / original_avoided_adverse) - 1) * 100:.1f}%" if original_avoided_adverse > 0 else None,
                delta_color="normal"
            )
        
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
                
                if new_total_investment > 0 and annual > 0:
                    sens_roi = (annual / new_total_investment) * 100
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
        
        # Option to save as new scenario
        if st.button("Save as New Scenario"):
            # Create a new scenario name
            new_name = f"{base_scenario_name} (What-If)"
            
            # Determine device class and regulatory impact from base scenario
            device_class = base_scenario.get('device_class', 'Class II')
            regulatory_impact = base_scenario.get('regulatory_impact', 'No impact')
            
            success, message = optimizer.add_scenario(
                new_name, base_scenario['sku'], new_sales_30, new_avg_price,
                base_scenario['sales_channel'], new_returns_30, base_scenario['solution'],
                new_solution_cost, new_additional_cost, base_scenario['current_unit_cost'],
                new_reduction_rate, new_sales_30 * 12, new_returns_30 * 12, base_scenario['tag'],
                device_class, regulatory_impact, new_adverse_events, new_regulatory_cost
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
                file_name="meddevroi_scenarios.json",
                mime="application/json"
            )
            
            # Export as Excel
            excel_data = io.BytesIO()
            with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
                optimizer.scenarios.to_excel(writer, index=False, sheet_name='Scenarios')
                
                # Add risk matrix data if available
                if 'risk_matrix_data' in st.session_state and not st.session_state.risk_matrix_data.empty:
                    st.session_state.risk_matrix_data.to_excel(writer, index=False, sheet_name='Risk Matrix')
            
            st.download_button(
                "Export as Excel Spreadsheet",
                data=excel_data.getvalue(),
                file_name="meddevroi_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Export as CSV
            csv_data = optimizer.scenarios.to_csv(index=False).encode()
            st.download_button(
                "Export as CSV",
                data=csv_data,
                file_name="meddevroi_export.csv",
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
                # Also clear risk matrix data
                if 'risk_matrix_data' in st.session_state:
                    st.session_state.risk_matrix_data = pd.DataFrame(columns=[
                        'product_name', 'safety_score', 'compliance_score', 'logistics_score', 
                        'weighted_risk', 'risk_level', 'risk_color'])
                st.success("All data cleared!")
                st.experimental_rerun()
        
        # Theme settings
        st.markdown("#### Theme Preference")
        theme = st.selectbox("Color Theme", ["Medical Blue (Default)", "Clinical Green", "Regulatory Purple"])
        st.info("Theme customization will be available in a future update.")
        
        # Add regulatory documentation link
        st.markdown("#### Regulatory Resources")
        st.markdown("""
        <div class="regulatory-alert">
            <strong>FDA Resources:</strong><br>
            • <a href="https://www.fda.gov/medical-devices" target="_blank">FDA Medical Devices</a><br>
            • <a href="https://www.fda.gov/medical-devices/how-study-and-market-your-device/device-registration-and-listing" target="_blank">Device Registration & Listing</a><br>
            • <a href="https://www.fda.gov/medical-devices/premarket-submissions/premarket-notification-510k" target="_blank">510(k) Premarket Notification</a>
        </div>
        """, unsafe_allow_html=True)

# Initialize app
if 'optimizer' not in st.session_state:
    st.session_state.optimizer = ReturnOptimizer()
optimizer = st.session_state.optimizer

# Sidebar Navigation
with st.sidebar:
    st.image("https://via.placeholder.com/150x60?text=MedDevROI", width=150)
    st.markdown("## Navigation")
    
    # Navigation options
    nav_option = st.radio(
        "Go to:",
        ["Dashboard", "Add New Scenario", "Portfolio Analysis", "Risk Matrix", "What-If Analysis", "Settings"],
        index=0
    )
    
    st.markdown("---")
    
    # Help section
    with st.expander("📘 Help & Key Terms"):
        st.markdown("""
        ### Key Terms
        - **Return Rate**: Percentage of devices returned or complained about
        - **Reduction Rate**: Estimated reduction in returns after improvement
        - **Break-even**: Time to recover the implementation investment
        - **ROI**: Return on investment (net benefit / total investment)
        - **Net Benefit**: Annual savings minus additional costs
        
        ### Key Formulas
        - Return Rate = (Returns / Sales) × 100%
        - Avoided Returns = Returns × Reduction Rate
        - Net Benefit = Annual Savings - Annual Additional Costs
        - Annual Savings = Avoided Returns × Savings Per Item
        - ROI = (Net Benefit / Total Investment) × 100%
        - Break-even Time = Total Investment / Monthly Net Benefit
        """)
    
    with st.expander("🏥 Medical Device Classification"):
        st.markdown("""
        ### Device Classes
        - **Class I**: Low risk devices with general controls
          - Examples: bandages, examination gloves
        - **Class II**: Medium risk devices with special controls
          - Examples: infusion pumps, surgical needles
        - **Class III**: High risk devices requiring PMA
          - Examples: implantable pacemakers, heart valves
        
        ### Regulatory Pathways
        - **510(k)**: Premarket notification showing substantial equivalence
        - **De Novo**: For novel low/moderate risk devices
        - **PMA**: Premarket approval for high-risk devices
        - **HDE**: Humanitarian device exemption for rare conditions
        """)
    
    with st.expander("⚖️ Regulatory Impact Levels"):
        st.markdown("""
        ### Impact Levels
        - **No impact**: No regulatory filing required
          - Example: Minor labeling change not affecting IFU content
        - **Letter to File**: Documentation in design history file
          - Example: Minor material supplier change with same specs
        - **Special 510(k)**: Modified device notification
          - Example: Design change to improve usability
        - **New submission**: New 510(k) or PMA supplement
          - Example: New indication for use or major design change
        """)
    
    # Footer
    st.markdown("---")
    st.caption("MedDevROI v2.0 | Medical Device ROI & Risk Analysis Suite")
    st.caption("© 2025 MedDevROI Analytics")

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
    
    elif nav_option == "Risk Matrix":
        display_risk_matrix()
    
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
