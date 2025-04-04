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

# Improved compatibility check for Streamlit versions
if not hasattr(st, "rerun"):
    if hasattr(st, "experimental_rerun"):
        st.rerun = st.experimental_rerun  # compatibility shim
    else:
        # Fallback for very old Streamlit versions
        def rerun_fallback():
            raise RuntimeError("Your Streamlit version doesn't support rerun functionality")
        st.rerun = rerun_fallback

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

# Initialize app mode if not present
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = "Basic"

# Define color schemes function for better organization
def init_color_schemes() -> Dict[str, Dict[str, str]]:
    """
    Initialize and return available color schemes.
    Isolating this function makes it easier to add new schemes.
    
    Returns:
        Dict[str, Dict[str, str]]: Available color schemes
    """
    return {
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
        },
        # High contrast theme for accessibility
        "high_contrast": {
            "primary": "#0040FF",
            "secondary": "#008000",
            "tertiary": "#800080",
            "background": "#FFFFFF",
            "positive": "#008000",
            "negative": "#FF0000",
            "warning": "#FF8000",
            "neutral": "#0000FF",
            "text_dark": "#000000",
            "text_light": "#FFFFFF",
            "card_bg": "#FFFFFF",
            "sidebar_bg": "#000000",
            "hover": "#E0E0E0"
        }
    }

# Initialize color schemes
COLOR_SCHEMES = init_color_schemes()

def get_color_scheme(scheme_name: Optional[str] = None) -> Dict[str, str]:
    """
    Get a color scheme by name with error handling.
    
    Args:
        scheme_name: Name of the color scheme to get
        
    Returns:
        Dict[str, str]: The requested color scheme or default if not found
    """
    if scheme_name is None:
        scheme_name = st.session_state.get('color_scheme', 'default')
    
    # Safely get the scheme with fallback to default
    if scheme_name in COLOR_SCHEMES:
        return COLOR_SCHEMES[scheme_name]
    else:
        st.warning(f"Color scheme '{scheme_name}' not found. Using default.")
        return COLOR_SCHEMES['default']

def update_color_scheme(scheme_name: str) -> None:
    """
    Update the color scheme and reload CSS.
    
    Args:
        scheme_name: Name of the color scheme to set
    """
    if scheme_name in COLOR_SCHEMES:
        st.session_state.color_scheme = scheme_name
        # Trigger reloading of CSS when color scheme changes
        if 'css_loaded' in st.session_state:
            st.session_state.css_loaded = False
    else:
        st.warning(f"Color scheme '{scheme_name}' not found. Using default.")
        st.session_state.color_scheme = 'default'

# Initialize color scheme in session state if not present
if 'color_scheme' not in st.session_state:
    st.session_state.color_scheme = "default"

# Get current color scheme safely
COLOR_SCHEME = get_color_scheme()

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
# CSS Styling Modules
# =============================================================================

def get_base_css(colors: Dict[str, str]) -> str:
    """Base styling for the application"""
    return f"""
    /* Main styling */
    body, .stApp {{
        background-color: {colors["background"]};
        color: {colors["text_dark"]};
        font-family: 'Inter', sans-serif;
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: {colors["primary"]};
    }}
    """

def get_form_css(colors: Dict[str, str]) -> str:
    """Form control styling"""
    return f"""
    /* Button styling */
    .stButton>button {{
        background-color: {colors["secondary"]};
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }}
    .stButton>button:hover {{
        background-color: {colors["primary"]};
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
        border-color: {colors["secondary"]};
        box-shadow: 0 0 0 3px rgba(34, 167, 242, 0.2);
    }}
    """

def get_component_css(colors: Dict[str, str]) -> str:
    """Component styling (cards, metrics, etc.)"""
    return f"""
    /* Cards */
    .css-card {{
        border-radius: 12px;
        padding: 1.5rem;
        background-color: {colors["card_bg"]};
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
    """

def get_table_css(colors: Dict[str, str]) -> str:
    """Table and data display styling"""
    return f"""
    /* Dataframe styling */
    .stDataFrame thead tr th {{
        background-color: {colors["primary"]};
        color: white;
        padding: 10px 15px;
        font-weight: 500;
    }}
    .stDataFrame tbody tr:nth-child(even) {{
        background-color: rgba(245, 248, 255, 0.5);
    }}
    .stDataFrame tbody tr:hover {{
        background-color: {colors["hover"]};
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
        background-color: {colors["primary"]};
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
        border-bottom: 2px solid {colors["primary"]};
    }}
    
    .styled-table tbody tr.active-row {{
        font-weight: bold;
        color: {colors["primary"]};
    }}
    """

def get_tabs_css(colors: Dict[str, str]) -> str:
    """Tabs and navigation styling"""
    return f"""
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
        border-bottom: 2px solid {colors["secondary"]};
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
        background-color: {colors["primary"]};
        color: white;
    }}
    
    .progress-step.completed {{
        background-color: {colors["positive"]};
        color: white;
    }}
    
    .progress-label {{
        position: absolute;
        bottom: -25px;
        white-space: nowrap;
        font-size: 0.8rem;
        color: {colors["text_dark"]};
    }}
    """

def get_custom_components_css(colors: Dict[str, str]) -> str:
    """Custom components styling"""
    return f"""
    /* Tooltips */
    .tooltip {{
        position: relative;
        display: inline-block;
        cursor: help;
    }}
    
    .tooltip .tooltiptext {{
        visibility: hidden;
        width: 240px;
        background-color: {colors["text_dark"]};
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
        background-color: {colors["hover"]};
        border-left: 5px solid {colors["neutral"]};
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }}
    
    .warning-box {{
        background-color: rgba(245, 158, 11, 0.1);
        border-left: 5px solid {colors["warning"]};
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }}
    
    .success-box {{
        background-color: rgba(34, 197, 94, 0.1);
        border-left: 5px solid {colors["positive"]};
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }}
    
    .loading-spinner {{
        text-align: center;
        margin: 20px 0;
    }}
    
    /* New feature badge */
    .new-feature {{
        background-color: {colors["warning"]};
        color: white;
        font-size: 0.7rem;
        padding: 3px 8px;
        border-radius: 10px;
        margin-left: 8px;
        display: inline-block;
        vertical-align: middle;
        font-weight: 600;
    }}
    """

def get_charts_css(colors: Dict[str, str]) -> str:
    """Charts and visualizations styling"""
    return f"""
    /* Charts */
    .js-plotly-plot {{
        border-radius: 12px;
        background-color: white;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }}
    """

def get_sidebar_css(colors: Dict[str, str]) -> str:
    """Sidebar styling"""
    return f"""
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {colors["sidebar_bg"]};
    }}
    
    [data-testid="stSidebar"] .sidebar-content {{
        padding: 2rem 1rem;
    }}
    
    /* Sidebar headings and text */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6 {{
        color: {colors["text_light"]};
    }}
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div {{
        color: {colors["text_light"]};
    }}
    
    /* Mode toggle button */
    .mode-toggle {{
        background-color: {colors["secondary"]};
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
        background-color: {colors["primary"]};
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
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
        color: {colors["text_light"]};
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
        background-color: {colors["primary"]};
    }}
    
    input:focus + .slider {{
        box-shadow: 0 0 1px {colors["primary"]};
    }}
    
    input:checked + .slider:before {{
        transform: translateX(26px);
    }}
    """

def get_buttons_css(colors: Dict[str, str]) -> str:
    """Button and control styling"""
    return f"""
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
        background-color: {colors["secondary"]};
        border-color: {colors["secondary"]};
        color: white;
        font-weight: 500;
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
        color: {colors["text_dark"]};
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
        background-color: {colors["secondary"]};
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
        cursor: pointer;
    }}
    
    .next-button:hover {{
        background-color: {colors["primary"]};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    /* Floating help button */
    .help-button {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: {colors["secondary"]};
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
        background-color: {colors["primary"]};
        transform: scale(1.1);
    }}
    """

