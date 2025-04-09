"""
Kaizenalytics Enterprise - Advanced Return Analytics Platform
A comprehensive analytics tool for evaluating e-commerce return reduction investments.

This application helps businesses analyze and optimize return reduction strategies
with precise ROI calculations, scenario planning, Monte Carlo simulations, and interactive visualizations.
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
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import traceback
from typing import Dict, List, Tuple, Optional, Union, Any

# Suppress warnings
warnings.filterwarnings('ignore')

# Fallback for rerun depending on Streamlit version
if not hasattr(st, "rerun") and hasattr(st, "experimental_rerun"):
    st.rerun = st.experimental_rerun  # compatibility shim

# App configuration
st.set_page_config(
    page_title="Kaizenalytics | Advanced Return Analytics Platform",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# Constants and Configuration
# =============================================================================

# Check if the app is in basic or advanced mode
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = "Basic"

# Define color schemes
COLOR_SCHEMES = {
    "default": {
        "primary": "#3049D1",
        "secondary": "#22A7F2",
        "tertiary": "#00C2CB",
        "background": "#F5F8FF",
        "positive": "#22c55e",
        "negative": "#ef4444",
        "warning": "#f59e0b",
        "neutral": "#3b82f6",
        "text_dark": "#1e293b",
        "text_light": "#f8fafc",
        "card_bg": "#ffffff",
        "sidebar_bg": "#1e293b",
        "hover": "#dbeafe"
    },
    "forest": {
        "primary": "#10b981",
        "secondary": "#34d399",
        "tertiary": "#6ee7b7",
        "background": "#ecfdf5",
        "positive": "#22c55e",
        "negative": "#f87171",
        "warning": "#fbbf24",
        "neutral": "#2dd4bf",
        "text_dark": "#064e3b",
        "text_light": "#f0fdfa",
        "card_bg": "#ffffff",
        "sidebar_bg": "#064e3b",
        "hover": "#d1fae5"
    },
    "sunset": {
        "primary": "#f97316",
        "secondary": "#fb923c",
        "tertiary": "#fdba74",
        "background": "#fff7ed",
        "positive": "#22c55e",
        "negative": "#ef4444",
        "warning": "#facc15",
        "neutral": "#38bdf8",
        "text_dark": "#7c2d12",
        "text_light": "#ffedd5",
        "card_bg": "#ffffff",
        "sidebar_bg": "#7c2d12",
        "hover": "#fed7aa"
    },
    "royal": {
        "primary": "#8b5cf6",
        "secondary": "#a78bfa",
        "tertiary": "#c4b5fd",
        "background": "#f5f3ff",
        "positive": "#22c55e",
        "negative": "#ef4444",
        "warning": "#f59e0b",
        "neutral": "#3b82f6",
        "text_dark": "#4c1d95",
        "text_light": "#ede9fe",
        "card_bg": "#ffffff",
        "sidebar_bg": "#4c1d95",
        "hover": "#ddd6fe"
    }
   "dark": {
        "primary": "#8B5CF6",      # Purple
        "secondary": "#6366F1",    # Indigo
        "tertiary": "#3B82F6",     # Blue
        "background": "#1E1E2D",   # Dark background
        "positive": "#10B981",     # Green
        "negative": "#EF4444",     # Red
        "warning": "#F59E0B",      # Amber
        "neutral": "#60A5FA",      # Light blue
        "text_dark": "#E2E8F0",    # Light gray for dark mode
        "text_light": "#F8FAFC",   # Nearly white
        "card_bg": "#2D2D3A",      # Slightly lighter than background
        "sidebar_bg": "#171723",   # Darker than background
        "hover": "#374151"         # Medium gray for hover
    },
}

# Set default color scheme
if 'color_scheme' not in st.session_state:
    st.session_state.color_scheme = "default"

# Get current color scheme
COLOR_SCHEME = COLOR_SCHEMES[st.session_state.color_scheme]

# Example scenarios for demonstration
EXAMPLE_SCENARIOS = [
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
        "returns_365": 1140,
        "tag": "Packaging",
        "notes": "Focus on sustainable packaging and improved size charts"
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
        "returns_365": 860,
        "tag": "Size/Fit",
        "notes": "Using AR technology to help customers find the right fit"
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
        "returns_365": 1675,
        "tag": "Product Description",
        "notes": "Professional photography with detailed dimension specs"
    },
    {
        "scenario_name": "Quality Improvement Program",
        "sku": "TECH-234",
        "sales_30": 890,
        "avg_sale_price": 199.99,
        "sales_channel": "Multi-Channel",
        "returns_30": 62,
        "solution": "Enhanced QA process and better materials",
        "solution_cost": 12000,
        "additional_cost_per_item": 2.75,
        "current_unit_cost": 84.25,
        "reduction_rate": 40,
        "sales_365": 10680,
        "returns_365": 744,
        "tag": "Quality",
        "notes": "Implementing Six Sigma practices in manufacturing"
    }
]

# Columns for the scenarios DataFrame
SCENARIO_COLUMNS = [
    'uid', 'scenario_name', 'sku', 'sales_30', 'avg_sale_price',
    'sales_channel', 'returns_30', 'return_rate', 'solution', 'solution_cost',
    'additional_cost_per_item', 'current_unit_cost', 'reduction_rate',
    'return_cost_30', 'return_cost_annual', 'revenue_impact_30',
    'revenue_impact_annual', 'new_unit_cost', 'savings_30',
    'annual_savings', 'break_even_days', 'break_even_months',
    'roi', 'score', 'timestamp', 'annual_additional_costs', 'net_benefit',
    'margin_before', 'margin_after', 'margin_after_amortized',
    'sales_365', 'returns_365', 'avoided_returns_30', 'avoided_returns_365',
    'monthly_net_benefit', 'tag', 'notes', 'confidence_level',
    'risk_rating', 'implementation_time', 'implementation_effort'
]

# =============================================================================
# Custom CSS Styling
# =============================================================================

def load_custom_css():
    """Load custom CSS styling for the application"""
    st.markdown(f"""
    <style>
        /* Main styling */
        body, .stApp {{
            background-color: {COLOR_SCHEME["background"]};
            color: {COLOR_SCHEME["text_dark"]};
            font-family: 'Inter', sans-serif;
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            color: {COLOR_SCHEME["primary"]};
        }}
        
        /* Button styling */
        .stButton>button {{
            background-color: {COLOR_SCHEME["secondary"]};
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        .stButton>button:hover {{
            background-color: {COLOR_SCHEME["primary"]};
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transform: translateY(-1px);
        }}
        .stButton>button:active {{
            transform: translateY(1px);
        }}
        
        /* Form styling */
        .stTextInput>div>div>input, 
        .stNumberInput>div>div>input, 
        .stSelectbox>div>div>div,
        .stTextArea>div>div>textarea {{
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            padding: 0.75rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        
        .stTextInput>div>div>input:focus, 
        .stNumberInput>div>div>input:focus, 
        .stSelectbox>div>div>div:focus,
        .stTextArea>div>div>textarea:focus {{
            border-color: {COLOR_SCHEME["secondary"]};
            box-shadow: 0 0 0 3px rgba(34, 167, 242, 0.2);
        }}
        
        /* Dataframe styling */
        .stDataFrame thead tr th {{
            background-color: {COLOR_SCHEME["primary"]};
            color: white;
            padding: 10px 15px;
            font-weight: 500;
        }}
        .stDataFrame tbody tr:nth-child(even) {{
            background-color: rgba(245, 248, 255, 0.5);
        }}
        .stDataFrame tbody tr:hover {{
            background-color: {COLOR_SCHEME["hover"]};
        }}
        
        /* Cards */
        .css-card {{
            border-radius: 12px;
            padding: 1.5rem;
            background-color: {COLOR_SCHEME["card_bg"]};
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
            transition: all 0.3s;
            border: 1px solid #e2e8f0;
        }}
        
        .css-card:hover {{
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        /* Metric cards */
        .metric-container {{
            background-color: white;
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            transition: all 0.3s;
            height: 100%;
        }}
        
        .metric-container:hover {{
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.5rem;
        }}
        
        .metric-label {{
            font-size: 0.95rem;
            color: #64748b;
            font-weight: 500;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px 8px 0px 0px;
            padding: 10px 18px;
            background-color: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-bottom: none;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: white;
            border-color: #e2e8f0;
            border-bottom: 2px solid {COLOR_SCHEME["secondary"]};
        }}
        
        /* Tooltips */
        .tooltip {{
            position: relative;
            display: inline-block;
            cursor: help;
        }}
        
        .tooltip .tooltiptext {{
            visibility: hidden;
            width: 240px;
            background-color: {COLOR_SCHEME["text_dark"]};
            color: #fff;
            text-align: left;
            border-radius: 8px;
            padding: 12px;
            position: absolute;
            z-index: 1000;
            bottom: 125%;
            left: 50%;
            margin-left: -120px;
            opacity: 0;
            transition: opacity 0.3s;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            font-size: 0.85rem;
            line-height: 1.4;
        }}
        
        .tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
        }}
        
        /* Custom components */
        .info-box {{
            background-color: {COLOR_SCHEME["hover"]};
            border-left: 5px solid {COLOR_SCHEME["neutral"]};
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
        }}
        
        .warning-box {{
            background-color: rgba(245, 158, 11, 0.1);
            border-left: 5px solid {COLOR_SCHEME["warning"]};
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
        }}
        
        .success-box {{
            background-color: rgba(34, 197, 94, 0.1);
            border-left: 5px solid {COLOR_SCHEME["positive"]};
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
        }}
        
        .loading-spinner {{
            text-align: center;
            margin: 20px 0;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {COLOR_SCHEME["sidebar_bg"]};
        }}
        
        [data-testid="stSidebar"] .sidebar-content {{
            padding: 2rem 1rem;
        }}
        
        /* Charts */
        .js-plotly-plot {{
            border-radius: 12px;
            background-color: white;
            padding: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
        }}
        
        /* Sidebar headings and text */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] h5,
        [data-testid="stSidebar"] h6 {{
            color: {COLOR_SCHEME["text_light"]};
        }}
        
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] div {{
            color: {COLOR_SCHEME["text_light"]};
        }}
        
        /* Fix for sidebar radio buttons and other elements */
        [data-testid="stSidebar"] [data-testid="stRadio"] label {{
            color: {COLOR_SCHEME["text_light"]};
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label > div[role="radiogroup"] > label {{
            color: {COLOR_SCHEME["text_dark"]};
        }}
        
        [data-testid="stSidebar"] button {{
            color: {COLOR_SCHEME["text_dark"]};
        }}
        
        /* Fix for checkboxes in sidebar */
        [data-testid="stSidebar"] .stCheckbox label {{
            color: {COLOR_SCHEME["text_light"]};
        }}
        
        /* Mode toggle button */
        .mode-toggle {{
            background-color: {COLOR_SCHEME["secondary"]};
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            display: inline-block;
            text-align: center;
            font-weight: 500;
            margin: 10px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: all 0.3s;
            cursor: pointer;
        }}
        
        .mode-toggle:hover {{
            background-color: {COLOR_SCHEME["primary"]};
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        /* Progress tracker */
        .progress-container {{
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
            position: relative;
        }}
        
        .progress-container::before {{
            content: '';
            position: absolute;
            top: 15px;
            left: 0;
            right: 0;
            height: 4px;
            background-color: #e2e8f0;
            z-index: 1;
        }}
        
        .progress-step {{
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background-color: #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            z-index: 2;
            position: relative;
        }}
        
        .progress-step.active {{
            background-color: {COLOR_SCHEME["primary"]};
            color: white;
        }}
        
        .progress-step.completed {{
            background-color: {COLOR_SCHEME["positive"]};
            color: white;
        }}
        
        .progress-label {{
            position: absolute;
            bottom: -25px;
            white-space: nowrap;
            font-size: 0.8rem;
            color: {COLOR_SCHEME["text_dark"]};
        }}
        
        /* Table styling */
        .styled-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 0.9em;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .styled-table thead tr {{
            background-color: {COLOR_SCHEME["primary"]};
            color: #ffffff;
            text-align: left;
        }}
        
        .styled-table th,
        .styled-table td {{
            padding: 12px 15px;
        }}
        
        .styled-table tbody tr {{
            border-bottom: 1px solid #dddddd;
        }}
        
        .styled-table tbody tr:nth-of-type(even) {{
            background-color: #f3f3f3;
        }}
        
        .styled-table tbody tr:last-of-type {{
            border-bottom: 2px solid {COLOR_SCHEME["primary"]};
        }}
        
        .styled-table tbody tr.active-row {{
            font-weight: bold;
            color: {COLOR_SCHEME["primary"]};
        }}
        
        /* Custom radio buttons for mode selection */
        div.row-widget.stRadio > div {{
            display: flex;
            flex-direction: row;
            align-items: center;
            gap: 10px;
        }}
        
        div.row-widget.stRadio > div[role="radiogroup"] > label {{
            background-color: #f1f5f9;
            border: 1px solid #e2e8f0;
            padding: 8px 16px;
            border-radius: 20px;
            margin-right: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        div.row-widget.stRadio > div[role="radiogroup"] > label:hover {{
            background-color: #e2e8f0;
        }}
        
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div {{
            display: none;
        }}
        
        div.row-widget.stRadio > div[role="radiogroup"] > label[aria-checked="true"] {{
            background-color: {COLOR_SCHEME["secondary"]};
            border-color: {COLOR_SCHEME["secondary"]};
            color: white;
            font-weight: 500;
        }}
        
        /* Better visibility for sidebar text and selections */
        .stSelectbox label, .stMultiSelect label {{
            color: {COLOR_SCHEME["text_dark"]} !important;
        }}
        
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMultiSelect label {{
            color: {COLOR_SCHEME["text_light"]} !important;
        }}
        
        /* New feature badge */
        .new-feature {{
            background-color: {COLOR_SCHEME["warning"]};
            color: white;
            font-size: 0.7rem;
            padding: 3px 8px;
            border-radius: 10px;
            margin-left: 8px;
            display: inline-block;
            vertical-align: middle;
            font-weight: 600;
        }}
        
        /* Step navigation buttons */
        .step-buttons {{
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
        }}
        
        .back-button {{
            background-color: #f1f5f9;
            color: {COLOR_SCHEME["text_dark"]};
            border: 1px solid #e2e8f0;
            padding: 8px 20px;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s;
            cursor: pointer;
        }}
        
        .back-button:hover {{
            background-color: #e2e8f0;
        }}
        
        .next-button {{
            background-color: {COLOR_SCHEME["secondary"]};
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s;
            cursor: pointer;
        }}
        
        .next-button:hover {{
            background-color: {COLOR_SCHEME["primary"]};
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        /* Toggle switch for mode selection */
        .switch-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 15px 0;
        }}
        
        .switch-label {{
            margin: 0 10px;
            font-weight: 500;
            color: {COLOR_SCHEME["text_light"]};
        }}
        
        .switch {{
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
        }}
        
        .switch input {{
            opacity: 0;
            width: 0;
            height: 0;
        }}
        
        .slider {{
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }}
        
        .slider:before {{
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }}
        
        input:checked + .slider {{
            background-color: {COLOR_SCHEME["primary"]};
        }}
        
        input:focus + .slider {{
            box-shadow: 0 0 1px {COLOR_SCHEME["primary"]};
        }}
        
        input:checked + .slider:before {{
            transform: translateX(26px);
        }}
        
        /* Floating help button */
        .help-button {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: {COLOR_SCHEME["secondary"]};
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            cursor: pointer;
            z-index: 1000;
            transition: all 0.3s;
        }}
        
        .help-button:hover {{
            background-color: {COLOR_SCHEME["primary"]};
            transform: scale(1.1);
        }}
        
        /* Fix for dropdowns */
        .stSelectbox div[data-baseweb="select"] div span {{
            color: {COLOR_SCHEME["text_dark"]};
        }}
        
        /* Fix for multiselect */
        .stMultiSelect div[data-baseweb="select"] div span {{
            color: {COLOR_SCHEME["text_dark"]};
        }}
        
        /* Fix for sidebar selectbox */
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div[class$="-placeholder"] span,
        [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] div[class$="-placeholder"] span {{
            color: {COLOR_SCHEME["text_dark"]};
        }}
        
        /* Better visibility for selectbox values in the sidebar */
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div[class$="-valueContainer"] div span {{
            color: {COLOR_SCHEME["text_light"]};
        }}
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# Utility Functions
# =============================================================================

def format_currency(value: Optional[float]) -> str:
    """Format a value as currency."""
    if pd.isna(value) or value is None:
        return "-"
    return f"${value:,.2f}"

def format_percent(value: Optional[float]) -> str:
    """Format a value as percentage."""
    if pd.isna(value) or value is None:
        return "-"
    return f"{value:.2f}%"

def format_number(value: Optional[float]) -> str:
    """Format a value as number with commas."""
    if pd.isna(value) or value is None:
        return "-"
    return f"{value:,.2f}"

def get_icon(value: Optional[float], threshold: float = 0, positive_is_good: bool = True) -> str:
    """Get an icon based on value comparison to threshold."""
    if pd.isna(value) or value is None:
        return "❓"
    
    if positive_is_good:
        return "✅" if value >= threshold else "⚠️"
    else:
        return "✅" if value <= threshold else "⚠️"

def calculate_roi_score(roi: float, breakeven_days: float, reduction_rate: float) -> Optional[float]:
    """Calculate a weighted ROI score with multiple factors."""
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

def get_color_scale(value: Optional[float], min_val: float, max_val: float, reverse: bool = False) -> str:
    """Get color from a green-yellow-red scale based on value."""
    if pd.isna(value) or value is None:
        return "#cccccc"  # Gray for null values
    
    # Normalize value to 0-1 range
    if max_val == min_val:
        normalized = 0.5
    else:
        normalized = max(0, min(1, (value - min_val) / (max_val - min_val)))
    
    if reverse:
        normalized = 1 - normalized
    
    # Color scale: green (good) -> yellow (medium) -> red (poor)
    if normalized <= 0.33:
        color = COLOR_SCHEME["negative"] if not reverse else COLOR_SCHEME["positive"]
    elif normalized <= 0.66:
        color = COLOR_SCHEME["warning"]
    else:
        color = COLOR_SCHEME["positive"] if not reverse else COLOR_SCHEME["negative"]
    
    return color

def display_tooltip(label: str, help_text: str) -> str:
    """Display a label with a tooltip."""
    tooltip_html = f"""
    <div class="tooltip">{label}
        <span class="tooltiptext">{help_text}</span>
    </div>
    """
    return tooltip_html

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning a default if divisor is zero."""
    try:
        if b == 0:
            return default
        return a / b
    except:
        return default

# =============================================================================
# Data Management Class
# =============================================================================

class ReturnOptimizer:
    """Class to manage return optimization scenarios and calculations."""
    
    def __init__(self) -> None:
        """Initialize the ReturnOptimizer."""
        self.load_data()
        self.default_examples = EXAMPLE_SCENARIOS
    
    def load_data(self) -> None:
        """Load data from session state or initialize empty dataframe."""
        if 'scenarios' not in st.session_state:
            self.scenarios = pd.DataFrame(columns=SCENARIO_COLUMNS)
            st.session_state['scenarios'] = self.scenarios
        else:
            self.scenarios = st.session_state['scenarios']
    
    def save_data(self) -> None:
        """Save data to session state."""
        st.session_state['scenarios'] = self.scenarios
    
    def download_json(self) -> str:
        """Get scenarios data as JSON string."""
        return self.scenarios.to_json(orient='records', date_format='iso')
    
    def upload_json(self, json_str: str) -> bool:
        """Load scenarios from JSON string."""
        try:
            data = pd.read_json(json_str, orient='records')
            if not data.empty:
                # Ensure all required columns exist
                for col in SCENARIO_COLUMNS:
                    if col not in data.columns:
                        data[col] = None
                
                # Remove any extra columns
                data = data[SCENARIO_COLUMNS]
                
                self.scenarios = data
                self.save_data()
                return True

def display_scenario_table(df: pd.DataFrame, optimizer: ReturnOptimizer):
    """
    Display scenario table with filtering and sorting.
    
    Args:
        df: DataFrame with scenarios
        optimizer: ReturnOptimizer instance
    """
    if df.empty:
        st.info("No scenarios found. Add a new scenario or load example scenarios.")
        return
    
    # Add filters
    st.subheader("Scenario Analysis")
    
    # Advanced filtering in advanced mode
    if st.session_state.app_mode == "Advanced":
        with st.expander("Filtering Options", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                sku_filter = st.multiselect("Filter by SKU", 
                                       options=sorted(df['sku'].unique()),
                                       default=[],
                                       help="Select one or more SKUs to filter by")
            
            with col2:
                channel_filter = st.multiselect("Filter by Sales Channel", 
                                          options=sorted(df['sales_channel'].unique()),
                                          default=[],
                                          help="Select one or more sales channels")
            
            with col3:
                tag_filter = st.multiselect("Filter by Category", 
                                      options=sorted(df['tag'].dropna().unique()) if not df['tag'].dropna().empty else [],
                                      default=[],
                                      help="Select one or more solution categories")
            
            # Additional filters in advanced mode
            col1, col2 = st.columns(2)
            
            with col1:
                min_roi = st.slider("Minimum ROI (%)", 
                                  0, 500, 0, 
                                  help="Filter scenarios by minimum ROI percentage")
            
            with col2:
                max_breakeven = st.slider("Maximum Breakeven (months)", 
                                        0, 24, 24, 
                                        help="Filter scenarios by maximum breakeven time")
    else:
        # Simplified filtering in basic mode
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sku_options = sorted(df['sku'].unique())
            sku_filter = st.multiselect("Filter by SKU", 
                                   options=sku_options,
                                   default=[])
        
        with col2:
            channel_options = sorted(df['sales_channel'].unique())
            channel_filter = st.multiselect("Filter by Sales Channel", 
                                      options=channel_options,
                                      default=[])
        
        with col3:
            tag_options = sorted(df['tag'].dropna().unique()) if not df['tag'].dropna().empty else []
            tag_filter = st.multiselect("Filter by Category", 
                                  options=tag_options,
                                  default=[])
        
        # Default values for basic mode
        min_roi = 0
        max_breakeven = 24
    
    # Apply filters
    filtered_df = df.copy()
    
    if sku_filter:
        filtered_df = filtered_df[filtered_df['sku'].isin(sku_filter)]
    
    if channel_filter:
        filtered_df = filtered_df[filtered_df['sales_channel'].isin(channel_filter)]
    
    if tag_filter:
        filtered_df = filtered_df[filtered_df['tag'].isin(tag_filter)]
    
    # Apply ROI and breakeven filters
    if min_roi > 0:
        filtered_df = filtered_df[(filtered_df['roi'] >= min_roi) | (filtered_df['roi'].isna())]
    
    if max_breakeven < 24:
        filtered_df = filtered_df[(filtered_df['break_even_months'] <= max_breakeven) | (filtered_df['break_even_months'].isna())]
    
    # Display table
    if filtered_df.empty:
        st.warning("No scenarios match your filters. Try adjusting your criteria.")
        return
    
    # Prepare display columns
    if st.session_state.app_mode == "Advanced":
        display_df = filtered_df[[
            'uid', 'scenario_name', 'sku', 'sales_channel', 'tag', 'return_rate',
            'solution_cost', 'reduction_rate', 'roi', 'break_even_months',
            'net_benefit', 'score', 'confidence_level', 'risk_rating'
        ]].copy()
    else:
        display_df = filtered_df[[
            'uid', 'scenario_name', 'sku', 'sales_channel', 'return_rate',
            'solution_cost', 'reduction_rate', 'roi', 'break_even_months',
            'net_benefit', 'score'
        ]].copy()
    
    # Format columns for display
    display_df['return_rate'] = display_df['return_rate'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    display_df['solution_cost'] = display_df['solution_cost'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    display_df['reduction_rate'] = display_df['reduction_rate'].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "N/A")
    display_df['roi'] = display_df['roi'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    display_df['break_even_months'] = display_df['break_even_months'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
    display_df['net_benefit'] = display_df['net_benefit'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    
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
        'tag': 'Category',
        'return_rate': 'Return Rate',
        'solution_cost': 'Investment',
        'reduction_rate': 'Reduction',
        'roi': 'ROI',
        'break_even_months': 'Break-even',
        'net_benefit': 'Net Benefit',
        'score': 'ROI Score',
        'confidence_level': 'Confidence',
        'risk_rating': 'Risk'
    })
    
    # Hide UID column
    display_df = display_df.drop('uid', axis=1)
    
    # Display interactive table
    st.dataframe(display_df.reset_index(drop=True), 
               use_container_width=True, 
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
                                         filtered_df['scenario_name'].tolist(),
                                         key="scenario_select")
        
        if selected_scenario:
            selected_uid = filtered_df[filtered_df['scenario_name'] == selected_scenario]['uid'].iloc[0]
            
            with col2:
                if st.button("View Details", key="view_btn", use_container_width=True):
                    st.session_state['selected_scenario'] = selected_uid
                    st.session_state['view_scenario'] = True
                    st.rerun()
            
            with col3:
                if st.button("Clone", key="clone_btn", use_container_width=True):
                    success, message = optimizer.clone_scenario(selected_uid)
                    if success:
                        st.success(f"Scenario cloned successfully!")
                        st.rerun()
                    else:
                        st.error(message)
            
            with col4:
                if st.button("Delete", key="delete_btn", use_container_width=True):
                    if optimizer.delete_scenario(selected_uid):
                        st.success(f"Scenario '{selected_scenario}' deleted successfully.")
                        st.rerun()
                    else:
                        st.error("Failed to delete scenario.")
            
            # Additional actions in advanced mode
            if st.session_state.app_mode == "Advanced":
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("Run Monte Carlo", key="monte_carlo_btn", use_container_width=True):
                        st.session_state['monte_carlo_scenario'] = selected_uid
                        st.session_state['nav_option'] = "Monte Carlo"
                        st.rerun()
                
                with col2:
                    if st.button("Compare Scenarios", key="compare_btn", use_container_width=True):
                        if 'compare_list' not in st.session_state:
                            st.session_state['compare_list'] = []
                        
                        if selected_uid not in st.session_state['compare_list']:
                            st.session_state['compare_list'].append(selected_uid)
                        
                        st.success(f"Added '{selected_scenario}' to comparison list")
                        st.session_state['nav_option'] = "Compare Scenarios"
                        st.rerun()
                
                with col3:
                    # Export options for single scenario
                    export_format = st.selectbox("Export Format", 
                                          ["Excel", "CSV"],
                                          key="single_export_format")
                
                with col4:
                    if st.button("Export", key="export_btn", use_container_width=True):
                        # Create a subset of data with just the selected scenario
                        export_df = filtered_df[filtered_df['uid'] == selected_uid]
                        
                        if export_format == "Excel":
                            try:
                                # Create Excel file
                                excel_buffer = io.BytesIO()
                                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                                    export_df.to_excel(writer, index=False, sheet_name='Scenario Details')
                                    
                                    # Get the workbook and worksheet objects
                                    workbook = writer.book
                                    worksheet = writer.sheets['Scenario Details']
                                    
                                    # Add some formatting
                                    header_format = workbook.add_format({
                                        'bold': True,
                                        'bg_color': COLOR_SCHEME['primary'],
                                        'color': 'white',
                                        'border': 1
                                    })
                                    
                                    # Apply formatting to header row
                                    for col_num, value in enumerate(export_df.columns.values):
                                        worksheet.write(0, col_num, value, header_format)
                                        worksheet.set_column(col_num, col_num, 15)
                                
                                # Create download button
                                st.download_button(
                                    label="Download Excel Report",
                                    data=excel_buffer.getvalue(),
                                    file_name=f"{selected_scenario.replace(' ', '_')}_report.xlsx",
                                    mime="application/vnd.ms-excel"
                                )
                                
                            except Exception as e:
                                st.error(f"Error generating Excel file: {str(e)}")
                        
                        elif export_format == "CSV":
                            try:
                                # Create CSV
                                csv_data = export_df.to_csv(index=False).encode('utf-8')
                                
                                # Create download button
                                st.download_button(
                                    label="Download CSV Report",
                                    data=csv_data,
                                    file_name=f"{selected_scenario.replace(' ', '_')}_report.csv",
                                    mime="text/csv"
                                )
                                
                            except Exception as e:
                                st.error(f"Error generating CSV file: {str(e)}")

def display_scenario_details(uid: str, optimizer: ReturnOptimizer):
    """
    Display detailed view of a scenario.
    
    Args:
        uid: Scenario UID
        optimizer: ReturnOptimizer instance
    """
    scenario = optimizer.get_scenario(uid)
    if not scenario:
        st.error("Scenario not found")
        return
    
    st.subheader(f"Scenario Details: {scenario['scenario_name']}")
    
    # Tabs for different views
    if st.session_state.app_mode == "Advanced":
        tabs = st.tabs(["Overview", "Financial Impact", "Return Analysis", "Risk Assessment"])
        
        # Overview tab
        with tabs[0]:
            display_scenario_overview(scenario)
        
        # Financial Impact tab
        with tabs[1]:
            display_scenario_financials(scenario)
        
        # Return Analysis tab
        with tabs[2]:
            display_scenario_returns(scenario)
        
        # Risk Assessment tab
        with tabs[3]:
            display_scenario_risk(scenario)
    else:
        # Simplified view for basic mode
        display_scenario_overview(scenario)
        display_scenario_financials(scenario)
    
    # Return to dashboard button
    if st.button("← Return to Dashboard", use_container_width=True):
        st.session_state['view_scenario'] = False
        st.session_state['selected_scenario'] = None
        st.rerun()

def display_scenario_overview(scenario: Dict[str, Any]):
    """
    Display overview of scenario details.
    
    Args:
        scenario: Dictionary containing scenario data
    """
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
        margin_percent = (scenario['margin_before']/scenario['avg_sale_price']*100) if scenario['avg_sale_price'] > 0 else 0
        st.markdown(f"**Current Margin:** ${scenario['margin_before']:.2f} ({margin_percent:.1f}%)")
    
    # Solution details
    st.markdown("---")
    st.markdown("### Solution Details")
    
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown(f"**Proposed Solution:** {scenario['solution']}")
        st.markdown(f"**Expected Reduction:** {scenario['reduction_rate']:.1f}%")
        st.markdown(f"**Additional Cost/Item:** ${scenario['additional_cost_per_item']:.2f}")
        
        if scenario['notes']:
            st.markdown("**Notes:**")
            st.info(scenario['notes'])
    
    with col5:
        st.markdown(f"**Solution Investment:** ${scenario['solution_cost']:.2f}")
        st.markdown(f"**New Unit Cost:** ${scenario['new_unit_cost']:.2f}")
        new_margin_percent = (scenario['margin_after']/scenario['avg_sale_price']*100) if scenario['avg_sale_price'] > 0 else 0
        st.markdown(f"**New Margin:** ${scenario['margin_after']:.2f} ({new_margin_percent:.1f}%)")
        
        # Display additional details in advanced mode
        if st.session_state.app_mode == "Advanced":
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Confidence Level:** {scenario['confidence_level'] or 'Not specified'}")
            with col2:
                st.markdown(f"**Implementation Time:** {scenario['implementation_time'] or 'Not specified'}")
            with col3:
                st.markdown(f"**Implementation Effort:** {scenario['implementation_effort'] or 'Not specified'}/10")

def display_scenario_financials(scenario: Dict[str, Any]):
    """
    Display financial impact of a scenario.
    
    Args:
        scenario: Dictionary containing scenario data
    """
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
            (scenario['margin_before'] / scenario['avg_sale_price']) * 100 if scenario['avg_sale_price'] > 0 else 0,
            (scenario['margin_after'] / scenario['avg_sale_price']) * 100 if scenario['avg_sale_price'] > 0 else 0,
            (scenario['margin_after_amortized'] / scenario['avg_sale_price']) * 100 if scenario['avg_sale_price'] > 0 else 0
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

def display_scenario_returns(scenario: Dict[str, Any]):
    """
    Display return reduction impact analysis.
    
    Args:
        scenario: Dictionary containing scenario data
    """
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
    
    # Return reasons analysis (placeholder - would be filled with real data in a production app)
    st.markdown("### Return Reasons Analysis")
    
    # Create dummy data for return reasons
    reasons_data = {
        "Reason": ["Size/Fit Issues", "Quality Issues", "Not as Described", "Changed Mind", "Damaged in Transit"],
        "Percentage": [35, 25, 20, 15, 5]
    }
    reasons_df = pd.DataFrame(reasons_data)
    
    # Calculate expected reduction for each reason
    max_reduction = scenario['reduction_rate']
    
    # Different effectiveness for different reasons
    effectiveness = {
        "Size/Fit Issues": 0.8 if scenario['tag'] == "Size/Fit" else 0.3,
        "Quality Issues": 0.9 if scenario['tag'] == "Quality" else 0.2,
        "Not as Described": 0.85 if scenario['tag'] == "Product Description" else 0.4,
        "Changed Mind": 0.3,
        "Damaged in Transit": 0.7 if scenario['tag'] == "Packaging" else 0.1
    }
    
    # Calculate reduction for each reason
    reasons_df["Reduction"] = reasons_df["Reason"].apply(
        lambda x: min(reasons_df.loc[reasons_df["Reason"] == x, "Percentage"].values[0], 
                      max_reduction * effectiveness[x])
    )
    
    reasons_df["After"] = reasons_df["Percentage"] - reasons_df["Reduction"]
    
    # Create stacked bar chart
    fig_reasons = go.Figure()
    
    fig_reasons.add_trace(go.Bar(
        x=reasons_df["Reason"],
        y=reasons_df["After"],
        name="Remaining",
        marker_color=COLOR_SCHEME["neutral"]
    ))
    
    fig_reasons.add_trace(go.Bar(
        x=reasons_df["Reason"],
        y=reasons_df["Reduction"],
        name="Reduced",
        marker_color=COLOR_SCHEME["positive"]
    ))
    
    fig_reasons.update_layout(
        barmode="stack",
        title="Impact on Return Reasons",
        xaxis_title="Return Reason",
        yaxis_title="Percentage (%)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_reasons, use_container_width=True)
    
    st.info("Note: Return reasons analysis is based on industry benchmarks and may vary for your specific products.")

def display_scenario_risk(scenario: Dict[str, Any]):
    """
    Display risk assessment for a scenario.
    
    Args:
        scenario: Dictionary containing scenario data
    """
    st.markdown("### Risk Assessment")
    
    # Extract risk data
    risk_rating = scenario.get('risk_rating', 'Medium')
    confidence_level = scenario.get('confidence_level', 'Medium')
    implementation_time = scenario.get('implementation_time', '1-3 months')
    implementation_effort = scenario.get('implementation_effort', 5)
    
    # Display risk metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Risk rating gauge
        risk_value = {"Low": 25, "Medium": 50, "High": 75}.get(risk_rating, 50)
        risk_color = {"Low": COLOR_SCHEME["positive"], 
                      "Medium": COLOR_SCHEME["warning"], 
                      "High": COLOR_SCHEME["negative"]}.get(risk_rating, COLOR_SCHEME["warning"])
        
        fig_risk = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk_value,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Risk Rating"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": risk_color},
                "steps": [
                    {"range": [0, 33], "color": "rgba(46, 204, 113, 0.3)"},
                    {"range": [33, 66], "color": "rgba(243, 156, 18, 0.3)"},
                    {"range": [66, 100], "color": "rgba(231, 76, 60, 0.3)"}
                ]
            }
        ))
        
        fig_risk.update_layout(height=200, margin=dict(t=25, b=0, l=25, r=25))
        st.plotly_chart(fig_risk, use_container_width=True)
    
    with col2:
        # Confidence level gauge
        confidence_value = {"Low": 25, "Medium": 50, "High": 75}.get(confidence_level, 50)
        confidence_color = {"Low": COLOR_SCHEME["negative"], 
                            "Medium": COLOR_SCHEME["warning"], 
                            "High": COLOR_SCHEME["positive"]}.get(confidence_level, COLOR_SCHEME["warning"])
        
        fig_confidence = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=confidence_value,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Confidence Level"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": confidence_color},
                "steps": [
                    {"range": [0, 33], "color": "rgba(231, 76, 60, 0.3)"},
                    {"range": [33, 66], "color": "rgba(243, 156, 18, 0.3)"},
                    {"range": [66, 100], "color": "rgba(46, 204, 113, 0.3)"}
                ]
            }
        ))
        
        fig_confidence.update_layout(height=200, margin=dict(t=25, b=0, l=25, r=25))
        st.plotly_chart(fig_confidence, use_container_width=True)
    
    with col3:
        # Implementation time
        time_options = {"0-1 month": 15, "1-3 months": 40, "3-6 months": 70, "6+ months": 90}
        time_value = time_options.get(implementation_time, 40)
        
        fig_time = go.Figure(go.Indicator(
            mode="gauge+number",
            value=time_value,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Implementation Time"},
            gauge={
                "axis": {"range": [0, 100], "tickvals": [15, 40, 70, 90], 
                         "ticktext": ["<1m", "1-3m", "3-6m", "6m+"]},
                "bar": {"color": COLOR_SCHEME["secondary"]},
                "steps": [
                    {"range": [0, 30], "color": "rgba(46, 204, 113, 0.3)"},
                    {"range": [30, 60], "color": "rgba(243, 156, 18, 0.3)"},
                    {"range": [60, 100], "color": "rgba(231, 76, 60, 0.3)"}
                ]
            }
        ))
        
        fig_time.update_layout(height=200, margin=dict(t=25, b=0, l=25, r=25))
        st.plotly_chart(fig_time, use_container_width=True)
    
    with col4:
        # Implementation effort
        fig_effort = go.Figure(go.Indicator(
            mode="gauge+number",
            value=implementation_effort,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Implementation Effort"},
            gauge={
                "axis": {"range": [0, 10]},
                "bar": {"color": COLOR_SCHEME["tertiary"]},
                "steps": [
                    {"range": [0, 3], "color": "rgba(46, 204, 113, 0.3)"},
                    {"range": [3, 7], "color": "rgba(243, 156, 18, 0.3)"},
                    {"range": [7, 10], "color": "rgba(231, 76, 60, 0.3)"}
                ]
            }
        ))
        
        fig_effort.update_layout(height=200, margin=dict(t=25, b=0, l=25, r=25))
        st.plotly_chart(fig_effort, use_container_width=True)
    
    # Risk assessment summary
    st.markdown("### Risk Assessment Summary")
    
    # Calculate overall risk score
    risk_score = {"Low": 0, "Medium": 1, "High": 2}.get(risk_rating, 1)
    confidence_score = {"High": 0, "Medium": 1, "Low": 2}.get(confidence_level, 1)
    
    time_score = {"0-1 month": 0, "1-3 months": 1, "3-6 months": 2, "6+ months": 3}.get(implementation_time, 1)
    effort_score = int(min(implementation_effort / 10 * 3, 3))
    
    overall_score = risk_score + confidence_score + time_score + effort_score
    
    # Risk assessment text based on overall score
    risk_text = ""
    if overall_score <= 2:
        risk_text = """
        **Low Risk Assessment:**
        This scenario presents minimal risk with high confidence in projected outcomes. 
        Implementation should be straightforward and the return reduction strategy can be rolled out quickly.
        
        **Recommendation:** Proceed with implementation as planned. Consider potential for expansion to other products.
        """
    elif overall_score <= 5:
        risk_text = """
        **Moderate Risk Assessment:**
        This scenario presents a balanced risk profile with reasonable confidence in outcomes.
        Implementation will require moderate effort and oversight.
        
        **Recommendation:** Proceed with implementation but establish clear monitoring metrics and potential fallback options.
        """
    elif overall_score <= 8:
        risk_text = """
        **High Risk Assessment:**
        This scenario presents elevated risk factors that warrant careful consideration.
        Implementation will require significant resources and oversight.
        
        **Recommendation:** Consider a phased implementation approach, starting with a small pilot to validate assumptions.
        """
    else:
        risk_text = """
        **Very High Risk Assessment:**
        This scenario presents significant risks that may outweigh the potential benefits.
        Implementation will be challenging, time-consuming, and results are uncertain.
        
        **Recommendation:** Reconsider the approach or develop a smaller-scale pilot before committing to full implementation.
        """
    
    # Display risk assessment with appropriate color
    risk_colors = {
        "Low": COLOR_SCHEME["positive"],
        "Moderate": COLOR_SCHEME["warning"],
        "High": COLOR_SCHEME["negative"],
        "Very High": COLOR_SCHEME["negative"]
    }
    
    risk_level = "Low" if overall_score <= 2 else ("Moderate" if overall_score <= 5 else 
                ("High" if overall_score <= 8 else "Very High"))
    
    st.markdown(f"""
    <div style="padding: 20px; border-radius: 10px; background-color: rgba({', '.join(str(int(int(risk_colors[risk_level].lstrip('#')[i:i+2], 16) * 0.2)) for i in (0, 2, 4))}, 0.3); 
    border: 1px solid {risk_colors[risk_level]};">
        <h4 style="color: {risk_colors[risk_level]};">{risk_level} Risk Profile</h4>
        {risk_text}
    </div>
    """, unsafe_allow_html=True)
    
    # Risk mitigation strategies
    st.markdown("### Risk Mitigation Strategies")
    
    mitigation_strategies = {
        "High ROI Uncertainty": """
        • Run a small-scale pilot to validate ROI projections
        • Establish clear metrics and tracking mechanisms
        • Set staged implementation with go/no-go decision points
        """,
        
        "Long Implementation Time": """
        • Break implementation into smaller phases with measurable outcomes
        • Identify quick wins that can be implemented early
        • Create a detailed timeline with dependencies and critical path
        """,
        
        "Resource Constraints": """
        • Partner with vendors or consultants for specialized expertise
        • Consider software-as-a-service solutions instead of custom development
        • Prioritize elements with highest impact-to-effort ratio
        """,
        
        "Customer Resistance": """
        • Conduct customer research to refine the solution
        • Implement A/B testing to validate assumptions
        • Develop clear customer communication strategy
        """
    }
    
    # Display relevant mitigation strategies based on risk profile
    col1, col2 = st.columns(2)
    
    with col1:
        if confidence_score > 0:
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 8px; background-color: #f8f9fa; margin-bottom: 15px;">
                <h5>High ROI Uncertainty</h5>
                {mitigation_strategies["High ROI Uncertainty"]}
            </div>
            """, unsafe_allow_html=True)
        
        if effort_score > 1:
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 8px; background-color: #f8f9fa; margin-bottom: 15px;">
                <h5>Resource Constraints</h5>
                {mitigation_strategies["Resource Constraints"]}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if time_score > 1:
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 8px; background-color: #f8f9fa; margin-bottom: 15px;">
                <h5>Long Implementation Time</h5>
                {mitigation_strategies["Long Implementation Time"]}
            </div>
            """, unsafe_allow_html=True)
        
        if scenario['tag'] in ["Size/Fit", "Product Description"]:
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 8px; background-color: #f8f9fa; margin-bottom: 15px;">
                <h5>Customer Resistance</h5>
                {mitigation_strategies["Customer Resistance"]}
            </div>
            """, unsafe_allow_html=True)

def display_portfolio_analysis(df: pd.DataFrame):
    """
    Display portfolio-level analysis and visualizations.
    
    Args:
        df: DataFrame with scenarios
    """
    if df.empty:
        st.info("Add scenarios to see portfolio analysis.")
        return
    
    st.subheader("Portfolio Analysis")
    
    # Key portfolio metrics
    metrics = optimizer.get_aggregate_statistics()
    
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
        if 'tag' in df.columns and not df['tag'].isna().all():
            solution_group = df.groupby('tag').agg({
                'roi': 'mean',
                'solution_cost': 'sum',
                'net_benefit': 'sum'
            }).reset_index()
            
            fig_solution = px.bar(
                solution_group,
                x="tag",
                y="roi",
                color="net_benefit",
                color_continuous_scale=px.colors.sequential.Viridis,
                labels={
                    "tag": "Solution Category",
                    "roi": "Average ROI (%)",
                    "net_benefit": "Net Benefit ($)"
                },
                title="ROI by Solution Category"
            )
            
            fig_solution.update_layout(height=400)
            st.plotly_chart(fig_solution, use_container_width=True)
    
    with col2:
        # ROI by sales channel
        if 'sales_channel' in df.columns and not df['sales_channel'].isna().all():
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
    
    # Portfolio allocation in advanced mode
    if st.session_state.app_mode == "Advanced":
        st.markdown("### Portfolio Investment Allocation")
        
        # Investment allocation by category
        if 'tag' in df.columns and not df['tag'].isna().all():
            investment_by_tag = df.groupby('tag')['solution_cost'].sum().reset_index()
            if not investment_by_tag.empty:
                investment_by_tag['percentage'] = (investment_by_tag['solution_cost'] / investment_by_tag['solution_cost'].sum()) * 100
                
                # Create pie chart
                fig_investment = px.pie(
                    investment_by_tag,
                    values='solution_cost',
                    names='tag',
                    title='Investment Allocation by Category',
                    color_discrete_sequence=px.colors.sequential.Plasma
                )
                
                fig_investment.update_traces(textposition='inside', textinfo='percent+label')
                
                # Create treemap of investment vs return
                tag_roi = df.groupby('tag').agg({
                    'solution_cost': 'sum',
                    'net_benefit': 'sum',
                    'roi': 'mean'
                }).reset_index()
                
                tag_roi['roi_formatted'] = tag_roi['roi'].apply(lambda x: f"{x:.1f}%" if not pd.isna(x) else "N/A")
                
                fig_treemap = px.treemap(
                    tag_roi,
                    path=['tag'],
                    values='solution_cost',
                    color='roi',
                    color_continuous_scale=px.colors.sequential.Viridis,
                    hover_data=['net_benefit', 'roi_formatted'],
                    title='Investment vs ROI by Category'
                )
                
                # Display charts side by side
                col1, col2 = st.columns(2)
                
                with col1:
                    st.plotly_chart(fig_investment, use_container_width=True)
                
                with col2:
                    st.plotly_chart(fig_treemap, use_container_width=True)
        
        # Investment timeline & payback projection
        st.markdown("### Investment Timeline & Payback Projection")
        
        # Create timeline data (simplified simulation)
        timeline_months = 24
        monthly_data = []
        
        cumulative_investment = 0
        cumulative_savings = 0
        
        for month in range(1, timeline_months + 1):
            month_investment = df['solution_cost'].sum() if month == 1 else 0
            cumulative_investment += month_investment
            
            # Monthly savings grow over time as solutions are implemented
            implementation_factor = min(1.0, month / 6)  # Assumes full implementation by month 6
            month_savings = (df['monthly_net_benefit'].sum() * implementation_factor)
            cumulative_savings += month_savings
            
            monthly_data.append({
                'Month': month,
                'Investment': cumulative_investment,
                'Savings': cumulative_savings,
                'Net': cumulative_savings - cumulative_investment
            })
        
        timeline_df = pd.DataFrame(monthly_data)
        
        # Find breakeven point
        breakeven_month = None
        for month, row in enumerate(monthly_data, 1):
            if row['Net'] >= 0:
                breakeven_month = month
                break
        
        # Create line chart
        fig_timeline = go.Figure()
        
        fig_timeline.add_trace(go.Scatter(
            x=timeline_df['Month'],
            y=timeline_df['Investment'],
            name='Cumulative Investment',
            mode='lines',
            line=dict(width=3, color=COLOR_SCHEME['negative'])
        ))
        
        fig_timeline.add_trace(go.Scatter(
            x=timeline_df['Month'],
            y=timeline_df['Savings'],
            name='Cumulative Savings',
            mode='lines',
            line=dict(width=3, color=COLOR_SCHEME['positive'])
        ))
        
        fig_timeline.add_trace(go.Scatter(
            x=timeline_df['Month'],
            y=timeline_df['Net'],
            name='Net (Savings - Investment)',
            mode='lines',
            line=dict(width=3, color=COLOR_SCHEME['primary'])
        ))
        
        # Add breakeven marker if applicable
        if breakeven_month:
            breakeven_value = timeline_df.loc[timeline_df['Month'] == breakeven_month, 'Net'].values[0]
            
            fig_timeline.add_trace(go.Scatter(
                x=[breakeven_month],
                y=[breakeven_value],
                name='Breakeven Point',
                mode='markers',
                marker=dict(size=12, color=COLOR_SCHEME['secondary'], symbol='star'),
                text=f"Breakeven: Month {breakeven_month}"
            ))
            
            # Add vertical line at breakeven
            fig_timeline.add_shape(
                type="line",
                x0=breakeven_month, y0=0,
                x1=breakeven_month, y1=timeline_df['Savings'].max() * 1.1,
                line=dict(color="green", width=1, dash="dash")
            )
            
            fig_timeline.add_annotation(
                x=breakeven_month,
                y=timeline_df['Savings'].max() * 0.9,
                text=f"Portfolio Breakeven: Month {breakeven_month}",
                showarrow=True,
                arrowhead=1
            )
        
        fig_timeline.update_layout(
            title="Portfolio Investment and Returns Timeline",
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Portfolio recommendations
        st.markdown("### Portfolio Optimization Recommendations")
        
        # Calculate overall portfolio health
        avg_roi = df['roi'].mean() if not df['roi'].isnull().all() else 0
        avg_breakeven = df['break_even_months'].mean() if not df['break_even_months'].isnull().all() else 0
        avg_score = df['score'].mean() if not df['score'].isnull().all() else 0
        
        portfolio_health = "Excellent"
        recommendations = []
        
        if avg_roi < 50:
            portfolio_health = "Poor" if avg_roi < 20 else "Fair"
            recommendations.append("Focus on solutions with higher ROI potential")
        
        if avg_breakeven > 12:
            portfolio_health = "Poor" if avg_breakeven > 18 else "Fair"
            recommendations.append("Prioritize solutions with faster payback periods")
        
        if df['solution_cost'].sum() > 30000:
            recommendations.append("Consider phased implementation to distribute investment costs")
        
        if 'tag' in df.columns and 'Size/Fit' in df['tag'].values:
            size_fit_roi = df[df['tag'] == 'Size/Fit']['roi'].mean() if not df[df['tag'] == 'Size/Fit']['roi'].isnull().all() else 0
            if size_fit_roi > avg_roi:
                recommendations.append("Expand size/fit solutions across more products based on strong performance")
        
        if 'tag' in df.columns and len(df['tag'].unique()) < 3:
            recommendations.append("Diversify solution types to address multiple return reasons")
        
        # Display health score and recommendations
        health_colors = {
            "Excellent": COLOR_SCHEME["positive"],
            "Good": COLOR_SCHEME["secondary"],
            "Fair": COLOR_SCHEME["warning"],
            "Poor": COLOR_SCHEME["negative"]
        }
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div style="background-color: {health_colors[portfolio_health]}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                <h3 style="margin: 0;">Portfolio Health</h3>
                <h1 style="margin: 10px 0;">{portfolio_health}</h1>
                <p>Based on ROI, breakeven time, and diversity</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"### Optimization Recommendations")
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"**{i}.** {rec}")
            else:
                st.markdown("Your portfolio is performing well across all metrics. Continue monitoring for optimization opportunities.")

def display_what_if_analysis(optimizer: ReturnOptimizer):
    """
    Interactive what-if scenario analysis.
    
    Args:
        optimizer: ReturnOptimizer instance
    """
    st.subheader("What-If Analysis")
    
    # Get base scenario
    if not optimizer.scenarios.empty:
        # Let user select a base scenario
        scenario_names = optimizer.scenarios['scenario_name'].tolist()
        base_scenario_name = st.selectbox("Select base scenario for what-if analysis", scenario_names)
        
        # Get the selected scenario
        base_scenario = optimizer.scenarios[optimizer.scenarios['scenario_name'] == base_scenario_name].iloc[0]
        
        # Set up what-if parameters with responsive layout
        st.markdown("### Adjust Parameters")
        
        # Different parameter layouts for basic and advanced modes
        if st.session_state.app_mode == "Advanced":
            # More detailed parameters in advanced mode
            with st.expander("Sales & Returns Parameters", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    sales_change = st.slider(
                        "Sales Volume Change (%)", 
                        min_value=-50, 
                        max_value=100, 
                        value=0,
                        help="Adjust projected monthly sales volume"
                    )
                
                with col2:
                    return_rate_change = st.slider(
                        "Return Rate Change (%)", 
                        min_value=-50, 
                        max_value=50, 
                        value=0,
                        help="Adjust the projected return rate relative to current rate"
                    )
                
                with col3:
                    price_change = st.slider(
                        "Average Sale Price Change (%)", 
                        min_value=-25, 
                        max_value=25, 
                        value=0,
                        help="Adjust the average selling price of the product"
                    )
            
            with st.expander("Solution Parameters", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    solution_cost_change = st.slider(
                        "Solution Cost Change (%)", 
                        min_value=-50, 
                        max_value=100, 
                        value=0,
                        help="Adjust the one-time implementation cost of the solution"
                    )
                
                with col2:
                    reduction_effectiveness = st.slider(
                        "Return Reduction Effectiveness (%)", 
                        min_value=-50, 
                        max_value=50, 
                        value=0,
                        help="Adjust how effective the solution is at reducing returns compared to the initial estimate"
                    )
                
                with col3:
                    additional_cost_change = st.slider(
                        "Additional Cost per Item Change (%)", 
                        min_value=-50, 
                        max_value=100, 
                        value=0,
                        help="Adjust the ongoing additional cost per unit that results from implementing the solution"
                    )
            
            # Additional advanced parameters
            with st.expander("Advanced Parameters", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    seasonality_factor = st.slider(
                        "Seasonality Factor", 
                        min_value=0.5, 
                        max_value=1.5, 
                        value=1.0, 
                        step=0.1,
                        help="Adjust for seasonal variations in sales (values below 1 reduce sales, above 1 increase sales)"
                    )
                
                with col2:
                    marketing_factor = st.slider(
                        "Marketing Impact", 
                        min_value=0.0, 
                        max_value=0.5, 
                        value=0.0, 
                        step=0.05,
                        help="Additional sales boost from marketing activities (as a percentage increase)"
                    )
        else:
            # Simplified parameters in basic mode
            col1, col2 = st.columns(2)
            
            with col1:
                sales_change = st.slider(
                    "Sales Volume Change (%)", 
                    min_value=-50, 
                    max_value=100, 
                    value=0
                )
                
                solution_cost_change = st.slider(
                    "Solution Cost Change (%)", 
                    min_value=-50, 
                    max_value=100, 
                    value=0
                )
                
                additional_cost_change = st.slider(
                    "Additional Cost per Item Change (%)", 
                    min_value=-50, 
                    max_value=100, 
                    value=0
                )
            
            with col2:
                return_rate_change = st.slider(
                    "Return Rate Change (%)", 
                    min_value=-50, 
                    max_value=50, 
                    value=0
                )
                
                reduction_effectiveness = st.slider(
                    "Return Reduction Effectiveness (%)", 
                    min_value=-50, 
                    max_value=50, 
                    value=0
                )
                
                price_change = st.slider(
                    "Average Sale Price Change (%)", 
                    min_value=-25, 
                    max_value=25, 
                    value=0
                )
            
            # Default values for basic mode
            seasonality_factor = 1.0
            marketing_factor = 0.0
        
        # Calculate new values with error handling
        try:
            new_sales_30 = base_scenario['sales_30'] * (1 + sales_change/100) * seasonality_factor * (1 + marketing_factor)
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
            
            if base_scenario['solution_cost'] > 0 and original_monthly_net > 0:
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
            
            if new_solution_cost > 0 and new_monthly_net > 0:
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
            
            # Format the comparison table
            comparison_formatted = comparison_df.copy()
            comparison_formatted["Original"] = comparison_formatted.apply(
                lambda row: format_number(row["Original"]) if "units" in row["Metric"] 
                else (format_percent(row["Original"]) if "%" in row["Metric"] 
                      else format_currency(row["Original"]) if "$" in row["Metric"] 
                      else row["Original"]),
                axis=1
            )
            comparison_formatted["New"] = comparison_formatted.apply(
                lambda row: format_number(row["New"]) if "units" in row["Metric"] 
                else (format_percent(row["New"]) if "%" in row["Metric"] 
                      else format_currency(row["New"]) if "$" in row["Metric"] 
                      else row["New"]),
                axis=1
            )
            
            # Calculate and display changes
            comparison_formatted["Change"] = comparison_df.apply(
                lambda row: f"{((row['New'] - row['Original']) / row['Original'] * 100):.1f}%" 
                if row['Original'] != 0 else "N/A",
                axis=1
            )
            
            st.dataframe(comparison_formatted, use_container_width=True, hide_index=True)
            
            st.markdown("### Financial Impact Comparison")
            
            # Format the financial table
            financial_formatted = financial_df.copy()
            
            financial_formatted["Original"] = financial_formatted.apply(
                lambda row: format_currency(row["Original"]) if "$" in row["Metric"]
                else (format_percent(row["Original"]) if "%" in row["Metric"]
                      else format_number(row["Original"]) if "months" in row["Metric"]
                      else row["Original"]),
                axis=1
            )
            
            financial_formatted["New"] = financial_formatted.apply(
                lambda row: format_currency(row["New"]) if "$" in row["Metric"]
                else (format_percent(row["New"]) if "%" in row["Metric"]
                      else format_number(row["New"]) if "months" in row["Metric"]
                      else row["New"]),
                axis=1
            )
            
            # Calculate percentage changes for financial metrics
            financial_formatted["Change"] = financial_df.apply(
                lambda row: f"{((row['New'] - row['Original']) / row['Original'] * 100):.1f}%" 
                if pd.notna(row['Original']) and pd.notna(row['New']) and row['Original'] != 0 
                else "N/A",
                axis=1
            )
            
            st.dataframe(financial_formatted, use_container_width=True, hide_index=True)
            
            # Calculate percent changes for visualization
            net_benefit_change = 0
            if pd.notna(original_annual_net) and pd.notna(new_annual_net) and original_annual_net > 0:
                net_benefit_change = ((new_annual_net / original_annual_net) - 1) * 100
            
            roi_change = 0
            if pd.notna(original_roi) and pd.notna(new_roi) and original_roi > 0:
                roi_change = ((new_roi / original_roi) - 1) * 100
            
            breakeven_change = 0
            if pd.notna(original_breakeven) and pd.notna(new_breakeven) and original_breakeven > 0:
                breakeven_change = ((new_breakeven / original_breakeven) - 1) * 100
            
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
                if pd.notna(new_roi):
                    st.metric(
                        "Return on Investment",
                        f"{new_roi:.1f}%",
                        f"{roi_change:.1f}%",
                        delta_color="normal" if roi_change >= 0 else "inverse"
                    )
                else:
                    st.metric("Return on Investment", "N/A", delta=None)
            
            with col3:
                if pd.notna(new_breakeven):
                    st.metric(
                        "Break-even Time",
                        f"{new_breakeven:.1f} months",
                        f"{-breakeven_change:.1f}%",  # Negative because shorter is better
                        delta_color="normal" if breakeven_change <= 0 else "inverse"
                    )
                else:
                    st.metric("Break-even Time", "N/A", delta=None)
            
            # Create more visualizations in advanced mode
            if st.session_state.app_mode == "Advanced":
                # ROI sensitivity analysis
                st.markdown("### Sensitivity Analysis")
                st.caption("This chart shows how ROI changes with different parameter combinations")
                
                # Choose sensitivity parameters
                sens_param1 = st.selectbox(
                    "Primary Parameter",
                    ["Reduction Rate", "Additional Cost", "Sales Volume", "Return Rate", "Price"],
                    index=0
                )
                
                sens_param2 = st.selectbox(
                    "Secondary Parameter",
                    ["Reduction Rate", "Additional Cost", "Sales Volume", "Return Rate", "Price"],
                    index=1
                )
                
                # Ensure different parameters are selected
                if sens_param1 == sens_param2:
                    st.warning("Please select different parameters for sensitivity analysis")
                else:
                    # Set up parameter ranges
                    param_ranges = {
                        "Reduction Rate": {
                            "base": new_reduction_rate,
                            "range": np.linspace(max(0, new_reduction_rate - 20), min(100, new_reduction_rate + 20), 5),
                            "format": lambda x: f"{x:.0f}%"
                        },
                        "Additional Cost": {
                            "base": new_additional_cost,
                            "range": np.linspace(max(0, new_additional_cost - 1), new_additional_cost + 1, 5),
                            "format": lambda x: f"${x:.2f}"
                        },
                        "Sales Volume": {
                            "base": new_sales_30,
                            "range": np.linspace(max(1, new_sales_30 * 0.7), new_sales_30 * 1.3, 5),
                            "format": lambda x: f"{x:.0f} units"
                        },
                        "Return Rate": {
                            "base": new_return_rate,
                            "range": np.linspace(max(1, new_return_rate * 0.7), min(100, new_return_rate * 1.3), 5),
                            "format": lambda x: f"{x:.1f}%"
                        },
                        "Price": {
                            "base": new_avg_price,
                            "range": np.linspace(max(new_unit_cost, new_avg_price * 0.9), new_avg_price * 1.1, 5),
                            "format": lambda x: f"${x:.2f}"
                        }
                    }
                    
                    # Create sensitivity data
                    sensitivity_data = []
                    
                    for val1 in param_ranges[sens_param1]["range"]:
                        for val2 in param_ranges[sens_param2]["range"]:
                            # Create scenario with new parameter values
                            s_new_reduction_rate = val1 if sens_param1 == "Reduction Rate" else new_reduction_rate
                            s_new_additional_cost = val1 if sens_param1 == "Additional Cost" else new_additional_cost
                            s_new_sales_30 = val1 if sens_param1 == "Sales Volume" else new_sales_30
                            s_new_return_rate = val1 if sens_param1 == "Return Rate" else new_return_rate
                            s_new_avg_price = val1 if sens_param1 == "Price" else new_avg_price
                            
                            if sens_param2 == "Reduction Rate":
                                s_new_reduction_rate = val2
                            elif sens_param2 == "Additional Cost":
                                s_new_additional_cost = val2
                            elif sens_param2 == "Sales Volume":
                                s_new_sales_30 = val2
                            elif sens_param2 == "Return Rate":
                                s_new_return_rate = val2
                            elif sens_param2 == "Price":
                                s_new_avg_price = val2
                            
                            # Calculate financial metrics
                            s_new_returns_30 = (s_new_sales_30 * s_new_return_rate / 100)
                            s_new_unit_cost = base_scenario['current_unit_cost'] + s_new_additional_cost
                            s_new_avoided_returns = s_new_returns_30 * (s_new_reduction_rate / 100)
                            s_new_monthly_savings = s_new_avoided_returns * (s_new_avg_price - s_new_unit_cost)
                            s_new_monthly_cost = s_new_sales_30 * s_new_additional_cost
                            s_new_monthly_net = s_new_monthly_savings - s_new_monthly_cost
                            s_new_annual_net = s_new_monthly_net * 12
                            
                            if new_solution_cost > 0 and s_new_annual_net > 0:
                                s_new_roi = (s_new_annual_net / new_solution_cost) * 100
                                s_new_breakeven = new_solution_cost / s_new_monthly_net
                            else:
                                s_new_roi = 0
                                s_new_breakeven = 36  # Cap for visualization
                            
                            # Add to sensitivity data
                            sensitivity_data.append({
                                sens_param1: val1,
                                sens_param2: val2,
                                "ROI": s_new_roi if s_new_roi > 0 else 0,
                                "Breakeven": min(s_new_breakeven, 36) if s_new_breakeven else 36,
                                "Net Benefit": s_new_annual_net
                            })
                    
                    sensitivity_df = pd.DataFrame(sensitivity_data)
                    
                    # Create heatmap
                    fig_heatmap = px.density_heatmap(
                        sensitivity_df,
                        x=sens_param1,
                        y=sens_param2,
                        z="ROI",
                        labels={
                            sens_param1: sens_param1,
                            sens_param2: sens_param2,
                            "ROI": "Return on Investment (%)"
                        },
                        title=f"ROI Sensitivity: {sens_param1} vs {sens_param2}"
                    )
                    
                    # Customize heatmap
                    fig_heatmap.update_layout(
                        height=500,
                        xaxis=dict(
                            tickmode='array',
                            tickvals=param_ranges[sens_param1]["range"],
                            ticktext=[param_ranges[sens_param1]["format"](x) for x in param_ranges[sens_param1]["range"]]
                        ),
                        yaxis=dict(
                            tickmode='array',
                            tickvals=param_ranges[sens_param2]["range"],
                            ticktext=[param_ranges[sens_param2]["format"](x) for x in param_ranges[sens_param2]["range"]]
                        )
                    )
                    
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                    
                    # Create 3D surface plot
                    fig_3d = go.Figure(data=[go.Surface(
                        x=sensitivity_df[sens_param1].unique(),
                        y=sensitivity_df[sens_param2].unique(),
                        z=sensitivity_df.pivot(
                            index=sens_param2, 
                            columns=sens_param1, 
                            values="ROI"
                        ).values,
                        colorscale='Viridis'
                    )])
                    
                    fig_3d.update_layout(
                        title=f"3D ROI Surface: {sens_param1} vs {sens_param2}",
                        scene=dict(
                            xaxis_title=sens_param1,
                            yaxis_title=sens_param2,
                            zaxis_title="ROI (%)"
                        ),
                        height=600,
                        margin=dict(l=0, r=0, b=0, t=30)
                    )
                    
                    st.plotly_chart(fig_3d, use_container_width=True)
            
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
            
            # Option to save as new scenario
            col1, col2 = st.columns(2)
            
            with col1:
                new_scenario_name = st.text_input("New Scenario Name", f"{base_scenario_name} (What-If)")
            
            with col2:
                if st.button("Save as New Scenario", use_container_width=True):
                    # Create a new scenario name
                    if not new_scenario_name:
                        new_scenario_name = f"{base_scenario_name} (What-If)"
                    
                    success, message = optimizer.add_scenario(
                        new_scenario_name, base_scenario['sku'], new_sales_30, new_avg_price,
                        base_scenario['sales_channel'], new_returns_30, base_scenario['solution'],
                        new_solution_cost, new_additional_cost, base_scenario['current_unit_cost'],
                        new_reduction_rate, new_sales_30 * 12, new_returns_30 * 12, base_scenario['tag'],
                        f"What-if scenario based on {base_scenario_name}", base_scenario['confidence_level'],
                        base_scenario['risk_rating'], base_scenario['implementation_time'],
                        base_scenario['implementation_effort']
                    )
                    
                    if success:
                        st.success(f"What-if scenario saved as '{new_scenario_name}'!")
                        st.rerun()
                    else:
                        st.error(message)
        except Exception as e:
            st.error(f"Error in what-if analysis calculations: {str(e)}")
            st.error(traceback.format_exc())
    else:
        st.info("Add scenarios first to use the what-if analysis tool.")

def display_monte_carlo_simulation(optimizer: ReturnOptimizer):
    """
    Display Monte Carlo simulation for a scenario.
    
    Args:
        optimizer: ReturnOptimizer instance
    """
    st.subheader("Monte Carlo Simulation")
    
    # Check if we have a selected scenario
    if 'monte_carlo_scenario' in st.session_state:
        scenario_uid = st.session_state['monte_carlo_scenario']
        scenario = optimizer.get_scenario(scenario_uid)
        
        if not scenario:
            st.error("Selected scenario not found. Please select another scenario.")
            if st.button("Return to Dashboard", use_container_width=True):
                st.session_state.pop('monte_carlo_scenario', None)
                st.session_state['nav_option'] = "Dashboard"
                st.rerun()
            return
        
        st.markdown(f"### Monte Carlo Analysis: {scenario['scenario_name']}")
        
        # Simulation parameters
        st.markdown("### Simulation Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_simulations = st.slider("Number of Simulations", 
                               min_value=100, 
                               max_value=10000, 
                               value=1000, 
                               step=100)
        
        with col2:
            confidence_interval = st.selectbox("Confidence Interval", 
                                      ["80%", "90%", "95%", "99%"],
                                      index=2)
        
        # Parameter variation settings
        st.markdown("### Parameter Variation Settings")
        st.caption("Set the percentage by which each parameter can vary in the simulation.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            reduction_variation = st.slider("Return Reduction Variation (%)", 
                                   min_value=5, 
                                   max_value=50, 
                                   value=20)
            
            solution_cost_variation = st.slider("Solution Cost Variation (%)", 
                                      min_value=5, 
                                      max_value=50, 
                                      value=10)
        
        with col2:
            sales_variation = st.slider("Sales Variation (%)", 
                               min_value=5, 
                               max_value=50, 
                               value=5)
            
            returns_variation = st.slider("Returns Variation (%)", 
                                min_value=5, 
                                max_value=50, 
                                value=10)
        
        with col3:
            price_variation = st.slider("Price Variation (%)", 
                               min_value=5, 
                               max_value=50, 
                               value=5)
            
            additional_cost_variation = st.slider("Additional Cost Variation (%)", 
                                        min_value=5, 
                                        max_value=50, 
                                        value=15)
        
        # Create parameter variations dictionary
        param_variations = {
            'reduction_rate': reduction_variation,
            'solution_cost': solution_cost_variation,
            'sales_30': sales_variation,
            'returns_30': returns_variation,
            'avg_sale_price': price_variation,
            'additional_cost_per_item': additional_cost_variation
        }
        
        # Run simulation button
        if st.button("Run Monte Carlo Simulation", key="run_mc_btn", use_container_width=True):
            with st.spinner(f"Running {num_simulations} simulations..."):
                # Show progress bar
                progress_bar = st.progress(0)
                
                # Run simulation
                results, message = optimizer.run_monte_carlo_simulation(
                    scenario_uid, 
                    num_simulations=num_simulations,
                    param_variations=param_variations
                )
                
                # Update progress
                for i in range(100):
                    # Update progress bar
                    progress_bar.progress(i + 1)
                    time.sleep(0.01)
                
                # Remove progress bar
                progress_bar.empty()
                
                if results is None:
                    st.error(message)
                    return
                
                # Display simulation results
                st.success(f"Successfully completed {num_simulations} simulations!")
                
                # Calculate confidence intervals
                ci_map = {
                    "80%": 1.28,  # z-score for 80% CI
                    "90%": 1.645,  # z-score for 90% CI
                    "95%": 1.96,  # z-score for 95% CI
                    "99%": 2.576  # z-score for 99% CI
                }
                
                z_score = ci_map[confidence_interval]
                
                # Clean and filter simulation results
                results = results.dropna(subset=['roi', 'net_benefit'])
                
                # Calculate statistics for key metrics
                roi_mean = results['roi'].mean()
                roi_std = results['roi'].std()
                roi_ci_lower = roi_mean - z_score * roi_std / np.sqrt(len(results))
                roi_ci_upper = roi_mean + z_score * roi_std / np.sqrt(len(results))
                
                breakeven_mean = results['break_even_months'].mean()
                breakeven_std = results['break_even_months'].std()
                breakeven_ci_lower = breakeven_mean - z_score * breakeven_std / np.sqrt(len(results))
                breakeven_ci_upper = breakeven_mean + z_score * breakeven_std / np.sqrt(len(results))
                
                net_benefit_mean = results['net_benefit'].mean()
                net_benefit_std = results['net_benefit'].std()
                net_benefit_ci_lower = net_benefit_mean - z_score * net_benefit_std / np.sqrt(len(results))
                net_benefit_ci_upper = net_benefit_mean + z_score * net_benefit_std / np.sqrt(len(results))
                
                # Display summary statistics
                st.markdown("### Simulation Results")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Mean ROI", f"{roi_mean:.2f}%")
                    st.caption(f"{confidence_interval} CI: [{roi_ci_lower:.2f}%, {roi_ci_upper:.2f}%]")
                
                with col2:
                    st.metric("Mean Breakeven", f"{breakeven_mean:.2f} months")
                    st.caption(f"{confidence_interval} CI: [{breakeven_ci_lower:.2f}, {breakeven_ci_upper:.2f}] months")
                
                with col3:
                    st.metric("Mean Net Benefit", f"${net_benefit_mean:.2f}")
                    st.caption(f"{confidence_interval} CI: [${net_benefit_ci_lower:.2f}, ${net_benefit_ci_upper:.2f}]")
                
                # Probability of success metrics
                st.markdown("### Probability Analysis")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    prob_positive_roi = (results['roi'] > 0).mean() * 100
                    st.metric("Probability of Positive ROI", f"{prob_positive_roi:.1f}%")
                
                with col2:
                    prob_breakeven_under_12 = (results['break_even_months'] < 12).mean() * 100
                    st.metric("Probability of Breakeven < 12 months", f"{prob_breakeven_under_12:.1f}%")
                
                with col3:
                    target_roi = scenario['roi'] if pd.notna(scenario['roi']) else 50
                    prob_target_roi = (results['roi'] >= target_roi).mean() * 100
                    st.metric(f"Probability of ROI ≥ {target_roi:.0f}%", f"{prob_target_roi:.1f}%")
                
                # Distribution charts
                st.markdown("### Distribution Analysis")
                
                # ROI Distribution
                fig_roi_dist = px.histogram(
                    results, 
                    x="roi",
                    nbins=50,
                    title="ROI Distribution",
                    labels={"roi": "Return on Investment (%)"},
                    color_discrete_sequence=[COLOR_SCHEME["primary"]]
                )
                
                # Add vertical lines for confidence interval
                fig_roi_dist.add_vline(x=roi_ci_lower, line_dash="dash", line_color=COLOR_SCHEME["warning"])
                fig_roi_dist.add_vline(x=roi_ci_upper, line_dash="dash", line_color=COLOR_SCHEME["warning"])
                
                # Add vertical line for mean
                fig_roi_dist.add_vline(x=roi_mean, line_color=COLOR_SCHEME["secondary"])
                
                # Add vertical line for original scenario
                if pd.notna(scenario['roi']):
                    fig_roi_dist.add_vline(x=scenario['roi'], line_color=COLOR_SCHEME["positive"],
                                         annotation_text="Original Estimate")
                
                st.plotly_chart(fig_roi_dist, use_container_width=True)
                
                # Breakeven Distribution
                fig_breakeven_dist = px.histogram(
                    results, 
                    x="break_even_months",
                    nbins=50,
                    title="Breakeven Time Distribution",
                    labels={"break_even_months": "Breakeven Time (months)"},
                    color_discrete_sequence=[COLOR_SCHEME["primary"]]
                )
                
                # Add vertical lines for confidence interval
                fig_breakeven_dist.add_vline(x=breakeven_ci_lower, line_dash="dash", line_color=COLOR_SCHEME["warning"])
                fig_breakeven_dist.add_vline(x=breakeven_ci_upper, line_dash="dash", line_color=COLOR_SCHEME["warning"])
                
                # Add vertical line for mean
                fig_breakeven_dist.add_vline(x=breakeven_mean, line_color=COLOR_SCHEME["secondary"])
                
                # Add vertical line for original scenario
                if pd.notna(scenario['break_even_months']):
                    fig_breakeven_dist.add_vline(x=scenario['break_even_months'], line_color=COLOR_SCHEME["positive"],
                                               annotation_text="Original Estimate")
                
                # Add vertical line for 12 months (common target)
                fig_breakeven_dist.add_vline(x=12, line_color=COLOR_SCHEME["negative"], line_dash="dot",
                                           annotation_text="12 Month Target")
                
                st.plotly_chart(fig_breakeven_dist, use_container_width=True)
                
                # Scatter plot of ROI vs Breakeven
                fig_scatter = px.scatter(
                    results,
                    x="break_even_months",
                    y="roi",
                    color="net_benefit",
                    color_continuous_scale=px.colors.sequential.Viridis,
                    title="ROI vs. Breakeven Time",
                    labels={
                        "break_even_months": "Breakeven Time (months)",
                        "roi": "Return on Investment (%)",
                        "net_benefit": "Net Benefit ($)"
                    },
                )
                
                # Add horizontal line for target ROI
                fig_scatter.add_hline(y=target_roi, line_color=COLOR_SCHEME["warning"], line_dash="dot",
                                    annotation_text=f"Target ROI ({target_roi:.0f}%)")
                
                # Add vertical line for 12 month breakeven
                fig_scatter.add_vline(x=12, line_color=COLOR_SCHEME["warning"], line_dash="dot",
                                    annotation_text="12 Month Target")
                
                # Add point for original scenario
                if pd.notna(scenario['roi']) and pd.notna(scenario['break_even_months']):
                    fig_scatter.add_trace(go.Scatter(
                        x=[scenario['break_even_months']],
                        y=[scenario['roi']],
                        mode="markers",
                        marker=dict(
                            size=15,
                            color=COLOR_SCHEME["positive"],
                            symbol="star"
                        ),
                        name="Original Estimate"
                    ))
                
                st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Correlation analysis
                st.markdown("### Parameter Sensitivity Analysis")
                
                # Create correlation matrix
                corr_cols = ['reduction_rate', 'additional_cost_per_item', 'solution_cost', 
                           'sales_30', 'returns_30', 'avg_sale_price', 'roi', 'break_even_months', 'net_benefit']
                
                corr_matrix = results[corr_cols].corr()
                
                # Create heatmap
                fig_corr = px.imshow(
                    corr_matrix,
                    text_auto=".2f",
                    color_continuous_scale=px.colors.diverging.RdBu_r,
                    title="Correlation Matrix",
                    aspect="auto"
                )
                
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Tornado chart for parameter impact
                # Calculate correlation with ROI
                roi_corr = corr_matrix['roi'].drop('roi').sort_values(ascending=False)
                
                # Create tornado chart
                fig_tornado = go.Figure()
                
                # Add bars
                fig_tornado.add_trace(go.Bar(
                    y=roi_corr.index,
                    x=roi_corr.values,
                    orientation='h',
                    marker_color=[COLOR_SCHEME["positive"] if x > 0 else COLOR_SCHEME["negative"] for x in roi_corr.values]
                ))
                
                # Add vertical line at 0
                fig_tornado.add_shape(
                    type="line",
                    x0=0, y0=-0.5,
                    x1=0, y1=len(roi_corr) - 0.5,
                    line=dict(color="black", width=2)
                )
                
                # Update layout
                fig_tornado.update_layout(
                    title="Parameter Impact on ROI",
                    xaxis_title="Correlation with ROI",
                    yaxis_title="Parameter",
                    height=400
                )
                
                st.plotly_chart(fig_tornado, use_container_width=True)
                
                # Insights and recommendations
                st.markdown("### Insights & Recommendations")
                
                # Generate insights based on simulation results
                insights = []
                
                # ROI insights
                if prob_positive_roi < 75:
                    insights.append(f"**High Risk:** There's only a {prob_positive_roi:.1f}% chance of achieving a positive ROI.")
                elif prob_positive_roi > 95:
                    insights.append(f"**Low Risk:** There's a {prob_positive_roi:.1f}% chance of achieving a positive ROI.")
                
                # Breakeven insights
                if prob_breakeven_under_12 < 50:
                    insights.append(f"**Long Payback Period:** Only a {prob_breakeven_under_12:.1f}% chance of breaking even in less than 12 months.")
                elif prob_breakeven_under_12 > 90:
                    insights.append(f"**Quick Payback:** {prob_breakeven_under_12:.1f}% chance of breaking even in less than 12 months.")
                
                # Parameter sensitivity insights
                most_positive = roi_corr.idxmax()
                most_negative = roi_corr.idxmin()
                
                insights.append(f"**Key Driver:** {most_positive} has the strongest positive impact on ROI.")
                insights.append(f"**Risk Factor:** {most_negative} has the strongest negative impact on ROI.")
                
                # Compare to original estimate
                if pd.notna(scenario['roi']):
                    if scenario['roi'] > roi_ci_upper:
                        insights.append(f"**Optimism Bias:** Original ROI estimate of {scenario['roi']:.1f}% is higher than the {confidence_interval} confidence interval [{roi_ci_lower:.1f}%, {roi_ci_upper:.1f}%].")
                    elif scenario['roi'] < roi_ci_lower:
                        insights.append(f"**Conservative Estimate:** Original ROI estimate of {scenario['roi']:.1f}% is lower than the {confidence_interval} confidence interval [{roi_ci_lower:.1f}%, {roi_ci_upper:.1f}%].")
                
                # Display insights
                for insight in insights:
                    st.markdown(insight)
                
                # Display recommendations
                st.markdown("#### Recommendations")
                
                recommendations = []
                
                # Generate recommendations based on insights
                if prob_positive_roi < 75:
                    recommendations.append("Consider revising the solution to improve ROI or reduce implementation costs.")
                
                if "reduction_rate" in most_positive:
                    recommendations.append("Focus on maximizing the effectiveness of return reduction efforts, as this has the strongest impact on ROI.")
                
                if "solution_cost" in most_negative:
                    recommendations.append("Look for ways to reduce implementation costs without sacrificing effectiveness.")
                
                if "additional_cost_per_item" in most_negative:
                    recommendations.append("Find ways to minimize the ongoing per-unit cost increase from the solution.")
                
                # Add general recommendation
                recommendations.append(f"Set up a monitoring system to track actual performance against the {confidence_interval} confidence intervals found in this simulation.")
                
                # Display recommendations
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"**{i}.** {rec}")
                
                # Export options
                st.markdown("### Export Results")
                
                # Create download option for results as CSV
                csv_results = results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Simulation Results (CSV)",
                    data=csv_results,
                    file_name=f"monte_carlo_{scenario['scenario_name'].replace(' ', '_')}.csv",
                    mime="text/csv"
                )
                
                # Option to save as a new scenario
                st.markdown("### Save as New Scenario")
                new_name = st.text_input("New Scenario Name", f"{scenario['scenario_name']} (Monte Carlo)")
                
                if st.button("Save Mean Values as New Scenario", use_container_width=True):
                    # Calculate mean values from simulation
                    mean_reduction_rate = results['reduction_rate'].mean()
                    mean_additional_cost = results['additional_cost_per_item'].mean()
                    mean_sales_30 = results['sales_30'].mean()
                    mean_returns_30 = results['returns_30'].mean()
                    mean_avg_sale_price = results['avg_sale_price'].mean()
                    
                    # Create new scenario with mean values
                    success, message = optimizer.add_scenario(
                        new_name, scenario['sku'], mean_sales_30, mean_avg_sale_price,
                        scenario['sales_channel'], mean_returns_30, scenario['solution'],
                        scenario['solution_cost'], mean_additional_cost, scenario['current_unit_cost'],
                        mean_reduction_rate, mean_sales_30 * 12, mean_returns_30 * 12, scenario['tag'],
                        f"Monte Carlo simulation based on {scenario['scenario_name']} with {num_simulations} simulations",
                        scenario['confidence_level'], scenario['risk_rating'], 
                        scenario['implementation_time'], scenario['implementation_effort']
                    )
                    
                    if success:
                        st.success(f"Monte Carlo scenario saved as '{new_name}'!")
                        st.rerun()
                    else:
                        st.error(message)
        
        # Display info about Monte Carlo simulation if no simulation has been run yet
        else:
            st.info("""
            ### About Monte Carlo Simulation
            
            Monte Carlo simulation is a powerful technique that runs thousands of scenarios with varied inputs to understand the range of possible outcomes and their probabilities.
            
            **Benefits:**
            - Reveals the probability distribution of key metrics like ROI and breakeven time
            - Identifies which parameters have the greatest impact on outcomes
            - Helps quantify and manage risk in return reduction investments
            - Provides confidence intervals for more realistic planning
            
            Click the "Run Monte Carlo Simulation" button to analyze this scenario using the parameter variations you've set.
            """)
    
    else:
        st.info("Please select a scenario for Monte Carlo simulation from the Dashboard.")
        
        # Display sample results for demonstration
        if st.button("Show Demo Simulation", use_container_width=True):
            st.markdown("### Sample Simulation Results")
            
            # Create sample data
            np.random.seed(42)  # For reproducible results
            sample_size = 1000
            
            # Sample ROI data
            sample_roi = np.random.normal(120, 40, sample_size)
            
            # Sample breakeven data (in months)
            sample_breakeven = np.random.normal(9, 3, sample_size)
            
            # Sample net benefit data
            sample_net_benefit = np.random.normal(25000, 8000, sample_size)
            
            # Create sample dataframe
            sample_results = pd.DataFrame({
                'roi': sample_roi,
                'break_even_months': sample_breakeven,
                'net_benefit': sample_net_benefit
            })
            
            # Display sample statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Mean ROI", f"{sample_results['roi'].mean():.2f}%")
                st.caption("95% CI: [118.02%, 121.98%]")
            
            with col2:
                st.metric("Mean Breakeven", f"{sample_results['break_even_months'].mean():.2f} months")
                st.caption("95% CI: [8.81, 9.19] months")
            
            with col3:
                st.metric("Mean Net Benefit", f"${sample_results['net_benefit'].mean():.2f}")
                st.caption("95% CI: [$24,512.21, $25,487.79]")
            
            # Sample distribution chart
            fig_sample = px.histogram(
                sample_results, 
                x="roi",
                nbins=30,
                title="Sample ROI Distribution",
                labels={"roi": "Return on Investment (%)"},
                color_discrete_sequence=[COLOR_SCHEME["primary"]]
            )
            
            # Add vertical lines for 95% confidence interval
            ci_lower = sample_results['roi'].mean() - 1.96 * sample_results['roi'].std() / np.sqrt(len(sample_results))
            ci_upper = sample_results['roi'].mean() + 1.96 * sample_results['roi'].std() / np.sqrt(len(sample_results))
            
            fig_sample.add_vline(x=ci_lower, line_dash="dash", line_color=COLOR_SCHEME["warning"])
            fig_sample.add_vline(x=ci_upper, line_dash="dash", line_color=COLOR_SCHEME["warning"])
            
            # Add vertical line for mean
            fig_sample.add_vline(x=sample_results['roi'].mean(), line_color=COLOR_SCHEME["secondary"])
            
            st.plotly_chart(fig_sample, use_container_width=True)
            
            st.info("This is a demonstration using sample data. Select a real scenario from the Dashboard to run a simulation on your own data.")

def display_scenario_comparison(optimizer: ReturnOptimizer):
    """
    Display comparison between multiple scenarios.
    
    Args:
        optimizer: ReturnOptimizer instance
    """
    st.subheader("Scenario Comparison")
    
    # Get comparison list
    if 'compare_list' not in st.session_state:
        st.session_state['compare_list'] = []
    
    compare_list = st.session_state['compare_list']
    
    # If no scenarios in compare list, let user select them
    if not compare_list:
        # Get list of scenarios
        if not optimizer.scenarios.empty:
            scenario_options = optimizer.scenarios[['uid', 'scenario_name']].copy()
            
            st.info("Please select scenarios to compare.")
            
            # Let user select scenarios
            selected_scenarios = st.multiselect(
                "Select scenarios to compare",
                options=scenario_options['scenario_name'].tolist(),
                help="Select at least 2 scenarios to compare them"
            )
            
            # Add selected scenarios to compare list
            if selected_scenarios:
                compare_list = []
                for scenario in selected_scenarios:
                    uid = scenario_options[scenario_options['scenario_name'] == scenario]['uid'].iloc[0]
                    compare_list.append(uid)
                
                st.session_state['compare_list'] = compare_list
                
                # If we have at least 2 scenarios, show comparison button
                if len(compare_list) >= 2:
                    if st.button("Compare Selected Scenarios", use_container_width=True):
                        st.rerun()
        else:
            st.warning("No scenarios available. Please add scenarios first.")
            return
    
    # Show comparison if we have scenarios in compare list
    if len(compare_list) >= 2:
        # Get scenario data
        comparison_data = []
        
        for uid in compare_list:
            scenario = optimizer.get_scenario(uid)
            if scenario:
                comparison_data.append(scenario)
        
        # Convert to dataframe for easier comparison
        comparison_df = pd.DataFrame(comparison_data)
        
        # Show scenarios being compared
        st.markdown("### Comparing Scenarios")
        
        # Show scenario names
        scenario_names = comparison_df['scenario_name'].tolist()
        st.markdown(", ".join([f"**{name}**" for name in scenario_names]))
        
        # Actions
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear Comparison List", use_container_width=True):
                st.session_state['compare_list'] = []
                st.rerun()
        
        with col2:
            if st.button("Add More Scenarios", use_container_width=True):
                st.session_state['compare_list'] = []  # Clear to restart
                st.rerun()
        
        # Basic comparison table
        st.markdown("### Key Metrics Comparison")
        
        # Select columns to compare
        basic_cols = ['scenario_name', 'solution', 'solution_cost', 'reduction_rate', 
                    'return_rate', 'roi', 'break_even_months', 'net_benefit']
        
        basic_comparison = comparison_df[basic_cols].copy()
        
        # Format columns
        basic_comparison['solution_cost'] = basic_comparison['solution_cost'].apply(lambda x: f"${x:,.2f}")
        basic_comparison['reduction_rate'] = basic_comparison['reduction_rate'].apply(lambda x: f"{x:.1f}%")
        basic_comparison['return_rate'] = basic_comparison['return_rate'].apply(lambda x: f"{x:.2f}%")
        basic_comparison['roi'] = basic_comparison['roi'].apply(lambda x: f"{x:.1f}%" if not pd.isna(x) else "N/A")
        basic_comparison['break_even_months'] = basic_comparison['break_even_months'].apply(lambda x: f"{x:.1f}" if not pd.isna(x) else "N/A")
        basic_comparison['net_benefit'] = basic_comparison['net_benefit'].apply(lambda x: f"${x:,.2f}")
        
        # Rename columns
        basic_comparison = basic_comparison.rename(columns={
            'scenario_name': 'Scenario',
            'solution': 'Solution',
            'solution_cost': 'Investment',
            'reduction_rate': 'Reduction Rate',
            'return_rate': 'Return Rate',
            'roi': 'ROI',
            'break_even_months': 'Break-even',
            'net_benefit': 'Net Benefit'
        })
        
        # Display table
        st.dataframe(basic_comparison, use_container_width=True, hide_index=True)
        
        # Visual comparison
        st.markdown("### Visual Comparison")
        
        # ROI and breakeven comparison
        col1, col2 = st.columns(2)
        
        with col1:
            # ROI Bar Chart
            roi_data = comparison_df[['scenario_name', 'roi']].dropna().copy()
            
            if not roi_data.empty:
                fig_roi = px.bar(
                    roi_data,
                    x='scenario_name',
                    y='roi',
                    title="ROI Comparison",
                    labels={
                        'scenario_name': 'Scenario',
                        'roi': 'Return on Investment (%)'
                    },
                    color='roi',
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                
                # Add target line
                fig_roi.add_hline(y=100, line_dash="dot", line_color=COLOR_SCHEME["warning"],
                                annotation_text="100% ROI Target")
                
                st.plotly_chart(fig_roi, use_container_width=True)
            else:
                st.info("No ROI data available for comparison")
        
        with col2:
            # Breakeven Bar Chart
            breakeven_data = comparison_df[['scenario_name', 'break_even_months']].dropna().copy()
            
            if not breakeven_data.empty:
                fig_breakeven = px.bar(
                    breakeven_data,
                    x='scenario_name',
                    y='break_even_months',
                    title="Breakeven Comparison",
                    labels={
                        'scenario_name': 'Scenario',
                        'break_even_months': 'Breakeven Time (months)'
                    },
                    color='break_even_months',
                    color_continuous_scale=px.colors.sequential.Viridis_r  # Reversed so lower is better
                )
                
                # Add target line
                fig_breakeven.add_hline(y=12, line_dash="dot", line_color=COLOR_SCHEME["warning"],
                                    annotation_text="12 Month Target")
                
                st.plotly_chart(fig_breakeven, use_container_width=True)
            else:
                st.info("No breakeven data available for comparison")
        
        # Investment and benefit comparison
        col1, col2 = st.columns(2)
        
        with col1:
            # Investment vs. Return
            investment_return_data = comparison_df[['scenario_name', 'solution_cost', 'annual_savings']].copy()
            
            # Reshape for grouped bar chart
            investment_return_melted = pd.melt(
                investment_return_data, 
                id_vars=['scenario_name'],
                value_vars=['solution_cost', 'annual_savings'],
                var_name='Metric',
                value_name='Amount'
            )
            
            # Rename for display
            investment_return_melted['Metric'] = investment_return_melted['Metric'].map({
                'solution_cost': 'Investment',
                'annual_savings': 'Annual Savings'
            })
            
            fig_inv_return = px.bar(
                investment_return_melted,
                x='scenario_name',
                y='Amount',
                color='Metric',
                barmode='group',
                title="Investment vs. Annual Savings",
                labels={
                    'scenario_name': 'Scenario',
                    'Amount': 'Amount ($)',
                    'Metric': 'Metric'
                },
                color_discrete_map={
                    'Investment': COLOR_SCHEME["warning"],
                    'Annual Savings': COLOR_SCHEME["positive"]
                }
            )
            
            st.plotly_chart(fig_inv_return, use_container_width=True)
        
        with col2:
            # Return Rate Reduction
            return_rate_data = comparison_df[['scenario_name', 'return_rate', 'reduction_rate']].copy()
            
            # Calculate new return rate after reduction
            return_rate_data['new_return_rate'] = return_rate_data['return_rate'] * (1 - return_rate_data['reduction_rate'] / 100)
            
            # Reshape for grouped bar chart
            return_rate_melted = pd.melt(
                return_rate_data,
                id_vars=['scenario_name'],
                value_vars=['return_rate', 'new_return_rate'],
                var_name='Metric',
                value_name='Rate'
            )
            
            # Rename for display
            return_rate_melted['Metric'] = return_rate_melted['Metric'].map({
                'return_rate': 'Current Return Rate',
                'new_return_rate': 'After Reduction'
            })
            
            fig_return_rate = px.bar(
                return_rate_melted,
                x='scenario_name',
                y='Rate',
                color='Metric',
                barmode='group',
                title="Return Rate Comparison",
                labels={
                    'scenario_name': 'Scenario',
                    'Rate': 'Return Rate (%)',
                    'Metric': 'Metric'
                },
                color_discrete_map={
                    'Current Return Rate': COLOR_SCHEME["negative"],
                    'After Reduction': COLOR_SCHEME["positive"]
                }
            )
            
            st.plotly_chart(fig_return_rate, use_container_width=True)
        
        # ROI vs. Breakeven Scatter Plot
        roi_breakeven_data = comparison_df[['scenario_name', 'roi', 'break_even_months', 'net_benefit']].dropna().copy()
        
        if not roi_breakeven_data.empty:
            fig_scatter = px.scatter(
                roi_breakeven_data,
                x='break_even_months',
                y='roi',
                size='net_benefit',
                color='net_benefit',
                hover_name='scenario_name',
                size_max=50,
                title="ROI vs. Breakeven with Net Benefit",
                labels={
                    'break_even_months': 'Breakeven Time (months)',
                    'roi': 'Return on Investment (%)',
                    'net_benefit': 'Net Benefit ($)'
                },
                color_continuous_scale=px.colors.sequential.Viridis
            )
            
            # Add quadrant lines
            fig_scatter.add_hline(y=100, line_dash="dash", line_color="gray")
            fig_scatter.add_vline(x=12, line_dash="dash", line_color="gray")
            
            # Add quadrant labels
            fig_scatter.add_annotation(
                x=6, y=150,
                text="IDEAL: High ROI, Fast Payback",
                showarrow=False,
                font=dict(color="green", size=10)
            )
            
            fig_scatter.add_annotation(
                x=18, y=150,
                text="GOOD: High ROI, Slow Payback",
                showarrow=False,
                font=dict(color="blue", size=10)
            )
            
            fig_scatter.add_annotation(
                x=6, y=50,
                text="CONSIDER: Low ROI, Fast Payback",
                showarrow=False,
                font=dict(color="orange", size=10)
            )
            
            fig_scatter.add_annotation(
                x=18, y=50,
                text="AVOID: Low ROI, Slow Payback",
                showarrow=False,
                font=dict(color="red", size=10)
            )
            
            # Update layout
            fig_scatter.update_layout(height=600)
            
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Radar chart comparison (for advanced mode)
        if st.session_state.app_mode == "Advanced":
            st.markdown("### Multi-Dimensional Comparison")
            
            # Prepare data for radar chart
            radar_metrics = ['roi', 'reduction_rate', 'net_benefit', 'score']
            
            # We need to normalize the values for the radar chart
            radar_data = comparison_df[['scenario_name'] + radar_metrics].copy()
            
            # Replace NaN with 0
            radar_data = radar_data.fillna(0)
            
            # Normalize each metric to 0-100 scale
            for metric in radar_metrics:
                if radar_data[metric].max() > 0:
                    radar_data[metric] = 100 * radar_data[metric] / radar_data[metric].max()
            
            # Create radar chart
            fig_radar = go.Figure()
            
            # Add a trace for each scenario
            colors = px.colors.qualitative.Plotly
            for i, (_, row) in enumerate(radar_data.iterrows()):
                fig_radar.add_trace(go.Scatterpolar(
                    r=[row[m] for m in radar_metrics],
                    theta=radar_metrics,
                    fill='toself',
                    name=row['scenario_name'],
                    line_color=colors[i % len(colors)]
                ))
            
            # Update layout
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                title="Multi-Dimensional Comparison (Normalized Scale)",
                showlegend=True
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Table with additional metrics for advanced mode
            st.markdown("### Advanced Metrics Comparison")
            
            # Select additional columns to compare
            advanced_cols = ['scenario_name', 'confidence_level', 'risk_rating', 
                           'implementation_time', 'implementation_effort', 'margin_before', 
                           'margin_after', 'margin_after_amortized']
            
            advanced_comparison = comparison_df[advanced_cols].copy()
            
            # Format columns
            advanced_comparison['margin_before'] = advanced_comparison['margin_before'].apply(lambda x: f"${x:,.2f}")
            advanced_comparison['margin_after'] = advanced_comparison['margin_after'].apply(lambda x: f"${x:,.2f}")
            advanced_comparison['margin_after_amortized'] = advanced_comparison['margin_after_amortized'].apply(lambda x: f"${x:,.2f}")
            
            # Rename columns
            advanced_comparison = advanced_comparison.rename(columns={
                'scenario_name': 'Scenario',
                'confidence_level': 'Confidence',
                'risk_rating': 'Risk',
                'implementation_time': 'Implementation Time',
                'implementation_effort': 'Effort (1-10)',
                'margin_before': 'Original Margin',
                'margin_after': 'New Margin',
                'margin_after_amortized': 'Amortized Margin'
            })
            
            # Display table
            st.dataframe(advanced_comparison, use_container_width=True, hide_index=True)
        
        # Export comparison
        st.markdown("### Export Comparison")
        export_format = st.selectbox("Export Format", ["Excel", "CSV"])
        
        if st.button("Export Comparison", use_container_width=True):
            if export_format == "Excel":
                # Create Excel file with multiple sheets
                excel_buffer = io.BytesIO()
                
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    # Key metrics sheet
                    comparison_df[basic_cols].to_excel(writer, sheet_name='Key Metrics', index=False)
                    
                    # Format the Excel sheet
                    workbook = writer.book
                    worksheet = writer.sheets['Key Metrics']
                    
                    # Add some formatting
                    header_format = workbook.add_format({
                        'bold': True,
                        'bg_color': COLOR_SCHEME['primary'],
                        'color': 'white',
                        'border': 1
                    })
                    
                    # Apply formatting to header row
                    for col_num, value in enumerate(basic_cols):
                        worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(col_num, col_num, 15)
                    
                    # Add detailed sheet if in advanced mode
                    if st.session_state.app_mode == "Advanced":
                        # All metrics sheet
                        comparison_df.to_excel(writer, sheet_name='All Metrics', index=False)
                        
                        # Format the detailed sheet
                        worksheet = writer.sheets['All Metrics']
                        
                        # Apply formatting to header row
                        for col_num, value in enumerate(comparison_df.columns):
                            worksheet.write(0, col_num, value, header_format)
                            worksheet.set_column(col_num, col_num, 15)
                
                # Create download button
                st.download_button(
                    label="Download Excel Comparison",
                    data=excel_buffer.getvalue(),
                    file_name="scenario_comparison.xlsx",
                    mime="application/vnd.ms-excel"
                )
            
            elif export_format == "CSV":
                # Create CSV
                csv_data = comparison_df.to_csv(index=False).encode('utf-8')
                
                # Create download button
                st.download_button(
                    label="Download CSV Comparison",
                    data=csv_data,
                    file_name="scenario_comparison.csv",
                    mime="text/csv"
                )
    else:
        st.info("Please select at least 2 scenarios to compare.")

def display_settings(optimizer: ReturnOptimizer):
    """
    Display app settings and data management options.
    
    Args:
        optimizer: ReturnOptimizer instance
    """
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
                file_name="Kaizenalytics_scenarios.json",
                mime="application/json",
                use_container_width=True
            )
            
            # Export as Excel
            try:
                excel_data = io.BytesIO()
                with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
                    optimizer.scenarios.to_excel(writer, index=False, sheet_name='Scenarios')
                    
                    # Add formatting
                    workbook = writer.book
                    worksheet = writer.sheets['Scenarios']
                    
                    # Add header formatting
                    header_format = workbook.add_format({
                        'bold': True,
                        'bg_color': COLOR_SCHEME['primary'],
                        'color': 'white',
                        'border': 1
                    })
                    
                    # Apply formatting to header row
                    for col_num, value in enumerate(optimizer.scenarios.columns):
                        worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(col_num, col_num, 15)
                
                st.download_button(
                    "Export as Excel Spreadsheet",
                    data=excel_data.getvalue(),
                    file_name="Kaizenalytics_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error exporting to Excel: {str(e)}")
            
            # Export as CSV
            csv_data = optimizer.scenarios.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Export as CSV",
                data=csv_data,
                file_name="Kaizenalytics_export.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # Import data
        st.markdown("#### Import Data")
        uploaded_file = st.file_uploader("Upload scenario data (JSON, Excel, or CSV)", type=["json", "xlsx", "csv"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.json'):
                    json_str = uploaded_file.read().decode("utf-8")
                    if optimizer.upload_json(json_str):
                        st.success("JSON data imported successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to import JSON data. Please check the file format.")
                
                elif uploaded_file.name.endswith('.xlsx'):
                    # Read Excel file
                    df = pd.read_excel(uploaded_file)
                    
                    # Convert to JSON
                    json_str = df.to_json(orient='records', date_format='iso')
                    
                    # Import JSON
                    if optimizer.upload_json(json_str):
                        st.success("Excel data imported successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to import Excel data. Please check the file format.")
                
                elif uploaded_file.name.endswith('.csv'):
                    # Read CSV file
                    df = pd.read_csv(uploaded_file)
                    
                    # Convert to JSON
                    json_str = df.to_json(orient='records', date_format='iso')
                    
                    # Import JSON
                    if optimizer.upload_json(json_str):
                        st.success("CSV data imported successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to import CSV data. Please check the file format.")
            
            except Exception as e:
                st.error(f"Error importing data: {str(e)}")
    
    with col2:
        st.markdown("### App Settings")
        
        # Basic/Advanced Mode Toggle
        st.markdown("#### Application Mode")
        
        # Create mode toggle with better UI
        mode_options = ["Basic", "Advanced"]
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("Mode:")
        with col2:
            selected_mode = st.radio(
                "Select Mode", 
                mode_options, 
                horizontal=True,
                label_visibility="collapsed",
                index=mode_options.index(st.session_state.app_mode))
        
        # Update mode if changed
        if selected_mode != st.session_state.app_mode:
            st.session_state.app_mode = selected_mode
            st.success(f"Switched to {selected_mode} Mode")
            st.rerun()
        
        # Theme settings
        st.markdown("#### UI Theme")
        theme_options = ["default", "forest", "sunset", "royal"]
        theme_labels = {
            "default": "Blue (Default)",
            "forest": "Green",
            "sunset": "Orange",
            "royal": "Purple"
        }
        
        selected_theme = st.selectbox("Color Theme", 
                                     options=theme_options,
                                     format_func=lambda x: theme_labels[x],
                                     index=theme_options.index(st.session_state.color_scheme))
        
        # Update theme if changed
        if selected_theme != st.session_state.color_scheme:
            st.session_state.color_scheme = selected_theme
            st.success(f"Theme updated to {theme_labels[selected_theme]}")
            st.rerun()
        
        # Reset data
        st.markdown("#### Data Management")
        if st.button("Add Example Scenarios", use_container_width=True):
            count = optimizer.add_example_scenarios()
            st.success(f"Added {count} example scenarios!")
            st.rerun()
        
        if st.button("Clear All Data", use_container_width=True):
            confirm = st.checkbox("I understand this will delete all scenarios", key="confirm_clear")
            if confirm:
                optimizer.scenarios = pd.DataFrame(columns=optimizer.scenarios.columns)
                optimizer.save_data()
                
                # Also clear comparison list
                if 'compare_list' in st.session_state:
                    st.session_state.compare_list = []
                
                st.success("All data cleared!")
                st.rerun()
    
    # Advanced Settings (only in advanced mode)
    if st.session_state.app_mode == "Advanced":
        st.markdown("### Advanced Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Default Calculation Settings")
            
            # Monte Carlo default settings
            mc_sims = st.slider("Default Monte Carlo Simulations", 
                              min_value=100, 
                              max_value=10000, 
                              value=1000, 
                              step=100)
            
            if 'mc_default_sims' not in st.session_state or st.session_state.mc_default_sims != mc_sims:
                st.session_state.mc_default_sims = mc_sims
                st.success(f"Default Monte Carlo simulations set to {mc_sims}")
        
        with col2:
            st.markdown("#### Export Settings")
        
        # Feature toggles
        st.markdown("#### Feature Toggles")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            monte_carlo_enabled = st.toggle("Monte Carlo Simulation", 
                                          value=True, 
                                          disabled=True)
        
        with col2:
            wizard_enabled = st.toggle("Scenario Wizard", 
                                     value=True, 
                                     disabled=True)
        
        with col3:
            sensitivity_enabled = st.toggle("Sensitivity Analysis", 
                                          value=True, 
                                          disabled=True)
        
        st.info("Feature toggles are currently fixed to 'enabled' in this version.")
        
        # About section
        st.markdown("### About Kaizenalytics Enterprise")
        st.markdown("""
        Kaizenalytics Enterprise is a comprehensive return analytics platform designed to help businesses evaluate and optimize 
        return reduction strategies. The application provides advanced analytics, Monte Carlo simulations, 
        scenario comparison, and visualization tools to make data-driven decisions.
        
        **Version:** 2.0.0  
        **Build Date:** April 2025  
        **License:** MIT
        """)

# Display help modal
def display_help():
    """Display help information in a Streamlit expander."""
    with st.sidebar.expander("Help & Documentation", expanded=False):
        st.markdown("""
        ### Quick Start Guide
        
        **1. Add Scenarios**
        - Create new scenarios using the "Add Scenario" page
        - Use the Scenario Wizard for step-by-step guidance
        - Add example scenarios in Settings for quick testing
        
        **2. Analyze Results**
        - View ROI, breakeven time, and other key metrics
        - Compare scenarios side by side
        - Run Monte Carlo simulations to assess risk
        
        **3. Export & Share**
        - Export data in CSV, or Excel formats
        - Generate comprehensive reports
        - Share insights with stakeholders
        
        ### Core Concepts
        
        **Return Rate:** Percentage of products returned
        
        **Return Reduction:** Estimated percentage reduction in returns after implementing the solution
        
        **ROI Score:** Combined metric that factors in ROI, breakeven time, and reduction rate
        
        **Monte Carlo Simulation:** Runs thousands of simulations with varied parameters to assess risk and probability distributions
        
        ### Need More Help?
        
        Contact support at alexander.popoff@vivehealth.com
        """)

def setup_sidebar():
    """Setup the sidebar navigation."""
    with st.sidebar:
        
        # Mode toggle
        st.markdown(f"""
        <div class="switch-container">
            <span class="switch-label">Basic</span>
            <label class="switch">
                <input type="checkbox" {"checked" if st.session_state.app_mode == "Advanced" else ""}>
                <span class="slider"></span>
            </label>
            <span class="switch-label">Advanced</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("## Navigation")
        
        # Navigation options
        nav_options = ["Dashboard", "Add New Scenario", "Portfolio Analysis", "What-If Analysis", "Settings"]
        
        # Add advanced mode options
        if st.session_state.app_mode == "Advanced":
            nav_options.insert(3, "Monte Carlo")
            nav_options.insert(4, "Compare Scenarios")
        
        # Default to Dashboard if nav_option not set
        default_index = 0
        if 'nav_option' in st.session_state:
            try:
                default_index = nav_options.index(st.session_state.nav_option)
            except ValueError:
                default_index = 0
        
        nav_option = st.radio(
            "Go to:",
            nav_options,
            index=default_index
        )
        
        # Update navigation state
        if 'nav_option' not in st.session_state or st.session_state.nav_option != nav_option:
            st.session_state.nav_option = nav_option
        
        st.markdown("---")
        
        # Scenario Wizard button (only in basic mode)
        if st.session_state.app_mode == "Basic":
            if st.button("Scenario Creation Wizard", key="wizard_btn", use_container_width=True):
                st.session_state.wizard_mode = True
                st.session_state.nav_option = "Add New Scenario"
                st.rerun()
        
        # Help section
        display_help()
        
        # Footer
        st.markdown("---")
        st.caption(f"Kaizenalytics Enterprise v2.0 | {st.session_state.app_mode} Mode")
        st.caption("© 2025 Kaizenalytics Analytics")
        
        return nav_option

def route_content():
    """Route to appropriate content based on navigation state."""
    # Display header
    display_header()
    
    # Load custom CSS
    load_custom_css()
    
    # Route based on navigation option
    if 'nav_option' not in st.session_state:
        st.session_state.nav_option = "Dashboard"
    
    # Handle view scenario details if selected
    if 'view_scenario' in st.session_state and st.session_state['view_scenario'] and 'selected_scenario' in st.session_state:
        display_scenario_details(st.session_state['selected_scenario'], optimizer)
    else:
        # Regular navigation
        if st.session_state.nav_option == "Dashboard":
            display_metrics_overview(optimizer.scenarios)
            display_scenario_table(optimizer.scenarios, optimizer)
        
        elif st.session_state.nav_option == "Add New Scenario":
            if 'wizard_mode' in st.session_state and st.session_state.wizard_mode:
                create_scenario_form(wizard_mode=True)
            else:
                create_scenario_form()
        
        elif st.session_state.nav_option == "Portfolio Analysis":
            display_portfolio_analysis(optimizer.scenarios)
        
        elif st.session_state.nav_option == "What-If Analysis":
            display_what_if_analysis(optimizer)
        
        elif st.session_state.nav_option == "Monte Carlo":
            display_monte_carlo_simulation(optimizer)
        
        elif st.session_state.nav_option == "Compare Scenarios":
            display_scenario_comparison(optimizer)
        
        elif st.session_state.nav_option == "Settings":
            display_settings(optimizer)

def main():
    """Main application function."""
    # Display sidebar
    setup_sidebar()
    
    # Route to appropriate content
    route_content()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.error(traceback.format_exc())
            return False
        except Exception:
            st.error(f"Error loading data: {traceback.format_exc()}")
            return False
    
    def add_scenario(self, 
                  scenario_name: str, 
                  sku: str, 
                  sales_30: float, 
                  avg_sale_price: float, 
                  sales_channel: str,
                  returns_30: float, 
                  solution: str, 
                  solution_cost: float, 
                  additional_cost_per_item: float,
                  current_unit_cost: float, 
                  reduction_rate: float, 
                  sales_365: Optional[float] = None, 
                  returns_365: Optional[float] = None, 
                  tag: Optional[str] = None,
                  notes: Optional[str] = None,
                  confidence_level: Optional[str] = None,
                  risk_rating: Optional[str] = None,
                  implementation_time: Optional[str] = None,
                  implementation_effort: Optional[int] = None) -> Tuple[bool, str]:
        """
        Add a new scenario with calculations.
        
        Args:
            scenario_name: Name of the scenario
            sku: Product SKU
            sales_30: 30-day sales in units
            avg_sale_price: Average sale price per unit
            sales_channel: Sales channel (e.g., "Amazon")
            returns_30: 30-day returns in units
            solution: Description of the solution
            solution_cost: One-time cost of implementing the solution
            additional_cost_per_item: Additional per-unit cost after implementation
            current_unit_cost: Current cost per unit
            reduction_rate: Expected percentage reduction in returns
            sales_365: Annual sales in units (optional)
            returns_365: Annual returns in units (optional)
            tag: Category tag (optional)
            notes: Additional notes (optional)
            confidence_level: Confidence level in estimates (optional)
            risk_rating: Risk rating for the solution (optional)
            implementation_time: Expected implementation time (optional)
            implementation_effort: Implementation effort score (optional)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate inputs
            if not sku or not scenario_name:
                return False, "SKU and Scenario Name are required"
            
            if not isinstance(sales_30, (int, float)) or sales_30 <= 0:
                return False, "Sales must be a positive number"
            
            if not isinstance(returns_30, (int, float)) or returns_30 < 0:
                return False, "Returns must be a non-negative number"
            
            if returns_30 > sales_30:
                return False, "Returns cannot exceed sales"
            
            if not isinstance(current_unit_cost, (int, float)) or current_unit_cost <= 0:
                return False, "Unit cost must be a positive number"
                
            if not isinstance(avg_sale_price, (int, float)) or avg_sale_price <= 0:
                return False, "Sale price must be a positive number"
            
            if avg_sale_price <= current_unit_cost:
                return False, "Sale price must be greater than unit cost"
            
            # Use defaults if not provided
            if sales_365 is None or not isinstance(sales_365, (int, float)) or sales_365 <= 0:
                sales_365 = sales_30 * 12
            
            if returns_365 is None or not isinstance(returns_365, (int, float)) or returns_365 <= 0:
                returns_365 = returns_30 * 12
            
            # Generate a unique ID
            uid = str(uuid.uuid4())[:8]
            
            # Calculate basic metrics
            return_rate = safe_divide(returns_30 * 100, sales_30)
            
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
            amortized_solution_cost = safe_divide(solution_cost, sales_365)
            margin_after_amortized = margin_after - amortized_solution_cost
            
            # Calculate savings and ROI
            savings_per_avoided_return = avg_sale_price - new_unit_cost
            savings_30 = avoided_returns_30 * savings_per_avoided_return
            annual_savings = avoided_returns_365 * savings_per_avoided_return
            
            annual_additional_costs = additional_cost_per_item * sales_365
            net_benefit = annual_savings - annual_additional_costs - solution_cost
            monthly_net_benefit = safe_divide(annual_savings - annual_additional_costs, 12)
            
            # Calculate ROI metrics
            roi = break_even_days = break_even_months = score = None
            if solution_cost > 0 and monthly_net_benefit > 0:
                roi = safe_divide((annual_savings - annual_additional_costs) * 100, solution_cost)  # as percentage
                break_even_days = safe_divide(solution_cost * 30, monthly_net_benefit)
                break_even_months = safe_divide(break_even_days, 30)
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
                'notes': notes,
                'confidence_level': confidence_level,
                'risk_rating': risk_rating,
                'implementation_time': implementation_time,
                'implementation_effort': implementation_effort
            }

            # Add to dataframe
            self.scenarios = pd.concat([self.scenarios, pd.DataFrame([new_row])], ignore_index=True)
            self.save_data()
            return True, "Scenario added successfully!"
        except Exception as e:
            error_details = traceback.format_exc()
            return False, f"Error adding scenario: {str(e)}\n{error_details}"
    
    def get_scenario(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get a scenario by UID."""
        if uid in self.scenarios['uid'].values:
            return self.scenarios[self.scenarios['uid'] == uid].iloc[0].to_dict()
        return None
    
    def delete_scenario(self, uid: str) -> bool:
        """Delete a scenario by UID."""
        if uid in self.scenarios['uid'].values:
            self.scenarios = self.scenarios[self.scenarios['uid'] != uid]
            self.save_data()
            return True
        return False
    
    def update_scenario(self, uid: str, **kwargs) -> Tuple[bool, str]:
        """Update a scenario and recalculate values."""
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
            current['notes'], current['confidence_level'], current['risk_rating'],
            current['implementation_time'], current['implementation_effort']
        )
        
        return success, message
    
    def add_example_scenarios(self) -> int:
        """Add example scenarios for demonstration."""
        added = 0
        for example in self.default_examples:
            success, _ = self.add_scenario(**example)
            if success:
                added += 1
        return added

    def clone_scenario(self, uid: str, new_name: Optional[str] = None) -> Tuple[bool, str]:
        """Clone an existing scenario."""
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
            scenario['notes'], scenario['confidence_level'], scenario['risk_rating'],
            scenario['implementation_time'], scenario['implementation_effort']
        )
        
        return success, message
        
    def run_monte_carlo_simulation(self, 
                                 scenario_uid: str, 
                                 num_simulations: int = 1000, 
                                 param_variations: Optional[Dict[str, float]] = None) -> Tuple[Optional[pd.DataFrame], str]:
        """
        Run Monte Carlo simulation for a given scenario
        
        Args:
            scenario_uid: UID of the base scenario
            num_simulations: Number of simulation runs
            param_variations: Dict with parameters and their variation ranges as percentages
                e.g. {'reduction_rate': 15, 'additional_cost_per_item': 10}
                means reduction_rate can vary by ±15%, additional cost by ±10%
                
        Returns:
            Tuple of (results_dataframe, message)
        """
        scenario = self.get_scenario(scenario_uid)
        if not scenario:
            return None, "Scenario not found"
        
        # Set default parameter variations if not provided
        if not param_variations:
            param_variations = {
                'reduction_rate': 20,             # ±20% variation
                'additional_cost_per_item': 15,   # ±15% variation
                'solution_cost': 10,              # ±10% variation
                'sales_30': 5,                    # ±5% variation
                'returns_30': 10,                 # ±10% variation
                'avg_sale_price': 5               # ±5% variation
            }
        
        # Initialize results dataframe
        results = pd.DataFrame(columns=[
            'simulation_id', 'reduction_rate', 'additional_cost_per_item', 'solution_cost',
            'sales_30', 'returns_30', 'avg_sale_price', 'roi', 'break_even_months', 
            'net_benefit', 'annual_savings', 'annual_additional_costs'
        ])
        
        # Run simulations
        for i in range(num_simulations):
            try:
                # Create variations of parameters
                sim_reduction_rate = max(0, scenario['reduction_rate'] * np.random.uniform(
                    1 - param_variations['reduction_rate']/100,
                    1 + param_variations['reduction_rate']/100
                ))
                
                sim_additional_cost = max(0, scenario['additional_cost_per_item'] * np.random.uniform(
                    1 - param_variations['additional_cost_per_item']/100,
                    1 + param_variations['additional_cost_per_item']/100
                ))
                
                sim_solution_cost = max(0, scenario['solution_cost'] * np.random.uniform(
                    1 - param_variations['solution_cost']/100,
                    1 + param_variations['solution_cost']/100
                ))
                
                sim_sales_30 = max(1, scenario['sales_30'] * np.random.uniform(
                    1 - param_variations['sales_30']/100,
                    1 + param_variations['sales_30']/100
                ))
                
                sim_returns_30 = min(sim_sales_30, max(0, scenario['returns_30'] * np.random.uniform(
                    1 - param_variations['returns_30']/100,
                    1 + param_variations['returns_30']/100
                )))
                
                sim_avg_sale_price = max(scenario['current_unit_cost'], scenario['avg_sale_price'] * np.random.uniform(
                    1 - param_variations['avg_sale_price']/100,
                    1 + param_variations['avg_sale_price']/100
                ))
                
                # Calculate derived metrics
                sim_sales_365 = sim_sales_30 * 12
                sim_returns_365 = sim_returns_30 * 12
                sim_avoided_returns_365 = sim_returns_365 * (sim_reduction_rate / 100)
                
                sim_new_unit_cost = scenario['current_unit_cost'] + sim_additional_cost
                sim_savings_per_avoided_return = sim_avg_sale_price - sim_new_unit_cost
                
                sim_annual_savings = sim_avoided_returns_365 * sim_savings_per_avoided_return
                sim_annual_additional_costs = sim_additional_cost * sim_sales_365
                sim_monthly_net_benefit = safe_divide(sim_annual_savings - sim_annual_additional_costs, 12)
                sim_net_benefit = sim_annual_savings - sim_annual_additional_costs - sim_solution_cost
                
                # Calculate ROI metrics
                sim_roi = None
                sim_break_even_months = None
                
                if sim_solution_cost > 0 and sim_monthly_net_benefit > 0:
                    sim_roi = safe_divide((sim_annual_savings - sim_annual_additional_costs) * 100, sim_solution_cost)
                    sim_break_even_months = safe_divide(sim_solution_cost, sim_monthly_net_benefit)
                
                # Add to results
                results.loc[i] = [
                    i, sim_reduction_rate, sim_additional_cost, sim_solution_cost,
                    sim_sales_30, sim_returns_30, sim_avg_sale_price, sim_roi,
                    sim_break_even_months, sim_net_benefit, sim_annual_savings, 
                    sim_annual_additional_costs
                ]
            except Exception as e:
                # Log error and continue with next simulation
                print(f"Error in simulation {i}: {str(e)}")
                continue
        
        return results, "Simulation completed successfully"
    
    def get_aggregate_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics across all scenarios."""
        if self.scenarios.empty:
            return {
                'total_scenarios': 0,
                'total_investment': 0,
                'total_net_benefit': 0,
                'avg_roi': 0,
                'median_roi': 0,
                'avg_break_even': 0,
                'total_annual_savings': 0,
                'total_additional_costs': 0,
                'avg_reduction_rate': 0,
                'total_avoided_returns': 0,
                'portfolio_roi': 0,
                'best_scenario': None,
                'worst_scenario': None
            }
        
        stats = {
            'total_scenarios': len(self.scenarios),
            'total_investment': self.scenarios['solution_cost'].sum(),
            'total_net_benefit': self.scenarios['net_benefit'].sum(),
            'avg_roi': self.scenarios['roi'].mean() if not self.scenarios['roi'].isnull().all() else 0,
            'median_roi': self.scenarios['roi'].median() if not self.scenarios['roi'].isnull().all() else 0,
            'avg_break_even': self.scenarios['break_even_months'].mean() if not self.scenarios['break_even_months'].isnull().all() else 0,
            'total_annual_savings': self.scenarios['annual_savings'].sum(),
            'total_additional_costs': self.scenarios['annual_additional_costs'].sum(),
            'avg_reduction_rate': self.scenarios['reduction_rate'].mean(),
            'total_avoided_returns': self.scenarios['avoided_returns_365'].sum(),
            'best_scenario': None,
            'worst_scenario': None
        }
        
        # Find best and worst scenarios by ROI
        valid_roi_scenarios = self.scenarios[self.scenarios['roi'] > 0].copy()
        if not valid_roi_scenarios.empty:
            best_idx = valid_roi_scenarios['roi'].idxmax()
            stats['best_scenario'] = {
                'uid': self.scenarios.loc[best_idx, 'uid'],
                'name': self.scenarios.loc[best_idx, 'scenario_name'],
                'roi': self.scenarios.loc[best_idx, 'roi']
            }
        
            worst_idx = valid_roi_scenarios['roi'].idxmin()
            stats['worst_scenario'] = {
                'uid': self.scenarios.loc[worst_idx, 'uid'],
                'name': self.scenarios.loc[worst_idx, 'scenario_name'],
                'roi': self.scenarios.loc[worst_idx, 'roi']
            }
        
        # Portfolio ROI
        stats['portfolio_roi'] = safe_divide(
            (stats['total_annual_savings'] - stats['total_additional_costs']) * 100,
            stats['total_investment']
        )
        
        return stats

# Initialize app
if 'optimizer' not in st.session_state:
    st.session_state.optimizer = ReturnOptimizer()
optimizer = st.session_state.optimizer

# Wizard mode tracking
if 'wizard_step' not in st.session_state:
    st.session_state.wizard_step = 1
    
if 'wizard_data' not in st.session_state:
    st.session_state.wizard_data = {}

# =============================================================================
# UI Component Functions
# =============================================================================

def display_header():
    """Display app header with logo and navigation."""
    col1, col2 = st.columns([1, 5])
    
    # Logo (placeholder - in a real app, replace with actual logo)
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px">
            <h1 style="font-size: 32px; margin: 0; color: {COLOR_SCHEME["primary"]};">🔄</h1>
            <p style="margin: 0; font-weight: 600; color: {COLOR_SCHEME["secondary"]};">Kaizenalytics</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Title and description
    with col2:
        st.title("Return Analytics Platform")
        st.caption("Evaluate return reduction investments to improve profitability and customer experience.")

def display_metrics_overview(df: pd.DataFrame):
    """Display key metrics overview cards."""
    if df.empty:
        st.info("Add or generate scenarios to see metrics.")
        return
    
    # Get aggregate statistics
    stats = optimizer.get_aggregate_statistics()
    
    # Display metrics in cards
    st.subheader("Portfolio Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Total Scenarios</p>
            <p class="metric-value" style="color: {COLOR_SCHEME["primary"]};">{stats['total_scenarios']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Portfolio ROI</p>
            <p class="metric-value" style="color: {get_color_scale(stats['portfolio_roi'], 0, 300)};">{format_percent(stats['portfolio_roi'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Total Net Benefit</p>
            <p class="metric-value" style="color: {get_color_scale(stats['total_net_benefit'], 0, stats['total_net_benefit']*1.5)};">{format_currency(stats['total_net_benefit'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Avg. Break-even</p>
            <p class="metric-value" style="color: {get_color_scale(stats['avg_break_even'], 0, 12, reverse=True)};">{format_number(stats['avg_break_even'])} months</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row with more metrics in advanced mode
    if st.session_state.app_mode == "Advanced":
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <p class="metric-label">Total Investment</p>
                <p class="metric-value" style="color: {COLOR_SCHEME["primary"]};">{format_currency(stats['total_investment'])}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <p class="metric-label">Total Annual Savings</p>
                <p class="metric-value" style="color: {COLOR_SCHEME["positive"]};">{format_currency(stats['total_annual_savings'])}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <p class="metric-label">Avg. Reduction Rate</p>
                <p class="metric-value" style="color: {COLOR_SCHEME["secondary"]};">{format_percent(stats['avg_reduction_rate'])}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-container">
                <p class="metric-label">Total Avoided Returns</p>
                <p class="metric-value" style="color: {COLOR_SCHEME["tertiary"]};">{int(stats['total_avoided_returns'])}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display best and worst scenarios
        if stats['best_scenario']:
            st.markdown("### Top Performing Scenario")
            st.markdown(f"**{stats['best_scenario']['name']}** with ROI of {format_percent(stats['best_scenario']['roi'])}")

def create_scenario_form(wizard_mode: bool = False) -> bool:
    """
    Create form for adding a new scenario.
    
    Args:
        wizard_mode: Whether to use the step-by-step wizard interface
        
    Returns:
        bool: True if scenario was added successfully
    """
    if wizard_mode:
        # Set up wizard interface
        return create_scenario_wizard()
    
    with st.form(key="scenario_form"):
        st.subheader("Add New Scenario")
        
        # Display tips if in advanced mode
        if st.session_state.app_mode == "Advanced":
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="info-box">
                    <p><strong>Pro Tip:</strong> For more guided scenario creation, try the <b>Scenario Wizard</b> in the sidebar.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="success-box">
                    <p><strong>Best Practice:</strong> Use specific SKU identifiers and detailed solution descriptions for better tracking.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="warning-box">
                    <p><strong>Important:</strong> Be conservative with reduction rate estimates - real-world results are typically 15-30%.</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Basic Information
        st.markdown("### Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            scenario_name = st.text_input("Scenario Name", 
                                      help="A memorable name for this return reduction strategy")
            
            sku = st.text_input("SKU/Product ID", 
                             help="Product identifier")
            
            sales_channel = st.text_input("Sales Channel", 
                                       help="Main platform where product is sold (e.g., Amazon, Shopify, Website)")
            
        with col2:
            solution = st.text_input("Proposed Solution", 
                                  help="Description of the return reduction strategy")
            
            tag = st.selectbox("Category Tag", 
                            ["Packaging", "Product Description", "Size/Fit", "Quality", "Customer Education", "Other"],
                            help="Category of return reduction strategy")
            
            if st.session_state.app_mode == "Advanced":
                notes = st.text_area("Notes", 
                                  help="Additional details about the solution")
            else:
                notes = None
        
        # Sales and Returns Data
        st.markdown("### Sales & Returns Data")
        col1, col2 = st.columns(2)
        
        with col1:
            sales_30 = st.number_input("30-day Sales (units)", 
                                    min_value=0, 
                                    help="Units sold in the last 30 days")
            
            returns_30 = st.number_input("30-day Returns (units)", 
                                      min_value=0, 
                                      help="Units returned in the last 30 days")
            
        with col2:
            avg_sale_price = st.number_input("Average Sale Price ($)", 
                                          min_value=0.0, 
                                          format="%.2f", 
                                          help="Average selling price per unit")
            
            current_unit_cost = st.number_input("Current Unit Cost ($)", 
                                             min_value=0.0, 
                                             format="%.2f", 
                                             help="Cost to produce/acquire each unit")
            
        # Calculated return rate
        if sales_30 > 0 and returns_30 > 0:
            return_rate = (returns_30 / sales_30) * 100
            st.info(f"Current Return Rate: {return_rate:.2f}%")
        
        # Solution Implementation
        st.markdown("### Solution Implementation")
        col1, col2 = st.columns(2)
        
        with col1:
            solution_cost = st.number_input("Total Solution Cost ($)", 
                                         min_value=0.0, 
                                         format="%.2f", 
                                         help="One-time investment required for the solution")
            
            additional_cost_per_item = st.number_input("Additional Cost per Item ($)", 
                                                    min_value=0.0, 
                                                    format="%.2f", 
                                                    help="Any additional per-unit cost from implementing the solution")
        
        with col2:
            reduction_rate = st.slider("Estimated Return Reduction (%)", 
                                    min_value=0, 
                                    max_value=100, 
                                    value=20, 
                                    help="Expected percentage reduction in returns after implementing the solution")
            
            # Optional annual data
            annual_data = st.checkbox("Use custom annual data", 
                                   help="By default, 30-day data is multiplied by 12")
            
            if annual_data:
                sales_365 = st.number_input("365-day Sales (units)", 
                                         min_value=0, 
                                         help="Total units sold in a year (defaults to 30-day * 12)")
                
                returns_365 = st.number_input("365-day Returns (units)", 
                                           min_value=0, 
                                           help="Total units returned in a year (defaults to 30-day * 12)")
            else:
                sales_365 = sales_30 * 12
                returns_365 = returns_30 * 12
        
        # Advanced information (only in advanced mode)
        if st.session_state.app_mode == "Advanced":
            st.markdown("### Advanced Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                confidence_level = st.selectbox("Confidence Level", 
                                             ["High", "Medium", "Low"],
                                             help="Confidence in the return reduction estimate")
            
            with col2:
                risk_rating = st.selectbox("Risk Rating",
                                        ["Low", "Medium", "High"],
                                        help="Level of risk associated with implementing this solution")
            
            with col3:
                implementation_time = st.selectbox("Implementation Time",
                                                ["0-1 month", "1-3 months", "3-6 months", "6+ months"],
                                                help="Estimated time to implement the solution")
                
            implementation_effort = st.slider("Implementation Effort (1-10)", 
                                           min_value=1, 
                                           max_value=10, 
                                           value=5,
                                           help="Relative effort required to implement (1=Easy, 10=Very Difficult)")
        else:
            confidence_level = None
            risk_rating = None
            implementation_time = None
            implementation_effort = None
        
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
                    annual_roi = (annual_net / solution_cost) * 100
                else:
                    breakeven_months = None
                    annual_roi = None
                
                # Display key metrics
                st.markdown("### Key Metrics")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Return Rate Reduction", 
                            f"{reduction_rate}%", 
                            delta=f"{return_rate - (return_rate * (1 - reduction_rate/100)):.1f}%")
                
                with col2:
                    if breakeven_months:
                        st.metric("Breakeven Time", f"{breakeven_months:.1f} months")
                    else:
                        st.metric("Breakeven Time", "N/A")
                
                with col3:
                    if annual_roi:
                        st.metric("Annual ROI", f"{annual_roi:.1f}%")
                    else:
                        st.metric("Annual ROI", "N/A")
            
        except Exception as e:
            st.error(f"Error calculating metrics: {str(e)}")
        
        # Navigation and save buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Edit"):
                st.session_state.wizard_step = 4
                st.rerun()
        
        with col2:
            if st.button("Save Scenario"):
                # Extract all data from wizard
                try:
                    scenario_data = {
                        'scenario_name': st.session_state.wizard_data.get('scenario_name', ''),
                        'sku': st.session_state.wizard_data.get('sku', ''),
                        'sales_30': st.session_state.wizard_data.get('sales_30', 0),
                        'avg_sale_price': st.session_state.wizard_data.get('avg_sale_price', 0.0),
                        'sales_channel': st.session_state.wizard_data.get('sales_channel', ''),
                        'returns_30': st.session_state.wizard_data.get('returns_30', 0),
                        'solution': st.session_state.wizard_data.get('solution', ''),
                        'solution_cost': st.session_state.wizard_data.get('solution_cost', 0.0),
                        'additional_cost_per_item': st.session_state.wizard_data.get('additional_cost_per_item', 0.0),
                        'current_unit_cost': st.session_state.wizard_data.get('current_unit_cost', 0.0),
                        'reduction_rate': st.session_state.wizard_data.get('reduction_rate', 0),
                        'sales_365': st.session_state.wizard_data.get('sales_365', 0),
                        'returns_365': st.session_state.wizard_data.get('returns_365', 0),
                        'tag': st.session_state.wizard_data.get('tag', ''),
                        'notes': st.session_state.wizard_data.get('notes', ''),
                        'confidence_level': st.session_state.wizard_data.get('confidence_level', None),
                        'risk_rating': st.session_state.wizard_data.get('risk_rating', None),
                        'implementation_time': st.session_state.wizard_data.get('implementation_time', None),
                        'implementation_effort': st.session_state.wizard_data.get('implementation_effort', None)
                    }
                    
                    # Add the scenario
                    success, message = optimizer.add_scenario(**scenario_data)
                    
                    if success:
                        st.success("Scenario saved successfully!")
                        
                        # Reset wizard
                        st.session_state.wizard_step = 1
                        st.session_state.wizard_data = {}
                        
                        # Redirect to dashboard
                        st.session_state.nav_option = "Dashboard"
                        st.rerun()
                    else:
                        st.error(message)
                
                except Exception as e:
                    st.error(f"Error saving scenario: {str(e)}")
    
    return True_cost / monthly_net
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
                current_unit_cost, reduction_rate, sales_365, returns_365, tag,
                notes, confidence_level, risk_rating, implementation_time, implementation_effort
            )
            
            if success:
                st.success(message)
                return True
            else:
                st.error(message)
                return False
    
    return False

def create_scenario_wizard() -> bool:
    """
    Create a step-by-step wizard for adding a scenario.
    
    Returns:
        bool: True if wizard was completed successfully
    """
    # Initialize wizard_data if needed
    if 'wizard_data' not in st.session_state:
        st.session_state.wizard_data = {}
    
    # Display progress tracker
    st.markdown("### Scenario Creation Wizard")
    steps = ["Product Info", "Sales Data", "Return Solution", "Cost & Impact", "Review"]
    
    st.markdown("""
    <div class="progress-container">
    """, unsafe_allow_html=True)
    
    for i, step in enumerate(steps, 1):
        if i < st.session_state.wizard_step:
            status = "completed"
        elif i == st.session_state.wizard_step:
            status = "active"
        else:
            status = ""
        
        st.markdown(f"""
        <div class="progress-step {status}">{i}
            <div class="progress-label">{step}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    # Step 1: Product Information
    if st.session_state.wizard_step == 1:
        st.subheader("Step 1: Product Information")
        
        col1, col2 = st.columns(2)
        with col1:
            scenario_name = st.text_input("Scenario Name", 
                value=st.session_state.wizard_data.get('scenario_name', ''),
                help="A memorable name for this return reduction strategy")
            
            sku = st.text_input("SKU/Product ID", 
                value=st.session_state.wizard_data.get('sku', ''),
                help="Product identifier")
        
        with col2:
            sales_channel = st.text_input("Sales Channel", 
                value=st.session_state.wizard_data.get('sales_channel', ''),
                help="Main platform where product is sold (e.g., Amazon, Shopify, Website)")
            
            tag = st.selectbox("Category Tag", 
                ["Packaging", "Product Description", "Size/Fit", "Quality", "Customer Education", "Other"],
                index=["Packaging", "Product Description", "Size/Fit", "Quality", "Customer Education", "Other"].index(
                    st.session_state.wizard_data.get('tag', 'Packaging')),
                help="Category of return reduction strategy")
        
        notes = st.text_area("Product Notes (Optional)", 
            value=st.session_state.wizard_data.get('notes', ''),
            help="Additional context about the product")
        
        # Save data
        if st.button("Next: Sales Data"):
            # Validate inputs
            if not scenario_name:
                st.error("Please enter a Scenario Name")
                return False
            
            if not sku:
                st.error("Please enter a SKU/Product ID")
                return False
            
            # Save to session state
            st.session_state.wizard_data.update({
                'scenario_name': scenario_name,
                'sku': sku,
                'sales_channel': sales_channel,
                'tag': tag,
                'notes': notes
            })
            
            # Go to next step
            st.session_state.wizard_step = 2
            st.rerun()
    
    # Step 2: Sales and Returns Data
    elif st.session_state.wizard_step == 2:
        st.subheader("Step 2: Sales & Returns Data")
        
        col1, col2 = st.columns(2)
        with col1:
            sales_30 = st.number_input("30-day Sales (units)", 
                value=int(st.session_state.wizard_data.get('sales_30', 0)),
                min_value=0, 
                help="Units sold in the last 30 days")
            
            avg_sale_price = st.number_input("Average Sale Price ($)", 
                value=float(st.session_state.wizard_data.get('avg_sale_price', 0.0)),
                min_value=0.0, 
                format="%.2f", 
                help="Average selling price per unit")
        
        with col2:
            returns_30 = st.number_input("30-day Returns (units)", 
                value=int(st.session_state.wizard_data.get('returns_30', 0)),
                min_value=0, 
                help="Units returned in the last 30 days")
            
            current_unit_cost = st.number_input("Current Unit Cost ($)", 
                value=float(st.session_state.wizard_data.get('current_unit_cost', 0.0)),
                min_value=0.0, 
                format="%.2f", 
                help="Cost to produce/acquire each unit")
        
        # Calculate return rate
        if sales_30 > 0 and returns_30 > 0:
            return_rate = (returns_30 / sales_30) * 100
            st.info(f"Current Return Rate: {return_rate:.2f}%")
            
            # Industry benchmark comparison
            if return_rate > 30:
                st.warning("Your return rate is higher than the industry average (20-30%). This presents a significant opportunity for improvement.")
            elif return_rate > 15:
                st.info("Your return rate is within typical industry averages (15-30%).")
            else:
                st.success("Your return rate is below industry average. Well done!")
        
        # Annual data option
        annual_data = st.checkbox("Use custom annual data", 
            value=st.session_state.wizard_data.get('use_custom_annual', False),
            help="By default, 30-day data is multiplied by 12")
        
        if annual_data:
            col1, col2 = st.columns(2)
            with col1:
                sales_365 = st.number_input("365-day Sales (units)", 
                    value=int(st.session_state.wizard_data.get('sales_365', sales_30 * 12)),
                    min_value=0, 
                    help="Total units sold in a year")
            
            with col2:
                returns_365 = st.number_input("365-day Returns (units)", 
                    value=int(st.session_state.wizard_data.get('returns_365', returns_30 * 12)),
                    min_value=0, 
                    help="Total units returned in a year")
        else:
            sales_365 = sales_30 * 12
            returns_365 = returns_30 * 12
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.wizard_step = 1
                st.rerun()
        
        with col2:
            if st.button("Next: Return Solution"):
                # Validate inputs
                if sales_30 <= 0:
                    st.error("Please enter a value greater than 0 for 30-day Sales")
                    return False
                
                if returns_30 > sales_30:
                    st.error("Returns cannot exceed sales")
                    return False
                
                if current_unit_cost <= 0 or avg_sale_price <= 0:
                    st.error("Unit cost and sale price must be greater than zero")
                    return False
                
                if avg_sale_price <= current_unit_cost:
                    st.error("Sale price must be greater than unit cost")
                    return False
                
                # Save to session state
                st.session_state.wizard_data.update({
                    'sales_30': sales_30,
                    'returns_30': returns_30,
                    'avg_sale_price': avg_sale_price,
                    'current_unit_cost': current_unit_cost,
                    'use_custom_annual': annual_data,
                    'sales_365': sales_365,
                    'returns_365': returns_365
                })
                
                # Go to next step
                st.session_state.wizard_step = 3
                st.rerun()
    
    # Step 3: Return Solution
    elif st.session_state.wizard_step == 3:
        st.subheader("Step 3: Return Solution")
        
        solution = st.text_area("Proposed Solution", 
            value=st.session_state.wizard_data.get('solution', ''),
            help="Detailed description of the return reduction strategy")
        
        # Solution recommendations based on tag
        tag = st.session_state.wizard_data.get('tag', '')
        if tag:
            st.markdown(f"### Recommended Solutions for {tag}")
            
            if tag == "Packaging":
                st.markdown("""
                * **Premium protective packaging** with cushioned inserts
                * **Right-sized boxes** to prevent movement during shipping
                * **Clear unboxing instructions** to prevent damage during opening
                * **Sustainable packaging** with clear recycling instructions
                """)
            elif tag == "Product Description":
                st.markdown("""
                * **Enhanced product detail pages** with comprehensive specifications
                * **360° product photography** showing all angles and features
                * **Size comparison charts** with common reference objects
                * **Video demonstrations** of product use and features
                """)
            elif tag == "Size/Fit":
                st.markdown("""
                * **Interactive size finder tools** with body measurements
                * **Augmented reality try-on** technology
                * **Consistent sizing across product lines**
                * **Detailed measurement guides** with visual instructions
                """)
            elif tag == "Quality":
                st.markdown("""
                * **Enhanced quality control** processes during manufacturing
                * **Pre-shipping inspection** procedures
                * **Material upgrades** for common failure points
                * **Durability testing** protocols for high-stress components
                """)
            elif tag == "Customer Education":
                st.markdown("""
                * **Improved product manuals** with clear setup instructions
                * **Video tutorials** for complex products
                * **FAQ expansion** addressing common issues
                * **Post-purchase email sequence** with usage tips
                """)
        
        # Additional solution details
        st.markdown("### Solution Details")
        col1, col2 = st.columns(2)
        
        with col1:
            confidence_level = st.selectbox("Confidence Level", 
                ["High", "Medium", "Low"],
                index=["High", "Medium", "Low"].index(
                    st.session_state.wizard_data.get('confidence_level', 'Medium')),
                help="How confident are you in this solution's effectiveness?")
        
        with col2:
            implementation_time = st.selectbox("Implementation Time",
                ["0-1 month", "1-3 months", "3-6 months", "6+ months"],
                index=["0-1 month", "1-3 months", "3-6 months", "6+ months"].index(
                    st.session_state.wizard_data.get('implementation_time', '1-3 months')),
                help="How long will it take to implement this solution?")
        
        implementation_effort = st.slider("Implementation Effort (1-10)", 
            min_value=1, max_value=10, 
            value=int(st.session_state.wizard_data.get('implementation_effort', 5)),
            help="How difficult will this solution be to implement? (1=Easy, 10=Very Difficult)")
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.wizard_step = 2
                st.rerun()
        
        with col2:
            if st.button("Next: Cost & Impact"):
                # Validate inputs
                if not solution:
                    st.error("Please describe your proposed solution")
                    return False
                
                # Save to session state
                st.session_state.wizard_data.update({
                    'solution': solution,
                    'confidence_level': confidence_level,
                    'implementation_time': implementation_time,
                    'implementation_effort': implementation_effort
                })
                
                # Go to next step
                st.session_state.wizard_step = 4
                st.rerun()
    
    # Step 4: Cost and Impact
    elif st.session_state.wizard_step == 4:
        st.subheader("Step 4: Cost & Impact")
        
        col1, col2 = st.columns(2)
        with col1:
            solution_cost = st.number_input("Total Solution Cost ($)", 
                value=float(st.session_state.wizard_data.get('solution_cost', 0.0)),
                min_value=0.0, 
                format="%.2f", 
                help="One-time investment required for implementation")
        
        with col2:
            additional_cost_per_item = st.number_input("Additional Cost per Item ($)", 
                value=float(st.session_state.wizard_data.get('additional_cost_per_item', 0.0)),
                min_value=0.0, 
                format="%.2f", 
                help="Any ongoing per-unit cost increase from the solution")
        
        # Return reduction estimate
        st.markdown("### Impact Estimate")
        
        # Get data for context
        tag = st.session_state.wizard_data.get('tag', '')
        confidence = st.session_state.wizard_data.get('confidence_level', 'Medium')
        
        # Suggested reduction range based on tag and confidence
        suggested_min = 15
        suggested_max = 30
        
        if tag == "Size/Fit":
            suggested_min = 20
            suggested_max = 40
        elif tag == "Product Description":
            suggested_min = 15
            suggested_max = 35
        elif tag == "Quality":
            suggested_min = 25
            suggested_max = 45
        
        if confidence == "Low":
            suggested_min = max(10, suggested_min - 5)
            suggested_max = suggested_max - 5
        elif confidence == "High":
            suggested_min = suggested_min + 5
            suggested_max = min(60, suggested_max + 5)
        
        st.info(f"Based on your solution category and confidence level, similar initiatives typically achieve a {suggested_min}%-{suggested_max}% reduction in returns.")
        
        reduction_rate = st.slider("Estimated Return Reduction (%)", 
            min_value=0, max_value=100, 
            value=int(st.session_state.wizard_data.get('reduction_rate', (suggested_min + suggested_max) // 2)),
            help="Expected percentage reduction in returns after implementing the solution")
        
        risk_rating = st.selectbox("Risk Rating",
            ["Low", "Medium", "High"],
            index=["Low", "Medium", "High"].index(
                st.session_state.wizard_data.get('risk_rating', 'Medium')),
            help="Level of risk associated with this solution")
        
        # Calculate preview metrics
        sales_30 = st.session_state.wizard_data.get('sales_30', 0)
        returns_30 = st.session_state.wizard_data.get('returns_30', 0)
        avg_sale_price = st.session_state.wizard_data.get('avg_sale_price', 0.0)
        current_unit_cost = st.session_state.wizard_data.get('current_unit_cost', 0.0)
        
        # Safe calculations with proper error handling
        try:
            if sales_30 > 0 and returns_30 > 0:
                return_rate = (returns_30 / sales_30) * 100
                avoided_returns = returns_30 * (reduction_rate / 100)
                new_return_rate = return_rate * (1 - reduction_rate/100)
                
                # ROI calculations
                new_unit_cost = current_unit_cost + additional_cost_per_item
                monthly_savings = avoided_returns * (avg_sale_price - new_unit_cost)
                monthly_cost = sales_30 * additional_cost_per_item
                monthly_net = monthly_savings - monthly_cost
                annual_net = monthly_net * 12
                
                if solution_cost > 0 and monthly_net > 0:
                    breakeven_months = solution_cost / monthly_net
                    annual_roi = (annual_net / solution_cost) * 100
                else:
                    breakeven_months = None
                    annual_roi = None
                
                # Display financial impact
                st.markdown("### Financial Impact")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Monthly Net Benefit:** ${monthly_net:.2f}")
                    st.markdown(f"**Annual Net Benefit:** ${annual_net:.2f}")
                    
                    if breakeven_months:
                        st.markdown(f"**Breakeven Time:** {breakeven_months:.1f} months")
                    else:
                        st.markdown("**Breakeven Time:** N/A")
                
                with col2:
                    if annual_roi:
                        st.markdown(f"**Return on Investment:** {annual_roi:.1f}%")
                    else:
                        st.markdown("**Return on Investment:** N/A")
                    
                    st.markdown(f"**Avoided Returns (Monthly):** {avoided_returns:.1f} units")
                    st.markdown(f"**New Return Rate:** {new_return_rate:.2f}%")
        except Exception as e:
            st.error(f"Error in calculations: {str(e)}")
        
        # Allow final edits
        st.markdown("### Final Adjustments (Optional)")
        st.caption("Make any final adjustments before proceeding to review")
        
        final_scenario_name = st.text_input("Final Scenario Name", 
                                    value=st.session_state.wizard_data.get('scenario_name', ''))
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.wizard_step = 3
                st.rerun()
        
        with col2:
            if st.button("Next: Review"):
                # Update name if changed
                if final_scenario_name:
                    st.session_state.wizard_data['scenario_name'] = final_scenario_name
                
                # Save to session state
                st.session_state.wizard_data.update({
                    'solution_cost': solution_cost,
                    'additional_cost_per_item': additional_cost_per_item,
                    'reduction_rate': reduction_rate,
                    'risk_rating': risk_rating
                })
                
                # Go to next step
                st.session_state.wizard_step = 5
                st.rerun()
    
    # Step 5: Review and Save
    elif st.session_state.wizard_step == 5:
        st.subheader("Step 5: Review & Save")
        st.markdown("### Scenario Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Basic Information")
            st.markdown(f"**Scenario Name:** {st.session_state.wizard_data.get('scenario_name', '')}")
            st.markdown(f"**SKU/Product ID:** {st.session_state.wizard_data.get('sku', '')}")
            st.markdown(f"**Sales Channel:** {st.session_state.wizard_data.get('sales_channel', '')}")
            st.markdown(f"**Category:** {st.session_state.wizard_data.get('tag', '')}")
            
            st.markdown("#### Solution Details")
            st.markdown(f"**Solution:** {st.session_state.wizard_data.get('solution', '')}")
            st.markdown(f"**Implementation Time:** {st.session_state.wizard_data.get('implementation_time', '')}")
            st.markdown(f"**Confidence Level:** {st.session_state.wizard_data.get('confidence_level', '')}")
            st.markdown(f"**Risk Rating:** {st.session_state.wizard_data.get('risk_rating', '')}")
        
        with col2:
            st.markdown("#### Financial Data")
            st.markdown(f"**Monthly Sales:** {st.session_state.wizard_data.get('sales_30', 0)} units")
            st.markdown(f"**Monthly Returns:** {st.session_state.wizard_data.get('returns_30', 0)} units")
            st.markdown(f"**Average Sale Price:** ${st.session_state.wizard_data.get('avg_sale_price', 0.0):.2f}")
            st.markdown(f"**Current Unit Cost:** ${st.session_state.wizard_data.get('current_unit_cost', 0.0):.2f}")
            
            st.markdown("#### Solution Costs & Impact")
            st.markdown(f"**Solution Cost:** ${st.session_state.wizard_data.get('solution_cost', 0.0):.2f}")
            st.markdown(f"**Additional Cost/Item:** ${st.session_state.wizard_data.get('additional_cost_per_item', 0.0):.2f}")
            st.markdown(f"**Expected Reduction:** {st.session_state.wizard_data.get('reduction_rate', 0)}%")
        
        # Calculate key metrics for summary
        try:
            sales_30 = st.session_state.wizard_data.get('sales_30', 0)
            returns_30 = st.session_state.wizard_data.get('returns_30', 0)
            avg_sale_price = st.session_state.wizard_data.get('avg_sale_price', 0.0)
            current_unit_cost = st.session_state.wizard_data.get('current_unit_cost', 0.0)
            reduction_rate = st.session_state.wizard_data.get('reduction_rate', 0.0)
            solution_cost = st.session_state.wizard_data.get('solution_cost', 0.0)
            additional_cost_per_item = st.session_state.wizard_data.get('additional_cost_per_item', 0.0)
            
            if sales_30 > 0 and returns_30 > 0:
                return_rate = (returns_30 / sales_30) * 100
                avoided_returns = returns_30 * (reduction_rate / 100)
                new_unit_cost = current_unit_cost + additional_cost_per_item
                monthly_savings = avoided_returns * (avg_sale_price - new_unit_cost)
                monthly_cost = sales_30 * additional_cost_per_item
                monthly_net = monthly_savings - monthly_cost
                annual_net = monthly_net * 12
                
                # Calculate ROI and breakeven if applicable
                if solution_cost > 0 and monthly_net > 0:
                    breakeven_months = solution
