"""
ViveROI Analytics - PPC & Marketing ROI Analytics Platform
A comprehensive tool for Vive Health's e-commerce team to analyze and optimize marketing spend, 
evaluate channel performance, forecast ROI, and model different ad spend scenarios.

Features:
- Campaign performance tracking across Amazon, website, and other channels
- Marketing ROI calculations and forecasting
- Profit margin analysis with PPC cost impact
- Scenario modeling for ad spend, conversion rates, and other key metrics
- AI-powered campaign insights and recommendations
"""

import streamlit as st
import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import json
import os
import time
import warnings
import re
import logging
import requests
import traceback
from typing import Dict, List, Tuple, Optional, Union, Any

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("viveroi_analytics")

# Suppress warnings
warnings.filterwarnings('ignore')

# Fallback for rerun depending on Streamlit version
if not hasattr(st, "rerun") and hasattr(st, "experimental_rerun"):
    st.rerun = st.experimental_rerun  # compatibility shim

# App configuration
st.set_page_config(
    page_title="ViveROI | PPC & Marketing Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# Constants and Configuration
# =============================================================================

# Check if the app is in basic or advanced mode
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = "Basic"

# Default channels
DEFAULT_CHANNELS = ["Amazon", "Vive Website", "Walmart", "eBay", "Paid Social"]

# Default product categories
DEFAULT_CATEGORIES = ["Mobility", "Pain Relief", "Bathroom Safety", "Bedroom", "Daily Living Aids"]

# Define color schemes
COLOR_SCHEMES = {
    "default": {
        "primary": "#0366d6",
        "secondary": "#28a745",
        "tertiary": "#ffc107",
        "background": "#f8f9fa",
        "positive": "#28a745",
        "negative": "#dc3545",
        "warning": "#ffc107",
        "neutral": "#6c757d",
        "text_dark": "#212529",
        "text_light": "#f8f9fa",
        "card_bg": "#ffffff",
        "sidebar_bg": "#212529",
        "hover": "#e9ecef"
    },
    "vive": {
        "primary": "#00a3e0",
        "secondary": "#6cc24a",
        "tertiary": "#f7941d",
        "background": "#f5f8ff",
        "positive": "#6cc24a",
        "negative": "#d9534f",
        "warning": "#f7941d",
        "neutral": "#5bc0de",
        "text_dark": "#333333",
        "text_light": "#ffffff",
        "card_bg": "#ffffff",
        "sidebar_bg": "#003b5c",
        "hover": "#e1f0fa"
    },
    "amazon": {
        "primary": "#ff9900",
        "secondary": "#146eb4",
        "tertiary": "#232f3e",
        "background": "#f9f9f9",
        "positive": "#2e8b57",
        "negative": "#c41e3a",
        "warning": "#ff9900",
        "neutral": "#146eb4",
        "text_dark": "#232f3e",
        "text_light": "#ffffff",
        "card_bg": "#ffffff",
        "sidebar_bg": "#232f3e",
        "hover": "#fef8ec"
    },
    "dark": {
        "primary": "#0d6efd",
        "secondary": "#20c997",
        "tertiary": "#fd7e14",
        "background": "#212529",
        "positive": "#20c997",
        "negative": "#dc3545",
        "warning": "#ffc107",
        "neutral": "#6c757d",
        "text_dark": "#f8f9fa",
        "text_light": "#f8f9fa",
        "card_bg": "#2b3035",
        "sidebar_bg": "#1a1d20",
        "hover": "#343a40"
    }
}

# Set default color scheme
if 'color_scheme' not in st.session_state:
    st.session_state.color_scheme = "vive"

# Get current color scheme
COLOR_SCHEME = COLOR_SCHEMES[st.session_state.color_scheme]

# Example marketing campaigns for demonstration
EXAMPLE_CAMPAIGNS = [
    {
        "campaign_name": "Amazon PPC - Mobility Scooters",
        "product_name": "Vive Mobility Scooter",
        "channel": "Amazon",
        "category": "Mobility",
        "ad_spend": 5000,
        "clicks": 4200,
        "impressions": 102000,
        "conversions": 126,
        "revenue": 31500,
        "start_date": "2023-04-01",
        "end_date": "2023-04-30",
        "avg_cpc": 1.19,
        "ctr": 4.12,
        "conversion_rate": 3.00,
        "acos": 15.87,
        "roas": 6.30,
        "product_cost": 125,
        "selling_price": 250,
        "shipping_cost": 0,
        "amazon_fees": 37.50,
        "target_acos": 18,
        "notes": "Auto-targeting campaign for mobility scooters"
    },
    {
        "campaign_name": "Website PPC - Walkers",
        "product_name": "Vive Folding Walker",
        "channel": "Vive Website",
        "category": "Mobility",
        "ad_spend": 3200,
        "clicks": 2800,
        "impressions": 45000,
        "conversions": 98,
        "revenue": 12740,
        "start_date": "2023-04-01",
        "end_date": "2023-04-30",
        "avg_cpc": 1.14,
        "ctr": 6.22,
        "conversion_rate": 3.50,
        "acos": 25.12,
        "roas": 3.98,
        "product_cost": 48,
        "selling_price": 130,
        "shipping_cost": 8.50,
        "amazon_fees": 0,
        "target_acos": 25,
        "notes": "Google Ads campaign for folding walkers targeting mobility keywords"
    },
    {
        "campaign_name": "Amazon PPC - TENS Units",
        "product_name": "Vive TENS Unit",
        "channel": "Amazon",
        "category": "Pain Relief",
        "ad_spend": 2800,
        "clicks": 3500,
        "impressions": 78000,
        "conversions": 175,
        "revenue": 13125,
        "start_date": "2023-04-01",
        "end_date": "2023-04-30",
        "avg_cpc": 0.80,
        "ctr": 4.49,
        "conversion_rate": 5.00,
        "acos": 21.33,
        "roas": 4.69,
        "product_cost": 28,
        "selling_price": 75,
        "shipping_cost": 0,
        "amazon_fees": 11.25,
        "target_acos": 20,
        "notes": "Keyword-targeted campaign for TENS units"
    },
    {
        "campaign_name": "Walmart - Bathroom Safety",
        "product_name": "Vive Shower Chair",
        "channel": "Walmart",
        "category": "Bathroom Safety",
        "ad_spend": 1500,
        "clicks": 1200,
        "impressions": 28000,
        "conversions": 45,
        "revenue": 5850,
        "start_date": "2023-04-01",
        "end_date": "2023-04-30",
        "avg_cpc": 1.25,
        "ctr": 4.29,
        "conversion_rate": 3.75,
        "acos": 25.64,
        "roas": 3.90,
        "product_cost": 52,
        "selling_price": 130,
        "shipping_cost": 0,
        "amazon_fees": 0,
        "target_acos": 30,
        "notes": "Walmart Sponsored Products campaign for shower chairs"
    },
    {
        "campaign_name": "Meta Ads - Health Products",
        "product_name": "Vive Health Bundle",
        "channel": "Paid Social",
        "category": "Daily Living Aids",
        "ad_spend": 4000,
        "clicks": 5600,
        "impressions": 210000,
        "conversions": 112,
        "revenue": 16800,
        "start_date": "2023-04-01",
        "end_date": "2023-04-30",
        "avg_cpc": 0.71,
        "ctr": 2.67,
        "conversion_rate": 2.00,
        "acos": 23.81,
        "roas": 4.20,
        "product_cost": 65,
        "selling_price": 150,
        "shipping_cost": 9.95,
        "amazon_fees": 0,
        "target_acos": 25,
        "notes": "Facebook and Instagram ads targeting health-conscious audience"
    }
]

# Columns for the campaigns DataFrame
CAMPAIGN_COLUMNS = [
    'uid', 'campaign_name', 'product_name', 'channel', 'category', 'ad_spend',
    'clicks', 'impressions', 'conversions', 'revenue', 'start_date', 'end_date',
    'avg_cpc', 'ctr', 'conversion_rate', 'acos', 'roas', 'product_cost',
    'selling_price', 'shipping_cost', 'amazon_fees', 'profit', 'profit_margin',
    'target_acos', 'performance_score', 'timestamp', 'notes'
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
        .stTextArea>div>div>textarea,
        .stDateInput>div>div>input {{
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            padding: 0.75rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        
        .stTextInput>div>div>input:focus, 
        .stNumberInput>div>div>input:focus, 
        .stSelectbox>div>div>div:focus,
        .stTextArea>div>div>textarea:focus,
        .stDateInput>div>div>input:focus {{
            border-color: {COLOR_SCHEME["secondary"]};
            box-shadow: 0 0 0 3px rgba(44, 167, 70, 0.2);
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
            background-color: {COLOR_SCHEME["card_bg"]};
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
            background-color: rgba(255, 193, 7, 0.1);
            border-left: 5px solid {COLOR_SCHEME["warning"]};
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
        }}
        
        .success-box {{
            background-color: rgba(40, 167, 69, 0.1);
            border-left: 5px solid {COLOR_SCHEME["positive"]};
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
        }}
        
        .danger-box {{
            background-color: rgba(220, 53, 69, 0.1);
            border-left: 5px solid {COLOR_SCHEME["negative"]};
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
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
            background-color: {COLOR_SCHEME["card_bg"]};
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
        
        /* KPI/Metrics row */
        .metrics-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 24px;
        }}
        
        .metric-box {{
            flex: 1;
            min-width: 200px;
            padding: 16px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }}
        
        .metric-box .title {{
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }}
        
        .metric-box .value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        
        .metric-box .change {{
            font-size: 12px;
            margin-top: 8px;
        }}
        
        .metric-box .positive {{
            color: {COLOR_SCHEME["positive"]};
        }}
        
        .metric-box .negative {{
            color: {COLOR_SCHEME["negative"]};
        }}
        
        /* Amazon specific styling */
        .amazon-orange {{
            color: #ff9900;
        }}
        
        .amazon-blue {{
            color: #146eb4;
        }}
        
        /* Campaign card */
        .campaign-card {{
            padding: 16px;
            border-radius: 8px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 16px;
            border-left: 4px solid {COLOR_SCHEME["primary"]};
        }}
        
        .campaign-card.amazon {{
            border-left-color: #ff9900;
        }}
        
        .campaign-card.vive {{
            border-left-color: #00a3e0;
        }}
        
        .campaign-card.walmart {{
            border-left-color: #0071ce;
        }}
        
        .campaign-card.ebay {{
            border-left-color: #e53238;
        }}
        
        .campaign-card.social {{
            border-left-color: #4267B2;
        }}
        
        .campaign-card .header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        
        .campaign-card .title {{
            font-weight: bold;
            font-size: 16px;
        }}
        
        .campaign-card .channel {{
            font-size: 14px;
            color: #666;
        }}
        
        .campaign-card .metrics {{
            display: flex;
            justify-content: space-between;
            margin-top: 16px;
        }}
        
        .campaign-card .metric {{
            text-align: center;
        }}
        
        .campaign-card .metric-label {{
            font-size: 12px;
            color: #666;
        }}
        
        .campaign-card .metric-value {{
            font-weight: bold;
            font-size: 18px;
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

def format_number(value: Optional[float], decimals: int = 2) -> str:
    """Format a value as number with commas."""
    if pd.isna(value) or value is None:
        return "-"
    if decimals == 0:
        return f"{int(value):,}"
    return f"{value:,.{decimals}f}"

def format_large_number(value: Optional[float]) -> str:
    """Format large numbers with K, M, B suffixes."""
    if pd.isna(value) or value is None:
        return "-"
    
    if value < 1000:
        return f"{value:.0f}"
    elif value < 1000000:
        return f"{value/1000:.1f}K"
    elif value < 1000000000:
        return f"{value/1000000:.1f}M"
    else:
        return f"{value/1000000000:.1f}B"

def calculate_performance_score(roas: float, acos: float, conversion_rate: float, 
                              target_acos: float, profit_margin: float) -> Optional[float]:
    """Calculate a weighted performance score for a campaign."""
    if pd.isna(roas) or pd.isna(acos) or pd.isna(conversion_rate) or pd.isna(target_acos) or pd.isna(profit_margin):
        return None
    
    # ROAS score (higher is better)
    roas_score = min(1, roas / 8)  # Cap at 8x ROAS
    
    # ACoS score (lower is better)
    acos_ratio = target_acos / acos if acos > 0 else 2  # If ACoS is better than target, score higher
    acos_score = min(1, acos_ratio)
    
    # Conversion rate score
    conv_score = min(1, conversion_rate / 5)  # Cap at 5% conversion rate
    
    # Profit margin score
    margin_score = min(1, profit_margin / 40)  # Cap at 40% profit margin
    
    # Weighted scoring
    weighted_score = (roas_score * 0.35) + (acos_score * 0.3) + (conv_score * 0.15) + (margin_score * 0.2)
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

def get_channel_color(channel: str) -> str:
    """Get a color for a specific channel."""
    channel_colors = {
        "Amazon": "#ff9900",
        "Vive Website": "#00a3e0",
        "Walmart": "#0071ce",
        "eBay": "#e53238",
        "Paid Social": "#4267B2",
        "Meta Ads": "#4267B2",
        "Google Ads": "#4285F4",
        "Microsoft Ads": "#00a4ef"
    }
    
    return channel_colors.get(channel, COLOR_SCHEME["primary"])

def get_profit_metrics(unit_cost: float, selling_price: float, shipping_cost: float = 0, 
                     amazon_fees: float = 0, ad_cost_per_sale: float = 0) -> Dict[str, float]:
    """Calculate profit metrics for a product."""
    total_cost = unit_cost + shipping_cost + amazon_fees + ad_cost_per_sale
    profit = selling_price - total_cost
    profit_margin = safe_divide(profit * 100, selling_price)
    
    return {
        "total_cost": total_cost,
        "profit": profit,
        "profit_margin": profit_margin
    }

# --- AI ASSISTANT FUNCTIONS ---
def check_openai_api_key():
    """Check if OpenAI API key is available and valid."""
    api_key = st.secrets.get("openai_api_key", None)
    
    if not api_key:
        st.session_state.api_key_status = "missing"
        logger.warning("OpenAI API key not found in secrets")
        return False
    
    # Verify the API key is valid with a simple test request
    try:
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        payload = {
            "model": "gpt-4o", 
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 5
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", 
            headers=headers, 
            json=payload, 
            timeout=5
        )
        
        if response.status_code == 200:
            st.session_state.api_key_status = "valid"
            logger.info("OpenAI API key is valid")
            return True
        else:
            st.session_state.api_key_status = "invalid"
            logger.error(f"OpenAI API key is invalid: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.session_state.api_key_status = "error"
        logger.exception("Error checking OpenAI API key")
        return False

def call_openai_api(messages, model="gpt-4o", temperature=0.7, max_tokens=1024):
    """Call the OpenAI API with the given messages."""
    api_key = st.secrets.get("openai_api_key", None)
    
    # If API key is missing, generate a simulated response
    if not api_key:
        logger.warning("OpenAI API key not found in secrets, using simulated response")
        return generate_simulated_response(messages)
    
    # If API key is available, make the actual API call
    try:
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", 
            headers=headers, 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return f"Error: The AI assistant encountered a problem (HTTP {response.status_code}). Please try again later or contact support if the issue persists."
    except requests.exceptions.Timeout:
        logger.error("OpenAI API timeout")
        return "Error: The AI assistant timed out. Please try again later when the service is less busy."
    except requests.exceptions.ConnectionError:
        logger.error("OpenAI API connection error")
        return "Error: Could not connect to the AI service. Please check your internet connection and try again."
    except Exception as e:
        logger.exception("Error calling OpenAI API")
        return f"Error: The AI assistant encountered an unexpected problem. Please try again later or contact support if the issue persists."

def generate_simulated_response(messages):
    """Generate a simulated response for demonstration when API key is missing."""
    # Simulate API thinking time
    time.sleep(2)
    
    # Extract the latest user message
    user_message = "Unknown query"
    for msg in reversed(messages):
        if msg["role"] == "user":
            user_message = msg["content"]
            break
    
    # Generate a simulated response based on keywords in the user message
    if "roi" in user_message.lower() or "return on investment" in user_message.lower():
        return """Based on the campaign data, I recommend optimizing your ad spend on Amazon PPC for mobility products which currently show the highest ROAS at 6.3x. Consider:

1. Increasing budget allocation by 15-20% for top-performing Amazon campaigns
2. Reviewing keyword performance for TENS units to identify high-converting search terms
3. Testing higher bids on top-performing keywords to maintain position and visibility

The data indicates Amazon campaigns are outperforming website PPC by approximately 25% in terms of ROAS."""
        
    elif "acos" in user_message.lower():
        return """Your ACoS performance varies significantly across channels:

- Amazon PPC campaigns are averaging 15-21% ACoS, which is better than your target
- Website PPC campaigns are showing higher ACoS (25.12%), slightly above target
- Consider optimizing the Website Walker campaign by:
  * Improving landing page conversion elements
  * Testing more specific keyword targeting
  * Implementing negative keywords to reduce wasted spend
  
A 10% reduction in ACoS for the Website campaign could increase your profit margin by approximately 7.5%."""
        
    elif "budget" in user_message.lower() or "spend" in user_message.lower():
        return """For optimal budget allocation across your current campaigns:

1. Increase Amazon PPC budget for mobility scooters by 20% (potential ROAS increase to 6.8x)
2. Maintain current budget for TENS units but optimize keyword targeting
3. Reduce Walmart campaign spend by 15% and reallocate to better performing channels
4. Test incremental budget increases of 10% for Meta Ads with improved audience targeting

Based on current performance, each additional $1,000 in Amazon PPC could generate approximately $6,300 in revenue with a profit contribution of $1,890."""

    elif "conversion" in user_message.lower():
        return """Conversion rate analysis by channel:

- Amazon TENS Unit campaign shows highest conversion at 5.00%
- Website conversion rates are solid at 3.50%
- Meta Ads show lowest conversion at 2.00%

Recommendations to improve conversion:
1. For Amazon: Enhance product imagery and A+ content to maintain strong performance
2. For Website: Optimize checkout process and implement exit-intent offers
3. For Meta Ads: Refine audience targeting and implement retargeting campaigns for abandoned carts

A 0.5% improvement in Meta Ads conversion rate could increase revenue by approximately $7,500 monthly."""

    else:
        return """Based on your campaign performance data, I've identified several optimization opportunities:

1. Amazon PPC campaigns are your strongest performers with ROAS of 4.69-6.30x
2. Your Paid Social campaigns have good reach but the lowest conversion rates (2.00%)
3. Bathroom Safety products on Walmart show potential but need optimization

Recommended actions:
- Shift 15% of budget from lower-performing channels to Amazon PPC
- Improve product listings for Walmart to boost conversion rates
- Test new ad creatives for Meta campaigns focused on clear value propositions
- Implement more specific audience targeting for Paid Social

These adjustments could improve overall marketing ROI by approximately 18-22% based on current performance metrics."""

def get_ai_campaign_insights(campaign_data: pd.DataFrame, specific_campaign: Optional[str] = None):
    """
    Get AI-powered insights for marketing campaigns.
    
    Args:
        campaign_data: DataFrame with campaign data
        specific_campaign: Optional name of specific campaign to analyze
    """
    if campaign_data.empty:
        return "No campaign data available for analysis. Please add campaigns first."
    
    # Create system prompt with context
    system_prompt = "You are an expert marketing analyst for Vive Health, specializing in e-commerce PPC campaigns and marketing ROI analysis."
    
    # Add summary of all campaigns
    system_prompt += "\n\n## Campaign Performance Summary:\n"
    
    # Overall metrics
    total_spend = campaign_data['ad_spend'].sum()
    total_revenue = campaign_data['revenue'].sum()
    total_roas = safe_divide(total_revenue, total_spend)
    avg_acos = safe_divide(campaign_data['ad_spend'].sum() * 100, campaign_data['revenue'].sum())
    
    system_prompt += f"Total Ad Spend: ${total_spend:,.2f}\n"
    system_prompt += f"Total Revenue: ${total_revenue:,.2f}\n"
    system_prompt += f"Overall ROAS: {total_roas:.2f}x\n"
    system_prompt += f"Overall ACoS: {avg_acos:.2f}%\n\n"
    
    # Channel performance
    system_prompt += "## Channel Performance:\n"
    channel_perf = campaign_data.groupby('channel').agg({
        'ad_spend': 'sum',
        'revenue': 'sum',
        'conversions': 'sum',
        'clicks': 'sum'
    }).reset_index()
    
    for _, row in channel_perf.iterrows():
        channel_roas = safe_divide(row['revenue'], row['ad_spend'])
        channel_acos = safe_divide(row['ad_spend'] * 100, row['revenue'])
        channel_conv_rate = safe_divide(row['conversions'] * 100, row['clicks'])
        
        system_prompt += f"{row['channel']}:\n"
        system_prompt += f"  - Spend: ${row['ad_spend']:,.2f}\n"
        system_prompt += f"  - Revenue: ${row['revenue']:,.2f}\n"
        system_prompt += f"  - ROAS: {channel_roas:.2f}x\n"
        system_prompt += f"  - ACoS: {channel_acos:.2f}%\n"
        system_prompt += f"  - Conversion Rate: {channel_conv_rate:.2f}%\n\n"
    
    # If specific campaign is requested, add detailed info
    if specific_campaign and specific_campaign in campaign_data['campaign_name'].values:
        campaign = campaign_data[campaign_data['campaign_name'] == specific_campaign].iloc[0]
        
        system_prompt += f"## Specific Campaign Analysis: {specific_campaign}\n"
        system_prompt += f"Channel: {campaign['channel']}\n"
        system_prompt += f"Category: {campaign['category']}\n"
        system_prompt += f"Product: {campaign['product_name']}\n"
        system_prompt += f"Ad Spend: ${campaign['ad_spend']:,.2f}\n"
        system_prompt += f"Revenue: ${campaign['revenue']:,.2f}\n"
        system_prompt += f"ROAS: {campaign['roas']:.2f}x\n"
        system_prompt += f"ACoS: {campaign['acos']:.2f}%\n"
        system_prompt += f"Target ACoS: {campaign['target_acos']:.2f}%\n"
        system_prompt += f"Conversion Rate: {campaign['conversion_rate']:.2f}%\n"
        system_prompt += f"CTR: {campaign['ctr']:.2f}%\n"
        system_prompt += f"Product Cost: ${campaign['product_cost']:.2f}\n"
        system_prompt += f"Selling Price: ${campaign['selling_price']:.2f}\n"
        system_prompt += f"Profit Margin: {campaign['profit_margin']:.2f}%\n"
        system_prompt += f"Notes: {campaign['notes']}\n"
        
        # Compare to average for channel
        channel_avg = campaign_data[campaign_data['channel'] == campaign['channel']].mean()
        
        system_prompt += f"\nComparison to {campaign['channel']} Average:\n"
        system_prompt += f"ROAS: {campaign['roas']:.2f}x vs. {channel_avg['roas']:.2f}x average\n"
        system_prompt += f"ACoS: {campaign['acos']:.2f}% vs. {channel_avg['acos']:.2f}% average\n"
        system_prompt += f"Conversion Rate: {campaign['conversion_rate']:.2f}% vs. {channel_avg['conversion_rate']:.2f}% average\n"
        
        user_prompt = f"Please analyze this {campaign['channel']} campaign for {campaign['product_name']} and provide specific recommendations to improve its performance. Focus on optimizing ROAS, ACoS, and profit margin. What specific actions should we take? Include expected impact of your recommendations in percentages or dollar terms when possible."
    else:
        user_prompt = "Please analyze our overall marketing campaign performance across channels. What are the top 3-5 recommendations to optimize our marketing spend and improve ROI? Provide specific, actionable insights based on the data. Include expected impact of recommendations in percentages or dollar terms when possible."
    
    # Create messages array for API call
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    # Call the API
    try:
        response = call_openai_api(messages)
        return response
    except Exception as e:
        logger.exception("Error getting AI insights")
        return f"Error generating insights: {str(e)}\n\nPlease try again later or check your API key configuration."

# =============================================================================
# Data Management Class
# =============================================================================

class MarketingAnalyzer:
    """Class to manage marketing campaigns and perform analytics."""
    
    def __init__(self) -> None:
        """Initialize the MarketingAnalyzer."""
        self.load_data()
        self.default_examples = EXAMPLE_CAMPAIGNS
    
    def load_data(self) -> None:
        """Load data from session state or initialize empty dataframe."""
        if 'campaigns' not in st.session_state:
            self.campaigns = pd.DataFrame(columns=CAMPAIGN_COLUMNS)
            st.session_state['campaigns'] = self.campaigns
        else:
            self.campaigns = st.session_state['campaigns']
    
    def save_data(self) -> None:
        """Save data to session state."""
        st.session_state['campaigns'] = self.campaigns
    
    def download_json(self) -> str:
        """Get campaign data as JSON string."""
        return self.campaigns.to_json(orient='records', date_format='iso')
    
    def upload_json(self, json_str: str) -> bool:
        """Load campaigns from JSON string."""
        try:
            data = pd.read_json(json_str, orient='records')
            if not data.empty:
                # Ensure all required columns exist
                for col in CAMPAIGN_COLUMNS:
                    if col not in data.columns:
                        data[col] = None
                
                # Remove any extra columns
                data = data[CAMPAIGN_COLUMNS]
                
                self.campaigns = data
                self.save_data()
                return True
            return False
        except Exception:
            st.error(f"Error loading data: {traceback.format_exc()}")
            return False
    
    def add_campaign(self,
                  campaign_name: str,
                  product_name: str,
                  channel: str,
                  category: str,
                  ad_spend: float,
                  clicks: float,
                  impressions: float,
                  conversions: float,
                  revenue: float,
                  start_date: str,
                  end_date: str,
                  product_cost: float,
                  selling_price: float,
                  shipping_cost: float = 0,
                  amazon_fees: float = 0,
                  target_acos: float = 0,
                  notes: str = None) -> Tuple[bool, str]:
        """
        Add a new marketing campaign with calculations.
        
        Args:
            campaign_name: Name of the campaign
            product_name: Name of the product
            channel: Marketing channel (e.g., "Amazon")
            category: Product category
            ad_spend: Total ad spend
            clicks: Number of clicks
            impressions: Number of impressions
            conversions: Number of conversions
            revenue: Total revenue
            start_date: Campaign start date
            end_date: Campaign end date
            product_cost: Cost of the product
            selling_price: Selling price of the product
            shipping_cost: Shipping cost (optional)
            amazon_fees: Amazon fees (optional)
            target_acos: Target ACoS percentage (optional)
            notes: Additional notes (optional)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate inputs
            if not campaign_name:
                return False, "Campaign Name is required"
            
            if not product_name:
                return False, "Product Name is required"
            
            if not isinstance(ad_spend, (int, float)) or ad_spend < 0:
                return False, "Ad Spend must be a non-negative number"
            
            if not isinstance(clicks, (int, float)) or clicks < 0:
                return False, "Clicks must be a non-negative number"
            
            if not isinstance(conversions, (int, float)) or conversions < 0:
                return False, "Conversions must be a non-negative number"
                
            if not isinstance(revenue, (int, float)) or revenue < 0:
                return False, "Revenue must be a non-negative number"
            
            # Generate a unique ID
            uid = str(uuid.uuid4())[:8]
            
            # Calculate basic metrics
            avg_cpc = safe_divide(ad_spend, clicks)
            ctr = safe_divide(clicks * 100, impressions)
            conversion_rate = safe_divide(conversions * 100, clicks)
            acos = safe_divide(ad_spend * 100, revenue)
            roas = safe_divide(revenue, ad_spend)
            
            # Default target ACoS if not provided
            if target_acos <= 0:
                if channel == "Amazon":
                    target_acos = 20
                elif channel == "Vive Website":
                    target_acos = 25
                else:
                    target_acos = 30
            
            # Calculate profit metrics
            ad_cost_per_sale = safe_divide(ad_spend, conversions)
            profit_metrics = get_profit_metrics(
                product_cost, selling_price, shipping_cost, amazon_fees, ad_cost_per_sale
            )
            
            profit = profit_metrics["profit"] * conversions
            profit_margin = profit_metrics["profit_margin"]
            
            # Calculate performance score
            performance_score = calculate_performance_score(
                roas, acos, conversion_rate, target_acos, profit_margin
            )
            
            # Create new row
            new_row = {
                'uid': uid,
                'campaign_name': campaign_name,
                'product_name': product_name,
                'channel': channel,
                'category': category,
                'ad_spend': ad_spend,
                'clicks': clicks,
                'impressions': impressions,
                'conversions': conversions,
                'revenue': revenue,
                'start_date': start_date,
                'end_date': end_date,
                'avg_cpc': avg_cpc,
                'ctr': ctr,
                'conversion_rate': conversion_rate,
                'acos': acos,
                'roas': roas,
                'product_cost': product_cost,
                'selling_price': selling_price,
                'shipping_cost': shipping_cost,
                'amazon_fees': amazon_fees,
                'profit': profit,
                'profit_margin': profit_margin,
                'target_acos': target_acos,
                'performance_score': performance_score,
                'timestamp': datetime.now(),
                'notes': notes
            }

            # Add to dataframe
            self.campaigns = pd.concat([self.campaigns, pd.DataFrame([new_row])], ignore_index=True)
            self.save_data()
            return True, "Campaign added successfully!"
        except Exception as e:
            error_details = traceback.format_exc()
            return False, f"Error adding campaign: {str(e)}\n{error_details}"
    
    def get_campaign(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get a campaign by UID."""
        if uid in self.campaigns['uid'].values:
            return self.campaigns[self.campaigns['uid'] == uid].iloc[0].to_dict()
        return None
    
    def delete_campaign(self, uid: str) -> bool:
        """Delete a campaign by UID."""
        if uid in self.campaigns['uid'].values:
            self.campaigns = self.campaigns[self.campaigns['uid'] != uid]
            self.save_data()
            return True
        return False
    
    def update_campaign(self, uid: str, **kwargs) -> Tuple[bool, str]:
        """Update a campaign and recalculate values."""
        if uid not in self.campaigns['uid'].values:
            return False, "Campaign not found"
        
        # Get current values
        current = self.get_campaign(uid)
        if not current:
            return False, "Failed to retrieve campaign data"
        
        # Update with new values
        for key, value in kwargs.items():
            if key in current:
                current[key] = value
        
        # Delete current campaign
        self.delete_campaign(uid)
        
        # Add updated campaign
        success, message = self.add_campaign(
            current['campaign_name'], current['product_name'], current['channel'],
            current['category'], current['ad_spend'], current['clicks'],
            current['impressions'], current['conversions'], current['revenue'],
            current['start_date'], current['end_date'], current['product_cost'],
            current['selling_price'], current['shipping_cost'], current['amazon_fees'],
            current['target_acos'], current['notes']
        )
        
        return success, message
    
    def add_example_campaigns(self) -> int:
        """Add example campaigns for demonstration."""
        added = 0
        for example in self.default_examples:
            success, _ = self.add_campaign(**example)
            if success:
                added += 1
        return added

    def clone_campaign(self, uid: str, new_name: Optional[str] = None) -> Tuple[bool, str]:
        """Clone an existing campaign."""
        if uid not in self.campaigns['uid'].values:
            return False, "Campaign not found"
        
        campaign = self.get_campaign(uid)
        if not campaign:
            return False, "Failed to retrieve campaign data"
        
        # Create new name if not provided
        if not new_name:
            new_name = f"{campaign['campaign_name']} (Clone)"
        
        # Clone campaign
        success, message = self.add_campaign(
            new_name, campaign['product_name'], campaign['channel'],
            campaign['category'], campaign['ad_spend'], campaign['clicks'],
            campaign['impressions'], campaign['conversions'], campaign['revenue'],
            campaign['start_date'], campaign['end_date'], campaign['product_cost'],
            campaign['selling_price'], campaign['shipping_cost'], campaign['amazon_fees'],
            campaign['target_acos'], campaign['notes']
        )
        
        return success, message
    
    def run_monte_carlo_simulation(self, 
                                 campaign_uid: str, 
                                 num_simulations: int = 1000, 
                                 param_variations: Optional[Dict[str, float]] = None) -> Tuple[Optional[pd.DataFrame], str]:
        """
        Run Monte Carlo simulation for a campaign to model outcomes with different parameters
        
        Args:
            campaign_uid: UID of the base campaign
            num_simulations: Number of simulation runs
            param_variations: Dict with parameters and their variation ranges as percentages
                
        Returns:
            Tuple of (results_dataframe, message)
        """
        campaign = self.get_campaign(campaign_uid)
        if not campaign:
            return None, "Campaign not found"
        
        # Set default parameter variations if not provided
        if not param_variations:
            param_variations = {
                'ad_spend': 20,             # ±20% variation
                'ctr': 15,                  # ±15% variation
                'conversion_rate': 25,      # ±25% variation
                'avg_cpc': 15,              # ±15% variation
                'selling_price': 5,         # ±5% variation
                'product_cost': 10          # ±10% variation
            }
        
        # Initialize results dataframe
        results = pd.DataFrame(columns=[
            'simulation_id', 'ad_spend', 'ctr', 'conversion_rate', 'avg_cpc',
            'impressions', 'clicks', 'conversions', 'revenue', 'acos', 'roas',
            'profit', 'profit_margin'
        ])
        
        # Run simulations
        for i in range(num_simulations):
            try:
                # Create variations of parameters
                sim_ad_spend = max(0, campaign['ad_spend'] * np.random.uniform(
                    1 - param_variations['ad_spend']/100,
                    1 + param_variations['ad_spend']/100
                ))
                
                sim_ctr = max(0, campaign['ctr'] * np.random.uniform(
                    1 - param_variations['ctr']/100,
                    1 + param_variations['ctr']/100
                ))
                
                sim_conversion_rate = max(0, campaign['conversion_rate'] * np.random.uniform(
                    1 - param_variations['conversion_rate']/100,
                    1 + param_variations['conversion_rate']/100
                ))
                
                sim_avg_cpc = max(0.01, campaign['avg_cpc'] * np.random.uniform(
                    1 - param_variations['avg_cpc']/100,
                    1 + param_variations['avg_cpc']/100
                ))
                
                sim_selling_price = max(campaign['product_cost'], campaign['selling_price'] * np.random.uniform(
                    1 - param_variations['selling_price']/100,
                    1 + param_variations['selling_price']/100
                ))
                
                sim_product_cost = max(0, campaign['product_cost'] * np.random.uniform(
                    1 - param_variations['product_cost']/100,
                    1 + param_variations['product_cost']/100
                ))
                
                # Calculate simulated metrics
                sim_clicks = sim_ad_spend / sim_avg_cpc
                sim_impressions = (sim_clicks * 100) / sim_ctr
                sim_conversions = (sim_clicks * sim_conversion_rate) / 100
                sim_revenue = sim_conversions * sim_selling_price
                
                sim_acos = safe_divide(sim_ad_spend * 100, sim_revenue)
                sim_roas = safe_divide(sim_revenue, sim_ad_spend)
                
                # Calculate profit metrics
                sim_ad_cost_per_sale = safe_divide(sim_ad_spend, sim_conversions)
                sim_profit_metrics = get_profit_metrics(
                    sim_product_cost, sim_selling_price, 
                    campaign['shipping_cost'], campaign['amazon_fees'], 
                    sim_ad_cost_per_sale
                )
                
                sim_profit = sim_profit_metrics["profit"] * sim_conversions
                sim_profit_margin = sim_profit_metrics["profit_margin"]
                
                # Add to results
                results.loc[i] = [
                    i, sim_ad_spend, sim_ctr, sim_conversion_rate, sim_avg_cpc,
                    sim_impressions, sim_clicks, sim_conversions, sim_revenue,
                    sim_acos, sim_roas, sim_profit, sim_profit_margin
                ]
            except Exception as e:
                # Log error and continue with next simulation
                logger.error(f"Error in simulation {i}: {str(e)}")
                continue
        
        return results, "Simulation completed successfully"
    
    def get_channel_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics across channels."""
        if self.campaigns.empty:
            return {
                'total_campaigns': 0,
                'total_spend': 0,
                'total_revenue': 0,
                'total_profit': 0,
                'overall_roas': 0,
                'overall_acos': 0,
                'avg_conversion_rate': 0,
                'best_channel_roas': None,
                'best_channel_acos': None,
                'worst_channel_roas': None,
                'channels': []
            }
        
        # Get overall metrics
        stats = {
            'total_campaigns': len(self.campaigns),
            'total_spend': self.campaigns['ad_spend'].sum(),
            'total_revenue': self.campaigns['revenue'].sum(),
            'total_profit': self.campaigns['profit'].sum(),
            'overall_roas': safe_divide(self.campaigns['revenue'].sum(), self.campaigns['ad_spend'].sum()),
            'overall_acos': safe_divide(self.campaigns['ad_spend'].sum() * 100, self.campaigns['revenue'].sum()),
            'avg_conversion_rate': self.campaigns['conversion_rate'].mean(),
            'channels': []
        }
        
        # Get channel stats
        channel_stats = self.campaigns.groupby('channel').agg({
            'ad_spend': 'sum',
            'revenue': 'sum',
            'profit': 'sum',
            'conversions': 'sum',
            'clicks': 'sum',
            'impressions': 'sum'
        }).reset_index()
        
        # Calculate channel metrics
        channel_stats['roas'] = channel_stats.apply(lambda x: safe_divide(x['revenue'], x['ad_spend']), axis=1)
        channel_stats['acos'] = channel_stats.apply(lambda x: safe_divide(x['ad_spend'] * 100, x['revenue']), axis=1)
        channel_stats['conversion_rate'] = channel_stats.apply(
            lambda x: safe_divide(x['conversions'] * 100, x['clicks']), axis=1
        )
        channel_stats['profit_margin'] = channel_stats.apply(
            lambda x: safe_divide(x['profit'] * 100, x['revenue']), axis=1
        )
        
        # Store channel data
        for _, channel in channel_stats.iterrows():
            stats['channels'].append({
                'name': channel['channel'],
                'ad_spend': channel['ad_spend'],
                'revenue': channel['revenue'],
                'profit': channel['profit'],
                'conversions': channel['conversions'],
                'clicks': channel['clicks'],
                'impressions': channel['impressions'],
                'roas': channel['roas'],
                'acos': channel['acos'],
                'conversion_rate': channel['conversion_rate'],
                'profit_margin': channel['profit_margin']
            })
        
        # Find best and worst channels
        if not channel_stats.empty:
            best_roas_idx = channel_stats['roas'].idxmax()
            stats['best_channel_roas'] = {
                'name': channel_stats.loc[best_roas_idx, 'channel'],
                'roas': channel_stats.loc[best_roas_idx, 'roas']
            }
            
            best_acos_idx = channel_stats['acos'].idxmin()
            stats['best_channel_acos'] = {
                'name': channel_stats.loc[best_acos_idx, 'channel'],
                'acos': channel_stats.loc[best_acos_idx, 'acos']
            }
            
            worst_roas_idx = channel_stats['roas'].idxmin()
            stats['worst_channel_roas'] = {
                'name': channel_stats.loc[worst_roas_idx, 'channel'],
                'roas': channel_stats.loc[worst_roas_idx, 'roas']
            }
        
        return stats

    def create_scenario(self, base_campaign_uid: str, **adjustments) -> Dict[str, Any]:
        """
        Create a what-if scenario based on an existing campaign.
        
        Args:
            base_campaign_uid: UID of the base campaign
            adjustments: Dict of parameters to adjust (e.g., ad_spend_change=20)
            
        Returns:
            Dict with calculated metrics for the scenario
        """
        campaign = self.get_campaign(base_campaign_uid)
        if not campaign:
            return {"error": "Campaign not found"}
        
        # Get adjustment parameters with defaults
        ad_spend_change = adjustments.get('ad_spend_change', 0)
        cpc_change = adjustments.get('cpc_change', 0)
        ctr_change = adjustments.get('ctr_change', 0)
        conversion_rate_change = adjustments.get('conversion_rate_change', 0)
        price_change = adjustments.get('price_change', 0)
        cost_change = adjustments.get('cost_change', 0)
        
        # Calculate new values
        new_ad_spend = campaign['ad_spend'] * (1 + ad_spend_change / 100)
        new_avg_cpc = campaign['avg_cpc'] * (1 + cpc_change / 100)
        new_ctr = campaign['ctr'] * (1 + ctr_change / 100)
        new_conversion_rate = campaign['conversion_rate'] * (1 + conversion_rate_change / 100)
        new_selling_price = campaign['selling_price'] * (1 + price_change / 100)
        new_product_cost = campaign['product_cost'] * (1 + cost_change / 100)
        
        # Calculate derived metrics
        new_clicks = new_ad_spend / new_avg_cpc
        new_impressions = (new_clicks * 100) / new_ctr
        new_conversions = (new_clicks * new_conversion_rate) / 100
        new_revenue = new_conversions * new_selling_price
        
        new_acos = safe_divide(new_ad_spend * 100, new_revenue)
        new_roas = safe_divide(new_revenue, new_ad_spend)
        
        # Calculate profit metrics
        new_ad_cost_per_sale = safe_divide(new_ad_spend, new_conversions)
        new_profit_metrics = get_profit_metrics(
            new_product_cost, new_selling_price, 
            campaign['shipping_cost'], campaign['amazon_fees'], 
            new_ad_cost_per_sale
        )
        
        new_profit = new_profit_metrics["profit"] * new_conversions
        new_profit_margin = new_profit_metrics["profit_margin"]
        
        # Create scenario dict
        scenario = {
            'base_campaign': campaign['campaign_name'],
            'ad_spend': new_ad_spend,
            'avg_cpc': new_avg_cpc,
            'ctr': new_ctr,
            'clicks': new_clicks,
            'impressions': new_impressions,
            'conversion_rate': new_conversion_rate,
            'conversions': new_conversions,
            'selling_price': new_selling_price,
            'product_cost': new_product_cost,
            'revenue': new_revenue,
            'acos': new_acos,
            'roas': new_roas,
            'profit': new_profit,
            'profit_margin': new_profit_margin,
            # Calculate changes from base campaign
            'changes': {
                'ad_spend_change': (new_ad_spend - campaign['ad_spend']) / campaign['ad_spend'] * 100 if campaign['ad_spend'] > 0 else 0,
                'clicks_change': (new_clicks - campaign['clicks']) / campaign['clicks'] * 100 if campaign['clicks'] > 0 else 0,
                'conversions_change': (new_conversions - campaign['conversions']) / campaign['conversions'] * 100 if campaign['conversions'] > 0 else 0,
                'revenue_change': (new_revenue - campaign['revenue']) / campaign['revenue'] * 100 if campaign['revenue'] > 0 else 0,
                'profit_change': (new_profit - campaign['profit']) / campaign['profit'] * 100 if campaign['profit'] > 0 else 0,
                'roas_change': (new_roas - campaign['roas']) / campaign['roas'] * 100 if campaign['roas'] > 0 else 0,
                'acos_change': (new_acos - campaign['acos']) / campaign['acos'] * 100 if campaign['acos'] > 0 else 0
            }
        }
        
        return scenario

# Initialize app
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = MarketingAnalyzer()
analyzer = st.session_state.analyzer

# Wizard mode tracking
if 'wizard_step' not in st.session_state:
    st.session_state.wizard_step = 1
    
if 'wizard_data' not in st.session_state:
    st.session_state.wizard_data = {}

# Check OpenAI API key validity on startup
if 'api_key_status' not in st.session_state:
    check_openai_api_key()

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
            <h1 style="font-size: 32px; margin: 0; color: {COLOR_SCHEME["primary"]};">📊</h1>
            <p style="margin: 0; font-weight: 600; color: {COLOR_SCHEME["secondary"]};">ViveROI</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Title and description
    with col2:
        st.title("PPC & Marketing Analytics")
        st.caption("Optimize marketing spend, track channel performance, and maximize ROI across e-commerce platforms")

def display_metrics_overview(df: pd.DataFrame):
    """Display key metrics overview cards."""
    if df.empty:
        st.info("Add or import campaigns to see metrics.")
        return
    
    # Get aggregate statistics
    stats = analyzer.get_channel_statistics()
    
    # Display metrics in cards
    st.subheader("Marketing Performance Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Total Ad Spend</p>
            <p class="metric-value" style="color: {COLOR_SCHEME["primary"]};">{format_currency(stats['total_spend'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Overall ROAS</p>
            <p class="metric-value" style="color: {get_color_scale(stats['overall_roas'], 2, 6)};">{stats['overall_roas']:.2f}x</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Overall ACoS</p>
            <p class="metric-value" style="color: {get_color_scale(stats['overall_acos'], 40, 10, reverse=True)};">{format_percent(stats['overall_acos'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <p class="metric-label">Total Profit</p>
            <p class="metric-value" style="color: {get_color_scale(stats['total_profit'], 0, stats['total_profit']*1.5)};">{format_currency(stats['total_profit'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row with more metrics in advanced mode
    if st.session_state.app_mode == "Advanced":
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        # Try to get average performance scores
        avg_score = df['performance_score'].mean() if 'performance_score' in df.columns else None
        conversion_rate = stats['avg_conversion_rate']
        
        # Try to get best and worst channels
        best_channel = stats['best_channel_roas']['name'] if stats['best_channel_roas'] else "N/A"
        best_roas = stats['best_channel_roas']['roas'] if stats['best_channel_roas'] else 0
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <p class="metric-label">Campaigns</p>
                <p class="metric-value" style="color: {COLOR_SCHEME["primary"]};">{stats['total_campaigns']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <p class="metric-label">Avg. Performance Score</p>
                <p class="metric-value" style="color: {get_color_scale(avg_score, 40, 80)};">{avg_score:.1f if avg_score else 'N/A'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <p class="metric-label">Avg. Conversion Rate</p>
                <p class="metric-value" style="color: {get_color_scale(conversion_rate, 1, 4)};">{format_percent(conversion_rate)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-container">
                <p class="metric-label">Best Performing Channel</p>
                <p class="metric-value" style="color: {COLOR_SCHEME["positive"]};">{best_channel}</p>
                <p style="font-size: 0.8rem; margin: 0;">{format_number(best_roas, 2)}x ROAS</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display top performing campaigns
        st.markdown("### Top Performing Campaigns")
        try:
            # Get top 3 campaigns by ROAS
            top_campaigns = df.sort_values(by='roas', ascending=False).head(3)
            
            col1, col2, col3 = st.columns(3)
            columns = [col1, col2, col3]
            
            for i, (_, campaign) in enumerate(top_campaigns.iterrows()):
                if i < len(columns):
                    with columns[i]:
                        channel_class = campaign['channel'].lower().replace(' ', '')
                        st.markdown(f"""
                        <div class="campaign-card {channel_class}">
                            <div class="header">
                                <span class="title">{campaign['campaign_name']}</span>
                                <span class="channel">{campaign['channel']}</span>
                            </div>
                            <div class="product">{campaign['product_name']}</div>
                            <div class="metrics">
                                <div class="metric">
                                    <div class="metric-label">ROAS</div>
                                    <div class="metric-value" style="color: {get_color_scale(campaign['roas'], 2, 6)};">{campaign['roas']:.2f}x</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-label">ACoS</div>
                                    <div class="metric-value" style="color: {get_color_scale(campaign['acos'], 40, 10, reverse=True)};">{campaign['acos']:.2f}%</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-label">Conv. Rate</div>
                                    <div class="metric-value">{campaign['conversion_rate']:.2f}%</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error displaying top campaigns: {str(e)}")

def create_campaign_form(wizard_mode: bool = False) -> bool:
    """
    Create form for adding a new marketing campaign.
    
    Args:
        wizard_mode: Whether to use the step-by-step wizard interface
        
    Returns:
        bool: True if campaign was added successfully
    """
    if wizard_mode:
        # Set up wizard interface
        return create_campaign_wizard()
    
    with st.form(key="campaign_form"):
        st.subheader("Add New Marketing Campaign")
        
        # Display tips if in advanced mode
        if st.session_state.app_mode == "Advanced":
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="info-box">
                    <p><strong>Pro Tip:</strong> For more guided campaign creation, try the <b>Campaign Wizard</b> in the sidebar.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="success-box">
                    <p><strong>Best Practice:</strong> Be sure to include product costs and all fees for accurate profit margin calculations.</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Basic Information
        st.markdown("### Campaign Information")
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("Campaign Name", 
                                      help="A descriptive name for this marketing campaign")
            
            product_name = st.text_input("Product Name", 
                                     help="The product being advertised")
            
            # Channel selection
            channel = st.selectbox("Marketing Channel", 
                                DEFAULT_CHANNELS,
                                help="The platform or channel where the campaign is running")
        
        with col2:
            category = st.selectbox("Product Category", 
                                 DEFAULT_CATEGORIES,
                                 help="The category this product belongs to")
            
            start_date = st.date_input("Start Date", 
                                     datetime.now() - timedelta(days=30),
                                     help="When the campaign started")
            
            end_date = st.date_input("End Date", 
                                   datetime.now(),
                                   help="When the campaign ended")
        
        # Marketing Metrics
        st.markdown("### Marketing Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ad_spend = st.number_input("Ad Spend ($)", 
                                    min_value=0.0, 
                                    format="%.2f", 
                                    help="Total amount spent on ads")
            
            impressions = st.number_input("Impressions", 
                                       min_value=0, 
                                       help="Total number of ad impressions")
        
        with col2:
            clicks = st.number_input("Clicks", 
                                  min_value=0, 
                                  help="Total number of clicks on ads")
            
            conversions = st.number_input("Conversions", 
                                       min_value=0, 
                                       help="Total number of conversions or sales")
        
        with col3:
            revenue = st.number_input("Revenue ($)", 
                                   min_value=0.0, 
                                   format="%.2f", 
                                   help="Total revenue generated from the campaign")
            
            target_acos = st.number_input("Target ACoS (%)", 
                                       min_value=0.0, 
                                       max_value=100.0, 
                                       format="%.2f", 
                                       help="Target Advertising Cost of Sales percentage")
        
        # Product Economics
        st.markdown("### Product Economics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            product_cost = st.number_input("Product Cost ($)", 
                                        min_value=0.0, 
                                        format="%.2f", 
                                        help="Cost to produce or acquire the product")
            
            selling_price = st.number_input("Selling Price ($)", 
                                         min_value=0.0, 
                                         format="%.2f", 
                                         help="Price the product is sold for")
        
        with col2:
            shipping_cost = st.number_input("Shipping Cost ($)", 
                                         min_value=0.0, 
                                         format="%.2f", 
                                         value=0.0,
                                         help="Cost to ship the product")
            
            amazon_fees = st.number_input("Amazon Fees ($)", 
                                       min_value=0.0, 
                                       format="%.2f", 
                                       value=0.0,
                                       help="Amazon referral and FBA fees if applicable")
        
        with col3:
            notes = st.text_area("Campaign Notes", 
                              help="Additional details about the campaign")
        
        # Calculate and preview stats if we have data
        if ad_spend > 0 and clicks > 0 and conversions > 0 and revenue > 0:
            # Calculate metrics
            avg_cpc = ad_spend / clicks if clicks > 0 else 0
            ctr = (clicks / impressions) * 100 if impressions > 0 else 0
            conversion_rate = (conversions / clicks) * 100 if clicks > 0 else 0
            acos = (ad_spend / revenue) * 100 if revenue > 0 else 0
            roas = revenue / ad_spend if ad_spend > 0 else 0
            
            # Calculate profit
            ad_cost_per_sale = ad_spend / conversions if conversions > 0 else 0
            profit_metrics = get_profit_metrics(
                product_cost, selling_price, shipping_cost, amazon_fees, ad_cost_per_sale
            )
            profit_per_unit = profit_metrics["profit"]
            profit = profit_per_unit * conversions
            profit_margin = profit_metrics["profit_margin"]
            
            # Display preview
            st.markdown("### Campaign Performance Preview")
            
            # Performance metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Avg. CPC", f"${avg_cpc:.2f}")
                st.metric("CTR", f"{ctr:.2f}%")
            
            with col2:
                st.metric("Conversion Rate", f"{conversion_rate:.2f}%")
                st.metric("ACoS", f"{acos:.2f}%", 
                        delta=f"{target_acos - acos:.2f}%" if target_acos > 0 else None)
            
            with col3:
                st.metric("ROAS", f"{roas:.2f}x")
                st.metric("Profit Margin", f"{profit_margin:.2f}%")
            
            with col4:
                st.metric("Total Profit", f"${profit:.2f}")
                st.metric("Profit per Sale", f"${profit_per_unit:.2f}")
            
            # Performance assessment
            assessment = ""
            if roas >= 4:
                assessment = "Excellent"
                color = COLOR_SCHEME["positive"]
            elif roas >= 3:
                assessment = "Good"
                color = COLOR_SCHEME["positive"]
            elif roas >= 2:
                assessment = "Average"
                color = COLOR_SCHEME["warning"]
            else:
                assessment = "Poor"
                color = COLOR_SCHEME["negative"]
            
            st.markdown(f"""
            <div style="padding: 10px; border-radius: 5px; background-color: {color}30; border-left: 4px solid {color};">
                <strong>Campaign Assessment:</strong> {assessment} - ROAS of {roas:.2f}x {f"with ACoS {acos:.2f}% vs target {target_acos:.2f}%" if target_acos > 0 else ""} 
                and profit margin of {profit_margin:.2f}%
            </div>
            """, unsafe_allow_html=True)
        
        # Submit button
        submitted = st.form_submit_button("Save Campaign")
        
        if submitted:
            success, message = analyzer.add_campaign(
                campaign_name, product_name, channel, category,
                ad_spend, clicks, impressions, conversions, revenue,
                start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),
                product_cost, selling_price, shipping_cost, amazon_fees,
                target_acos, notes
            )
            
            if success:
                st.success(message)
                return True
            else:
                st.error(message)
                return False
    
    return False

def create_campaign_wizard() -> bool:
    """
    Create a step-by-step wizard for adding a campaign.
    
    Returns:
        bool: True if wizard was completed successfully
    """
    # Initialize wizard_data if needed
    if 'wizard_data' not in st.session_state:
        st.session_state.wizard_data = {}
    
    # Display progress tracker
    st.markdown("### Campaign Creation Wizard")
    steps = ["Basic Info", "Campaign Data", "Product Economics", "Review"]
    
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
    
    # Step 1: Basic Information
    if st.session_state.wizard_step == 1:
        st.subheader("Step 1: Basic Campaign Information")
        
        col1, col2 = st.columns(2)
        with col1:
            campaign_name = st.text_input("Campaign Name", 
                value=st.session_state.wizard_data.get('campaign_name', ''),
                help="A descriptive name for this marketing campaign")
            
            product_name = st.text_input("Product Name", 
                value=st.session_state.wizard_data.get('product_name', ''),
                help="The product being advertised")
            
            # Channel selection
            channel = st.selectbox("Marketing Channel", 
                DEFAULT_CHANNELS,
                index=DEFAULT_CHANNELS.index(st.session_state.wizard_data.get('channel', 'Amazon')) 
                    if st.session_state.wizard_data.get('channel', '') in DEFAULT_CHANNELS else 0,
                help="The platform or channel where the campaign is running")
        
        with col2:
            category = st.selectbox("Product Category", 
                DEFAULT_CATEGORIES,
                index=DEFAULT_CATEGORIES.index(st.session_state.wizard_data.get('category', 'Mobility')) 
                    if st.session_state.wizard_data.get('category', '') in DEFAULT_CATEGORIES else 0,
                help="The category this product belongs to")
            
            start_date = st.date_input("Start Date", 
                datetime.strptime(st.session_state.wizard_data.get('start_date', 
                    (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')), '%Y-%m-%d'),
                help="When the campaign started")
            
            end_date = st.date_input("End Date", 
                datetime.strptime(st.session_state.wizard_data.get('end_date', 
                    datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d'),
                help="When the campaign ended")
        
        notes = st.text_area("Campaign Notes", 
            value=st.session_state.wizard_data.get('notes', ''),
            help="Additional details about the campaign")
        
        # Channel-specific tips
        if channel == "Amazon":
            st.info("""
            **Amazon PPC Tips:**
            - For Sponsored Products, target ACoS is typically 15-25%
            - For new products, you might need higher ACoS (25-35%) initially
            - Track organic rank improvements as a secondary KPI
            """)
        elif channel == "Vive Website":
            st.info("""
            **Website PPC Tips:**
            - Include conversion tracking for accurate attribution
            - Consider the full customer journey including post-purchase value
            - Track new vs. returning visitors separately
            """)
        
        # Save data
        if st.button("Next: Campaign Data"):
            # Validate inputs
            if not campaign_name:
                st.error("Please enter a Campaign Name")
                return False
            
            if not product_name:
                st.error("Please enter a Product Name")
                return False
            
            # Save to session state
            st.session_state.wizard_data.update({
                'campaign_name': campaign_name,
                'product_name': product_name,
                'channel': channel,
                'category': category,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'notes': notes
            })
            
            # Go to next step
            st.session_state.wizard_step = 2
            st.rerun()
    
    # Step 2: Campaign Data
    elif st.session_state.wizard_step == 2:
        st.subheader("Step 2: Campaign Performance Data")
        
        # Show the campaign name and channel from previous step
        st.markdown(f"""
        <div style="padding: 10px; border-radius: 5px; background-color: {COLOR_SCHEME['primary']}20; margin-bottom: 20px;">
            <strong>Campaign:</strong> {st.session_state.wizard_data.get('campaign_name', '')} | 
            <strong>Channel:</strong> {st.session_state.wizard_data.get('channel', '')} | 
            <strong>Product:</strong> {st.session_state.wizard_data.get('product_name', '')}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ad_spend = st.number_input("Ad Spend ($)", 
                value=float(st.session_state.wizard_data.get('ad_spend', 0.0)),
                min_value=0.0, 
                format="%.2f", 
                help="Total amount spent on ads")
            
            impressions = st.number_input("Impressions", 
                value=int(st.session_state.wizard_data.get('impressions', 0)),
                min_value=0, 
                help="Total number of ad impressions")
        
        with col2:
            clicks = st.number_input("Clicks", 
                value=int(st.session_state.wizard_data.get('clicks', 0)),
                min_value=0, 
                help="Total number of clicks on ads")
            
            conversions = st.number_input("Conversions", 
                value=int(st.session_state.wizard_data.get('conversions', 0)),
                min_value=0, 
                help="Total number of conversions or sales")
        
        with col3:
            revenue = st.number_input("Revenue ($)", 
                value=float(st.session_state.wizard_data.get('revenue', 0.0)),
                min_value=0.0, 
                format="%.2f", 
                help="Total revenue generated from the campaign")
            
            target_acos = st.number_input("Target ACoS (%)", 
                value=float(st.session_state.wizard_data.get('target_acos', 0.0)),
                min_value=0.0, 
                max_value=100.0, 
                format="%.2f", 
                help="Target Advertising Cost of Sales percentage")
        
        # Show calculated metrics if we have data
        if ad_spend > 0 and clicks > 0:
            # Calculate metrics
            avg_cpc = ad_spend / clicks if clicks > 0 else 0
            ctr = (clicks / impressions) * 100 if impressions > 0 else 0
            conversion_rate = (conversions / clicks) * 100 if clicks > 0 else 0
            acos = (ad_spend / revenue) * 100 if revenue > 0 else 0
            roas = revenue / ad_spend if ad_spend > 0 else 0
            
            # Display metrics
            st.markdown("### Calculated Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Avg. CPC", f"${avg_cpc:.2f}")
            
            with col2:
                st.metric("CTR", f"{ctr:.2f}%")
            
            with col3:
                st.metric("Conversion Rate", f"{conversion_rate:.2f}%")
            
            with col4:
                if revenue > 0:
                    st.metric("ACoS", f"{acos:.2f}%", 
                            delta=f"{target_acos - acos:.2f}%" if target_acos > 0 else None,
                            delta_color="inverse")
                    st.metric("ROAS", f"{roas:.2f}x")
            
            # Channel-specific benchmarks
            channel = st.session_state.wizard_data.get('channel', '')
            if channel == "Amazon":
                st.info(f"""
                **Amazon PPC Benchmarks:**
                - Average CPC: $0.70-$1.20
                - Average CTR: 0.3-0.5%
                - Average Conversion Rate: 10-15%
                - Good ACoS: 15-25%
                
                Your metrics: CPC ${avg_cpc:.2f}, CTR {ctr:.2f}%, Conv. Rate {conversion_rate:.2f}%, ACoS {acos:.2f}%
                """)
            elif channel == "Vive Website":
                st.info(f"""
                **Website PPC Benchmarks:**
                - Average CPC: $1.00-$2.00
                - Average CTR: 2-4%
                - Average Conversion Rate: 2-4%
                - Good ACoS: 20-30%
                
                Your metrics: CPC ${avg_cpc:.2f}, CTR {ctr:.2f}%, Conv. Rate {conversion_rate:.2f}%, ACoS {acos:.2f}%
                """)
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.wizard_step = 1
                st.rerun()
        
        with col2:
            if st.button("Next: Product Economics"):
                # Validate inputs
                if ad_spend <= 0:
                    st.error("Please enter a value greater than 0 for Ad Spend")
                    return False
                
                if clicks <= 0:
                    st.error("Please enter a value greater than 0 for Clicks")
                    return False
                
                if impressions <= 0:
                    st.error("Please enter a value greater than 0 for Impressions")
                    return False
                
                if revenue <= 0 and conversions > 0:
                    st.error("Please enter a value greater than 0 for Revenue")
                    return False
                
                # Save to session state
                st.session_state.wizard_data.update({
                    'ad_spend': ad_spend,
                    'clicks': clicks,
                    'impressions': impressions,
                    'conversions': conversions,
                    'revenue': revenue,
                    'target_acos': target_acos
                })
                
                # Go to next step
                st.session_state.wizard_step = 3
                st.rerun()
    
    # Step 3: Product Economics
    elif st.session_state.wizard_step == 3:
        st.subheader("Step 3: Product Economics")
        
        # Show campaign info
        st.markdown(f"""
        <div style="padding: 10px; border-radius: 5px; background-color: {COLOR_SCHEME['primary']}20; margin-bottom: 20px;">
            <strong>Campaign:</strong> {st.session_state.wizard_data.get('campaign_name', '')} | 
            <strong>Channel:</strong> {st.session_state.wizard_data.get('channel', '')} | 
            <strong>ROAS:</strong> {safe_divide(st.session_state.wizard_data.get('revenue', 0), st.session_state.wizard_data.get('ad_spend', 0)):.2f}x
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            product_cost = st.number_input("Product Cost ($)", 
                value=float(st.session_state.wizard_data.get('product_cost', 0.0)),
                min_value=0.0, 
                format="%.2f", 
                help="Cost to produce or acquire the product")
            
            selling_price = st.number_input("Selling Price ($)", 
                value=float(st.session_state.wizard_data.get('selling_price', 0.0)),
                min_value=0.0, 
                format="%.2f", 
                help="Price the product is sold for")
        
        with col2:
            shipping_cost = st.number_input("Shipping Cost ($)", 
                value=float(st.session_state.wizard_data.get('shipping_cost', 0.0)),
                min_value=0.0, 
                format="%.2f",
                help="Cost to ship the product")
            
            channel = st.session_state.wizard_data.get('channel', '')
            if channel == "Amazon":
                amazon_fees_label = "Amazon Fees ($)"
                amazon_fees_help = "Amazon referral and FBA fees"
            else:
                amazon_fees_label = "Platform Fees ($)"
                amazon_fees_help = f"Any {channel} platform fees"
            
            amazon_fees = st.number_input(amazon_fees_label, 
                value=float(st.session_state.wizard_data.get('amazon_fees', 0.0)),
                min_value=0.0, 
                format="%.2f",
                help=amazon_fees_help)
        
        with col3:
            # Display placeholder for calculated values
            st.markdown("#### Calculated Metrics")
            st.write("Complete the form to see metrics")
        
        # Calculate and show profit metrics if we have the necessary data
        if product_cost > 0 and selling_price > 0 and st.session_state.wizard_data.get('conversions', 0) > 0:
            # Get data from previous steps
            ad_spend = st.session_state.wizard_data.get('ad_spend', 0)
            conversions = st.session_state.wizard_data.get('conversions', 0)
            revenue = st.session_state.wizard_data.get('revenue', 0)
            
            # Calculate metrics
            ad_cost_per_sale = ad_spend / conversions if conversions > 0 else 0
            profit_metrics = get_profit_metrics(
                product_cost, selling_price, shipping_cost, amazon_fees, ad_cost_per_sale
            )
            
            profit_per_unit = profit_metrics["profit"]
            total_profit = profit_per_unit * conversions
            profit_margin = profit_metrics["profit_margin"]
            
            # Display in the third column
            with col3:
                st.metric("Profit per Sale", f"${profit_per_unit:.2f}")
                st.metric("Total Profit", f"${total_profit:.2f}")
                st.metric("Profit Margin", f"{profit_margin:.2f}%")
            
            # Visual breakdown of costs and revenue
            st.markdown("### Economics Breakdown")
            
            # Create sankey diagram data
            if st.session_state.app_mode == "Advanced":
                # For advanced mode, show detailed cost breakdown
                fig = go.Figure(go.Waterfall(
                    name="Product Economics",
                    orientation="v",
                    measure=["relative", "relative", "relative", "relative", "relative", "total"],
                    x=["Selling Price", "Product Cost", "Shipping", f"{channel} Fees", "Ad Cost/Sale", "Profit"],
                    textposition="outside",
                    y=[selling_price, -product_cost, -shipping_cost, -amazon_fees, -ad_cost_per_sale, profit_per_unit],
                    connector={"line": {"color": "rgb(63, 63, 63)"}},
                    decreasing={"marker": {"color": COLOR_SCHEME["negative"]}},
                    increasing={"marker": {"color": COLOR_SCHEME["positive"]}},
                    totals={"marker": {"color": COLOR_SCHEME["secondary"]}}
                ))
                
                fig.update_layout(
                    title="Per-Unit Economics Breakdown",
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                # For basic mode, show simplified pie chart
                labels = ["Profit", "Product Cost", "Shipping", f"{channel} Fees", "Ad Cost"]
                values = [profit_per_unit, product_cost, shipping_cost, amazon_fees, ad_cost_per_sale]
                
                fig = px.pie(
                    names=labels,
                    values=values,
                    title="Revenue Allocation",
                    color=labels,
                    color_discrete_map={
                        "Profit": COLOR_SCHEME["positive"],
                        "Product Cost": COLOR_SCHEME["negative"],
                        "Shipping": COLOR_SCHEME["negative"],
                        f"{channel} Fees": COLOR_SCHEME["negative"],
                        "Ad Cost": COLOR_SCHEME["warning"]
                    }
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Show performance assessment
            if profit_margin >= 30:
                margin_assessment = "Excellent"
                color = COLOR_SCHEME["positive"]
            elif profit_margin >= 20:
                margin_assessment = "Good"
                color = COLOR_SCHEME["positive"]
            elif profit_margin >= 10:
                margin_assessment = "Average"
                color = COLOR_SCHEME["warning"]
            else:
                margin_assessment = "Poor"
                color = COLOR_SCHEME["negative"]
            
            st.markdown(f"""
            <div style="padding: 10px; border-radius: 5px; background-color: {color}30; border-left: 4px solid {color};">
                <strong>Profitability Assessment:</strong> {margin_assessment} - Profit margin of {profit_margin:.2f}%
                with ${profit_per_unit:.2f} profit per sale and ${total_profit:.2f} total profit.
            </div>
            """, unsafe_allow_html=True)
            
            # Channel-specific recommendations
            if channel == "Amazon" and profit_margin < 20:
                st.warning("""
                **Amazon Profitability Alert:**
                Your profit margin is below recommended levels for Amazon (20-30%). Consider:
                1. Increasing your selling price
                2. Finding ways to reduce product or shipping costs
                3. Optimizing Amazon FBA fees by improving packaging
                4. Reducing ACoS by focusing on higher-converting keywords
                """)
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.wizard_step = 2
                st.rerun()
        
        with col2:
            if st.button("Next: Review"):
                # Validate inputs
                if product_cost <= 0:
                    st.error("Please enter a value greater than 0 for Product Cost")
                    return False
                
                if selling_price <= 0:
                    st.error("Please enter a value greater than 0 for Selling Price")
                    return False
                
                if selling_price <= product_cost:
                    st.warning("Warning: Selling price is less than or equal to product cost")
                
                # Save to session state
                st.session_state.wizard_data.update({
                    'product_cost': product_cost,
                    'selling_price': selling_price,
                    'shipping_cost': shipping_cost,
                    'amazon_fees': amazon_fees
                })
                
                # Go to next step
                st.session_state.wizard_step = 4
                st.rerun()
    
    # Step 4: Review and Save
    elif st.session_state.wizard_step == 4:
        st.subheader("Step 4: Review & Save Campaign")
        
        # Calculate all metrics for review
        campaign_data = st.session_state.wizard_data
        
        # Basic metrics
        ad_spend = campaign_data.get('ad_spend', 0)
        clicks = campaign_data.get('clicks', 0)
        impressions = campaign_data.get('impressions', 0)
        conversions = campaign_data.get('conversions', 0)
        revenue = campaign_data.get('revenue', 0)
        
        # Product economics
        product_cost = campaign_data.get('product_cost', 0)
        selling_price = campaign_data.get('selling_price', 0)
        shipping_cost = campaign_data.get('shipping_cost', 0)
        amazon_fees = campaign_data.get('amazon_fees', 0)
        
        # Calculate derived metrics
        avg_cpc = safe_divide(ad_spend, clicks)
        ctr = safe_divide(clicks * 100, impressions)
        conversion_rate = safe_divide(conversions * 100, clicks)
        acos = safe_divide(ad_spend * 100, revenue)
        roas = safe_divide(revenue, ad_spend)
        
        # Profit calculations
        ad_cost_per_sale = safe_divide(ad_spend, conversions)
        profit_metrics = get_profit_metrics(
            product_cost, selling_price, shipping_cost, amazon_fees, ad_cost_per_sale
        )
        
        profit_per_unit = profit_metrics["profit"]
        total_profit = profit_per_unit * conversions
        profit_margin = profit_metrics["profit_margin"]
        
        # Display summary
        st.markdown("### Campaign Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Basic Information")
            st.markdown(f"**Campaign Name:** {campaign_data.get('campaign_name', '')}")
            st.markdown(f"**Product:** {campaign_data.get('product_name', '')}")
            st.markdown(f"**Channel:** {campaign_data.get('channel', '')}")
            st.markdown(f"**Category:** {campaign_data.get('category', '')}")
            st.markdown(f"**Date Range:** {campaign_data.get('start_date', '')} to {campaign_data.get('end_date', '')}")
        
        with col2:
            st.markdown("#### Campaign Performance")
            st.markdown(f"**Ad Spend:** ${ad_spend:.2f}")
            st.markdown(f"**Impressions:** {impressions:,}")
            st.markdown(f"**Clicks:** {clicks:,}")
            st.markdown(f"**Conversions:** {conversions:,}")
            st.markdown(f"**Revenue:** ${revenue:.2f}")
        
        st.markdown("#### Key Metrics")
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric("ROAS", f"{roas:.2f}x")
            st.metric("ACoS", f"{acos:.2f}%")
        
        with metric_col2:
            st.metric("Conversion Rate", f"{conversion_rate:.2f}%")
            st.metric("Avg. CPC", f"${avg_cpc:.2f}")
        
        with metric_col3:
            st.metric("CTR", f"{ctr:.2f}%")
            st.metric("Profit per Sale", f"${profit_per_unit:.2f}")
        
        with metric_col4:
            st.metric("Total Profit", f"${total_profit:.2f}")
            st.metric("Profit Margin", f"{profit_margin:.2f}%")
        
        # Campaign assessment
        st.markdown("### Campaign Assessment")
        
        # Define assessment criteria
        if roas >= 4 and profit_margin >= 25:
            assessment = "Excellent"
            color = COLOR_SCHEME["positive"]
            recommendations = [
                "Consider increasing ad spend to capture more market share",
                "Expand to similar product categories",
                "Test premium ad placements for even better visibility"
            ]
        elif roas >= 3 and profit_margin >= 15:
            assessment = "Good"
            color = COLOR_SCHEME["positive"]
            recommendations = [
                "Fine-tune keyword targeting to improve ACoS",
                "Test incremental budget increases",
                "Optimize product listing to improve conversion rate"
            ]
        elif roas >= 2:
            assessment = "Average"
            color = COLOR_SCHEME["warning"]
            recommendations = [
                "Review keywords and eliminate poor performers",
                "Improve product images and content to boost conversion rate",
                "Consider pricing adjustments to improve margins"
            ]
        else:
            assessment = "Needs Improvement"
            color = COLOR_SCHEME["negative"]
            recommendations = [
                "Significantly reduce spend on poorly performing keywords",
                "Review product pricing and costs",
                "Audit the entire campaign structure",
                "Consider pausing the campaign if performance doesn't improve"
            ]
        
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 5px; background-color: {color}30; border-left: 4px solid {color}; margin-bottom: 20px;">
            <h4 style="margin-top: 0;">Performance: {assessment}</h4>
            <p>This campaign is performing at a <strong>{assessment.lower()}</strong> level with a ROAS of {roas:.2f}x 
            and profit margin of {profit_margin:.2f}%.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display recommendations
        st.markdown("### Recommendations")
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
        
        # Add notes field
        notes = campaign_data.get('notes', '')
        final_notes = st.text_area("Additional Notes", value=notes, help="Add any final notes before saving")
        
        # Navigation and save buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Edit"):
                st.session_state.wizard_step = 3
                st.rerun()
        
        with col2:
            if st.button("Save Campaign"):
                # Update notes if changed
                if final_notes != notes:
                    st.session_state.wizard_data['notes'] = final_notes
                
                # Create campaign
                success, message = analyzer.add_campaign(
                    campaign_data.get('campaign_name', ''),
                    campaign_data.get('product_name', ''),
                    campaign_data.get('channel', ''),
                    campaign_data.get('category', ''),
                    ad_spend,
                    clicks,
                    impressions,
                    conversions,
                    revenue,
                    campaign_data.get('start_date', ''),
                    campaign_data.get('end_date', ''),
                    product_cost,
                    selling_price,
                    shipping_cost,
                    amazon_fees,
                    campaign_data.get('target_acos', 0),
                    final_notes
                )
                
                if success:
                    st.success("Campaign saved successfully!")
                    
                    # Reset wizard
                    st.session_state.wizard_step = 1
                    st.session_state.wizard_data = {}
                    
                    # Redirect to dashboard
                    st.session_state.nav_option = "Campaign Dashboard"
                    st.rerun()
                else:
                    st.error(message)
    
    return True

def display_campaign_table(df: pd.DataFrame, analyzer: MarketingAnalyzer):
    """
    Display campaign table with filtering and sorting.
    
    Args:
        df: DataFrame with campaigns
        analyzer: MarketingAnalyzer instance
    """
    if df.empty:
        st.info("No campaigns found. Add a new campaign or load example campaigns.")
        return
    
    # Add filters
    st.subheader("Campaign Analysis")
    
    # Advanced filtering in advanced mode
    if st.session_state.app_mode == "Advanced":
        with st.expander("Filtering Options", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                channel_filter = st.multiselect("Filter by Channel", 
                                          options=sorted(df['channel'].unique()),
                                          default=[],
                                          help="Select one or more channels")
            
            with col2:
                category_filter = st.multiselect("Filter by Category", 
                                           options=sorted(df['category'].unique()),
                                           default=[],
                                           help="Select one or more categories")
            
            with col3:
                # Date range filter
                date_filter = st.date_input("Filter by Date Range",
                                         value=(datetime.now() - timedelta(days=90), datetime.now()),
                                         help="Filter campaigns by date range")
            
            # Additional filters in advanced mode
            col1, col2 = st.columns(2)
            
            with col1:
                min_roas = st.slider("Minimum ROAS", 
                                  0.0, 10.0, 0.0, 0.1,
                                  help="Filter campaigns by minimum ROAS")
            
            with col2:
                max_acos = st.slider("Maximum ACoS (%)", 
                                   0.0, 100.0, 100.0, 1.0,
                                   help="Filter campaigns by maximum ACoS")
    else:
        # Simplified filtering in basic mode
        col1, col2, col3 = st.columns(3)
        
        with col1:
            channel_options = sorted(df['channel'].unique())
            channel_filter = st.multiselect("Filter by Channel", 
                                       options=channel_options,
                                       default=[])
        
        with col2:
            category_options = sorted(df['category'].unique())
            category_filter = st.multiselect("Filter by Category", 
                                        options=category_options,
                                        default=[])
        
        with col3:
            # Simple performance filter
            performance_filter = st.selectbox("Performance Filter", 
                                         ["All", "High Performers (ROAS > 3)", "Low Performers (ROAS < 2)"])
        
        # Default values for basic mode
        min_roas = 0.0
        max_acos = 100.0
        if performance_filter == "High Performers (ROAS > 3)":
            min_roas = 3.0
        elif performance_filter == "Low Performers (ROAS < 2)":
            min_roas = 0.0
            max_acos = 50.0  # Assuming we want to see fixable campaigns
        
        # Default date range (all dates)
        date_filter = (datetime.min.date(), datetime.max.date())
    
    # Apply filters
    filtered_df = df.copy()
    
    if channel_filter:
        filtered_df = filtered_df[filtered_df['channel'].isin(channel_filter)]
    
    if category_filter:
        filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
    
    # Apply date filter if dates are provided
    if date_filter and len(date_filter) == 2:
        start_date, end_date = date_filter
        # Convert string dates to datetime for comparison
        filtered_df['start_date_dt'] = pd.to_datetime(filtered_df['start_date'])
        filtered_df['end_date_dt'] = pd.to_datetime(filtered_df['end_date'])
        
        # Filter campaigns that overlap with the selected date range
        filtered_df = filtered_df[
            (filtered_df['start_date_dt'].dt.date <= end_date) & 
            (filtered_df['end_date_dt'].dt.date >= start_date)
        ]
        
        # Drop temporary datetime columns
        filtered_df = filtered_df.drop(['start_date_dt', 'end_date_dt'], axis=1)
    
    # Apply ROAS and ACoS filters
    if min_roas > 0:
        filtered_df = filtered_df[filtered_df['roas'] >= min_roas]
    
    if max_acos < 100:
        filtered_df = filtered_df[filtered_df['acos'] <= max_acos]
    
    # Display table
    if filtered_df.empty:
        st.warning("No campaigns match your filters. Try adjusting your criteria.")
        return
    
    # Prepare display columns
    if st.session_state.app_mode == "Advanced":
        display_df = filtered_df[[
            'uid', 'campaign_name', 'product_name', 'channel', 'category',
            'ad_spend', 'revenue', 'conversions', 'conversion_rate',
            'acos', 'roas', 'profit', 'profit_margin', 'performance_score'
        ]].copy()
    else:
        display_df = filtered_df[[
            'uid', 'campaign_name', 'product_name', 'channel', 'category',
            'ad_spend', 'revenue', 'roas', 'acos', 'profit'
        ]].copy()
    
    # Format columns for display
    display_df['ad_spend'] = display_df['ad_spend'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    display_df['revenue'] = display_df['revenue'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    display_df['roas'] = display_df['roas'].apply(lambda x: f"{x:.2f}x" if pd.notna(x) else "N/A")
    display_df['acos'] = display_df['acos'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
    display_df['profit'] = display_df['profit'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    
    if 'conversion_rate' in display_df.columns:
        display_df['conversion_rate'] = display_df['conversion_rate'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
    
    if 'profit_margin' in display_df.columns:
        display_df['profit_margin'] = display_df['profit_margin'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
    
    if 'conversions' in display_df.columns:
        display_df['conversions'] = display_df['conversions'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "N/A")
    
    # Add color-coded performance score column if in advanced mode
    if 'performance_score' in display_df.columns:
        def format_score(row):
            score = row['performance_score']
            if pd.isna(score):
                return "N/A"
            
            color = get_color_scale(score, 40, 80)
            return f"<span style='color: {color}; font-weight: bold;'>{score:.1f}</span>"
        
        display_df['performance_score'] = filtered_df.apply(format_score, axis=1)
    
    # Rename columns for display
    display_df = display_df.rename(columns={
        'campaign_name': 'Campaign',
        'product_name': 'Product',
        'channel': 'Channel',
        'category': 'Category',
        'ad_spend': 'Ad Spend',
        'revenue': 'Revenue',
        'conversions': 'Conv.',
        'conversion_rate': 'Conv. Rate',
        'acos': 'ACoS',
        'roas': 'ROAS',
        'profit': 'Profit',
        'profit_margin': 'Margin',
        'performance_score': 'Score'
    })
    
    # Hide UID column
    display_df = display_df.drop('uid', axis=1)
    
    # Display interactive table
    st.dataframe(display_df.reset_index(drop=True), 
               use_container_width=True,
               hide_index=True)
    
    # Action buttons for selected campaign
    if not filtered_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            selected_campaign = st.selectbox("Select campaign for actions:", 
                                         filtered_df['campaign_name'].tolist())
        
        selected_uid = filtered_df[filtered_df['campaign_name'] == selected_campaign]['uid'].iloc[0]
        
        with col2:
            if st.button("View Details", key="view_btn"):
                st.session_state['selected_campaign'] = selected_uid
                st.session_state['view_campaign'] = True
                st.rerun()
        
        with col3:
            if st.button("Clone", key="clone_btn"):
                success, message = analyzer.clone_campaign(selected_uid)
                if success:
                    st.success(f"Campaign cloned successfully!")
                    st.rerun()
                else:
                    st.error(message)
        
        with col4:
            if st.button("Delete", key="delete_btn"):
                if analyzer.delete_campaign(selected_uid):
                    st.success(f"Campaign '{selected_campaign}' deleted successfully.")
                    st.rerun()
                else:
                    st.error("Failed to delete campaign.")
        
        # Additional actions in advanced mode
        if st.session_state.app_mode == "Advanced":
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("What-If Analysis", key="what_if_btn"):
                    st.session_state['what_if_campaign'] = selected_uid
                    st.session_state['nav_option'] = "What-If Analysis"
                    st.rerun()
            
            with col2:
                if st.button("Run Monte Carlo", key="monte_carlo_btn"):
                    st.session_state['monte_carlo_campaign'] = selected_uid
                    st.session_state['nav_option'] = "Monte Carlo"
                    st.rerun()
            
            with col3:
                if st.button("Compare Campaigns", key="compare_btn"):
                    if 'compare_list' not in st.session_state:
                        st.session_state['compare_list'] = []
                    
                    if selected_uid not in st.session_state['compare_list']:
                        st.session_state['compare_list'].append(selected_uid)
                    
                    st.success(f"Added '{selected_campaign}' to comparison list")
                    st.session_state['nav_option'] = "Compare Campaigns"
                    st.rerun()
            
            with col4:
                # Export options for single campaign
                export_format = st.selectbox("Export Format", 
                                      ["Excel", "CSV", "PDF"],
                                      key="single_export_format")
                
                if st.button("Export", key="export_btn"):
                    # Create a subset of data with just the selected campaign
                    export_df = filtered_df[filtered_df['uid'] == selected_uid]
                    
                    if export_format == "Excel":
                        try:
                            # Create Excel file
                            excel_buffer = io.BytesIO()
                            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                                export_df.to_excel(writer, index=False, sheet_name='Campaign Details')
                                
                                # Get the workbook and worksheet objects
                                workbook = writer.book
                                worksheet = writer.sheets['Campaign Details']
                                
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
                                file_name=f"{selected_campaign.replace(' ', '_')}_report.xlsx",
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
                                file_name=f"{selected_campaign.replace(' ', '_')}_report.csv",
                                mime="text/csv"
                            )
                            
                        except Exception as e:
                            st.error(f"Error generating CSV file: {str(e)}")
                    
                    elif export_format == "PDF":
                        st.info("PDF export is coming soon. Please use Excel or CSV for now.")

def display_campaign_details(uid: str, analyzer: MarketingAnalyzer):
    """
    Display detailed view of a campaign.
    
    Args:
        uid: Campaign UID
        analyzer: MarketingAnalyzer instance
    """
    campaign = analyzer.get_campaign(uid)
    if not campaign:
        st.error("Campaign not found")
        return
    
    st.subheader(f"Campaign Details: {campaign['campaign_name']}")
    
    # Tabs for different views
    if st.session_state.app_mode == "Advanced":
        tabs = st.tabs(["Overview", "Performance Metrics", "Economics", "AI Insights"])
        
        # Overview tab
        with tabs[0]:
            display_campaign_overview(campaign)
        
        # Performance Metrics tab
        with tabs[1]:
            display_campaign_performance(campaign)
        
        # Economics tab
        with tabs[2]:
            display_campaign_economics(campaign)
        
        # AI Insights tab
        with tabs[3]:
            display_campaign_insights(campaign)
    else:
        # Simplified view for basic mode
        display_campaign_overview(campaign)
        display_campaign_performance(campaign)
    
    # Return to dashboard button
    if st.button("← Return to Dashboard"):
        st.session_state['view_campaign'] = False
        st.session_state['selected_campaign'] = None
        st.rerun()

def display_campaign_overview(campaign: Dict[str, Any]):
    """
    Display overview of campaign details.
    
    Args:
        campaign: Dictionary containing campaign data
    """
    # Basic info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**Product:** {campaign['product_name']}")
        st.markdown(f"**Channel:** {campaign['channel']}")
        st.markdown(f"**Category:** {campaign['category']}")
    
    with col2:
        st.markdown(f"**Date Range:** {campaign['start_date']} to {campaign['end_date']}")
        st.markdown(f"**Ad Spend:** ${campaign['ad_spend']:.2f}")
        st.markdown(f"**Revenue:** ${campaign['revenue']:.2f}")
    
    with col3:
        st.markdown(f"**ROAS:** {campaign['roas']:.2f}x")
        st.markdown(f"**ACoS:** {campaign['acos']:.2f}%")
        st.markdown(f"**Target ACoS:** {campaign['target_acos']:.2f}%")
    
    # Campaign summary
    st.markdown("---")
    st.markdown("### Campaign Summary")
    
    # Calculate date metrics
    try:
        start_date = datetime.strptime(campaign['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(campaign['end_date'], '%Y-%m-%d')
        campaign_days = (end_date - start_date).days + 1
        
        # Daily averages
        daily_spend = campaign['ad_spend'] / campaign_days
        daily_revenue = campaign['revenue'] / campaign_days
        daily_conversions = campaign['conversions'] / campaign_days
        
        # Display summary metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Campaign Duration:** {campaign_days} days")
            st.markdown(f"**Total Clicks:** {int(campaign['clicks']):,}")
            st.markdown(f"**Total Conversions:** {int(campaign['conversions']):,}")
            st.markdown(f"**Conversion Rate:** {campaign['conversion_rate']:.2f}%")
        
        with col2:
            st.markdown(f"**Daily Ad Spend:** ${daily_spend:.2f}")
            st.markdown(f"**Daily Revenue:** ${daily_revenue:.2f}")
            st.markdown(f"**Daily Conversions:** {daily_conversions:.1f}")
            st.markdown(f"**Total Profit:** ${campaign['profit']:.2f}")
    except Exception as e:
        st.error(f"Error calculating date metrics: {str(e)}")
    
    # Campaign notes
    if campaign['notes']:
        st.markdown("### Notes")
        st.info(campaign['notes'])
    
    # Channel-specific performance context
    channel = campaign['channel']
    if channel == "Amazon":
        # Show Amazon context
        st.markdown("### Amazon PPC Context")
        
        # Get typical benchmarks for the category
        category = campaign['category']
        category_benchmarks = {
            "Mobility": {"acos": 18, "conversion": 10, "ctr": 0.4},
            "Pain Relief": {"acos": 22, "conversion": 12, "ctr": 0.45},
            "Bathroom Safety": {"acos": 20, "conversion": 11, "ctr": 0.35},
            "Bedroom": {"acos": 19, "conversion": 9.5, "ctr": 0.38},
            "Daily Living Aids": {"acos": 21, "conversion": 10.5, "ctr": 0.42}
        }
        
        benchmark = category_benchmarks.get(category, {"acos": 20, "conversion": 10, "ctr": 0.4})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Your Performance vs. Category Benchmarks:**")
            st.markdown(f"ACoS: {campaign['acos']:.2f}% vs. {benchmark['acos']}% benchmark")
            st.markdown(f"Conversion Rate: {campaign['conversion_rate']:.2f}% vs. {benchmark['conversion']}% benchmark")
            st.markdown(f"CTR: {campaign['ctr']:.2f}% vs. {benchmark['ctr']}% benchmark")
        
        with col2:
            # Calculate ACoS performance against target
            acos_diff = campaign['target_acos'] - campaign['acos']
            acos_perf = "on target" if abs(acos_diff) < 2 else ("better than target" if acos_diff > 0 else "worse than target")
            
            st.markdown("**Performance Assessment:**")
            st.markdown(f"ACoS is {acos_perf} ({acos_diff:.2f}% {'below' if acos_diff > 0 else 'above'} target)")
            
            # ROAS assessment
            roas_assessment = "excellent" if campaign['roas'] >= 5 else ("good" if campaign['roas'] >= 3 else 
                            ("average" if campaign['roas'] >= 2 else "poor"))
            
            st.markdown(f"ROAS of {campaign['roas']:.2f}x is {roas_assessment} for Amazon PPC")
            
            # Profit margin assessment
            margin_assessment = "excellent" if campaign['profit_margin'] >= 25 else ("good" if campaign['profit_margin'] >= 15 else 
                              ("average" if campaign['profit_margin'] >= 10 else "poor"))
            
            st.markdown(f"Profit margin of {campaign['profit_margin']:.2f}% is {margin_assessment}")
    
    elif channel == "Vive Website":
        # Show website context
        st.markdown("### Website PPC Context")
        
        # Website benchmarks are different
        st.markdown("""
        **Website Performance Context:**
        - Website campaigns typically have higher CPCs but better tracking of customer journey
        - Customer acquisition through owned channels tends to have better lifetime value
        - Consider post-purchase behavior and customer retention in evaluating performance
        """)
        
        # Display website-specific metrics if available
        if 'avg_cpc' in campaign:
            st.markdown(f"**Avg. CPC:** ${campaign['avg_cpc']:.2f} (typical range for medical supplies: $1.20-$2.50)")
        
        # ROAS assessment for website is different than Amazon
        roas_assessment = "excellent" if campaign['roas'] >= 4 else ("good" if campaign['roas'] >= 2.5 else 
                        ("average" if campaign['roas'] >= 1.5 else "poor"))
        
        st.markdown(f"ROAS of {campaign['roas']:.2f}x is {roas_assessment} for Website PPC")

def display_campaign_performance(campaign: Dict[str, Any]):
    """
    Display performance metrics for a campaign.
    
    Args:
        campaign: Dictionary containing campaign data
    """
    st.markdown("### Performance Metrics")
    
    # Key metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "CTR",
            f"{campaign['ctr']:.2f}%",
            help="Click-Through Rate (Clicks ÷ Impressions)"
        )
    
    with col2:
        st.metric(
            "Conversion Rate",
            f"{campaign['conversion_rate']:.2f}%",
            help="Conversion Rate (Conversions ÷ Clicks)"
        )
    
    with col3:
        st.metric(
            "ACoS",
            f"{campaign['acos']:.2f}%",
            delta=f"{campaign['target_acos'] - campaign['acos']:.2f}%" if campaign['target_acos'] > 0 else None,
            delta_color="inverse" if campaign['target_acos'] > 0 else "normal",
            help="Advertising Cost of Sale (Ad Spend ÷ Revenue)"
        )
    
    with col4:
        st.metric(
            "ROAS",
            f"{campaign['roas']:.2f}x",
            help="Return on Ad Spend (Revenue ÷ Ad Spend)"
        )
    
    # Create conversion funnel
    st.markdown("### Conversion Funnel")
    
    # Calculate funnel metrics
    impressions = campaign['impressions']
    clicks = campaign['clicks']
    conversions = campaign['conversions']
    click_rate = campaign['ctr'] / 100
    conversion_rate = campaign['conversion_rate'] / 100
    
    # Create the funnel chart
    funnel_data = {
        'Stage': ['Impressions', 'Clicks', 'Conversions'],
        'Value': [impressions, clicks, conversions],
        'Percent': [100, click_rate * 100, click_rate * conversion_rate * 100]
    }
    
    fig_funnel = go.Figure()
    
    fig_funnel.add_trace(go.Funnel(
        name="Conversion Funnel",
        y=funnel_data['Stage'],
        x=funnel_data['Value'],
        textposition="inside",
        textinfo="value+percent initial",
        marker={"color": [COLOR_SCHEME["tertiary"], COLOR_SCHEME["secondary"], COLOR_SCHEME["primary"]]},
        connector={"line": {"color": "gray", "dash": "dot", "width": 1}}
    ))
    
    fig_funnel.update_layout(
        title="Conversion Funnel",
        height=400
    )
    
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    # Advanced metrics in advanced mode
    if st.session_state.app_mode == "Advanced":
        # Ad efficiency metrics
        st.markdown("### Ad Efficiency Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cpc = campaign['ad_spend'] / campaign['clicks'] if campaign['clicks'] > 0 else 0
            st.metric(
                "Cost per Click (CPC)",
                f"${cpc:.2f}"
            )
        
        with col2:
            cpm = (campaign['ad_spend'] / campaign['impressions']) * 1000 if campaign['impressions'] > 0 else 0
            st.metric(
                "Cost per Mille (CPM)",
                f"${cpm:.2f}"
            )
        
        with col3:
            cpa = campaign['ad_spend'] / campaign['conversions'] if campaign['conversions'] > 0 else 0
            st.metric(
                "Cost per Acquisition (CPA)",
                f"${cpa:.2f}"
            )
        
        # Performance score breakdown
        if 'performance_score' in campaign and campaign['performance_score'] is not None:
            st.markdown("### Performance Score Breakdown")
            
            # Calculate individual component scores
            roas_score = min(1, campaign['roas'] / 8) * 100  # Cap at 8x ROAS
            acos_ratio = campaign['target_acos'] / campaign['acos'] if campaign['acos'] > 0 else 2
            acos_score = min(1, acos_ratio) * 100
            conv_score = min(1, campaign['conversion_rate'] / 5) * 100  # Cap at 5% conversion rate
            margin_score = min(1, campaign['profit_margin'] / 40) * 100  # Cap at 40% profit margin
            
            # Create horizontal bar chart for score components
            score_data = {
                'Component': ['ROAS', 'ACoS vs Target', 'Conversion Rate', 'Profit Margin'],
                'Score': [roas_score, acos_score, conv_score, margin_score],
                'Weight': [35, 30, 15, 20]
            }
            
            fig_scores = px.bar(
                score_data,
                y='Component',
                x='Score',
                orientation='h',
                color='Score',
                color_continuous_scale=px.colors.sequential.Viridis,
                title=f"Performance Score Components (Overall: {campaign['performance_score']:.1f}/100)",
                labels={'Score': 'Component Score (0-100)'},
                text='Score'
            )
            
            fig_scores.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_scores.update_layout(height=300)
            
            st.plotly_chart(fig_scores, use_container_width=True)
            
            # Score interpretation
            score = campaign['performance_score']
            if score >= 80:
                st.success("This campaign is performing excellently across all key metrics!")
            elif score >= 65:
                st.info("This campaign is performing well, with some room for optimization.")
            elif score >= 50:
                st.warning("This campaign has average performance. Consider optimization strategies.")
            else:
                st.error("This campaign needs significant improvement in multiple areas.")

def display_campaign_economics(campaign: Dict[str, Any]):
    """
    Display economic analysis for a campaign.
    
    Args:
        campaign: Dictionary containing campaign data
    """
    st.markdown("### Campaign Economics")
    
    # Basic economic metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Product Cost",
            f"${campaign['product_cost']:.2f}"
        )
        st.metric(
            "Selling Price",
            f"${campaign['selling_price']:.2f}"
        )
    
    with col2:
        shipping = campaign.get('shipping_cost', 0)
        platform_fees = campaign.get('amazon_fees', 0)
        st.metric(
            "Shipping Cost",
            f"${shipping:.2f}"
        )
        st.metric(
            f"{campaign['channel']} Fees",
            f"${platform_fees:.2f}"
        )
    
    with col3:
        st.metric(
            "Profit per Sale",
            f"${campaign['profit'] / campaign['conversions'] if campaign['conversions'] > 0 else 0:.2f}"
        )
        st.metric(
            "Profit Margin",
            f"{campaign['profit_margin']:.2f}%"
        )
    
    # Calculate ad cost impact
    ad_cost_per_sale = campaign['ad_spend'] / campaign['conversions'] if campaign['conversions'] > 0 else 0
    base_profit = (campaign['selling_price'] - campaign['product_cost'] - 
                  campaign.get('shipping_cost', 0) - campaign.get('amazon_fees', 0))
    base_margin = (base_profit / campaign['selling_price']) * 100
    
    # Create waterfall chart for unit economics
    st.markdown("### Unit Economics")
    
    unit_data = {
        'Category': ['Selling Price', 'Product Cost', 'Shipping', f"{campaign['channel']} Fees",
                    'Ad Cost/Sale', 'Net Profit'],
        'Value': [campaign['selling_price'], -campaign['product_cost'], 
                 -campaign.get('shipping_cost', 0), -campaign.get('amazon_fees', 0),
                 -ad_cost_per_sale, 
                 campaign['selling_price'] - campaign['product_cost'] - 
                 campaign.get('shipping_cost', 0) - campaign.get('amazon_fees', 0) - 
                 ad_cost_per_sale]
    }
    
    # Create waterfall chart
    fig_waterfall = go.Figure(go.Waterfall(
        name="Unit Economics",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "total"],
        x=unit_data['Category'],
        textposition="outside",
        y=unit_data['Value'],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": COLOR_SCHEME["negative"]}},
        increasing={"marker": {"color": COLOR_SCHEME["positive"]}},
        totals={"marker": {"color": COLOR_SCHEME["primary"]}}
    ))
    
    fig_waterfall.update_layout(
        title="Per-Unit Economics Breakdown",
        showlegend=False,
        height=450
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # Impact of advertising on profit margin
    st.markdown("### Ad Spend Impact on Profit Margin")
    
    impact_data = {
        'Category': ['Base Margin (No Ads)', 'Margin with Ad Costs'],
        'Margin': [base_margin, campaign['profit_margin']]
    }
    
    fig_impact = px.bar(
        impact_data,
        x='Category',
        y='Margin',
        color='Category',
        title="Ad Spend Impact on Profit Margin",
        labels={'Margin': 'Profit Margin (%)'},
        text_auto='.2f',
        color_discrete_map={
            'Base Margin (No Ads)': COLOR_SCHEME["positive"],
            'Margin with Ad Costs': COLOR_SCHEME["secondary"]
        }
    )
    
    fig_impact.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_impact.update_layout(height=400)
    
    st.plotly_chart(fig_impact, use_container_width=True)
    
    # Ad Spend Optimization section in advanced mode
    if st.session_state.app_mode == "Advanced":
        st.markdown("### Ad Spend Optimization Analysis")
        
        # Create a simplified model for ad spend vs. revenue
        # This is a theoretical model assuming diminishing returns
        spend_levels = np.linspace(campaign['ad_spend'] * 0.5, campaign['ad_spend'] * 2, 10)
        
        # Simple model: revenue = k * (ad_spend)^0.7 (diminishing returns)
        # Calibrate k based on current performance
        k = campaign['revenue'] / (campaign['ad_spend'] ** 0.7)
        
        # Calculate predicted revenue and profit at different spend levels
        revenues = [k * (spend ** 0.7) for spend in spend_levels]
        
        # Calculate profits (assuming same conversion rate and profit per sale)
        profit_per_sale = campaign['profit'] / campaign['conversions'] if campaign['conversions'] > 0 else 0
        sales_at_spends = [rev / campaign['selling_price'] for rev in revenues]
        profits = [sale * profit_per_sale for sale in sales_at_spends]
        
        # Calculate ROAS for each level
        roas_levels = [rev / spend for rev, spend in zip(revenues, spend_levels)]
        
        # Create a DataFrame for plotting
        optimization_data = pd.DataFrame({
            'Ad Spend': spend_levels,
            'Predicted Revenue': revenues,
            'Predicted Profit': profits,
            'Predicted ROAS': roas_levels
        })
        
        # Find the optimal spend level (max profit)
        optimal_index = np.argmax(profits)
        optimal_spend = spend_levels[optimal_index]
        optimal_profit = profits[optimal_index]
        
        # Create the plot
        fig_opt = go.Figure()
        
        # Add revenue line
        fig_opt.add_trace(go.Scatter(
            x=optimization_data['Ad Spend'],
            y=optimization_data['Predicted Revenue'],
            mode='lines',
            name='Revenue',
            line=dict(color=COLOR_SCHEME["positive"], width=3)
        ))
        
        # Add profit line
        fig_opt.add_trace(go.Scatter(
            x=optimization_data['Ad Spend'],
            y=optimization_data['Predicted Profit'],
            mode='lines',
            name='Profit',
            line=dict(color=COLOR_SCHEME["primary"], width=3)
        ))
        
        # Add current point
        fig_opt.add_trace(go.Scatter(
            x=[campaign['ad_spend']],
            y=[campaign['profit']],
            mode='markers',
            marker=dict(color=COLOR_SCHEME["secondary"], size=12, symbol='circle'),
            name='Current'
        ))
        
        # Add optimal point
        fig_opt.add_trace(go.Scatter(
            x=[optimal_spend],
            y=[optimal_profit],
            mode='markers',
            marker=dict(color=COLOR_SCHEME["tertiary"], size=12, symbol='star'),
            name='Optimal'
        ))
        
        # Update layout
        fig_opt.update_layout(
            title="Ad Spend Optimization Curve (Theoretical Model)",
            xaxis_title="Ad Spend ($)",
            yaxis_title="Amount ($)",
            height=500
        )
        
        st.plotly_chart(fig_opt, use_container_width=True)
        
        # Optimization recommendation
        spend_diff = optimal_spend - campaign['ad_spend']
        profit_diff = optimal_profit - campaign['profit']
        
        if abs(spend_diff) / campaign['ad_spend'] > 0.1:  # If >10% difference
            if spend_diff > 0:
                st.info(f"""
                **Optimization Opportunity:**
                Based on this model, increasing ad spend by ${spend_diff:.2f} (to ${optimal_spend:.2f}) 
                could increase profit by approximately ${profit_diff:.2f} to ${optimal_profit:.2f}.
                """)
            else:
                st.info(f"""
                **Optimization Opportunity:**
                Based on this model, decreasing ad spend by ${-spend_diff:.2f} (to ${optimal_spend:.2f}) 
                could increase profit by approximately ${profit_diff:.2f} to ${optimal_profit:.2f}.
                """)
        else:
            st.success("Based on this model, your current ad spend is already near the optimal level for maximizing profit.")
        
        st.caption("""
        Note: This is a simplified model based on diminishing returns. Real-world performance may vary based on 
        market conditions, competition, and campaign optimizations.
        """)

def display_campaign_insights(campaign: Dict[str, Any]):
    """
    Display AI-powered insights for a campaign.
    
    Args:
        campaign: Dictionary containing campaign data
    """
    st.markdown("### AI-Powered Campaign Analysis")
    
    # Check if OpenAI API key is available
    api_key_status = st.session_state.get('api_key_status', None)
    
    if api_key_status == "valid":
        # Show AI insights
        with st.spinner("Generating AI-powered insights..."):
            # Get campaign insights
            insights = get_ai_campaign_insights(
                pd.DataFrame([campaign]), 
                specific_campaign=campaign['campaign_name']
            )
            
            # Display insights
            st.markdown(insights)
    
    elif api_key_status == "missing":
        st.warning("""
        OpenAI API key is missing. AI-powered insights are unavailable.
        
        To enable AI insights, add your OpenAI API key in the Streamlit secrets.
        """)
    
    elif api_key_status == "invalid":
        st.error("""
        Your OpenAI API key is invalid. AI-powered insights are unavailable.
        
        Please check your OpenAI API key and ensure it has the necessary permissions.
        """)
    
    else:
        # Check API key
        with st.spinner("Checking API key status..."):
            valid = check_openai_api_key()
            if valid:
                st.rerun()  # Refresh to show insights
            else:
                st.warning("Unable to connect to OpenAI API. AI-powered insights are unavailable.")
    
    # Manual insights section
    st.markdown("### Key Performance Indicators")
    
    # ROAS assessment
    roas = campaign['roas']
    if roas >= 4:
        roas_color = COLOR_SCHEME["positive"]
        roas_message = "Excellent ROAS, significantly above industry benchmarks"
    elif roas >= 3:
        roas_color = COLOR_SCHEME["positive"]
        roas_message = "Good ROAS, above industry benchmarks"
    elif roas >= 2:
        roas_color = COLOR_SCHEME["warning"]
        roas_message = "Average ROAS, near industry benchmarks"
    else:
        roas_color = COLOR_SCHEME["negative"]
        roas_message = "Below average ROAS, needs optimization"
    
    # ACoS assessment
    acos = campaign['acos']
    target_acos = campaign['target_acos']
    acos_diff = target_acos - acos
    
    if acos_diff >= 5:
        acos_color = COLOR_SCHEME["positive"]
        acos_message = f"ACoS is significantly better than target (${acos_diff:.2f}% below target)"
    elif acos_diff > 0:
        acos_color = COLOR_SCHEME["positive"]
        acos_message = f"ACoS is better than target (${acos_diff:.2f}% below target)"
    elif acos_diff > -5:
        acos_color = COLOR_SCHEME["warning"]
        acos_message = f"ACoS is slightly above target (${-acos_diff:.2f}% above target)"
    else:
        acos_color = COLOR_SCHEME["negative"]
        acos_message = f"ACoS is significantly above target (${-acos_diff:.2f}% above target)"
    
    # Conversion rate assessment
    conv_rate = campaign['conversion_rate']
    channel = campaign['channel']
    
    # Different benchmarks by channel
    if channel == "Amazon":
        if conv_rate >= 15:
            conv_color = COLOR_SCHEME["positive"]
            conv_message = "Excellent conversion rate for Amazon"
        elif conv_rate >= 10:
            conv_color = COLOR_SCHEME["positive"]
            conv_message = "Good conversion rate for Amazon"
        elif conv_rate >= 5:
            conv_color = COLOR_SCHEME["warning"]
            conv_message = "Average conversion rate for Amazon"
        else:
            conv_color = COLOR_SCHEME["negative"]
            conv_message = "Below average conversion rate for Amazon"
    else:
        if conv_rate >= 5:
            conv_color = COLOR_SCHEME["positive"]
            conv_message = f"Excellent conversion rate for {channel}"
        elif conv_rate >= 3:
            conv_color = COLOR_SCHEME["positive"]
            conv_message = f"Good conversion rate for {channel}"
        elif conv_rate >= 2:
            conv_color = COLOR_SCHEME["warning"]
            conv_message = f"Average conversion rate for {channel}"
        else:
            conv_color = COLOR_SCHEME["negative"]
            conv_message = f"Below average conversion rate for {channel}"
    
    # Display KPI cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 5px; background-color: {roas_color}20; border-left: 4px solid {roas_color};">
            <h4 style="margin-top: 0; color: {roas_color};">ROAS: {roas:.2f}x</h4>
            <p>{roas_message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 5px; background-color: {acos_color}20; border-left: 4px solid {acos_color};">
            <h4 style="margin-top: 0; color: {acos_color};">ACoS: {acos:.2f}%</h4>
            <p>{acos_message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 5px; background-color: {conv_color}20; border-left: 4px solid {conv_color};">
            <h4 style="margin-top: 0; color: {conv_color};">Conversion Rate: {conv_rate:.2f}%</h4>
            <p>{conv_message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Standard recommendations based on performance
    st.markdown("### Optimization Recommendations")
    
    recommendations = []
    
    # ROAS-based recommendations
    if roas < 2:
        recommendations.append(
            "**Improve ROAS:** Review keywords and pause those with high spend but low conversion rates. "
            "Focus budget on top-performing keywords and products."
        )
    
    # ACoS-based recommendations
    if acos > target_acos:
        recommendations.append(
            f"**Reduce ACoS:** Your ACoS of {acos:.2f}% is above your target of {target_acos:.2f}%. "
            "Consider adjusting bids downward on underperforming keywords and adding negative keywords."
        )
    
    # Conversion rate recommendations
    if (channel == "Amazon" and conv_rate < 10) or (channel != "Amazon" and conv_rate < 3):
        recommendations.append(
            f"**Improve Conversion Rate:** Your conversion rate of {conv_rate:.2f}% is below benchmark. "
            "Review product listings and landing pages for optimization opportunities."
        )
    
    # CTR recommendations
    if campaign['ctr'] < 0.5:
        recommendations.append(
            f"**Improve CTR:** Your click-through rate of {campaign['ctr']:.2f}% is relatively low. "
            "Consider testing new ad creatives or improving your product titles and images."
        )
    
    # Add channel-specific recommendations
    if channel == "Amazon":
        recommendations.append(
            "**Amazon-specific:** Ensure you have sufficient inventory to maintain the Buy Box. "
            "Check your pricing strategy against competitors."
        )
    elif channel == "Vive Website":
        recommendations.append(
            "**Website-specific:** Analyze the customer journey for drop-off points. "
            "Optimize landing pages and checkout process to reduce abandonment."
        )
    elif channel == "Paid Social":
        recommendations.append(
            "**Social Ads:** Refine audience targeting and test different creative formats. "
            "Social platforms typically have lower intent, so focus on engaging content."
        )
    
    # Display recommendations
    if recommendations:
        for rec in recommendations:
            st.markdown(rec)
    else:
        st.success("This campaign is performing well across all key metrics. Continue monitoring and consider small incremental optimizations.")

def display_what_if_analysis(analyzer: MarketingAnalyzer):
    """
    Interactive what-if scenario analysis for marketing campaigns.
    
    Args:
        analyzer: MarketingAnalyzer instance
    """
    st.subheader("What-If Analysis")
    
    # Get base campaign
    if not analyzer.campaigns.empty:
        # Check if a campaign is pre-selected for what-if analysis
        preselected_uid = st.session_state.get('what_if_campaign', None)
        
        # Let user select a base campaign
        campaign_names = analyzer.campaigns['campaign_name'].tolist()
        
        if preselected_uid:
            preselected_campaign = analyzer.get_campaign(preselected_uid)
            if preselected_campaign:
                default_index = campaign_names.index(preselected_campaign['campaign_name']) if preselected_campaign['campaign_name'] in campaign_names else 0
            else:
                default_index = 0
        else:
            default_index = 0
        
        base_campaign_name = st.selectbox(
            "Select base campaign for what-if analysis", 
            campaign_names,
            index=default_index
        )
        
        # Get the selected campaign
        base_campaign = analyzer.campaigns[analyzer.campaigns['campaign_name'] == base_campaign_name].iloc[0]
        
        # Set up what-if parameters with responsive layout
        st.markdown("### Adjust Parameters")
        
        # Set up tabs for different parameter groups
        tabs = st.tabs(["Ad Spend & Performance", "Pricing & Costs", "Advanced Parameters"])
        
        with tabs[0]:
            col1, col2 = st.columns(2)
            
            with col1:
                ad_spend_change = st.slider(
                    "Ad Spend Change (%)", 
                    min_value=-50, 
                    max_value=100, 
                    value=0,
                    help="Adjust monthly ad spend"
                )
                
                ctr_change = st.slider(
                    "CTR Change (%)", 
                    min_value=-25, 
                    max_value=50, 
                    value=0,
                    help="Adjust click-through rate"
                )
            
            with col2:
                conversion_rate_change = st.slider(
                    "Conversion Rate Change (%)", 
                    min_value=-25, 
                    max_value=50, 
                    value=0,
                    help="Adjust conversion rate"
                )
                
                cpc_change = st.slider(
                    "CPC Change (%)", 
                    min_value=-25, 
                    max_value=50, 
                    value=0,
                    help="Adjust cost per click"
                )
        
        with tabs[1]:
            col1, col2 = st.columns(2)
            
            with col1:
                price_change = st.slider(
                    "Price Change (%)", 
                    min_value=-25, 
                    max_value=50, 
                    value=0,
                    help="Adjust product selling price"
                )
                
                cost_change = st.slider(
                    "Product Cost Change (%)", 
                    min_value=-25, 
                    max_value=50, 
                    value=0,
                    help="Adjust product cost"
                )
            
            with col2:
                if base_campaign['channel'] == "Amazon":
                    fee_label = "Amazon Fees Change (%)"
                    fee_help = "Adjust Amazon fees (referral, FBA, etc.)"
                else:
                    fee_label = "Platform Fees Change (%)"
                    fee_help = f"Adjust {base_campaign['channel']} fees"
                
                fees_change = st.slider(
                    fee_label, 
                    min_value=-25, 
                    max_value=50, 
                    value=0,
                    help=fee_help
                )
                
                shipping_change = st.slider(
                    "Shipping Cost Change (%)", 
                    min_value=-25, 
                    max_value=50, 
                    value=0,
                    help="Adjust shipping costs"
                )
        
        with tabs[2]:
            col1, col2 = st.columns(2)
            
            with col1:
                elasticity = st.slider(
                    "Price Elasticity", 
                    min_value=0.0, 
                    max_value=2.0, 
                    value=1.0, 
                    step=0.1,
                    help="How price changes affect conversion (1.0 = proportional, >1.0 = more elastic)"
                )
                
                competition_factor = st.slider(
                    "Competition Factor", 
                    min_value=0.5, 
                    max_value=1.5, 
                    value=1.0, 
                    step=0.1,
                    help="Competitive market conditions (1.0 = normal, <1.0 = less competitive, >1.0 = more competitive)"
                )
            
            with col2:
                seasonality = st.slider(
                    "Seasonality Factor", 
                    min_value=0.5, 
                    max_value=1.5, 
                    value=1.0, 
                    step=0.1,
                    help="Seasonal impact on performance (1.0 = normal, >1.0 = peak season)"
                )
                
                quality_factor = st.slider(
                    "Quality Improvement Factor", 
                    min_value=1.0, 
                    max_value=2.0, 
                    value=1.0, 
                    step=0.1,
                    help="Impact of product quality improvements on conversion rate"
                )
        
        # Create a scenario with the adjusted parameters
        adjustments = {
            'ad_spend_change': ad_spend_change,
            'cpc_change': cpc_change,
            'ctr_change': ctr_change,
            'conversion_rate_change': conversion_rate_change,
            'price_change': price_change,
            'cost_change': cost_change
        }
        
        # Apply advanced factors
        if elasticity != 1.0 and price_change != 0:
            # Adjust conversion rate based on price elasticity
            # If price increases by 10% and elasticity is 1.5, conversions decrease by 15%
            price_impact = -1 * price_change * elasticity
            adjustments['conversion_rate_change'] += price_impact
        
        if competition_factor != 1.0:
            # Adjust CTR and CPC based on competition
            if competition_factor > 1.0:
                # Higher competition means lower CTR and higher CPC
                competition_impact = (competition_factor - 1.0) * 20  # 20% impact for each 0.1 change
                adjustments['ctr_change'] -= competition_impact
                adjustments['cpc_change'] += competition_impact
            else:
                # Lower competition means higher CTR and lower CPC
                competition_impact = (1.0 - competition_factor) * 20
                adjustments['ctr_change'] += competition_impact
                adjustments['cpc_change'] -= competition_impact
        
        if seasonality != 1.0:
            # Adjust CTR and conversion rate based on seasonality
            seasonality_impact = (seasonality - 1.0) * 30  # 30% impact for each 0.1 change
            adjustments['ctr_change'] += seasonality_impact
            adjustments['conversion_rate_change'] += seasonality_impact
        
        if quality_factor > 1.0:
            # Adjust conversion rate based on quality improvements
            quality_impact = (quality_factor - 1.0) * 50  # 50% impact for each 0.1 change
            adjustments['conversion_rate_change'] += quality_impact
        
        # Create the scenario
        scenario = analyzer.create_scenario(base_campaign['uid'], **adjustments)
        
        # Check if scenario was created successfully
        if 'error' in scenario:
            st.error(scenario['error'])
        else:
            # Display scenario comparison
            st.markdown("### Scenario Comparison")
            
            # Display key metrics comparison
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Ad Spend",
                    f"${scenario['ad_spend']:,.2f}",
                    f"{scenario['changes']['ad_spend_change']:.1f}%",
                    delta_color="inverse"  # Higher spend is negative
                )
                
                st.metric(
                    "Revenue",
                    f"${scenario['revenue']:,.2f}",
                    f"{scenario['changes']['revenue_change']:.1f}%"
                )
            
            with col2:
                st.metric(
                    "ROAS",
                    f"{scenario['roas']:.2f}x",
                    f"{scenario['changes']['roas_change']:.1f}%"
                )
                
                st.metric(
                    "ACoS",
                    f"{scenario['acos']:.2f}%",
                    f"{scenario['changes']['acos_change']:.1f}%",
                    delta_color="inverse"  # Lower ACoS is better
                )
            
            with col3:
                st.metric(
                    "Conversion Rate",
                    f"{scenario['conversion_rate']:.2f}%",
                    f"{adjustments['conversion_rate_change']:.1f}%"
                )
                
                st.metric(
                    "Conversions",
                    f"{scenario['conversions']:.0f}",
                    f"{scenario['changes']['conversions_change']:.1f}%"
                )
            
            with col4:
                st.metric(
                    "Profit",
                    f"${scenario['profit']:,.2f}",
                    f"{scenario['changes']['profit_change']:.1f}%"
                )
                
                st.metric(
                    "Profit Margin",
                    f"{scenario['profit_margin']:.2f}%",
                    f"{scenario['profit_margin'] - base_campaign['profit_margin']:.2f}%"
                )
            
            # Visualization of the comparison
            st.markdown("### Visual Comparison")
            
            # Create comparison data
            comparison_data = {
                'Metric': ['Ad Spend', 'Revenue', 'Profit', 'ROAS', 'ACoS', 'Profit Margin'],
                'Current': [
                    base_campaign['ad_spend'],
                    base_campaign['revenue'],
                    base_campaign['profit'],
                    base_campaign['roas'],
                    base_campaign['acos'],
                    base_campaign['profit_margin']
                ],
                'Projected': [
                    scenario['ad_spend'],
                    scenario['revenue'],
                    scenario['profit'],
                    scenario['roas'],
                    scenario['acos'],
                    scenario['profit_margin']
                ]
            }
            
            # Create separate dataframes for financial metrics and ratios
            financial_metrics = ['Ad Spend', 'Revenue', 'Profit']
            ratio_metrics = ['ROAS', 'ACoS', 'Profit Margin']
            
            financial_df = pd.DataFrame({
                'Metric': financial_metrics,
                'Current': [comparison_data['Current'][comparison_data['Metric'].index(m)] for m in financial_metrics],
                'Projected': [comparison_data['Projected'][comparison_data['Metric'].index(m)] for m in financial_metrics]
            })
            
            ratio_df = pd.DataFrame({
                'Metric': ratio_metrics,
                'Current': [comparison_data['Current'][comparison_data['Metric'].index(m)] for m in ratio_metrics],
                'Projected': [comparison_data['Projected'][comparison_data['Metric'].index(m)] for m in ratio_metrics]
            })
            
            # Create comparison charts
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Financial metrics chart
                financial_melted = pd.melt(
                    financial_df, 
                    id_vars=['Metric'],
                    value_vars=['Current', 'Projected'],
                    var_name='Scenario',
                    value_name='Value'
                )
                
                fig_financial = px.bar(
                    financial_melted,
                    x='Metric',
                    y='Value',
                    color='Scenario',
                    barmode='group',
                    title="Financial Metrics Comparison",
                    labels={'Value': 'Amount ($)', 'Metric': ''},
                    color_discrete_map={
                        'Current': COLOR_SCHEME["secondary"],
                        'Projected': COLOR_SCHEME["primary"]
                    }
                )
                
                # Format y-axis to show dollar amounts
                fig_financial.update_layout(
                    yaxis=dict(
                        tickprefix="$",
                        showgrid=True
                    ),
                    height=400
                )
                
                # Show values on bars
                fig_financial.update_traces(
                    texttemplate='$%{y:,.0f}',
                    textposition='outside'
                )
                
                st.plotly_chart(fig_financial, use_container_width=True)
            
            with col2:
                # Ratio metrics chart
                ratio_melted = pd.melt(
                    ratio_df, 
                    id_vars=['Metric'],
                    value_vars=['Current', 'Projected'],
                    var_name='Scenario',
                    value_name='Value'
                )
                
                fig_ratio = px.bar(
                    ratio_melted,
                    x='Metric',
                    y='Value',
                    color='Scenario',
                    barmode='group',
                    title="Ratio Metrics Comparison",
                    labels={'Value': 'Value', 'Metric': ''},
                    color_discrete_map={
                        'Current': COLOR_SCHEME["secondary"],
                        'Projected': COLOR_SCHEME["primary"]
                    }
                )
                
                # Format values based on metric
                fig_ratio.update_traces(
                    texttemplate='%{y:.2f}' + '%' if 'ACoS' in ratio_melted['Metric'].values or 'Profit Margin' in ratio_melted['Metric'].values else 'x',
                    textposition='outside'
                )
                
                fig_ratio.update_layout(height=400)
                
                st.plotly_chart(fig_ratio, use_container_width=True)
            
            # Impact analysis
            st.markdown("### Impact Analysis")
            
            # Create waterfall chart showing contribution of each factor to profit change
            base_profit = base_campaign['profit']
            new_profit = scenario['profit']
            profit_change = new_profit - base_profit
            
            # Simplistic attribution of profit change to different factors
            # This is a very simplified model and would need to be more sophisticated in a real app
            
            # Estimate impact of each factor on profit
            ad_spend_impact = -1 * (scenario['ad_spend'] - base_campaign['ad_spend'])
            
            # Conversion impact includes both rate and volume changes
            conversion_impact = (scenario['conversions'] - base_campaign['conversions']) * base_campaign['profit'] / base_campaign['conversions'] if base_campaign['conversions'] > 0 else 0
            
            # Price impact
            price_impact = scenario['conversions'] * (scenario['selling_price'] - base_campaign['selling_price'])
            
            # Cost impact (includes product cost, shipping, fees)
            cost_impact = -1 * scenario['conversions'] * ((scenario['product_cost'] - base_campaign['product_cost']) + 
                                                        (shipping_change / 100 * base_campaign.get('shipping_cost', 0)) +
                                                        (fees_change / 100 * base_campaign.get('amazon_fees', 0)))
            
            # Remaining change (interactions, etc.)
            remaining_impact = profit_change - (ad_spend_impact + conversion_impact + price_impact + cost_impact)
            
            # Create waterfall chart data
            waterfall_data = [
                {"Factor": "Base Profit", "Impact": base_profit, "Type": "Total"},
                {"Factor": "Ad Spend Change", "Impact": ad_spend_impact, "Type": "Increase" if ad_spend_impact > 0 else "Decrease"},
                {"Factor": "Conversion Changes", "Impact": conversion_impact, "Type": "Increase" if conversion_impact > 0 else "Decrease"},
                {"Factor": "Price Change", "Impact": price_impact, "Type": "Increase" if price_impact > 0 else "Decrease"},
                {"Factor": "Cost Changes", "Impact": cost_impact, "Type": "Increase" if cost_impact > 0 else "Decrease"},
                {"Factor": "Interactions & Other", "Impact": remaining_impact, "Type": "Increase" if remaining_impact > 0 else "Decrease"},
                {"Factor": "New Profit", "Impact": new_profit, "Type": "Total"}
            ]
            
            waterfall_df = pd.DataFrame(waterfall_data)
            
            # Create the waterfall chart
            fig_waterfall = go.Figure(go.Waterfall(
                name="Profit Change Analysis",
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
                title="Profit Change Attribution",
                showlegend=False,
                height=500
            )
            
            st.plotly_chart(fig_waterfall, use_container_width=True)
            
            # Recommendations based on scenario results
            st.markdown("### Recommendations")
            
            recommendations = []
            
            # Analyze results and generate recommendations
            if scenario['changes']['profit_change'] > 10:
                recommendations.append(
                    f"**Implement Changes:** This scenario projects a {scenario['changes']['profit_change']:.1f}% profit increase. "
                    "Consider implementing these changes."
                )
            elif scenario['changes']['profit_change'] > 0:
                recommendations.append(
                    f"**Test Changes:** This scenario projects a modest {scenario['changes']['profit_change']:.1f}% profit increase. "
                    "Consider A/B testing these changes before full implementation."
                )
            else:
                recommendations.append(
                    f"**Avoid These Changes:** This scenario projects a {-scenario['changes']['profit_change']:.1f}% profit decrease. "
                    "The proposed changes would likely harm campaign performance."
                )
            
            # Factor-specific recommendations
            if ad_spend_change != 0:
                if ad_spend_impact > 0:
                    recommendations.append(
                        f"**Ad Spend:** Reducing ad spend by {-ad_spend_change:.1f}% improves profitability, suggesting "
                        "current spending may be past the point of optimal returns. Consider targeted reductions."
                    )
                elif scenario['roas'] > base_campaign['roas']:
                    recommendations.append(
                        f"**Ad Spend:** Increasing ad spend by {ad_spend_change:.1f}% improves ROAS from "
                        f"{base_campaign['roas']:.2f}x to {scenario['roas']:.2f}x, suggesting good scaling potential."
                    )
            
            if price_change != 0:
                if price_impact > 0:
                    recommendations.append(
                        f"**Pricing:** The {price_change:.1f}% price increase has a positive impact on profit "
                        f"(+${price_impact:.2f}), suggesting the product has pricing power."
                    )
                else:
                    recommendations.append(
                        f"**Pricing:** The {price_change:.1f}% price change reduces profit by ${-price_impact:.2f}, "
                        "suggesting you should maintain current pricing."
                    )
            
            if conversion_rate_change != 0:
                if conversion_impact > 0:
                    recommendations.append(
                        f"**Conversion Optimization:** The {conversion_rate_change:.1f}% improvement in conversion rate "
                        f"increases profit by ${conversion_impact:.2f}. Focus on testing UI improvements, better product images, "
                        "and enhanced product descriptions."
                    )
            
            # Display recommendations
            for rec in recommendations:
                st.markdown(rec)
            
            # Option to save as new campaign
            st.markdown("### Save Scenario")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_campaign_name = st.text_input("New Campaign Name", f"{base_campaign['campaign_name']} (What-If)")
            
            with col2:
                if st.button("Save as New Campaign"):
                    # Create a new campaign name
                    if not new_campaign_name:
                        new_campaign_name = f"{base_campaign['campaign_name']} (What-If)"
                    
                    # Calculate new values for campaign creation
                    new_ad_spend = scenario['ad_spend']
                    new_clicks = scenario['clicks']
                    new_impressions = scenario['impressions']
                    new_conversions = scenario['conversions']
                    new_revenue = scenario['revenue']
                    new_product_cost = scenario['product_cost']
                    new_selling_price = scenario['selling_price']
                    
                    # Calculate new shipping and amazon fees
                    new_shipping = base_campaign.get('shipping_cost', 0) * (1 + shipping_change/100)
                    new_fees = base_campaign.get('amazon_fees', 0) * (1 + fees_change/100)
                    
                    success, message = analyzer.add_campaign(
                        new_campaign_name, base_campaign['product_name'], base_campaign['channel'],
                        base_campaign['category'], new_ad_spend, new_clicks, new_impressions,
                        new_conversions, new_revenue, base_campaign['start_date'], base_campaign['end_date'],
                        new_product_cost, new_selling_price, new_shipping, new_fees,
                        base_campaign['target_acos'], f"What-if scenario based on {base_campaign['campaign_name']}"
                    )
                    
                    if success:
                        st.success(f"What-if scenario saved as '{new_campaign_name}'!")
                        # Clear the preselected campaign since we've now used it
                        if 'what_if_campaign' in st.session_state:
                            del st.session_state['what_if_campaign']
                        st.rerun()
                    else:
                        st.error(message)
    else:
        st.info("Add campaigns first to use the what-if analysis tool.")

def display_monte_carlo_simulation(analyzer: MarketingAnalyzer):
    """
    Display Monte Carlo simulation for a campaign.
    
    Args:
        analyzer: MarketingAnalyzer instance
    """
    st.subheader("Monte Carlo Simulation")
    
    # Check if we have a selected campaign
    if 'monte_carlo_campaign' in st.session_state:
        campaign_uid = st.session_state['monte_carlo_campaign']
        campaign = analyzer.get_campaign(campaign_uid)
        
        if not campaign:
            st.error("Selected campaign not found. Please select another campaign.")
            if st.button("Return to Dashboard"):
                st.session_state.pop('monte_carlo_campaign', None)
                st.session_state['nav_option'] = "Campaign Dashboard"
                st.rerun()
            return
        
        st.markdown(f"### Monte Carlo Analysis: {campaign['campaign_name']}")
        
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
            ad_spend_variation = st.slider("Ad Spend Variation (%)", 
                               min_value=5, 
                               max_value=50, 
                               value=20)
            
            ctr_variation = st.slider("CTR Variation (%)", 
                           min_value=5, 
                           max_value=50, 
                           value=15)
        
        with col2:
            conversion_variation = st.slider("Conversion Rate Variation (%)", 
                                   min_value=5, 
                                   max_value=50, 
                                   value=25)
            
            cpc_variation = st.slider("CPC Variation (%)", 
                           min_value=5, 
                           max_value=50, 
                           value=15)
        
        with col3:
            price_variation = st.slider("Selling Price Variation (%)", 
                             min_value=5, 
                             max_value=25, 
                             value=5)
            
            cost_variation = st.slider("Product Cost Variation (%)", 
                            min_value=5, 
                            max_value=25, 
                            value=10)
        
        # Create parameter variations dictionary
        param_variations = {
            'ad_spend': ad_spend_variation,
            'ctr': ctr_variation,
            'conversion_rate': conversion_variation,
            'avg_cpc': cpc_variation,
            'selling_price': price_variation,
            'product_cost': cost_variation
        }
        
        # Run simulation button
        if st.button("Run Monte Carlo Simulation"):
            with st.spinner(f"Running {num_simulations} simulations..."):
                # Show progress bar
                progress_bar = st.progress(0)
                
                # Run simulation
                results, message = analyzer.run_monte_carlo_simulation(
                    campaign_uid, 
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
                results = results.dropna(subset=['roas', 'profit'])
                
                # Calculate statistics for key metrics
                roas_mean = results['roas'].mean()
                roas_std = results['roas'].std()
                roas_ci_lower = roas_mean - z_score * roas_std / np.sqrt(len(results))
                roas_ci_upper = roas_mean + z_score * roas_std / np.sqrt(len(results))
                
                acos_mean = results['acos'].mean()
                acos_std = results['acos'].std()
                acos_ci_lower = acos_mean - z_score * acos_std / np.sqrt(len(results))
                acos_ci_upper = acos_mean + z_score * acos_std / np.sqrt(len(results))
                
                profit_mean = results['profit'].mean()
                profit_std = results['profit'].std()
                profit_ci_lower = profit_mean - z_score * profit_std / np.sqrt(len(results))
                profit_ci_upper = profit_mean + z_score * profit_std / np.sqrt(len(results))
                
                # Display summary statistics
                st.markdown("### Simulation Results")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Mean ROAS", f"{roas_mean:.2f}x")
                    st.caption(f"{confidence_interval} CI: [{roas_ci_lower:.2f}x, {roas_ci_upper:.2f}x]")
                
                with col2:
                    st.metric("Mean ACoS", f"{acos_mean:.2f}%")
                    st.caption(f"{confidence_interval} CI: [{acos_ci_lower:.2f}%, {acos_ci_upper:.2f}%]")
                
                with col3:
                    st.metric("Mean Profit", f"${profit_mean:.2f}")
                    st.caption(f"{confidence_interval} CI: [${profit_ci_lower:.2f}, ${profit_ci_upper:.2f}]")
                
                # Probability of success metrics
                st.markdown("### Probability Analysis")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    prob_positive_roi = (results['roas'] > 1).mean() * 100
                    st.metric("Probability of Positive ROI", f"{prob_positive_roi:.1f}%")
                
                with col2:
                    target_acos = campaign['target_acos']
                    prob_target_acos = (results['acos'] <= target_acos).mean() * 100
                    st.metric(f"Probability of ACoS ≤ {target_acos:.1f}%", f"{prob_target_acos:.1f}%")
                
                with col3:
                    target_roas = 3  # Example target ROAS of 3x
                    prob_target_roas = (results['roas'] >= target_roas).mean() * 100
                    st.metric(f"Probability of ROAS ≥ {target_roas:.1f}x", f"{prob_target_roas:.1f}%")
                
                # Distribution charts
                st.markdown("### Distribution Analysis")
                
                # ROAS Distribution
                fig_roas_dist = px.histogram(
                    results, 
                    x="roas",
                    nbins=50,
                    title="ROAS Distribution",
                    labels={"roas": "Return on Ad Spend (ROAS)"},
                    color_discrete_sequence=[COLOR_SCHEME["primary"]]
                )
                
                # Add vertical lines for confidence interval
                fig_roas_dist.add_vline(x=roas_ci_lower, line_dash="dash", line_color=COLOR_SCHEME["warning"])
                fig_roas_dist.add_vline(x=roas_ci_upper, line_dash="dash", line_color=COLOR_SCHEME["warning"])
                
                # Add vertical line for mean
                fig_roas_dist.add_vline(x=roas_mean, line_color=COLOR_SCHEME["secondary"])
                
                # Add vertical line for original campaign
                fig_roas_dist.add_vline(x=campaign['roas'], line_color=COLOR_SCHEME["positive"],
                                     annotation_text="Original Value")
                
                st.plotly_chart(fig_roas_dist, use_container_width=True)
                
                # ACoS Distribution
                fig_acos_dist = px.histogram(
                    results, 
                    x="acos",
                    nbins=50,
                    title="ACoS Distribution",
                    labels={"acos": "Advertising Cost of Sale (ACoS)"},
                    color_discrete_sequence=[COLOR_SCHEME["primary"]]
                )
                
                # Add vertical lines for confidence interval
                fig_acos_dist.add_vline(x=acos_ci_lower, line_dash="dash", line_color=COLOR_SCHEME["warning"])
                fig_acos_dist.add_vline(x=acos_ci_upper, line_dash="dash", line_color=COLOR_SCHEME["warning"])
                
                # Add vertical line for mean
                fig_acos_dist.add_vline(x=acos_mean, line_color=COLOR_SCHEME["secondary"])
                
                # Add vertical line for original campaign
                fig_acos_dist.add_vline(x=campaign['acos'], line_color=COLOR_SCHEME["positive"],
                                     annotation_text="Original Value")
                
                # Add vertical line for target ACoS
                fig_acos_dist.add_vline(x=target_acos, line_color=COLOR_SCHEME["negative"], line_dash="dot",
                                     annotation_text=f"Target ACoS ({target_acos}%)")
                
                st.plotly_chart(fig_acos_dist, use_container_width=True)
                
                # Scatter plot of ROAS vs ACoS
                fig_scatter = px.scatter(
                    results,
                    x="acos",
                    y="roas",
                    color="profit",
                    color_continuous_scale=px.colors.sequential.Viridis,
                    title="ROAS vs. ACoS by Profit",
                    labels={
                        "acos": "ACoS (%)",
                        "roas": "ROAS",
                        "profit": "Profit ($)"
                    },
                )
                
                # Add horizontal line for target ROAS
                fig_scatter.add_hline(y=target_roas, line_color=COLOR_SCHEME["warning"], line_dash="dot",
                                    annotation_text=f"Target ROAS ({target_roas}x)")
                
                # Add vertical line for target ACoS
                fig_scatter.add_vline(x=target_acos, line_color=COLOR_SCHEME["warning"], line_dash="dot",
                                    annotation_text=f"Target ACoS ({target_acos}%)")
                
                # Add point for original campaign
                fig_scatter.add_trace(go.Scatter(
                    x=[campaign['acos']],
                    y=[campaign['roas']],
                    mode="markers",
                    marker=dict(
                        size=15,
                        color=COLOR_SCHEME["positive"],
                        symbol="star"
                    ),
                    name="Original Campaign"
                ))
                
                st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Correlation analysis
                st.markdown("### Parameter Sensitivity Analysis")
                
                # Create correlation matrix
                corr_cols = ['ad_spend', 'ctr', 'conversion_rate', 'avg_cpc', 
                           'roas', 'acos', 'profit', 'profit_margin']
                
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
                # Calculate correlation with ROAS
                roas_corr = corr_matrix['roas'].drop('roas').sort_values(ascending=False)
                
                # Create tornado chart
                fig_tornado = go.Figure()
                
                # Add bars
                fig_tornado.add_trace(go.Bar(
                    y=roas_corr.index,
                    x=roas_corr.values,
                    orientation='h',
                    marker_color=[COLOR_SCHEME["positive"] if x > 0 else COLOR_SCHEME["negative"] for x in roas_corr.values]
                ))
                
                # Add vertical line at 0
                fig_tornado.add_shape(
                    type="line",
                    x0=0, y0=-0.5,
                    x1=0, y1=len(roas_corr) - 0.5,
                    line=dict(color="black", width=2)
                )
                
                # Update layout
                fig_tornado.update_layout(
                    title="Parameter Impact on ROAS",
                    xaxis_title="Correlation with ROAS",
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
                
                # ACoS insights
                if prob_target_acos < 50:
                    insights.append(f"**ACoS Risk:** Only a {prob_target_acos:.1f}% chance of meeting your target ACoS of {target_acos:.1f}%.")
                elif prob_target_acos > 90:
                    insights.append(f"**Strong ACoS Performance:** {prob_target_acos:.1f}% chance of meeting your target ACoS of {target_acos:.1f}%.")
                
                # Parameter sensitivity insights
                most_positive = roas_corr.idxmax()
                most_negative = roas_corr.idxmin()
                
                insights.append(f"**Key Driver:** {most_positive} has the strongest positive impact on ROAS.")
                insights.append(f"**Risk Factor:** {most_negative} has the strongest negative impact on ROAS.")
                
                # Compare to original value
                roas_diff_pct = ((roas_mean - campaign['roas']) / campaign['roas']) * 100
                if abs(roas_diff_pct) > 10:
                    if roas_diff_pct > 0:
                        insights.append(f"**Optimistic Outlook:** Monte Carlo average ROAS of {roas_mean:.2f}x is {roas_diff_pct:.1f}% higher than your current ROAS of {campaign['roas']:.2f}x.")
                    else:
                        insights.append(f"**Cautious Outlook:** Monte Carlo average ROAS of {roas_mean:.2f}x is {-roas_diff_pct:.1f}% lower than your current ROAS of {campaign['roas']:.2f}x.")
                
                # Display insights
                for insight in insights:
                    st.markdown(insight)
                
                # Display recommendations
                st.markdown("#### Recommendations")
                
                recommendations = []
                
                # Generate recommendations based on insights
                if prob_positive_roi < 75:
                    recommendations.append("Consider revising the campaign parameters to improve ROI or reduce risk.")
                
                if "conversion_rate" in most_positive:
                    recommendations.append("Focus on improving conversion rate, as this has the strongest impact on ROAS. Test landing page improvements and better product images.")
                
                if "avg_cpc" in most_negative:
                    recommendations.append("Monitor CPC closely and look for ways to reduce it through better keyword targeting and bid optimization.")
                
                if "ad_spend" in most_negative:
                    recommendations.append("Consider testing lower ad spend to potentially improve overall ROAS.")
                
                # Add general recommendation
                recommendations.append(f"Set up monitoring to track actual performance against the {confidence_interval} confidence intervals found in this simulation.")
                
                # Add channel-specific recommendations
                if campaign['channel'] == "Amazon":
                    recommendations.append("For Amazon campaigns, test automatic targeting alongside manual targeting to potentially discover new high-performing keywords.")
                elif campaign['channel'] == "Vive Website":
                    recommendations.append("For website traffic, implement UTM parameters and conversion tracking to more accurately attribute performance.")
                
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
                    file_name=f"monte_carlo_{campaign['campaign_name'].replace(' ', '_')}.csv",
                    mime="text/csv"
                )
                
                # Option to save as a new campaign
                st.markdown("### Save as New Campaign")
                new_name = st.text_input("New Campaign Name", f"{campaign['campaign_name']} (Monte Carlo)")
                
                if st.button("Save Mean Values as New Campaign"):
                    # Calculate mean values from simulation
                    mean_ad_spend = campaign['ad_spend']  # Keep original ad spend
                    mean_avg_cpc = results['avg_cpc'].mean()
                    mean_ctr = results['ctr'].mean()
                    
                    # Calculate other metrics
                    mean_conversions = results['conversions'].mean()
                    mean_clicks = results['clicks'].mean()
                    mean_impressions = (mean_clicks * 100) / mean_ctr if mean_ctr > 0 else campaign['impressions']
                    mean_revenue = results['revenue'].mean()
                    
                    # Create new campaign with mean values
                    success, message = analyzer.add_campaign(
                        new_name, campaign['product_name'], campaign['channel'],
                        campaign['category'], mean_ad_spend, mean_clicks, mean_impressions,
                        mean_conversions, mean_revenue, campaign['start_date'], campaign['end_date'],
                        campaign['product_cost'], campaign['selling_price'], campaign['shipping_cost'],
                        campaign['amazon_fees'], campaign['target_acos'],
                        f"Monte Carlo simulation based on {campaign['campaign_name']} with {num_simulations} simulations"
                    )
                    
                    if success:
                        st.success(f"Monte Carlo scenario saved as '{new_name}'!")
                        # Clear the preselected campaign
                        if 'monte_carlo_campaign' in st.session_state:
                            del st.session_state['monte_carlo_campaign']
                        st.rerun()
                    else:
                        st.error(message)
        
        # Display info about Monte Carlo simulation if no simulation has been run yet
        else:
            st.info("""
            ### About Monte Carlo Simulation
            
            Monte Carlo simulation is a powerful technique that runs thousands of scenarios with varied inputs to understand the range of possible outcomes and their probabilities.
            
            **Benefits:**
            - Reveals the probability distribution of key metrics like ROAS and ACoS
            - Identifies which parameters have the greatest impact on outcomes
            - Helps quantify and manage risk in marketing campaigns
            - Provides confidence intervals for more realistic forecasting
            
            Click the "Run Monte Carlo Simulation" button to analyze this campaign using the parameter variations you've set.
            """)
    
    else:
        st.info("Please select a campaign for Monte Carlo simulation from the Dashboard.")
        
        # Display sample results for demonstration
        if st.button("Show Demo Simulation"):
            st.markdown("### Sample Simulation Results")
            
            # Create sample data
            np.random.seed(42)  # For reproducible results
            sample_size = 1000
            
            # Sample ROAS data
            sample_roas = np.random.normal(3.5, 1.2, sample_size)
            
            # Sample ACoS data 
            sample_acos = np.random.normal(22, 5, sample_size)
            
            # Sample profit data
            sample_profit = np.random.normal(2000, 500, sample_size)
            
            # Create sample dataframe
            sample_results = pd.DataFrame({
                'roas': sample_roas,
                'acos': sample_acos,
                'profit': sample_profit
            })
            
            # Display sample statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Mean ROAS", f"{sample_results['roas'].mean():.2f}x")
                st.caption("95% CI: [3.42x, 3.58x]")
            
            with col2:
                st.metric("Mean ACoS", f"{sample_results['acos'].mean():.2f}%")
                st.caption("95% CI: [21.65%, 22.35%]")
            
            with col3:
                st.metric("Mean Profit", f"${sample_results['profit'].mean():.2f}")
                st.caption("95% CI: [$1,964.00, $2,036.00]")
            
            # Sample distribution chart
            fig_sample = px.histogram(
                sample_results, 
                x="roas",
                nbins=30,
                title="Sample ROAS Distribution",
                labels={"roas": "Return on Ad Spend (ROAS)"},
                color_discrete_sequence=[COLOR_SCHEME["primary"]]
            )
            
            # Add vertical lines for 95% confidence interval
            ci_lower = sample_results['roas'].mean() - 1.96 * sample_results['roas'].std() / np.sqrt(len(sample_results))
            ci_upper = sample_results['roas'].mean() + 1.96 * sample_results['roas'].std() / np.sqrt(len(sample_results))
            
            fig_sample.add_vline(x=ci_lower, line_dash="dash", line_color=COLOR_SCHEME["warning"])
            fig_sample.add_vline(x=ci_upper, line_dash="dash", line_color=COLOR_SCHEME["warning"])
            
            # Add vertical line for mean
            fig_sample.add_vline(x=sample_results['roas'].mean(), line_color=COLOR_SCHEME["secondary"])
            
            st.plotly_chart(fig_sample, use_container_width=True)
            
            st.info("This is a demonstration using sample data. Select a real campaign from the Dashboard to run a simulation on your own data.")

def display_campaign_comparison(analyzer: MarketingAnalyzer):
    """
    Display comparison between multiple campaigns.
    
    Args:
        analyzer: MarketingAnalyzer instance
    """
    st.subheader("Campaign Comparison")
    
    # Get comparison list
    if 'compare_list' not in st.session_state:
        st.session_state['compare_list'] = []
    
    compare_list = st.session_state['compare_list']
    
    # If no campaigns in compare list, let user select them
    if not compare_list:
        # Get list of campaigns
        if not analyzer.campaigns.empty:
            campaign_options = analyzer.campaigns[['uid', 'campaign_name']].copy()
            
            st.info("Please select campaigns to compare.")
            
            # Let user select campaigns
            selected_campaigns = st.multiselect(
                "Select campaigns to compare",
                options=campaign_options['campaign_name'].tolist(),
                help="Select at least 2 campaigns to compare them"
            )
            
            # Add selected campaigns to compare list
            if selected_campaigns:
                compare_list = []
                for campaign in selected_campaigns:
                    uid = campaign_options[campaign_options['campaign_name'] == campaign]['uid'].iloc[0]
                    compare_list.append(uid)
                
                st.session_state['compare_list'] = compare_list
                
                # If we have at least 2 campaigns, show comparison button
                if len(compare_list) >= 2:
                    if st.button("Compare Selected Campaigns"):
                        st.rerun()
        else:
            st.warning("No campaigns available. Please add campaigns first.")
            return
    
    # Show comparison if we have campaigns in compare list
    if len(compare_list) >= 2:
        # Get campaign data
        comparison_data = []
        
        for uid in compare_list:
            campaign = analyzer.get_campaign(uid)
            if campaign:
                comparison_data.append(campaign)
        
        # Convert to dataframe for easier comparison
        comparison_df = pd.DataFrame(comparison_data)
        
        # Show campaigns being compared
        st.markdown("### Comparing Campaigns")
        
        # Show campaign names
        campaign_names = comparison_df['campaign_name'].tolist()
        st.markdown(", ".join([f"**{name}**" for name in campaign_names]))
        
        # Actions
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear Comparison List"):
                st.session_state['compare_list'] = []
                st.rerun()
        
        with col2:
            if st.button("Add More Campaigns"):
                st.session_state['compare_list'] = []  # Clear to restart
                st.rerun()
        
        # Basic comparison table
        st.markdown("### Key Metrics Comparison")
        
        # Select columns to compare
        basic_cols = ['campaign_name', 'channel', 'product_name', 'ad_spend', 
                    'conversions', 'revenue', 'roas', 'acos', 'profit', 'profit_margin']
        
        basic_comparison = comparison_df[basic_cols].copy()
        
        # Format columns
        basic_comparison['ad_spend'] = basic_comparison['ad_spend'].apply(lambda x: f"${x:,.2f}")
        basic_comparison['revenue'] = basic_comparison['revenue'].apply(lambda x: f"${x:,.2f}")
        basic_comparison['conversions'] = basic_comparison['conversions'].apply(lambda x: f"{int(x):,}")
        basic_comparison['roas'] = basic_comparison['roas'].apply(lambda x: f"{x:.2f}x")
        basic_comparison['acos'] = basic_comparison['acos'].apply(lambda x: f"{x:.2f}%")
        basic_comparison['profit'] = basic_comparison['profit'].apply(lambda x: f"${x:,.2f}")
        basic_comparison['profit_margin'] = basic_comparison['profit_margin'].apply(lambda x: f"{x:.2f}%")
        
        # Rename columns
        basic_comparison = basic_comparison.rename(columns={
            'campaign_name': 'Campaign',
            'channel': 'Channel',
            'product_name': 'Product',
            'ad_spend': 'Ad Spend',
            'conversions': 'Conversions',
            'revenue': 'Revenue',
            'roas': 'ROAS',
            'acos': 'ACoS',
            'profit': 'Profit',
            'profit_margin': 'Margin'
        })
        
        # Display table
        st.dataframe(basic_comparison, use_container_width=True, hide_index=True)
        
        # Visual comparison
        st.markdown("### Visual Comparison")
        
        # ROAS and ACoS comparison
        col1, col2 = st.columns(2)
        
        with col1:
            # ROAS Bar Chart
            roas_data = comparison_df[['campaign_name', 'roas']].copy()
            
            fig_roas = px.bar(
                roas_data,
                x='campaign_name',
                y='roas',
                title="ROAS Comparison",
                labels={
                    'campaign_name': 'Campaign',
                    'roas': 'Return on Ad Spend (ROAS)'
                },
                color='roas',
                color_continuous_scale=px.colors.sequential.Viridis
            )
            
            # Add target line
            fig_roas.add_hline(y=3, line_dash="dot", line_color=COLOR_SCHEME["warning"],
                             annotation_text="3x ROAS Target")
            
            # Show values on bars
            fig_roas.update_traces(
                texttemplate='%{y:.2f}x',
                textposition='outside'
            )
            
            st.plotly_chart(fig_roas, use_container_width=True)
        
        with col2:
            # ACoS Bar Chart
            acos_data = comparison_df[['campaign_name', 'acos', 'target_acos']].copy()
            
            fig_acos = px.bar(
                acos_data,
                x='campaign_name',
                y='acos',
                title="ACoS Comparison",
                labels={
                    'campaign_name': 'Campaign',
                    'acos': 'Advertising Cost of Sale (ACoS)'
                },
                color='acos',
                color_continuous_scale=px.colors.sequential.Viridis_r  # Reversed so lower is better
            )
            
            # Show values on bars
            fig_acos.update_traces(
                texttemplate='%{y:.2f}%',
                textposition='outside'
            )
            
            # Add target lines for each campaign
            for i, row in acos_data.iterrows():
                fig_acos.add_shape(
                    type="line",
                    x0=i-0.4, x1=i+0.4,
                    y0=row['target_acos'], y1=row['target_acos'],
                    line=dict(color=COLOR_SCHEME["warning"], width=2, dash="dot")
                )
            
            st.plotly_chart(fig_acos, use_container_width=True)
        
        # Financial metrics comparison
        col1, col2 = st.columns(2)
        
        with col1:
            # Ad Spend vs. Revenue
            finance_data = comparison_df[['campaign_name', 'ad_spend', 'revenue', 'profit']].copy()
            
            # Reshape for grouped bar chart
            finance_melted = pd.melt(
                finance_data, 
                id_vars=['campaign_name'],
                value_vars=['ad_spend', 'revenue', 'profit'],
                var_name='Metric',
                value_name='Amount'
            )
            
            # Rename for display
            finance_melted['Metric'] = finance_melted['Metric'].map({
                'ad_spend': 'Ad Spend',
                'revenue': 'Revenue',
                'profit': 'Profit'
            })
            
            fig_finance = px.bar(
                finance_melted,
                x='campaign_name',
                y='Amount',
                color='Metric',
                barmode='group',
                title="Financial Metrics Comparison",
                labels={
                    'campaign_name': 'Campaign',
                    'Amount': 'Amount ($)',
                    'Metric': 'Metric'
                },
                color_discrete_map={
                    'Ad Spend': COLOR_SCHEME["negative"],
                    'Revenue': COLOR_SCHEME["positive"],
                    'Profit': COLOR_SCHEME["secondary"]
                }
            )
            
            # Format y-axis to show dollar amounts
            fig_finance.update_layout(
                yaxis=dict(
                    tickprefix="$",
                    showgrid=True
                )
            )
            
            st.plotly_chart(fig_finance, use_container_width=True)
        
        with col2:
            # Conversion Rate and Profit Margin
            performance_data = comparison_df[['campaign_name', 'conversion_rate', 'profit_margin']].copy()
            
            # Reshape for grouped bar chart
            performance_melted = pd.melt(
                performance_data,
                id_vars=['campaign_name'],
                value_vars=['conversion_rate', 'profit_margin'],
                var_name='Metric',
                value_name='Percentage'
            )
            
            # Rename for display
            performance_melted['Metric'] = performance_melted['Metric'].map({
                'conversion_rate': 'Conversion Rate',
                'profit_margin': 'Profit Margin'
            })
            
            fig_performance = px.bar(
                performance_melted,
                x='campaign_name',
                y='Percentage',
                color='Metric',
                barmode='group',
                title="Performance Metrics Comparison",
                labels={
                    'campaign_name': 'Campaign',
                    'Percentage': 'Percentage (%)',
                    'Metric': 'Metric'
                },
                color_discrete_map={
                    'Conversion Rate': COLOR_SCHEME["tertiary"],
                    'Profit Margin': COLOR_SCHEME["secondary"]
                }
            )
            
            # Show values on bars
            fig_performance.update_traces(
                texttemplate='%{y:.2f}%',
                textposition='outside'
            )
            
            st.plotly_chart(fig_performance, use_container_width=True)
        
        # Spider/Radar chart comparison in advanced mode
        if st.session_state.app_mode == "Advanced":
            st.markdown("### Multi-Dimensional Comparison")
            
            # Prepare data for radar chart
            radar_metrics = ['roas', 'conversion_rate', 'profit_margin', 'ctr']
            radar_labels = ['ROAS', 'Conversion Rate', 'Profit Margin', 'CTR']
            
            # We need to normalize the values for the radar chart
            radar_data = comparison_df[['campaign_name'] + radar_metrics].copy()
            
            # Replace NaN with 0
            radar_data = radar_data.fillna(0)
            
            # Normalize each metric to 0-100 scale
            for metric in radar_metrics:
                if radar_data[metric].max() > 0:
                    radar_data[metric] = 100 * radar_data[metric] / radar_data[metric].max()
            
            # Create radar chart
            fig_radar = go.Figure()
            
            # Add a trace for each campaign
            colors = px.colors.qualitative.Plotly
            for i, (_, row) in enumerate(radar_data.iterrows()):
                fig_radar.add_trace(go.Scatterpolar(
                    r=[row[m] for m in radar_metrics],
                    theta=radar_labels,
                    fill='toself',
                    name=row['campaign_name'],
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
            
            # ROI vs. ACoS Scatter Plot
            roi_acos_data = comparison_df[['campaign_name', 'roas', 'acos', 'profit', 'conversion_rate']].copy()
            
            if not roi_acos_data.empty:
                fig_scatter = px.scatter(
                    roi_acos_data,
                    x='acos',
                    y='roas',
                    size='profit',
                    color='conversion_rate',
                    hover_name='campaign_name',
                    size_max=50,
                    title="ROAS vs. ACoS with Profit & Conversion Rate",
                    labels={
                        'acos': 'ACoS (%)',
                        'roas': 'ROAS',
                        'profit': 'Profit ($)',
                        'conversion_rate': 'Conversion Rate (%)'
                    },
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                
                # Add quadrant lines
                fig_scatter.add_hline(y=3, line_dash="dash", line_color="gray")
                fig_scatter.add_vline(x=25, line_dash="dash", line_color="gray")
                
                # Add quadrant labels
                fig_scatter.add_annotation(
                    x=12.5, y=4.5,
                    text="IDEAL: High ROAS, Low ACoS",
                    showarrow=False,
                    font=dict(color="green", size=10)
                )
                
                fig_scatter.add_annotation(
                    x=37.5, y=4.5,
                    text="GOOD: High ROAS, High ACoS",
                    showarrow=False,
                    font=dict(color="blue", size=10)
                )
                
                fig_scatter.add_annotation(
                    x=12.5, y=1.5,
                    text="CONSIDER: Low ROAS, Low ACoS",
                    showarrow=False,
                    font=dict(color="orange", size=10)
                )
                
                fig_scatter.add_annotation(
                    x=37.5, y=1.5,
                    text="AVOID: Low ROAS, High ACoS",
                    showarrow=False,
                    font=dict(color="red", size=10)
                )
                
                # Update layout
                fig_scatter.update_layout(height=600)
                
                st.plotly_chart(fig_scatter, use_container_width=True)
        
        # AI-powered comparison insights
        if st.session_state.app_mode == "Advanced":
            st.markdown("### AI-Powered Comparison Insights")
            
            # Check if OpenAI API key is available
            api_key_status = st.session_state.get('api_key_status', None)
            
            if api_key_status == "valid":
                # Show AI insights
                with st.spinner("Generating AI-powered comparison insights..."):
                    # Get comparison insights
                    insights = get_ai_campaign_insights(comparison_df)
                    
                    # Display insights
                    st.markdown(insights)
            else:
                st.info("""
                AI-powered comparison insights are available with a valid OpenAI API key.
                Go to Settings to configure your API key.
                """)
        
        # Export comparison
        st.markdown("### Export Comparison")
        export_format = st.selectbox("Export Format", ["Excel", "CSV", "PDF"])
        
        if st.button("Export Comparison"):
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
                    file_name="campaign_comparison.xlsx",
                    mime="application/vnd.ms-excel"
                )
            
            elif export_format == "CSV":
                # Create CSV
                csv_data = comparison_df.to_csv(index=False).encode('utf-8')
                
                # Create download button
                st.download_button(
                    label="Download CSV Comparison",
                    data=csv_data,
                    file_name="campaign_comparison.csv",
                    mime="text/csv"
                )
            
            elif export_format == "PDF":
                st.info("PDF export is coming soon. Please use Excel or CSV for now.")
    else:
        st.info("Please select at least 2 campaigns to compare.")

def display_dashboard(analyzer: MarketingAnalyzer):
    """
    Display main marketing dashboard with key metrics and visualizations.
    
    Args:
        analyzer: MarketingAnalyzer instance
    """
    st.subheader("Marketing Performance Dashboard")
    
    # Check if we have campaigns
    if analyzer.campaigns.empty:
        st.info("No campaigns found. Add campaigns to see dashboard.")
        
        # Add example campaigns button
        if st.button("Load Example Campaigns"):
            count = analyzer.add_example_campaigns()
            st.success(f"Added {count} example campaigns!")
            st.rerun()
        return
    
    # Get aggregate statistics
    stats = analyzer.get_channel_statistics()
    
    # Key metrics
    st.markdown("### Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Ad Spend", 
            f"${stats['total_spend']:,.2f}"
        )
    
    with col2:
        st.metric(
            "Overall ROAS", 
            f"{stats['overall_roas']:.2f}x"
        )
    
    with col3:
        st.metric(
            "Overall ACoS", 
            f"{stats['overall_acos']:.2f}%"
        )
    
    with col4:
        st.metric(
            "Total Profit", 
            f"${stats['total_profit']:,.2f}"
        )
    
    # Channel performance comparison
    st.markdown("### Channel Performance")
    
    if stats['channels']:
        # Create Channel comparison data
        channel_data = pd.DataFrame(stats['channels'])
        
        # Create visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # ROAS by Channel bar chart
            fig_roas = px.bar(
                channel_data,
                x='name',
                y='roas',
                title="ROAS by Channel",
                labels={
                    'name': 'Channel',
                    'roas': 'ROAS'
                },
                color='name',
                color_discrete_map={c['name']: get_channel_color(c['name']) for c in stats['channels']}
            )
            
            # Add target line for good ROAS
            fig_roas.add_hline(y=3, line_dash="dot", line_color=COLOR_SCHEME["warning"],
                             annotation_text="Good ROAS (3x)")
            
            # Show values on bars
            fig_roas.update_traces(
                texttemplate='%{y:.2f}x',
                textposition='outside'
            )
            
            # Hide legend
            fig_roas.update_layout(showlegend=False)
            
            st.plotly_chart(fig_roas, use_container_width=True)
        
        with col2:
            # ACoS by Channel bar chart
            fig_acos = px.bar(
                channel_data,
                x='name',
                y='acos',
                title="ACoS by Channel",
                labels={
                    'name': 'Channel',
                    'acos': 'ACoS (%)'
                },
                color='name',
                color_discrete_map={c['name']: get_channel_color(c['name']) for c in stats['channels']}
            )
            
            # Add target line for good ACoS
            fig_acos.add_hline(y=25, line_dash="dot", line_color=COLOR_SCHEME["warning"],
                             annotation_text="Target ACoS (25%)")
            
            # Show values on bars
            fig_acos.update_traces(
                texttemplate='%{y:.2f}%',
                textposition='outside'
            )
            
            # Hide legend
            fig_acos.update_layout(showlegend=False)
            
            st.plotly_chart(fig_acos, use_container_width=True)
        
        # Conversion metrics
        st.markdown("### Conversion Metrics by Channel")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Conversion Rate by Channel
            fig_conv = px.bar(
                channel_data,
                x='name',
                y='conversion_rate',
                title="Conversion Rate by Channel",
                labels={
                    'name': 'Channel',
                    'conversion_rate': 'Conversion Rate (%)'
                },
                color='name',
                color_discrete_map={c['name']: get_channel_color(c['name']) for c in stats['channels']}
            )
            
            # Show values on bars
            fig_conv.update_traces(
                texttemplate='%{y:.2f}%',
                textposition='outside'
            )
            
            # Hide legend
            fig_conv.update_layout(showlegend=False)
            
            st.plotly_chart(fig_conv, use_container_width=True)
        
        with col2:
            # Profit Margin by Channel
            fig_margin = px.bar(
                channel_data,
                x='name',
                y='profit_margin',
                title="Profit Margin by Channel",
                labels={
                    'name': 'Channel',
                    'profit_margin': 'Profit Margin (%)'
                },
                color='name',
                color_discrete_map={c['name']: get_channel_color(c['name']) for c in stats['channels']}
            )
            
            # Show values on bars
            fig_margin.update_traces(
                texttemplate='%{y:.2f}%',
                textposition='outside'
            )
            
            # Hide legend
            fig_margin.update_layout(showlegend=False)
            
            st.plotly_chart(fig_margin, use_container_width=True)
        
        # Spend allocation
        st.markdown("### Budget Allocation")
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            # Ad Spend by Channel pie chart
            fig_spend = px.pie(
                channel_data,
                values='ad_spend',
                names='name',
                title="Ad Spend by Channel",
                color='name',
                color_discrete_map={c['name']: get_channel_color(c['name']) for c in stats['channels']}
            )
            
            # Show percentages on pie chart
            fig_spend.update_traces(textposition='inside', textinfo='percent+label')
            
            st.plotly_chart(fig_spend, use_container_width=True)
        
        with col2:
            # Investment vs. Return treemap
            for channel in channel_data.itertuples():
                channel_data.loc[channel.Index, 'efficiency'] = channel.revenue / channel.ad_spend if channel.ad_spend > 0 else 0
            
            fig_treemap = px.treemap(
                channel_data,
                path=['name'],
                values='ad_spend',
                color='efficiency',
                color_continuous_scale=px.colors.sequential.Viridis,
                hover_data=['ad_spend', 'revenue', 'roas', 'acos'],
                title='Ad Spend vs. Efficiency by Channel'
            )
            
            # Customize tooltip
            fig_treemap.update_traces(
                hovertemplate='<b>%{label}</b><br>Ad Spend: $%{value:,.2f}<br>ROAS: %{customdata[2]:.2f}x<br>ACoS: %{customdata[3]:.2f}%'
            )
            
            st.plotly_chart(fig_treemap, use_container_width=True)
        
        # Top campaigns
        st.markdown("### Top Performing Campaigns")
        
        # Get top 5 campaigns by ROAS
        top_campaigns = analyzer.campaigns.sort_values(by='roas', ascending=False).head(5)
        
        # Create campaign cards
        col1, col2, col3, col4, col5 = st.columns(5)
        cols = [col1, col2, col3, col4, col5]
        
        for i, campaign in enumerate(top_campaigns.itertuples()):
            if i < len(cols):
                with cols[i]:
                    st.markdown(f"""
                    <div class="campaign-card {campaign.channel.lower().replace(' ', '')}">
                        <div class="header">
                            <span class="title">{campaign.campaign_name}</span>
                        </div>
                        <div style="font-size: 12px;">{campaign.channel}</div>
                        <div class="metrics">
                            <div class="metric">
                                <div class="metric-label">ROAS</div>
                                <div class="metric-value" style="color: {get_color_scale(campaign.roas, 2, 6)};">{campaign.roas:.2f}x</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">ACoS</div>
                                <div class="metric-value" style="color: {get_color_scale(campaign.acos, 40, 10, reverse=True)};">{campaign.acos:.2f}%</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Advanced analytics in advanced mode
    if st.session_state.app_mode == "Advanced":
        st.markdown("### Advanced Analytics")
        
        # ROAS vs ACoS Scatter Plot
        fig_scatter = px.scatter(
            analyzer.campaigns,
            x="acos",
            y="roas",
            size="ad_spend",
            color="channel",
            hover_name="campaign_name",
            size_max=60,
            title="ROAS vs. ACoS by Channel and Ad Spend",
            labels={
                "acos": "ACoS (%)",
                "roas": "ROAS",
                "ad_spend": "Ad Spend ($)",
                "channel": "Channel"
            },
            color_discrete_map={c['name']: get_channel_color(c['name']) for c in stats['channels']}
        )
        
        # Add quadrant lines
        fig_scatter.add_hline(y=3, line_dash="dash", line_color="gray")
        fig_scatter.add_vline(x=25, line_dash="dash", line_color="gray")
        
        # Add quadrant labels
        fig_scatter.add_annotation(
            x=12.5, y=4.5,
            text="IDEAL: High ROAS, Low ACoS",
            showarrow=False,
            font=dict(color="green", size=10)
        )
        
        fig_scatter.add_annotation(
            x=37.5, y=4.5,
            text="GOOD: High ROAS, High ACoS",
            showarrow=False,
            font=dict(color="blue", size=10)
        )
        
        fig_scatter.add_annotation(
            x=12.5, y=1.5,
            text="CONSIDER: Low ROAS, Low ACoS",
            showarrow=False,
            font=dict(color="orange", size=10)
        )
        
        fig_scatter.add_annotation(
            x=37.5, y=1.5,
            text="AVOID: Low ROAS, High ACoS",
            showarrow=False,
            font=dict(color="red", size=10)
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # AI Market Insights
        st.markdown("### AI Marketing Insights")
        
        # Check if OpenAI API key is available
        api_key_status = st.session_state.get('api_key_status', None)
        
        if api_key_status == "valid":
            # Show AI insights button
            if st.button("Generate AI Insights"):
                with st.spinner("Generating AI-powered marketing insights..."):
                    insights = get_ai_campaign_insights(analyzer.campaigns)
                    st.markdown(insights)
        else:
            st.info("""
            AI-powered marketing insights are available with a valid OpenAI API key.
            Go to Settings to configure your API key.
            """)
    
    # Recent campaigns
    st.markdown("### Recent Campaigns")
    
    # Get most recent 5 campaigns by timestamp
    recent_campaigns = analyzer.campaigns.sort_values(by='timestamp', ascending=False).head(5)
    
    # Display recent campaigns table
    if not recent_campaigns.empty:
        recent_df = recent_campaigns[[
            'campaign_name', 'channel', 'ad_spend', 'revenue', 'roas', 'acos', 'profit'
        ]].copy()
        
        # Format columns
        recent_df['ad_spend'] = recent_df['ad_spend'].apply(lambda x: f"${x:,.2f}")
        recent_df['revenue'] = recent_df['revenue'].apply(lambda x: f"${x:,.2f}")
        recent_df['roas'] = recent_df['roas'].apply(lambda x: f"{x:.2f}x")
        recent_df['acos'] = recent_df['acos'].apply(lambda x: f"{x:.2f}%")
        recent_df['profit'] = recent_df['profit'].apply(lambda x: f"${x:,.2f}")
        
        # Rename columns
        recent_df = recent_df.rename(columns={
            'campaign_name': 'Campaign',
            'channel': 'Channel',
            'ad_spend': 'Ad Spend',
            'revenue': 'Revenue',
            'roas': 'ROAS',
            'acos': 'ACoS',
            'profit': 'Profit'
        })
        
        # Display table
        st.dataframe(recent_df, use_container_width=True, hide_index=True)

def display_settings(analyzer: MarketingAnalyzer):
    """
    Display app settings and data management options.
    
    Args:
        analyzer: MarketingAnalyzer instance
    """
    st.subheader("Settings & Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Import/Export Data")
        
        # Export current data
        if not analyzer.campaigns.empty:
            json_data = analyzer.download_json()
            st.download_button(
                "Export All Campaigns (JSON)",
                data=json_data,
                file_name="ViveROI_campaigns.json",
                mime="application/json"
            )
            
            # Export as Excel
            try:
                excel_data = io.BytesIO()
                with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
                    analyzer.campaigns.to_excel(writer, index=False, sheet_name='Campaigns')
                    
                    # Add formatting
                    workbook = writer.book
                    worksheet = writer.sheets['Campaigns']
                    
                    # Add header formatting
                    header_format = workbook.add_format({
                        'bold': True,
                        'bg_color': COLOR_SCHEME['primary'],
                        'color': 'white',
                        'border': 1
                    })
                    
                    # Apply formatting to header row
                    for col_num, value in enumerate(analyzer.campaigns.columns):
                        worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(col_num, col_num, 15)
                
                st.download_button(
                    "Export as Excel Spreadsheet",
                    data=excel_data.getvalue(),
                    file_name="ViveROI_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error exporting to Excel: {str(e)}")
            
            # Export as CSV
            csv_data = analyzer.campaigns.to_csv(index=False).encode()
            st.download_button(
                "Export as CSV",
                data=csv_data,
                file_name="ViveROI_export.csv",
                mime="text/csv"
            )
        
        # Import data
        st.markdown("#### Import Data")
        uploaded_file = st.file_uploader("Upload campaign data (JSON, Excel, or CSV)", type=["json", "xlsx", "csv"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.json'):
                    json_str = uploaded_file.read().decode("utf-8")
                    if analyzer.upload_json(json_str):
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
                    if analyzer.upload_json(json_str):
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
                    if analyzer.upload_json(json_str):
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
        
        # Create mode toggle
        mode_options = ["Basic", "Advanced"]
        selected_mode = st.radio("Select Mode", mode_options, 
                                horizontal=True,
                                index=mode_options.index(st.session_state.app_mode))
        
        # Update mode if changed
        if selected_mode != st.session_state.app_mode:
            st.session_state.app_mode = selected_mode
            st.success(f"Switched to {selected_mode} Mode")
            st.rerun()
        
        # Theme settings
        st.markdown("#### UI Theme")
        theme_options = ["vive", "default", "amazon", "dark"]
        theme_labels = {
            "vive": "Vive Blue",
            "default": "Standard Blue",
            "amazon": "Amazon Orange",
            "dark": "Dark Mode"
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
        
        # AI Settings
        st.markdown("#### AI Assistant Configuration")
        
        # Check API key status
        api_key_status = st.session_state.get('api_key_status', None)
        
        if api_key_status == "valid":
            st.success("OpenAI API Key is configured and valid")
        elif api_key_status == "invalid":
            st.error("OpenAI API Key is invalid. Please check your API key in the Streamlit secrets.")
        elif api_key_status == "missing":
            st.warning("OpenAI API Key is missing. Add your key to the Streamlit secrets to enable AI features.")
        else:
            st.info("Checking OpenAI API key status...")
            check_openai_api_key()
            st.rerun()
        
        # AI model selection (for future use)
        if api_key_status == "valid":
            ai_model = st.selectbox(
                "AI Model",
                ["gpt-4o", "gpt-3.5-turbo"],
                index=0,
                help="Select the AI model for campaign insights"
            )
        
        # Reset data
        st.markdown("#### Data Management")
        if st.button("Add Example Campaigns"):
            count = analyzer.add_example_campaigns()
            st.success(f"Added {count} example campaigns!")
            st.rerun()
        
        if st.button("Clear All Data"):
            confirm = st.checkbox("I understand this will delete all campaigns")
            if confirm:
                analyzer.campaigns = pd.DataFrame(columns=analyzer.campaigns.columns)
                analyzer.save_data()
                
                # Also clear comparison list
                if 'compare_list' in st.session_state:
                    st.session_state.compare_list = []
                
                st.success("All data cleared!")
                st.rerun()
    
    # About section
    st.markdown("### About ViveROI Analytics")
    st.markdown("""
    ViveROI Analytics is a comprehensive marketing analytics platform designed for Vive Health's e-commerce team to analyze and optimize PPC and marketing spend across Amazon and other channels. The application provides advanced analytics including ROI calculations, what-if analysis, Monte Carlo simulations, and AI-powered insights.
    
    **Version:** 1.0.0  
    **Build Date:** May 2025  
    **Developed for:** Vive Health E-commerce Team, contact alexander.popoff@vivehealth.com for support
    """)