def load_custom_css():
    """
    Load custom CSS styling for the application.
    Now modularized for better maintainability and with performance optimization.
    """
    # Only load CSS once per session or when color scheme changes
    if not st.session_state.get('css_loaded', False):
        # Get current color scheme safely
        colors = get_color_scheme()
        
        # Build CSS from modules
        css_modules = [
            get_base_css(colors),
            get_form_css(colors),
            get_component_css(colors),
            get_table_css(colors),
            get_tabs_css(colors),
            get_custom_components_css(colors),
            get_charts_css(colors),
            get_sidebar_css(colors),
            get_buttons_css(colors)
        ]
        
        # Combine all CSS modules
        complete_css = "\n".join(css_modules)
        
        # Apply the CSS
        st.markdown(f"<style>{complete_css}</style>", unsafe_allow_html=True)
        
        # Mark CSS as loaded
        st.session_state.css_loaded = True

# =============================================================================
# Utility Functions
# =============================================================================

def format_currency(amount: Optional[float]) -> str:
    """
    Format a value as currency with proper handling of None/NaN values.
    
    Args:
        amount: The amount to format
        
    Returns:
        str: Formatted currency string
    """
    if pd.isna(amount) or amount is None:
        return "-"
    return f"${amount:,.2f}"

def format_percent(value: Optional[float]) -> str:
    """
    Format a value as percentage with proper handling of None/NaN values.
    
    Args:
        value: The value to format
        
    Returns:
        str: Formatted percentage string
    """
    if pd.isna(value) or value is None:
        return "-"
    return f"{value:.2f}%"

def format_number(value: Optional[float]) -> str:
    """
    Format a value as number with commas and proper handling of None/NaN values.
    
    Args:
        value: The value to format
        
    Returns:
        str: Formatted number string
    """
    if pd.isna(value) or value is None:
        return "-"
    return f"{value:,.2f}"

def get_icon(value: Optional[float], threshold: float = 0, positive_is_good: bool = True) -> str:
    """
    Get an icon based on value comparison to threshold.
    
    Args:
        value: The value to evaluate
        threshold: The threshold for comparison
        positive_is_good: Whether positive values are considered good
        
    Returns:
        str: Icon representing the value's status
    """
    if pd.isna(value) or value is None:
        return "❓"
    
    if positive_is_good:
        return "✅" if value >= threshold else "⚠️"
    else:
        return "✅" if value <= threshold else "⚠️"

def calculate_return_rate(returns: int, sales: int) -> float:
    """
    Calculate return rate safely.
    
    Args:
        returns: Number of returns
        sales: Number of sales
        
    Returns:
        float: Return rate as a percentage (0-100)
    """
    if sales == 0:
        return 0.0
    return (returns / sales) * 100

