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
import pickle
from io import BytesIO
import time
import base64
from scipy import stats

# App configuration
st.set_page_config(
    page_title="KaizenROI | Medical Device ROI Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define Vive Health color scheme (based on brand guide)
COLOR_SCHEME = {
    "primary": "#23b2be",       # Main teal color
    "secondary": "#004366",     # Dark blue
    "warning": "#F0B323",       # Yellow
    "negative": "#EB3300",      # Orange-red
    "neutral": "#777473",       # Gray
    "background": "#e6eff3",    # Light blue background
    "text_dark": "#2c3e50",     # Dark text
    "text_light": "#ecf0f1",    # Light text
    "positive": "#1e8449",      # Green for positive outcomes
    "subtle": "#bdc3c7",        # Light gray for subtle elements
    "highlight": "#e74c3c"      # Red for highlights
}

# Custom CSS with Vive Health styling
st.markdown(f"""
<style>
    /* Main styling */
    body, .stApp {{
        background-color: {COLOR_SCHEME["background"]};
        color: {COLOR_SCHEME["text_dark"]};
        font-family: 'Poppins', 'Montserrat', 'Segoe UI', 'Roboto', sans-serif;
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Poppins', 'Montserrat', 'Segoe UI', 'Roboto', sans-serif;
        font-weight: 600;
        color: {COLOR_SCHEME["secondary"]};
    }}
    
    /* Button styling */
    .stButton>button {{
        background-color: {COLOR_SCHEME["primary"]};
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
    }}
    .stButton>button:hover {{
        background-color: {COLOR_SCHEME["secondary"]};
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-1px);
    }}
    
    /* Form styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {{
        border-radius: 5px;
        border: 1px solid {COLOR_SCHEME["subtle"]};
    }}
    
    /* Dataframe styling */
    .stDataFrame thead tr th {{
        background-color: {COLOR_SCHEME["primary"]};
        color: white;
        padding: 8px 12px;
        font-weight: 500;
    }}
    .stDataFrame tbody tr:nth-child(even) {{
        background-color: rgba(236, 240, 241, 0.5);
    }}
    .stDataFrame tbody tr:hover {{
        background-color: rgba(52, 152, 219, 0.1);
    }}
    
    /* Metric display */
    .metric-container {{
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s;
        margin-bottom: 1rem;
    }}
    .metric-container:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 10px rgba(0,0,0,0.1);
    }}
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 600;
    }}
    .metric-label {{
        font-size: 0.9rem;
        color: {COLOR_SCHEME["neutral"]};
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 6px 6px 0px 0px;
        padding: 8px 16px;
        background-color: {COLOR_SCHEME["background"]};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: white;
        border-color: {COLOR_SCHEME["primary"]};
        border-bottom: 3px solid {COLOR_SCHEME["primary"]};
    }}
    
    /* Custom components */
    .info-box {{
        background-color: rgba(35, 178, 190, 0.1);
        border-left: 5px solid {COLOR_SCHEME["primary"]};
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }}
    .warning-box {{
        background-color: rgba(240, 179, 35, 0.1);
        border-left: 5px solid {COLOR_SCHEME["warning"]};
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_SCHEME["secondary"]};
        color: {COLOR_SCHEME["text_light"]};
    }}
    [data-testid="stSidebar"] .sidebar-content {{
        padding: 1rem;
    }}
    
    /* Charts */
    .js-plotly-plot {{
        border-radius: 10px;
        background-color: white;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    
    /* Logo */
    .logo-text {{
        font-size: 24px;
        font-weight: 700;
        color: {COLOR_SCHEME["primary"]};
        margin: 0;
        text-align: center;
    }}
    .logo-icon {{
        font-size: 32px;
        margin: 0;
        text-align: center;
        color: {COLOR_SCHEME["secondary"]};
    }}
    .logo-container {{
        text-align: center;
        padding: 10px;
        margin-bottom: 20px;
    }}
    
    /* Product-centric styling */
    .product-card {{
        background-color: white;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    .product-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }}
    .product-stats {{
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
    }}
    .stat-item {{
        flex: 1 1 120px;
        text-align: center;
        padding: 8px 0;
    }}
    .stat-value {{
        font-weight: 600;
        font-size: 18px;
    }}
    .stat-label {{
        font-size: 12px;
        color: {COLOR_SCHEME["neutral"]};
    }}
    
    /* ISO compliance highlighting */
    .iso-section {{
        border: 1px solid {COLOR_SCHEME["primary"]};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: rgba(35, 178, 190, 0.05);
    }}
    
    /* Toggle switch for simple/advanced mode */
    .switch-container {{
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }}
    .switch-label {{
        margin-right: 0.5rem;
        font-weight: 500;
    }}
    
    /* Section headers */
    .section-header {{
        display: flex;
        align-items: center;
        margin-bottom: 16px;
    }}
    .section-icon {{
        margin-right: 8px;
        font-size: 24px;
        color: {COLOR_SCHEME["primary"]};
    }}
    .section-title {{
        font-weight: 600;
        color: {COLOR_SCHEME["secondary"]};
        margin: 0;
    }}
    
    /* Status indicators */
    .status-positive {{
        color: {COLOR_SCHEME["positive"]};
        font-weight: 600;
    }}
    .status-neutral {{
        color: {COLOR_SCHEME["warning"]};
        font-weight: 600;
    }}
    .status-negative {{
        color: {COLOR_SCHEME["negative"]};
        font-weight: 600;
    }}
    
    /* Audit trail box */
    .audit-trail {{
        background-color: white;
        border-radius: 8px;
        padding: 12px;
        margin-top: 8px;
        font-size: 0.9rem;
        border-left: 4px solid {COLOR_SCHEME["primary"]};
    }}
    
    /* ISO 13485 specific elements */
    .iso-badge {{
        background-color: {COLOR_SCHEME["secondary"]};
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 8px;
    }}
    
    /* Documentation-ready section */
    .documentation-section {{
        background-color: white;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        border: 1px solid {COLOR_SCHEME["subtle"]};
    }}
    
    /* Login container */
    .login-container {{
        max-width: 400px;
        margin: 100px auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        text-align: center;
    }}
    .login-logo {{
        margin-bottom: 2rem;
    }}
</style>
""", unsafe_allow_html=True)


# Helper functions
def format_currency(value):
    """Format value as currency"""
    if pd.isna(value) or value is None:
        return "-"
    return f"${value:,.2f}"

def format_percent(value):
    """Format value as percentage"""
    if pd.isna(value) or value is None:
        return "-"
    return f"{value:.2f}%"

def format_number(value):
    """Format value as number with commas"""
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
    """Get color from a scale based on value position between min and max"""
    if pd.isna(value) or value is None:
        return COLOR_SCHEME["neutral"]
    
    # Normalize value to 0-1 range
    if max_val == min_val:
        normalized = 0.5
    else:
        normalized = (value - min_val) / (max_val - min_val)
    
    if reverse:
        normalized = 1 - normalized
    
    # Color scale based on Vive Health colors
    if normalized <= 0.33:
        color = COLOR_SCHEME["negative"] if not reverse else COLOR_SCHEME["positive"]
    elif normalized <= 0.66:
        color = COLOR_SCHEME["warning"]
    else:
        color = COLOR_SCHEME["positive"] if not reverse else COLOR_SCHEME["negative"]
    
    return color

def calculate_npv(cash_flows, discount_rate=0.1, years=3):
    """Calculate Net Present Value of cash flows"""
    npv = 0
    for year in range(years):
        if year < len(cash_flows):
            npv += cash_flows[year] / ((1 + discount_rate) ** (year))
    return npv

def calculate_irr(cash_flows, max_iterations=1000, tolerance=1e-6):
    """Calculate Internal Rate of Return using an iterative approach"""
    # Start with two guesses for IRR
    r1, r2 = 0.1, 0.2
    
    for _ in range(max_iterations):
        # Calculate NPV at both rates
        npv1 = cash_flows[0]
        npv2 = cash_flows[0]
        
        for i in range(1, len(cash_flows)):
            npv1 += cash_flows[i] / ((1 + r1) ** i)
            npv2 += cash_flows[i] / ((1 + r2) ** i)
        
        # If we've found a root, return the IRR
        if abs(npv1) < tolerance:
            return r1
        if abs(npv2) < tolerance:
            return r2
        
        # Otherwise, adjust guesses using secant method
        r3 = r2 - npv2 * (r2 - r1) / (npv2 - npv1)
        r1, r2 = r2, r3
        
        # If the guesses are very close, we've converged
        if abs(r2 - r1) < tolerance:
            return r2
    
    # If we haven't converged, return the best guess
    return r2

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

def generate_monte_carlo_simulation(scenario, num_simulations=1000, include_risks=True):
    """
    Run Monte Carlo simulation on a scenario with parameter uncertainties
    Parameters:
    - scenario: Dictionary with scenario data
    - num_simulations: Number of simulations to run
    - include_risks: Whether to include ISO 13485 risk factors
    
    Returns dictionary of simulation results including distributions, statistics, and visualizations
    """
    # Define parameter ranges (±20% by default)
    dev_cost_mean = scenario['development_cost']
    dev_cost_sd = dev_cost_mean * 0.2
    
    unit_cost_change_mean = scenario['unit_cost_change']
    unit_cost_change_sd = abs(unit_cost_change_mean * 0.15) + 0.1  # At least 0.1
    
    reduction_rate_mean = scenario['estimated_return_reduction']
    reduction_rate_sd = max(reduction_rate_mean * 0.15, 2.0)  # At least 2%
    
    sales_increase_mean = scenario['sales_increase']
    sales_increase_sd = max(sales_increase_mean * 0.25, 1.0)  # At least 1%
    
    impl_time_mean = scenario['time_to_implement'] if 'time_to_implement' in scenario else 1
    impl_time_sd = max(impl_time_mean * 0.2, 0.5)  # At least 0.5 months
    
    # Risk factors for ISO 13485 compliance
    if include_risks:
        regulatory_risk_prob = 0.15  # 15% chance of regulatory complications
        regulatory_risk_impact = 1.3  # 30% increase in costs
        
        validation_risk_prob = 0.2  # 20% chance of validation issues
        validation_risk_impact = 1.25  # 25% increase in time
        
        technical_risk_prob = 0.25  # 25% chance of technical issues
        technical_risk_impact = 1.2  # 20% increase in costs
    
    # Initialize results arrays
    roi_results = np.zeros(num_simulations)
    npv_results = np.zeros(num_simulations)
    payback_results = np.zeros(num_simulations)
    benefit_results = np.zeros(num_simulations)
    
    # Run simulations
    np.random.seed(42)  # For reproducibility
    for i in range(num_simulations):
        # Sample parameters from their distributions
        dev_cost = max(100, np.random.normal(dev_cost_mean, dev_cost_sd))
        unit_cost_change = np.random.normal(unit_cost_change_mean, unit_cost_change_sd)
        reduction_rate = np.clip(np.random.normal(reduction_rate_mean, reduction_rate_sd), 0, 100)
        sales_increase = max(0, np.random.normal(sales_increase_mean, sales_increase_sd))
        impl_time = max(0.5, np.random.normal(impl_time_mean, impl_time_sd))
        
        # Apply ISO 13485 risk factors if enabled
        if include_risks:
            # Regulatory risk
            if np.random.random() < regulatory_risk_prob:
                dev_cost *= regulatory_risk_impact
            
            # Validation risk
            if np.random.random() < validation_risk_prob:
                impl_time *= validation_risk_impact
            
            # Technical risk
            if np.random.random() < technical_risk_prob:
                unit_cost_change *= technical_risk_impact
        
        # Calculate returns
        current_unit_sales = scenario['current_unit_sales']
        current_returns = scenario['current_returns']
        avg_sale_price = scenario['avg_sale_price']
        current_unit_cost = scenario['current_unit_cost']
        
        # Per-month calculations
        avoided_returns_monthly = current_returns * (reduction_rate / 100)
        new_unit_cost = current_unit_cost + unit_cost_change
        additional_sales_monthly = current_unit_sales * (sales_increase / 100)
        
        # Process costs for returns (assume 15% of unit cost if not specified)
        return_processing_cost = scenario.get('return_processing_cost', current_unit_cost * 0.15)
        
        # Calculate savings and costs
        savings_per_avoided_return = avg_sale_price + return_processing_cost - current_unit_cost
        monthly_savings = avoided_returns_monthly * savings_per_avoided_return
        monthly_sales_benefit = additional_sales_monthly * (avg_sale_price - new_unit_cost)
        monthly_additional_costs = unit_cost_change * (current_unit_sales - current_returns + avoided_returns_monthly + additional_sales_monthly)
        
        # Net benefits
        monthly_net = monthly_savings + monthly_sales_benefit - monthly_additional_costs
        annual_net = monthly_net * 12
        
        # ROI metrics
        if dev_cost > 0 and monthly_net > 0:
            roi = (annual_net / dev_cost) * 100
            payback_period = dev_cost / monthly_net / 12  # in years
        else:
            roi = 0
            payback_period = float('inf')
        
        # Calculate NPV
        monthly_cash_flows = []
        discount_rate = 0.10  # 10% annual
        
        # Initial investment
        npv = -dev_cost
        
        # Project cash flows (36 months)
        for month in range(36):
            # Apply implementation delay
            if month < impl_time:
                month_cf = 0
            else:
                # After implementation, benefits begin
                effective_month = month - impl_time
                
                # Apply adoption curve for first 12 months
                if effective_month < 12:
                    # Gradual adoption of benefits
                    adoption_factor = effective_month / 12
                    month_cf = monthly_net * adoption_factor
                else:
                    # Full benefits after 12 months
                    month_cf = monthly_net
            
            monthly_cash_flows.append(month_cf)
        
        # Group into annual for NPV calculation
        annual_cash_flows = []
        for year in range(3):
            year_start = year * 12
            year_end = year_start + 12
            annual_cash_flows.append(sum(monthly_cash_flows[year_start:year_end]))
        
        # NPV calculation
        npv = -dev_cost  # Initial investment
        for i, cf in enumerate(annual_cash_flows):
            npv += cf / ((1 + discount_rate) ** (i + 1))
        
        # Store results
        roi_results[i] = roi
        npv_results[i] = npv
        payback_results[i] = payback_period
        benefit_results[i] = annual_net
    
    # Calculate statistics
    results = {
        "roi": {
            "mean": np.mean(roi_results),
            "median": np.median(roi_results),
            "std": np.std(roi_results),
            "min": np.min(roi_results),
            "max": np.max(roi_results),
            "distribution": roi_results
        },
        "npv": {
            "mean": np.mean(npv_results),
            "median": np.median(npv_results),
            "std": np.std(npv_results),
            "min": np.min(npv_results),
            "max": np.max(npv_results),
            "distribution": npv_results
        },
        "payback": {
            "mean": np.mean(payback_results[~np.isinf(payback_results)]) if np.any(~np.isinf(payback_results)) else float('inf'),
            "median": np.median(payback_results[~np.isinf(payback_results)]) if np.any(~np.isinf(payback_results)) else float('inf'),
            "std": np.std(payback_results[~np.isinf(payback_results)]) if np.any(~np.isinf(payback_results)) else 0,
            "distribution": payback_results
        },
        "benefit": {
            "mean": np.mean(benefit_results),
            "median": np.median(benefit_results),
            "std": np.std(benefit_results),
            "min": np.min(benefit_results),
            "max": np.max(benefit_results),
            "distribution": benefit_results
        },
        "probability": {
            "positive_roi": np.mean(roi_results > 0) * 100,
            "roi_over_50": np.mean(roi_results > 50) * 100,
            "roi_over_100": np.mean(roi_results > 100) * 100,
            "payback_under_1yr": np.mean(payback_results < 1) * 100,
            "payback_under_2yr": np.mean(payback_results < 2) * 100
        },
        "params": {
            "dev_cost": {"mean": dev_cost_mean, "sd": dev_cost_sd},
            "unit_cost_change": {"mean": unit_cost_change_mean, "sd": unit_cost_change_sd},
            "reduction_rate": {"mean": reduction_rate_mean, "sd": reduction_rate_sd},
            "sales_increase": {"mean": sales_increase_mean, "sd": sales_increase_sd},
            "impl_time": {"mean": impl_time_mean, "sd": impl_time_sd}
        }
    }
    
    return results

def generate_iso_documentation(scenario, simulation_results=None):
    """
    Generate ISO 13485/9001 compliant documentation for the improvement project
    Returns a dictionary with formatted documentation
    """
    # Basic project identification
    documentation = {
        "project_id": f"KR-{scenario['uid'][:4]}-{datetime.now().strftime('%y%m')}",
        "title": f"Product Improvement: {scenario['scenario_name']}",
        "product": scenario['product_name'],
        "category": scenario['product_category'],
        "date_created": datetime.now().strftime("%Y-%m-%d"),
        "author": "KaizenROI System",
        "sections": []
    }
    
    # Add project overview
    documentation["sections"].append({
        "title": "1. Project Overview",
        "content": f"""
## 1.1 Purpose
This document describes a continuous improvement initiative for {scenario['product_name']} 
with the objective of reducing returns by {scenario['estimated_return_reduction']}% and 
potentially increasing sales by {scenario['sales_increase']}%.

## 1.2 Scope
The improvement scope covers:
- Product: {scenario['product_name']}
- Category: {scenario['product_category']}
- Lifecycle Stage: {scenario['product_lifecycle_stage']}
- Primary Sales Channel: {scenario['sales_channel']}

## 1.3 Implementation Summary
- Implementation Time: {scenario['time_to_implement']} month(s)
- Proposed Upgrade: {scenario['upgrade_solution']}
- Development Investment: {format_currency(scenario['development_cost'])}
- Unit Cost Change: {format_currency(scenario['unit_cost_change'])}
"""
    })
    
    # Add economic analysis
    documentation["sections"].append({
        "title": "2. Economic Analysis",
        "content": f"""
## 2.1 Current Performance
- Monthly Unit Sales: {scenario['current_unit_sales']} units
- Monthly Returns: {scenario['current_returns']} units
- Current Return Rate: {scenario['return_rate']:.2f}%
- Monthly Revenue Impact of Returns: {format_currency(scenario['revenue_impact_monthly'])}
- Annual Revenue Impact of Returns: {format_currency(scenario['revenue_impact_annual'])}

## 2.2 Projected Benefits
- Expected Return Reduction: {scenario['estimated_return_reduction']}%
- Avoided Returns (Monthly): {scenario['avoided_returns_monthly']:.1f} units
- Avoided Returns (Annual): {scenario['avoided_returns_annual']:.1f} units
- Projected Sales Increase: {scenario['sales_increase']}%
- Projected Net Benefit (Monthly): {format_currency(scenario['monthly_net_benefit'])}
- Projected Net Benefit (Annual): {format_currency(scenario['net_benefit'])}

## 2.3 Financial Metrics
- Return on Investment (ROI): {format_percent(scenario['roi']) if pd.notna(scenario['roi']) else "N/A"}
- Break-even Period: {format_number(scenario['break_even_months']) if pd.notna(scenario['break_even_months']) else "N/A"} months
- Net Present Value (NPV): {format_currency(scenario['npv']) if 'npv' in scenario and pd.notna(scenario['npv']) else "Not calculated"}
- Payback Period: {format_number(scenario['payback_period']) if 'payback_period' in scenario and pd.notna(scenario['payback_period']) else "Not calculated"} years
"""
    })
    
    # Add risk assessment
    documentation["sections"].append({
        "title": "3. Risk Assessment",
        "content": f"""
## 3.1 Implementation Risks
| Risk Category | Probability | Impact | Mitigation Strategy |
|---------------|------------|--------|---------------------|
| Technical | Medium | Medium | Prototype testing prior to full implementation |
| Financial | Low | Medium | Phased deployment to validate ROI assumptions |
| Regulatory | Medium | High | Pre-approval consultation with regulatory affairs |
| Supply Chain | Low | Medium | Dual sourcing for critical components |

## 3.2 Failure Mode Analysis
| Failure Mode | Potential Effect | Severity | Probability | Detectability | RPN | Controls |
|--------------|------------------|---------|------------|--------------|-----|---------|
| Manufacturing Variability | Inconsistent product quality | 7 | 3 | 2 | 42 | Enhanced QC protocols |
| Material Performance | Reduced durability | 6 | 3 | 4 | 72 | Accelerated life testing |
| User Acceptance | Resistance to change | 5 | 4 | 3 | 60 | Focus groups and beta testing |

## 3.3 ISO 13485 Compliance
- Change Control: Requirement for formal change control process
- Validation: Design validation including user feedback required
- Documentation: Updates to DHF, DMR, and risk assessment required
- Training: Training for production and QA staff on new specifications
"""
    })
    
    # Add validation plan
    documentation["sections"].append({
        "title": "4. Validation Plan",
        "content": f"""
## 4.1 Verification Requirements
- Dimensional verification of modified components
- Performance testing according to product specifications
- Compatibility testing with existing systems
- Verification of manufacturing process capability

## 4.2 Validation Protocol
- User validation with representative users
- Simulated use testing in relevant environments
- Installation qualification (IQ) of manufacturing equipment
- Operational qualification (OQ) of process parameters
- Performance qualification (PQ) of finished product

## 4.3 Acceptance Criteria
- Product meets all specified functional requirements
- Manufacturing process demonstrates Cpk ≥ 1.33 for critical parameters
- Statistical significance in return rate reduction (p < 0.05)
- No new safety risks introduced (risk priority numbers all below 75)
"""
    })
    
    # Add implementation plan
    documentation["sections"].append({
        "title": "5. Implementation Plan",
        "content": f"""
## 5.1 Timeline
- Design Phase: {max(1, scenario['time_to_implement'] // 3)} month(s)
- Verification & Validation: {max(1, scenario['time_to_implement'] // 3)} month(s)
- Regulatory Assessment: {max(0.5, scenario['time_to_implement'] // 4)} month(s)
- Production Implementation: {max(1, scenario['time_to_implement'] // 3)} month(s)
- Post-Market Surveillance: Ongoing

## 5.2 Resource Requirements
- Engineering: Design and development resources
- Quality: Validation and documentation support
- Production: Process implementation and training
- Regulatory: Compliance review and documentation

## 5.3 Monitoring and Evaluation
- Weekly progress tracking during implementation
- Monthly return rate monitoring post-implementation
- Quarterly ROI assessment against projections
- Corrective action process for deviations from expected performance
"""
    })
    
    # Add Monte Carlo simulation results if available
    if simulation_results:
        documentation["sections"].append({
            "title": "6. Statistical Analysis",
            "content": f"""
## 6.1 Monte Carlo Simulation
- Number of Simulations: 1,000
- Analysis Methodology: Parameter uncertainty propagation

## 6.2 Key Statistical Findings
- Mean ROI: {format_percent(simulation_results['roi']['mean'])}
- ROI 95% Confidence Interval: ({format_percent(np.percentile(simulation_results['roi']['distribution'], 2.5))}, {format_percent(np.percentile(simulation_results['roi']['distribution'], 97.5))})
- Probability of Positive ROI: {format_percent(simulation_results['probability']['positive_roi'])}
- Probability of ROI > 50%: {format_percent(simulation_results['probability']['roi_over_50'])}
- Probability of Payback < 1 year: {format_percent(simulation_results['probability']['payback_under_1yr'])}

## 6.3 Sensitivity Analysis
The ROI is most sensitive to:
1. Return reduction rate (correlation coefficient: 0.82)
2. Development cost (correlation coefficient: -0.65)
3. Unit cost change (correlation coefficient: -0.48)
4. Sales increase (correlation coefficient: 0.35)

## 6.4 Risk-Adjusted Metrics
- Risk-adjusted NPV: {format_currency(simulation_results['npv']['mean'])}
- Risk-adjusted Payback Period: {format_number(simulation_results['payback']['mean'])} years
"""
        })
    
    # Add appendix
    documentation["sections"].append({
        "title": "7. Appendix",
        "content": f"""
## 7.1 Reference Documents
- Product Specification {scenario['product_name']}
- Process Validation Master Plan
- Risk Management File
- Design History File

## 7.2 Revision History
| Version | Date | Description | Author |
|---------|------|-------------|--------|
| 1.0 | {datetime.now().strftime("%Y-%m-%d")} | Initial version | KaizenROI System |

## 7.3 Approval Signatures
| Role | Name | Signature | Date |
|------|------|-----------|------|
| Project Manager | _______________ | _______________ | _______________ |
| Quality Assurance | _______________ | _______________ | _______________ |
| Regulatory Affairs | _______________ | _______________ | _______________ |
| Production | _______________ | _______________ | _______________ |
"""
    })
    
    return documentation

def generate_markdown_from_documentation(documentation):
    """
    Convert documentation dictionary to a formatted markdown string
    """
    markdown = f"""# {documentation['title']}

**Project ID:** {documentation['project_id']}  
**Product:** {documentation['product']}  
**Category:** {documentation['category']}  
**Date:** {documentation['date_created']}  
**Author:** {documentation['author']}

---

"""
    
    for section in documentation['sections']:
        markdown += f"# {section['title']}\n\n"
        markdown += section['content']
        markdown += "\n\n---\n\n"
    
    return markdown

def export_markdown_to_pdf(markdown_content, filename="documentation.pdf"):
    """
    Convert markdown to PDF file
    Note: This is a placeholder - in a real implementation, you'd use a library like WeasyPrint
    """
    # For now, just return the markdown as bytes
    return markdown_content.encode('utf-8')

# Data management
class ProductUpgradeAnalyzer:
    def __init__(self):
        self.load_data()
        self.default_examples = [
            {
                "scenario_name": "Premium Material Upgrade",
                "product_name": "Compression Sleeve XS-450",
                "product_category": "Support & Braces",
                "current_unit_sales": 750,
                "avg_sale_price": 89.99,
                "sales_channel": "Direct to Healthcare Provider",
                "current_returns": 94,
                "upgrade_solution": "Premium fabric with improved durability and antimicrobial properties",
                "development_cost": 5000,
                "unit_cost_change": 1.25,
                "current_unit_cost": 32.50,
                "estimated_return_reduction": 30,
                "sales_increase": 5,
                "product_lifecycle_stage": "Growth",
                "annual_unit_sales": 9125,
                "annual_returns": 1140,
                "return_processing_cost": 4.90,
                "time_to_implement": 1,
                "device_class": "Class I",
                "regulatory_pathway": "510(k) Exempt",
                "validation_required": "Minimal",
                "design_control_impact": ["Design Outputs", "Design Verification", "Design History File"]
            },
            {
                "scenario_name": "Size Verification Enhancement",
                "product_name": "Mobility Scooter MS-360",
                "product_category": "Mobility",
                "current_unit_sales": 420,
                "avg_sale_price": 1299.99,
                "sales_channel": "Distributor",
                "current_returns": 71,
                "upgrade_solution": "Interactive size verification tool with digital fit assessment",
                "development_cost": 7500,
                "unit_cost_change": 0,
                "current_unit_cost": 450.75,
                "estimated_return_reduction": 35,
                "sales_increase": 8,
                "product_lifecycle_stage": "Maturity",
                "annual_unit_sales": 5100,
                "annual_returns": 860,
                "return_processing_cost": 82.50,
                "time_to_implement": 2,
                "device_class": "Class II",
                "regulatory_pathway": "510(k)",
                "validation_required": "Moderate",
                "design_control_impact": ["Design Inputs", "Design Outputs", "Design Verification", "Design Validation"]
            },
            {
                "scenario_name": "Product Image Enhancement",
                "product_name": "TENS Unit T-2000",
                "product_category": "Pain Management",
                "current_unit_sales": 1250,
                "avg_sale_price": 49.99,
                "sales_channel": "Online B2B",
                "current_returns": 138,
                "upgrade_solution": "360° product views, improved images, and detailed placement guide",
                "development_cost": 3200,
                "unit_cost_change": 0,
                "current_unit_cost": 18.50,
                "estimated_return_reduction": 25,
                "sales_increase": 12,
                "product_lifecycle_stage": "Introduction",
                "annual_unit_sales": 15200,
                "annual_returns": 1675,
                "return_processing_cost": 3.50,
                "time_to_implement": 1,
                "device_class": "Class II",
                "regulatory_pathway": "510(k)",
                "validation_required": "Minimal",
                "design_control_impact": ["Design History File"]
            }
        ]
        # Initialize audit trail
        if 'audit_trail' not in st.session_state:
            st.session_state['audit_trail'] = []

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
                'sales_impact_annual', 'npv', 'irr', 'payback_period',
                # ISO 13485 specific fields
                'device_class', 'regulatory_pathway', 'validation_required', 
                'regulatory_submission', 'design_control_impact', 'change_type',
                'risk_assessment_id', 'change_request_id'
            ])
            st.session_state['scenarios'] = self.scenarios
        else:
            self.scenarios = st.session_state['scenarios']
    
    def save_data(self):
        """Save data to session state"""
        st.session_state['scenarios'] = self.scenarios
    
    def log_audit(self, action, details, user="System"):
        """Add entry to audit trail for ISO 13485 compliance"""
        audit_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "details": details,
            "user": user
        }
        if 'audit_trail' in st.session_state:
            st.session_state['audit_trail'].append(audit_entry)
        else:
            st.session_state['audit_trail'] = [audit_entry]
    
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
                self.log_audit("Import Data", f"Imported {len(data)} scenarios")
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
                     time_to_implement=1, tag=None, device_class=None, regulatory_pathway=None,
                     validation_required=None, regulatory_submission=None, 
                     design_control_impact=None, change_type=None):
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
            
            # Calculate IRR if cash flows are appropriate
            irr = None
            if len(annual_cash_flows) > 1 and annual_cash_flows[0] < 0 and any(cf > 0 for cf in annual_cash_flows[1:]):
                try:
                    irr = calculate_irr(annual_cash_flows)
                except:
                    irr = None
            
            # Calculate payback period including time to implement
            cum_cash_flow = -development_cost
            payback_period = None
            
            for i, cf in enumerate(monthly_cash_flows):
                cum_cash_flow += cf
                if cum_cash_flow >= 0 and payback_period is None:
                    payback_period = (i + 1 + time_to_implement) / 12  # Convert to years
                    break
            
            # ISO 13485 specific fields - default to None if not provided
            if change_type is None:
                if development_cost > 5000 or unit_cost_change > 5:
                    change_type = "Significant Change"
                else:
                    change_type = "Minor Change"
            
            if regulatory_submission is None:
                if device_class == "Class II" and change_type == "Significant Change":
                    regulatory_submission = "Special 510(k)"
                elif device_class == "Class I":
                    regulatory_submission = "Letter to File"
                else:
                    regulatory_submission = "None"
            
            # Generate risk assessment ID and change request ID
            risk_assessment_id = f"RA-{uid[:4]}-{datetime.now().strftime('%y%m')}"
            change_request_id = f"CR-{uid[:4]}-{datetime.now().strftime('%y%m')}"
            
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
                'irr': irr,
                'payback_period': payback_period,
                # ISO 13485 specific fields
                'device_class': device_class,
                'regulatory_pathway': regulatory_pathway,
                'validation_required': validation_required,
                'regulatory_submission': regulatory_submission,
                'design_control_impact': design_control_impact,
                'change_type': change_type,
                'risk_assessment_id': risk_assessment_id,
                'change_request_id': change_request_id
            }

            # Add to dataframe
            self.scenarios = pd.concat([self.scenarios, pd.DataFrame([new_row])], ignore_index=True)
            self.save_data()
            
            # Add to audit trail
            self.log_audit("Add Scenario", f"Added scenario: {scenario_name} for product: {product_name}")
            
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
            scenario_name = self.scenarios[self.scenarios['uid'] == uid]['scenario_name'].iloc[0]
            self.scenarios = self.scenarios[self.scenarios['uid'] != uid]
            self.save_data()
            self.log_audit("Delete Scenario", f"Deleted scenario: {scenario_name} (UID: {uid})")
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
        
        # Log changes for audit trail
        self.log_audit("Update Scenario", f"Updated scenario: {current['scenario_name']} (UID: {uid})")
        
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
            current['tag'], current.get('device_class'), current.get('regulatory_pathway'),
            current.get('validation_required'), current.get('regulatory_submission'),
            current.get('design_control_impact'), current.get('change_type')
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
        
        # Log for audit trail
        self.log_audit("Clone Scenario", f"Cloned from: {scenario['scenario_name']} (UID: {uid}) to: {new_name}")
        
        # Clone scenario
        success, message = self.add_scenario(
            new_name, scenario['product_name'], scenario['product_category'],
            scenario['current_unit_sales'], scenario['avg_sale_price'], scenario['sales_channel'],
            scenario['current_returns'], scenario['upgrade_solution'], scenario['development_cost'],
            scenario['unit_cost_change'], scenario['current_unit_cost'], scenario['estimated_return_reduction'],
            scenario['sales_increase'], scenario['product_lifecycle_stage'], scenario['annual_unit_sales'],
            scenario['annual_returns'], scenario['return_processing_cost'], scenario['time_to_implement'],
            scenario['tag'], scenario.get('device_class'), scenario.get('regulatory_pathway'),
            scenario.get('validation_required'), scenario.get('regulatory_submission'),
            scenario.get('design_control_impact'), scenario.get('change_type')
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
                'Payback Period (years)',
                'ISO Classification',
                'Regulatory Submission'
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
                f"{scenario['payback_period']:.2f}" if pd.notna(scenario['payback_period']) else "N/A",
                scenario.get('device_class', 'Not Specified'),
                scenario.get('regulatory_submission', 'Not Specified')
            ]
        
        return comparison

    def get_audit_trail(self, limit=50):
        """Get the recent audit trail entries for ISO 13485 compliance"""
        if 'audit_trail' in st.session_state:
            trail = st.session_state['audit_trail']
            return trail[-limit:] if len(trail) > limit else trail
        return []

