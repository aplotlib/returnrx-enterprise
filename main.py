"""
KaizenROI - Product Upgrade ROI Analyzer
A specialized analytics tool for evaluating product improvement investments based on 
return rate reduction and enhanced sales performance.
"""

import streamlit as st
import pandas as pd
import numpy as np
import uuid
from datetime import datetime
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import io
import json
from io import BytesIO

# App configuration
st.set_page_config(
    page_title="KaizenROI | Product Upgrade ROI Analyzer",
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
    "text_light": "#ecf0f1",
    "subtle": "#bdc3c7",
    "highlight": "#e74c3c"
}

# Custom CSS
st.markdown("""
<style>
    /* Main styling */
    body, .stApp {
        background-color: #e6eff3;
        color: #2c3e50;
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
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
        transform: translateY(-1px);
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
    
    /* Metric display */
    .metric-container {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s;
    }
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 10px rgba(0,0,0,0.1);
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
    
    /* Logo */
    .logo-text {
        font-size: 24px;
        font-weight: 700;
        color: #23b2be;
        margin: 0;
        text-align: center;
    }
    .logo-icon {
        font-size: 32px;
        margin: 0;
        text-align: center;
        color: #004366;
    }
    .logo-container {
        text-align: center;
        padding: 10px;
        margin-bottom: 20px;
    }
    
    /* Product-centric styling */
    .product-card {
        background-color: white;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .product-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .product-stats {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
    }
    .stat-item {
        flex: 1 1 120px;
        text-align: center;
        padding: 8px 0;
    }
    .stat-value {
        font-weight: 600;
        font-size: 18px;
    }
    .stat-label {
        font-size: 12px;
        color: #7f8c8d;
    }
    
    /* Highlight elements */
    .highlight-box {
        background-color: rgba(231, 76, 60, 0.05);
        border-radius: 8px;
        padding: 16px;
        border: 1px solid rgba(231, 76, 60, 0.1);
    }
    
    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
    }
    .section-icon {
        margin-right: 8px;
        font-size: 24px;
        color: #23b2be;
    }
    .section-title {
        font-weight: 600;
        color: #004366;
        margin: 0;
    }
    
    /* Tooltip styling */
    .tooltip-icon {
        color: #bdc3c7;
        font-size: 14px;
        cursor: help;
        margin-left: 4px;
    }
    
    /* Update color-coded status */
    .status-positive {
        color: #1e8449;
        font-weight: 600;
    }
    .status-neutral {
        color: #f39c12;
        font-weight: 600;
    }
    .status-negative {
        color: #922b21;
        font-weight: 600;
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

def get_roi_status(roi):
    """Return status class based on ROI value"""
    if pd.isna(roi) or roi is None:
        return "status-neutral"
    elif roi > 150:
        return "status-positive"
    elif roi > 50:
        return "status-neutral"
    else:
        return "status-negative"

def calculate_roi_score(roi, breakeven_days, reduction_rate, sales_increase=0):
    """Calculate a weighted ROI score with multiple factors including sales increase"""
    if pd.isna(roi) or pd.isna(breakeven_days):
        return None
    
    # Lower breakeven days is better, normalize to 0-1 scale (max 365 days)
    breakeven_score = max(0, 1 - (breakeven_days / 365))
    
    # Higher ROI is better
    roi_score = min(1, roi / 5)  # Cap at 500% ROI
    
    # Higher reduction rate is better
    reduction_score = reduction_rate / 100
    
    # Sales increase impact (if provided)
    sales_score = min(1, sales_increase / 50)  # Cap at 50% sales increase
    
    # Weighted scoring with all factors
    if sales_increase > 0:
        weighted_score = (roi_score * 0.4) + (breakeven_score * 0.3) + (reduction_score * 0.15) + (sales_score * 0.15)
    else:
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

def calculate_npv(cash_flows, discount_rate=0.1, years=3):
    """Calculate Net Present Value of cash flows"""
    npv = 0
    for year in range(years):
        if year < len(cash_flows):
            npv += cash_flows[year] / ((1 + discount_rate) ** (year))
    return npv

def interpolate_adoption_curve(initial_rate, final_rate, curve_type="linear", periods=12):
    """Generate adoption curve for product upgrades over time"""
    if curve_type == "linear":
        return np.linspace(initial_rate, final_rate, periods)
    elif curve_type == "s_curve":
        # Create S-curve adoption pattern
        x = np.linspace(-3, 3, periods)
        curve = 1 / (1 + np.exp(-x))
        # Normalize to initial and final rates
        curve = initial_rate + (final_rate - initial_rate) * (curve - curve.min()) / (curve.max() - curve.min())
        return curve
    elif curve_type == "fast_initial":
        # Rapid initial adoption followed by slower growth
        x = np.linspace(0, 1, periods)
        curve = np.sqrt(x)
        # Normalize to initial and final rates
        curve = initial_rate + (final_rate - initial_rate) * curve
        return curve
    else:
        # Default to linear if unknown curve type
        return np.linspace(initial_rate, final_rate, periods)

# Data management
class ProductUpgradeAnalyzer:
    def __init__(self):
        self.load_data()
        self.default_examples = [
            {
                "scenario_name": "Premium Material Upgrade",
                "product_name": "Premium Apparel XS-450",
                "product_category": "Apparel",
                "current_unit_sales": 750,
                "avg_sale_price": 89.99,
                "sales_channel": "Direct to Consumer",
                "current_returns": 94,
                "upgrade_solution": "Premium fabric with improved durability",
                "development_cost": 5000,
                "unit_cost_change": 1.25,
                "current_unit_cost": 32.50,
                "estimated_return_reduction": 30,
                "sales_increase": 5,
                "product_lifecycle_stage": "Growth",
                "annual_unit_sales": 9125,
                "annual_returns": 1140,
                "return_processing_cost": 4.90,
                "time_to_implement": 1
            },
            {
                "scenario_name": "Size Verification Enhancement",
                "product_name": "Athletic Shoes 360",
                "product_category": "Footwear",
                "current_unit_sales": 420,
                "avg_sale_price": 129.99,
                "sales_channel": "Shopify",
                "current_returns": 71,
                "upgrade_solution": "Interactive size verification tool",
                "development_cost": 7500,
                "unit_cost_change": 0,
                "current_unit_cost": 45.75,
                "estimated_return_reduction": 35,
                "sales_increase": 8,
                "product_lifecycle_stage": "Maturity",
                "annual_unit_sales": 5100,
                "annual_returns": 860,
                "return_processing_cost": 8.25,
                "time_to_implement": 2
            },
            {
                "scenario_name": "Product Image Enhancement",
                "product_name": "HomeStyle Décor Collection",
                "product_category": "Home Goods",
                "current_unit_sales": 1250,
                "avg_sale_price": 49.99,
                "sales_channel": "Amazon",
                "current_returns": 138,
                "upgrade_solution": "360° product views and improved images",
                "development_cost": 3200,
                "unit_cost_change": 0,
                "current_unit_cost": 18.50,
                "estimated_return_reduction": 25,
                "sales_increase": 12,
                "product_lifecycle_stage": "Introduction",
                "annual_unit_sales": 15200,
                "annual_returns": 1675,
                "return_processing_cost": 3.50,
                "time_to_implement": 1
            }
        ]

    def load_data(self):
        """Load data from session state or initialize empty dataframe"""
        if 'scenarios' not in st.session_state:
            self.scenarios = pd.DataFrame(columns=[
                'uid', 'scenario_name', 'product_name', 'product_category', 
                'current_unit_sales', 'avg_sale_price', 'sales_channel', 
                'current_returns', 'return_rate', 'upgrade_solution', 
                'development_cost', 'unit_cost_change', 'current_unit_cost', 
                'estimated_return_reduction', 'sales_increase', 'product_lifecycle_stage',
                'return_cost_monthly', 'return_cost_annual', 'revenue_impact_monthly',
                'revenue_impact_annual', 'new_unit_cost', 'savings_monthly',
                'annual_savings', 'break_even_days', 'break_even_months',
                'roi', 'score', 'timestamp', 'annual_additional_costs', 'net_benefit',
                'margin_before', 'margin_after', 'margin_after_amortized',
                'annual_unit_sales', 'annual_returns', 'avoided_returns_monthly', 
                'avoided_returns_annual', 'monthly_net_benefit', 'tag', 
                'return_processing_cost', 'time_to_implement', 'sales_impact_monthly',
                'sales_impact_annual', 'npv', 'irr', 'payback_period'
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

    def add_scenario(self, scenario_name, product_name, product_category, current_unit_sales, 
                     avg_sale_price, sales_channel, current_returns, upgrade_solution, 
                     development_cost, unit_cost_change, current_unit_cost, 
                     estimated_return_reduction, sales_increase=0, product_lifecycle_stage="Growth",
                     annual_unit_sales=None, annual_returns=None, return_processing_cost=None, 
                     time_to_implement=1, tag=None):
        """Add a new product upgrade scenario with comprehensive calculations"""
        try:
            # Validate inputs
            if not product_name or not scenario_name:
                return False, "Product Name and Scenario Name are required"
            
            if current_unit_sales <= 0:
                return False, "Current unit sales must be greater than zero"
            
            if current_returns > current_unit_sales:
                return False, "Returns cannot exceed sales"
            
            if current_unit_cost <= 0 or avg_sale_price <= 0:
                return False, "Unit cost and sale price must be greater than zero"
            
            if avg_sale_price <= current_unit_cost:
                return False, "Sale price must be greater than unit cost"
            
            if time_to_implement <= 0:
                return False, "Time to implement must be greater than zero"
            
            # Default for return processing cost if not provided (handling, support, logistics)
            if return_processing_cost is None:
                # Default to 15% of unit cost as a reasonable estimate for return processing
                return_processing_cost = current_unit_cost * 0.15
            
            # Generate a unique ID
            uid = str(uuid.uuid4())[:8]
            
            # Calculate return rate
            return_rate = (current_returns / current_unit_sales) * 100 if current_unit_sales else 0
            
            # If annual data not provided, extrapolate from monthly
            if annual_unit_sales is None or annual_unit_sales <= 0:
                annual_unit_sales = current_unit_sales * 12
            
            if annual_returns is None or annual_returns <= 0:
                annual_returns = current_returns * 12
            
            # Calculate avoided returns based on reduction rate
            avoided_returns_monthly = current_returns * (estimated_return_reduction / 100)
            avoided_returns_annual = annual_returns * (estimated_return_reduction / 100)
            
            # Calculate the new unit cost (with additional costs)
            new_unit_cost = current_unit_cost + unit_cost_change
            
            # Calculate current costs of returns
            return_cost_monthly = current_returns * (current_unit_cost + return_processing_cost)
            return_cost_annual = annual_returns * (current_unit_cost + return_processing_cost)
            
            # Calculate revenue impact of returns
            revenue_impact_monthly = current_returns * avg_sale_price
            revenue_impact_annual = annual_returns * avg_sale_price
            
            # Calculate product margins
            margin_before = avg_sale_price - current_unit_cost
            margin_after = avg_sale_price - new_unit_cost
            
            # Calculate additional sales from sales increase percentage
            additional_sales_monthly = current_unit_sales * (sales_increase / 100)
            additional_sales_annual = annual_unit_sales * (sales_increase / 100)
            
            # Calculate revenue impact from additional sales
            sales_impact_monthly = additional_sales_monthly * margin_after
            sales_impact_annual = additional_sales_annual * margin_after
            
            # Calculate amortized development cost per unit
            # Only amortize over units actually sold and kept (not returned)
            net_units_kept_annually = (annual_unit_sales + additional_sales_annual) - (annual_returns - avoided_returns_annual)
            
            # Avoid division by zero
            if net_units_kept_annually > 0:
                amortized_solution_cost = development_cost / net_units_kept_annually
            else:
                amortized_solution_cost = 0
                
            margin_after_amortized = margin_after - amortized_solution_cost
            
            # Calculate savings and costs - CORRECTED FORMULA
            # Savings per avoided return includes:
            # 1. Recovered sale value (avg_sale_price)
            # 2. Avoided return processing cost
            # 3. Subtracted by the cost to make the item (already spent)
            savings_per_avoided_return = avg_sale_price + return_processing_cost - current_unit_cost
            
            # Monthly and annual savings from avoided returns
            savings_monthly = avoided_returns_monthly * savings_per_avoided_return
            annual_savings = avoided_returns_annual * savings_per_avoided_return
            
            # Additional costs only apply to units that aren't returned
            # This is more accurate than applying to all units
            annual_additional_costs = unit_cost_change * (annual_unit_sales - annual_returns + avoided_returns_annual)
            
            # Calculate net benefit (including sales increase impact)
            net_benefit = annual_savings - annual_additional_costs + sales_impact_annual
            monthly_net_benefit = net_benefit / 12
            
            # Calculate ROI metrics with better error handling
            roi = break_even_days = break_even_months = score = None
            
            # Only calculate ROI if there's a development cost
            if development_cost > 0:
                roi = (net_benefit / development_cost) * 100  # as percentage
                
                # Check for positive net benefit before calculating break-even
                if net_benefit > 0:
                    break_even_days = (development_cost / net_benefit) * 365
                    break_even_months = break_even_days / 30
                    score = calculate_roi_score(roi/100, break_even_days, estimated_return_reduction, sales_increase)
                else:
                    # Negative ROI case - solution doesn't pay for itself
                    roi = (net_benefit / development_cost) * 100  # Will be negative
                    # Leave break_even as None for negative net benefit
            
            # Calculate NPV and IRR
            cash_flows = [-development_cost]  # Initial investment as negative cash flow
            
            # Use adoption curves to model gradual implementation
            return_reduction_curve = interpolate_adoption_curve(0, estimated_return_reduction, 
                                                             "s_curve", 12)
            sales_increase_curve = interpolate_adoption_curve(0, sales_increase,
                                                           "fast_initial", 12)
            
            # Calculate monthly cash flows for 36 months (3 years)
            monthly_cash_flows = []
            
            for month in range(36):
                # Apply implementation delay
                if month < time_to_implement:
                    month_cf = 0
                else:
                    effective_month = month - time_to_implement
                    
                    # Apply adoption curves
                    if effective_month < 12:
                        month_reduction = return_reduction_curve[effective_month]
                        month_sales_increase = sales_increase_curve[effective_month]
                    else:
                        month_reduction = estimated_return_reduction
                        month_sales_increase = sales_increase
                    
                    # Calculate avoided returns for this month
                    month_avoided = current_returns * (month_reduction / 100)
                    month_return_savings = month_avoided * savings_per_avoided_return
                    
                    # Calculate additional sales for this month
                    month_add_sales = current_unit_sales * (month_sales_increase / 100)
                    month_sales_benefit = month_add_sales * margin_after
                    
                    # Calculate costs for this month (new units only)
                    month_additional_costs = unit_cost_change * (current_unit_sales - current_returns + month_avoided)
                    
                    # Calculate net benefit for this month
                    month_cf = month_return_savings - month_additional_costs + month_sales_benefit
                
                monthly_cash_flows.append(month_cf)
            
            # Group monthly cash flows into annual for NPV calculation
            annual_cash_flows = [sum(monthly_cash_flows[i:i+12]) for i in range(0, 36, 12)]
            
            # Add initial investment to the beginning
            annual_cash_flows = [-development_cost] + annual_cash_flows
            
            # Calculate NPV with 10% discount rate
            npv = calculate_npv(annual_cash_flows, 0.1, 4)
            
            # Calculate payback period including time to implement
            cum_cash_flow = -development_cost
            payback_period = None
            
            for i, cf in enumerate(monthly_cash_flows):
                cum_cash_flow += cf
                if cum_cash_flow >= 0 and payback_period is None:
                    payback_period = (i + 1 + time_to_implement) / 12  # Convert to years
                    break
            
            # Create new row
            new_row = {
                'uid': uid,
                'scenario_name': scenario_name,
                'product_name': product_name,
                'product_category': product_category,
                'current_unit_sales': current_unit_sales,
                'avg_sale_price': avg_sale_price,
                'sales_channel': sales_channel,
                'current_returns': current_returns,
                'return_rate': return_rate,
                'upgrade_solution': upgrade_solution,
                'development_cost': development_cost,
                'unit_cost_change': unit_cost_change,
                'current_unit_cost': current_unit_cost,
                'estimated_return_reduction': estimated_return_reduction,
                'sales_increase': sales_increase,
                'product_lifecycle_stage': product_lifecycle_stage,
                'return_cost_monthly': return_cost_monthly,
                'return_cost_annual': return_cost_annual,
                'revenue_impact_monthly': revenue_impact_monthly,
                'revenue_impact_annual': revenue_impact_annual,
                'new_unit_cost': new_unit_cost,
                'savings_monthly': savings_monthly,
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
                'annual_unit_sales': annual_unit_sales,
                'annual_returns': annual_returns,
                'avoided_returns_monthly': avoided_returns_monthly,
                'avoided_returns_annual': avoided_returns_annual,
                'monthly_net_benefit': monthly_net_benefit,
                'tag': tag or product_category,
                'return_processing_cost': return_processing_cost,
                'time_to_implement': time_to_implement,
                'sales_impact_monthly': sales_impact_monthly,
                'sales_impact_annual': sales_impact_annual,
                'npv': npv,
                'irr': None,  # Placeholder for future implementation
                'payback_period': payback_period
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
            current['scenario_name'], current['product_name'], current['product_category'],
            current['current_unit_sales'], current['avg_sale_price'], current['sales_channel'],
            current['current_returns'], current['upgrade_solution'], current['development_cost'],
            current['unit_cost_change'], current['current_unit_cost'], current['estimated_return_reduction'],
            current['sales_increase'], current['product_lifecycle_stage'], current['annual_unit_sales'],
            current['annual_returns'], current['return_processing_cost'], current['time_to_implement'],
            current['tag']
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
            new_name, scenario['product_name'], scenario['product_category'],
            scenario['current_unit_sales'], scenario['avg_sale_price'], scenario['sales_channel'],
            scenario['current_returns'], scenario['upgrade_solution'], scenario['development_cost'],
            scenario['unit_cost_change'], scenario['current_unit_cost'], scenario['estimated_return_reduction'],
            scenario['sales_increase'], scenario['product_lifecycle_stage'], scenario['annual_unit_sales'],
            scenario['annual_returns'], scenario['return_processing_cost'], scenario['time_to_implement'],
            scenario['tag']
        )
        
        return success, message

    def compare_scenarios(self, scenario_ids):
        """Compare multiple scenarios side by side"""
        if not scenario_ids or len(scenario_ids) < 2:
            return None
        
        scenarios = [self.get_scenario(uid) for uid in scenario_ids if uid in self.scenarios['uid'].values]
        if not scenarios or len(scenarios) < 2:
            return None
        
        # Create comparison dataframe
        comparison = pd.DataFrame({
            'Metric': [
                'Product',
                'Category',
                'Upgrade Solution',
                'Development Cost',
                'Unit Cost Change',
                'Return Reduction',
                'Sales Increase',
                'Time to Implement',
                'ROI',
                'Break-even (months)',
                'Net Benefit (annual)',
                'NPV',
                'Payback Period (years)'
            ]
        })
        
        # Add each scenario as a column
        for scenario in scenarios:
            comparison[scenario['scenario_name']] = [
                scenario['product_name'],
                scenario['product_category'],
                scenario['upgrade_solution'],
                f"${scenario['development_cost']:,.2f}",
                f"${scenario['unit_cost_change']:,.2f}",
                f"{scenario['estimated_return_reduction']:.1f}%",
                f"{scenario['sales_increase']:.1f}%",
                f"{scenario['time_to_implement']} {('month' if scenario['time_to_implement'] == 1 else 'months')}",
                f"{scenario['roi']:.1f}%" if pd.notna(scenario['roi']) else "N/A",
                f"{scenario['break_even_months']:.1f}" if pd.notna(scenario['break_even_months']) else "N/A",
                f"${scenario['net_benefit']:,.2f}",
                f"${scenario['npv']:,.2f}" if pd.notna(scenario['npv']) else "N/A",
                f"{scenario['payback_period']:.2f}" if pd.notna(scenario['payback_period']) else "N/A"
            ]
        
        return comparison

# Initialize app
if 'optimizer' not in st.session_state:
    st.session_state.optimizer = ProductUpgradeAnalyzer()
optimizer = st.session_state.optimizer

# App functions
def display_header():
    """Display app header with logo and navigation"""
    col1, col2 = st.columns([1, 5])
    
    # Text-based logo instead of image
    with col1:
        st.markdown("""
        <div class="logo-container">
            <p class="logo-icon">🔄</p>
            <p class="logo-text">KaizenROI</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Title and description
    with col2:
        st.title("Product Upgrade ROI Analyzer")
        st.caption("Evaluate product improvements based on return reduction and sales growth potential.")

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
    total_investment = df['development_cost'].sum()
    portfolio_roi = (total_net_benefit / total_investment * 100) if total_investment > 0 else 0
    avg_sales_increase = df['sales_increase'].mean()
    
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
            <p class="metric-label">Avg. Sales Increase</p>
            <p class="metric-value" style="color: {get_color_scale(avg_sales_increase, 0, 20)};">{format_percent(avg_sales_increase)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional metrics
    st.markdown("### Key Performance Indicators")
    
    # Get top categories
    if 'product_category' in df.columns and not df['product_category'].isna().all():
        category_data = df.groupby('product_category').agg({
            'net_benefit': 'sum',
            'roi': 'mean',
            'sales_increase': 'mean',
            'estimated_return_reduction': 'mean',
            'development_cost': 'sum'
        }).reset_index()
        
        # Find top category by net benefit
        top_category = category_data.loc[category_data['net_benefit'].idxmax()]['product_category']
        top_category_roi = category_data.loc[category_data['net_benefit'].idxmax()]['roi']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <p class="metric-label">Best Performing Category</p>
                <p class="metric-value" style="color: {COLOR_SCHEME['primary']};">{top_category}</p>
                <p class="metric-label">ROI: {format_percent(top_category_roi)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Find quickest payback scenario
            if 'payback_period' in df.columns:
                payback_df = df[df['payback_period'].notna()]
                if not payback_df.empty:
                    quickest_payback = payback_df.loc[payback_df['payback_period'].idxmin()]
                    st.markdown(f"""
                    <div class="metric-container">
                        <p class="metric-label">Quickest Payback Upgrade</p>
                        <p class="metric-value" style="color: {COLOR_SCHEME['secondary']};">{quickest_payback['scenario_name']}</p>
                        <p class="metric-label">{format_number(quickest_payback['payback_period'])} years</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="metric-container">
                        <p class="metric-label">Quickest Payback Upgrade</p>
                        <p class="metric-value">No data</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col3:
            # Find highest NPV scenario
            if 'npv' in df.columns:
                npv_df = df[df['npv'].notna()]
                if not npv_df.empty:
                    highest_npv = npv_df.loc[npv_df['npv'].idxmax()]
                    st.markdown(f"""
                    <div class="metric-container">
                        <p class="metric-label">Highest NPV Upgrade</p>
                        <p class="metric-value" style="color: {COLOR_SCHEME['positive']};">{highest_npv['scenario_name']}</p>
                        <p class="metric-label">NPV: {format_currency(highest_npv['npv'])}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="metric-container">
                        <p class="metric-label">Highest NPV Upgrade</p>
                        <p class="metric-value">No data</p>
                    </div>
                    """, unsafe_allow_html=True)

def create_scenario_form():
    """Create form for adding a new upgrade scenario"""
    with st.form(key="scenario_form"):
        st.subheader("Add New Product Upgrade Scenario")
        
        # Use tabs for better organization
        tabs = st.tabs(["Product Details", "Upgrade Information", "Financial Projections"])
        
        with tabs[0]:  # Product Details
            col1, col2 = st.columns(2)
            with col1:
                scenario_name = st.text_input("Scenario Name", 
                                            help="A memorable name for this upgrade scenario")
                
                product_name = st.text_input("Product Name", 
                                           help="The name of the product being upgraded")
                
                product_category = st.selectbox("Product Category", 
                                              ["Apparel", "Footwear", "Electronics", "Home Goods", "Accessories", 
                                               "Beauty", "Toys", "Sporting Goods", "Furniture", "Other"],
                                              help="The category this product belongs to")
                
                sales_channel = st.selectbox("Primary Sales Channel", 
                                           ["Direct to Consumer", "Amazon", "Shopify", "Retail Partners", 
                                            "Marketplace", "Wholesale", "Other"],
                                           help="Main platform where product is sold")
                
                product_lifecycle_stage = st.selectbox("Product Lifecycle Stage",
                                                    ["Introduction", "Growth", "Maturity", "Decline"],
                                                    help="Current stage in the product lifecycle")
            
            with col2:
                current_unit_sales = st.number_input("Monthly Unit Sales", 
                                                   min_value=0, 
                                                   help="Current monthly sales volume")
                
                current_returns = st.number_input("Monthly Returns", 
                                                min_value=0, 
                                                help="Current monthly return volume")
                
                avg_sale_price = st.number_input("Average Sale Price ($)", 
                                               min_value=0.0, 
                                               format="%.2f", 
                                               help="Average selling price per unit")
                
                current_unit_cost = st.number_input("Current Unit Cost ($)", 
                                                  min_value=0.0, 
                                                  format="%.2f", 
                                                  help="Cost to produce/acquire each unit")
                
                return_processing_cost = st.number_input("Return Processing Cost ($)", 
                                                      min_value=0.0, 
                                                      format="%.2f", 
                                                      value=round(current_unit_cost * 0.15, 2) if current_unit_cost > 0 else 0.0,
                                                      help="Cost to process each return including customer service, shipping, and restocking")
                
                # Optional annual data
                annual_data = st.checkbox("Use custom annual data", 
                                        help="By default, monthly data is multiplied by 12")
                
                if annual_data:
                    annual_unit_sales = st.number_input("Annual Unit Sales", 
                                                      min_value=0, 
                                                      help="Total units sold in a year")
                    annual_returns = st.number_input("Annual Returns", 
                                                   min_value=0, 
                                                   help="Total units returned in a year")
                else:
                    annual_unit_sales = current_unit_sales * 12
                    annual_returns = current_returns * 12
        
        with tabs[1]:  # Upgrade Information
            col1, col2 = st.columns(2)
            with col1:
                upgrade_solution = st.text_area("Proposed Upgrade", 
                                              height=100,
                                              help="Detailed description of the product improvement")
                
                development_cost = st.number_input("Development Cost ($)", 
                                                 min_value=0.0, 
                                                 format="%.2f", 
                                                 help="One-time investment required to implement the upgrade")
                
                unit_cost_change = st.number_input("Unit Cost Change ($)", 
                                                 format="%.2f", 
                                                 help="Change in cost per unit after upgrade (can be negative for cost reductions)")
            
            with col2:
                estimated_return_reduction = st.slider("Estimated Return Reduction (%)", 
                                                    0, 100, 20, 
                                                    help="Expected percentage reduction in returns after implementing the upgrade")
                
                sales_increase = st.slider("Estimated Sales Increase (%)", 
                                         0, 50, 5, 
                                         help="Expected percentage increase in sales volume due to the upgrade")
                
                time_to_implement = st.number_input("Implementation Time (months)", 
                                                  min_value=1, 
                                                  max_value=24, 
                                                  value=1, 
                                                  help="Time required to fully implement the upgrade")
        
        with tabs[2]:  # Financial Projections
            # Calculate and preview stats
            if current_unit_sales > 0 and current_returns > 0 and current_unit_cost > 0:
                return_rate = (current_returns / current_unit_sales) * 100
                avoided_returns = current_returns * (estimated_return_reduction / 100)
                additional_sales = current_unit_sales * (sales_increase / 100)
                
                st.markdown("### Preview Calculations")
                
                # Show financial impact
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Return Impact")
                    st.metric("Current Return Rate", f"{return_rate:.2f}%")
                    st.metric("Monthly Returns Value", f"${current_returns * avg_sale_price:,.2f}")
                    st.metric("Avoided Returns (Monthly)", f"{avoided_returns:.1f} units")
                    st.metric("New Return Rate", f"{return_rate * (1 - estimated_return_reduction/100):.2f}%")
                
                with col2:
                    st.markdown("#### Sales & Profit Impact")
                    # Calculate new costs
                    new_unit_cost = current_unit_cost + unit_cost_change
                    
                    # Calculate savings per avoided return (with proper formula)
                    savings_per_avoided_return = avg_sale_price + return_processing_cost - current_unit_cost
                    
                    # Calculate avoided returns benefit
                    monthly_return_savings = avoided_returns * savings_per_avoided_return
                    
                    # Calculate additional sales benefit
                    monthly_sales_benefit = additional_sales * (avg_sale_price - new_unit_cost)
                    
                    # Calculate additional costs
                    monthly_additional_costs = unit_cost_change * (current_unit_sales - current_returns + avoided_returns + additional_sales)
                    
                    # Calculate net benefit
                    monthly_net = monthly_return_savings + monthly_sales_benefit - monthly_additional_costs
                    annual_net = monthly_net * 12
                    
                    # Calculate simple payback and ROI
                    if development_cost > 0 and monthly_net > 0:
                        payback_months = development_cost / monthly_net
                        roi_percent = (annual_net / development_cost) * 100
                        
                        st.metric("Additional Monthly Sales", f"{additional_sales:.1f} units")
                        st.metric("Monthly Net Benefit", f"${monthly_net:.2f}")
                        st.metric("Simple Payback", f"{payback_months:.1f} months")
                        st.metric("Simple ROI", f"{roi_percent:.1f}%")
                    else:
                        st.metric("Additional Monthly Sales", f"{additional_sales:.1f} units")
                        st.metric("Monthly Net Benefit", f"${monthly_net:.2f}")
                        st.metric("Simple Payback", "N/A")
                        st.metric("Simple ROI", "N/A")
                    
                # Show breakout of benefits
                st.markdown("#### Benefit Breakdown")
                benefit_data = {
                    'Category': ['Return Reduction', 'Sales Increase', 'Additional Costs', 'Net Benefit'],
                    'Monthly Impact': [monthly_return_savings, monthly_sales_benefit, -monthly_additional_costs, monthly_net],
                    'Annual Impact': [monthly_return_savings*12, monthly_sales_benefit*12, -monthly_additional_costs*12, annual_net]
                }
                benefit_df = pd.DataFrame(benefit_data)
                
                # Format for display
                benefit_df['Monthly Impact'] = benefit_df['Monthly Impact'].apply(lambda x: f"${x:,.2f}")
                benefit_df['Annual Impact'] = benefit_df['Annual Impact'].apply(lambda x: f"${x:,.2f}")
                
                st.dataframe(benefit_df, hide_index=True)
        
        # Submit button
        submitted = st.form_submit_button("Save Scenario")
        
        if submitted:
            success, message = optimizer.add_scenario(
                scenario_name, product_name, product_category,
                current_unit_sales, avg_sale_price, sales_channel,
                current_returns, upgrade_solution, development_cost,
                unit_cost_change, current_unit_cost, estimated_return_reduction,
                sales_increase, product_lifecycle_stage, annual_unit_sales,
                annual_returns, return_processing_cost, time_to_implement
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
    st.subheader("Upgrade Scenario Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        product_filter = st.multiselect("Filter by Product", 
                                       options=sorted(df['product_name'].unique()),
                                       default=[])
    
    with col2:
        category_filter = st.multiselect("Filter by Category", 
                                       options=sorted(df['product_category'].unique()),
                                       default=[])
    
    with col3:
        lifecycle_filter = st.multiselect("Filter by Lifecycle Stage", 
                                        options=sorted(df['product_lifecycle_stage'].unique()),
                                        default=[])
    
    # Apply filters
    filtered_df = df.copy()
    
    if product_filter:
        filtered_df = filtered_df[filtered_df['product_name'].isin(product_filter)]
    
    if category_filter:
        filtered_df = filtered_df[filtered_df['product_category'].isin(category_filter)]
    
    if lifecycle_filter:
        filtered_df = filtered_df[filtered_df['product_lifecycle_stage'].isin(lifecycle_filter)]
    
    # Display table
    if filtered_df.empty:
        st.warning("No scenarios match your filters. Try adjusting your criteria.")
        return
    
    # Prepare display columns
    display_df = filtered_df[[
        'uid', 'scenario_name', 'product_name', 'product_category', 'product_lifecycle_stage',
        'development_cost', 'estimated_return_reduction', 'sales_increase', 'roi', 
        'break_even_months', 'net_benefit', 'npv'
    ]].copy()
    
    # Format columns for display
    display_df['development_cost'] = display_df['development_cost'].apply(lambda x: f"${x:,.2f}")
    display_df['estimated_return_reduction'] = display_df['estimated_return_reduction'].apply(lambda x: f"{x:.0f}%")
    display_df['sales_increase'] = display_df['sales_increase'].apply(lambda x: f"{x:.0f}%")
    
    # Format ROI with color coding
    def format_roi(roi):
        if pd.isna(roi):
            return "N/A"
        
        status_class = get_roi_status(roi)
        return f"<span class='{status_class}'>{roi:.1f}%</span>"
    
    display_df['roi'] = filtered_df['roi'].apply(format_roi)
    
    display_df['break_even_months'] = display_df['break_even_months'].apply(
        lambda x: f"{x:.1f}" if not pd.isna(x) else "N/A")
    
    display_df['net_benefit'] = display_df['net_benefit'].apply(lambda x: f"${x:,.2f}")
    display_df['npv'] = display_df['npv'].apply(lambda x: f"${x:,.2f}" if not pd.isna(x) else "N/A")
    
    # Rename columns for display
    display_df = display_df.rename(columns={
        'scenario_name': 'Scenario',
        'product_name': 'Product',
        'product_category': 'Category',
        'product_lifecycle_stage': 'Lifecycle Stage',
        'development_cost': 'Dev. Cost',
        'estimated_return_reduction': 'Return Reduction',
        'sales_increase': 'Sales Increase',
        'roi': 'ROI',
        'break_even_months': 'Break-even',
        'net_benefit': 'Annual Benefit',
        'npv': 'NPV'
    })
    
    # Hide UID column
    display_df = display_df.drop('uid', axis=1)
    
    # Display interactive table
    st.dataframe(display_df.reset_index(drop=True), use_container_width=True, 
               column_config={
                   "ROI": st.column_config.Column(
                       "ROI",
                       help="Return on Investment - Annual Benefit / Development Cost",
                       width="medium"
                   )
               },
               hide_index=True)
    
    # Action buttons for selected scenario
    st.markdown("### Scenario Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        selected_scenario = st.selectbox("Select scenario:", 
                                     filtered_df['scenario_name'].tolist(),
                                     help="Choose a scenario to view or modify")
    
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
            confirm = st.checkbox("Confirm deletion")
            if confirm and optimizer.delete_scenario(selected_uid):
                st.success(f"Scenario '{selected_scenario}' deleted successfully.")
            elif confirm:
                st.error("Failed to delete scenario.")
    
    # Comparison tool
    if len(filtered_df) >= 2:
        st.markdown("### Compare Scenarios")
        scenarios_to_compare = st.multiselect(
            "Select scenarios to compare:",
            options=filtered_df['scenario_name'].tolist(),
            default=[],
            max_selections=4,
            help="Choose 2-4 scenarios to compare side by side"
        )
        
        if len(scenarios_to_compare) >= 2:
            # Get UIDs for selected scenarios
            scenario_uids = filtered_df[filtered_df['scenario_name'].isin(scenarios_to_compare)]['uid'].tolist()
            
            # Get comparison data
            comparison = optimizer.compare_scenarios(scenario_uids)
            
            if comparison is not None:
                st.dataframe(comparison, use_container_width=True, hide_index=True)
                
                # Create visual comparison
                st.markdown("#### Visual Comparison")
                
                # Get data for charts
                chart_data = []
                for i, scenario_name in enumerate(scenarios_to_compare):
                    scenario = filtered_df[filtered_df['scenario_name'] == scenario_name].iloc[0]
                    chart_data.append({
                        'Scenario': scenario_name,
                        'ROI (%)': scenario['roi'] if not pd.isna(scenario['roi']) else 0,
                        'Return Reduction (%)': scenario['estimated_return_reduction'],
                        'Sales Increase (%)': scenario['sales_increase'],
                        'Break-even (months)': scenario['break_even_months'] if not pd.isna(scenario['break_even_months']) else 36,
                        'Net Benefit ($)': scenario['net_benefit'],
                        'NPV ($)': scenario['npv'] if not pd.isna(scenario['npv']) else 0
                    })
                
                chart_df = pd.DataFrame(chart_data)
                
                # Create radar chart for multi-factor comparison
                categories = ['ROI (%)', 'Return Reduction (%)', 'Sales Increase (%)', 'Break-even (months)']
                
                # Add traces for each scenario
                fig = go.Figure()
                
                # Normalize values for radar chart
                max_roi = max(chart_df['ROI (%)'].max(), 200)  # Cap at 200% for visualization
                max_reduction = 100
                max_increase = max(chart_df['Sales Increase (%)'].max(), 50)  # Cap at 50% for visualization
                max_breakeven = 36  # Cap at 36 months
                
                for _, row in chart_df.iterrows():
                    # Normalize and reverse break-even (lower is better)
                    breakeven_normalized = 1 - min(row['Break-even (months)'] / max_breakeven, 1)
                    
                    fig.add_trace(go.Scatterpolar(
                        r=[
                            min(row['ROI (%)'] / max_roi, 1),
                            row['Return Reduction (%)'] / max_reduction,
                            row['Sales Increase (%)'] / max_increase,
                            breakeven_normalized
                        ],
                        theta=categories,
                        fill='toself',
                        name=row['Scenario']
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )
                    ),
                    height=500,
                    title="Scenario Comparison by Key Metrics"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Bar chart comparing financial metrics
                fig_bar = go.Figure()
                
                # Add ROI bars
                fig_bar.add_trace(go.Bar(
                    x=chart_df['Scenario'],
                    y=chart_df['ROI (%)'],
                    name='ROI (%)',
                    marker_color=COLOR_SCHEME['positive']
                ))
                
                # Add Net Benefit bars
                fig_bar.add_trace(go.Bar(
                    x=chart_df['Scenario'],
                    y=chart_df['Net Benefit ($)'],
                    name='Annual Net Benefit ($)',
                    marker_color=COLOR_SCHEME['neutral'],
                    yaxis='y2'
                ))
                
                # Configure axes
                fig_bar.update_layout(
                    yaxis=dict(
                        title='ROI (%)',
                        side='left',
                        titlefont=dict(color=COLOR_SCHEME['positive']),
                        tickfont=dict(color=COLOR_SCHEME['positive'])
                    ),
                    yaxis2=dict(
                        title='Net Benefit ($)',
                        side='right',
                        overlaying='y',
                        titlefont=dict(color=COLOR_SCHEME['neutral']),
                        tickfont=dict(color=COLOR_SCHEME['neutral'])
                    ),
                    title="Financial Impact Comparison",
                    barmode='group',
                    height=500
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)

def display_scenario_details(uid):
    """Display detailed view of a scenario"""
    scenario = optimizer.get_scenario(uid)
    if not scenario:
        st.error("Scenario not found")
        return
    
    st.markdown(f"""
    <div class="section-header">
        <span class="section-icon">📊</span>
        <h2 class="section-title">Upgrade Analysis: {scenario['scenario_name']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Product details card
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">📦</span>
        <h3 class="section-title">Product Information</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="product-card">
            <div class="product-header">
                <strong>Product Details</strong>
            </div>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">{scenario['product_name']}</div>
                    <div class="stat-label">Product Name</div>
                </div>
            </div>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">{scenario['product_category']}</div>
                    <div class="stat-label">Category</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{scenario['product_lifecycle_stage']}</div>
                    <div class="stat-label">Lifecycle Stage</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="product-card">
            <div class="product-header">
                <strong>Sales Metrics</strong>
            </div>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">{scenario['current_unit_sales']:,}</div>
                    <div class="stat-label">Monthly Units</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${scenario['avg_sale_price']:.2f}</div>
                    <div class="stat-label">Average Price</div>
                </div>
            </div>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">{scenario['current_returns']:,}</div>
                    <div class="stat-label">Monthly Returns</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{scenario['return_rate']:.1f}%</div>
                    <div class="stat-label">Return Rate</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="product-card">
            <div class="product-header">
                <strong>Cost Structure</strong>
            </div>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">${scenario['current_unit_cost']:.2f}</div>
                    <div class="stat-label">Unit Cost</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${scenario['margin_before']:.2f}</div>
                    <div class="stat-label">Current Margin</div>
                </div>
            </div>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">${scenario['return_processing_cost']:.2f}</div>
                    <div class="stat-label">Return Process Cost</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{(scenario['margin_before']/scenario['avg_sale_price']*100):.1f}%</div>
                    <div class="stat-label">Margin %</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Upgrade details
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🔄</span>
        <h3 class="section-title">Upgrade Details</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="product-card">
            <div class="product-header">
                <strong>Upgrade Solution</strong>
            </div>
            <p>{scenario['upgrade_solution']}</p>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">${scenario['development_cost']:,.2f}</div>
                    <div class="stat-label">Development Cost</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{scenario['time_to_implement']} {('month' if scenario['time_to_implement'] == 1 else 'months')}</div>
                    <div class="stat-label">Implementation Time</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="product-card">
            <div class="product-header">
                <strong>Expected Impact</strong>
            </div>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">${scenario['unit_cost_change']:.2f}</div>
                    <div class="stat-label">Unit Cost Change</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{scenario['estimated_return_reduction']:.1f}%</div>
                    <div class="stat-label">Return Reduction</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{scenario['sales_increase']:.1f}%</div>
                    <div class="stat-label">Sales Increase</div>
                </div>
            </div>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">{scenario['avoided_returns_monthly']:.1f}</div>
                    <div class="stat-label">Monthly Avoided Returns</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{scenario['return_rate'] * (1 - scenario['estimated_return_reduction']/100):.1f}%</div>
                    <div class="stat-label">New Return Rate</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{scenario['current_unit_sales'] * (scenario['sales_increase']/100):.1f}</div>
                    <div class="stat-label">Additional Monthly Sales</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Financial impacts
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">💰</span>
        <h3 class="section-title">Financial Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        roi_status = get_roi_status(scenario['roi'])
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Return on Investment</p>
            <p class="metric-value {roi_status}">{scenario['roi']:.1f}% </p>
            <p class="metric-label">Annual Net Benefit / Development Cost</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # NPV with status color
        npv_status = "status-positive" if scenario['npv'] > scenario['development_cost'] else "status-negative"
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Net Present Value (NPV)</p>
            <p class="metric-value {npv_status}">${scenario['npv']:,.2f}</p>
            <p class="metric-label">Future cash flows at 10% discount rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Break-even with status color
        if pd.notna(scenario['break_even_months']):
            be_status = "status-positive" if scenario['break_even_months'] < 12 else (
                "status-neutral" if scenario['break_even_months'] < 24 else "status-negative")
            be_value = f"{scenario['break_even_months']:.1f} months"
        else:
            be_status = "status-negative"
            be_value = "N/A"
            
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Break-even Time</p>
            <p class="metric-value {be_status}">{be_value}</p>
            <p class="metric-label">Development Cost / Monthly Net Benefit</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Payback period with status color
        if pd.notna(scenario['payback_period']):
            pp_status = "status-positive" if scenario['payback_period'] < 1 else (
                "status-neutral" if scenario['payback_period'] < 2 else "status-negative")
            pp_value = f"{scenario['payback_period']:.2f} years"
        else:
            pp_status = "status-negative"
            pp_value = "N/A"
            
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Payback Period</p>
            <p class="metric-value {pp_status}">{pp_value}</p>
            <p class="metric-label">Includes implementation time</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Financial breakdown charts
    st.markdown("### Financial Impact")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create data for benefit sources
        benefit_data = {
            "Source": ["Return Reduction", "Sales Increase", "Additional Costs", "Net Benefit"],
            "Annual Amount": [
                scenario['annual_savings'],
                scenario['sales_impact_annual'], 
                -scenario['annual_additional_costs'],
                scenario['net_benefit']
            ]
        }
        benefit_df = pd.DataFrame(benefit_data)
        
        # Create waterfall chart
        fig_benefit = go.Figure(go.Waterfall(
            name="Annual Financial Impact",
            orientation="v",
            measure=["relative", "relative", "relative", "total"],
            x=benefit_df["Source"],
            y=benefit_df["Annual Amount"],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": COLOR_SCHEME["negative"]}},
            increasing={"marker": {"color": COLOR_SCHEME["positive"]}},
            totals={"marker": {"color": COLOR_SCHEME["primary"]}}
        ))
        
        fig_benefit.update_layout(
            title="Annual Financial Impact Breakdown",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_benefit, use_container_width=True)
    
    with col2:
        # Create data for margin analysis
        margin_data = {
            "State": ["Before", "After"],
            "Unit Sales": [
                scenario['current_unit_sales'] * 12,
                scenario['current_unit_sales'] * 12 * (1 + scenario['sales_increase']/100)
            ],
            "Return Rate": [
                scenario['return_rate'],
                scenario['return_rate'] * (1 - scenario['estimated_return_reduction']/100)
            ],
            "Unit Margin": [
                scenario['margin_before'],
                scenario['margin_after']
            ]
        }
        margin_df = pd.DataFrame(margin_data)
        
        # Create grouped bar chart
        fig_margin = go.Figure()
        
        # Add unit sales bars
        fig_margin.add_trace(go.Bar(
            x=margin_df["State"],
            y=margin_df["Unit Sales"],
            name="Annual Unit Sales",
            marker_color=COLOR_SCHEME["neutral"],
            yaxis="y"
        ))
        
        # Add return rate line
        fig_margin.add_trace(go.Scatter(
            x=margin_df["State"],
            y=margin_df["Return Rate"],
            name="Return Rate (%)",
            mode="lines+markers",
            marker=dict(size=10),
            line=dict(width=3, color=COLOR_SCHEME["negative"]),
            yaxis="y2"
        ))
        
        # Add unit margin line
        fig_margin.add_trace(go.Scatter(
            x=margin_df["State"],
            y=margin_df["Unit Margin"],
            name="Unit Margin ($)",
            mode="lines+markers",
            marker=dict(size=10),
            line=dict(width=3, color=COLOR_SCHEME["positive"]),
            yaxis="y3"
        ))
        
        # Configure axes
        fig_margin.update_layout(
            yaxis=dict(
                title="Annual Unit Sales",
                side="left",
                showgrid=False
            ),
            yaxis2=dict(
                title="Return Rate (%)",
                side="right",
                overlaying="y",
                range=[0, max(margin_df["Return Rate"]) * 1.5],
                showgrid=False
            ),
            yaxis3=dict(
                title="Unit Margin ($)",
                side="right",
                overlaying="y",
                anchor="free",
                position=0.95,
                range=[0, max(margin_df["Unit Margin"]) * 1.5],
                showgrid=False
            ),
            title="Product Performance Before vs After",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            height=400
        )
        
        st.plotly_chart(fig_margin, use_container_width=True)
    
    # Cash flow analysis
    st.markdown("### Investment Analysis Over Time")
    
    # Create cash flow projection
    months = list(range(37))  # 0-36 months (3 years)
    impl_time = scenario['time_to_implement']
    
    # Model gradual adoption of benefits
    return_reduction_curve = list(interpolate_adoption_curve(0, scenario['estimated_return_reduction'], "s_curve", 12))
    sales_increase_curve = list(interpolate_adoption_curve(0, scenario['sales_increase'], "fast_initial", 12))
    
    # Calculate monthly cash flows
    monthly_cash_flows = [-scenario['development_cost']]  # Initial investment
    cumulative_cash_flow = [-scenario['development_cost']]
    
    # For each future month
    for month in range(1, 37):
        # Apply implementation delay
        if month <= impl_time:
            month_cf = 0
        else:
            effective_month = month - impl_time - 1
            
            # Apply adoption curves
            if effective_month < 12:
                month_reduction = return_reduction_curve[effective_month]
                month_sales_increase = sales_increase_curve[effective_month]
            else:
                month_reduction = scenario['estimated_return_reduction']
                month_sales_increase = scenario['sales_increase']
            
            # Calculate avoided returns for this month
            month_avoided = scenario['current_returns'] * (month_reduction / 100)
            savings_per_return = scenario['avg_sale_price'] + scenario['return_processing_cost'] - scenario['current_unit_cost']
            month_return_savings = month_avoided * savings_per_return
            
            # Calculate additional sales for this month
            month_add_sales = scenario['current_unit_sales'] * (month_sales_increase / 100)
            margin_after = scenario['avg_sale_price'] - (scenario['current_unit_cost'] + scenario['unit_cost_change'])
            month_sales_benefit = month_add_sales * margin_after
            
            # Calculate costs for this month
            month_additional_costs = scenario['unit_cost_change'] * (
                scenario['current_unit_sales'] - scenario['current_returns'] + month_avoided + month_add_sales
            )
            
            # Calculate net benefit for this month
            month_cf = month_return_savings - month_additional_costs + month_sales_benefit
        
        monthly_cash_flows.append(month_cf)
        cumulative_cash_flow.append(cumulative_cash_flow[-1] + month_cf)
    
    # Create cash flow chart
    cash_flow_data = {
        "Month": months,
        "Monthly Cash Flow": monthly_cash_flows,
        "Cumulative Cash Flow": cumulative_cash_flow
    }
    cf_df = pd.DataFrame(cash_flow_data)
    
    # Find break-even point
    breakeven_month = None
    for i, cf in enumerate(cumulative_cash_flow):
        if cf >= 0 and breakeven_month is None:
            breakeven_month = i
            break
    
    fig_cash_flow = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add monthly cash flow bars
    fig_cash_flow.add_trace(
        go.Bar(
            x=cf_df["Month"],
            y=cf_df["Monthly Cash Flow"],
            name="Monthly Cash Flow",
            marker_color=COLOR_SCHEME["secondary"]
        ),
        secondary_y=False
    )
    
    # Add cumulative cash flow line
    fig_cash_flow.add_trace(
        go.Scatter(
            x=cf_df["Month"],
            y=cf_df["Cumulative Cash Flow"],
            name="Cumulative Cash Flow",
            mode="lines+markers",
            line=dict(width=3, color=COLOR_SCHEME["primary"])
        ),
        secondary_y=True
    )
    
    # Add break-even point marker if it exists
    if breakeven_month is not None:
        fig_cash_flow.add_trace(
            go.Scatter(
                x=[breakeven_month],
                y=[0],
                name="Break-even Point",
                mode="markers",
                marker=dict(
                    color=COLOR_SCHEME["positive"],
                    size=15,
                    symbol="star"
                ),
                hoverinfo="text",
                hovertext=f"Break-even at month {breakeven_month}"
            ),
            secondary_y=True
        )
    
    # Configure axes
    fig_cash_flow.update_layout(
        title="Cash Flow Analysis Over 3 Years",
        xaxis_title="Month",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        height=500
    )
    
    fig_cash_flow.update_yaxes(
        title_text="Monthly Cash Flow ($)",
        secondary_y=False
    )
    
    fig_cash_flow.update_yaxes(
        title_text="Cumulative Cash Flow ($)",
        secondary_y=True
    )
    
    # Add implementation period shade
    if impl_time > 0:
        fig_cash_flow.add_vrect(
            x0=0,
            x1=impl_time,
            fillcolor=COLOR_SCHEME["subtle"],
            opacity=0.2,
            line_width=0,
            annotation_text="Implementation Period",
            annotation_position="top left"
        )
    
    st.plotly_chart(fig_cash_flow, use_container_width=True)
    
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
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.multiselect(
            "Filter by Category:",
            options=sorted(df['product_category'].unique()),
            default=[]
        )
    
    with col2:
        lifecycle_filter = st.multiselect(
            "Filter by Lifecycle Stage:",
            options=sorted(df['product_lifecycle_stage'].unique()),
            default=[]
        )
    
    with col3:
        roi_threshold = st.slider(
            "Minimum ROI (%)", 
            min_value=-100,
            max_value=500,
            value=0,
            step=25
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if category_filter:
        filtered_df = filtered_df[filtered_df['product_category'].isin(category_filter)]
    
    if lifecycle_filter:
        filtered_df = filtered_df[filtered_df['product_lifecycle_stage'].isin(lifecycle_filter)]
    
    if roi_threshold > -100:
        filtered_df = filtered_df[filtered_df['roi'] >= roi_threshold]
    
    if filtered_df.empty:
        st.warning("No scenarios match your filter criteria.")
        return
    
    # Portfolio quadrant analysis
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">📈</span>
        <h3 class="section-title">Upgrade ROI Quadrant Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Prepare data
    plot_df = filtered_df.copy()
    
    # Set bubble size proportional to net benefit
    size_max = 50
    if plot_df['net_benefit'].max() > 0:
        plot_df['bubble_size'] = size_max * (plot_df['net_benefit'] / plot_df['net_benefit'].max())
        plot_df['bubble_size'] = plot_df['bubble_size'].apply(lambda x: max(10, x))  # Minimum size
    else:
        plot_df['bubble_size'] = 15  # Default size
    
    # Create the bubble chart
    fig_bubble = px.scatter(
        plot_df,
        x="payback_period",
        y="roi",
        size="bubble_size",
        color="score",
        color_continuous_scale="viridis",
        hover_name="scenario_name",
        text="product_name",
        size_max=size_max,
        labels={
            "payback_period": "Payback Period (years)",
            "roi": "Return on Investment (%)",
            "score": "ROI Score"
        },
        title="Upgrade Investment Portfolio Analysis"
    )
    
    # Quadrant lines (1 year payback, 100% ROI)
    fig_bubble.add_shape(
        type="line",
        x0=1, y0=plot_df['roi'].min() if plot_df['roi'].min() < 0 else 0,
        x1=1, y1=plot_df['roi'].max() * 1.1,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    fig_bubble.add_shape(
        type="line",
        x0=0, y0=100,
        x1=plot_df['payback_period'].max() * 1.1 if not pd.isna(plot_df['payback_period'].max()) else
            3, y1=100,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    # Add quadrant labels
    avg_x = 2
    avg_y = 250
    
    fig_bubble.add_annotation(
        x=0.5, y=250,
        text="IDEAL: High ROI, Fast Payback",
        showarrow=False,
        font=dict(color="green", size=12)
    )
    
    fig_bubble.add_annotation(
        x=2, y=250,
        text="GOOD: High ROI, Slower Payback",
        showarrow=False,
        font=dict(color="blue", size=12)
    )
    
    fig_bubble.add_annotation(
        x=0.5, y=50,
        text="CONSIDER: Modest ROI, Fast Payback",
        showarrow=False,
        font=dict(color="orange", size=12)
    )
    
    fig_bubble.add_annotation(
        x=2, y=50,
        text="CAUTION: Lower ROI, Slower Payback",
        showarrow=False,
        font=dict(color="red", size=12)
    )
    
    fig_bubble.update_traces(textposition='top center')
    fig_bubble.update_layout(height=600)
    
    st.plotly_chart(fig_bubble, use_container_width=True)
    
    # Return reduction vs. sales increase analysis
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🔍</span>
        <h3 class="section-title">Return Reduction vs. Sales Growth Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create scatter plot
    fig_scatter = px.scatter(
        plot_df,
        x="estimated_return_reduction",
        y="sales_increase",
        size="development_cost",
        color="roi",
        color_continuous_scale="RdYlGn",
        hover_name="scenario_name",
        text="product_name",
        labels={
            "estimated_return_reduction": "Return Reduction (%)",
            "sales_increase": "Sales Increase (%)",
            "development_cost": "Development Cost ($)",
            "roi": "ROI (%)"
        },
        title="Impact Analysis: Return Reduction vs. Sales Growth"
    )
    
    fig_scatter.update_layout(height=600)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Product category analysis
    if 'product_category' in filtered_df.columns and len(filtered_df['product_category'].unique()) > 1:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">📊</span>
            <h3 class="section-title">Category Performance Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Group by category
        category_data = filtered_df.groupby('product_category').agg({
            'roi': 'mean',
            'net_benefit': 'sum',
            'development_cost': 'sum',
            'estimated_return_reduction': 'mean',
            'sales_increase': 'mean',
            'break_even_months': 'mean'
        }).reset_index()
        
        # Create bar chart for ROI by category
        fig_category = px.bar(
            category_data,
            x="product_category",
            y="roi",
            color="net_benefit",
            color_continuous_scale="viridis",
            labels={
                "product_category": "Product Category",
                "roi": "Average ROI (%)",
                "net_benefit": "Total Net Benefit ($)"
            },
            title="ROI by Product Category"
        )
        
        fig_category.update_layout(height=500)
        st.plotly_chart(fig_category, use_container_width=True)
        
        # Radar chart for category comparison
        categories = ['roi', 'estimated_return_reduction', 'sales_increase']
        categories_display = ['Avg. ROI (%)', 'Avg. Return Reduction (%)', 'Avg. Sales Increase (%)']
        
        # Normalize values for radar chart
        max_roi = max(category_data['roi'].max(), 200)  # Cap at 200% for visualization
        max_reduction = 100
        max_increase = max(category_data['sales_increase'].max(), 50)  # Cap at 50% for visualization
        
        fig_radar = go.Figure()
        
        for _, row in category_data.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[
                    min(row['roi'] / max_roi, 1) * 100,
                    row['estimated_return_reduction'] / max_reduction * 100,
                    row['sales_increase'] / max_increase * 100
                ],
theta=categories_display,
                fill='toself',
                name=row['product_category']
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            height=500,
            title="Category Comparison by Key Metrics"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # Product lifecycle stage analysis
    if 'product_lifecycle_stage' in filtered_df.columns and len(filtered_df['product_lifecycle_stage'].unique()) > 1:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">🔄</span>
            <h3 class="section-title">Product Lifecycle Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Group by lifecycle stage
        lifecycle_data = filtered_df.groupby('product_lifecycle_stage').agg({
            'roi': 'mean',
            'net_benefit': 'sum',
            'development_cost': 'sum',
            'estimated_return_reduction': 'mean',
            'sales_increase': 'mean',
            'payback_period': 'mean'
        }).reset_index()
        
        # Ensure lifecycle stages are in correct order
        lifecycle_order = ["Introduction", "Growth", "Maturity", "Decline"]
        lifecycle_data['product_lifecycle_stage'] = pd.Categorical(
            lifecycle_data['product_lifecycle_stage'], 
            categories=lifecycle_order, 
            ordered=True
        )
        lifecycle_data = lifecycle_data.sort_values('product_lifecycle_stage')
        
        # Create comparison chart
        fig_lifecycle = go.Figure()
        
        # Add ROI bars
        fig_lifecycle.add_trace(go.Bar(
            x=lifecycle_data['product_lifecycle_stage'],
            y=lifecycle_data['roi'],
            name='ROI (%)',
            marker_color=COLOR_SCHEME['positive']
        ))
        
        # Add sales increase line
        fig_lifecycle.add_trace(go.Scatter(
            x=lifecycle_data['product_lifecycle_stage'],
            y=lifecycle_data['sales_increase'],
            name='Sales Increase (%)',
            mode='lines+markers',
            marker=dict(size=10),
            line=dict(width=3, color=COLOR_SCHEME['neutral']),
            yaxis='y2'
        ))
        
        # Configure axes
        fig_lifecycle.update_layout(
            yaxis=dict(
                title='ROI (%)',
                side='left',
                titlefont=dict(color=COLOR_SCHEME['positive']),
                tickfont=dict(color=COLOR_SCHEME['positive'])
            ),
            yaxis2=dict(
                title='Sales Increase (%)',
                side='right',
                overlaying='y',
                titlefont=dict(color=COLOR_SCHEME['neutral']),
                tickfont=dict(color=COLOR_SCHEME['neutral'])
            ),
            title="ROI and Sales Impact by Product Lifecycle Stage",
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig_lifecycle, use_container_width=True)
    
    # Development cost vs. net benefit analysis
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">💵</span>
        <h3 class="section-title">Investment vs. Return Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Scatter plot of development cost vs. net benefit
    fig_cost_benefit = px.scatter(
        filtered_df,
        x="development_cost",
        y="net_benefit",
        color="payback_period",
        size="bubble_size",
        color_continuous_scale="RdYlGn_r",  # Reversed scale - lower payback is better
        hover_name="scenario_name",
        text="product_name",
        labels={
            "development_cost": "Development Cost ($)",
            "net_benefit": "Annual Net Benefit ($)",
            "payback_period": "Payback Period (years)"
        },
        title="Development Cost vs. Annual Net Benefit"
    )
    
    # Add 1:1 reference line
    max_val = max(
        filtered_df['development_cost'].max(),
        filtered_df['net_benefit'].max()
    )
    
    fig_cost_benefit.add_shape(
        type="line",
        x0=0, y0=0,
        x1=max_val, y1=max_val,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    # Add annotation for 1:1 line
    fig_cost_benefit.add_annotation(
        x=max_val*0.7,
        y=max_val*0.7,
        text="1:1 Line (1-year payback)",
        showarrow=False,
        textangle=-45,
        font=dict(color="gray", size=10)
    )
    
    fig_cost_benefit.update_layout(height=600)
    st.plotly_chart(fig_cost_benefit, use_container_width=True)
    
    # Investment recommendations
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🎯</span>
        <h3 class="section-title">Investment Recommendations</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Find the best scenarios by different metrics
    best_roi = filtered_df.loc[filtered_df['roi'].idxmax()]
    best_npv = filtered_df.loc[filtered_df['npv'].fillna(-float('inf')).idxmax()]
    
    # Find quickest payback
    payback_df = filtered_df[filtered_df['payback_period'].notna()]
    quickest_payback = payback_df.loc[payback_df['payback_period'].idxmin()] if not payback_df.empty else None
    
    # Best sales impact
    best_sales = filtered_df.loc[filtered_df['sales_impact_annual'].idxmax()]
    
    # Best return reduction
    best_return = filtered_df.loc[(filtered_df['estimated_return_reduction'] * filtered_df['return_rate']).idxmax()]
    
    # Display recommendations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="product-card highlight-box">
            <div class="product-header">
                <strong>Best ROI Upgrade</strong>
            </div>
            <p><strong>{}</strong> - {}</p>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">{:.1f}%</div>
                    <div class="stat-label">ROI</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${:,.2f}</div>
                    <div class="stat-label">Dev. Cost</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${:,.2f}</div>
                    <div class="stat-label">Annual Net Benefit</div>
                </div>
            </div>
        </div>
        """.format(
            best_roi['scenario_name'],
            best_roi['upgrade_solution'],
            best_roi['roi'],
            best_roi['development_cost'],
            best_roi['net_benefit']
        ), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="product-card highlight-box">
            <div class="product-header">
                <strong>Best NPV Upgrade</strong>
            </div>
            <p><strong>{}</strong> - {}</p>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">${:,.2f}</div>
                    <div class="stat-label">NPV</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{:.1f}%</div>
                    <div class="stat-label">ROI</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{:.2f} years</div>
                    <div class="stat-label">Payback Period</div>
                </div>
            </div>
        </div>
        """.format(
            best_npv['scenario_name'],
            best_npv['upgrade_solution'],
            best_npv['npv'],
            best_npv['roi'],
            best_npv['payback_period'] if pd.notna(best_npv['payback_period']) else 'N/A'
        ), unsafe_allow_html=True)
    
    with col2:
        if quickest_payback is not None:
            st.markdown("""
            <div class="product-card highlight-box">
                <div class="product-header">
                    <strong>Quickest Payback Upgrade</strong>
                </div>
                <p><strong>{}</strong> - {}</p>
                <div class="product-stats">
                    <div class="stat-item">
                        <div class="stat-value">{:.2f} years</div>
                        <div class="stat-label">Payback Period</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{:.1f}%</div>
                        <div class="stat-label">ROI</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${:,.2f}</div>
                        <div class="stat-label">Development Cost</div>
                    </div>
                </div>
            </div>
            """.format(
                quickest_payback['scenario_name'],
                quickest_payback['upgrade_solution'],
                quickest_payback['payback_period'],
                quickest_payback['roi'],
                quickest_payback['development_cost']
            ), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="product-card highlight-box">
            <div class="product-header">
                <strong>Best Sale/Return Impact Upgrade</strong>
            </div>
            <p><strong>{}</strong> - {}</p>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">{:.1f}%</div>
                    <div class="stat-label">Sales Increase</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{:.1f}%</div>
                    <div class="stat-label">Return Reduction</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{:.1f}%</div>
                    <div class="stat-label">ROI</div>
                </div>
            </div>
        </div>
        """.format(
            best_sales['scenario_name'] if best_sales['sales_increase'] > best_return['estimated_return_reduction'] else best_return['scenario_name'],
            best_sales['upgrade_solution'] if best_sales['sales_increase'] > best_return['estimated_return_reduction'] else best_return['upgrade_solution'],
            best_sales['sales_increase'],
            best_return['estimated_return_reduction'],
            best_sales['roi'] if best_sales['sales_increase'] > best_return['estimated_return_reduction'] else best_return['roi']
        ), unsafe_allow_html=True)

def display_what_if_analysis():
    """Interactive what-if scenario analysis for product upgrades"""
    st.subheader("Product Upgrade What-If Analysis")
    
    # Get base scenario
    if not optimizer.scenarios.empty:
        # Let user select a base scenario
        scenario_names = optimizer.scenarios['scenario_name'].tolist()
        base_scenario_name = st.selectbox("Select base scenario for what-if analysis", scenario_names)
        
        # Get the selected scenario
        base_scenario = optimizer.scenarios[optimizer.scenarios['scenario_name'] == base_scenario_name].iloc[0]
        
        # Create a more tailored what-if analysis using tabs
        tabs = st.tabs(["Upgrade Parameters", "Financial Impacts", "Sales/Return Impacts", "Production Timeline"])
        
        # Store what-if parameters in session state to share between tabs
        if 'whatif_params' not in st.session_state:
            st.session_state.whatif_params = {
                'development_cost_change': 0,
                'unit_cost_change_adjust': 0,
                'return_reduction_adjust': 0,
                'sales_increase_adjust': 0,
                'return_processing_change': 0,
                'implementation_time_change': 0,
                'price_change': 0
            }
        
        # Tab 1: Upgrade Parameters
        with tabs[0]:
            st.markdown("### Adjust Upgrade Parameters")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Development cost change
                st.session_state.whatif_params['development_cost_change'] = st.slider(
                    "Development Cost Change (%)", 
                    min_value=-50, 
                    max_value=100, 
                    value=st.session_state.whatif_params['development_cost_change'],
                    help="Adjust the one-time cost required to implement the upgrade. For example, -20% means the upgrade costs 20% less than estimated."
                )
                
                # Unit cost change adjustment
                st.session_state.whatif_params['unit_cost_change_adjust'] = st.slider(
                    "Unit Cost Change Adjustment ($)", 
                    min_value=-max(2, abs(base_scenario['unit_cost_change']*2)), 
                    max_value=max(2, abs(base_scenario['unit_cost_change']*2)), 
                    value=st.session_state.whatif_params['unit_cost_change_adjust'],
                    step=0.05,
                    help="Adjust how much the upgrade affects the unit production cost. Positive means increased cost, negative means savings."
                )
                
                # Implementation time change
                st.session_state.whatif_params['implementation_time_change'] = st.slider(
                    "Implementation Time Change (months)", 
                    min_value=-max(3, base_scenario['time_to_implement']), 
                    max_value=12, 
                    value=st.session_state.whatif_params['implementation_time_change'],
                    help="Adjust how long it takes to implement the product upgrade. Negative means faster implementation."
                )
            
            with col2:
                # Return reduction adjustment
                st.session_state.whatif_params['return_reduction_adjust'] = st.slider(
                    "Return Reduction Adjustment (%)", 
                    min_value=-base_scenario['estimated_return_reduction'], 
                    max_value=min(50, 100 - base_scenario['estimated_return_reduction']), 
                    value=st.session_state.whatif_params['return_reduction_adjust'],
                    help="Adjust how effective the upgrade is at reducing returns. For example, +10% means the upgrade reduces returns by 10% more than originally estimated."
                )
                
                # Sales increase adjustment
                st.session_state.whatif_params['sales_increase_adjust'] = st.slider(
                    "Sales Increase Adjustment (%)", 
                    min_value=-base_scenario['sales_increase'], 
                    max_value=50, 
                    value=st.session_state.whatif_params['sales_increase_adjust'],
                    help="Adjust the projected sales increase from the upgrade. For example, +5% means the upgrade increases sales by 5% more than originally estimated."
                )
                
                # Return processing cost change
                st.session_state.whatif_params['return_processing_change'] = st.slider(
                    "Return Processing Cost Change (%)", 
                    min_value=-50, 
                    max_value=50, 
                    value=st.session_state.whatif_params['return_processing_change'],
                    help="Adjust the cost to process each return. This affects the value of each avoided return."
                )
                
                # Price change
                st.session_state.whatif_params['price_change'] = st.slider(
                    "Product Price Change (%)", 
                    min_value=-25, 
                    max_value=25, 
                    value=st.session_state.whatif_params['price_change'],
                    help="Adjust the product's sales price. This affects both revenue and the value of avoided returns."
                )
            
            # Calculate new values based on adjusted parameters
            new_development_cost = base_scenario['development_cost'] * (1 + st.session_state.whatif_params['development_cost_change']/100)
            new_unit_cost_change = base_scenario['unit_cost_change'] + st.session_state.whatif_params['unit_cost_change_adjust']
            new_reduction_rate = base_scenario['estimated_return_reduction'] + st.session_state.whatif_params['return_reduction_adjust']
            new_sales_increase = base_scenario['sales_increase'] + st.session_state.whatif_params['sales_increase_adjust']
            new_return_processing_cost = base_scenario['return_processing_cost'] * (1 + st.session_state.whatif_params['return_processing_change']/100)
            new_implementation_time = max(1, base_scenario['time_to_implement'] + st.session_state.whatif_params['implementation_time_change'])
            new_avg_price = base_scenario['avg_sale_price'] * (1 + st.session_state.whatif_params['price_change']/100)
            
            # Display comparison table
            st.markdown("### Parameter Comparison")
            
            comparison_data = {
                "Parameter": [
                    "Development Cost ($)",
                    "Unit Cost Change ($)",
                    "Return Reduction (%)",
                    "Sales Increase (%)",
                    "Return Processing Cost ($)",
                    "Implementation Time (months)",
                    "Average Price ($)"
                ],
                "Original": [
                    base_scenario['development_cost'],
                    base_scenario['unit_cost_change'],
                    base_scenario['estimated_return_reduction'],
                    base_scenario['sales_increase'],
                    base_scenario['return_processing_cost'],
                    base_scenario['time_to_implement'],
                    base_scenario['avg_sale_price']
                ],
                "New": [
                    new_development_cost,
                    new_unit_cost_change,
                    new_reduction_rate,
                    new_sales_increase,
                    new_return_processing_cost,
                    new_implementation_time,
                    new_avg_price
                ]
            }
            
            # Format for display
            comparison_df = pd.DataFrame(comparison_data)
            
            # Format currencies
            for i, param in enumerate(comparison_df["Parameter"]):
                if "Cost" in param or "Price" in param:
                    comparison_df.loc[i, "Original"] = f"${comparison_df.loc[i, 'Original']:,.2f}"
                    comparison_df.loc[i, "New"] = f"${float(comparison_df.loc[i, 'New']):,.2f}"
                elif "%" in param:
                    comparison_df.loc[i, "Original"] = f"{comparison_df.loc[i, 'Original']:.1f}%"
                    comparison_df.loc[i, "New"] = f"{float(comparison_df.loc[i, 'New']):.1f}%"
            
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        # Tab 2: Financial Impacts
        with tabs[1]:
            st.markdown("### Financial Impact Analysis")
            
            # Recalculate key metrics with new parameters
            # Get the parameter values
            development_cost = base_scenario['development_cost'] * (1 + st.session_state.whatif_params['development_cost_change']/100)
            unit_cost_change = base_scenario['unit_cost_change'] + st.session_state.whatif_params['unit_cost_change_adjust']
            reduction_rate = base_scenario['estimated_return_reduction'] + st.session_state.whatif_params['return_reduction_adjust']
            sales_increase = base_scenario['sales_increase'] + st.session_state.whatif_params['sales_increase_adjust']
            return_processing_cost = base_scenario['return_processing_cost'] * (1 + st.session_state.whatif_params['return_processing_change']/100)
            implementation_time = max(1, base_scenario['time_to_implement'] + st.session_state.whatif_params['implementation_time_change'])
            avg_price = base_scenario['avg_sale_price'] * (1 + st.session_state.whatif_params['price_change']/100)
            
            # Calculate original avoided returns and financial impact
            original_avoided_monthly = base_scenario['current_returns'] * (base_scenario['estimated_return_reduction'] / 100)
            original_savings_per_avoided = base_scenario['avg_sale_price'] + base_scenario['return_processing_cost'] - base_scenario['current_unit_cost']
            original_monthly_return_savings = original_avoided_monthly * original_savings_per_avoided
            
            original_additional_sales = base_scenario['current_unit_sales'] * (base_scenario['sales_increase'] / 100)
            original_margin_after = base_scenario['avg_sale_price'] - (base_scenario['current_unit_cost'] + base_scenario['unit_cost_change'])
            original_monthly_sales_benefit = original_additional_sales * original_margin_after
            
            original_additional_costs = base_scenario['unit_cost_change'] * (
                base_scenario['current_unit_sales'] - base_scenario['current_returns'] + original_avoided_monthly + original_additional_sales
            )
            
            original_monthly_net = original_monthly_return_savings + original_monthly_sales_benefit - original_additional_costs
            original_annual_net = original_monthly_net * 12
            
            # Calculate new financial impact
            new_avoided_monthly = base_scenario['current_returns'] * (reduction_rate / 100)
            new_savings_per_avoided = avg_price + return_processing_cost - base_scenario['current_unit_cost']
            new_monthly_return_savings = new_avoided_monthly * new_savings_per_avoided
            
            new_additional_sales = base_scenario['current_unit_sales'] * (sales_increase / 100)
            new_margin_after = avg_price - (base_scenario['current_unit_cost'] + unit_cost_change)
            new_monthly_sales_benefit = new_additional_sales * new_margin_after
            
            new_additional_costs = unit_cost_change * (
                base_scenario['current_unit_sales'] - base_scenario['current_returns'] + new_avoided_monthly + new_additional_sales
            )
            
            new_monthly_net = new_monthly_return_savings + new_monthly_sales_benefit - new_additional_costs
            new_annual_net = new_monthly_net * 12
            
            # Calculate ROI metrics
            if base_scenario['development_cost'] > 0 and original_annual_net > 0:
                original_roi = (original_annual_net / base_scenario['development_cost']) * 100
                original_payback = base_scenario['development_cost'] / original_monthly_net / 12
            else:
                original_roi = 0
                original_payback = None
            
            if development_cost > 0 and new_annual_net > 0:
                new_roi = (new_annual_net / development_cost) * 100
                new_payback = development_cost / new_monthly_net / 12
            else:
                new_roi = 0
                new_payback = None
            
            # Create financial comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Return Reduction Impact")
                
                metrics_data = {
                    "Metric": [
                        "Monthly Avoided Returns",
                        "Savings per Avoided Return",
                        "Monthly Return Savings"
                    ],
                    "Original": [
                        f"{original_avoided_monthly:.1f} units",
                        f"${original_savings_per_avoided:.2f}",
                        f"${original_monthly_return_savings:.2f}"
                    ],
                    "New": [
                        f"{new_avoided_monthly:.1f} units",
                        f"${new_savings_per_avoided:.2f}",
                        f"${new_monthly_return_savings:.2f}"
                    ],
                    "Change": [
                        f"{(new_avoided_monthly - original_avoided_monthly):.1f} units",
                        f"${(new_savings_per_avoided - original_savings_per_avoided):.2f}",
                        f"${(new_monthly_return_savings - original_monthly_return_savings):.2f}"
                    ]
                }
                
                metrics_df = pd.DataFrame(metrics_data)
                st.dataframe(metrics_df, use_container_width=True, hide_index=True)
                
                return_impact = (new_monthly_return_savings - original_monthly_return_savings) * 12
                
                # Chart comparing original and new return impact
                fig_return = go.Figure()
                
                categories = ['Avoided Returns', 'Monthly Return Savings']
                original_values = [original_avoided_monthly, original_monthly_return_savings]
                new_values = [new_avoided_monthly, new_monthly_return_savings]
                
                fig_return.add_trace(go.Bar(
                    x=categories,
                    y=original_values,
                    name='Original',
                    marker_color=COLOR_SCHEME['neutral']
                ))
                
                fig_return.add_trace(go.Bar(
                    x=categories,
                    y=new_values,
                    name='New',
                    marker_color=COLOR_SCHEME['positive']
                ))
                
                fig_return.update_layout(
                    title="Return Reduction Impact Comparison",
                    barmode='group',
                    height=400,
                    yaxis=dict(title='Value')
                )
                
                st.plotly_chart(fig_return, use_container_width=True)
            
            with col2:
                st.markdown("#### Sales Growth Impact")
                
                sales_metrics = {
                    "Metric": [
                        "Monthly Additional Sales",
                        "Margin per Unit",
                        "Monthly Sales Benefit"
                    ],
                    "Original": [
                        f"{original_additional_sales:.1f} units",
                        f"${original_margin_after:.2f}",
                        f"${original_monthly_sales_benefit:.2f}"
                    ],
                    "New": [
                        f"{new_additional_sales:.1f} units",
                        f"${new_margin_after:.2f}",
                        f"${new_monthly_sales_benefit:.2f}"
                    ],
                    "Change": [
                        f"{(new_additional_sales - original_additional_sales):.1f} units",
                        f"${(new_margin_after - original_margin_after):.2f}",
                        f"${(new_monthly_sales_benefit - original_monthly_sales_benefit):.2f}"
                    ]
                }
                
                sales_df = pd.DataFrame(sales_metrics)
                st.dataframe(sales_df, use_container_width=True, hide_index=True)
                
                sales_impact = (new_monthly_sales_benefit - original_monthly_sales_benefit) * 12
                
                # Chart comparing original and new sales impact
                fig_sales = go.Figure()
                
                categories = ['Additional Sales', 'Monthly Sales Benefit']
                original_values = [original_additional_sales, original_monthly_sales_benefit]
                new_values = [new_additional_sales, new_monthly_sales_benefit]
                
                fig_sales.add_trace(go.Bar(
                    x=categories,
                    y=original_values,
                    name='Original',
                    marker_color=COLOR_SCHEME['neutral']
                ))
                
                fig_sales.add_trace(go.Bar(
                    x=categories,
                    y=new_values,
                    name='New',
                    marker_color=COLOR_SCHEME['positive']
                ))
                
                fig_sales.update_layout(
                    title="Sales Growth Impact Comparison",
                    barmode='group',
                    height=400,
                    yaxis=dict(title='Value')
                )
                
                st.plotly_chart(fig_sales, use_container_width=True)
            
            # Overall financial impact
            st.markdown("#### Overall Financial Impact")
            
            # Summary metrics table
            summary_data = {
                "Metric": [
                    "Monthly Return Savings",
                    "Monthly Sales Benefit",
                    "Monthly Additional Costs",
                    "Monthly Net Benefit",
                    "Annual Net Benefit",
                    "Return on Investment",
                    "Payback Period"
                ],
                "Original": [
                    f"${original_monthly_return_savings:.2f}",
                    f"${original_monthly_sales_benefit:.2f}",
                    f"${original_additional_costs:.2f}",
                    f"${original_monthly_net:.2f}",
                    f"${original_annual_net:.2f}",
                    f"{original_roi:.1f}%" if original_roi is not None else "N/A",
                    f"{original_payback:.2f} years" if original_payback is not None else "N/A"
                ],
                "New": [
                    f"${new_monthly_return_savings:.2f}",
                    f"${new_monthly_sales_benefit:.2f}",
                    f"${new_additional_costs:.2f}",
                    f"${new_monthly_net:.2f}",
                    f"${new_annual_net:.2f}",
                    f"{new_roi:.1f}%" if new_roi is not None else "N/A",
                    f"{new_payback:.2f} years" if new_payback is not None else "N/A"
                ]
            }
            
            # Calculate percent changes
            summary_data["Change"] = [
                f"{((new_monthly_return_savings / original_monthly_return_savings) - 1) * 100:.1f}%" if original_monthly_return_savings > 0 else "N/A",
                f"{((new_monthly_sales_benefit / original_monthly_sales_benefit) - 1) * 100:.1f}%" if original_monthly_sales_benefit > 0 else "N/A",
                f"{((new_additional_costs / original_additional_costs) - 1) * 100:.1f}%" if original_additional_costs > 0 else "N/A",
                f"{((new_monthly_net / original_monthly_net) - 1) * 100:.1f}%" if original_monthly_net > 0 else "N/A",
                f"{((new_annual_net / original_annual_net) - 1) * 100:.1f}%" if original_annual_net > 0 else "N/A",
                f"{((new_roi / original_roi) - 1) * 100:.1f}%" if original_roi is not None and original_roi > 0 and new_roi is not None else "N/A",
                f"{((new_payback / original_payback) - 1) * 100:.1f}%" if original_payback is not None and new_payback is not None else "N/A"
            ]
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            # Waterfall chart
            st.markdown("#### Impact Breakdown")
            
            # Create waterfall chart data
            waterfall_data = [
                {"Factor": "Original Net Benefit", "Impact": original_monthly_net, "Type": "Total"},
                {"Factor": "Return Reduction", "Impact": new_monthly_return_savings - original_monthly_return_savings, "Type": "Increase" if new_monthly_return_savings > original_monthly_return_savings else "Decrease"},
                {"Factor": "Sales Growth", "Impact": new_monthly_sales_benefit - original_monthly_sales_benefit, "Type": "Increase" if new_monthly_sales_benefit > original_monthly_sales_benefit else "Decrease"},
                {"Factor": "Additional Costs", "Impact": original_additional_costs - new_additional_costs, "Type": "Increase" if original_additional_costs > new_additional_costs else "Decrease"},
                {"Factor": "New Net Benefit", "Impact": new_monthly_net, "Type": "Total"}
            ]
            
            waterfall_df = pd.DataFrame(waterfall_data)
            
            # Create the waterfall chart
            fig_waterfall = go.Figure(go.Waterfall(
                name="Monthly Net Benefit Changes",
                orientation="v",
                measure=["absolute"] + ["relative"] * 3 + ["total"],
                x=waterfall_df["Factor"],
                y=waterfall_df["Impact"],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                decreasing={"marker": {"color": COLOR_SCHEME["negative"]}},
                increasing={"marker": {"color": COLOR_SCHEME["positive"]}},
                totals={"marker": {"color": COLOR_SCHEME["primary"]}}
            ))
            
            fig_waterfall.update_layout(
                title="Monthly Net Benefit Impact Analysis",
                showlegend=False,
                height=500
            )
            
            st.plotly_chart(fig_waterfall, use_container_width=True)
            
            # Compare ROI and payback
            col1, col2 = st.columns(2)
            
            with col1:
                # ROI comparison
                roi_change = ((new_roi / original_roi) - 1) * 100 if original_roi > 0 and new_roi is not None else 0
                
                st.metric(
                    "Return on Investment",
                    f"{new_roi:.1f}%" if new_roi is not None else "N/A",
                    f"{roi_change:.1f}%" if original_roi > 0 and new_roi is not None else None,
                    delta_color="normal" if roi_change >= 0 else "inverse"
                )
            
            with col2:
                # Payback comparison
                if original_payback is not None and new_payback is not None:
                    payback_change = ((new_payback / original_payback) - 1) * 100
                    
                    st.metric(
                        "Payback Period",
                        f"{new_payback:.2f} years",
                        f"{payback_change:.1f}%",
                        delta_color="inverse"  # Inverse because lower payback is better
                    )
                else:
                    st.metric(
                        "Payback Period",
                        "N/A",
                        None
                    )
        
        # Tab 3: Sales/Return Impacts
        with tabs[2]:
            st.markdown("### Product Performance Analysis")
            
            # Extract parameters
            reduction_rate = base_scenario['estimated_return_reduction'] + st.session_state.whatif_params['return_reduction_adjust']
            sales_increase = base_scenario['sales_increase'] + st.session_state.whatif_params['sales_increase_adjust']
            
            # Calculate impacts on returns and sales
            original_return_rate = base_scenario['return_rate']
            new_return_rate = original_return_rate * (1 - reduction_rate/100)
            
            original_monthly_sales = base_scenario['current_unit_sales']
            new_monthly_sales = original_monthly_sales * (1 + sales_increase/100)
            
            original_monthly_returns = base_scenario['current_returns']
            new_monthly_returns = new_monthly_sales * (new_return_rate/100)
            
            monthly_returns_change = new_monthly_returns - original_monthly_returns
            monthly_returns_percent_change = (monthly_returns_change / original_monthly_returns) * 100
            
            # Create before/after comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Return Rate Impact")
                
                # Create return rate comparison chart
                return_data = {
                    "Metric": ["Return Rate", "Monthly Returns", "Annual Returns"],
                    "Before": [
                        f"{original_return_rate:.2f}%",
                        f"{original_monthly_returns:.1f} units",
                        f"{original_monthly_returns * 12:.1f} units"
                    ],
                    "After": [
                        f"{new_return_rate:.2f}%",
                        f"{new_monthly_returns:.1f} units",
                        f"{new_monthly_returns * 12:.1f} units"
                    ],
                    "Change": [
                        f"{(new_return_rate - original_return_rate):.2f}%",
                        f"{monthly_returns_change:.1f} units",
                        f"{monthly_returns_change * 12:.1f} units"
                    ]
                }
                
                return_df = pd.DataFrame(return_data)
                st.dataframe(return_df, use_container_width=True, hide_index=True)
                
                # Return rate chart
                fig_return_rate = go.Figure()
                
                # Add return rate bars
                fig_return_rate.add_trace(go.Bar(
                    x=["Before", "After"],
                    y=[original_return_rate, new_return_rate],
                    name="Return Rate (%)",
                    marker_color=[COLOR_SCHEME["negative"], COLOR_SCHEME["positive"]],
                    text=[f"{original_return_rate:.2f}%", f"{new_return_rate:.2f}%"],
                    textposition="auto"
                ))
                
                fig_return_rate.update_layout(
                    title="Return Rate Before vs After Upgrade",
                    height=400,
                    yaxis=dict(title="Return Rate (%)")
                )
                
                st.plotly_chart(fig_return_rate, use_container_width=True)
            
            with col2:
                st.markdown("#### Sales Volume Impact")
                
                # Create sales volume comparison chart
                sales_data = {
                    "Metric": ["Monthly Sales", "Annual Sales", "Sales Growth"],
                    "Before": [
                        f"{original_monthly_sales:.1f} units",
                        f"{original_monthly_sales * 12:.1f} units",
                        "N/A"
                    ],
                    "After": [
                        f"{new_monthly_sales:.1f} units",
                        f"{new_monthly_sales * 12:.1f} units",
                        f"{sales_increase:.2f}%"
                    ],
                    "Change": [
                        f"{(new_monthly_sales - original_monthly_sales):.1f} units",
                        f"{(new_monthly_sales - original_monthly_sales) * 12:.1f} units",
                        f"{sales_increase:.2f}%"
                    ]
                }
                
                sales_df = pd.DataFrame(sales_data)
                st.dataframe(sales_df, use_container_width=True, hide_index=True)
                
                # Sales volume chart
                fig_sales = go.Figure()
                
                # Add sales volume bars
                fig_sales.add_trace(go.Bar(
                    x=["Before", "After"],
                    y=[original_monthly_sales, new_monthly_sales],
                    name="Monthly Sales (units)",
                    marker_color=[COLOR_SCHEME["neutral"], COLOR_SCHEME["positive"]],
                    text=[f"{original_monthly_sales:.1f}", f"{new_monthly_sales:.1f}"],
                    textposition="auto"
                ))
                
                fig_sales.update_layout(
                    title="Monthly Sales Before vs After Upgrade",
                    height=400,
                    yaxis=dict(title="Monthly Sales (units)")
                )
                
                st.plotly_chart(fig_sales, use_container_width=True)
            
            # Combined impact
            st.markdown("#### Combined Impact on Unit Economics")
            
            # Calculate unit economics
            price_change = st.session_state.whatif_params['price_change']
            unit_cost_change = base_scenario['unit_cost_change'] + st.session_state.whatif_params['unit_cost_change_adjust']
            
            original_price = base_scenario['avg_sale_price']
            new_price = original_price * (1 + price_change/100)
            
            original_unit_cost = base_scenario['current_unit_cost']
            new_unit_cost = original_unit_cost + unit_cost_change
            
            original_margin = original_price - original_unit_cost
            new_margin = new_price - new_unit_cost
            
            original_margin_percent = (original_margin / original_price) * 100
            new_margin_percent = (new_margin / new_price) * 100
            
            # Calculate total revenue and profit impact
            original_monthly_revenue = original_monthly_sales * original_price
            new_monthly_revenue = new_monthly_sales * new_price
            
            original_monthly_profit = original_monthly_sales * original_margin
            new_monthly_profit = new_monthly_sales * new_margin
            
            revenue_change = new_monthly_revenue - original_monthly_revenue
            profit_change = new_monthly_profit - original_monthly_profit
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Monthly Revenue",
                    f"${new_monthly_revenue:.2f}",
                    f"{((new_monthly_revenue / original_monthly_revenue) - 1) * 100:.1f}%",
                    delta_color="normal"
                )
            
            with col2:
                st.metric(
                    "Monthly Profit",
                    f"${new_monthly_profit:.2f}",
                    f"{((new_monthly_profit / original_monthly_profit) - 1) * 100:.1f}%",
                    delta_color="normal"
                )
            
            with col3:
                st.metric(
                    "Unit Margin",
                    f"${new_margin:.2f} ({new_margin_percent:.1f}%)",
                    f"{((new_margin / original_margin) - 1) * 100:.1f}%",
                    delta_color="normal" if new_margin >= original_margin else "inverse"
                )
            
            # Create unit economics comparison chart
            fig_unit = go.Figure()
            
            # Add price, cost, and margin bars
            categories = ["Price", "Unit Cost", "Margin"]
            original_values = [original_price, original_unit_cost, original_margin]
            new_values = [new_price, new_unit_cost, new_margin]
            
            fig_unit.add_trace(go.Bar(
                x=categories,
                y=original_values,
                name="Before",
                marker_color=COLOR_SCHEME["neutral"]
            ))
            
            fig_unit.add_trace(go.Bar(
                x=categories,
                y=new_values,
                name="After",
                marker_color=COLOR_SCHEME["positive"]
            ))
            
            fig_unit.update_layout(
                title="Unit Economics Before vs After Upgrade",
                barmode="group",
                height=400,
                yaxis=dict(title="Amount ($)")
            )
            
            st.plotly_chart(fig_unit, use_container_width=True)
        
        # Tab 4: Production Timeline
        with tabs[3]:
            st.markdown("### Implementation Timeline Analysis")
            
            # Get implementation time parameters
            original_time = base_scenario['time_to_implement']
            new_time = max(1, original_time + st.session_state.whatif_params['implementation_time_change'])
            
            # Calculate development cost
            original_dev_cost = base_scenario['development_cost']
            new_dev_cost = original_dev_cost * (1 + st.session_state.whatif_params['development_cost_change']/100)
            
            # Calculate monthly net benefit
            original_monthly_net = base_scenario['monthly_net_benefit']
            
            # Recalculate monthly net with new parameters
            reduction_rate = base_scenario['estimated_return_reduction'] + st.session_state.whatif_params['return_reduction_adjust']
            sales_increase = base_scenario['sales_increase'] + st.session_state.whatif_params['sales_increase_adjust']
            unit_cost_change = base_scenario['unit_cost_change'] + st.session_state.whatif_params['unit_cost_change_adjust']
            avg_price = base_scenario['avg_sale_price'] * (1 + st.session_state.whatif_params['price_change']/100)
            return_processing_cost = base_scenario['return_processing_cost'] * (1 + st.session_state.whatif_params['return_processing_change']/100)
            
            # Calculate new monthly net benefit
            new_avoided_monthly = base_scenario['current_returns'] * (reduction_rate / 100)
            new_savings_per_avoided = avg_price + return_processing_cost - base_scenario['current_unit_cost']
            new_monthly_return_savings = new_avoided_monthly * new_savings_per_avoided
            
            new_additional_sales = base_scenario['current_unit_sales'] * (sales_increase / 100)
            new_margin_after = avg_price - (base_scenario['current_unit_cost'] + unit_cost_change)
            new_monthly_sales_benefit = new_additional_sales * new_margin_after
            
            new_additional_costs = unit_cost_change * (
                base_scenario['current_unit_sales'] - base_scenario['current_returns'] + new_avoided_monthly + new_additional_sales
            )
            
            new_monthly_net = new_monthly_return_savings + new_monthly_sales_benefit - new_additional_costs
            
            # Calculate time to breakeven
            if original_monthly_net > 0:
                original_breakeven_months = original_dev_cost / original_monthly_net
                original_total_time = original_time + original_breakeven_months
            else:
                original_breakeven_months = float('inf')
                original_total_time = float('inf')
            
            if new_monthly_net > 0:
                new_breakeven_months = new_dev_cost / new_monthly_net
                new_total_time = new_time + new_breakeven_months
            else:
                new_breakeven_months = float('inf')
                new_total_time = float('inf')
            
            # Display timeline comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Timeline Comparison")
                
                timeline_data = {
                    "Metric": [
                        "Implementation Time",
                        "Breakeven Time (after implementation)",
                        "Total Time to ROI Positive"
                    ],
                    "Original": [
                        f"{original_time} months",
                        f"{original_breakeven_months:.1f} months" if original_breakeven_months != float('inf') else "Never",
                        f"{original_total_time:.1f} months" if original_total_time != float('inf') else "Never"
                    ],
                    "New": [
                        f"{new_time} months",
                        f"{new_breakeven_months:.1f} months" if new_breakeven_months != float('inf') else "Never",
                        f"{new_total_time:.1f} months" if new_total_time != float('inf') else "Never"
                    ],
                    "Change": [
                        f"{new_time - original_time} months",
                        f"{new_breakeven_months - original_breakeven_months:.1f} months" if original_breakeven_months != float('inf') and new_breakeven_months != float('inf') else "N/A",
                        f"{new_total_time - original_total_time:.1f} months" if original_total_time != float('inf') and new_total_time != float('inf') else "N/A"
                    ]
                }
                
                timeline_df = pd.DataFrame(timeline_data)
                st.dataframe(timeline_df, use_container_width=True, hide_index=True)
                
                # Show key metrics
                st.markdown("#### Key Timeline Metrics")
                
                time_diff = new_total_time - original_total_time if original_total_time != float('inf') and new_total_time != float('inf') else None
                
                st.metric(
                    "Total Time to Positive ROI",
                    f"{new_total_time:.1f} months" if new_total_time != float('inf') else "Never",
                    f"{time_diff:.1f} months" if time_diff is not None else None,
                    delta_color="inverse"  # Inverse because shorter time is better
                )
                
                # Calculate opportunity cost
                if original_monthly_net > 0:
                    opportunity_cost = original_monthly_net * (new_time - original_time) if new_time > original_time else 0
                    
                    st.metric(
                        "Opportunity Cost of Delayed Implementation",
                        f"${opportunity_cost:.2f}",
                        None
                    )
            
            with col2:
                st.markdown("#### Timeline Visualization")
                
                # Create timeline visualization
                # First, create data for Gantt-like chart
                
                # Original timeline
                original_timeline = [
                    dict(Task="Original", Start=0, Finish=original_time, Resource="Implementation"),
                    dict(Task="Original", Start=original_time, Finish=original_time + original_breakeven_months if original_breakeven_months != float('inf') else 36, Resource="Breakeven")
                ]
                
                # New timeline
                new_timeline = [
                    dict(Task="New", Start=0, Finish=new_time, Resource="Implementation"),
                    dict(Task="New", Start=new_time, Finish=new_time + new_breakeven_months if new_breakeven_months != float('inf') else 36, Resource="Breakeven")
                ]
                
                # Combined timeline data
                timeline_chart_data = pd.DataFrame(original_timeline + new_timeline)
                
                # Create Gantt-like chart using a bar chart
                fig_timeline = px.timeline(
                    timeline_chart_data,
                    x_start="Start",
                    x_end="Finish",
                    y="Task",
                    color="Resource",
                    color_discrete_map={
                        "Implementation": COLOR_SCHEME["warning"],
                        "Breakeven": COLOR_SCHEME["positive"]
                    },
                    labels={"Task": "Scenario", "Start": "Month", "Finish": "Month"},
                    title="Implementation and Breakeven Timeline"
                )
                
                fig_timeline.update_yaxes(autorange="reversed")
                fig_timeline.update_layout(height=300)
                
                st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Cumulative cash flow chart
                st.markdown("#### Cumulative Cash Flow")
                
                # Generate monthly cash flows for both scenarios
                months = list(range(37))  # 0-36 months
                
                # Original cash flows
                original_cash_flows = [-original_dev_cost]  # Initial investment
                original_cum_cash_flow = [-original_dev_cost]
                
                # New cash flows
                new_cash_flows = [-new_dev_cost]  # Initial investment
                new_cum_cash_flow = [-new_dev_cost]
                
                # For each future month
                for month in range(1, 37):
                    # Original scenario
                    if month <= original_time:
                        original_cf = 0
                    else:
                        original_cf = original_monthly_net
                    
                    original_cash_flows.append(original_cf)
                    original_cum_cash_flow.append(original_cum_cash_flow[-1] + original_cf)
                    
                    # New scenario
                    if month <= new_time:
                        new_cf = 0
                    else:
                        new_cf = new_monthly_net
                    
                    new_cash_flows.append(new_cf)
                    new_cum_cash_flow.append(new_cum_cash_flow[-1] + new_cf)
                
                # Create cash flow chart
                fig_cash_flow = go.Figure()
                
                # Add original cumulative cash flow
                fig_cash_flow.add_trace(go.Scatter(
                    x=months,
                    y=original_cum_cash_flow,
                    name="Original",
                    mode="lines",
                    line=dict(width=3, color=COLOR_SCHEME["neutral"])
                ))
                
                # Add new cumulative cash flow
                fig_cash_flow.add_trace(go.Scatter(
                    x=months,
                    y=new_cum_cash_flow,
                    name="New",
                    mode="lines",
                    line=dict(width=3, color=COLOR_SCHEME["positive"])
                ))
                
                # Add horizontal line at y=0
                fig_cash_flow.add_shape(
                    type="line",
                    x0=0, y0=0,
                    x1=36, y1=0,
                    line=dict(color="black", width=1, dash="dash")
                )
                
                # Configure chart
                fig_cash_flow.update_layout(
                    title="Cumulative Cash Flow Comparison",
                    xaxis_title="Month",
                    yaxis_title="Cumulative Cash Flow ($)",
                    height=400,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    )
                )
                
                st.plotly_chart(fig_cash_flow, use_container_width=True)
        
        # Option to save as new scenario
        st.markdown("### Save What-If Scenario")
        
        new_name = st.text_input("New Scenario Name", 
                               value=f"{base_scenario_name} (What-If)", 
                               help="Name for the new scenario if you choose to save it")
        
        if st.button("Save as New Scenario"):
            # Get all the updated values
            development_cost = base_scenario['development_cost'] * (1 + st.session_state.whatif_params['development_cost_change']/100)
            unit_cost_change = base_scenario['unit_cost_change'] + st.session_state.whatif_params['unit_cost_change_adjust']
            reduction_rate = base_scenario['estimated_return_reduction'] + st.session_state.whatif_params['return_reduction_adjust']
            sales_increase = base_scenario['sales_increase'] + st.session_state.whatif_params['sales_increase_adjust']
            return_processing_cost = base_scenario['return_processing_cost'] * (1 + st.session_state.whatif_params['return_processing_change']/100)
            implementation_time = max(1, base_scenario['time_to_implement'] + st.session_state.whatif_params['implementation_time_change'])
            avg_price = base_scenario['avg_sale_price'] * (1 + st.session_state.whatif_params['price_change']/100)
            
            # Recalculate annual values based on new pricing
            annual_unit_sales = base_scenario['annual_unit_sales']
            annual_returns = base_scenario['annual_returns']
            
            # Call add_scenario with the new values
            success, message = optimizer.add_scenario(
                new_name, base_scenario['product_name'], base_scenario['product_category'],
                base_scenario['current_unit_sales'], avg_price, base_scenario['sales_channel'],
                base_scenario['current_returns'], base_scenario['upgrade_solution'], development_cost,
                unit_cost_change, base_scenario['current_unit_cost'], reduction_rate,
                sales_increase, base_scenario['product_lifecycle_stage'], annual_unit_sales,
                annual_returns, return_processing_cost, implementation_time
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

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <p class="logo-icon">🔄</p>
        <p class="logo-text">KaizenROI</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        - **Return Processing Cost**: Cost to handle each return (customer service, shipping, inspection)
        - **Return Reduction**: Estimated percentage reduction in returns after product upgrade
        - **Sales Increase**: Estimated percentage increase in sales from the upgrade
        - **Break-even**: Time to recover the development investment
        - **ROI**: Return on investment (net benefit / development cost)
        - **NPV**: Net Present Value of future cash flows at 10% discount rate
        - **Payback Period**: Total time to recoup investment including implementation time
        
        ### Key Formulas
        - Return Rate = (Returns / Sales) × 100%
        - Avoided Returns = Returns × Reduction Rate
        - Savings per Avoided Return = Sale Price + Return Processing Cost - Unit Cost
        - Additional Sales = Current Sales × Sales Increase %
        - Sales Benefit = Additional Sales × Margin per Unit
        - Net Benefit = Return Savings + Sales Benefit - Additional Costs
        - ROI = (Net Benefit / Development Cost) × 100%
        """)
    
    with st.expander("🔎 Understanding Product Upgrade ROI"):
        st.markdown("""
        ### Product Upgrade ROI Analysis
        
        Product upgrades typically impact ROI through two main mechanisms:
        
        1. **Return Rate Reduction**: Improving product quality, clearer descriptions, better size guides, etc. can significantly reduce costly returns.
        
        2. **Sales Growth**: Enhanced products often experience higher sales volumes through improved customer satisfaction, word-of-mouth, and review ratings.
        
        The most successful product upgrades positively impact both dimensions simultaneously, creating a compounding effect on ROI.
        
        ### Maximizing Product Upgrade ROI
        
        - **Low-Cost, High-Impact Improvements**: Prioritize changes that require minimal investment but address top return reasons.
        
        - **Focus on Production Efficiency**: When possible, design upgrades that reduce per-unit costs while improving quality.
        
        - **Accelerate Implementation**: Faster implementation means quicker payback and less opportunity cost.
        
        - **Target Growth-Stage Products**: Products in the growth phase of their lifecycle typically see the highest ROI from upgrades.
        """)
    
    # Footer
    st.markdown("---")
    st.caption("KaizenROI v2.0 | Product Upgrade ROI Analyzer")
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