def calculate_roi_score(roi: float, breakeven_days: float, reduction_rate: float) -> Optional[float]:
    """
    Calculate a weighted ROI score combining multiple factors.
    
    Args:
        roi: Return on investment percentage
        breakeven_days: Days until breakeven
        reduction_rate: Return reduction percentage
        
    Returns:
        Optional[float]: Combined score (0-100) or None if inputs are invalid
    """
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
    """
    Get color from a green-yellow-red scale based on value.
    
    Args:
        value: The value to evaluate
        min_val: Minimum value in the scale
        max_val: Maximum value in the scale
        reverse: Whether to reverse the color scale
        
    Returns:
        str: Hex color code
    """
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
    """
    Display a label with a tooltip.
    
    Args:
        label: The label text
        help_text: The tooltip text
        
    Returns:
        str: HTML for label with tooltip
    """
    tooltip_html = f"""
    <div class="tooltip">{label}
        <span class="tooltiptext">{help_text}</span>
    </div>
    """
    return tooltip_html

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning a default if divisor is zero.
    
    Args:
        a: Numerator
        b: Denominator
        default: Default value to return if division is invalid
        
    Returns:
        float: Result of division or default value
    """
    try:
        if b == 0:
            return default
        return a / b
    except:
        return default

def generate_uid() -> str:
    """
    Generate a unique identifier for scenarios.
    
    Returns:
        str: Unique ID
    """
    return str(uuid.uuid4())[:8]

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
            uid = generate_uid()
            
            # Calculate basic metrics
            return_rate = safe_divide(returns_30 * 100, sales_30)
            
            # Calculate avoided returns
            avoided_returns_30 = returns_30 * (reduction_rate / 100)
            avoided_returns_365 = returns_365 * (reduction_rate / 100)
            
            # Calculate costs and benefits
            return_processing_cost = 15  # Average cost to process a return
            return_cost_30 = returns_30 * (current_unit_cost * 0.25 + return_processing_cost)
            return_cost_annual = returns_365 * (current_unit_cost * 0.25 + return_processing_cost)
            
            # Calculate revenue impact (assuming 20% of returns lead to lost sales)
            lost_sale_percent = 0.2
            revenue_impact_30 = returns_30 * lost_sale_percent * avg_sale_price
            revenue_impact_annual = returns_365 * lost_sale_percent * avg_sale_price
            
            # Calculate new unit cost
            new_unit_cost = current_unit_cost + additional_cost_per_item
            
            # Calculate savings from avoided returns
            savings_30 = (
                avoided_returns_30 * (current_unit_cost * 0.25 + return_processing_cost) +
                avoided_returns_30 * lost_sale_percent * avg_sale_price
            )
            
            annual_savings = (
                avoided_returns_365 * (current_unit_cost * 0.25 + return_processing_cost) +
                avoided_returns_365 * lost_sale_percent * avg_sale_price
            )
            
            # Calculate annual additional costs
            annual_additional_costs = sales_365 * additional_cost_per_item
            
            # Calculate net benefit
            net_benefit = annual_savings - annual_additional_costs - solution_cost
            monthly_net_benefit = net_benefit / 12
            
            # Calculate break-even
            if solution_cost > 0 and monthly_net_benefit > 0:
                break_even_days = solution_cost / (monthly_net_benefit / 30)
                break_even_months = break_even_days / 30
            else:
                break_even_days = float('inf')
                break_even_months = float('inf')
            
            # Calculate ROI
            if solution_cost > 0:
                roi = (net_benefit / solution_cost) * 100
            else:
                roi = float('inf') if net_benefit > 0 else 0.0
            
            # Calculate margin impact
            margin_before = avg_sale_price - current_unit_cost
            margin_after = avg_sale_price - new_unit_cost
            
            # Calculate amortized margin
            amortized_solution_cost = solution_cost / sales_365
            margin_after_amortized = margin_after - amortized_solution_cost
            
            # Calculate ROI score
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
                'timestamp': datetime.now().isoformat(),
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
                
                # Apply the return_processing_cost of 15
                return_processing_cost = 15
                sim_savings_per_avoided_return = (scenario['current_unit_cost'] * 0.25 + return_processing_cost) + 0.2 * sim_avg_sale_price
                
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
    st.markdown("#### Solution")
            st.markdown(f"**Proposed Solution:** {st.session_state.wizard_data.get('solution', '')}")
            st.markdown(f"**Implementation Time:** {st.session_state.wizard_data.get('implementation_time', '')}")
            st.markdown(f"**Implementation Effort:** {st.session_state.wizard_data.get('implementation_effort', '')} / 10")
            st.markdown(f"**Confidence Level:** {st.session_state.wizard_data.get('confidence_level', '')}")
            st.markdown(f"**Risk Rating:** {st.session_state.wizard_data.get('risk_rating', '')}")
        
        with col2:
            st.markdown("#### Financial Impact")
            st.markdown(f"**30-day Sales:** {st.session_state.wizard_data.get('sales_30', 0)} units")
            st.markdown(f"**30-day Returns:** {st.session_state.wizard_data.get('returns_30', 0)} units")
            st.markdown(f"**Average Sale Price:** ${st.session_state.wizard_data.get('avg_sale_price', 0.0):.2f}")
            st.markdown(f"**Current Unit Cost:** ${st.session_state.wizard_data.get('current_unit_cost', 0.0):.2f}")
            st.markdown(f"**Solution Cost:** ${st.session_state.wizard_data.get('solution_cost', 0.0):.2f}")
            st.markdown(f"**Additional Per-Item Cost:** ${st.session_state.wizard_data.get('additional_cost_per_item', 0.0):.2f}")
            st.markdown(f"**Target Reduction Rate:** {st.session_state.wizard_data.get('reduction_rate', 0)}%")
        
        st.markdown("### Financial Projections")
        # Calculate projections for display
        try:
            data = st.session_state.wizard_data
            
            # Basic data
            sales_30 = data.get('sales_30', 0)
            returns_30 = data.get('returns_30', 0)
            avg_sale_price = data.get('avg_sale_price', 0.0)
            current_unit_cost = data.get('current_unit_cost', 0.0)
            reduction_rate = data.get('reduction_rate', 0)
            solution_cost = data.get('solution_cost', 0.0)
            additional_cost_per_item = data.get('additional_cost_per_item', 0.0)
            sales_365 = data.get('sales_365', sales_30 * 12)
            returns_365 = data.get('returns_365', returns_30 * 12)
            
            # Calculate metrics
            return_rate = (returns_30 / sales_30) * 100 if sales_30 > 0 else 0
            new_return_rate = return_rate * (1 - reduction_rate/100)
            avoided_returns_30 = returns_30 * (reduction_rate / 100)
            avoided_returns_365 = returns_365 * (reduction_rate / 100)
            
            # Financial impact calculations
            return_processing_cost = 15  # Average cost to process a return
            lost_sale_percent = 0.2  # Percentage of returns leading to lost sales
            
            return_cost_30 = returns_30 * (current_unit_cost * 0.25 + return_processing_cost)
            revenue_impact_30 = returns_30 * lost_sale_percent * avg_sale_price
            
            new_unit_cost = current_unit_cost + additional_cost_per_item
            
            savings_30 = (
                avoided_returns_30 * (current_unit_cost * 0.25 + return_processing_cost) +
                avoided_returns_30 * lost_sale_percent * avg_sale_price
            )
            
            annual_savings = (
                avoided_returns_365 * (current_unit_cost * 0.25 + return_processing_cost) +
                avoided_returns_365 * lost_sale_percent * avg_sale_price
            )
            
            annual_additional_costs = sales_365 * additional_cost_per_item
            net_benefit = annual_savings - annual_additional_costs - solution_cost
            monthly_net_benefit = net_benefit / 12
            
            # Break-even and ROI
            if solution_cost > 0 and monthly_net_benefit > 0:
                break_even_days = solution_cost / (monthly_net_benefit / 30)
                break_even_months = break_even_days / 30
                roi = (net_benefit / solution_cost) * 100
            else:
                break_even_days = float('inf')
                break_even_months = float('inf')
                roi = 0.0 if solution_cost > 0 else float('inf')
            
            # Display projections in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Return Rate", f"{return_rate:.2f}%")
                st.metric("New Return Rate", f"{new_return_rate:.2f}%")
                st.metric("Monthly Avoided Returns", f"{avoided_returns_30:.1f} units")
            
            with col2:
                st.metric("Monthly Savings", f"${savings_30:.2f}")
                st.metric("Annual Savings", f"${annual_savings:.2f}")
                st.metric("Additional Annual Costs", f"${annual_additional_costs:.2f}")
            
            with col3:
                st.metric("Break-even Period", f"{break_even_months:.1f} months" if break_even_months != float('inf') else "N/A")
                st.metric("Annual Net Benefit", f"${net_benefit:.2f}")
                st.metric("ROI", f"{roi:.1f}%" if roi != float('inf') else "∞")
            
            # Create summary for confirmation
            st.markdown("### Ready to save?")
            
            if break_even_months < 6 and roi > 100:
                st.success("✅ This scenario shows excellent potential with a quick break-even period and strong ROI.")
            elif break_even_months < 12 and roi > 50:
                st.info("📈 This scenario shows good potential with a reasonable break-even period.")
            elif net_benefit > 0:
                st.warning("⚠️ This scenario is profitable but may take time to realize significant returns.")
            else:
                st.error("❌ This scenario may not be financially viable based on current estimates.")
            
        except Exception as e:
            st.error(f"Error in calculations: {str(e)}")
        
        # Navigation and save
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.wizard_step = 4
                st.rerun()
        
        with col2:
            if st.button("Save Scenario"):
                # Extract all data from wizard
                data = st.session_state.wizard_data
                
                # Create scenario
                success, message = optimizer.add_scenario(
                    data.get('scenario_name', ''), 
                    data.get('sku', ''), 
                    data.get('sales_30', 0), 
                    data.get('avg_sale_price', 0.0), 
                    data.get('sales_channel', ''),
                    data.get('returns_30', 0), 
                    data.get('solution', ''), 
                    data.get('solution_cost', 0.0), 
                    data.get('additional_cost_per_item', 0.0),
                    data.get('current_unit_cost', 0.0), 
                    data.get('reduction_rate', 0), 
                    data.get('sales_365', None), 
                    data.get('returns_365', None), 
                    data.get('tag', None),
                    data.get('notes', None),
                    data.get('confidence_level', None),
                    data.get('risk_rating', None),
                    data.get('implementation_time', None),
                    data.get('implementation_effort', None)
                )
                
                if success:
                    st.success("🎉 Scenario saved successfully!")
                    # Reset wizard
                    st.session_state.wizard_step = 1
                    st.session_state.wizard_data = {}
                    return True
                else:
                    st.error(message)
                    return False
    
    return False

def display_scenarios_table(df: pd.DataFrame):
    """
    Display scenarios in a sortable, filterable table.
    
    Args:
        df: Dataframe containing scenarios
    """
    if df.empty:
        st.info("No scenarios found. Add a new scenario or generate example scenarios.")
        return
    
    # Table display options
    st.subheader("Scenario Comparison")
    
    # Filtering options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sku_filter = st.text_input("Filter by SKU", "")
    
    with col2:
        tag_options = ["All"] + sorted(df["tag"].unique().tolist())
        tag_filter = st.selectbox("Filter by Category", tag_options)
    
    with col3:
        sort_options = {
            "ROI (High to Low)": ("roi", False),
            "ROI (Low to High)": ("roi", True),
            "Break-Even (Fastest First)": ("break_even_days", True),
            "Net Benefit (High to Low)": ("net_benefit", False),
            "Recent First": ("timestamp", False),
            "Scenario Name": ("scenario_name", True)
        }
        sort_by = st.selectbox("Sort by", list(sort_options.keys()))
    
    # Apply filters
    filtered_df = df.copy()
    
    if sku_filter:
        filtered_df = filtered_df[filtered_df["sku"].str.contains(sku_filter, case=False)]
    
    if tag_filter != "All":
        filtered_df = filtered_df[filtered_df["tag"] == tag_filter]
    
    # Apply sorting
    sort_column, ascending = sort_options[sort_by]
    filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending)
    
    # Display table with key metrics
    display_df = filtered_df[['scenario_name', 'sku', 'sales_30', 'returns_30', 
                         'return_rate', 'reduction_rate', 'solution_cost', 
                         'break_even_months', 'roi', 'tag']].copy()
    
    # Format columns for display
    display_df["return_rate"] = display_df["return_rate"].apply(format_percent)
    display_df["reduction_rate"] = display_df["reduction_rate"].apply(format_percent)
    display_df["solution_cost"] = display_df["solution_cost"].apply(format_currency)
    display_df["break_even_months"] = display_df["break_even_months"].apply(
        lambda x: f"{x:.1f}" if x != float('inf') else "N/A")
    display_df["roi"] = display_df["roi"].apply(
        lambda x: f"{x:.1f}%" if x != float('inf') else "∞")
    
    # Rename columns for display
    display_df.columns = ["Scenario", "SKU", "Sales (30d)", "Returns (30d)", 
                       "Return Rate", "Reduction Target", "Solution Cost", 
                       "Break-Even", "ROI", "Category"]
    
    st.dataframe(display_df, use_container_width=True)
    
    # Display number of results
    st.caption(f"Showing {len(filtered_df)} of {len(df)} scenarios")
    
    # Actions for scenarios
    if not filtered_df.empty:
        st.subheader("Scenario Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_scenario = st.selectbox(
                "Select Scenario for Actions",
                filtered_df["scenario_name"].tolist()
            )
            scenario_uid = filtered_df[filtered_df["scenario_name"] == selected_scenario]["uid"].iloc[0]
        
        with col2:
            action = st.selectbox(
                "Choose Action",
                ["View Details", "Delete Scenario", "Clone Scenario", "Run Simulation"]
            )
        
        with col3:
            if st.button("Execute Action"):
                if action == "View Details":
                    st.session_state.view_scenario = scenario_uid
                elif action == "Delete Scenario":
                    if optimizer.delete_scenario(scenario_uid):
                        st.success(f"Scenario '{selected_scenario}' deleted")
                        st.rerun()
                    else:
                        st.error("Failed to delete scenario")
                elif action == "Clone Scenario":
                    success, message = optimizer.clone_scenario(scenario_uid)
                    if success:
                        st.success(f"Scenario cloned: {message}")
                        st.rerun()
                    else:
                        st.error(f"Failed to clone scenario: {message}")
                elif action == "Run Simulation":
                    st.session_state.simulate_scenario = scenario_uid

def display_scenario_details(scenario_uid: str):
    """
    Display detailed view of a single scenario.
    
    Args:
        scenario_uid: UID of the scenario to display
    """
    scenario = optimizer.get_scenario(scenario_uid)
    if not scenario:
        st.error("Scenario not found")
        return
    
    # Display header with back button
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("← Back to Scenarios"):
            st.session_state.view_scenario = None
            st.rerun()
    
    with col2:
        st.title(scenario["scenario_name"])
        st.caption(f"SKU: {scenario['sku']} | Category: {scenario['tag']}")
    
    # Main details in tabs
    tab1, tab2, tab3 = st.tabs(["Overview", "Financial Impact", "Detailed Metrics"])
    
    # Overview tab
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Solution Details")
            st.markdown(f"**Solution Approach:** {scenario['solution']}")
            st.markdown(f"**Implementation Time:** {scenario.get('implementation_time', 'Not specified')}")
            st.markdown(f"**Risk Rating:** {scenario.get('risk_rating', 'Not specified')}")
            
            if scenario.get('notes'):
                st.markdown("**Notes:**")
                st.markdown(f"> {scenario['notes']}")
            
            st.subheader("Key Metrics")
            metric_cols = st.columns(2)
            
            with metric_cols[0]:
                st.metric("ROI", format_percent(scenario["roi"]))
                st.metric("Break-Even Period", f"{scenario['break_even_months']:.1f} months" 
                         if scenario['break_even_months'] != float('inf') else "N/A")
            
            with metric_cols[1]:
                st.metric("Reduction Target", format_percent(scenario["reduction_rate"]))
                st.metric("Return Rate Impact", 
                         f"{scenario['return_rate']:.2f}% → {scenario['return_rate'] * (1 - scenario['reduction_rate']/100):.2f}%")
        
        with col2:
            st.subheader("Current Return Metrics")
            current_metrics = {
                "Monthly Sales": scenario["sales_30"],
                "Monthly Returns": scenario["returns_30"],
                "Annual Sales": scenario["sales_365"],
                "Annual Returns": scenario["returns_365"],
                "Return Rate": f"{scenario['return_rate']:.2f}%",
                "Avg. Sale Price": f"${scenario['avg_sale_price']:.2f}",
                "Current Unit Cost": f"${scenario['current_unit_cost']:.2f}"
            }
            
            st.table(pd.DataFrame(list(current_metrics.items()), columns=["Metric", "Value"]))
            
            st.subheader("Solution Economics")
            solution_metrics = {
                "Solution Cost": f"${scenario['solution_cost']:.2f}",
                "Additional Cost Per Item": f"${scenario['additional_cost_per_item']:.2f}",
                "New Unit Cost": f"${scenario['new_unit_cost']:.2f}",
                "Annual Additional Costs": f"${scenario['annual_additional_costs']:.2f}",
                "Margin Before": f"${scenario['margin_before']:.2f}",
                "Margin After": f"${scenario['margin_after']:.2f}"
            }
            
            st.table(pd.DataFrame(list(solution_metrics.items()), columns=["Metric", "Value"]))
    
    # Financial Impact tab
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Return Reduction Impact")
            
            # Create chart showing returns before and after
            chart_data = pd.DataFrame({
                'Month': range(1, 13),
                'Current Returns': [scenario['returns_30'] for _ in range(12)],
                'Projected Returns': [scenario['returns_30'] * (1 - scenario['reduction_rate']/100) for _ in range(12)]
            })
            
            fig = px.line(chart_data, x='Month', y=['Current Returns', 'Projected Returns'],
                        labels={'value': 'Returns', 'variable': 'Scenario'},
                        title='Monthly Returns: Before vs After',
                        color_discrete_map={
                            'Current Returns': COLOR_SCHEME["negative"],
                            'Projected Returns': COLOR_SCHEME["positive"]
                        })
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Avoided returns metrics
            st.metric("Monthly Avoided Returns", f"{scenario['avoided_returns_30']:.1f} units")
            st.metric("Annual Avoided Returns", f"{scenario['avoided_returns_365']:.1f} units")
        
        with col2:
            st.subheader("Financial Returns")
            
            # ROI and payback visualization
            if scenario['break_even_months'] != float('inf'):
                # Create payback period chart
                periods = min(24, int(scenario['break_even_months'] * 2))
                monthly_benefit = scenario['monthly_net_benefit']
                
                chart_data = pd.DataFrame({
                    'Month': range(1, periods + 1),
                    'Cumulative Benefit': [monthly_benefit * m for m in range(1, periods + 1)],
                    'Solution Cost': [scenario['solution_cost'] for _ in range(periods)]
                })
                
                fig = px.line(chart_data, x='Month', y=['Cumulative Benefit', 'Solution Cost'],
                            labels={'value': 'Amount ($)', 'variable': 'Metric'},
                            title='Return On Investment Over Time',
                            color_discrete_map={
                                'Cumulative Benefit': COLOR_SCHEME["positive"],
                                'Solution Cost': COLOR_SCHEME["negative"]
                            })
                
                # Add a vertical line at break-even point
                fig.add_vline(x=scenario['break_even_months'], line_dash="dash", 
                             line_color=COLOR_SCHEME["warning"],
                             annotation_text="Break-even Point", 
                             annotation_position="top right")
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Break-even period could not be calculated for this scenario.")
            
            # Financial metrics
            metrics_col1, metrics_col2 = st.columns(2)
            
            with metrics_col1:
                st.metric("Monthly Net Benefit", format_currency(scenario['monthly_net_benefit']))
                st.metric("Annual Net Benefit", format_currency(scenario['net_benefit']))
            
            with metrics_col2:
                st.metric("Solution Cost", format_currency(scenario['solution_cost']))
                st.metric("Annual Additional Costs", format_currency(scenario['annual_additional_costs']))
    
    # Detailed Metrics tab
    with tab3:
        st.subheader("All Scenario Metrics")
        
        # Create a more organized view of all metrics
        metrics_categories = {
            "Basic Information": [
                ("Scenario Name", scenario['scenario_name']),
                ("SKU", scenario['sku']),
                ("Category", scenario.get('tag', 'Not specified')),
                ("Sales Channel", scenario.get('sales_channel', 'Not specified')),
                ("Solution", scenario['solution'])
            ],
            
            "Sales & Returns": [
                ("30-day Sales", f"{scenario['sales_30']} units"),
                ("30-day Returns", f"{scenario['returns_30']} units"),
                ("365-day Sales", f"{scenario['sales_365']} units"),
                ("365-day Returns", f"{scenario['returns_365']} units"),
                ("Return Rate", format_percent(scenario['return_rate'])),
                ("New Return Rate", format_percent(scenario['return_rate'] * (1 - scenario['reduction_rate']/100))),
                ("Avoided Returns (30d)", f"{scenario['avoided_returns_30']:.1f} units"),
                ("Avoided Returns (365d)", f"{scenario['avoided_returns_365']:.1f} units")
            ],
            
            "Financial Data": [
                ("Average Sale Price", format_currency(scenario['avg_sale_price'])),
                ("Current Unit Cost", format_currency(scenario['current_unit_cost'])),
                ("New Unit Cost", format_currency(scenario['new_unit_cost'])),
                ("Margin Before", format_currency(scenario['margin_before'])),
                ("Margin After", format_currency(scenario['margin_after'])),
                ("Margin After (Amortized)", format_currency(scenario['margin_after_amortized']))
            ],
            
            "Return Costs": [
                ("30-day Return Cost", format_currency(scenario['return_cost_30'])),
                ("Annual Return Cost", format_currency(scenario['return_cost_annual'])),
                ("30-day Revenue Impact", format_currency(scenario['revenue_impact_30'])),
                ("Annual Revenue Impact", format_currency(scenario['revenue_impact_annual']))
            ],
            
            "Solution Metrics": [
                ("Solution Cost", format_currency(scenario['solution_cost'])),
                ("Additional Cost per Item", format_currency(scenario['additional_cost_per_item'])),
                ("Reduction Rate", format_percent(scenario['reduction_rate'])),
                ("30-day Savings", format_currency(scenario['savings_30'])),
                ("Annual Savings", format_currency(scenario['annual_savings'])),
                ("Annual Additional Costs", format_currency(scenario['annual_additional_costs'])),
                ("Monthly Net Benefit", format_currency(scenario['monthly_net_benefit'])),
                ("Net Benefit", format_currency(scenario['net_benefit']))
            ],
            
            "ROI Metrics": [
                ("Break-even Days", f"{scenario['break_even_days']:.1f}" if scenario['break_even_days'] != float('inf') else "N/A"),
                ("Break-even Months", f"{scenario['break_even_months']:.1f}" if scenario['break_even_months'] != float('inf') else "N/A"),
                ("ROI", format_percent(scenario['roi'])),
                ("Score", f"{scenario['score']:.1f}/100" if scenario['score'] else "N/A")
            ]
        }
        
        for category, metrics in metrics_categories.items():
            with st.expander(category, expanded=True):
                # Create a dataframe for better display
                df = pd.DataFrame(metrics, columns=["Metric", "Value"])
                st.table(df)

def display_monte_carlo_simulation(scenario_uid: str):
    """
    Display Monte Carlo simulation interface and results.
    
    Args:
        scenario_uid: UID of the scenario to simulate
    """
    scenario = optimizer.get_scenario(scenario_uid)
    if not scenario:
        st.error("Scenario not found")
        return
    
    # Display header with back button
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("← Back to Scenarios"):
            st.session_state.simulate_scenario = None
            st.rerun()
    
    with col2:
        st.title(f"Monte Carlo Simulation: {scenario['scenario_name']}")
        st.caption(f"SKU: {scenario['sku']} | Category: {scenario['tag']}")
    
    # Simulation configuration
    st.subheader("Simulation Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_simulations = st.slider("Number of Simulations", 
                                min_value=100, 
                                max_value=5000, 
                                value=1000, 
                                step=100,
                                help="More simulations provide more accurate results but take longer")
        
        # Confidence level for the prediction intervals
        confidence_level = st.select_slider("Confidence Level", 
                                      options=[0.8, 0.85, 0.9, 0.95, 0.99], 
                                      value=0.9,
                                      format_func=lambda x: f"{int(x*100)}%",
                                      help="Higher confidence levels produce wider prediction intervals")
    
    with col2:
        st.markdown("### Variation Ranges")
        st.caption("Set the parameter variation ranges (±%) for the simulation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            reduction_variation = st.slider("Reduction Rate Variation", 5, 40, 20, 5,
                                        help="How much the reduction rate might vary")
            
            solution_cost_variation = st.slider("Solution Cost Variation", 0, 30, 10, 5,
                                            help="How much the solution cost might vary")
            
            sales_variation = st.slider("Sales Volume Variation", 0, 25, 5, 5,
                                    help="How much the sales volume might vary")
        
        with col2:
            additional_cost_variation = st.slider("Additional Cost Variation", 0, 30, 15, 5,
                                             help="How much the additional per-item cost might vary")
            
            returns_variation = st.slider("Returns Variation", 0, 30, 10, 5,
                                      help="How much the return volume might vary")
            
            price_variation = st.slider("Price Variation", 0, 20, 5, 5,
                                    help="How much the average sale price might vary")
    
    # Parameter variations
    param_variations = {
        'reduction_rate': reduction_variation,
        'additional_cost_per_item': additional_cost_variation,
        'solution_cost': solution_cost_variation,
        'sales_30': sales_variation,
        'returns_30': returns_variation,
        'avg_sale_price': price_variation
    }
    
    # Run simulation button
    if st.button("Run Monte Carlo Simulation"):
        with st.spinner("Running simulation..."):
            # Run the simulation
            results_df, message = optimizer.run_monte_carlo_simulation(
                scenario_uid, 
                num_simulations=num_simulations, 
                param_variations=param_variations
            )
            
            if results_df is not None:
                # Store results in session state for reuse
                st.session_state.monte_carlo_results = results_df
                st.session_state.monte_carlo_scenario = scenario_uid
                st.success(f"Simulation completed with {len(results_df)} iterations")
            else:
                st.error(f"Simulation failed: {message}")
    
    # Display simulation results if available
    if ('monte_carlo_results' in st.session_state and 
        'monte_carlo_scenario' in st.session_state and 
        st.session_state.monte_carlo_scenario == scenario_uid):
        
        results_df = st.session_state.monte_carlo_results
        
        st.subheader("Simulation Results")
        
        # Summary statistics
        st.markdown("### Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        # Calculate ROI statistics
        roi_data = results_df['roi'].dropna()
        
        with col1:
            st.metric("Median ROI", f"{roi_data.median():.1f}%")
            
            # Calculate ROI confidence intervals
            lower_bound = np.percentile(roi_data, (1 - confidence_level) * 100 / 2)
            upper_bound = np.percentile(roi_data, 100 - (1 - confidence_level) * 100 / 2)
            
            st.metric(f"{int(confidence_level*100)}% CI for ROI", f"{lower_bound:.1f}% to {upper_bound:.1f}%")
        
        # Calculate break-even statistics
        breakeven_data = results_df['break_even_months'].dropna()
        
        with col2:
            st.metric("Median Break-even", f"{breakeven_data.median():.1f} months")
            
            # Calculate break-even confidence intervals
            lower_bound = np.percentile(breakeven_data, (1 - confidence_level) * 100 / 2)
            upper_bound = np.percentile(breakeven_data, 100 - (1 - confidence_level) * 100 / 2)
            
            st.metric(f"{int(confidence_level*100)}% CI for Break-even", f"{lower_bound:.1f} to {upper_bound:.1f} months")
        
        # Calculate net benefit statistics
        net_benefit_data = results_df['net_benefit'].dropna()
        
        with col3:
            st.metric("Median Net Benefit", f"${net_benefit_data.median():.2f}")
            
            # Calculate net benefit confidence intervals
            lower_bound = np.percentile(net_benefit_data, (1 - confidence_level) * 100 / 2)
            upper_bound = np.percentile(net_benefit_data, 100 - (1 - confidence_level) * 100 / 2)
            
            st.metric(f"{int(confidence_level*100)}% CI for Net Benefit", 
                   f"${lower_bound:.2f} to ${upper_bound:.2f}")
        
        # Probability calculations
        st.markdown("### Risk Assessment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Probability of positive ROI
            prob_positive_roi = (roi_data > 0).mean() * 100
            st.metric("Probability of Positive ROI", f"{prob_positive_roi:.1f}%")
            
            # Probability of ROI > 100%
            prob_high_roi = (roi_data > 100).mean() * 100
            st.metric("Probability of ROI > 100%", f"{prob_high_roi:.1f}%")
        
        with col2:
            # Probability of break-even < 6 months
            prob_quick_breakeven = (breakeven_data < 6).mean() * 100
            st.metric("Probability of Break-even < 6 months", f"{prob_quick_breakeven:.1f}%")
            
            # Probability of break-even < 12 months
            prob_annual_breakeven = (breakeven_data < 12).mean() * 100
            st.metric("Probability of Break-even < 12 months", f"{prob_annual_breakeven:.1f}%")
        
        # Visualizations
        st.markdown("### Simulation Visualizations")
        
        tab1, tab2 = st.tabs(["ROI Distribution", "Break-even Distribution"])
        
        with tab1:
            # ROI distribution
            fig = make_subplots(rows=2, cols=1, 
                             shared_xaxes=True,
                             vertical_spacing=0.1,
                             subplot_titles=("ROI Distribution", "Cumulative Probability"))
            
            # Histogram for ROI
            fig.add_trace(go.Histogram(
                x=roi_data,
                nbinsx=30,
                marker_color=COLOR_SCHEME["primary"],
                name="Frequency"
            ), row=1, col=1)
            
            # Add vertical line for median
            fig.add_vline(x=roi_data.median(), line_dash="dash", 
                       line_color=COLOR_SCHEME["warning"],
                       annotation_text="Median", 
                       annotation_position="top right",
                       row=1, col=1)
            
            # Add vertical lines for confidence interval
            lower_bound = np.percentile(roi_data, (1 - confidence_level) * 100 / 2)
            upper_bound = np.percentile(roi_data, 100 - (1 - confidence_level) * 100 / 2)
            
            fig.add_vline(x=lower_bound, line_dash="dash", 
                       line_color=COLOR_SCHEME["negative"],
                       row=1, col=1)
            
            fig.add_vline(x=upper_bound, line_dash="dash", 
                       line_color=COLOR_SCHEME["negative"],
                       row=1, col=1)
            
            # Cumulative distribution
            sorted_roi = np.sort(roi_data)
            cumulative = np.arange(1, len(sorted_roi) + 1) / len(sorted_roi)
            
            fig.add_trace(go.Scatter(
                x=sorted_roi,
                y=cumulative,
                mode='lines',
                name="Cumulative Probability",
                line=dict(color=COLOR_SCHEME["secondary"])
            ), row=2, col=1)
            
            # Add reference line at 50% probability
            fig.add_hline(y=0.5, line_dash="dash", 
                       line_color=COLOR_SCHEME["warning"],
                       annotation_text="50% Probability", 
                       annotation_position="top right",
                       row=2, col=1)
            
            fig.update_layout(
                height=600,
                title_text=f"ROI Distribution ({int(confidence_level*100)}% Confidence Interval)",
                showlegend=False,
                xaxis2_title="Return on Investment (%)",
                yaxis_title="Frequency",
                yaxis2_title="Probability",
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Break-even distribution
            fig = make_subplots(rows=2, cols=1, 
                             shared_xaxes=True,
                             vertical_spacing=0.1,
                             subplot_titles=("Break-even Distribution", "Cumulative Probability"))
            
            # Histogram for break-even
            fig.add_trace(go.Histogram(
                x=breakeven_data,
                nbinsx=30,
                marker_color=COLOR_SCHEME["primary"],
                name="Frequency"
            ), row=1, col=1)
            
            # Add vertical line for median
            fig.add_vline(x=breakeven_data.median(), line_dash="dash", 
                       line_color=COLOR_SCHEME["warning"],
                       annotation_text="Median", 
                       annotation_position="top right",
                       row=1, col=1)
            
            # Add vertical lines for confidence interval
            lower_bound = np.percentile(breakeven_data, (1 - confidence_level) * 100 / 2)
            upper_bound = np.percentile(breakeven_data, 100 - (1 - confidence_level) * 100 / 2)
            
            fig.add_vline(x=lower_bound, line_dash="dash", 
                       line_color=COLOR_SCHEME["negative"],
                       row=1, col=1)
            
            fig.add_vline(x=upper_bound, line_dash="dash", 
                       line_color=COLOR_SCHEME["negative"],
                       row=1, col=1)
            
            # Cumulative distribution
            sorted_be = np.sort(breakeven_data)
            cumulative = np.arange(1, len(sorted_be) + 1) / len(sorted_be)
            
            fig.add_trace(go.Scatter(
                x=sorted_be,
                y=cumulative,
                mode='lines',
                name="Cumulative Probability",
                line=dict(color=COLOR_SCHEME["secondary"])
            ), row=2, col=1)
            
            # Add reference line at 50% probability
            fig.add_hline(y=0.5, line_dash="dash", 
                       line_color=COLOR_SCHEME["warning"],
                       annotation_text="50% Probability", 
                       annotation_position="top right",
                       row=2, col=1)
            
            fig.update_layout(
                height=600,
                title_text=f"Break-even Distribution ({int(confidence_level*100)}% Confidence Interval)",
                showlegend=False,
                xaxis2_title="Break-even Period (months)",
                yaxis_title="Frequency",
                yaxis2_title="Probability",
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Parameter sensitivity analysis
        st.subheader("Parameter Sensitivity Analysis")
        
        # Calculate correlations with ROI and break-even
        sensitivity_data = results_df.copy()
        
        # Calculate correlations where data is available
        roi_correlations = sensitivity_data.corr()['roi'].drop('roi').dropna()
        breakeven_correlations = sensitivity_data.corr()['break_even_months'].drop('break_even_months').dropna()
        
        # Create dataframe for display
        sensitivity_df = pd.DataFrame({
            'Parameter': roi_correlations.index,
            'Impact on ROI': roi_correlations.values,
            'Impact on Break-even': breakeven_correlations.loc[roi_correlations.index].values
        })
        
        # Format parameter names for display
        parameter_display_names = {
            'reduction_rate': 'Reduction Rate',
            'additional_cost_per_item': 'Additional Cost',
            'solution_cost': 'Solution Cost',
            'sales_30': 'Sales Volume',
            'returns_30': 'Returns Volume',
            'avg_sale_price': 'Average Price'
        }
        
        sensitivity_df['Parameter'] = sensitivity_df['Parameter'].map(
            lambda x: parameter_display_names.get(x, x)
        )
        
        # Sort by absolute impact on ROI
        sensitivity_df = sensitivity_df.iloc[np.abs(sensitivity_df['Impact on ROI']).argsort()[::-1]]
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        # Add bars for ROI impact
        fig.add_trace(go.Bar(
            y=sensitivity_df['Parameter'],
            x=sensitivity_df['Impact on ROI'],
            name='Impact on ROI',
            orientation='h',
            marker=dict(color=COLOR_SCHEME["positive"]),
            text=[f"{x:.2f}" for x in sensitivity_df['Impact on ROI']],
            textposition='auto'
        ))
        
        # Add bars for break-even impact (negative correlation is good for break-even)
        fig.add_trace(go.Bar(
            y=sensitivity_df['Parameter'],
            x=-sensitivity_df['Impact on Break-even'],  # Negate to match ROI direction
            name='Impact on Break-even',
            orientation='h',
            marker=dict(color=COLOR_SCHEME["tertiary"]),
            text=[f"{x:.2f}" for x in sensitivity_df['Impact on Break-even']],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Parameter Sensitivity Analysis",
            xaxis_title="Correlation Coefficient",
            barmode='group',
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("""
        **Interpretation Guide:**
        - **Positive Impact on ROI**: Higher values of this parameter increase ROI
        - **Negative Impact on ROI**: Higher values of this parameter decrease ROI
        - **Positive Impact on Break-even**: Higher values of this parameter reduce break-even time 
        - **Negative Impact on Break-even**: Higher values of this parameter increase break-even time
        """)
        
        # Raw simulation data in an expander
        with st.expander("View Simulation Raw Data"):
            st.dataframe(results_df)
            
            # Download option
            csv = results_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Simulation Data",
                csv,
                f"simulation_{scenario_uid}.csv",
                "text/csv",
                key='download-simulation-csv'
            )

def display_data_management():
    """Display data management interface for importing/exporting scenarios."""
    st.subheader("Data Management")
    
    tab1, tab2, tab3 = st.tabs(["Export Data", "Import Data", "Example Scenarios"])
    
    # Export Data tab
    with tab1:
        st.markdown("### Export Scenarios")
        st.info("Export your scenarios to a JSON file for backup or sharing.")
        
        if optimizer.scenarios.empty:
            st.warning("No scenarios to export. Add scenarios first.")
        else:
            scenarios_json = optimizer.download_json()
            st.download_button(
                "Download Scenarios JSON",
                scenarios_json,
                "kaizenalytics_scenarios.json",
                "application/json",
                key='download-json'
            )
    
    # Import Data tab
    with tab2:
        st.markdown("### Import Scenarios")
        st.info("Import scenarios from a previously exported JSON file.")
        
        uploaded_file = st.file_uploader("Choose a JSON file", type="json")
        
        if uploaded_file is not None:
            # Read file
            try:
                json_str = uploaded_file.getvalue().decode("utf-8")
                
                # Confirm import
                if st.button("Import Scenarios"):
                    success = optimizer.upload_json(json_str)
                    if success:
                        st.success("Scenarios imported successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to import scenarios. Please check the file format.")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    # Example Scenarios tab
    with tab3:
        st.markdown("### Example Scenarios")
        st.info("Add example scenarios to explore the platform's capabilities.")
        
        if st.button("Generate Example Scenarios"):
            count = optimizer.add_example_scenarios()
            st.success(f"Added {count} example scenarios!")
            st.rerun()

def display_help_and_resources():
    """Display help and resources page."""
    st.header("Help & Resources")
    
    tab1, tab2, tab3 = st.tabs(["Getting Started", "Formula Explanations", "Best Practices"])
    
    # Getting Started tab
    with tab1:
        st.markdown("### Welcome to Kaizenalytics")
        st.markdown("""
        This platform helps you analyze return reduction strategies and calculate their ROI. Here's how to get started:
        
        1. **Create Your First Scenario** - Use the "Add Scenario" option or the step-by-step Scenario Wizard to create your first return reduction strategy.
        
        2. **Compare Strategies** - View all your scenarios in the "Scenarios" tab to compare their effectiveness.
        
        3. **Run Simulations** - Use Monte Carlo simulations to assess risk and probability of success for your most promising strategies.
        
        4. **Export Your Work** - Once you've created scenarios, you can export them for sharing or backup.
        """)
        
        st.markdown("### Key Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Scenario Wizard**
            - Step-by-step guided scenario creation
            - Contextual recommendations
            - Visual impact preview
            
            **Financial Analysis**
            - Break-even calculation
            - ROI and net benefit analysis
            - Margin impact assessment
            """)
        
        with col2:
            st.markdown("""
            **Monte Carlo Simulation**
            - Risk assessment
            - Confidence intervals
            - Parameter sensitivity analysis
            
            **Visualization**
            - Return reduction impact charts
            - ROI and payback visualizations
            - Comparative scenario analysis
            """)
    
    # Formula Explanations tab
    with tab2:
        st.markdown("### Key Formulas & Calculations")
        
        formulas = {
            "Return Rate": {
                "Formula": "Returns ÷ Sales × 100",
                "Example": "50 returns ÷ 500 sales × 100 = 10% return rate",
                "Notes": "Measures the percentage of units returned relative to total sales."
            },
            "Avoided Returns": {
                "Formula": "Current Returns × Reduction Rate",
                "Example": "50 returns × 25% reduction = 12.5 avoided returns",
                "Notes": "Estimates how many fewer returns you'll have after implementing your solution."
            },
            "Return Processing Cost": {
                "Formula": "Returns × (Unit Cost × 0.25 + Fixed Processing Cost)",
                "Example": "50 returns × ($20 × 0.25 + $15) = $1,000",
                "Notes": "Includes inventory depreciation (25% of unit cost) plus fixed processing costs ($15)."
            },
            "Revenue Impact": {
                "Formula": "Returns × Lost Sale Percentage × Average Sale Price",
                "Example": "50 returns × 20% lost sales × $100 = $1,000",
                "Notes": "Estimates revenue loss assuming 20% of returns represent lost future sales."
            },
            "Monthly Net Benefit": {
                "Formula": "Monthly Savings - Monthly Additional Costs",
                "Example": "$500 savings - $200 additional costs = $300 net monthly benefit",
                "Notes": "The net monthly financial benefit from implementing the solution."
            },
            "Break-even Period": {
                "Formula": "Solution Cost ÷ Monthly Net Benefit",
                "Example": "$1,800 solution cost ÷ $300 monthly benefit = 6 months",
                "Notes": "The time required to recoup the initial investment."
            },
            "Return on Investment (ROI)": {
                "Formula": "(Annual Net Benefit ÷ Solution Cost) × 100",
                "Example": "($3,600 annual benefit ÷ $1,800 cost) × 100 = 200% ROI",
                "Notes": "Measures the percentage return on your investment over one year."
            }
        }
        
        for formula_name, details in formulas.items():
            with st.expander(formula_name):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Formula:**\n{details['Formula']}")
                    st.markdown(f"**Example:**\n{details['Example']}")
                
                with col2:
                    st.markdown(f"**Notes:**\n{details['Notes']}")
    
    # Best Practices tab
    with tab3:
        st.markdown("### Best Practices for Return Reduction Analysis")
        
        best_practices = [
            {
                "category": "Data Quality",
                "practices": [
                    "Use at least 30 days of sales and returns data for reliable analysis",
                    "Consider seasonality when extrapolating annual figures",
                    "Segment analysis by product category or return reason for more targeted solutions",
                    "Document your assumptions for future reference"
                ]
            },
            {
                "category": "Solution Design",
                "practices": [
                    "Focus on the highest return rate categories first",
                    "Consider customer experience impact alongside financial metrics",
                    "Plan for phased implementation to validate assumptions",
                    "Set clear success metrics and measurement processes"
                ]
            },
            {
                "category": "ROI Estimation",
                "practices": [
                    "Be conservative with reduction rate estimates (15-30% is typical)",
                    "Include all implementation costs, not just direct expenses",
                    "Account for ongoing maintenance costs in your calculations",
                    "Use sensitivity analysis to identify critical success factors"
                ]
            },
            {
                "category": "Implementation",
                "practices": [
                    "Establish baseline metrics before implementing changes",
                    "Test solutions on a subset of products when possible",
                    "Monitor both return rates and sales conversion to capture full impact",
                    "Regularly review and adjust your strategies based on results"
                ]
            }
        ]
        
        for practice in best_practices:
            st.markdown(f"#### {practice['category']}")
            for item in practice['practices']:
                st.markdown(f"- {item}")
            st.markdown("---")
        
        st.markdown("### Common Return Reasons & Solutions")
        
        return_solutions = pd.DataFrame({
            "Return Reason": [
                "Sizing/Fit Issues", 
                "Product Damaged in Transit",
                "Product Not as Described",
                "Product Quality Issues",
                "Wrong Item Shipped",
                "Buyer's Remorse"
            ],
            "Typical Rate": [
                "30-40%", 
                "15-25%",
                "15-20%",
                "10-15%",
                "5-10%",
                "10-20%"
            ],
            "Effective Solutions": [
                "Size guides, fit visualization tools, consistent sizing standards",
                "Improved packaging, package testing, handling instructions",
                "Enhanced product images, detailed specifications, video demonstrations",
                "Quality control processes, material upgrades, design improvements",
                "Order verification systems, barcode scanning, staff training",
                "Post-purchase reassurance, usage guides, loyalty incentives"
            ]
        })
        
        st.table(return_solutions)