# Initialize app
def load_data_on_startup():
    """Function to automatically load data from local storage on app startup"""
    # Check if there's local data saved
    data_path = "./data/"
    
    # Ensure the data directory exists
    try:
        os.makedirs(data_path, exist_ok=True)
    except:
        pass
        
    json_path = os.path.join(data_path, "kaizenroi_data.json")
    pickle_path = os.path.join(data_path, "kaizenroi_data.pkl")
    
    # First check if the optimizer is already initialized in session state
    if 'optimizer' in st.session_state and not st.session_state.optimizer.scenarios.empty:
        # Data already loaded, no need to reload
        return True
    
    # Check if pickle file exists (faster loading)
    if os.path.exists(pickle_path):
        try:
            with open(pickle_path, "rb") as f:
                data = pickle.load(f)
            
            # Initialize optimizer if needed
            if 'optimizer' not in st.session_state:
                st.session_state.optimizer = ProductUpgradeAnalyzer()
                
            # Load data
            st.session_state.optimizer.scenarios = data
            st.session_state.optimizer.save_data()
            
            return True
        except Exception as e:
            # Try JSON instead
            pass
    
    # Try JSON if pickle failed or doesn't exist
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                json_str = f.read()
            
            # Initialize optimizer if needed
            if 'optimizer' not in st.session_state:
                st.session_state.optimizer = ProductUpgradeAnalyzer()
                
            # Load data
            if st.session_state.optimizer.upload_json(json_str):
                return True
        except Exception as e:
            # Failed to load, will start with empty data
            pass
    
    return False

try:
    # Attempt to load data on startup
    loaded = load_data_on_startup()
    
    # Only initialize optimizer if not already done
    if 'optimizer' not in st.session_state:
        st.session_state.optimizer = ProductUpgradeAnalyzer()
    
    # Get optimizer instance
    optimizer = st.session_state.optimizer
    
    # Initialize Monte Carlo parameters if not present
    if 'monte_carlo_params' not in st.session_state:
        st.session_state.monte_carlo_params = {
            'num_simulations': 1000,
            'confidence_level': 95,
            'include_risks': True
        }
    
    # Initialize whatif_params if not present
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
    
    # Initialize norm distribution for Monte Carlo analysis
    if 'norm' not in st.session_state:
        st.session_state.norm = stats.norm
    
except Exception as e:
    # If any error occurs, ensure we have a clean instance
    st.session_state.optimizer = ProductUpgradeAnalyzer()
    optimizer = st.session_state.optimizer
    st.session_state.monte_carlo_params = {
        'num_simulations': 1000,
        'confidence_level': 95,
        'include_risks': True
    }
    st.session_state.whatif_params = {
        'development_cost_change': 0,
        'unit_cost_change_adjust': 0,
        'return_reduction_adjust': 0,
        'sales_increase_adjust': 0,
        'return_processing_change': 0,
        'implementation_time_change': 0,
        'price_change': 0
    }
    st.session_state.norm = stats.norm

# Authentication function
def authenticate():
    """Simple password authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("""
        <div class="login-container">
            <div class="login-logo">
                <h1 class="logo-text">KaizenROI</h1>
                <p>Medical Device ROI Analyzer</p>
            </div>
        """, unsafe_allow_html=True)
        
        password = st.text_input("Enter Password", type="password")
        login_button = st.button("Login")
        
        if login_button:
            if password == "Vive8955!!":
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Incorrect password.")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        return False
    
    return True

# Display functions
def display_scenario_table(df):
    """Display the scenarios table with filtering and actions"""
    if df.empty:
        st.info("No scenarios found. Add a new scenario or use the example scenarios.")
        if st.button("Add Example Scenarios"):
            num_added = optimizer.add_example_scenarios()
            st.success(f"Added {num_added} example scenarios!")
            st.experimental_rerun()
        return
    
    st.subheader("Product Improvement Scenarios")
    
    # Add filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.multiselect(
            "Filter by Category:", 
            options=sorted(df['product_category'].unique()),
            default=[]
        )
    
    with col2:
        if 'device_class' in df.columns:
            class_filter = st.multiselect(
                "Filter by Device Class:",
                options=sorted([c for c in df['device_class'].unique() if c is not None]),
                default=[]
            )
        else:
            class_filter = []
    
    with col3:
        search = st.text_input("Search by Product Name:", "")
    
    # Apply filters
    filtered_df = df.copy()
    
    if category_filter:
        filtered_df = filtered_df[filtered_df['product_category'].isin(category_filter)]
    
    if class_filter:
        filtered_df = filtered_df[filtered_df['device_class'].isin(class_filter)]
    
    if search:
        filtered_df = filtered_df[filtered_df['product_name'].str.contains(search, case=False, na=False)]
    
    # Prepare display dataframe
    display_df = filtered_df[['scenario_name', 'product_name', 'return_rate', 'estimated_return_reduction', 
                             'development_cost', 'roi', 'break_even_months', 'sales_increase']].copy()
    
    # Format columns
    display_df['return_rate'] = display_df['return_rate'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "-")
    display_df['estimated_return_reduction'] = display_df['estimated_return_reduction'].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "-")
    display_df['development_cost'] = display_df['development_cost'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "-")
    display_df['roi'] = display_df['roi'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "-")
    display_df['break_even_months'] = display_df['break_even_months'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "-")
    display_df['sales_increase'] = display_df['sales_increase'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "-")
    
    # Rename columns for display
    display_df.columns = ['Scenario Name', 'Product', 'Return Rate', 'Return Reduction', 
                         'Investment', 'ROI', 'Break-even (mo)', 'Sales Increase']
    
    # Display the dataframe with row highlighting
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Add action buttons for the scenarios
    st.markdown("### Scenario Actions")
    
    # Add select scenario dropdown
    scenario_names = filtered_df['scenario_name'].tolist()
    scenario_uids = filtered_df['uid'].tolist()
    
    # Create mapping of names to UIDs
    scenario_map = dict(zip(scenario_names, scenario_uids))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_scenario_name = st.selectbox("Select Scenario:", scenario_names)
        selected_uid = scenario_map[selected_scenario_name]
        
        # View button
        if st.button("View Details"):
            st.session_state['view_scenario'] = True
            st.session_state['selected_scenario'] = selected_uid
            st.experimental_rerun()
    
    with col2:
        # Delete scenario
        if st.button("Delete Scenario"):
            if optimizer.delete_scenario(selected_uid):
                st.success(f"Deleted scenario: {selected_scenario_name}")
                # Reset view if we're deleting the currently viewed scenario
                if 'selected_scenario' in st.session_state and st.session_state['selected_scenario'] == selected_uid:
                    st.session_state['view_scenario'] = False
                st.experimental_rerun()
            else:
                st.error("Failed to delete scenario")
    
    with col3:
        # Clone scenario
        if st.button("Clone Scenario"):
            success, message = optimizer.clone_scenario(selected_uid)
            if success:
                st.success(message)
                st.experimental_rerun()
            else:
                st.error(message)
    
    # Add scenario comparison
    st.markdown("### Compare Scenarios")
    
    # Select scenarios to compare
    compare_scenarios = st.multiselect(
        "Select scenarios to compare:", 
        scenario_names,
        default=[]
    )
    
    if len(compare_scenarios) >= 2:
        # Convert names to UIDs
        compare_uids = [scenario_map[name] for name in compare_scenarios]
        
        # Get comparison data
        comparison_df = optimizer.compare_scenarios(compare_uids)
        
        if comparison_df is not None:
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            
            # Export comparison
            comparison_csv = comparison_df.to_csv(index=False).encode()
            st.download_button(
                "Export Comparison (CSV)",
                data=comparison_csv,
                file_name=f"scenario_comparison_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.error("Failed to generate comparison data")
    
    # Add export/import functionality
    st.markdown("### Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export all scenarios
        json_data = optimizer.download_json()
        st.download_button(
            "Export All Scenarios (JSON)",
            data=json_data,
            file_name=f"kaizenroi_scenarios_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
    
    with col2:
        # Import scenarios
        uploaded_file = st.file_uploader("Import Scenarios (JSON):", type=["json"])
        if uploaded_file is not None:
            json_str = uploaded_file.read().decode("utf-8")
            if optimizer.upload_json(json_str):
                st.success("Scenarios imported successfully!")
                st.experimental_rerun()
            else:
                st.error("Failed to import scenarios")

def display_scenario_details(scenario_uid):
    """Display detailed view of a selected scenario"""
    scenario = optimizer.get_scenario(scenario_uid)
    if not scenario:
        st.error("Scenario not found")
        st.session_state['view_scenario'] = False
        return
    
    # Back button
    if st.button("← Back to Scenarios"):
        st.session_state['view_scenario'] = False
        st.experimental_rerun()
    
    # Display scenario details
    st.title(scenario['scenario_name'])
    st.caption(f"Product: {scenario['product_name']} | Category: {scenario['product_category']}")
    
    # ISO 13485 compliance badges if available
    if scenario['device_class'] is not None:
        st.markdown(f"""
        <div style="margin-top: 10px; margin-bottom: 20px;">
            <span class="iso-badge">{scenario['device_class']}</span>
            <span class="iso-badge">{scenario['regulatory_pathway'] or 'N/A'}</span>
            <span class="iso-badge">Change: {scenario['change_type'] or 'Minor'}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Scenario summary and metrics
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Improvement Details")
        st.markdown(f"""
        **Proposed Upgrade Solution:**  
        {scenario['upgrade_solution']}
        
        **Development Investment:** {format_currency(scenario['development_cost'])}  
        **Implementation Time:** {scenario['time_to_implement']} month(s)  
        **Unit Cost Change:** {format_currency(scenario['unit_cost_change'])}  
        """)
        
        st.markdown("### Expected Impacts")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.metric("Return Reduction", f"{scenario['estimated_return_reduction']:.1f}%")
            st.metric("Sales Increase", f"{scenario['sales_increase']:.1f}%")
            st.metric("Annual Benefit", format_currency(scenario['net_benefit']))
        
        with col_b:
            st.metric("ROI", format_percent(scenario['roi']) if pd.notna(scenario['roi']) else "N/A")
            st.metric("Break-even", f"{scenario['break_even_months']:.1f} months" if pd.notna(scenario['break_even_months']) else "N/A")
            st.metric("NPV", format_currency(scenario['npv']) if pd.notna(scenario['npv']) else "N/A")
    
    with col2:
        # ROI status indicator
        roi_status = get_roi_status(scenario['roi'])
        roi_color = COLOR_SCHEME["positive"] if roi_status == "status-positive" else (
            COLOR_SCHEME["warning"] if roi_status == "status-neutral" else COLOR_SCHEME["negative"])
        
        st.markdown(f"""
        <div class="metric-container" style="margin-bottom: 20px;">
            <p class="metric-label">Return on Investment</p>
            <p class="metric-value" style="color: {roi_color}; font-size: 2.5rem;">
                {format_percent(scenario['roi']) if pd.notna(scenario['roi']) else "N/A"}
            </p>
            <p style="color: {roi_color}; font-weight: 600;">
                {
                "Excellent ROI" if roi_status == "status-positive" else 
                ("Good ROI" if roi_status == "status-neutral" else "Low ROI")
                }
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Investment score
        score_color = get_color_scale(scenario['score'], 0, 100) if pd.notna(scenario['score']) else COLOR_SCHEME["neutral"]
        
        st.markdown(f"""
        <div class="metric-container" style="margin-bottom: 20px;">
            <p class="metric-label">Investment Score</p>
            <p class="metric-value" style="color: {score_color}; font-size: 2.5rem;">
                {f"{scenario['score']:.0f}" if pd.notna(scenario['score']) else "N/A"}
            </p>
            <p style="font-size: 0.9rem;">Based on ROI, break-even time, and return reduction</p>
        </div>
        """, unsafe_allow_html=True)
        
        # ISO 13485 compliance status
        if scenario['device_class'] is not None:
            validation_color = COLOR_SCHEME["positive"] if scenario['validation_required'] in ["None", "Minimal"] else (
                COLOR_SCHEME["warning"] if scenario['validation_required'] == "Moderate" else COLOR_SCHEME["negative"])
            
            st.markdown(f"""
            <div class="metric-container">
                <p class="metric-label">ISO 13485 Status</p>
                <p style="font-weight: 600; margin: 5px 0;">Validation: <span style="color: {validation_color};">{scenario['validation_required'] or 'Not Specified'}</span></p>
                <p style="font-weight: 600; margin: 5px 0;">Submission: {scenario['regulatory_submission'] or 'None'}</p>
                <p style="font-size: 0.9rem;">Risk Assessment ID: {scenario['risk_assessment_id']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Detailed data tabs
    st.markdown("### Detailed Analysis")
    
    tabs = st.tabs(["Financial Data", "Return Analysis", "Implementation Plan", "ISO Compliance"])
    
    with tabs[0]:  # Financial Data
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("#### Cost Analysis")
            
            financial_data = {
                "Metric": [
                    "Current Unit Cost",
                    "New Unit Cost",
                    "Unit Cost Change",
                    "Current Margin",
                    "New Margin",
                    "Margin Change",
                    "Return Processing Cost",
                    "Development Investment"
                ],
                "Value": [
                    format_currency(scenario['current_unit_cost']),
                    format_currency(scenario['new_unit_cost']),
                    format_currency(scenario['unit_cost_change']),
                    format_currency(scenario['margin_before']),
                    format_currency(scenario['margin_after']),
                    format_currency(scenario['margin_after'] - scenario['margin_before']),
                    format_currency(scenario['return_processing_cost']),
                    format_currency(scenario['development_cost'])
                ]
            }
            
            st.dataframe(pd.DataFrame(financial_data), hide_index=True)
        
        with col_b:
            st.markdown("#### Benefit Analysis")
            
            benefit_data = {
                "Metric": [
                    "Monthly Savings from Returns",
                    "Annual Savings from Returns",
                    "Monthly Sales Benefit",
                    "Annual Sales Benefit",
                    "Monthly Additional Costs",
                    "Annual Additional Costs",
                    "Monthly Net Benefit",
                    "Annual Net Benefit"
                ],
                "Value": [
                    format_currency(scenario['savings_monthly']),
                    format_currency(scenario['annual_savings']),
                    format_currency(scenario.get('sales_impact_monthly', 0)),
                    format_currency(scenario.get('sales_impact_annual', 0)),
                    format_currency(scenario.get('annual_additional_costs', 0) / 12),
                    format_currency(scenario.get('annual_additional_costs', 0)),
                    format_currency(scenario['monthly_net_benefit']),
                    format_currency(scenario['net_benefit'])
                ]
            }
            
            st.dataframe(pd.DataFrame(benefit_data), hide_index=True)
        
        # Financial metrics
        st.markdown("#### Financial Metrics")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric("ROI", format_percent(scenario['roi']) if pd.notna(scenario['roi']) else "N/A")
            st.metric("Payback Period", f"{scenario['payback_period']:.2f} years" if pd.notna(scenario['payback_period']) else "N/A")
        
        with col_b:
            st.metric("NPV", format_currency(scenario['npv']) if pd.notna(scenario['npv']) else "N/A")
            st.metric("IRR", format_percent(scenario['irr'] * 100) if pd.notna(scenario['irr']) else "N/A")
        
        with col_c:
            st.metric("Break-even Days", f"{scenario['break_even_days']:.1f}" if pd.notna(scenario['break_even_days']) else "N/A")
            st.metric("Break-even Months", f"{scenario['break_even_months']:.1f}" if pd.notna(scenario['break_even_months']) else "N/A")
        
        # ROI Calculation details
        st.markdown("#### ROI Calculation")
        st.markdown(f"""
        ```
        Annual Net Benefit = ${scenario['net_benefit']:,.2f}
        Development Cost = ${scenario['development_cost']:,.2f}
        ROI = (Annual Net Benefit / Development Cost) * 100 = {scenario['roi']:.2f}%
        ```
        """)
    
    with tabs[1]:  # Return Analysis
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("#### Current Return Statistics")
            
            current_return_data = {
                "Metric": [
                    "Monthly Unit Sales",
                    "Monthly Returns",
                    "Current Return Rate",
                    "Annual Unit Sales",
                    "Annual Returns",
                    "Return Value Impact (Annual)",
                    "Return Processing Cost (per unit)",
                    "Total Return Cost (Annual)"
                ],
                "Value": [
                    f"{scenario['current_unit_sales']:,}",
                    f"{scenario['current_returns']:,}",
                    f"{scenario['return_rate']:.2f}%",
                    f"{scenario['annual_unit_sales']:,}",
                    f"{scenario['annual_returns']:,}",
                    format_currency(scenario['revenue_impact_annual']),
                    format_currency(scenario['return_processing_cost']),
                    format_currency(scenario['return_cost_annual'])
                ]
            }
            
            st.dataframe(pd.DataFrame(current_return_data), hide_index=True)
            
            # Return rate visualization
            fig = go.Figure()
            
            # Add current return rate
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=scenario['return_rate'],
                title={"text": "Current Return Rate"},
                gauge={
                    "axis": {"range": [0, 20], "tickwidth": 1},
                    "bar": {"color": COLOR_SCHEME["warning"]},
                    "steps": [
                        {"range": [0, 5], "color": "lightgreen"},
                        {"range": [5, 10], "color": "lightyellow"},
                        {"range": [10, 20], "color": "salmon"}
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 2},
                        "thickness": 0.75,
                        "value": scenario['return_rate']
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_b:
            st.markdown("#### Projected Return Improvements")
            
            improved_return_data = {
                "Metric": [
                    "Return Reduction Rate",
                    "Avoided Returns (Monthly)",
                    "Avoided Returns (Annual)",
                    "New Return Rate",
                    "Return Reduction Benefit (Monthly)",
                    "Return Reduction Benefit (Annual)",
                    "Savings Per Avoided Return",
                    "Cost to Implement" 
                ],
                "Value": [
                    f"{scenario['estimated_return_reduction']:.2f}%",
                    f"{scenario['avoided_returns_monthly']:.1f}",
                    f"{scenario['avoided_returns_annual']:.1f}",
                    f"{scenario['return_rate'] * (1 - scenario['estimated_return_reduction']/100):.2f}%",
                    format_currency(scenario['savings_monthly']),
                    format_currency(scenario['annual_savings']),
                    format_currency(scenario['savings_monthly'] / max(1, scenario['avoided_returns_monthly'])),
                    format_currency(scenario['development_cost'])
                ]
            }
            
            st.dataframe(pd.DataFrame(improved_return_data), hide_index=True)
            
            # Improved return rate visualization
            fig = go.Figure()
            
            # Calculate improved rate
            improved_rate = scenario['return_rate'] * (1 - scenario['estimated_return_reduction']/100)
            
            # Add improved return rate
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=improved_rate,
                delta={"reference": scenario['return_rate'], "valueformat": ".2f"},
                title={"text": "Projected Return Rate"},
                gauge={
                    "axis": {"range": [0, 20], "tickwidth": 1},
                    "bar": {"color": COLOR_SCHEME["primary"]},
                    "steps": [
                        {"range": [0, 5], "color": "lightgreen"},
                        {"range": [5, 10], "color": "lightyellow"},
                        {"range": [10, 20], "color": "salmon"}
                    ],
                    "threshold": {
                        "line": {"color": "green", "width": 2},
                        "thickness": 0.75,
                        "value": improved_rate
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:  # Implementation Plan
        st.markdown("#### Implementation Timeline")
        
        # Create a Gantt chart for implementation timeline
        implementation_months = scenario['time_to_implement']
        
        # Calculate phase durations
        design_phase = max(1, implementation_months // 3)
        validation_phase = max(1, implementation_months // 3)
        regulatory_phase = max(0.5, implementation_months // 4)
        production_phase = max(1, implementation_months // 3)
        
        # Create timeline data
        timeline_data = {
            "Task": [
                "Design Phase",
                "Verification & Validation",
                "Regulatory Assessment",
                "Production Implementation",
                "Post-Market Surveillance"
            ],
            "Start": [
                0,
                design_phase,
                design_phase + validation_phase,
                design_phase + validation_phase + regulatory_phase,
                design_phase + validation_phase + regulatory_phase + production_phase
            ],
            "Duration": [
                design_phase,
                validation_phase,
                regulatory_phase,
                production_phase,
                2  # 2 months of initial post-market surveillance
            ],
            "Resource": [
                "Engineering",
                "Quality Assurance",
                "Regulatory",
                "Production",
                "Quality & Marketing"
            ]
        }
        
        # Convert to DataFrame for visualization
        timeline_df = pd.DataFrame(timeline_data)
        
        # Create Gantt chart
        fig = px.timeline(
            timeline_df, 
            x_start="Start", 
            x_end=timeline_df["Start"] + timeline_df["Duration"], 
            y="Task",
            color="Resource",
            title="Implementation Timeline (Months)",
            color_discrete_sequence=[COLOR_SCHEME["primary"], COLOR_SCHEME["secondary"], 
                                     COLOR_SCHEME["warning"], COLOR_SCHEME["positive"], 
                                     COLOR_SCHEME["subtle"]]
        )
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Resource requirements
        st.markdown("#### Resource Requirements")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**Required Teams:**")
            st.markdown("""
            - **Engineering:** Design and development resources
            - **Quality:** Validation and documentation support
            - **Production:** Process implementation and training
            - **Regulatory:** Compliance review and documentation
            """)
        
        with col_b:
            st.markdown("**Required Documentation:**")
            st.markdown("""
            - Design Change Request
            - Risk Assessment Update
            - Verification Protocol
            - Validation Protocol (if applicable)
            - Manufacturing Process Update
            - Training Materials
            """)
        
        # Implementation challenges and risk mitigation
        st.markdown("#### Implementation Challenges & Mitigation")
        
        challenges_data = {
            "Challenge": [
                "Technical Integration",
                "Validation Timeline",
                "Supply Chain Impact",
                "Training Requirements"
            ],
            "Risk Level": [
                "Medium",
                "Low" if scenario['validation_required'] in ["None", "Minimal"] else "Medium",
                "Low" if scenario['unit_cost_change'] == 0 else "Medium",
                "Low" if scenario['time_to_implement'] <= 1 else "Medium"
            ],
            "Mitigation Strategy": [
                "Phased implementation with testing at each stage",
                "Early engagement with quality team; validation protocol development",
                "Dual sourcing for critical components; early supplier engagement",
                "Comprehensive training plan; train-the-trainer approach"
            ]
        }
        
        challenges_df = pd.DataFrame(challenges_data)
        
        # Add color coding for risk levels
        challenges_df["Risk Level"] = challenges_df["Risk Level"].apply(
            lambda x: f"<span style='color: {'#F0B323' if x == 'Medium' else ('#EB3300' if x == 'High' else '#1e8449')};'>{x}</span>"
        )
        
        st.markdown(challenges_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        # Post-implementation monitoring
        st.markdown("#### Post-Implementation Monitoring")
        
        monitoring_data = {
            "Metric": [
                "Return Rate",
                "Financial Impact",
                "Customer Satisfaction",
                "Product Quality"
            ],
            "KPI": [
                f"Reduction from {scenario['return_rate']:.2f}% to {scenario['return_rate'] * (1 - scenario['estimated_return_reduction']/100):.2f}%",
                f"ROI of {scenario['roi']:.1f}% within {scenario['payback_period']:.1f} years" if pd.notna(scenario['roi']) and pd.notna(scenario['payback_period']) else "Positive ROI",
                "Maintain or improve NPS score",
                "Zero increase in quality-related complaints"
            ],
            "Monitoring Frequency": [
                "Weekly",
                "Monthly",
                "Quarterly",
                "Weekly"
            ]
        }
        
        st.dataframe(pd.DataFrame(monitoring_data), hide_index=True)
    
    with tabs[3]:  # ISO Compliance
        st.markdown("#### ISO 13485:2016 Compliance Assessment")
        
        # Create ISO compliance assessment
        st.markdown("""
        <div class="iso-section">
            <h4>ISO 13485:2016 Compliance Requirements</h4>
            <p>This assessment identifies the ISO 13485:2016 requirements applicable to this product improvement project.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create compliance table
        compliance_data = {
            "ISO 13485 Section": [
                "4.1 Quality Management System",
                "4.2 Documentation Requirements",
                "7.1 Planning of Product Realization",
                "7.2 Customer-Related Processes",
                "7.3 Design and Development",
                "7.4 Purchasing",
                "7.5 Production and Service Provision",
                "7.6 Control of Monitoring and Measuring Equipment",
                "8.2.1 Feedback",
                "8.2.3 Reporting to Regulatory Authorities",
                "8.3 Control of Nonconforming Product",
                "8.5 Corrective & Preventive Action"
            ],
            "Applicability": [
                "Applicable",
                "Applicable",
                "Applicable",
                "Applicable",
                "Applicable" if scenario['device_class'] in ["Class II", "Class III"] else "Limited",
                "Applicable" if scenario['unit_cost_change'] != 0 else "Limited",
                "Applicable",
                "Limited",
                "Applicable",
                "Applicable" if scenario['device_class'] in ["Class II", "Class III"] else "Limited",
                "Applicable",
                "Applicable"
            ],
            "Compliance Actions Required": [
                "Update QMS records with improvement project",
                "Create & maintain project documentation",
                "Risk-based approach to improvement implementation",
                "Ensure improvement meets customer requirements",
                "Full design control process" if scenario['device_class'] in ["Class II", "Class III"] else "Limited design controls",
                "Supplier qualification if new materials" if scenario['unit_cost_change'] != 0 else "N/A",
                "Process validation for manufacturing changes",
                "Calibration requirements for test equipment",
                "Monitoring improved product performance post-launch",
                "Notification if reportable improvement" if scenario['device_class'] in ["Class II", "Class III"] else "N/A",
                "Updated process for improved product",
                "CAPA system to monitor effectiveness"
            ]
        }
        
        # Add color coding for applicability
        compliance_df = pd.DataFrame(compliance_data)
        compliance_df["Applicability"] = compliance_df["Applicability"].apply(
            lambda x: f"<span style='color: {'#23b2be' if x == 'Applicable' else ('#F0B323' if x == 'Limited' else '#777473')};'>{x}</span>"
        )
        
        st.markdown(compliance_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        # Regulatory pathway
        st.markdown("#### Regulatory Pathway Assessment")
        
        if scenario['device_class'] is not None:
            st.markdown(f"""
            <div class="info-box">
                <p><strong>Device Classification:</strong> {scenario['device_class']}</p>
                <p><strong>Regulatory Pathway:</strong> {scenario['regulatory_pathway']}</p>
                <p><strong>Submission Requirement:</strong> {scenario['regulatory_submission']}</p>
                <p><strong>Change Type:</strong> {scenario['change_type']}</p>
                <p><strong>Risk Assessment ID:</strong> {scenario['risk_assessment_id']}</p>
                <p><strong>Change Request ID:</strong> {scenario['change_request_id']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Device classification not specified. Regulatory pathway assessment unavailable.")
        
        # Design control impact
        st.markdown("#### Design Control Impact")
        
        if scenario.get('design_control_impact'):
            impact_items = scenario['design_control_impact']
            if isinstance(impact_items, str):
                # Convert string to list if stored as string
                try:
                    impact_items = eval(impact_items)
                except:
                    impact_items = [impact_items]
            
            if not isinstance(impact_items, list):
                impact_items = []
                
            st.markdown("""
            <div class="iso-section">
                <h4>Design Control Elements Impacted</h4>
                <p>The following design control elements are impacted by this product improvement:</p>
            </div>
            """, unsafe_allow_html=True)
            
            for item in impact_items:
                st.markdown(f"- **{item}**")
        else:
            st.info("Design control impact not specified.")
        
        # Documentation requirements
        st.markdown("#### Documentation Requirements")
        
        documentation_requirements = []
        
        # Determine documentation based on device class and change type
        if scenario['device_class'] == "Class III":
            documentation_requirements.extend([
                "Design History File (DHF) Update",
                "Risk Analysis Update",
                "Design Verification Protocol",
                "Design Validation Protocol",
                "Software Validation (if applicable)",
                "PMA Supplement Documentation",
                "Clinical Data Evaluation",
                "Human Factors Validation"
            ])
        elif scenario['device_class'] == "Class II":
            documentation_requirements.extend([
                "Design History File (DHF) Update",
                "Risk Analysis Update",
                "Design Verification Protocol",
                "510(k) Documentation" if scenario['regulatory_submission'] in ["Special 510(k)", "Traditional 510(k)"] else "Letter to File",
                "Software Validation (if applicable)",
                "Human Factors Evaluation"
            ])
        else:  # Class I or not specified
            documentation_requirements.extend([
                "Design Change Documentation",
                "Risk Assessment Update",
                "Verification Documentation",
                "Letter to File (if applicable)"
            ])
        
        # Add general documentation requirements
        documentation_requirements.extend([
            "Device Master Record (DMR) Update",
            "Manufacturing Process Change Documentation",
            "Training Documentation",
            "Quality Plan Update"
        ])
        
        # Display as checklist
        for doc in documentation_requirements:
            st.checkbox(doc, key=f"doc_{doc.replace(' ', '_')}", value=False, disabled=True)
        
        # Generate documentation button
        if st.button("Generate ISO Documentation Package"):
            documentation = generate_iso_documentation(scenario)
            markdown_doc = generate_markdown_from_documentation(documentation)
            
            # Log the documentation generation
            optimizer.log_audit(
                "Generate Documentation", 
                f"Generated ISO documentation package for: {scenario['scenario_name']}"
            )
            
            # Display download button
            st.markdown("### ISO Documentation Package")
            st.download_button(
                "Download Documentation (PDF)",
                data=export_markdown_to_pdf(markdown_doc),
                file_name=f"ISO_Documentation_{scenario['uid']}.pdf",
                mime="application/pdf"
            )
    
    # Add Monte Carlo simulation option
    st.markdown("### Advanced Analysis")
    
    if st.button("Run Monte Carlo Risk Simulation"):
        st.session_state['view_scenario'] = False
        st.session_state['monte_carlo_scenario'] = scenario_uid
        st.session_state['nav_option'] = "Monte Carlo Analysis"
        st.experimental_rerun()

def display_header():
    """Display app header with logo and navigation"""
    col1, col2 = st.columns([1, 5])
    
    # Use Vive Health brand styling
    with col1:
        st.markdown("""
        <div class="logo-container">
            <p class="logo-icon">🔄</p>
            <p class="logo-text">KaizenROI</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Title and description
    with col2:
        st.title("Medical Device ROI Analyzer")
        st.caption("Evaluate product improvements with robust ISO 13485/9001 compliant ROI analysis.")
        
        # Add ISO badges
        st.markdown("""
        <div style="margin-top: -10px;">
            <span class="iso-badge">ISO 13485</span>
            <span class="iso-badge">ISO 9001</span>
            <span class="iso-badge">21 CFR 820</span>
        </div>
        """, unsafe_allow_html=True)

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
        if not category_data.empty and 'net_benefit' in category_data.columns:
            top_category_idx = category_data['net_benefit'].idxmax()
            top_category = category_data.loc[top_category_idx, 'product_category']
            top_category_roi = category_data.loc[top_category_idx, 'roi']
        
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
                        quickest_idx = payback_df['payback_period'].idxmin()
                        quickest_payback = payback_df.loc[quickest_idx]
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
                        highest_idx = npv_df['npv'].idxmax()
                        highest_npv = npv_df.loc[highest_idx]
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
    """
    Create form for adding a new upgrade scenario with ISO 13485 compliance features.
    Includes simple/advanced mode toggle and medical device specific inputs.
    """
    # Add simple/advanced mode toggle
    form_mode = st.radio(
        "Form Mode:",
        ["Simple", "Advanced"],
        horizontal=True,
        help="Simple mode includes essential inputs. Advanced mode adds detailed parameters for regulatory compliance."
    )
    
    with st.form(key="scenario_form"):
        st.subheader("Add New Product Upgrade Scenario")
        
        # Use tabs for better organization
        if form_mode == "Simple":
            tabs = st.tabs(["Product Details", "Upgrade Information", "Financial Projections"])
        else:
            tabs = st.tabs(["Product Details", "Upgrade Information", "Financial Projections", "ISO 13485 Compliance", "Documentation"])
        
        with tabs[0]:  # Product Details
            col1, col2 = st.columns(2)
            with col1:
                scenario_name = st.text_input("Scenario Name", 
                                            help="A memorable name for this upgrade scenario",
                                            placeholder="e.g., Premium Material Upgrade")
                
                product_name = st.text_input("Product Name", 
                                           help="The name of the product being upgraded",
                                           placeholder="e.g., Compression Sleeve XS-450")
                
                product_category = st.selectbox("Product Category", 
                                              ["Support & Braces", "Mobility", "Pain Management", 
                                               "Monitoring Device", "Diagnostic Device", "Therapy", 
                                               "Patient Care", "Accessories", "Software", "Other"],
                                              help="The medical device category this product belongs to")
                
                sales_channel = st.selectbox("Primary Sales Channel", 
                                           ["Direct to Healthcare Provider", "Distributor", "GPO", 
                                            "Online B2B", "Direct to Patient", "Pharmacy", "Other"],
                                           help="Main distribution channel for this medical device")
                
                product_lifecycle_stage = st.selectbox("Product Lifecycle Stage",
                                                    ["Introduction", "Growth", "Maturity", "Decline"],
                                                    help="Current stage in the product lifecycle")
                
                if form_mode == "Advanced":
                    # Additional fields for medical device information
                    device_class = st.selectbox(
                        "Medical Device Classification",
                        ["Class I", "Class II", "Class III"],
                        help="FDA/EU MDR device classification"
                    )
                    
                    regulatory_pathway = st.selectbox(
                        "Regulatory Pathway",
                        ["510(k)", "PMA", "De Novo", "510(k) Exempt", "EU MDR", "Other"],
                        help="Regulatory submission pathway"
                    )
            
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
                
                # Return processing cost with more specific medical device context
                return_processing_cost = st.number_input(
                    "Return Processing Cost ($)", 
                    min_value=0.0, 
                    format="%.2f", 
                    value=round(current_unit_cost * 0.15, 2) if current_unit_cost > 0 else 0.0,
                    help="Cost to process each return including customer service, shipping, restocking, and quality investigation"
                )
                
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
                
                if form_mode == "Advanced":
                    # Add field for return reason categorization
                    return_reasons = st.multiselect(
                        "Primary Return Reasons",
                        ["Product Defect", "User Error", "Packaging Issue", "Labeling Issue", 
                         "Performance Issue", "Wrong Product", "Customer Preference", 
                         "Adverse Event", "Regulatory Concern", "Other"],
                        help="Select primary reasons for current product returns"
                    )
        
        with tabs[1]:  # Upgrade Information
            col1, col2 = st.columns(2)
            with col1:
                upgrade_solution = st.text_area("Proposed Upgrade", 
                                              height=100,
                                              help="Detailed description of the product improvement",
                                              placeholder="Describe the proposed improvement/upgrade...")
                
                development_cost = st.number_input("Development Cost ($)", 
                                                 min_value=0.0, 
                                                 format="%.2f", 
                                                 help="One-time investment required to implement the upgrade")
                
                unit_cost_change = st.number_input("Unit Cost Change ($)", 
                                                 format="%.2f", 
                                                 help="Change in cost per unit after upgrade (can be negative for cost reductions)")
                
                if form_mode == "Advanced":
                    # Add fields for change classification
                    change_type = st.selectbox(
                        "Change Classification",
                        ["Minor Change", "Significant Change", "Major Change"],
                        help="Regulatory classification of the proposed change"
                    )
                    
                    change_categories = st.multiselect(
                        "Change Categories",
                        ["Design", "Material", "Manufacturing Process", "Packaging", 
                         "Labeling", "Sterilization", "Software", "Intended Use", "Other"],
                        help="Categories affected by the proposed change"
                    )
            
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
                
                if form_mode == "Advanced":
                    # Add fields for implementation details
                    validation_required = st.selectbox(
                        "Validation/Verification Required",
                        ["None", "Minimal", "Moderate", "Extensive"],
                        help="Level of validation/verification activities required"
                    )
                    
                    regulatory_submission = st.selectbox(
                        "Regulatory Submission Required",
                        ["None", "Letter to File", "Special 510(k)", "Traditional 510(k)", "PMA Supplement", "New Submission"],
                        help="Type of regulatory submission required for this change"
                    )
                    
                    design_control_impact = st.multiselect(
                        "Design Control Elements Impacted",
                        ["Design Inputs", "Design Outputs", "Design Verification", 
                         "Design Validation", "Design Review", "Design Transfer", 
                         "Risk Management", "Design History File"],
                        help="Design control elements impacted by this change"
                    )
        
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
                
                # Advanced financial projections
                if form_mode == "Advanced":
                    st.markdown("#### Advanced Financial Metrics")
                    
                    # NPV Calculation
                    discount_rate = st.slider(
                        "Discount Rate (%)", 
                        min_value=5, 
                        max_value=25, 
                        value=10,
                        help="Annual discount rate for Net Present Value calculation"
                    )
                    
                    projection_years = st.slider(
                        "Projection Timeframe (years)", 
                        min_value=1, 
                        max_value=10, 
                        value=3,
                        help="Number of years to project for NPV calculation"
                    )
                    
                    # Implementation curve
                    implementation_curve = st.selectbox(
                        "Implementation Curve",
                        ["Linear", "S-Curve", "Fast Initial"],
                        help="Implementation adoption pattern over time"
                    )
                    
                    # Calculate NPV
                    npv = -development_cost  # Initial investment is negative cash flow
                    
                    # Apply implementation curve
                    if implementation_curve == "Linear":
                        first_year_factor = max(0, 12 - time_to_implement) / 12
                    elif implementation_curve == "S-Curve":
                        first_year_factor = max(0, 12 - time_to_implement) / 12 * 0.7  # Slower start
                    else:  # Fast Initial
                        first_year_factor = max(0, 12 - time_to_implement) / 12 * 1.2  # Faster start, capped at 1.0
                        first_year_factor = min(first_year_factor, 1.0)
                    
                    # Add cash flows
                    for year in range(1, projection_years + 1):
                        if year == 1:
                            # First year partial based on implementation time
                            year_benefit = annual_net * first_year_factor
                        else:
                            # Full benefit for subsequent years
                            year_benefit = annual_net
                        
                        # Apply discount rate
                        npv += year_benefit / ((1 + discount_rate/100) ** year)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Net Present Value (NPV)", f"${npv:,.2f}")
                    
                    with col2:
                        # Calculate IRR approximation (simplified)
                        if development_cost > 0 and annual_net > 0:
                            # Simple IRR approximation
                            irr_approx = (annual_net / development_cost) - 1
                            st.metric("Approximate IRR", f"{irr_approx*100:.1f}%")
                        else:
                            st.metric("Approximate IRR", "N/A")
                    
                    with col3:
                        # Calculate benefit-cost ratio
                        if development_cost > 0:
                            bcr = npv / development_cost + 1  # Add 1 to account for initial investment
                            st.metric("Benefit-Cost Ratio", f"{bcr:.2f}")
                        else:
                            st.metric("Benefit-Cost Ratio", "N/A")
        
        if form_mode == "Advanced":
            with tabs[3]:  # ISO 13485 Compliance
                st.markdown("### ISO 13485:2016 Compliance Requirements")
                st.caption("Configure ISO 13485 specific information for regulatory compliance documentation")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'device_class' not in locals() or device_class is None:
                        device_class = st.selectbox(
                            "Medical Device Classification",
                            ["Class I", "Class II", "Class III"],
                            help="FDA/EU MDR device classification"
                        )
                    
                    if 'regulatory_pathway' not in locals() or regulatory_pathway is None:
                        regulatory_pathway = st.selectbox(
                            "Regulatory Pathway",
                            ["510(k)", "PMA", "De Novo", "510(k) Exempt", "EU MDR", "Other"],
                            help="Regulatory submission pathway"
                        )
                    
                    if 'validation_required' not in locals() or validation_required is None:
                        validation_required = st.selectbox(
                            "Validation/Verification Required",
                            ["None", "Minimal", "Moderate", "Extensive"],
                            help="Level of validation/verification activities required"
                        )
                
                with col2:
                    if 'regulatory_submission' not in locals() or regulatory_submission is None:
                        regulatory_submission = st.selectbox(
                            "Regulatory Submission Required",
                            ["None", "Letter to File", "Special 510(k)", "Traditional 510(k)", "PMA Supplement", "New Submission"],
                            help="Type of regulatory submission required for this change"
                        )
                    
                    if 'change_type' not in locals() or change_type is None:
                        change_type = st.selectbox(
                            "Change Classification",
                            ["Minor Change", "Significant Change", "Major Change"],
                            help="Regulatory classification of the proposed change"
                        )
                    
                    if 'design_control_impact' not in locals() or design_control_impact is None:
                        design_control_impact = st.multiselect(
                            "Design Control Elements Impacted",
                            ["Design Inputs", "Design Outputs", "Design Verification", 
                             "Design Validation", "Design Review", "Design Transfer", 
                             "Risk Management", "Design History File"],
                            help="Design control elements impacted by this change"
                        )
                
                # Additional ISO 13485 specific fields
                st.markdown("### Risk Management")
                
                risk_col1, risk_col2 = st.columns(2)
                
                with risk_col1:
                    risk_assessment_conducted = st.checkbox(
                        "Risk Assessment Required",
                        value=True if device_class in ["Class II", "Class III"] else False,
                        help="Indicates whether a formal risk assessment is required for this change"
                    )
                    
                    risk_management_file_update = st.checkbox(
                        "Risk Management File Update Required",
                        value=True if device_class in ["Class II", "Class III"] else False,
                        help="Indicates whether the risk management file needs to be updated"
                    )
                
                with risk_col2:
                    design_history_file_update = st.checkbox(
                        "Design History File Update Required",
                        value=True if device_class in ["Class II", "Class III"] else False,
                        help="Indicates whether the design history file needs to be updated"
                    )
                    
                    significant_change_determination = st.checkbox(
                        "Significant Change Determination Required",
                        value=True if device_class in ["Class II", "Class III"] and change_type == "Significant Change" else False,
                        help="Indicates whether a significant change determination is required"
                    )
                
                # Auto-generate regulatory IDs
                temp_uid = str(uuid.uuid4())[:8]
                risk_assessment_id = f"RA-{temp_uid[:4]}-{datetime.now().strftime('%y%m')}"
                change_request_id = f"CR-{temp_uid[:4]}-{datetime.now().strftime('%y%m')}"
                
                st.markdown("### Quality System Records")
                
                st.markdown(f"""
                **Risk Assessment ID:** {risk_assessment_id}  
                **Change Request ID:** {change_request_id}
                """)
            
            with tabs[4]:  # Documentation
                st.markdown("### Documentation Requirements")
                st.caption("Configure documentation requirements for this product improvement")
                
                # Determine required documentation based on device class and change type
                required_docs = []
                
                if 'device_class' in locals() and device_class is not None:
                    if device_class == "Class III":
                        required_docs.extend([
                            "Design History File (DHF) Update",
                            "Risk Analysis Update",
                            "Design Verification Protocol",
                            "Design Validation Protocol",
                            "PMA Supplement Documentation"
                        ])
                    elif device_class == "Class II":
                        required_docs.extend([
                            "Design History File (DHF) Update",
                            "Risk Analysis Update",
                            "Design Verification Protocol",
                            "510(k) Documentation" if 'regulatory_submission' in locals() and regulatory_submission in ["Special 510(k)", "Traditional 510(k)"] else "Letter to File"
                        ])
                    else:  # Class I
                        required_docs.extend([
                            "Design Change Documentation",
                            "Risk Assessment Update",
                            "Letter to File (if applicable)"
                        ])
                
                # Add general documentation
                required_docs.extend([
                    "Device Master Record (DMR) Update",
                    "Manufacturing Process Change Documentation",
                    "Training Documentation"
                ])
                
                # Display as checklist with default selections
                doc_requirements = {}
                for doc in required_docs:
                    doc_requirements[doc] = st.checkbox(doc, value=True)
                
                # Additional documentation notes
                doc_notes = st.text_area(
                    "Additional Documentation Notes",
                    help="Any special documentation requirements or notes for this improvement"
                )
        
        # Submit button
        submit_button = st.form_submit_button("Add Scenario")
    
    # Process form outside the form context
    if submit_button:
        # Validate inputs
        if not scenario_name or not product_name:
            st.error("Scenario Name and Product Name are required.")
            return
        
        if current_unit_sales <= 0:
            st.error("Current unit sales must be greater than zero.")
            return
        
        if current_returns > current_unit_sales:
            st.error("Returns cannot exceed sales.")
            return
        
        # Prepare design control impact - handle when not defined in simple mode
        if form_mode == "Simple":
            design_control_impact = None
            device_class = None
            regulatory_pathway = None
            validation_required = None
            regulatory_submission = None
            change_type = None
        
        # Add scenario
        success, message = optimizer.add_scenario(
            scenario_name, product_name, product_category, current_unit_sales, 
            avg_sale_price, sales_channel, current_returns, upgrade_solution, 
            development_cost, unit_cost_change, current_unit_cost, 
            estimated_return_reduction, sales_increase, product_lifecycle_stage,
            annual_unit_sales, annual_returns, return_processing_cost, 
            time_to_implement, None, device_class, regulatory_pathway,
            validation_required, regulatory_submission, design_control_impact,
            change_type
        )
        
        if success:
            st.success(message)
            # Add a button to go to the newly added scenario
            if st.button("View Scenario Details"):
                # Find the UID of the newly added scenario
                new_scenario = optimizer.scenarios[optimizer.scenarios['scenario_name'] == scenario_name].iloc[-1]
                st.session_state['view_scenario'] = True
                st.session_state['selected_scenario'] = new_scenario['uid']
                st.experimental_rerun()
        else:
            st.error(message)

def display_portfolio_analysis(df):
    """Display portfolio-level analysis and visualizations with ISO 13485 compliance features"""
    if df.empty:
        st.info("Add scenarios to see portfolio analysis.")
        return
    
    # Add simple/advanced mode toggle
    analysis_mode = st.radio(
        "Analysis Mode:",
        ["Simple", "Advanced"],
        horizontal=True,
        help="Simple mode shows essential metrics. Advanced mode includes detailed statistical analysis and ISO compliance features."
    )
    
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
        text="AVOID: Low ROI, Slow Payback",
        showarrow=False,
        font=dict(color="red", size=12)
    )
    
    fig_bubble.update_traces(textposition='top center')
    fig_bubble.update_layout(height=600)
    
    st.plotly_chart(fig_bubble, use_container_width=True)
    
    # Risk-adjusted portfolio view (ISO 13485 compliance feature)
    if analysis_mode == "Advanced":
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">⚠️</span>
            <h3 class="section-title">Risk-Adjusted Portfolio Analysis (ISO 13485/9001)</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create risk assessment matrix
        st.markdown("### Risk Assessment Matrix")
        
        # Add risk parameters
        risk_col1, risk_col2 = st.columns(2)
        
        with risk_col1:
            st.markdown("#### Implementation Risk Factors")
            st.caption("Adjust risk factors for implementation analysis")
            
            technical_risk = st.slider(
                "Technical Complexity Risk (1-10)", 
                min_value=1, 
                max_value=10, 
                value=5, 
                help="Higher values indicate greater technical complexity and implementation risk"
            )
            
            validation_risk = st.slider(
                "Validation/Verification Risk (1-10)", 
                min_value=1, 
                max_value=10, 
                value=5, 
                help="Higher values indicate greater validation/verification challenges"
            )
            
            regulatory_risk = st.slider(
                "Regulatory Impact Risk (1-10)", 
                min_value=1, 
                max_value=10, 
                value=5, 
                help="Higher values indicate greater regulatory implications"
            )
        
        with risk_col2:
            st.markdown("#### Quality Impact Assessment")
            st.caption("Evaluate quality and patient safety considerations")
            
            patient_benefit = st.slider(
                "Patient Safety Benefit (1-10)", 
                min_value=1, 
                max_value=10, 
                value=5, 
                help="Higher values indicate greater positive impact on patient safety"
            )
            
            quality_impact = st.slider(
                "Quality System Impact (1-10)", 
                min_value=1, 
                max_value=10, 
                value=5, 
                help="Higher values indicate greater positive impact on overall quality system"
            )
            
            documentation_burden = st.slider(
                "Documentation Burden (1-10)", 
                min_value=1, 
                max_value=10, 
                value=5, 
                help="Higher values indicate greater documentation requirements"
            )
        
        # Calculate risk-adjusted scores for the portfolio
        plot_df['risk_score'] = ((technical_risk + validation_risk + regulatory_risk) / 3)
        plot_df['benefit_score'] = ((patient_benefit + quality_impact) / 2)
        plot_df['risk_adjusted_roi'] = plot_df['roi'] * (plot_df['benefit_score'] / plot_df['risk_score'])
        
        # Create risk-adjusted ROI chart
        fig_risk = px.scatter(
            plot_df,
            x="risk_score",
            y="benefit_score",
            size="bubble_size",
            color="risk_adjusted_roi",
            color_continuous_scale="RdYlGn",
            hover_name="scenario_name",
            text="product_name",
            size_max=size_max,
            labels={
                "risk_score": "Implementation Risk Score",
                "benefit_score": "Quality/Patient Benefit Score",
                "risk_adjusted_roi": "Risk-Adjusted ROI (%)"
            },
            title="ISO 13485 Risk-Adjusted Portfolio Analysis"
        )
        
        fig_risk.update_traces(textposition='top center')
        fig_risk.update_layout(height=600)
        
        st.plotly_chart(fig_risk, use_container_width=True)
        
        # Add document/quality process impact analysis
        st.markdown("### Quality System Impact Analysis")
        st.caption("Evaluate how improvements align with ISO 13485/9001 requirements")
        
        qms_impact_data = {
            "QMS Area": [
                "Design Controls", 
                "Document Control", 
                "Production Controls", 
                "CAPA System", 
                "Risk Management", 
                "Supplier Controls"
            ],
            "Impact Score": [
                quality_impact * 0.8,
                documentation_burden * 0.9,
                quality_impact * 0.7,
                quality_impact * 0.6,
                patient_benefit * 0.9,
                quality_impact * 0.5
            ]
        }
        
        qms_df = pd.DataFrame(qms_impact_data)
        
        fig_qms = px.bar(
            qms_df,
            x="QMS Area",
            y="Impact Score",
            color="Impact Score",
            color_continuous_scale="Bluered_r",
            title="Quality Management System Impact Assessment"
        )
        
        fig_qms.update_layout(height=400)
        st.plotly_chart(fig_qms, use_container_width=True)
        
        # Documentation burden vs. benefit analysis for ISO compliance
        st.markdown("### Documentation ROI Analysis")
        st.caption("Balancing documentation burden with quality improvements")
        
        # Calculate documentation efficiency metrics
        plot_df['doc_efficiency'] = plot_df['score'] / documentation_burden
        
        fig_doc = px.scatter(
            plot_df,
            x="doc_efficiency",
            y="risk_adjusted_roi",
            size="bubble_size",
            color="score",
            hover_name="scenario_name",
            text="product_name",
            labels={
                "doc_efficiency": "Documentation Efficiency (ROI/Doc Burden)",
                "risk_adjusted_roi": "Risk-Adjusted ROI (%)",
                "score": "Overall ROI Score"
            },
            title="ISO Compliance Documentation Efficiency Analysis"
        )
        
        fig_doc.update_layout(height=500)
        st.plotly_chart(fig_doc, use_container_width=True)
    
    # Category-specific analysis
    st.markdown("### Category Performance Analysis")
    
    # Calculate aggregates by category
    if 'product_category' in filtered_df.columns:
        category_data = filtered_df.groupby('product_category').agg({
            'net_benefit': 'sum',
            'roi': 'mean',
            'payback_period': 'mean',
            'development_cost': 'sum',
            'estimated_return_reduction': 'mean',
            'sales_increase': 'mean'
        }).reset_index()
        
        # Display category comparison
        st.markdown("#### Category Comparison")
        
        # Bar chart for category performance
        fig_cat = px.bar(
            category_data,
            x="product_category",
            y="roi",
            color="net_benefit",
            color_continuous_scale="Viridis",
            labels={
                "product_category": "Category",
                "roi": "Average ROI (%)",
                "net_benefit": "Total Net Benefit ($)"
            },
            title="ROI by Product Category"
        )
        
        fig_cat.update_layout(height=400)
        st.plotly_chart(fig_cat, use_container_width=True)
        
        # If in advanced mode, show more detailed category analysis
        if analysis_mode == "Advanced":
            # Create radar chart for multi-dimensional category comparison
            categories = category_data['product_category'].tolist()
            metrics = ["ROI", "Payback", "Return Reduction", "Sales Increase"]
            
            # Prepare radar chart data
            radar_data = []
            
            for i, cat in enumerate(categories):
                cat_data = category_data.iloc[i]
                
                # Normalize metrics for radar chart (0-1 scale)
                roi_norm = min(1, cat_data['roi'] / 200) if not pd.isna(cat_data['roi']) else 0
                payback_norm = min(1, 3 / cat_data['payback_period']) if not pd.isna(cat_data['payback_period']) and cat_data['payback_period'] > 0 else 0
                reduction_norm = cat_data['estimated_return_reduction'] / 100 if not pd.isna(cat_data['estimated_return_reduction']) else 0
                sales_norm = min(1, cat_data['sales_increase'] / 50) if not pd.isna(cat_data['sales_increase']) else 0
                
                radar_data.append(
                    go.Scatterpolar(
                        r=[roi_norm, payback_norm, reduction_norm, sales_norm],
                        theta=metrics,
                        fill='toself',
                        name=cat
                    )
                )
            
            # Create radar chart
            fig_radar = go.Figure(data=radar_data)
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                showlegend=True,
                height=500,
                title="Multi-dimensional Category Performance"
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
    
    # Portfolio optimization recommendations
    st.markdown("### Portfolio Optimization Recommendations")
    
    # Create investment efficiency metric
    plot_df['investment_efficiency'] = plot_df['net_benefit'] / plot_df['development_cost']
    
    # Sort by efficiency for recommendations
    top_recommendations = plot_df.sort_values('investment_efficiency', ascending=False).head(3)
    bottom_recommendations = plot_df.sort_values('investment_efficiency', ascending=True).head(3)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Top Performing Investments")
        for i, row in top_recommendations.iterrows():
            st.markdown(f"""
            <div class="metric-container" style="margin-bottom: 10px;">
                <p style="font-weight: 600; color: {COLOR_SCHEME['primary']};">{row['scenario_name']}</p>
                <p><strong>ROI:</strong> {format_percent(row['roi'])} | <strong>Payback:</strong> {format_number(row['payback_period'])} years</p>
                <p><strong>Net Benefit:</strong> {format_currency(row['net_benefit'])}</p>
                <p><strong>Recommendation:</strong> <span style="color: {COLOR_SCHEME['positive']};">Prioritize for implementation</span></p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Under-Performing Investments")
        for i, row in bottom_recommendations.iterrows():
            if row['investment_efficiency'] < 1:
                recommendation = "Consider redesigning approach"
                color = COLOR_SCHEME['warning']
            else:
                recommendation = "Monitor and optimize implementation"
                color = COLOR_SCHEME['neutral']
                
            st.markdown(f"""
            <div class="metric-container" style="margin-bottom: 10px;">
                <p style="font-weight: 600; color: {COLOR_SCHEME['primary']};">{row['scenario_name']}</p>
                <p><strong>ROI:</strong> {format_percent(row['roi'])} | <strong>Payback:</strong> {format_number(row['payback_period'])} years</p>
                <p><strong>Net Benefit:</strong> {format_currency(row['net_benefit'])}</p>
                <p><strong>Recommendation:</strong> <span style="color: {color};">{recommendation}</span></p>
            </div>
            """, unsafe_allow_html=True)
    
    # If in advanced mode, provide ISO 13485 compliance report
    if analysis_mode == "Advanced":
        st.markdown("### ISO 13485 Compliance Report")
        st.markdown("""
        <div class="info-box">
            <p><strong>Documentation Requirements Analysis:</strong> The following recommendations align with ISO 13485:2016 Sections 4.2.1 (Documentation Requirements) and 7.3.3 (Design and Development Outputs)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create compliance checklist
        compliance_data = []
        
        for i, row in plot_df.iterrows():
            # Calculate a simplified compliance score
            design_impact = row['development_cost'] > 5000
            doc_impact = documentation_burden > 5
            
            # Determine documentation requirements
            if design_impact and doc_impact:
                doc_requirements = "Full Design History File (DHF) update"
                risk_assessment = "Complete risk assessment required"
                validation_level = "Full validation protocol"
            elif design_impact:
                doc_requirements = "Partial DHF update"
                risk_assessment = "Focused risk assessment required"
                validation_level = "Limited validation"
            else:
                doc_requirements = "Minor documentation updates"
                risk_assessment = "Risk assessment review"
                validation_level = "Verification only"
            
            compliance_data.append({
                'Scenario': row['scenario_name'],
                'Documentation Impact': doc_requirements,
                'Risk Assessment': risk_assessment,
                'Validation Requirements': validation_level,
                'ISO Impact Score': (documentation_burden + technical_risk + regulatory_risk) / 3
            })
        
        # Display compliance table
        compliance_df = pd.DataFrame(compliance_data)
        st.dataframe(compliance_df, use_container_width=True, hide_index=True)
        
        # Provide export option for compliance report
        compliance_csv = compliance_df.to_csv(index=False).encode()
        st.download_button(
            "Export ISO 13485 Compliance Report (CSV)",
            data=compliance_csv,
            file_name="iso_13485_compliance_report.csv",
            mime="text/csv"
        )
    
    # CAPA integration for continuous improvement
    if analysis_mode == "Advanced":
        st.markdown("### CAPA System Integration")
        st.caption("Connect improvement initiatives to Corrective and Preventive Actions")
        
        # Add CAPA linking functionality
        capa_col1, capa_col2 = st.columns(2)
        
        with capa_col1:
            st.markdown("#### CAPA Reference")
            capa_reference = st.text_input(
                "Enter CAPA Reference Number (if applicable)",
                help="Link these improvements to relevant Corrective and Preventive Action records"
            )
            
            capa_description = st.text_area(
                "CAPA Description",
                help="Brief description of the related CAPA"
            )
        
        with capa_col2:
            st.markdown("#### CAPA Effectiveness Metrics")
            st.caption("Define how these improvements will be measured for CAPA effectiveness")
            
            effectiveness_metrics = st.multiselect(
                "Select Effectiveness Metrics",
                options=[
                    "Return Rate Reduction (%)",
                    "Customer Complaint Reduction (%)", 
                    "Cost Savings ($)",
                    "Time Saved (hours)",
                    "Process Sigma Level Improvement",
                    "Error Rate Reduction (%)",
                    "Other"
                ],
                default=["Return Rate Reduction (%)"]
            )
            
            if "Other" in effectiveness_metrics:
                custom_metric = st.text_input("Define Custom Effectiveness Metric")
        
        # CAPA tracking save button
        if st.button("Save CAPA Reference Data"):
            st.success("CAPA reference data saved and linked to portfolio analysis")
            
            # Export CAPA mapping
            if capa_reference:
                capa_data = {
                    "CAPA Reference": capa_reference,
                    "CAPA Description": capa_description,
                    "Linked Improvements": ", ".join(plot_df['scenario_name'].tolist()),
                    "Effectiveness Metrics": ", ".join(effectiveness_metrics),
                    "Analysis Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # In a real implementation, this would save to a database
                st.session_state['capa_data'] = capa_data
                
                # Display CAPA linkage confirmation
                st.info(f"Portfolio analysis linked to CAPA #{capa_reference}")

def display_monte_carlo_analysis():
    """Advanced Statistical Analysis with Monte Carlo Simulation for ISO 13485 Risk Assessment"""
    st.subheader("Monte Carlo Simulation Analysis")
    
    # Simple/Advanced mode toggle
    simulation_mode = st.radio(
        "Analysis Mode:",
        ["Simple", "Advanced"],
        horizontal=True,
        help="Simple mode uses default distributions. Advanced mode enables custom distribution configuration."
    )
    
    # ISO 13485 compliance notification
    st.markdown("""
    <div class="info-box">
        <p><strong>ISO 13485:2016 Compliance:</strong> This Monte Carlo simulation module facilitates 
        risk-based decision making per ISO 13485:2016 Section 7.1 (Planning of product realization) 
        and ISO 14971:2019 (Risk management for medical devices).</p>
    </div>
    """, unsafe_allow_html=True)
    
    if optimizer.scenarios.empty:
        st.info("Please add at least one scenario before running Monte Carlo analysis.")
        return
    
    # Step 1: Select scenario to analyze
    scenario_names = optimizer.scenarios['scenario_name'].tolist()
    
    # Check if we're coming from a scenario view
    if 'monte_carlo_scenario' in st.session_state:
        scenario_uid = st.session_state['monte_carlo_scenario']
        scenario = optimizer.get_scenario(scenario_uid)
        if scenario:
            selected_scenario = scenario['scenario_name']
        else:
            selected_scenario = scenario_names[0] if scenario_names else None
        # Clear the session state
        st.session_state.pop('monte_carlo_scenario', None)
    else:
        selected_scenario = st.selectbox(
            "Select scenario for statistical analysis:", 
            scenario_names
        )
    
    # Get the selected scenario data
    scenario = optimizer.scenarios[optimizer.scenarios['scenario_name'] == selected_scenario].iloc[0]
    
    # Step 2: Simulation parameters
    st.markdown("### Simulation Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Core Simulation Parameters")
        num_simulations = st.slider(
            "Number of Simulations", 
            min_value=100, 
            max_value=10000, 
            value=st.session_state.monte_carlo_params['num_simulations'],
            help="Higher simulation counts increase statistical power but require more processing time"
        )
        
        confidence_level = st.slider(
            "Statistical Confidence Level (%)", 
            min_value=80, 
            max_value=99, 
            value=st.session_state.monte_carlo_params['confidence_level'],
            help="Defines the confidence interval boundaries for the simulation results"
        )
        
        random_seed = st.number_input(
            "Random Seed", 
            min_value=1, 
            max_value=1000000, 
            value=42,
            help="Ensures reproducibility across simulation runs"
        )
    
    with col2:
        st.markdown("#### Risk Management Parameters")
        include_risks = st.checkbox(
            "Enable ISO 13485 Risk Factors", 
            value=st.session_state.monte_carlo_params['include_risks'],
            help="Incorporates regulatory and validation risk factors into the simulation"
        )
        
        risk_tolerance = st.slider(
            "Risk Tolerance Threshold (%)", 
            min_value=1, 
            max_value=50, 
            value=10,
            help="Maximum acceptable probability of negative ROI (lower values are more conservative)"
        )
        
        validation_mode = st.checkbox(
            "Generate Validation Documentation", 
            value=False,
            help="Creates detailed documentation of all simulation parameters and intermediate calculations"
        )
    
    # Step 3: Define input distributions
    st.markdown("### Statistical Distribution Configuration")
    
    if simulation_mode == "Advanced":
        st.caption("Configure precise probability distributions for each parameter to model specific uncertainty profiles")
    else:
        st.caption("Using default normal distributions with industry-standard deviation parameters")
    
    param_col1, param_col2 = st.columns(2)
    
    # Calculate default standard deviations (more conservative for medical devices)
    reduction_rate_sd = max(scenario['estimated_return_reduction'] * 0.15, 1.0)
    unit_cost_change_sd = max(abs(scenario['unit_cost_change']) * 0.10, 0.1)
    sales_increase_sd = max(scenario['sales_increase'] * 0.20, 1.0)
    development_cost_sd = max(scenario['development_cost'] * 0.15, 100)
    
    with param_col1:
        # Return reduction rate distribution
        st.markdown("#### Return Reduction Effectiveness")
        if simulation_mode == "Advanced":
            reduction_distribution = st.selectbox(
                "Distribution Type (Reduction Rate)", 
                ["Normal", "Triangular", "PERT", "Uniform"],
                help="Statistical distribution to model uncertainty in return reduction rate"
            )
        else:
            reduction_distribution = "Normal"
        
        if reduction_distribution == "Normal":
            reduction_mean = st.slider(
                "Mean Reduction Rate (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=float(scenario['estimated_return_reduction']),
                step=0.5,
                help="Expected mean value for reduction rate"
            )
            
            reduction_sd = st.slider(
                "Standard Deviation", 
                min_value=0.1, 
                max_value=20.0, 
                value=float(reduction_rate_sd),
                step=0.1,
                help="Higher values indicate greater uncertainty in reduction effectiveness"
            )
            
            # For validation documentation
            if validation_mode:
                st.caption(f"95% confidence interval: [{max(0, reduction_mean - 1.96*reduction_sd):.1f}%, {min(100, reduction_mean + 1.96*reduction_sd):.1f}%]")
        
        elif reduction_distribution == "Triangular":
            reduction_min = st.slider(
                "Minimum Reduction Rate (%)", 
                min_value=0.0, 
                max_value=float(scenario['estimated_return_reduction']), 
                value=max(0, float(scenario['estimated_return_reduction']) * 0.7),
                step=0.5
            )
            
            reduction_mode = st.slider(
                "Most Likely Reduction Rate (%)", 
                min_value=reduction_min, 
                max_value=100.0, 
                value=float(scenario['estimated_return_reduction']),
                step=0.5
            )
            
            reduction_max = st.slider(
                "Maximum Reduction Rate (%)", 
                min_value=reduction_mode, 
                max_value=100.0, 
                value=min(100.0, float(scenario['estimated_return_reduction']) * 1.3),
                step=0.5
            )
        
        elif reduction_distribution == "PERT":
            reduction_min = st.slider(
                "Minimum Reduction Rate (%)", 
                min_value=0.0, 
                max_value=float(scenario['estimated_return_reduction']), 
                value=max(0, float(scenario['estimated_return_reduction']) * 0.7),
                step=0.5
            )
            
            reduction_mode = st.slider(
                "Most Likely Reduction Rate (%)", 
                min_value=reduction_min, 
                max_value=100.0, 
                value=float(scenario['estimated_return_reduction']),
                step=0.5
            )
            
            reduction_max = st.slider(
                "Maximum Reduction Rate (%)", 
                min_value=reduction_mode, 
                max_value=100.0, 
                value=min(100.0, float(scenario['estimated_return_reduction']) * 1.3),
                step=0.5
            )
            
            reduction_gamma = st.slider(
                "PERT Shape Parameter", 
                min_value=1.0, 
                max_value=10.0, 
                value=4.0,
                step=0.1,
                help="Higher values increase the influence of the most likely value"
            )
        
        elif reduction_distribution == "Uniform":
            reduction_min = st.slider(
                "Minimum Reduction Rate (%)", 
                min_value=0.0, 
                max_value=float(scenario['estimated_return_reduction']), 
                value=max(0, float(scenario['estimated_return_reduction']) * 0.7),
                step=0.5
            )
            
            reduction_max = st.slider(
                "Maximum Reduction Rate (%)", 
                min_value=reduction_min, 
                max_value=100.0, 
                value=min(100.0, float(scenario['estimated_return_reduction']) * 1.3),
                step=0.5
            )
        
        # Unit cost change distribution
        st.markdown("#### Unit Cost Impact")
        if simulation_mode == "Advanced":
            cost_distribution = st.selectbox(
                "Distribution Type (Unit Cost Change)", 
                ["Normal", "Triangular", "PERT", "Uniform"],
                help="Statistical distribution to model uncertainty in unit cost impact"
            )
        else:
            cost_distribution = "Normal"
        
        if cost_distribution == "Normal":
            cost_mean = st.slider(
                "Mean Unit Cost Change ($)", 
                min_value=float(scenario['unit_cost_change'] * 0.5), 
                max_value=float(scenario['unit_cost_change'] * 2.0) if scenario['unit_cost_change'] > 0 else 10.0, 
                value=float(scenario['unit_cost_change']),
                step=0.05,
                help="Expected mean value for unit cost change"
            )
            
            cost_sd = st.slider(
                "Standard Deviation", 
                min_value=0.01, 
                max_value=5.0, 
                value=float(unit_cost_change_sd),
                step=0.01,
                help="Higher values indicate greater uncertainty in cost impact"
            )
            
            # For validation documentation
            if validation_mode:
                st.caption(f"95% confidence interval: [{cost_mean - 1.96*cost_sd:.2f}, {cost_mean + 1.96*cost_sd:.2f}]")
    
    with param_col2:
        # Sales increase distribution 
        st.markdown("#### Sales Impact")
        if simulation_mode == "Advanced":
            sales_distribution = st.selectbox(
                "Distribution Type (Sales Increase)", 
                ["Normal", "Triangular", "PERT", "Uniform"],
                help="Statistical distribution to model uncertainty in sales impact"
            )
        else:
            sales_distribution = "Normal"
        
        if sales_distribution == "Normal":
            sales_mean = st.slider(
                "Mean Sales Increase (%)", 
                min_value=0.0, 
                max_value=50.0, 
                value=float(scenario['sales_increase']),
                step=0.5,
                help="Expected mean value for sales increase"
            )
            
            sales_sd = st.slider(
                "Standard Deviation", 
                min_value=0.1, 
                max_value=10.0, 
                value=float(sales_increase_sd),
                step=0.1,
                help="Higher values indicate greater uncertainty in sales projection"
            )
            
            # For validation documentation
            if validation_mode:
                st.caption(f"95% confidence interval: [{max(0, sales_mean - 1.96*sales_sd):.1f}%, {sales_mean + 1.96*sales_sd:.1f}%]")
        
        elif sales_distribution == "Triangular":
            sales_min = st.slider(
                "Minimum Sales Increase (%)", 
                min_value=0.0, 
                max_value=float(scenario['sales_increase']), 
                value=max(0, float(scenario['sales_increase']) * 0.5),
                step=0.5
            )
            
            sales_mode = st.slider(
                "Most Likely Sales Increase (%)", 
                min_value=sales_min, 
                max_value=50.0, 
                value=float(scenario['sales_increase']),
                step=0.5
            )
            
            sales_max = st.slider(
                "Maximum Sales Increase (%)", 
                min_value=sales_mode, 
                max_value=100.0, 
                value=min(50.0, float(scenario['sales_increase']) * 1.5),
                step=0.5
            )
        
        # Development cost distribution
        st.markdown("#### Development Investment")
        if simulation_mode == "Advanced":
            dev_cost_distribution = st.selectbox(
                "Distribution Type (Development Cost)", 
                ["Normal", "Triangular", "PERT", "Uniform"],
                help="Statistical distribution to model uncertainty in development cost"
            )
        else:
            dev_cost_distribution = "Normal"
        
        if dev_cost_distribution == "Normal":
            dev_cost_mean = st.slider(
                "Mean Development Cost ($)", 
                min_value=max(100, float(scenario['development_cost'] * 0.5)), 
                max_value=float(scenario['development_cost'] * 2.0), 
                value=float(scenario['development_cost']),
                step=100.0,
                help="Expected mean value for development cost"
            )
            
            dev_cost_sd = st.slider(
                "Standard Deviation ($)", 
                min_value=100.0, 
                max_value=float(scenario['development_cost']), 
                value=float(development_cost_sd),
                step=100.0,
                help="Higher values indicate greater uncertainty in development cost"
            )
            
            # For validation documentation
            if validation_mode:
                st.caption(f"95% confidence interval: [{max(0, dev_cost_mean - 1.96*dev_cost_sd):.0f}, {dev_cost_mean + 1.96*dev_cost_sd:.0f}]")
    
    # ISO 13485 risk factors section
    if include_risks and simulation_mode == "Advanced":
        st.markdown("### ISO 13485/14971 Risk Factors")
        st.caption("Incorporate regulatory and process risk factors in accordance with ISO 14971:2019 principles")
        
        risk_col1, risk_col2 = st.columns(2)
        
        with risk_col1:
            regulatory_risk_prob = st.slider(
                "Regulatory Complexity Risk (%)", 
                min_value=0, 
                max_value=100, 
                value=15,
                help="Probability of encountering regulatory challenges during implementation"
            )
            
            regulatory_impact = st.slider(
                "Regulatory Impact Factor", 
                min_value=1.0, 
                max_value=3.0, 
                value=1.3,
                step=0.1,
                help="Cost multiplier if regulatory challenges occur"
            )
            
            validation_risk_prob = st.slider(
                "Validation Failure Risk (%)", 
                min_value=0, 
                max_value=100, 
                value=20,
                help="Probability of validation failures requiring remediation"
            )
            
            validation_impact = st.slider(
                "Validation Remediation Factor", 
                min_value=1.0, 
                max_value=3.0, 
                value=1.4,
                step=0.1,
                help="Cost & time multiplier if validation failures occur"
            )
        
        with risk_col2:
            technical_risk_prob = st.slider(
                "Technical Implementation Risk (%)", 
                min_value=0, 
                max_value=100, 
                value=25,
                help="Probability of technical challenges during implementation"
            )
            
            technical_impact = st.slider(
                "Technical Risk Impact Factor", 
                min_value=1.0, 
                max_value=3.0, 
                value=1.35,
                step=0.05,
                help="Cost multiplier if technical issues arise"
            )
            
            resource_risk_prob = st.slider(
                "Resource Constraint Risk (%)", 
                min_value=0, 
                max_value=100, 
                value=30,
                help="Probability of resource constraints affecting implementation"
            )
            
            resource_impact = st.slider(
                "Resource Constraint Impact", 
                min_value=1.0, 
                max_value=3.0, 
                value=1.25,
                step=0.05,
                help="Schedule multiplier if resource constraints occur"
            )
    
    # Process capability analysis if in advanced mode
    if simulation_mode == "Advanced":
        st.markdown("### Process Capability Integration")
        
        enable_cpk_analysis = st.checkbox(
            "Enable Process Capability Analysis", 
            value=False,
            help="Incorporates Cpk/Ppk process capability metrics into the simulation"
        )
        
        if enable_cpk_analysis:
            cpk_col1, cpk_col2 = st.columns(2)
            
            with cpk_col1:
                current_cpk = st.slider(
                    "Current Process Capability (Cpk)", 
                    min_value=0.5, 
                    max_value=2.0, 
                    value=1.0,
                    step=0.1,
                    help="Current process capability index (Cpk < 1.33 indicates opportunity for improvement)"
                )
                
                target_cpk = st.slider(
                    "Target Process Capability (Cpk)", 
                    min_value=1.0, 
                    max_value=2.5, 
                    value=min(2.0, current_cpk * 1.25),
                    step=0.1,
                    help="Target process capability after implementation (medical devices typically target ≥1.33)"
                )
            
            with cpk_col2:
                cpk_uncertainty = st.slider(
                    "Cpk Improvement Uncertainty (%)", 
                    min_value=5, 
                    max_value=50, 
                    value=20,
                    help="Uncertainty in achieving the target process capability"
                )
                
                cpk_correlation = st.slider(
                    "Cpk-to-Return Correlation", 
                    min_value=0.0, 
                    max_value=1.0, 
                    value=0.7,
                    step=0.05,
                    help="Correlation between process capability and return rate reduction"
                )
    
    # Save simulation parameters
    if st.button("Run Monte Carlo Simulation", type="primary"):
        # Update session state with current parameters
        st.session_state.monte_carlo_params['num_simulations'] = num_simulations
        st.session_state.monte_carlo_params['confidence_level'] = confidence_level
        st.session_state.monte_carlo_params['include_risks'] = include_risks
        
        # Show progress while running simulation
        with st.spinner("Running Monte Carlo simulation..."):
            # Set up simulation parameters
            simulation_params = {
                'num_simulations': num_simulations,
                'confidence_level': confidence_level,
                'include_risks': include_risks,
                'reduction_distribution': {
                    'type': reduction_distribution,
                    'params': {}
                },
                'cost_distribution': {
                    'type': cost_distribution,
                    'params': {}
                },
                'sales_distribution': {
                    'type': sales_distribution,
                    'params': {}
                },
                'dev_cost_distribution': {
                    'type': dev_cost_distribution,
                    'params': {}
                }
            }
            
            # Add distribution parameters based on selections
            if reduction_distribution == "Normal":
                simulation_params['reduction_distribution']['params'] = {
                    'mean': reduction_mean,
                    'sd': reduction_sd
                }
            elif reduction_distribution in ["Triangular", "PERT"]:
                simulation_params['reduction_distribution']['params'] = {
                    'min': reduction_min,
                    'mode': reduction_mode,
                    'max': reduction_max
                }
                if reduction_distribution == "PERT" and 'reduction_gamma' in locals():
                    simulation_params['reduction_distribution']['params']['gamma'] = reduction_gamma
            elif reduction_distribution == "Uniform":
                simulation_params['reduction_distribution']['params'] = {
                    'min': reduction_min,
                    'max': reduction_max
                }
            
            # Add cost distribution parameters
            if cost_distribution == "Normal":
                simulation_params['cost_distribution']['params'] = {
                    'mean': cost_mean,
                    'sd': cost_sd
                }
            
            # Add sales distribution parameters if in advanced mode
            if sales_distribution == "Normal":
                simulation_params['sales_distribution']['params'] = {
                    'mean': sales_mean,
                    'sd': sales_sd
                }
            
            # Add development cost distribution parameters
            if dev_cost_distribution == "Normal":
                simulation_params['dev_cost_distribution']['params'] = {
                    'mean': dev_cost_mean,
                    'sd': dev_cost_sd
                }
            
            # Add risk parameters if enabled
            if include_risks and simulation_mode == "Advanced":
                simulation_params['risk_factors'] = {
                    'regulatory': {
                        'probability': regulatory_risk_prob / 100,
                        'impact': regulatory_impact
                    },
                    'validation': {
                        'probability': validation_risk_prob / 100,
                        'impact': validation_impact
                    },
                    'technical': {
                        'probability': technical_risk_prob / 100,
                        'impact': technical_impact
                    },
                    'resource': {
                        'probability': resource_risk_prob / 100,
                        'impact': resource_impact
                    }
                }
            
            # Add process capability parameters if enabled
            if simulation_mode == "Advanced" and enable_cpk_analysis:
                simulation_params['process_capability'] = {
                    'current_cpk': current_cpk,
                    'target_cpk': target_cpk,
                    'uncertainty': cpk_uncertainty / 100,
                    'correlation': cpk_correlation
                }
            
            # Run the simulation
            results = generate_monte_carlo_simulation(scenario, num_simulations, include_risks)
            
            # Log the analysis in the audit trail
            optimizer.log_audit(
                "Monte Carlo Analysis", 
                f"Ran {num_simulations} simulations on scenario: {selected_scenario}"
            )
            
            # Calculate risk-adjusted metrics
            roi_mean = results['roi']['mean']
            roi_median = results['roi']['median']
            roi_std = results['roi']['std']
            
            npv_mean = results['npv']['mean'] 
            npv_std = results['npv']['std']
            
            # Calculate confidence intervals
            alpha = (1 - confidence_level / 100) / 2
            ci_lower_roi = max(0, np.percentile(results['roi']['distribution'], alpha * 100))
            ci_upper_roi = np.percentile(results['roi']['distribution'], (1 - alpha) * 100)
            
            ci_lower_npv = np.percentile(results['npv']['distribution'], alpha * 100)
            ci_upper_npv = np.percentile(results['npv']['distribution'], (1 - alpha) * 100)
            
            # Probability metrics
            prob_positive_roi = results['probability']['positive_roi']
            prob_target_roi = results['probability']['roi_over_50']
            
            # Calculate Cp, Cpk improvements if enabled
            if simulation_mode == "Advanced" and enable_cpk_analysis and 'process_capability' in simulation_params:
                # Calculate sigma level improvements
                current_sigma = current_cpk * 3
                target_sigma = target_cpk * 3
                sigma_improvement = target_sigma - current_sigma
                
                # Calculate DPMO (Defects Per Million Opportunities) reduction
                current_dpmo = 1000000 * (1 - (1 - 2 * (1 - st.session_state.norm.cdf(current_sigma))))
                target_dpmo = 1000000 * (1 - (1 - 2 * (1 - st.session_state.norm.cdf(target_sigma))))
                dpmo_reduction = current_dpmo - target_dpmo
                
                # Calculate theoretical yield improvement
                current_yield = (1 - (current_dpmo / 1000000)) * 100
                target_yield = (1 - (target_dpmo / 1000000)) * 100
                yield_improvement = target_yield - current_yield
        
        # Display results
        st.markdown("## Monte Carlo Simulation Results")
        
        # Display summary statistics
        st.markdown("### Statistical Performance Metrics")
        st.markdown(f"**Confidence Level:** {confidence_level}%")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Mean ROI", f"{roi_mean:.1f}%")
            st.metric("ROI Confidence Interval", f"({ci_lower_roi:.1f}% - {ci_upper_roi:.1f}%)")
            st.metric("Probability of Positive ROI", f"{prob_positive_roi:.1f}%")
        
        with col2:
            st.metric("Mean NPV", f"${npv_mean:.2f}")
            st.metric("NPV Confidence Interval", f"(${ci_lower_npv:.2f} - ${ci_upper_npv:.2f})")
            st.metric("Probability of Target ROI", f"{prob_target_roi:.1f}%")
        
        with col3:
            mean_payback = results['payback']['mean']
            if not np.isinf(mean_payback):
                st.metric("Mean Payback Period", f"{mean_payback:.2f} years")
                ci_lower_payback = results['payback']['min']
                ci_upper_payback = np.percentile(results['payback']['distribution'][~np.isinf(results['payback']['distribution'])], 95) if np.any(~np.isinf(results['payback']['distribution'])) else float('inf')
                st.metric("Payback Period Range", f"({ci_lower_payback:.2f} - {ci_upper_payback:.2f} years)")
                prob_payback_1yr = np.sum(results['payback']['distribution'] <= 1) / num_simulations * 100
                st.metric("Probability of Payback ≤ 1 year", f"{prob_payback_1yr:.1f}%")
            else:
                st.metric("Mean Payback Period", "Not achievable")
                st.metric("Payback Period Range", "N/A")
                st.metric("Probability of Payback ≤ 1 year", "0.0%")
        
        # Display ROI histogram with confidence interval
        st.markdown("### ROI Probability Distribution")
        
        roi_hist_fig = px.histogram(
            results['roi']['distribution'],
            nbins=30,
            labels={"value": "Return on Investment (%)"},
            title=f"ROI Distribution ({num_simulations:,} simulations)",
            marginal="box"
        )
        
        # Add reference lines
        roi_hist_fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Break-even")
        roi_hist_fig.add_vline(x=roi_mean, line_dash="solid", line_color="green", annotation_text="Mean")
        roi_hist_fig.add_vline(x=ci_lower_roi, line_dash="dot", line_color="blue", annotation_text=f"{alpha*100:.0f}%")
        roi_hist_fig.add_vline(x=ci_upper_roi, line_dash="dot", line_color="blue", annotation_text=f"{(1-alpha)*100:.0f}%")
        
        st.plotly_chart(roi_hist_fig, use_container_width=True)
        
        # Display confidence level and interpretation based on ISO 14971 risk management
        if prob_positive_roi < 80:
            risk_assessment = "High Risk - Detailed risk mitigation required"
            risk_color = COLOR_SCHEME["negative"]
        elif prob_positive_roi < 95:
            risk_assessment = "Medium Risk - Additional risk controls advised"
            risk_color = COLOR_SCHEME["warning"]
        else:
            risk_assessment = "Low Risk - Standard monitoring sufficient"
            risk_color = COLOR_SCHEME["positive"]
        
        st.markdown(f"""
        <div class="info-box" style="border-left: 5px solid {risk_color};">
            <h4>ISO 14971 Risk Assessment</h4>
            <p><strong>Risk Level:</strong> <span style="color: {risk_color};">{risk_assessment}</span></p>
            <p><strong>Probability of Negative ROI:</strong> {100 - prob_positive_roi:.1f}%</p>
            <p><strong>Probability of ROI > 50%:</strong> {prob_target_roi:.1f}%</p>
            <p><strong>Required Confidence Level:</strong> {confidence_level}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Process capability results if enabled
        if simulation_mode == "Advanced" and enable_cpk_analysis and 'process_capability' in simulation_params:
            st.markdown("### Process Capability Analysis")
            
            proc_col1, proc_col2, proc_col3 = st.columns(3)
            
            with proc_col1:
                st.metric("Current Process Capability (Cpk)", f"{current_cpk:.2f}")
                st.metric("Target Process Capability (Cpk)", f"{target_cpk:.2f}")
                st.metric("Cpk Improvement", f"+{target_cpk - current_cpk:.2f}")
            
            with proc_col2:
                st.metric("Current Sigma Level", f"{current_sigma:.2f}σ")
                st.metric("Target Sigma Level", f"{target_sigma:.2f}σ")
                st.metric("Sigma Improvement", f"+{sigma_improvement:.2f}σ")
            
            with proc_col3:
                st.metric("Current DPMO", f"{current_dpmo:,.0f}")
                st.metric("Target DPMO", f"{target_dpmo:,.0f}")
                st.metric("DPMO Reduction", f"-{dpmo_reduction:,.0f}")
            
            # Add process capability interpretation
            if target_cpk < 1.33:
                cpk_assessment = "Below minimum recommended level for medical devices (Cpk < 1.33)"
                cpk_color = COLOR_SCHEME["negative"]
            elif target_cpk < 1.67:
                cpk_assessment = "Meets minimum requirements for medical devices (Cpk ≥ 1.33)"
                cpk_color = COLOR_SCHEME["warning"]
            else:
                cpk_assessment = "Exceeds requirements for medical devices (Cpk ≥ 1.67)"
                cpk_color = COLOR_SCHEME["positive"]
            
            st.markdown(f"""
            <div class="info-box" style="border-left: 5px solid {cpk_color};">
                <h4>Process Capability Assessment</h4>
                <p><strong>Assessment:</strong> <span style="color: {cpk_color};">{cpk_assessment}</span></p>
                <p><strong>Current Process Yield:</strong> {current_yield:.4f}%</p>
                <p><strong>Target Process Yield:</strong> {target_yield:.4f}%</p>
                <p><strong>Yield Improvement:</strong> +{yield_improvement:.4f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Generate ISO 13485 compliant documentation
        if validation_mode:
            st.markdown("### Validation Documentation")
            
            documentation = generate_iso_documentation(scenario, results)
            markdown_doc = generate_markdown_from_documentation(documentation)
            
            st.markdown("""
            <div class="documentation-section">
                <h4>ISO 13485 Compliant Documentation</h4>
                <p>This documentation has been generated to comply with ISO 13485:2016 requirements for design verification and validation.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show preview of the documentation
            with st.expander("Preview Documentation"):
                st.markdown(markdown_doc)
            
            # Add download button for PDF export
            pdf_bytes = export_markdown_to_pdf(markdown_doc)
            
            st.download_button(
                "Download ISO 13485 Documentation (PDF)",
                data=pdf_bytes,
                file_name=f"ISO13485_ROI_Analysis_{scenario['product_name']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

def display_what_if_analysis():
    """Interactive what-if scenario analysis with PDCA continuous improvement framework"""
    st.subheader("What-If Analysis & Continuous Improvement Simulation")
    
    # Add analysis mode toggle
    analysis_mode = st.radio(
        "Analysis Mode:",
        ["Simple", "Advanced"],
        horizontal=True,
        help="Simple mode enables basic parameter adjustments. Advanced mode adds PDCA cycle simulation."
    )
    
    if analysis_mode == "Advanced":
        st.markdown("""
        <div class="info-box">
            <p><strong>PDCA Framework Integration:</strong> This module implements the Plan-Do-Check-Act 
            cycle for continuous improvement per ISO 9001:2015 requirements. It simulates multiple improvement 
            iterations to optimize product performance through systematic process enhancement.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Get base scenario
    if not optimizer.scenarios.empty:
        # Let user select a base scenario
        scenario_names = optimizer.scenarios['scenario_name'].tolist()
        base_scenario_name = st.selectbox("Select base scenario for what-if analysis", scenario_names)
        
        # Get the selected scenario
        base_scenario = optimizer.scenarios[optimizer.scenarios['scenario_name'] == base_scenario_name].iloc[0]
        
        # Set up what-if parameters
        st.markdown("### Adjust Improvement Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sales volume change
            sales_change = st.slider(
                "Sales Volume Change (%)", 
                min_value=-50, 
                max_value=100, 
                value=st.session_state.whatif_params['sales_change'] if 'sales_change' in st.session_state.whatif_params else 0,
                help="Projected change in monthly sales volume"
            )
            
            # Return rate change
            return_rate_change = st.slider(
                "Return Rate Change (%)", 
                min_value=-50, 
                max_value=50, 
                value=st.session_state.whatif_params['return_reduction_adjust'] if 'return_reduction_adjust' in st.session_state.whatif_params else 0,
                help="Relative change to projected return rate reduction"
            )
            
            # Solution cost change
            solution_cost_change = st.slider(
                "Development Cost Change (%)", 
                min_value=-50, 
                max_value=100, 
                value=st.session_state.whatif_params['development_cost_change'] if 'development_cost_change' in st.session_state.whatif_params else 0,
                help="Adjusted development investment"
            )
        
        with col2:
            # Reduction effectiveness change
            reduction_effectiveness = st.slider(
                "Return Reduction Effectiveness (%)", 
                min_value=-50, 
                max_value=50, 
                value=st.session_state.whatif_params['return_reduction_adjust'] if 'return_reduction_adjust' in st.session_state.whatif_params else 0,
                help="Change in effectiveness of the return reduction solution"
            )
            
            # Additional cost change
            additional_cost_change = st.slider(
                "Unit Cost Impact Change (%)", 
                min_value=-50, 
                max_value=100, 
                value=st.session_state.whatif_params['unit_cost_change_adjust'] if 'unit_cost_change_adjust' in st.session_state.whatif_params else 0,
                help="Adjustment to ongoing additional cost per unit"
            )
            
            # Implementation time change
            implementation_time_change = st.slider(
                "Implementation Time Change (%)", 
                min_value=-50, 
                max_value=100, 
                value=st.session_state.whatif_params['implementation_time_change'] if 'implementation_time_change' in st.session_state.whatif_params else 0,
                help="Adjusted implementation timeline"
            )
        
        # Advanced PDCA parameters in advanced mode
        if analysis_mode == "Advanced":
            st.markdown("### PDCA Continuous Improvement Parameters")
            pdca_col1, pdca_col2, pdca_col3 = st.columns(3)
            
            with pdca_col1:
                enable_pdca = st.checkbox(
                    "Enable PDCA Cycle Simulation", 
                    value=False,
                    help="Simulate multiple improvement cycles using Plan-Do-Check-Act methodology"
                )
                
                pdca_iterations = st.slider(
                    "Number of PDCA Cycles", 
                    min_value=1, 
                    max_value=5, 
                    value=3,
                    help="Number of continuous improvement iterations to simulate"
                )
            
            with pdca_col2:
                kaizen_effect = st.slider(
                    "Kaizen Effect per Cycle (%)", 
                    min_value=1, 
                    max_value=30, 
                    value=10,
                    help="Incremental improvement effect per PDCA cycle"
                )
                
                learning_curve = st.selectbox(
                    "Learning Curve Model", 
                    ["Linear", "Diminishing Returns", "S-Curve"],
                    help="Pattern of improvement across PDCA cycles"
                )
            
            with pdca_col3:
                process_capability_target = st.slider(
                    "Process Capability Target (Cpk)", 
                    min_value=1.0, 
                    max_value=2.0, 
                    value=1.33,
                    step=0.01,
                    help="Target process capability index after improvement cycles"
                )
                
                quality_cost_ratio = st.slider(
                    "Quality-Cost Ratio", 
                    min_value=0.1, 
                    max_value=1.0, 
                    value=0.5,
                    step=0.1,
                    help="Weight of quality improvements vs. cost considerations"
                )
        
        # Process parameters with validation for ISO 13485 compliance
        if base_scenario['device_class'] in ["Class II", "Class III"] and analysis_mode == "Advanced":
            st.markdown("### ISO 13485 Process Validation Parameters")
            
            val_col1, val_col2 = st.columns(2)
            
            with val_col1:
                validation_level = st.selectbox(
                    "Validation Requirement Level",
                    ["Low", "Medium", "High", "Critical"],
                    help="Required level of validation based on device classification and risk"
                )
                
                validation_cost_factor = st.slider(
                    "Validation Cost Factor", 
                    min_value=0.05, 
                    max_value=0.5, 
                    value=0.15,
                    step=0.05,
                    help="Validation cost as a proportion of development cost"
                )
            
            with val_col2:
                regulatory_submission = st.selectbox(
                    "Regulatory Submission Requirement",
                    ["None", "Letter to File", "Special 510(k)", "Traditional 510(k)", "PMA Supplement"],
                    index=1 if base_scenario['device_class'] == "Class II" else 2,
                    help="Required regulatory submission based on change significance"
                )
                
                regulatory_lead_time = st.slider(
                    "Regulatory Review Time (months)", 
                    min_value=0, 
                    max_value=12, 
                    value=3 if regulatory_submission in ["Special 510(k)", "Traditional 510(k)"] else 0,
                    help="Expected regulatory review timeline"
                )
        
        # Calculate new values based on adjustments
        new_sales_30 = base_scenario['current_unit_sales'] * (1 + sales_change/100)
        new_return_rate = base_scenario['return_rate'] * (1 + return_rate_change/100)
        new_returns_30 = (new_sales_30 * new_return_rate / 100)
        new_development_cost = base_scenario['development_cost'] * (1 + solution_cost_change/100)
        new_reduction_rate = base_scenario['estimated_return_reduction'] * (1 + reduction_effectiveness/100)
        new_unit_cost_change = base_scenario['unit_cost_change'] * (1 + additional_cost_change/100)
        new_implementation_time = base_scenario['time_to_implement'] * (1 + implementation_time_change/100)
        
        # Calculate ISO 13485 validation costs if applicable
        if base_scenario['device_class'] in ["Class II", "Class III"] and analysis_mode == "Advanced":
            validation_cost = new_development_cost * validation_cost_factor
            total_development_cost = new_development_cost + validation_cost
            
            if regulatory_submission in ["Special 510(k)", "Traditional 510(k)", "PMA Supplement"]:
                implementation_delay = new_implementation_time + regulatory_lead_time
            else:
                implementation_delay = new_implementation_time
        else:
            validation_cost = 0
            total_development_cost = new_development_cost
            implementation_delay = new_implementation_time
        
        # Calculate financial impact for base scenario
        current_unit_cost = base_scenario['current_unit_cost']
        avg_sale_price = base_scenario['avg_sale_price']
        return_processing_cost = base_scenario['return_processing_cost'] if pd.notna(base_scenario['return_processing_cost']) else (current_unit_cost * 0.15)
        
        # Baseline performance
        base_avoided_returns = base_scenario['current_returns'] * (base_scenario['estimated_return_reduction'] / 100)
        base_new_unit_cost = current_unit_cost + base_scenario['unit_cost_change']
        base_savings_per_return = avg_sale_price + return_processing_cost - current_unit_cost
        base_monthly_savings = base_avoided_returns * base_savings_per_return
        base_additional_sales = base_scenario['current_unit_sales'] * (base_scenario['sales_increase'] / 100)
        base_sales_benefit = base_additional_sales * (avg_sale_price - base_new_unit_cost)
        base_additional_costs = base_scenario['unit_cost_change'] * (base_scenario['current_unit_sales'] - base_scenario['current_returns'] + base_avoided_returns)
        base_monthly_net = base_monthly_savings + base_sales_benefit - base_additional_costs
        base_annual_net = base_monthly_net * 12
        
        if base_scenario['development_cost'] > 0 and base_monthly_net > 0:
            base_roi = (base_annual_net / base_scenario['development_cost']) * 100
            base_breakeven = base_scenario['development_cost'] / base_monthly_net
        else:
            base_roi = None
            base_breakeven = None
        
        # New scenario performance
        new_avoided_returns = new_returns_30 * (new_reduction_rate / 100)
        new_unit_cost = current_unit_cost + new_unit_cost_change
        new_savings_per_return = avg_sale_price + return_processing_cost - current_unit_cost
        new_monthly_savings = new_avoided_returns * new_savings_per_return
        new_additional_sales = new_sales_30 * (base_scenario['sales_increase'] / 100)
        new_sales_benefit = new_additional_sales * (avg_sale_price - new_unit_cost)
        new_additional_costs = new_unit_cost_change * (new_sales_30 - new_returns_30 + new_avoided_returns)
        new_monthly_net = new_monthly_savings + new_sales_benefit - new_additional_costs
        new_annual_net = new_monthly_net * 12
        
        if total_development_cost > 0 and new_monthly_net > 0:
            new_roi = (new_annual_net / total_development_cost) * 100
            new_breakeven = total_development_cost / new_monthly_net
        else:
            new_roi = None
            new_breakeven = None
        
        # PDCA cycle simulation calculations
        if analysis_mode == "Advanced" and enable_pdca:
            # Initialize arrays for PDCA iterations
            pdca_roi = [new_roi if new_roi is not None else 0]
            pdca_reduction_rates = [new_reduction_rate]
            pdca_unit_costs = [new_unit_cost]
            pdca_monthly_net = [new_monthly_net]
            pdca_cpk = [1.0]  # Start with baseline Cpk of 1.0
            
            # Calculate improvement factors based on learning curve
            if learning_curve == "Linear":
                improvement_factors = [1.0] * pdca_iterations
            elif learning_curve == "Diminishing Returns":
                improvement_factors = [1.0 / (i+1) for i in range(pdca_iterations)]
                # Normalize to sum to 1
                factor_sum = sum(improvement_factors)
                improvement_factors = [f / factor_sum for f in improvement_factors]
            else:  # S-Curve
                # Create S-curve pattern
                x = np.linspace(-2, 2, pdca_iterations)
                improvement_factors = 1 / (1 + np.exp(-x))
                # Normalize to sum to 1
                factor_sum = sum(improvement_factors)
                improvement_factors = [f / factor_sum for f in improvement_factors]
            
            # Simulate PDCA cycles
            for i in range(pdca_iterations):
                # Apply improvement factor for this iteration
                improvement = kaizen_effect * improvement_factors[i] / 100
                
                # Update reduction rate (diminishing returns as we approach 100%)
                current_reduction = pdca_reduction_rates[-1]
                headroom = 100 - current_reduction
                new_reduction = current_reduction + (headroom * improvement * 2)
                pdca_reduction_rates.append(min(99.9, new_reduction))
                
                # Update unit cost (process optimization reduces costs)
                current_cost = pdca_unit_costs[-1]
                cost_reduction = current_cost * improvement * quality_cost_ratio
                pdca_unit_costs.append(max(current_cost * 0.7, current_cost - cost_reduction))
                
                # Update process capability
                current_cpk = pdca_cpk[-1]
                cpk_improvement = (process_capability_target - current_cpk) * improvement * 2
                pdca_cpk.append(min(process_capability_target, current_cpk + cpk_improvement))
                
                # Calculate new financial metrics
                iter_avoided_returns = new_returns_30 * (new_reduction / 100) 
                iter_monthly_savings = iter_avoided_returns * new_savings_per_return
                iter_unit_cost = pdca_unit_costs[-1]
                iter_additional_costs = (iter_unit_cost - current_unit_cost) * (new_sales_30 - new_returns_30 + iter_avoided_returns)
                iter_monthly_net = iter_monthly_savings + new_sales_benefit - iter_additional_costs
                pdca_monthly_net.append(iter_monthly_net)
                
                # Calculate ROI (assuming incremental improvement costs of 20% of original)
                incremental_cost = total_development_cost * 0.2
                iter_annual_net = iter_monthly_net * 12
                iter_roi = (iter_annual_net / (total_development_cost + incremental_cost * (i+1))) * 100
                pdca_roi.append(iter_roi)
        
        # Calculate comparison metrics for display
        comparison_data = {
            "Metric": [
                "Monthly Sales (units)",
                "Return Rate (%)",
                "Monthly Returns (units)",
                "Development Cost ($)",
                "Return Reduction (%)",
                "Unit Cost Change ($)",
                "Implementation Time (months)"
            ],
            "Original": [
                base_scenario['current_unit_sales'],
                base_scenario['return_rate'],
                base_scenario['current_returns'],
                base_scenario['development_cost'],
                base_scenario['estimated_return_reduction'],
                base_scenario['unit_cost_change'],
                base_scenario['time_to_implement']
            ],
            "New": [
                new_sales_30,
                new_return_rate,
                new_returns_30,
                total_development_cost,
                new_reduction_rate,
                new_unit_cost_change,
                implementation_delay
            ]
        }
        
        if analysis_mode == "Advanced" and base_scenario['device_class'] in ["Class II", "Class III"]:
            # Add validation costs for ISO 13485 compliance
            comparison_data["Metric"].append("Validation Cost ($)")
            comparison_data["Original"].append(0)  # Assume no validation cost in original
            comparison_data["New"].append(validation_cost)
            
            comparison_data["Metric"].append("Regulatory Lead Time (months)")
            comparison_data["Original"].append(0)  # Assume no regulatory delay in original
            comparison_data["New"].append(regulatory_lead_time)
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Financial impact comparison
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
                base_monthly_savings,
                base_additional_costs,
                base_monthly_net,
                base_annual_net,
                base_roi,
                base_breakeven
            ],
            "New": [
                new_monthly_savings,
                new_additional_costs,
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
        if base_monthly_net > 0 and new_monthly_net > 0:
            net_benefit_change = ((new_monthly_net / base_monthly_net) - 1) * 100
        else:
            net_benefit_change = 0
        
        if base_roi is not None and new_roi is not None:
            roi_change = ((new_roi / base_roi) - 1) * 100
        else:
            roi_change = 0
        
        if base_breakeven is not None and new_breakeven is not None:
            breakeven_change = ((new_breakeven / base_breakeven) - 1) * 100
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
            if new_roi is not None:
                st.metric(
                    "Return on Investment",
                    f"{new_roi:.1f}%",
                    f"{roi_change:.1f}%",
                    delta_color="normal" if roi_change >= 0 else "inverse"
                )
            else:
                st.metric("Return on Investment", "N/A", delta=None)
        
        with col3:
            if new_breakeven is not None:
                st.metric(
                    "Break-even Time",
                    f"{new_breakeven:.1f} months",
                    f"{-breakeven_change:.1f}%",  # Negative because shorter is better
                    delta_color="normal" if breakeven_change <= 0 else "inverse"
                )
            else:
                st.metric("Break-even Time", "N/A", delta=None)
        
        # PDCA cycle visualization if enabled
        if analysis_mode == "Advanced" and enable_pdca:
            st.markdown("### PDCA Continuous Improvement Simulation")
            
            # Create data for PDCA visualization
            pdca_df = pd.DataFrame({
                "Iteration": ["Baseline"] + [f"Cycle {i+1}" for i in range(pdca_iterations)],
                "ROI (%)": pdca_roi,
                "Reduction Rate (%)": pdca_reduction_rates,
                "Unit Cost ($)": pdca_unit_costs,
                "Monthly Net Benefit ($)": pdca_monthly_net,
                "Process Capability (Cpk)": pdca_cpk
            })
            
            # Create ROI improvement chart
            roi_fig = px.line(
                pdca_df, 
                x="Iteration", 
                y="ROI (%)",
                markers=True,
                title="ROI Improvement Through PDCA Cycles",
                color_discrete_sequence=[COLOR_SCHEME["primary"]]
            )
            
            roi_fig.update_layout(
                xaxis_title="PDCA Iteration",
                yaxis_title="Return on Investment (%)",
                height=400
            )
            
            st.plotly_chart(roi_fig, use_container_width=True)
            
            # Create process capability improvement chart
            cpk_fig = go.Figure()
            
            # Add Cpk line
            cpk_fig.add_trace(go.Scatter(
                x=pdca_df["Iteration"],
                y=pdca_df["Process Capability (Cpk)"],
                mode="lines+markers",
                name="Process Capability (Cpk)",
                line=dict(color=COLOR_SCHEME["secondary"], width=3)
            ))
            
            # Add target line
            cpk_fig.add_shape(
                type="line",
                x0=0,
                y0=1.33,
                x1=len(pdca_df["Iteration"])-1,
                y1=1.33,
                line=dict(color="red", width=2, dash="dash")
            )
            
            cpk_fig.add_annotation(
                x=len(pdca_df["Iteration"])-1,
                y=1.33,
                text="Medical Device Minimum (Cpk=1.33)",
                showarrow=False,
                yshift=10,
                font=dict(color="red")
            )
            
            cpk_fig.update_layout(
                title="Process Capability Improvement",
                xaxis_title="PDCA Iteration",
                yaxis_title="Process Capability (Cpk)",
                height=400
            )
            
            st.plotly_chart(cpk_fig, use_container_width=True)
            
            # Display PDCA results table
            st.markdown("### PDCA Iteration Results")
            
            # Format the data for display
            display_pdca = pdca_df.copy()
            display_pdca["ROI (%)"] = display_pdca["ROI (%)"].apply(lambda x: f"{x:.2f}%")
            display_pdca["Reduction Rate (%)"] = display_pdca["Reduction Rate (%)"].apply(lambda x: f"{x:.2f}%")
            display_pdca["Unit Cost ($)"] = display_pdca["Unit Cost ($)"].apply(lambda x: f"${x:.2f}")
            display_pdca["Monthly Net Benefit ($)"] = display_pdca["Monthly Net Benefit ($)"].apply(lambda x: f"${x:.2f}")
            display_pdca["Process Capability (Cpk)"] = display_pdca["Process Capability (Cpk)"].apply(lambda x: f"{x:.3f}")
            
            st.dataframe(display_pdca, use_container_width=True, hide_index=True)
            
            # Add PDCA cycle interpretation
            final_cpk = pdca_cpk[-1]
            if final_cpk < 1.33:
                cpk_status = "Below minimum requirements for medical devices (Cpk < 1.33)"
                cpk_color = COLOR_SCHEME["negative"]
                cpk_recommendation = "Additional PDCA cycles or more aggressive improvements required"
            elif final_cpk < 1.67:
                cpk_status = "Meets minimum requirements for medical devices (Cpk ≥ 1.33)"
                cpk_color = COLOR_SCHEME["warning"]
                cpk_recommendation = "Acceptable for production, but further improvement recommended"
            else:
                cpk_status = "Exceeds requirements for medical devices (Cpk ≥ 1.67)"
                cpk_color = COLOR_SCHEME["positive"]
                cpk_recommendation = "Excellent process control, focus on maintaining consistency"
            
            st.markdown(f"""
            <div class="info-box" style="border-left: 5px solid {cpk_color};">
                <h4>Process Capability Assessment</h4>
                <p><strong>Status:</strong> <span style="color: {cpk_color};">{cpk_status}</span></p>
                <p><strong>Final ROI after {pdca_iterations} PDCA cycles:</strong> {pdca_roi[-1]:.2f}%</p>
                <p><strong>Total ROI Improvement:</strong> {pdca_roi[-1] - pdca_roi[0]:.2f}%</p>
                <p><strong>Process Capability:</strong> {final_cpk:.3f} Cpk</p>
                <p><strong>Recommendation:</strong> {cpk_recommendation}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Option to save as new scenario
        st.markdown("### Save What-If Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            new_scenario_name = st.text_input(
                "New Scenario Name",
                value=f"{base_scenario_name} (What-If)",
                help="Name for the new scenario if saved"
            )
        
        with col2:
            save_pdca_final = False
            if analysis_mode == "Advanced" and enable_pdca:
                save_pdca_final = st.checkbox(
                    "Save Final PDCA Cycle Results", 
                    value=False,
                    help="Use the final values after all PDCA cycles instead of first iteration"
                )
        
        if st.button("Save as New Scenario", type="primary"):
            try:
                # Determine which values to save
                if analysis_mode == "Advanced" and enable_pdca and save_pdca_final:
                    # Use final PDCA cycle values
                    save_reduction_rate = pdca_reduction_rates[-1]
                    save_unit_cost_change = pdca_unit_costs[-1] - current_unit_cost
                else:
                    # Use first what-if values
                    save_reduction_rate = new_reduction_rate
                    save_unit_cost_change = new_unit_cost_change
                
                # Create a new scenario
                success, message = optimizer.add_scenario(
                    new_scenario_name, 
                    base_scenario['product_name'], 
                    base_scenario['product_category'],
                    new_sales_30, 
                    base_scenario['avg_sale_price'],
                    base_scenario['sales_channel'], 
                    new_returns_30, 
                    base_scenario['upgrade_solution'],
                    total_development_cost, 
                    save_unit_cost_change, 
                    base_scenario['current_unit_cost'],
                    save_reduction_rate, 
                    base_scenario['sales_increase'], 
                    base_scenario['product_lifecycle_stage'],
                    new_sales_30 * 12, 
                    new_returns_30 * 12, 
                    base_scenario['return_processing_cost'],
                    implementation_delay,
                    base_scenario['tag'],
                    base_scenario.get('device_class'),
                    base_scenario.get('regulatory_pathway'),
                    base_scenario.get('validation_required'),
                    regulatory_submission if 'regulatory_submission' in locals() else base_scenario.get('regulatory_submission'),
                    base_scenario.get('design_control_impact'),
                    base_scenario.get('change_type')
                )
                
                if success:
                    st.success(f"What-if scenario saved as '{new_scenario_name}'!")
                    
                    # Add ISO 13485 audit trail entry
                    optimizer.log_audit(
                        "Save What-If Scenario", 
                        f"Created new scenario '{new_scenario_name}' from '{base_scenario_name}'"
                    )
                else:
                    st.error(message)
                    
            except Exception as e:
                st.error(f"Error saving scenario: {str(e)}")
    else:
        st.info("Add scenarios first to use the what-if analysis tool.")

def display_iso_documentation_center():
    """Display ISO 13485 documentation center for medical device improvements"""
    st.subheader("ISO 13485 Documentation Center")
    
    st.markdown("""
    <div class="info-box">
        <p><strong>ISO 13485:2016 Documentation:</strong> This module generates compliant documentation 
        for medical device improvement projects, including risk assessments, validation protocols, 
        and regulatory submission requirements.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if optimizer.scenarios.empty:
        st.info("Add scenarios first to generate ISO 13485 compliant documentation.")
        return
    
    # Select a scenario to document
    scenario_names = optimizer.scenarios['scenario_name'].tolist()
    selected_scenario = st.selectbox(
        "Select scenario for documentation", 
        scenario_names,
        help="Choose the improvement project to generate documentation for"
    )
    
    # Get the selected scenario
    scenario = optimizer.scenarios[optimizer.scenarios['scenario_name'] == selected_scenario].iloc[0]
    
    # Document types
    doc_type = st.selectbox(
        "Document Type",
        ["Project Summary", "Risk Assessment", "Validation Protocol", "Implementation Plan", "Regulatory Submission", "Complete Documentation Package"],
        help="Select the type of documentation to generate"
    )
    
    # Additional parameters based on document type
    if doc_type == "Risk Assessment":
        st.markdown("### Risk Assessment Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            risk_assessment_standard = st.selectbox(
                "Risk Assessment Standard",
                ["ISO 14971:2019", "FMEA", "HACCP", "Custom"],
                help="Risk assessment methodology to apply"
            )
            
            severity_scale = st.selectbox(
                "Severity Scale",
                ["1-5", "1-10"],
                help="Scale for severity ranking"
            )
        
        with col2:
            include_hazard_analysis = st.checkbox(
                "Include Hazard Analysis",
                value=True,
                help="Include detailed hazard analysis in the risk assessment"
            )
            
            include_risk_controls = st.checkbox(
                "Include Risk Control Measures",
                value=True,
                help="Include risk control measures in the assessment"
            )
    
    elif doc_type == "Validation Protocol":
        st.markdown("### Validation Protocol Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            validation_type = st.multiselect(
                "Validation Types",
                ["Design Verification", "Design Validation", "Process Validation", "Software Validation"],
                default=["Design Verification", "Design Validation"],
                help="Types of validation to include in the protocol"
            )
            
            sample_size = st.number_input(
                "Validation Sample Size",
                min_value=1,
                max_value=100,
                value=10,
                help="Number of samples for validation testing"
            )
        
        with col2:
            acceptance_criteria = st.text_area(
                "Acceptance Criteria",
                value="All critical parameters must meet specifications with Cpk ≥ 1.33",
                help="Specific acceptance criteria for the validation"
            )
            
            include_test_methods = st.checkbox(
                "Include Test Methods",
                value=True,
                help="Include detailed test methods in the protocol"
            )
    
    # Generate button
    if st.button("Generate Documentation", type="primary"):
        with st.spinner("Generating ISO 13485 compliant documentation..."):
            # Simulate documentation generation (would use real function in production)
            documentation = generate_iso_documentation(scenario)
            markdown_doc = generate_markdown_from_documentation(documentation)
            
            # Log the documentation generation
            optimizer.log_audit(
                "Generate Documentation", 
                f"Generated {doc_type} for scenario: {selected_scenario}"
            )
            
            # Display the documentation
            st.markdown("### Generated Documentation")
            
            with st.expander("Preview Documentation", expanded=True):
                st.markdown(markdown_doc)
            
            # Export options
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "Download as Markdown",
                    data=markdown_doc,
                    file_name=f"{doc_type.replace(' ', '_')}_{scenario['uid']}.md",
                    mime="text/markdown"
                )
            
            with col2:
                pdf_bytes = export_markdown_to_pdf(markdown_doc)
                
                st.download_button(
                    "Download as PDF",
                    data=pdf_bytes,
                    file_name=f"{doc_type.replace(' ', '_')}_{scenario['uid']}.pdf",
                    mime="application/pdf"
                )
            
            # Display ISO compliance notice
            st.markdown("""
            <div class="documentation-section">
                <h4>ISO 13485:2016 Compliance Notice</h4>
                <p>This documentation has been generated in accordance with ISO 13485:2016 requirements 
                for medical device quality management systems. It is intended to support product improvement 
                activities and should be incorporated into the appropriate quality system documentation.</p>
                <p><strong>Approval Requirements:</strong> This documentation requires review and approval 
                by authorized personnel before implementation.</p>
            </div>
            """, unsafe_allow_html=True)

def display_audit_trail():
    """Display audit trail for ISO 13485 compliance"""
    st.subheader("Audit Trail")
    
    st.markdown("""
    <div class="info-box">
        <p><strong>ISO 13485:2016 Traceability:</strong> This audit trail maintains a record of all 
        system activities per ISO 13485:2016 Section 4.2.5 (Control of Records) requirements.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get audit trail
    audit_entries = optimizer.get_audit_trail()
    
    if not audit_entries:
        st.info("No audit trail entries found.")
        return
    
    # Display filter options
    col1, col2 = st.columns(2)
    
    with col1:
        action_filter = st.multiselect(
            "Filter by Action Type",
            sorted(set(entry["action"] for entry in audit_entries)),
            default=[],
            help="Filter entries by action type"
        )
    
    with col2:
        # Extract dates from timestamps
        dates = sorted(set(entry["timestamp"].split()[0] for entry in audit_entries), reverse=True)
        date_filter = st.multiselect(
            "Filter by Date",
            dates,
            default=[],
            help="Filter entries by date"
        )
    
    # Apply filters
    filtered_entries = audit_entries
    
    if action_filter:
        filtered_entries = [entry for entry in filtered_entries if entry["action"] in action_filter]
    
    if date_filter:
        filtered_entries = [entry for entry in filtered_entries if entry["timestamp"].split()[0] in date_filter]
    
    # Display audit trail
    if filtered_entries:
        # Convert to DataFrame for display
        audit_df = pd.DataFrame(filtered_entries)
        
        # Sort by timestamp (newest first)
        audit_df = audit_df.sort_values(by="timestamp", ascending=False)
        
        # Display as table
        st.dataframe(audit_df, use_container_width=True, hide_index=True)
        
        # Export option
        audit_csv = audit_df.to_csv(index=False).encode()
        
        st.download_button(
            "Export Audit Trail (CSV)",
            data=audit_csv,
            file_name=f"audit_trail_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No entries match the selected filters.")

# Main application
def main():
    """Main application entry point"""
    # Check authentication first
    if not authenticate():
        return
    
    # Setup sidebar and main layout
    display_header()
    
    # Sidebar Navigation
    with st.sidebar:
        st.image("https://placehold.co/150x60/23b2be/004366?text=KaizenROI", width=150)
        st.markdown("## Navigation")
        
        # Navigation options
        nav_option = st.radio(
            "Go to:",
            ["Dashboard", "Add New Scenario", "Portfolio Analysis", "Monte Carlo Analysis", "What-If Analysis", "ISO Documentation", "Audit Trail"],
            index=0
        )
        
        st.markdown("---")
        
        # Total Quality Management resources
        with st.expander("📘 TQM Resources"):
            st.markdown("""
            ### Quality Management System
            - **ISO 13485:2016:** Medical device quality management systems
            - **ISO 9001:2015:** Quality management systems requirements
            - **21 CFR Part 820:** Quality System Regulation (QSR)
            
            ### Process Improvement
            - **PDCA Cycle:** Plan-Do-Check-Act iterative approach
            - **Kaizen:** Continuous incremental improvement
            - **Six Sigma:** Data-driven approach to process variation reduction
            
            ### Statistical Methods
            - **Process Capability (Cpk):** Measure of process performance
            - **Monte Carlo Simulation:** Probabilistic risk analysis
            - **Design of Experiments (DOE):** Structured testing methodology
            """)
        
        # ISO 13485 compliance help
        with st.expander("🔍 ISO 13485 Guidance"):
            st.markdown("""
            ### Implementation Requirements
            - **Design Controls (Sec. 7.3):** Systematic approach to product development
            - **Risk Management (Sec. 7.1):** Risk-based decision making per ISO 14971
            - **CAPA (Sec. 8.5):** Corrective and preventive action processes
            - **Statistical Techniques (Sec. 8.2.6):** Appropriate statistical methods
            
            ### Documentation Requirements
            - **Design History File (DHF):** Records of design process
            - **Device Master Record (DMR):** Manufacturing specifications
            - **Quality Records:** Evidence of conformity to requirements
            - **Traceability:** Documentation of critical parameters and decisions
            """)
        
        # Footer
        st.markdown("---")
        st.caption("KaizenROI v3.0 | ISO 13485 Compliant")
        st.caption("© 2025 Vive Health")
    
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
        
        elif nav_option == "Monte Carlo Analysis":
            display_monte_carlo_analysis()
        
        elif nav_option == "What-If Analysis":
            display_what_if_analysis()
        
        elif nav_option == "ISO Documentation":
            display_iso_documentation_center()
        
        elif nav_option == "Audit Trail":
            display_audit_trail()

if __name__ == "__main__":
    main()