def create_comparative_analysis():
    """Create comparative analysis dashboard for scenarios."""
    if optimizer.scenarios.empty:
        st.info("Add at least two scenarios to enable comparative analysis.")
        return
    
    st.subheader("Comparative Analysis")
    
    # Scenario selection
    scenarios_list = optimizer.scenarios['scenario_name'].tolist()
    
    if len(scenarios_list) < 2:
        st.warning("Add at least two scenarios to enable comparison.")
        return
    
    # Select scenarios to compare
    selected_scenarios = st.multiselect(
        "Select Scenarios to Compare",
        scenarios_list,
        default=scenarios_list[:min(4, len(scenarios_list))]
    )
    
    if len(selected_scenarios) < 2:
        st.warning("Select at least two scenarios to compare.")
        return
    
    # Get data for selected scenarios
    comparison_data = optimizer.scenarios[optimizer.scenarios['scenario_name'].isin(selected_scenarios)].copy()
    
    # Create metrics for quick comparison
    st.markdown("### Key Metrics Comparison")
    
    # ROI comparison
    fig = px.bar(
        comparison_data,
        x='scenario_name',
        y='roi',
        color='roi',
        color_continuous_scale=px.colors.sequential.Blues,
        labels={'scenario_name': 'Scenario', 'roi': 'Return on Investment (%)'},
        title='ROI Comparison'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Break-even comparison
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            comparison_data,
            x='scenario_name',
            y='break_even_months',
            color='break_even_months',
            color_continuous_scale=px.colors.sequential.Blues_r,  # Reversed scale
            labels={'scenario_name': 'Scenario', 'break_even_months': 'Break-even (Months)'},
            title='Break-even Period Comparison'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            comparison_data,
            x='scenario_name',
            y='net_benefit',
            color='net_benefit',
            color_continuous_scale=px.colors.sequential.Blues,
            labels={'scenario_name': 'Scenario', 'net_benefit': 'Annual Net Benefit ($)'},
            title='Net Benefit Comparison'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Investment vs. Return visualization
    st.markdown("### Investment vs. Return Analysis")
    
    fig = px.scatter(
        comparison_data,
        x='solution_cost',
        y='annual_savings',
        size='roi',
        color='break_even_months',
        hover_name='scenario_name',
        color_continuous_scale=px.colors.sequential.Blues_r,  # Reversed scale
        labels={
            'solution_cost': 'Initial Investment ($)',
            'annual_savings': 'Annual Savings ($)',
            'roi': 'ROI (%)',
            'break_even_months': 'Break-even (Months)'
        },
        title='Investment vs. Return Analysis'
    )
    
    # Add reference line for break-even
    max_value = max(comparison_data['solution_cost'].max(), comparison_data['annual_savings'].max())
    fig.add_trace(go.Scatter(
        x=[0, max_value],
        y=[0, max_value],
        mode='lines',
        line=dict(color='red', dash='dash'),
        name='1-Year Break-even Line'
    ))
    
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("""
    **Chart Interpretation:**
    - **Bubble Size**: Larger bubbles indicate higher ROI
    - **Color**: Darker color indicates shorter break-even period
    - **Above Red Line**: Scenarios that return more than the investment within a year
    - **Below Red Line**: Scenarios that take longer than a year to break even
    """)
    
    # Detailed comparison table
    st.markdown("### Detailed Comparison")
    
    # Select columns for comparison
    comparison_metrics = [
        'scenario_name', 'tag', 'sales_30', 'returns_30', 'return_rate',
        'reduction_rate', 'solution_cost', 'additional_cost_per_item',
        'savings_30', 'annual_savings', 'break_even_months', 'roi',
        'net_benefit', 'score'
    ]
    
    comparison_df = comparison_data[comparison_metrics].copy()
    
    # Format columns for display
    format_columns = {
        'return_rate': format_percent,
        'reduction_rate': format_percent,
        'solution_cost': format_currency,
        'additional_cost_per_item': format_currency,
        'savings_30': format_currency,
        'annual_savings': format_currency,
        'roi': format_percent,
        'net_benefit': format_currency
    }
    
    for col, formatter in format_columns.items():
        comparison_df[col] = comparison_df[col].apply(formatter)
    
    # Apply special formatting for break-even
    comparison_df['break_even_months'] = comparison_df['break_even_months'].apply(
        lambda x: f"{float(x):.1f}" if x != 'inf' else "N/A"
    )
    
    # Format score as integer with /100
    comparison_df['score'] = comparison_df['score'].apply(
        lambda x: f"{float(x):.0f}/100" if not pd.isna(x) else "N/A"
    )
    
    # Rename columns for display
    column_names = {
        'scenario_name': 'Scenario',
        'tag': 'Category',
        'sales_30': 'Monthly Sales',
        'returns_30': 'Monthly Returns',
        'return_rate': 'Return Rate',
        'reduction_rate': 'Reduction Target',
        'solution_cost': 'Solution Cost',
        'additional_cost_per_item': 'Add\'l Cost/Item',
        'savings_30': 'Monthly Savings',
        'annual_savings': 'Annual Savings',
        'break_even_months': 'Break-even',
        'roi': 'ROI',
        'net_benefit': 'Net Benefit',
        'score': 'Score'
    }
    
    comparison_df = comparison_df.rename(columns=column_names)
    
    # Display table
    st.dataframe(comparison_df, use_container_width=True)
    
    # Portfolio efficiency frontier
    st.markdown("### Portfolio Efficiency Analysis")
    
    # Create efficiency frontier visualization
    fig = px.scatter(
        comparison_data,
        x='break_even_months',
        y='roi',
        color='score',
        size='solution_cost',
        hover_name='scenario_name',
        color_continuous_scale=px.colors.sequential.Blues,
        labels={
            'break_even_months': 'Break-even Period (Months)',
            'roi': 'Return on Investment (%)',
            'score': 'Overall Score',
            'solution_cost': 'Investment ($)'
        },
        title='ROI vs. Break-even Analysis'
    )
    
    # Customize layout
    fig.update_layout(
        height=500,
        xaxis=dict(rangemode='tozero'),
        yaxis=dict(rangemode='tozero')
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("""
    **Portfolio Efficiency Interpretation:**
    - **Ideal Position**: Top-left (high ROI, quick break-even)
    - **Bubble Size**: Larger bubbles represent larger investments
    - **Color**: Darker colors indicate higher overall scores
    """)

def display_sidebar():
    """Display sidebar with navigation and settings."""
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px">
            <h1 style="font-size: 28px; margin: 0; color: {COLOR_SCHEME["text_light"]};">Kaizenalytics</h1>
            <p style="margin: 0; font-weight: 400; color: {COLOR_SCHEME["text_light"]};">Return Analytics Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### Navigation")
        
        nav_options = {
            "Dashboard": "View metrics and overview",
            "Add Scenario": "Create a new scenario",
            "Scenario Wizard": "Step-by-step scenario creation",
            "Scenarios": "View and compare all scenarios",
            "Comparative Analysis": "Compare multiple scenarios",
            "Data Management": "Import and export data",
            "Help & Resources": "Learn how to use the platform"
        }
        
        for nav, desc in nav_options.items():
            if st.sidebar.button(nav, key=f"nav_{nav}", help=desc):
                st.session_state.page = nav
                
                # Reset wizard if navigating away
                if nav != "Scenario Wizard":
                    st.session_state.wizard_step = 1
                    st.session_state.wizard_data = {}
                
                # Reset scenario view if navigating away
                if nav != "Scenarios":
                    st.session_state.view_scenario = None
                    st.session_state.simulate_scenario = None
                
                st.rerun()
        
        st.markdown("---")
        
        # Application settings
        st.markdown("### Settings")
        
        # Mode toggle
        app_mode = st.radio("Application Mode", ["Basic", "Advanced"], 
                        index=0 if st.session_state.app_mode == "Basic" else 1,
                        help="Advanced mode shows more detailed metrics and options")
        
        if app_mode != st.session_state.app_mode:
            st.session_state.app_mode = app_mode
            st.rerun()
        
        # Color scheme selector
        scheme_options = list(COLOR_SCHEMES.keys())
        selected_scheme = st.selectbox("Color Theme", 
                                   scheme_options,
                                   index=scheme_options.index(st.session_state.color_scheme),
                                   help="Change the application color theme")
        
        if selected_scheme != st.session_state.color_scheme:
            update_color_scheme(selected_scheme)
            st.rerun()
        
        st.markdown("---")
        
        # App info
        st.markdown("### About")
        st.markdown(f"""
        <div style="color: {COLOR_SCHEME["text_light"]}; font-size: 0.9rem">
            <p>Version 1.0.0</p>
            <p>© 2023 Kaizenalytics</p>
            <p>A comprehensive ROI toolkit for e-commerce return reduction strategies.</p>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main application entry point."""
    # Initialize page if not set
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    
    # Initialize view scenario state
    if 'view_scenario' not in st.session_state:
        st.session_state.view_scenario = None
    
    # Initialize simulate scenario state
    if 'simulate_scenario' not in st.session_state:
        st.session_state.simulate_scenario = None
    
    # Load custom CSS
    load_custom_css()
    
    # Display sidebar
    display_sidebar()
    
    # Display header
    display_header()
    
    # Handle page routing
    if st.session_state.view_scenario:
        # Show scenario details
        display_scenario_details(st.session_state.view_scenario)
    
    elif st.session_state.simulate_scenario:
        # Show Monte Carlo simulation
        display_monte_carlo_simulation(st.session_state.simulate_scenario)
    
    else:
        # Regular page navigation
        if st.session_state.page == "Dashboard":
            display_metrics_overview(optimizer.scenarios)
            
            if not optimizer.scenarios.empty:
                create_comparative_analysis()
            
        elif st.session_state.page == "Add Scenario":
            create_scenario_form()
            
        elif st.session_state.page == "Scenario Wizard":
            create_scenario_wizard()
            
        elif st.session_state.page == "Scenarios":
            display_scenarios_table(optimizer.scenarios)
            
        elif st.session_state.page == "Comparative Analysis":
            create_comparative_analysis()
            
        elif st.session_state.page == "Data Management":
            display_data_management()
            
        elif st.session_state.page == "Help & Resources":
            display_help_and_resources()

if __name__ == "__main__":
    main()
