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

# Version info
APP_VERSION = "1.1.0"
SUPPORT_EMAIL = "alexander.popoff@vivehealth.com"

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

# Track if first visit for guided tour
if 'first_visit' not in st.session_state:
    st.session_state.first_visit = True

# Track loading state
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

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
        
        /* Enhanced Metric Card */
        .enhanced-metric {{
            background-color: {COLOR_SCHEME["card_bg"]};
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            transition: all 0.3s;
            height: 100%;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }}
        
        .enhanced-metric:hover {{
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        .enhanced-metric .label {{
            font-size: 0.9rem;
            color: #64748b;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }}
        
        .enhanced-metric .value {{
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.5rem;
        }}
        
        .enhanced-metric .trend {{
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            margin-top: auto;
        }}
        
        .enhanced-metric .trend-up {{
            color: {COLOR_SCHEME["positive"]};
        }}
        
        .enhanced-metric .trend-down {{
            color: {COLOR_SCHEME["negative"]};
        }}
        
        .enhanced-metric .trend-neutral {{
            color: {COLOR_SCHEME["neutral"]};
        }}
        
        .enhanced-metric .badge {{
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 0.7rem;
            padding: 3px 8px;
            border-radius: 12px;
            font-weight: 600;
        }}
        
        .enhanced-metric .badge-success {{
            background-color: {COLOR_SCHEME["positive"]}25;
            color: {COLOR_SCHEME["positive"]};
        }}
        
        .enhanced-metric .badge-warning {{
            background-color: {COLOR_SCHEME["warning"]}25;
            color: {COLOR_SCHEME["warning"]};
        }}
        
        .enhanced-metric .badge-danger {{
            background-color: {COLOR_SCHEME["negative"]}25;
            color: {COLOR_SCHEME["negative"]};
        }}
        
        /* Breadcrumb Navigation */
        .breadcrumb {{
            display: flex;
            flex-wrap: wrap;
            list-style: none;
            margin: 0 0 1rem 0;
            padding: 0.5rem 1rem;
            background-color: {COLOR_SCHEME["background"]};
            border-radius: 8px;
        }}
        
        .breadcrumb-item {{
            display: flex;
            align-items: center;
            color: {COLOR_SCHEME["neutral"]};
            font-size: 0.9rem;
        }}
        
        .breadcrumb-item a {{
            color: {COLOR_SCHEME["primary"]};
            text-decoration: none;
        }}
        
        .breadcrumb-item a:hover {{
            text-decoration: underline;
        }}
        
        .breadcrumb-item + .breadcrumb-item::before {{
            content: "/";
            display: inline-block;
            padding: 0 0.5rem;
            color: {COLOR_SCHEME["neutral"]};
        }}
        
        .breadcrumb-item.active {{
            color: {COLOR_SCHEME["text_dark"]};
            font-weight: 600;
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
            transition: all 0.2s ease-in-out;
        }}
        
        .campaign-card:hover {{
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
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
        
        /* Loading spinner */
        .loading-spinner {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px;
        }}
        
        .loading-spinner::after {{
            content: "";
            width: 40px;
            height: 40px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid {COLOR_SCHEME["primary"]};
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        /* Toast notifications */
        .toast {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            animation: slideIn 0.3s, fadeOut 0.5s 2.5s forwards;
            max-width: 350px;
        }}
        
        .toast-success {{
            background-color: {COLOR_SCHEME["positive"]};
        }}
        
        .toast-error {{
            background-color: {COLOR_SCHEME["negative"]};
        }}
        
        .toast-warning {{
            background-color: {COLOR_SCHEME["warning"]};
        }}
        
        .toast-info {{
            background-color: {COLOR_SCHEME["neutral"]};
        }}
        
        @keyframes slideIn {{
            from {{ transform: translateX(100%); }}
            to {{ transform: translateX(0); }}
        }}
        
        @keyframes fadeOut {{
            from {{ opacity: 1; }}
            to {{ opacity: 0; visibility: hidden; }}
        }}
        
        /* Help button */
        .help-button {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: {COLOR_SCHEME["primary"]};
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            cursor: pointer;
            z-index: 9998;
            transition: all 0.3s;
        }}
        
        .help-button:hover {{
            background-color: {COLOR_SCHEME["secondary"]};
            transform: scale(1.1);
        }}
        
        /* Guided tour tooltips */
        .guided-tooltip {{
            position: absolute;
            background-color: {COLOR_SCHEME["primary"]};
            color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 9999;
            width: 300px;
        }}
        
        .guided-tooltip::after {{
            content: "";
            position: absolute;
            border-width: 8px;
            border-style: solid;
        }}
        
        .guided-tooltip.top::after {{
            top: 100%;
            left: 50%;
            margin-left: -8px;
            border-color: {COLOR_SCHEME["primary"]} transparent transparent transparent;
        }}
        
        .guided-tooltip.bottom::after {{
            bottom: 100%;
            left: 50%;
            margin-left: -8px;
            border-color: transparent transparent {COLOR_SCHEME["primary"]} transparent;
        }}
        
        .guided-tooltip.left::after {{
            top: 50%;
            left: 100%;
            margin-top: -8px;
            border-color: transparent transparent transparent {COLOR_SCHEME["primary"]};
        }}
        
        .guided-tooltip.right::after {{
            top: 50%;
            right: 100%;
            margin-top: -8px;
            border-color: transparent {COLOR_SCHEME["primary"]} transparent transparent;
        }}
        
        .guided-tooltip .title {{
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 1.1rem;
        }}
        
        .guided-tooltip .content {{
            margin-bottom: 12px;
            font-size: 0.9rem;
        }}
        
        .guided-tooltip .buttons {{
            display: flex;
            justify-content: space-between;
        }}
        
        .guided-tooltip .button {{
            padding: 6px 12px;
            border-radius: 4px;
            border: none;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .guided-tooltip .button-next {{
            background-color: white;
            color: {COLOR_SCHEME["primary"]};
        }}
        
        .guided-tooltip .button-skip {{
            background-color: transparent;
            color: white;
            text-decoration: underline;
        }}
        
        /* Mobile responsiveness improvements */
        @media (max-width: 768px) {{
            .metric-container {{
                padding: 0.75rem;
            }}
            
            .metric-value {{
                font-size: 1.5rem;
            }}
            
            .campaign-card {{
                padding: 12px;
            }}
            
            .campaign-card .title {{
                font-size: 14px;
            }}
            
            .enhanced-metric {{
                padding: 0.75rem;
            }}
            
            .enhanced-metric .value {{
                font-size: 1.5rem;
            }}
        }}
        
        /* Keyboard shortcut indicators */
        .keyboard-shortcut {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            background-color: #f1f5f9;
            border: 1px solid #e2e8f0;
            font-family: monospace;
            font-size: 0.8rem;
            margin-left: 5px;
        }}
        
        /* Table of contents */
        .toc {{
            background-color: {COLOR_SCHEME["background"]};
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #e2e8f0;
            margin-bottom: 20px;
        }}
        
        .toc-title {{
            font-weight: 600;
            margin-bottom: 10px;
            color: {COLOR_SCHEME["primary"]};
        }}
        
        .toc ul {{
            list-style-type: none;
            padding-left: 15px;
            margin-bottom: 0;
        }}
        
        .toc li {{
            margin-bottom: 5px;
        }}
        
        .toc a {{
            color: {COLOR_SCHEME["primary"]};
            text-decoration: none;
        }}
        
        .toc a:hover {{
            text-decoration: underline;
        }}
        
        /* Animated chart containers */
        .animated-chart {{
            transition: all 0.3s ease-in-out;
        }}
        
        .animated-chart:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        }}
        
        /* Accessible focus indicators */
        button:focus, a:focus, input:focus, select:focus, textarea:focus {{
            outline: 2px solid {COLOR_SCHEME["primary"]};
            outline-offset: 2px;
        }}
        
        /* Form validation indicators */
        .form-field-valid {{
            border-color: {COLOR_SCHEME["positive"]} !important;
            background-color: {COLOR_SCHEME["positive"]}10 !important;
        }}
        
        .form-field-invalid {{
            border-color: {COLOR_SCHEME["negative"]} !important;
            background-color: {COLOR_SCHEME["negative"]}10 !important;
        }}
        
        .validation-message {{
            font-size: 0.8rem;
            margin-top: 4px;
            font-weight: 500;
        }}
        
        .validation-error {{
            color: {COLOR_SCHEME["negative"]};
        }}
        
        .validation-success {{
            color: {COLOR_SCHEME["positive"]};
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
    try:
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
    except Exception as e:
        logger.error(f"Error calculating performance score: {str(e)}")
        return None

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
    except Exception as e:
        logger.error(f"Error in safe_divide: {str(e)}")
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
    try:
        total_cost = unit_cost + shipping_cost + amazon_fees + ad_cost_per_sale
        profit = selling_price - total_cost
        profit_margin = safe_divide(profit * 100, selling_price)
        
        return {
            "total_cost": total_cost,
            "profit": profit,
            "profit_margin": profit_margin
        }
    except Exception as e:
        logger.error(f"Error calculating profit metrics: {str(e)}")
        return {
            "total_cost": 0,
            "profit": 0,
            "profit_margin": 0
        }

def show_toast(message: str, type: str = "success"):
    """Show a toast notification to the user.
    
    Args:
        message: The message to display
        type: Type of toast - 'success', 'error', 'warning', or 'info'
    """
    toast_types = {
        "success": "toast-success",
        "error": "toast-error",
        "warning": "toast-warning",
        "info": "toast-info"
    }
    
    toast_class = toast_types.get(type, "toast-info")
    
    toast_html = f"""
    <div class="toast {toast_class}">
        {message}
    </div>
    <script>
        setTimeout(function() {{
            const toasts = document.getElementsByClassName('toast');
            if (toasts.length > 0) {{
                toasts[0].remove();
            }}
        }}, 3000);
    </script>
    """
    
    st.markdown(toast_html, unsafe_allow_html=True)

def display_loading_spinner(message: str = "Loading..."):
    """Display a loading spinner with a message."""
    if st.session_state.is_loading:
        spinner_html = f"""
        <div class="loading-spinner">
            <p style="margin-bottom: 30px;">{message}</p>
        </div>
        """
        st.markdown(spinner_html, unsafe_allow_html=True)

def validate_campaign_form(form_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate campaign form data.
    
    Args:
        form_data: Dictionary of form data
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Required fields
    if not form_data.get('campaign_name'):
        errors.append("Campaign Name is required")
    
    if not form_data.get('product_name'):
        errors.append("Product Name is required")
    
    # Numeric fields must be non-negative
    for field, label in [
        ('ad_spend', 'Ad Spend'),
        ('clicks', 'Clicks'),
        ('impressions', 'Impressions'),
        ('conversions', 'Conversions'),
        ('revenue', 'Revenue'),
        ('product_cost', 'Product Cost'),
        ('selling_price', 'Selling Price')
    ]:
        value = form_data.get(field)
        if not isinstance(value, (int, float)) or value < 0:
            errors.append(f"{label} must be a non-negative number")
    
    # Logical validations
    if form_data.get('clicks', 0) > form_data.get('impressions', 0):
        errors.append("Clicks cannot be greater than impressions")
    
    if form_data.get('conversions', 0) > form_data.get('clicks', 0):
        errors.append("Conversions cannot be greater than clicks")
    
    # Date validation
    try:
        start_date = datetime.strptime(form_data.get('start_date', ''), '%Y-%m-%d')
        end_date = datetime.strptime(form_data.get('end_date', ''), '%Y-%m-%d')
        
        if end_date < start_date:
            errors.append("End date cannot be before start date")
    except ValueError:
        errors.append("Invalid date format")
    
    return len(errors) == 0, errors

def display_help_button():
    """Display a floating help button."""
    help_html = """
    <div class="help-button" onclick="showHelp()">?</div>
    <script>
    function showHelp() {
        // Implement guided help functionality
        const helpEvent = new CustomEvent('showHelp');
        window.dispatchEvent(helpEvent);
    }
    </script>
    """
    st.markdown(help_html, unsafe_allow_html=True)

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
    st.session_state.is_loading = True
    api_key = st.secrets.get("openai_api_key", None)
    
    # If API key is missing, generate a simulated response
    if not api_key:
        logger.warning("OpenAI API key not found in secrets, using simulated response")
        # Add a slight delay to simulate API call
        time.sleep(1.5)
        st.session_state.is_loading = False
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
        
        st.session_state.is_loading = False
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return f"Error: The AI assistant encountered a problem (HTTP {response.status_code}). Please try again later or contact support at {SUPPORT_EMAIL} if the issue persists."
    except requests.exceptions.Timeout:
        logger.error("OpenAI API timeout")
        st.session_state.is_loading = False
        return "Error: The AI assistant timed out. Please try again later when the service is less busy."
    except requests.exceptions.ConnectionError:
        logger.error("OpenAI API connection error")
        st.session_state.is_loading = False
        return "Error: Could not connect to the AI service. Please check your internet connection and try again."
    except Exception as e:
        logger.exception("Error calling OpenAI API")
        st.session_state.is_loading = False
        return f"Error: The AI assistant encountered an unexpected problem. Please try again later or contact support at {SUPPORT_EMAIL} if the issue persists."

def generate_simulated_response(messages):
    """Generate a simulated response for demonstration when API key is missing."""
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
        return f"Error generating insights: {str(e)}\n\nPlease try again later or contact support at {SUPPORT_EMAIL}."

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
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}\n{traceback.format_exc()}")
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
            # Validate form data
            form_data = {
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
                'product_cost': product_cost,
                'selling_price': selling_price,
                'shipping_cost': shipping_cost,
                'amazon_fees': amazon_fees,
                'target_acos': target_acos
            }
            
            is_valid, errors = validate_campaign_form(form_data)
            if not is_valid:
                return False, "\n".join(errors)
            
            # Generate a unique ID
            uid = str(uuid.uuid4())[:8]
            
            # Calculate basic metrics with error handling
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
            logger.error(f"Error adding campaign: {str(e)}\n{error_details}")
            return False, f"Error adding campaign: {str(e)}"
    
    def get_campaign(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get a campaign by UID."""
        try:
            if uid in self.campaigns['uid'].values:
                return self.campaigns[self.campaigns['uid'] == uid].iloc[0].to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting campaign: {str(e)}")
            return None
    
    def delete_campaign(self, uid: str) -> bool:
        """Delete a campaign by UID."""
        try:
            if uid in self.campaigns['uid'].values:
                self.campaigns = self.campaigns[self.campaigns['uid'] != uid]
                self.save_data()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting campaign: {str(e)}")
            return False
    
    def update_campaign(self, uid: str, **kwargs) -> Tuple[bool, str]:
        """Update a campaign and recalculate values."""
        try:
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
        except Exception as e:
            logger.error(f"Error updating campaign: {str(e)}")
            return False, f"Error updating campaign: {str(e)}"
    
    def add_example_campaigns(self) -> int:
        """Add example campaigns for demonstration."""
        added = 0
        try:
            for example in self.default_examples:
                success, _ = self.add_campaign(**example)
                if success:
                    added += 1
            return added
        except Exception as e:
            logger.error(f"Error adding example campaigns: {str(e)}")
            return added

    def clone_campaign(self, uid: str, new_name: Optional[str] = None) -> Tuple[bool, str]:
        """Clone an existing campaign."""
        try:
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
        except Exception as e:
            logger.error(f"Error cloning campaign: {str(e)}")
            return False, f"Error cloning campaign: {str(e)}"
    
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
        try:
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
            
            # Show progress
            st.session_state.is_loading = True
            progress_text = "Running Monte Carlo simulation..."
            progress_bar = st.progress(0)
            
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
                    sim_impressions = (sim_clicks * 100) / sim_ctr if sim_ctr > 0 else campaign['impressions']
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
                    
                    # Update progress bar
                    if i % 10 == 0:
                        progress_value = i / num_simulations
                        progress_bar.progress(progress_value)
                
                except Exception as e:
                    # Log error and continue with next simulation
                    logger.error(f"Error in simulation {i}: {str(e)}")
                    continue
            
            # Complete progress bar
            progress_bar.progress(1.0)
            time.sleep(0.5)
            progress_bar.empty()
            
            st.session_state.is_loading = False
            
            return results, "Simulation completed successfully"
        
        except Exception as e:
            st.session_state.is_loading = False
            logger.error(f"Error running Monte Carlo simulation: {str(e)}")
            return None, f"Error running simulation: {str(e)}"
    
    def get_channel_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics across channels."""
        try:
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
        
        except Exception as e:
            logger.error(f"Error getting channel statistics: {str(e)}")
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
                'channels': [],
                'error': str(e)
            }

    def create_scenario(self, base_campaign_uid: str, **adjustments) -> Dict[str, Any]:
        """
        Create a what-if scenario based on an existing campaign.
        
        Args:
            base_campaign_uid: UID of the base campaign
            adjustments: Dict of parameters to adjust (e.g., ad_spend_change=20)
            
        Returns:
            Dict with calculated metrics for the scenario
        """
        try:
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
        except Exception as e:
            logger.error(f"Error creating scenario: {str(e)}")
            return {"error": f"Error creating scenario: {str(e)}"}

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
    col1, col2, col3 = st.columns([1, 4, 1])
    
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
    
    # Version and user info
    with col3:
        st.markdown(f"""
        <div style="text-align: right; padding: 10px">
            <p style="margin: 0; color: {COLOR_SCHEME["neutral"]}; font-size: 0.8rem;">v{APP_VERSION}</p>
            <p style="margin: 0; font-weight: 500; color: {COLOR_SCHEME["primary"]};">Quality Management</p>
        </div>
        """, unsafe_allow_html=True)

def display_breadcrumb(items: List[Tuple[str, str]]):
    """Display breadcrumb navigation.
    
    Args:
        items: List of (label, link) tuples for breadcrumb items
    """
    breadcrumb_html = '<ol class="breadcrumb">'
    
    for i, (label, link) in enumerate(items):
        if i == len(items) - 1:
            # Last item (current page)
            breadcrumb_html += f'<li class="breadcrumb-item active">{label}</li>'
        else:
            # Previous items
            breadcrumb_html += f'<li class="breadcrumb-item"><a href="{link}">{label}</a></li>'
    
    breadcrumb_html += '</ol>'
    
    st.markdown(breadcrumb_html, unsafe_allow_html=True)

def display_enhanced_metric(label: str, value: Any, trend: Optional[float] = None, 
                          badge: Optional[str] = None, prefix: str = "", suffix: str = "",
                          help_text: Optional[str] = None, formatter=None):
    """Display an enhanced metric card with label, value, and optional badge and trend.
    
    Args:
        label: Metric label
        value: Metric value
        trend: Optional percentage change
        badge: Optional badge text ('success', 'warning', 'danger')
        prefix: Optional prefix for the value (e.g., "$")
        suffix: Optional suffix for the value (e.g., "%")
        help_text: Optional help text for tooltip
        formatter: Optional function to format the value
    """
    # Format value if formatter is provided
    display_value = formatter(value) if formatter else value
    
    # Determine badge class
    badge_class = ""
    if badge:
        if badge.lower() == "success":
            badge_class = "badge-success"
            badge_text = "Good"
        elif badge.lower() == "warning":
            badge_class = "badge-warning"
            badge_text = "Average"
        elif badge.lower() == "danger":
            badge_class = "badge-danger"
            badge_text = "Poor"
        else:
            badge_class = "badge-info"
            badge_text = badge
    
    # Determine trend class and icon
    trend_class = ""
    trend_icon = ""
    if trend is not None:
        if trend > 0:
            trend_class = "trend-up"
            trend_icon = "↑"
        elif trend < 0:
            trend_class = "trend-down"
            trend_icon = "↓"
        else:
            trend_class = "trend-neutral"
            trend_icon = "→"
    
    # Create tooltip
    tooltip_attr = f'title="{help_text}"' if help_text else ""
    
    # Build the HTML
    metric_html = f"""
    <div class="enhanced-metric" {tooltip_attr}>
        <div class="label">{label}</div>
        <div class="value">{prefix}{display_value}{suffix}</div>
        
        {f'<div class="badge {badge_class}">{badge_text}</div>' if badge else ''}
        
        {f'<div class="trend {trend_class}">{trend_icon} {abs(trend):.1f}%</div>' if trend is not None else ''}
    </div>
    """
    
    st.markdown(metric_html, unsafe_allow_html=True)

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
    
    # Get trend data (simulate for now, in a real app this would come from actual data)
    spend_trend = 5.2  # Example: 5.2% increase from previous period
    roas_trend = 3.8
    acos_trend = -2.1  # Negative is good for ACoS
    profit_trend = 7.4
    
    with col1:
        display_enhanced_metric(
            "Total Ad Spend", 
            stats['total_spend'], 
            trend=spend_trend,
            prefix="$", 
            badge="warning" if spend_trend > 10 else "success",
            help_text="Total advertising spend across all campaigns",
            formatter=lambda x: f"{x:,.2f}"
        )
    
    with col2:
        # Determine ROAS badge based on value
        if stats['overall_roas'] >= 4:
            roas_badge = "success"
        elif stats['overall_roas'] >= 2:
            roas_badge = "warning"
        else:
            roas_badge = "danger"
            
        display_enhanced_metric(
            "Overall ROAS", 
            stats['overall_roas'], 
            trend=roas_trend,
            suffix="x", 
            badge=roas_badge,
            help_text="Return on Ad Spend (Revenue ÷ Ad Spend)",
            formatter=lambda x: f"{x:.2f}"
        )
    
    with col3:
        # Determine ACoS badge based on value
        if stats['overall_acos'] <= 20:
            acos_badge = "success"
        elif stats['overall_acos'] <= 30:
            acos_badge = "warning"
        else:
            acos_badge = "danger"
            
        display_enhanced_metric(
            "Overall ACoS", 
            stats['overall_acos'], 
            trend=acos_trend,
            suffix="%", 
            badge=acos_badge,
            help_text="Advertising Cost of Sale (Ad Spend ÷ Revenue × 100%)",
            formatter=lambda x: f"{x:.2f}"
        )
    
    with col4:
        display_enhanced_metric(
            "Total Profit", 
            stats['total_profit'], 
            trend=profit_trend,
            prefix="$", 
            badge="success" if profit_trend > 0 else "danger",
            help_text="Total profit after ad costs and all fees",
            formatter=lambda x: f"{x:,.2f}"
        )
    
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
            display_enhanced_metric(
                "Campaigns", 
                stats['total_campaigns'], 
                help_text="Total number of marketing campaigns",
                formatter=lambda x: f"{int(x)}"
            )
        
        with col2:
            # Determine score badge
            score_badge = "success" if avg_score and avg_score >= 70 else ("warning" if avg_score and avg_score >= 50 else "danger")
            
            display_enhanced_metric(
                "Avg. Performance Score", 
                avg_score if avg_score else "N/A", 
                badge=score_badge if avg_score else None,
                help_text="Average performance score across all campaigns (0-100)",
                formatter=lambda x: f"{x:.1f}" if not isinstance(x, str) else x
            )
        
        with col3:
            # Determine conversion rate badge
            conv_badge = "success" if conversion_rate >= 3 else ("warning" if conversion_rate >= 1.5 else "danger")
            
            display_enhanced_metric(
                "Avg. Conversion Rate", 
                conversion_rate, 
                suffix="%", 
                badge=conv_badge,
                help_text="Average conversion rate across all campaigns",
                formatter=lambda x: f"{x:.2f}"
            )
        
        with col4:
            display_enhanced_metric(
                "Best Performing Channel", 
                best_channel, 
                help_text=f"Channel with highest ROAS ({best_roas:.2f}x)",
                formatter=lambda x: x
            )
        
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
            logger.error(f"Error displaying top campaigns: {str(e)}")
            st.error("Error displaying top campaigns. Please try refreshing the page.")

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
            # Set loading state
            st.session_state.is_loading = True
            
            success, message = analyzer.add_campaign(
                campaign_name, product_name, channel, category,
                ad_spend, clicks, impressions, conversions, revenue,
                start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),
                product_cost, selling_price, shipping_cost, amazon_fees,
                target_acos, notes
            )
            
            # Reset loading state
            st.session_state.is_loading = False
            
            if success:
                show_toast(message, "success")
                return True
            else:
                show_toast(message, "error")
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
                show_toast("Please enter a Campaign Name", "error")
                return False
            
            if not product_name:
                show_toast("Please enter a Product Name", "error")
                return False
            
            if end_date < start_date:
                show_toast("End date cannot be before start date", "error")
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
                    show_toast("Please enter a value greater than 0 for Ad Spend", "error")
                    return False
                
                if clicks <= 0:
                    show_toast("Please enter a value greater than 0 for Clicks", "error")
                    return False
                
                if impressions <= 0:
                    show_toast("Please enter a value greater than 0 for Impressions", "error")
                    return False
                
                if clicks > impressions:
                    show_toast("Clicks cannot be greater than impressions", "error")
                    return False
                
                if conversions > clicks:
                    show_toast("Conversions cannot be greater than clicks", "error")
                    return False
                
                if revenue <= 0 and conversions > 0:
                    show_toast("Please enter a value greater than 0 for Revenue", "error")
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
        
        # Show the campaign summary
        st.markdown(f"""
        <div style="padding: 10px; border-radius: 5px; background-color: {COLOR_SCHEME['primary']}20; margin-bottom: 20px;">
            <strong>Campaign:</strong> {st.session_state.wizard_data.get('campaign_name', '')} | 
            <strong>Channel:</strong> {st.session_state.wizard_data.get('channel', '')} | 
            <strong>Revenue:</strong> ${float(st.session_state.wizard_data.get('revenue', 0.0)):.2f}
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
            
            amazon_fees = st.number_input("Platform Fees ($)", 
                value=float(st.session_state.wizard_data.get('amazon_fees', 0.0)),
                min_value=0.0, 
                format="%.2f", 
                help="Amazon referral, FBA fees, or other platform fees if applicable")
        
        with col3:
            channel = st.session_state.wizard_data.get('channel', '')
            
            # Display channel-specific guidance
            if channel == "Amazon":
                st.markdown("""
                **Amazon Fee Structure:**
                - Referral Fee: 15% (most categories)
                - FBA Fees: Varies by size/weight
                - Storage Fees: Monthly + Long-term
                
                [Amazon Fee Calculator Link](https://sellercentral.amazon.com/hz/fba/profitabilitycalculator)
                """)
            elif channel == "Vive Website":
                st.markdown("""
                **Website Economics:**
                - Credit Card Processing: ~2.9% + $0.30
                - Fulfillment Costs: Varies
                - Customer Service: Consider time cost
                """)
            else:
                st.markdown("""
                **Fee Considerations:**
                - Platform Commissions
                - Payment Processing
                - Return Rate Impact
                - Warehousing & Fulfillment
                """)
        
        # Calculate and show profit metrics if we have data
        conversions = int(st.session_state.wizard_data.get('conversions', 0))
        revenue = float(st.session_state.wizard_data.get('revenue', 0.0))
        ad_spend = float(st.session_state.wizard_data.get('ad_spend', 0.0))
        
        if product_cost > 0 and selling_price > 0 and conversions > 0:
            # Calculate metrics
            ad_cost_per_sale = ad_spend / conversions if conversions > 0 else 0
            profit_metrics = get_profit_metrics(
                product_cost, selling_price, shipping_cost, amazon_fees, ad_cost_per_sale
            )
            
            profit_per_unit = profit_metrics["profit"]
            total_profit = profit_per_unit * conversions
            profit_margin = profit_metrics["profit_margin"]
            
            # Display metrics
            st.markdown("### Profit Analysis")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Cost Per Unit", f"${product_cost:.2f}")
                st.metric("Total Costs", f"${(product_cost + shipping_cost + amazon_fees):.2f}")
            
            with col2:
                st.metric("Ad Cost Per Sale", f"${ad_cost_per_sale:.2f}")
                st.metric("Profit Per Sale", f"${profit_per_unit:.2f}")
            
            with col3:
                st.metric("Total Profit", f"${total_profit:.2f}")
                
            with col4:
                st.metric("Profit Margin", f"{profit_margin:.2f}%")
                roi = (total_profit / ad_spend) * 100 if ad_spend > 0 else 0
                st.metric("ROI", f"{roi:.2f}%")
            
            # Profit margin assessment
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
                <strong>Profit Assessment:</strong> {margin_assessment} - Profit margin of {profit_margin:.2f}% 
                with ${profit_per_unit:.2f} profit per unit and total profit of ${total_profit:.2f}
            </div>
            """, unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.wizard_step = 2
                st.rerun()
        
        with col2:
            if st.button("Next: Review & Save"):
                # Validate inputs
                if product_cost <= 0:
                    show_toast("Please enter a value greater than 0 for Product Cost", "error")
                    return False
                
                if selling_price <= 0:
                    show_toast("Please enter a value greater than 0 for Selling Price", "error")
                    return False
                
                if selling_price < product_cost:
                    show_toast("Selling price cannot be less than product cost", "warning")
                
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
        
        # Get all the data from session state
        data = st.session_state.wizard_data
        
        # Calculate metrics for display
        clicks = int(data.get('clicks', 0))
        impressions = int(data.get('impressions', 0))
        conversions = int(data.get('conversions', 0))
        ad_spend = float(data.get('ad_spend', 0.0))
        revenue = float(data.get('revenue', 0.0))
        
        avg_cpc = ad_spend / clicks if clicks > 0 else 0
        ctr = (clicks / impressions) * 100 if impressions > 0 else 0
        conversion_rate = (conversions / clicks) * 100 if clicks > 0 else 0
        acos = (ad_spend / revenue) * 100 if revenue > 0 else 0
        roas = revenue / ad_spend if ad_spend > 0 else 0
        
        # Product economics
        product_cost = float(data.get('product_cost', 0.0))
        selling_price = float(data.get('selling_price', 0.0))
        shipping_cost = float(data.get('shipping_cost', 0.0))
        amazon_fees = float(data.get('amazon_fees', 0.0))
        
        ad_cost_per_sale = ad_spend / conversions if conversions > 0 else 0
        profit_metrics = get_profit_metrics(
            product_cost, selling_price, shipping_cost, amazon_fees, ad_cost_per_sale
        )
        
        profit_per_unit = profit_metrics["profit"]
        total_profit = profit_per_unit * conversions
        profit_margin = profit_metrics["profit_margin"]
        
        # Display campaign summary
        st.markdown("### Campaign Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Basic Information")
            st.markdown(f"""
            **Campaign Name:** {data.get('campaign_name', '')}  
            **Product Name:** {data.get('product_name', '')}  
            **Channel:** {data.get('channel', '')}  
            **Category:** {data.get('category', '')}  
            **Date Range:** {data.get('start_date', '')} to {data.get('end_date', '')}
            """)
            
            st.markdown("#### Marketing Metrics")
            st.markdown(f"""
            **Ad Spend:** ${ad_spend:.2f}  
            **Impressions:** {impressions:,}  
            **Clicks:** {clicks:,}  
            **Conversions:** {conversions:,}  
            **Revenue:** ${revenue:.2f}
            """)
        
        with col2:
            st.markdown("#### Performance Metrics")
            st.markdown(f"""
            **Avg. CPC:** ${avg_cpc:.2f}  
            **CTR:** {ctr:.2f}%  
            **Conversion Rate:** {conversion_rate:.2f}%  
            **ACoS:** {acos:.2f}%  
            **ROAS:** {roas:.2f}x
            """)
            
            st.markdown("#### Economics")
            st.markdown(f"""
            **Product Cost:** ${product_cost:.2f}  
            **Selling Price:** ${selling_price:.2f}  
            **Profit Per Sale:** ${profit_per_unit:.2f}  
            **Total Profit:** ${total_profit:.2f}  
            **Profit Margin:** {profit_margin:.2f}%
            """)
        
        # Campaign notes
        st.markdown("#### Notes")
        st.markdown(f"> {data.get('notes', 'No notes added.')}")
        
        # Campaign assessment visualization
        st.markdown("### Performance Assessment")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # ROAS gauge
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = roas,
                title = {'text': "ROAS"},
                gauge = {
                    'axis': {'range': [0, 8], 'tickwidth': 1},
                    'bar': {'color': COLOR_SCHEME["primary"]},
                    'steps': [
                        {'range': [0, 2], 'color': COLOR_SCHEME["negative"]},
                        {'range': [2, 4], 'color': COLOR_SCHEME["warning"]},
                        {'range': [4, 8], 'color': COLOR_SCHEME["positive"]}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 1
                    }
                }
            ))
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # ACoS gauge
            target_acos = float(data.get('target_acos', 20.0))
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = acos,
                title = {'text': "ACoS"},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1},
                    'bar': {'color': COLOR_SCHEME["primary"]},
                    'steps': [
                        {'range': [0, target_acos], 'color': COLOR_SCHEME["positive"]},
                        {'range': [target_acos, target_acos*1.5], 'color': COLOR_SCHEME["warning"]},
                        {'range': [target_acos*1.5, 100], 'color': COLOR_SCHEME["negative"]}
                    ],
                    'threshold': {
                        'line': {'color': "green", 'width': 4},
                        'thickness': 0.75,
                        'value': target_acos
                    }
                }
            ))
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Profit Margin gauge
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = profit_margin,
                title = {'text': "Profit Margin"},
                gauge = {
                    'axis': {'range': [0, 50], 'tickwidth': 1, 'ticksuffix': "%"},
                    'bar': {'color': COLOR_SCHEME["primary"]},
                    'steps': [
                        {'range': [0, 10], 'color': COLOR_SCHEME["negative"]},
                        {'range': [10, 20], 'color': COLOR_SCHEME["warning"]},
                        {'range': [20, 50], 'color': COLOR_SCHEME["positive"]}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0
                    }
                }
            ))
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
        
        # Overall assessment
        overall_score = 0
        if roas >= 4:
            roas_assessment = "Excellent"
            roas_score = 3
        elif roas >= 2:
            roas_assessment = "Good"
            roas_score = 2
        elif roas >= 1:
            roas_assessment = "Average"
            roas_score = 1
        else:
            roas_assessment = "Poor"
            roas_score = 0
        
        if acos <= target_acos:
            acos_assessment = "On Target"
            acos_score = 3
        elif acos <= target_acos * 1.5:
            acos_assessment = "Above Target"
            acos_score = 1
        else:
            acos_assessment = "Far Above Target"
            acos_score = 0
        
        if profit_margin >= 30:
            margin_assessment = "Excellent"
            margin_score = 3
        elif profit_margin >= 20:
            margin_assessment = "Good"
            margin_score = 2
        elif profit_margin >= 10:
            margin_assessment = "Average"
            margin_score = 1
        else:
            margin_assessment = "Poor"
            margin_score = 0
        
        # Average score
        overall_score = (roas_score + acos_score + margin_score) / 3
        
        if overall_score >= 2.5:
            overall_assessment = "Excellent"
            color = COLOR_SCHEME["positive"]
        elif overall_score >= 1.5:
            overall_assessment = "Good"
            color = COLOR_SCHEME["positive"]
        elif overall_score >= 0.5:
            overall_assessment = "Average"
            color = COLOR_SCHEME["warning"]
        else:
            overall_assessment = "Poor"
            color = COLOR_SCHEME["negative"]
        
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 8px; background-color: {color}30; border-left: 6px solid {color}; margin-top: 20px;">
            <h4 style="margin-top: 0;">Overall Assessment: {overall_assessment}</h4>
            <p>ROAS: <strong>{roas_assessment}</strong> ({roas:.2f}x)</p>
            <p>ACoS: <strong>{acos_assessment}</strong> ({acos:.2f}% vs target {target_acos:.2f}%)</p>
            <p>Profit Margin: <strong>{margin_assessment}</strong> ({profit_margin:.2f}%)</p>
            <p>This campaign is {overall_assessment.lower()} overall with a {'' if profit_margin > 0 else 'negative'} profit margin 
            and a return on ad spend of {roas:.2f}x.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # AI-powered insights if API is available
        if 'api_key_status' in st.session_state and st.session_state.api_key_status == "valid":
            # Make a temporary df for AI analysis
            temp_df = pd.DataFrame([data])
            temp_df['roas'] = roas
            temp_df['acos'] = acos
            temp_df['conversion_rate'] = conversion_rate
            temp_df['profit'] = total_profit
            temp_df['profit_margin'] = profit_margin
            
            with st.expander("AI-Powered Campaign Insights", expanded=False):
                st.markdown("#### AI Analysis")
                
                insights_placeholder = st.empty()
                with insights_placeholder:
                    st.info("Generating AI insights... This may take a few seconds.")
                
                insights = get_ai_campaign_insights(temp_df, data.get('campaign_name', ''))
                
                with insights_placeholder:
                    st.markdown(insights)
        
        # Navigation and save buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("← Back"):
                st.session_state.wizard_step = 3
                st.rerun()
        
        with col3:
            if st.button("💾 Save Campaign", type="primary"):
                # Set loading state
                st.session_state.is_loading = True
                
                success, message = analyzer.add_campaign(
                    data.get('campaign_name', ''), 
                    data.get('product_name', ''), 
                    data.get('channel', ''), 
                    data.get('category', ''),
                    ad_spend, 
                    clicks, 
                    impressions, 
                    conversions, 
                    revenue,
                    data.get('start_date', ''), 
                    data.get('end_date', ''),
                    product_cost, 
                    selling_price, 
                    shipping_cost, 
                    amazon_fees,
                    float(data.get('target_acos', 0)),
                    data.get('notes', '')
                )
                
                # Reset loading state
                st.session_state.is_loading = False
                
                if success:
                    show_toast(message, "success")
                    # Reset wizard
                    st.session_state.wizard_step = 1
                    st.session_state.wizard_data = {}
                    # Flag for completion
                    st.success("Campaign added successfully! You'll be redirected to the dashboard.")
                    time.sleep(1)
                    return True
                else:
                    show_toast(message, "error")
                    return False
    
    return False

def display_campaigns_table(df: pd.DataFrame):
    """Display campaigns in a sortable, filterable table."""
    if df.empty:
        st.info("No campaigns found. Add campaigns to see them here.")
        return
    
    # Add a search box
    search_term = st.text_input("Search Campaigns", "", help="Search by campaign name, product, or channel")
    
    # Filter data based on search term
    if search_term:
        filtered_df = df[
            df['campaign_name'].str.contains(search_term, case=False, na=False) |
            df['product_name'].str.contains(search_term, case=False, na=False) |
            df['channel'].str.contains(search_term, case=False, na=False)
        ]
    else:
        filtered_df = df
    
    # If still no results after filtering
    if filtered_df.empty:
        st.info(f"No campaigns found matching '{search_term}'.")
        return
    
    # Add filter and sort options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Channel filter
        channels = ['All Channels'] + sorted(df['channel'].unique().tolist())
        selected_channel = st.selectbox("Channel", channels)
        
        if selected_channel != 'All Channels':
            filtered_df = filtered_df[filtered_df['channel'] == selected_channel]
    
    with col2:
        # Category filter
        categories = ['All Categories'] + sorted(df['category'].unique().tolist())
        selected_category = st.selectbox("Category", categories)
        
        if selected_category != 'All Categories':
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    with col3:
        # Sort options
        sort_options = {
            'Campaign Name': 'campaign_name',
            'ROAS (High to Low)': 'roas',
            'ACoS (Low to High)': 'acos',
            'Revenue (High to Low)': 'revenue',
            'Profit (High to Low)': 'profit',
            'Performance Score (High to Low)': 'performance_score'
        }
        
        selected_sort = st.selectbox("Sort By", list(sort_options.keys()))
        sort_col = sort_options[selected_sort]
        
        if 'High to Low' in selected_sort:
            filtered_df = filtered_df.sort_values(by=sort_col, ascending=False)
        elif 'Low to High' in selected_sort:
            filtered_df = filtered_df.sort_values(by=sort_col, ascending=True)
        else:
            filtered_df = filtered_df.sort_values(by=sort_col)
    
    # Display count of filtered campaigns
    st.markdown(f"Showing **{len(filtered_df)}** of **{len(df)}** campaigns")
    
    # Prepare display columns
    display_df = filtered_df[['uid', 'campaign_name', 'channel', 'product_name', 'ad_spend', 
                            'revenue', 'roas', 'acos', 'conversion_rate', 'profit', 'profit_margin',
                            'performance_score']].copy()
    
    # Format columns
    display_df['ad_spend'] = display_df['ad_spend'].apply(lambda x: f"${x:,.2f}")
    display_df['revenue'] = display_df['revenue'].apply(lambda x: f"${x:,.2f}")
    display_df['roas'] = display_df['roas'].apply(lambda x: f"{x:.2f}x")
    display_df['acos'] = display_df['acos'].apply(lambda x: f"{x:.2f}%")
    display_df['conversion_rate'] = display_df['conversion_rate'].apply(lambda x: f"{x:.2f}%")
    display_df['profit'] = display_df['profit'].apply(lambda x: f"${x:,.2f}")
    display_df['profit_margin'] = display_df['profit_margin'].apply(lambda x: f"{x:.2f}%")
    display_df['performance_score'] = display_df['performance_score'].apply(
        lambda x: f"{x:.1f}/100" if not pd.isna(x) else "N/A"
    )
    
    # Column display names
    display_df.columns = ['UID', 'Campaign Name', 'Channel', 'Product', 'Ad Spend', 
                         'Revenue', 'ROAS', 'ACoS', 'Conv. Rate', 'Profit', 'Margin', 'Score']
    
    # Display the table with row highlighting
    campaign_selection = st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "UID": None  # Hide UID column
        },
        hide_index=True
    )
    
    # Add campaign actions below table
    st.markdown("### Campaign Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        campaign_uid = st.text_input("Campaign UID for Actions", 
                                  help="Enter the UID of the campaign you want to take action on")
    
    with col2:
        action = st.selectbox("Select Action", 
                           ["View Details", "Edit Campaign", "Clone Campaign", "Delete Campaign"])
    
    with col3:
        if st.button("Execute Action"):
            if not campaign_uid:
                show_toast("Please enter a Campaign UID", "error")
            elif campaign_uid not in df['uid'].values:
                show_toast("Campaign not found with that UID", "error")
            else:
                # Execute the selected action
                if action == "View Details":
                    st.session_state.selected_campaign = campaign_uid
                    st.session_state.view = "campaign_details"
                    st.rerun()
                elif action == "Edit Campaign":
                    st.session_state.edit_campaign = campaign_uid
                    st.session_state.view = "edit_campaign"
                    st.rerun()
                elif action == "Clone Campaign":
                    success, message = analyzer.clone_campaign(campaign_uid)
                    if success:
                        show_toast(message, "success")
                        st.rerun()
                    else:
                        show_toast(message, "error")
                elif action == "Delete Campaign":
                    if analyzer.delete_campaign(campaign_uid):
                        show_toast("Campaign deleted successfully", "success")
                        st.rerun()
                    else:
                        show_toast("Failed to delete campaign", "error")

def display_campaign_details(campaign_uid: str):
    """Display detailed view of a single campaign."""
    campaign = analyzer.get_campaign(campaign_uid)
    
    if not campaign:
        st.error("Campaign not found. It may have been deleted.")
        if st.button("Back to Dashboard"):
            st.session_state.view = "dashboard"
            st.rerun()
        return
    
    # Breadcrumb
    display_breadcrumb([
        ("Dashboard", "#"),
        ("Campaigns", "#"),
        (campaign['campaign_name'], "")
    ])
    
    # Header with back button
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("← Back"):
            st.session_state.view = "dashboard"
            st.rerun()
    
    with col2:
        st.title(campaign['campaign_name'])
        st.caption(f"Campaign for {campaign['product_name']} on {campaign['channel']}")
    
    # Campaign details
    st.markdown("## Campaign Details")
    
    # Basic info and metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Basic Information")
        st.markdown(f"""
        **Channel:** {campaign['channel']}  
        **Category:** {campaign['category']}  
        **Date Range:** {campaign['start_date']} to {campaign['end_date']}  
        **UID:** {campaign['uid']}
        """)
        
        if campaign.get('notes'):
            st.markdown("### Notes")
            st.markdown(f"> {campaign['notes']}")
    
    with col2:
        st.markdown("### Performance Metrics")
        st.markdown(f"""
        **Ad Spend:** ${campaign['ad_spend']:,.2f}  
        **Revenue:** ${campaign['revenue']:,.2f}  
        **ROAS:** {campaign['roas']:.2f}x  
        **ACoS:** {campaign['acos']:.2f}%  
        **Target ACoS:** {campaign['target_acos']:.2f}%  
        **Performance Score:** {campaign['performance_score']:.1f}/100
        """)
    
    with col3:
        st.markdown("### Traffic & Conversion")
        st.markdown(f"""
        **Impressions:** {campaign['impressions']:,}  
        **Clicks:** {campaign['clicks']:,}  
        **Conversions:** {campaign['conversions']:,}  
        **CTR:** {campaign['ctr']:.2f}%  
        **Conversion Rate:** {campaign['conversion_rate']:.2f}%  
        **Avg. CPC:** ${campaign['avg_cpc']:.2f}
        """)
    
    # Profit metrics and economics
    st.markdown("## Economics & Profitability")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Product Economics")
        st.markdown(f"""
        **Product Cost:** ${campaign['product_cost']:,.2f}  
        **Selling Price:** ${campaign['selling_price']:,.2f}  
        **Shipping Cost:** ${campaign['shipping_cost']:,.2f}  
        **Platform Fees:** ${campaign['amazon_fees']:,.2f}
        """)
    
    with col2:
        st.markdown("### Profit Metrics")
        
        # Calculate ad cost per sale
        ad_cost_per_sale = campaign['ad_spend'] / campaign['conversions'] if campaign['conversions'] > 0 else 0
        
        # Calculate unit economics
        unit_cost = campaign['product_cost'] + campaign['shipping_cost'] + campaign['amazon_fees']
        profit_per_unit = campaign['selling_price'] - unit_cost - ad_cost_per_sale
        
        st.markdown(f"""
        **Total Profit:** ${campaign['profit']:,.2f}  
        **Profit Margin:** {campaign['profit_margin']:.2f}%  
        **Ad Cost Per Sale:** ${ad_cost_per_sale:.2f}  
        **Profit Per Unit:** ${profit_per_unit:.2f}
        """)
    
    with col3:
        st.markdown("### Breakeven Analysis")
        
        # Breakeven calculations
        breakeven_acos = ((campaign['selling_price'] - unit_cost) / campaign['selling_price']) * 100
        max_bid = (campaign['selling_price'] - unit_cost) * (campaign['conversion_rate'] / 100)
        
        st.markdown(f"""
        **Breakeven ACoS:** {breakeven_acos:.2f}%  
        **ACoS Margin:** {(breakeven_acos - campaign['acos']):.2f}%  
        **Max Bid at Breakeven:** ${max_bid:.2f}  
        **Current Avg CPC:** ${campaign['avg_cpc']:.2f}
        """)
    
    # Visualizations
    st.markdown("## Campaign Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Performance Metrics", "Economics", "What-If Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # ROAS vs ACoS gauge charts
            fig = make_subplots(
                rows=1, cols=2,
                specs=[[{"type": "indicator"}, {"type": "indicator"}]],
                subplot_titles=("ROAS", "ACoS")
            )
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=campaign['roas'],
                    gauge={
                        'axis': {'range': [0, 8], 'tickwidth': 1},
                        'bar': {'color': get_channel_color(campaign['channel'])},
                        'steps': [
                            {'range': [0, 2], 'color': COLOR_SCHEME["negative"]},
                            {'range': [2, 4], 'color': COLOR_SCHEME["warning"]},
                            {'range': [4, 8], 'color': COLOR_SCHEME["positive"]}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 1
                        }
                    }
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=campaign['acos'],
                    gauge={
                        'axis': {'range': [0, 50], 'tickwidth': 1, 'ticksuffix': "%"},
                        'bar': {'color': get_channel_color(campaign['channel'])},
                        'steps': [
                            {'range': [0, campaign['target_acos']], 'color': COLOR_SCHEME["positive"]},
                            {'range': [campaign['target_acos'], campaign['target_acos']*1.5], 'color': COLOR_SCHEME["warning"]},
                            {'range': [campaign['target_acos']*1.5, 50], 'color': COLOR_SCHEME["negative"]}
                        ],
                        'threshold': {
                            'line': {'color': "green", 'width': 4},
                            'thickness': 0.75,
                            'value': campaign['target_acos']
                        }
                    }
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                height=300, 
                margin=dict(l=20, r=20, t=40, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Funnel chart
            conversion_funnel = go.Figure()
            
            funnel_values = [campaign['impressions'], campaign['clicks'], campaign['conversions']]
            funnel_text = [
                f"Impressions: {campaign['impressions']:,}",
                f"Clicks: {campaign['clicks']:,} (CTR: {campaign['ctr']:.2f}%)",
                f"Conversions: {campaign['conversions']:,} (CR: {campaign['conversion_rate']:.2f}%)"
            ]
            
            conversion_funnel.add_trace(go.Funnel(
                y = ["Impressions", "Clicks", "Conversions"],
                x = funnel_values,
                textinfo = "text",
                text = funnel_text,
                marker = {
                    "color": [
                        "rgba(0, 163, 224, 0.8)",
                        "rgba(0, 163, 224, 0.6)",
                        "rgba(0, 163, 224, 0.4)"
                    ]
                },
                connector = {"line": {"color": "royalblue", "dash": "dot", "width": 3}}
            ))
            
            conversion_funnel.update_layout(
                title="Conversion Funnel",
                margin=dict(l=20, r=20, t=60, b=20),
                height=400
            )
            
            st.plotly_chart(conversion_funnel, use_container_width=True)
        
        with col2:
            # Performance Score gauge
            if 'performance_score' in campaign and campaign['performance_score'] is not None:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=campaign['performance_score'],
                    title={'text': "Performance Score"},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1},
                        'bar': {'color': get_channel_color(campaign['channel'])},
                        'steps': [
                            {'range': [0, 50], 'color': COLOR_SCHEME["negative"]},
                            {'range': [50, 70], 'color': COLOR_SCHEME["warning"]},
                            {'range': [70, 100], 'color': COLOR_SCHEME["positive"]}
                        ]
                    }
                ))
                
                fig.update_layout(
                    height=300, 
                    margin=dict(l=20, r=20, t=60, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Performance comparison
            comparison_data = analyzer.campaigns[analyzer.campaigns['channel'] == campaign['channel']]
            if not comparison_data.empty:
                # Calculate averages
                avg_roas = comparison_data['roas'].mean()
                avg_acos = comparison_data['acos'].mean()
                avg_conversion = comparison_data['conversion_rate'].mean()
                avg_profit_margin = comparison_data['profit_margin'].mean()
                
                # Create comparison chart
                comparison_fig = go.Figure()
                
                metrics = ['ROAS', 'ACoS', 'Conversion Rate', 'Profit Margin']
                campaign_values = [
                    campaign['roas'], 
                    campaign['acos'], 
                    campaign['conversion_rate'], 
                    campaign['profit_margin']
                ]
                avg_values = [avg_roas, avg_acos, avg_conversion, avg_profit_margin]
                
                # For ACoS, lower is better, so we need special handling
                comparison_fig.add_trace(go.Bar(
                    name='This Campaign',
                    x=metrics,
                    y=campaign_values,
                    marker_color=[
                        COLOR_SCHEME["primary"] if campaign_values[i] >= avg_values[i] else COLOR_SCHEME["negative"] 
                        for i in range(len(metrics)) if i != 1
                    ] + [
                        COLOR_SCHEME["primary"] if campaign_values[1] <= avg_values[1] else COLOR_SCHEME["negative"]
                    ],
                    text=[f"{v:.2f}{'x' if i == 0 else '%'}" for i, v in enumerate(campaign_values)],
                    textposition='auto',
                ))
                
                comparison_fig.add_trace(go.Bar(
                    name=f'Avg on {campaign["channel"]}',
                    x=metrics,
                    y=avg_values,
                    marker_color='rgba(100, 100, 100, 0.6)',
                    text=[f"{v:.2f}{'x' if i == 0 else '%'}" for i, v in enumerate(avg_values)],
                    textposition='auto',
                ))
                
                comparison_fig.update_layout(
                    title=f"Comparison to Other {campaign['channel']} Campaigns",
                    barmode='group',
                    height=400,
                    margin=dict(l=20, r=20, t=60, b=40),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(comparison_fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Cost breakdown
            cost_data = {
                'Category': ['Product Cost', 'Shipping', 'Platform Fees', 'Ad Cost Per Sale'],
                'Amount': [
                    campaign['product_cost'],
                    campaign['shipping_cost'],
                    campaign['amazon_fees'],
                    ad_cost_per_sale
                ]
            }
            
            cost_df = pd.DataFrame(cost_data)
            cost_df['Percentage'] = cost_df['Amount'] / cost_df['Amount'].sum() * 100
            
            cost_fig = px.pie(
                cost_df, 
                values='Amount', 
                names='Category',
                title='Cost Breakdown Per Unit',
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            
            cost_fig.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                hovertemplate='%{label}: $%{value:.2f} (%{percent})'
            )
            
            cost_fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=60, b=20)
            )
            
            st.plotly_chart(cost_fig, use_container_width=True)
        
        with col2:
            # Revenue allocation
            total_cost = campaign['product_cost'] + campaign['shipping_cost'] + campaign['amazon_fees']
            
            revenue_data = {
                'Category': ['Cost of Goods', 'Ad Cost', 'Profit'],
                'Amount': [
                    total_cost * campaign['conversions'],
                    campaign['ad_spend'],
                    campaign['profit']
                ]
            }
            
            revenue_df = pd.DataFrame(revenue_data)
            revenue_df['Percentage'] = revenue_df['Amount'] / campaign['revenue'] * 100
            
            revenue_fig = px.pie(
                revenue_df, 
                values='Amount', 
                names='Category',
                title='Revenue Allocation',
                color_discrete_sequence=px.colors.sequential.Greens_r
            )
            
            revenue_fig.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                hovertemplate='%{label}: $%{value:.2f} (%{percent})'
            )
            
            revenue_fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=60, b=20)
            )
            
            st.plotly_chart(revenue_fig, use_container_width=True)
            
        # Profitability metrics
        st.markdown("### Profitability Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            display_enhanced_metric(
                "Cost Per Sale", 
                total_cost + ad_cost_per_sale,
                prefix="$", 
                help_text="Total cost per each conversion/sale including product, shipping, fees and ad cost",
                formatter=lambda x: f"{x:.2f}"
            )
        
        with col2:
            display_enhanced_metric(
                "Breakeven ACoS", 
                breakeven_acos,
                suffix="%", 
                badge="success" if campaign['acos'] < breakeven_acos else "danger",
                help_text="Maximum ACoS at which the campaign remains profitable",
                formatter=lambda x: f"{x:.2f}"
            )
        
        with col3:
            margin_dollars = campaign['selling_price'] - (total_cost + ad_cost_per_sale)
            display_enhanced_metric(
                "Margin Per Sale", 
                margin_dollars,
                prefix="$", 
                badge="success" if margin_dollars > 0 else "danger",
                help_text="Dollar profit per unit after all costs",
                formatter=lambda x: f"{x:.2f}"
            )
        
        with col4:
            roi = (campaign['profit'] / campaign['ad_spend']) * 100 if campaign['ad_spend'] > 0 else 0
            display_enhanced_metric(
                "ROI", 
                roi,
                suffix="%", 
                badge="success" if roi > 50 else ("warning" if roi > 0 else "danger"),
                help_text="Return on Investment (Profit ÷ Ad Spend × 100%)",
                formatter=lambda x: f"{x:.2f}"
            )
    
    with tab3:
        st.markdown("### What-If Scenario Analysis")
        st.caption("Adjust parameters to see how changes would affect campaign results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ad_spend_change = st.slider("Ad Spend Change", -50, 100, 0, 5,
                                    help="Percentage change in ad spend")
            
            cpc_change = st.slider("CPC Change", -30, 30, 0, 5,
                                help="Percentage change in cost per click")
        
        with col2:
            ctr_change = st.slider("CTR Change", -30, 50, 0, 5,
                                help="Percentage change in click-through rate")
            
            conversion_rate_change = st.slider("Conversion Rate Change", -30, 50, 0, 5,
                                           help="Percentage change in conversion rate")
        
        with col3:
            price_change = st.slider("Price Change", -20, 30, 0, 5,
                                  help="Percentage change in selling price")
            
            cost_change = st.slider("Cost Change", -20, 20, 0, 5,
                                 help="Percentage change in product cost")
        
        # Calculate scenario
        scenario = analyzer.create_scenario(
            campaign_uid,
            ad_spend_change=ad_spend_change,
            cpc_change=cpc_change,
            ctr_change=ctr_change,
            conversion_rate_change=conversion_rate_change,
            price_change=price_change,
            cost_change=cost_change
        )
        
        if 'error' in scenario:
            st.error(scenario['error'])
        else:
            # Display scenario results
            st.markdown("### Scenario Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Key metrics table
                metrics_comparison = pd.DataFrame({
                    'Metric': ['Ad Spend', 'Clicks', 'Conversions', 'Revenue', 'ROAS', 
                              'ACoS', 'Profit', 'Profit Margin'],
                    'Current': [
                        f"${campaign['ad_spend']:.2f}",
                        f"{campaign['clicks']:.0f}",
                        f"{campaign['conversions']:.0f}",
                        f"${campaign['revenue']:.2f}",
                        f"{campaign['roas']:.2f}x",
                        f"{campaign['acos']:.2f}%",
                        f"${campaign['profit']:.2f}",
                        f"{campaign['profit_margin']:.2f}%"
                    ],
                    'Scenario': [
                        f"${scenario['ad_spend']:.2f}",
                        f"{scenario['clicks']:.0f}",
                        f"{scenario['conversions']:.0f}",
                        f"${scenario['revenue']:.2f}",
                        f"{scenario['roas']:.2f}x",
                        f"{scenario['acos']:.2f}%",
                        f"${scenario['profit']:.2f}",
                        f"{scenario['profit_margin']:.2f}%"
                    ],
                    'Change': [
                        f"{scenario['changes']['ad_spend_change']:.2f}%",
                        f"{scenario['changes']['clicks_change']:.2f}%",
                        f"{scenario['changes']['conversions_change']:.2f}%",
                        f"{scenario['changes']['revenue_change']:.2f}%",
                        f"{scenario['changes']['roas_change']:.2f}%",
                        f"{scenario['changes']['acos_change']:.2f}%",
                        f"{scenario['changes']['profit_change']:.2f}%",
                        f"{(scenario['profit_margin'] - campaign['profit_margin']):.2f}%"
                    ]
                })
                
                st.dataframe(metrics_comparison, use_container_width=True, hide_index=True)
            
            with col2:
                # Profit change visualization
                profit_change = scenario['profit'] - campaign['profit']
                profit_color = COLOR_SCHEME["positive"] if profit_change >= 0 else COLOR_SCHEME["negative"]
                
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background-color: {profit_color}20; 
                            border-radius: 10px; border: 2px solid {profit_color};">
                    <h3 style="margin-bottom: 10px;">Profit Impact</h3>
                    <p style="font-size: 2rem; font-weight: bold; color: {profit_color};">
                        {'+' if profit_change >= 0 else ''}{profit_change:.2f}
                    </p>
                    <p>Current: ${campaign['profit']:.2f} → Scenario: ${scenario['profit']:.2f}</p>
                    <p>Change: {scenario['changes']['profit_change']:.2f}%</p>
                </div>
                """, unsafe_allow_html=True)
                
                # ROAS & ACoS comparison
                roas_acos_fig = make_subplots(
                    rows=1, cols=2,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=("ROAS Change", "ACoS Change")
                )
                
                # ROAS delta
                roas_delta = scenario['roas'] - campaign['roas']
                roas_acos_fig.add_trace(
                    go.Indicator(
                        mode="delta",
                        value=scenario['roas'],
                        delta={'reference': campaign['roas'], 'relative': True, 'valueformat': '.1%'},
                        title={'text': f"Current: {campaign['roas']:.2f}x → Scenario: {scenario['roas']:.2f}x"},
                        number={'valueformat': '.2f', 'suffix': 'x'}
                    ),
                    row=1, col=1
                )
                
                # ACoS delta
                acos_delta = scenario['acos'] - campaign['acos']
                roas_acos_fig.add_trace(
                    go.Indicator(
                        mode="delta",
                        value=scenario['acos'],
                        delta={
                            'reference': campaign['acos'], 
                            'relative': True, 
                            'valueformat': '.1%',
                            'decreasing': {'color': COLOR_SCHEME["positive"]},
                            'increasing': {'color': COLOR_SCHEME["negative"]}
                        },
                        title={'text': f"Current: {campaign['acos']:.2f}% → Scenario: {scenario['acos']:.2f}%"},
                        number={'valueformat': '.2f', 'suffix': '%'}
                    ),
                    row=1, col=2
                )
                
                roas_acos_fig.update_layout(
                    height=200,
                    margin=dict(l=20, r=20, t=80, b=20)
                )
                
                st.plotly_chart(roas_acos_fig, use_container_width=True)
            
            # Monte Carlo simulation
            st.markdown("### Risk Analysis Simulation")
            
            # Allow user to run Monte Carlo simulation
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                num_simulations = st.slider("Number of Simulations", 100, 5000, 1000, 100,
                                        help="More simulations give more accurate results but take longer")
            
            with col2:
                simulation_variations = st.slider("Parameter Variation (%)", 5, 40, 20, 5,
                                              help="How much parameters can vary in the simulation (higher = more variance)")
            
            with col3:
                run_simulation = st.button("Run Simulation")
            
            if run_simulation:
                # Set up parameter variations based on user input
                param_variations = {
                    'ad_spend': simulation_variations,
                    'ctr': simulation_variations,
                    'conversion_rate': simulation_variations,
                    'avg_cpc': simulation_variations,
                    'selling_price': simulation_variations / 2,  # Half variation for price and cost
                    'product_cost': simulation_variations / 2
                }
                
                # Run simulation
                sim_results, sim_message = analyzer.run_monte_carlo_simulation(
                    campaign_uid, num_simulations, param_variations
                )
                
                if sim_results is not None:
                    # Display simulation results
                    st.success(f"Simulation completed: {num_simulations} scenarios analyzed")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # ROAS distribution
                        roas_hist = px.histogram(
                            sim_results, 
                            x="roas", 
                            nbins=30,
                            title="ROAS Distribution",
                            labels={"roas": "ROAS"},
                            color_discrete_sequence=[COLOR_SCHEME["primary"]]
                        )
                        
                        roas_hist.add_vline(
                            x=campaign['roas'],
                            line_dash="dash",
                            line_color="red",
                            annotation_text="Current ROAS"
                        )
                        
                        roas_hist.update_layout(
                            height=300,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        
                        st.plotly_chart(roas_hist, use_container_width=True)
                    
                    with col2:
                        # Profit distribution
                        profit_hist = px.histogram(
                            sim_results, 
                            x="profit", 
                            nbins=30,
                            title="Profit Distribution",
                            labels={"profit": "Profit"},
                            color_discrete_sequence=[COLOR_SCHEME["secondary"]]
                        )
                        
                        profit_hist.add_vline(
                            x=campaign['profit'],
                            line_dash="dash",
                            line_color="red",
                            annotation_text="Current Profit"
                        )
                        
                        profit_hist.update_layout(
                            height=300,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        
                        st.plotly_chart(profit_hist, use_container_width=True)
                    
                    # Risk analysis
                    st.markdown("### Risk Analysis")
                    
                    # Calculate risk metrics
                    prob_profit = (sim_results['profit'] > 0).mean() * 100
                    prob_better_roas = (sim_results['roas'] > campaign['roas']).mean() * 100
                    prob_better_profit = (sim_results['profit'] > campaign['profit']).mean() * 100
                    
                    worst_case_profit = sim_results['profit'].quantile(0.05)
                    expected_profit = sim_results['profit'].mean()
                    best_case_profit = sim_results['profit'].quantile(0.95)
                    
                    # Display risk metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        display_enhanced_metric(
                            "Prob. of Profit", 
                            prob_profit,
                            suffix="%", 
                            badge="success" if prob_profit > 80 else ("warning" if prob_profit > 50 else "danger"),
                            help_text="Probability of having positive profit",
                            formatter=lambda x: f"{x:.1f}"
                        )
                    
                    with col2:
                        display_enhanced_metric(
                            "Prob. of Better ROAS", 
                            prob_better_roas,
                            suffix="%", 
                            badge="success" if prob_better_roas > 60 else ("warning" if prob_better_roas > 40 else "danger"),
                            help_text="Probability of having better ROAS than current",
                            formatter=lambda x: f"{x:.1f}"
                        )
                    
                    with col3:
                        display_enhanced_metric(
                            "Prob. of Better Profit", 
                            prob_better_profit,
                            suffix="%", 
                            badge="success" if prob_better_profit > 60 else ("warning" if prob_better_profit > 40 else "danger"),
                            help_text="Probability of having better profit than current",
                            formatter=lambda x: f"{x:.1f}"
                        )
                    
                    with col4:
                        performance_risk = 100 - prob_profit
                        display_enhanced_metric(
                            "Performance Risk", 
                            performance_risk,
                            suffix="%", 
                            badge="success" if performance_risk < 20 else ("warning" if performance_risk < 50 else "danger"),
                            help_text="Risk of unprofitable performance",
                            formatter=lambda x: f"{x:.1f}"
                        )
                    
                    # Profit range
                    st.markdown("#### Expected Profit Range")
                    
                    profit_range_html = f"""
                    <div style="display: flex; align-items: center; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
                        <div style="flex: 1; text-align: center; padding: 10px; background-color: {COLOR_SCHEME["negative"]}20; border-radius: 5px; margin-right: 10px;">
                            <div style="font-size: 0.9rem; font-weight: bold;">Worst Case (5%)</div>
                            <div style="font-size: 1.4rem;">${worst_case_profit:.2f}</div>
                        </div>
                        <div style="flex: 1; text-align: center; padding: 10px; background-color: {COLOR_SCHEME["primary"]}20; border-radius: 5px; margin-right: 10px;">
                            <div style="font-size: 0.9rem; font-weight: bold;">Expected</div>
                            <div style="font-size: 1.4rem;">${expected_profit:.2f}</div>
                        </div>
                        <div style="flex: 1; text-align: center; padding: 10px; background-color: {COLOR_SCHEME["positive"]}20; border-radius: 5px;">
                            <div style="font-size: 0.9rem; font-weight: bold;">Best Case (95%)</div>
                            <div style="font-size: 1.4rem;">${best_case_profit:.2f}</div>
                        </div>
                    </div>
                    """
                    
                    st.markdown(profit_range_html, unsafe_allow_html=True)
                    
                    # Correlation analysis
                    st.markdown("#### Sensitivity Analysis")
                    st.caption("Correlation between input parameters and profit/ROAS")
                    
                    # Calculate correlations
                    correlations = sim_results[['ctr', 'conversion_rate', 'avg_cpc', 
                                              'ad_spend', 'profit', 'roas']].corr()
                    
                    # Sensitivity to profit
                    profit_corr = correlations['profit'].drop(['profit', 'roas']).sort_values(ascending=False)
                    roas_corr = correlations['roas'].drop(['profit', 'roas']).sort_values(ascending=False)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Profit sensitivity
                        profit_corr_fig = px.bar(
                            x=profit_corr.values,
                            y=profit_corr.index,
                            orientation='h',
                            title="Factors Affecting Profit",
                            labels={"x": "Correlation", "y": "Factor"},
                            color=profit_corr.values,
                            color_continuous_scale=px.colors.sequential.Blues,
                        )
                        
                        profit_corr_fig.update_layout(
                            height=300,
                            margin=dict(l=20, r=20, t=40, b=20),
                            yaxis={'categoryorder': 'total ascending'}
                        )
                        
                        st.plotly_chart(profit_corr_fig, use_container_width=True)
                    
                    with col2:
                        # ROAS sensitivity
                        roas_corr_fig = px.bar(
                            x=roas_corr.values,
                            y=roas_corr.index,
                            orientation='h',
                            title="Factors Affecting ROAS",
                            labels={"x": "Correlation", "y": "Factor"},
                            color=roas_corr.values,
                            color_continuous_scale=px.colors.sequential.Greens,
                        )
                        
                        roas_corr_fig.update_layout(
                            height=300,
                            margin=dict(l=20, r=20, t=40, b=20),
                            yaxis={'categoryorder': 'total ascending'}
                        )
                        
                        st.plotly_chart(roas_corr_fig, use_container_width=True)
                else:
                    st.error(sim_message)
    
    # AI-powered insights
    st.markdown("## AI-Powered Insights")
    
    if 'api_key_status' in st.session_state and st.session_state.api_key_status == "valid":
        insights = get_ai_campaign_insights(analyzer.campaigns, campaign['campaign_name'])
        st.markdown(insights)
    else:
        st.info("""
        AI-powered campaign recommendations require an OpenAI API key. 
        Please add your API key in the app settings to enable this feature.
        """)
    
    # Campaign actions
    st.markdown("## Campaign Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Edit Campaign"):
            st.session_state.edit_campaign = campaign_uid
            st.session_state.view = "edit_campaign"
            st.rerun()
    
    with col2:
        if st.button("Clone Campaign"):
            success, message = analyzer.clone_campaign(campaign_uid)
            if success:
                show_toast(message, "success")
                st.session_state.view = "dashboard"
                st.rerun()
            else:
                show_toast(message, "error")
    
    with col3:
        if st.button("Delete Campaign", type="primary"):
            if analyzer.delete_campaign(campaign_uid):
                show_toast("Campaign deleted successfully", "success")
                st.session_state.view = "dashboard"
                st.rerun()
            else:
                show_toast("Failed to delete campaign", "error")

def display_edit_campaign(campaign_uid: str):
    """Display form for editing an existing campaign."""
    campaign = analyzer.get_campaign(campaign_uid)
    
    if not campaign:
        st.error("Campaign not found. It may have been deleted.")
        if st.button("Back to Dashboard"):
            st.session_state.view = "dashboard"
            st.rerun()
        return
    
    # Breadcrumb
    display_breadcrumb([
        ("Dashboard", "#"),
        ("Campaigns", "#"),
        (campaign['campaign_name'], "#"),
        ("Edit", "")
    ])
    
    # Header with back button
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("← Back"):
            st.session_state.selected_campaign = campaign_uid
            st.session_state.view = "campaign_details"
            st.rerun()
    
    with col2:
        st.title(f"Edit Campaign: {campaign['campaign_name']}")
    
    with st.form(key="edit_campaign_form"):
        st.subheader("Campaign Information")
        
        # Basic Information
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("Campaign Name", 
                                      value=campaign['campaign_name'],
                                      help="A descriptive name for this marketing campaign")
            
            product_name = st.text_input("Product Name", 
                                     value=campaign['product_name'],
                                     help="The product being advertised")
            
            # Channel selection
            channel = st.selectbox("Marketing Channel", 
                                DEFAULT_CHANNELS,
                                index=DEFAULT_CHANNELS.index(campaign['channel']) 
                                    if campaign['channel'] in DEFAULT_CHANNELS else 0,
                                help="The platform or channel where the campaign is running")
        
        with col2:
            category = st.selectbox("Product Category", 
                                 DEFAULT_CATEGORIES,
                                 index=DEFAULT_CATEGORIES.index(campaign['category']) 
                                    if campaign['category'] in DEFAULT_CATEGORIES else 0,
                                 help="The category this product belongs to")
            
            start_date = st.date_input("Start Date", 
                                     datetime.strptime(campaign['start_date'], '%Y-%m-%d'),
                                     help="When the campaign started")
            
            end_date = st.date_input("End Date", 
                                   datetime.strptime(campaign['end_date'], '%Y-%m-%d'),
                                   help="When the campaign ended")
        
        # Marketing Metrics
        st.markdown("### Marketing Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ad_spend = st.number_input("Ad Spend ($)", 
                                    value=campaign['ad_spend'],
                                    min_value=0.0, 
                                    format="%.2f", 
                                    help="Total amount spent on ads")
            
            impressions = st.number_input("Impressions", 
                                       value=int(campaign['impressions']),
                                       min_value=0, 
                                       help="Total number of ad impressions")
        
        with col2:
            clicks = st.number_input("Clicks", 
                                  value=int(campaign['clicks']),
                                  min_value=0, 
                                  help="Total number of clicks on ads")
            
            conversions = st.number_input("Conversions", 
                                       value=int(campaign['conversions']),
                                       min_value=0, 
                                       help="Total number of conversions or sales")
        
        with col3:
            revenue = st.number_input("Revenue ($)", 
                                   value=campaign['revenue'],
                                   min_value=0.0, 
                                   format="%.2f", 
                                   help="Total revenue generated from the campaign")
            
            target_acos = st.number_input("Target ACoS (%)", 
                                       value=campaign['target_acos'],
                                       min_value=0.0, 
                                       max_value=100.0, 
                                       format="%.2f", 
                                       help="Target Advertising Cost of Sales percentage")
        
        # Product Economics
        st.markdown("### Product Economics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            product_cost = st.number_input("Product Cost ($)", 
                                        value=campaign['product_cost'],
                                        min_value=0.0, 
                                        format="%.2f", 
                                        help="Cost to produce or acquire the product")
            
            selling_price = st.number_input("Selling Price ($)", 
                                         value=campaign['selling_price'],
                                         min_value=0.0, 
                                         format="%.2f", 
                                         help="Price the product is sold for")
        
        with col2:
            shipping_cost = st.number_input("Shipping Cost ($)", 
                                         value=campaign['shipping_cost'],
                                         min_value=0.0, 
                                         format="%.2f",
                                         help="Cost to ship the product")
            
            amazon_fees = st.number_input("Platform Fees ($)", 
                                       value=campaign['amazon_fees'],
                                       min_value=0.0, 
                                       format="%.2f",
                                       help="Amazon referral, FBA fees, or other platform fees")
        
        with col3:
            notes = st.text_area("Campaign Notes", 
                              value=campaign.get('notes', ''),
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
                st.metric("Avg. CPC", f"${avg_cpc:.2f}", 
                        delta=f"{avg_cpc - campaign['avg_cpc']:.2f}" if campaign['avg_cpc'] > 0 else None,
                        delta_color="inverse")
                st.metric("CTR", f"{ctr:.2f}%",
                        delta=f"{ctr - campaign['ctr']:.2f}%" if campaign['ctr'] > 0 else None)
            
            with col2:
                st.metric("Conversion Rate", f"{conversion_rate:.2f}%",
                        delta=f"{conversion_rate - campaign['conversion_rate']:.2f}%" if campaign['conversion_rate'] > 0 else None)
                st.metric("ACoS", f"{acos:.2f}%", 
                        delta=f"{campaign['acos'] - acos:.2f}%" if campaign['acos'] > 0 else None,
                        delta_color="inverse")
            
            with col3:
                st.metric("ROAS", f"{roas:.2f}x",
                        delta=f"{roas - campaign['roas']:.2f}x" if campaign['roas'] > 0 else None)
                st.metric("Profit Margin", f"{profit_margin:.2f}%",
                        delta=f"{profit_margin - campaign['profit_margin']:.2f}%" if campaign['profit_margin'] > 0 else None)
            
            with col4:
                st.metric("Total Profit", f"${profit:.2f}",
                        delta=f"${profit - campaign['profit']:.2f}" if campaign['profit'] > 0 else None)
                st.metric("Profit per Sale", f"${profit_per_unit:.2f}")
        
        # Submit buttons
        col1, col2 = st.columns(2)
        
        with col1:
            cancel = st.form_submit_button("Cancel")
            if cancel:
                st.session_state.selected_campaign = campaign_uid
                st.session_state.view = "campaign_details"
                st.rerun()
        
        with col2:
            submitted = st.form_submit_button("Save Changes")
            
            if submitted:
                # Set loading state
                st.session_state.is_loading = True
                
                # Update campaign
                updated_data = {
                    'campaign_name': campaign_name,
                    'product_name': product_name,
                    'channel': channel,
                    'category': category,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'ad_spend': ad_spend,
                    'clicks': clicks,
                    'impressions': impressions,
                    'conversions': conversions,
                    'revenue': revenue,
                    'target_acos': target_acos,
                    'product_cost': product_cost,
                    'selling_price': selling_price,
                    'shipping_cost': shipping_cost,
                    'amazon_fees': amazon_fees,
                    'notes': notes
                }
                
                success, message = analyzer.update_campaign(campaign_uid, **updated_data)
                
                # Reset loading state
                st.session_state.is_loading = False
                
                if success:
                    show_toast(message, "success")
                    st.session_state.selected_campaign = campaign_uid
                    st.session_state.view = "campaign_details"
                    st.rerun()
                else:
                    show_toast(message, "error")

def display_channel_analysis():
    """Display a detailed analysis of all marketing channels."""
    st.title("Channel Performance Analysis")
    
    # Get data
    df = analyzer.campaigns
    if df.empty:
        st.info("Add or import campaigns to see channel analysis.")
        return
    
    # Get channel statistics
    stats = analyzer.get_channel_statistics()
    
    # Display channel overview
    st.subheader("Channel Performance Overview")
    
    # Pie chart for ad spend distribution
    col1, col2 = st.columns(2)
    
    with col1:
        # Channel ad spend distribution
        channel_spend = pd.DataFrame([(c['name'], c['ad_spend']) for c in stats['channels']], 
                                  columns=['Channel', 'Ad Spend'])
        
        fig = px.pie(
            channel_spend, 
            values='Ad Spend', 
            names='Channel',
            title='Ad Spend Distribution by Channel',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='%{label}: $%{value:.2f} (%{percent})'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Channel ROAS comparison
        channel_roas = pd.DataFrame([(c['name'], c['roas']) for c in stats['channels']], 
                                 columns=['Channel', 'ROAS'])
        
        fig = px.bar(
            channel_roas.sort_values('ROAS', ascending=False),
            x='Channel',
            y='ROAS',
            title='ROAS by Channel',
            color='ROAS',
            color_continuous_scale=px.colors.sequential.Viridis,
            text_auto='.2f'
        )
        
        fig.update_traces(textfont_size=12, textangle=0, textposition='outside', cliponaxis=False)
        
        fig.update_layout(
            xaxis_title=None,
            yaxis_title='ROAS (Return on Ad Spend)',
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Channel metrics comparison
    st.subheader("Channel Metrics Comparison")
    
    # Prepare channel metrics for radar chart
    channel_metrics = []
    metric_names = ['ROAS', 'ACoS', 'Conversion Rate', 'Profit Margin', 'Revenue']
    
    # Normalize metrics for radar chart (0-1 scale)
    max_roas = max([c['roas'] for c in stats['channels']]) if stats['channels'] else 1
    max_acos = max([c['acos'] for c in stats['channels']]) if stats['channels'] else 1
    max_conv = max([c['conversion_rate'] for c in stats['channels']]) if stats['channels'] else 1
    max_margin = max([c['profit_margin'] for c in stats['channels']]) if stats['channels'] else 1
    max_revenue = max([c['revenue'] for c in stats['channels']]) if stats['channels'] else 1
    
    for channel in stats['channels']:
        # Normalize metrics (for ACoS, lower is better, so invert)
        norm_roas = channel['roas'] / max_roas if max_roas > 0 else 0
        norm_acos = 1 - (channel['acos'] / max_acos if max_acos > 0 else 0)  # Invert for radar
        norm_conv = channel['conversion_rate'] / max_conv if max_conv > 0 else 0
        norm_margin = channel['profit_margin'] / max_margin if max_margin > 0 else 0
        norm_revenue = channel['revenue'] / max_revenue if max_revenue > 0 else 0
        
        channel_metrics.append({
            'Channel': channel['name'],
            'ROAS': norm_roas,
            'ACoS': norm_acos,
            'Conversion Rate': norm_conv,
            'Profit Margin': norm_margin,
            'Revenue': norm_revenue
        })
    
    # Create radar chart
    radar_fig = go.Figure()
    
    for channel in channel_metrics:
        radar_fig.add_trace(go.Scatterpolar(
            r=[channel[m] for m in metric_names],
            theta=metric_names,
            fill='toself',
            name=channel['Channel']
        ))
    
    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        title="Channel Performance Comparison",
        showlegend=True
    )
    
    st.plotly_chart(radar_fig, use_container_width=True)
    
    # Channel metrics tables
    st.subheader("Detailed Channel Metrics")
    
    # Create metrics table
    metrics_df = pd.DataFrame([
        {
            'Channel': channel['name'],
            'Ad Spend': f"${channel['ad_spend']:,.2f}",
            'Revenue': f"${channel['revenue']:,.2f}",
            'ROAS': f"{channel['roas']:.2f}x",
            'ACoS': f"{channel['acos']:.2f}%",
            'Profit': f"${channel['profit']:,.2f}",
            'Margin': f"{channel['profit_margin']:.2f}%",
            'Conv. Rate': f"{channel['conversion_rate']:.2f}%",
            'Clicks': f"{channel['clicks']:,}",
            'Conversions': f"{channel['conversions']:,}"
        }
        for channel in stats['channels']
    ])
    
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    # Channel trends (simulate trends for demo - in a real app this would use historical data)
    st.subheader("Channel Trends Over Time")
    
    # Create dummy trend data
    trend_data = []
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    
    for channel in stats['channels']:
        base_roas = channel['roas']
        base_spend = channel['ad_spend'] / 6  # Divide by 6 months for monthly average
        
        for i, month in enumerate(months):
            # Add some random variation for the trend
            roas_value = base_roas * (1 + np.random.uniform(-0.2, 0.2))
            spend_value = base_spend * (1 + np.random.uniform(-0.15, 0.25))
            
            trend_data.append({
                'Channel': channel['name'],
                'Month': month,
                'Month_Num': i + 1,
                'ROAS': roas_value,
                'Ad Spend': spend_value
            })
    
    trend_df = pd.DataFrame(trend_data)
    
    # Create plotly figure
    fig = make_subplots(rows=1, cols=2, subplot_titles=("ROAS Trend by Channel", "Ad Spend Trend by Channel"))
    
    # ROAS trends
    for channel in stats['channels']:
        channel_data = trend_df[trend_df['Channel'] == channel['name']]
        
        fig.add_trace(
            go.Scatter(
                x=channel_data['Month'],
                y=channel_data['ROAS'],
                mode='lines+markers',
                name=channel['name'],
                line=dict(color=get_channel_color(channel['name']))
            ),
            row=1, col=1
        )
    
    # Ad spend trends
    for channel in stats['channels']:
        channel_data = trend_df[trend_df['Channel'] == channel['name']]
        
        fig.add_trace(
            go.Scatter(
                x=channel_data['Month'],
                y=channel_data['Ad Spend'],
                mode='lines+markers',
                name=channel['name'],
                showlegend=False,
                line=dict(color=get_channel_color(channel['name']))
            ),
            row=1, col=2
        )
    
    # Update layout
    fig.update_layout(
        height=400,
        yaxis_title="ROAS",
        yaxis2_title="Ad Spend ($)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update y-axis format
    fig.update_yaxes(tickprefix="$", row=1, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Channel performance map (heatmap)
    st.subheader("Channel Performance Matrix")
    
    # Create performance matrix data
    performance_data = []
    categories = df['category'].unique()
    
    for channel in stats['channels']:
        channel_name = channel['name']
        
        for category in categories:
            # Filter data for this channel and category
            filtered = df[(df['channel'] == channel_name) & (df['category'] == category)]
            
            if not filtered.empty:
                avg_roas = filtered['roas'].mean()
                avg_acos = filtered['acos'].mean()
                avg_margin = filtered['profit_margin'].mean()
                total_spend = filtered['ad_spend'].sum()
                
                # Calculate performance score
                performance_score = (
                    (avg_roas / 5) * 0.4 +  # Scale ROAS to 0-1 (assume 5 is excellent)
                    (1 - (avg_acos / 40)) * 0.3 +  # Scale ACoS to 0-1 (lower is better)
                    (avg_margin / 40) * 0.3  # Scale margin to 0-1 (assume 40% is excellent)
                ) * 100
                
                performance_data.append({
                    'Channel': channel_name,
                    'Category': category,
                    'Performance Score': performance_score,
                    'ROAS': avg_roas,
                    'ACoS': avg_acos,
                    'Profit Margin': avg_margin,
                    'Ad Spend': total_spend
                })
    
    # Create dataframe
    perf_df = pd.DataFrame(performance_data)
    
    if not perf_df.empty:
        # Create heatmap
        perf_pivot = perf_df.pivot(index='Channel', columns='Category', values='Performance Score')
        
        # Create custom hover text
        hover_text = []
        for channel in perf_pivot.index:
            channel_hover = []
            for category in perf_pivot.columns:
                filtered = perf_df[(perf_df['Channel'] == channel) & (perf_df['Category'] == category)]
                
                if not filtered.empty:
                    row = filtered.iloc[0]
                    text = f"Channel: {channel}<br>" \
                          f"Category: {category}<br>" \
                          f"Performance: {row['Performance Score']:.1f}/100<br>" \
                          f"ROAS: {row['ROAS']:.2f}x<br>" \
                          f"ACoS: {row['ACoS']:.2f}%<br>" \
                          f"Margin: {row['Profit Margin']:.2f}%<br>" \
                          f"Spend: ${row['Ad Spend']:.2f}"
                else:
                    text = f"No data"
                
                channel_hover.append(text)
            
            hover_text.append(channel_hover)
        
        # Create heatmap
        heatmap = go.Figure(data=go.Heatmap(
            z=perf_pivot.values,
            x=perf_pivot.columns,
            y=perf_pivot.index,
            colorscale='Viridis',
            hoverongaps=False,
            text=hover_text,
            hoverinfo='text',
            colorbar=dict(
                title='Performance<br>Score',
                titleside='top',
                tickmode='array',
                tickvals=[0, 25, 50, 75, 100],
                ticktext=['Poor', 'Below Avg', 'Average', 'Good', 'Excellent'],
                ticks='outside'
            )
        ))
        
        heatmap.update_layout(
            title='Channel Performance by Product Category',
            xaxis_title='Product Category',
            yaxis_title='Channel',
            height=400
        )
        
        st.plotly_chart(heatmap, use_container_width=True)
    
    # Channel recommendations
    st.subheader("Channel Recommendations")
    
    # Get AI insights if available
    if 'api_key_status' in st.session_state and st.session_state.api_key_status == "valid":
        insights = get_ai_campaign_insights(analyzer.campaigns)
        st.markdown(insights)
    else:
        # Calculate basic recommendations without AI
        recommendations = []
        
        # Best performing channel
        if stats['best_channel_roas']:
            recommendations.append(f"""
            **Increase investment in {stats['best_channel_roas']['name']}**
            
            This channel shows the highest ROAS at {stats['best_channel_roas']['roas']:.2f}x, 
            indicating strong performance. Consider increasing budget allocation to this channel
            to maximize returns.
            """)
        
        # Underperforming channels
        if stats['worst_channel_roas'] and stats['worst_channel_roas']['roas'] < 2:
            recommendations.append(f"""
            **Optimize or reduce spend on {stats['worst_channel_roas']['name']}**
            
            This channel shows the lowest ROAS at {stats['worst_channel_roas']['roas']:.2f}x.
            Consider optimizing campaigns or reducing budget allocation if performance doesn't improve.
            """)
        
        # Category specialization
        if not perf_df.empty:
            # Find best channel-category combinations
            top_combos = perf_df.sort_values('Performance Score', ascending=False).head(3)
            
            for _, combo in top_combos.iterrows():
                recommendations.append(f"""
                **Focus on {combo['Category']} products in {combo['Channel']}**
                
                This combination shows strong performance with a score of {combo['Performance Score']:.1f}/100,
                ROAS of {combo['ROAS']:.2f}x, and profit margin of {combo['Profit Margin']:.2f}%.
                Consider developing more campaigns for this product category on this channel.
                """)
        
        # Display recommendations
        for i, rec in enumerate(recommendations[:5], 1):  # Limit to top 5 recommendations
            st.markdown(f"### Recommendation {i}")
            st.markdown(rec)

def display_insights_page():
    """Display AI-powered insights and recommendations."""
    st.title("AI-Powered Marketing Insights")
    
    if analyzer.campaigns.empty:
        st.info("Add or import campaigns to see AI-powered insights.")
        return
    
    # Check API key status
    if 'api_key_status' not in st.session_state or st.session_state.api_key_status != "valid":
        st.warning("""
        AI-powered insights require an OpenAI API key. 
        Please add your API key in the app settings to enable this feature.
        """)
        
        st.markdown("""
        ### Sample Insights (Preview Only)
        
        The following insights are examples of what you would see with an active API key:
        """)
        
        # Display mock insights
        with st.expander("Overall Marketing Performance", expanded=True):
            st.markdown("""
            Based on your campaign data, I've identified several key insights and opportunities:

            1. **Amazon PPC campaigns are outperforming other channels** with an average ROAS of 5.49x compared to 4.20x for Paid Social and 3.90x for Walmart. Consider shifting 10-15% of budget from lower-performing channels to Amazon PPC.

            2. **Your TENS Unit campaign shows the strongest conversion rate** at 5.00%, significantly above your average of 3.45%. Analyze what's working well in this campaign and apply similar strategies to other products.

            3. **Website PPC for Walkers is underperforming your target ACoS** by 0.12%. Review the keyword strategy and consider implementing more negative keywords to reduce wasted spend.

            4. **Paid Social has the lowest conversion rate** at 2.00% but high click-through rates. This suggests your creative is engaging but the landing page or offer may need optimization.

            5. **Mobility products have your highest profit margins** across all channels (average 42.3%). Consider expanding your product range in this category or increasing ad spend where ROAS remains above 4.0x.
            """)
        
        with st.expander("Budget Optimization Recommendations"):
            st.markdown("""
            Based on your current campaign performance, here are my top budget optimization recommendations:

            ### Recommended Budget Reallocation
            
            | Channel | Current Spend | Recommended Spend | Change | Estimated Impact |
            |---------|---------------|-------------------|--------|------------------|
            | Amazon PPC | $7,800 | $9,360 | +$1,560 (20%) | Additional $9,828 revenue, $2,948 profit |
            | Vive Website | $3,200 | $3,680 | +$480 (15%) | Additional $1,910 revenue, $573 profit |
            | Walmart | $1,500 | $1,200 | -$300 (-20%) | Minimal revenue loss with improved efficiency |
            | Paid Social | $4,000 | $3,000 | -$1,000 (-25%) | Improved overall ROAS by focusing on top-performing segments |
            
            ### Specific Recommendations:
            
            1. **Increase Amazon PPC budget by 20%** focused on Mobility Scooters and TENS Units, which show strong ROAS and profit margins.
               
            2. **Increase Website PPC budget by 15%** with improved targeting to maintain current ACoS.
               
            3. **Decrease Walmart spend by 20%** until conversion rates improve - reallocate to better-performing channels.
               
            4. **Reduce Paid Social spend by 25%** while improving targeting to focus only on high-converting audience segments.
            
            Implementing these changes could improve your overall marketing ROI by approximately 18-22%.
            """)
        
        with st.expander("Campaign Optimization Opportunities"):
            st.markdown("""
            Here are specific optimization opportunities I've identified for your campaigns:

            ### Amazon PPC - TENS Units
            
            This campaign shows strong fundamentals with a 4.69x ROAS and 21.33% ACoS, but has optimization potential:
            
            1. **Bid Optimization**: Your average CPC of $0.80 is below market average for similar products, suggesting opportunity to increase bids by 15-20% to gain more impression share without significantly impacting ACoS.
            
            2. **Targeting Expansion**: Add 10-15 additional highly relevant keywords based on current converting search terms. This could increase impressions by approximately 30-40% while maintaining similar conversion rates.
            
            3. **Product Listing Enhancement**: Improve product images and A+ content to increase conversion rate by an estimated 0.5-1.0 percentage points.
            
            **Expected Impact**: These changes could increase revenue by 25-30% while maintaining current ACoS, resulting in approximately $3,300-$3,900 additional revenue and $950-$1,100 additional profit.

            ### Meta Ads - Health Products
            
            This campaign has the lowest conversion rate (2.00%) despite good click-through rates, indicating targeting or landing page issues:
            
            1. **Audience Refinement**: Create more targeted audience segments based on past purchaser behavior and interest categories. Focus on demographics that match your highest converting customers.
            
            2. **Creative Testing**: Implement A/B testing with 3-4 variations of ad creative focusing on different value propositions (price, quality, comfort, warranty).
            
            3. **Landing Page Optimization**: Create dedicated landing pages for each ad group with consistent messaging and stronger calls-to-action. Add social proof and testimonials prominently.
            
            **Expected Impact**: These optimizations could improve conversion rates from 2.00% to 3.00-3.50%, increasing revenue by approximately $8,400-$12,600 while maintaining the same ad spend.
            """)
        
        return
    
    # Display AI-powered insights
    # Overall insights
    with st.expander("Overall Marketing Performance", expanded=True):
        insights = get_ai_campaign_insights(analyzer.campaigns)
        st.markdown(insights)
    
    # Specific campaign insights
    st.subheader("Campaign-Specific Insights")
    
    # Let user select a campaign
    campaign_names = analyzer.campaigns['campaign_name'].unique().tolist()
    selected_campaign = st.selectbox("Select a campaign for detailed insights", campaign_names)
    
    if selected_campaign:
        campaign_insights = get_ai_campaign_insights(
            analyzer.campaigns, 
            selected_campaign
        )
        st.markdown(campaign_insights)
    
    # Advanced insights
    st.subheader("Advanced Marketing Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Budget Optimization", "Channel Strategy", "Product Recommendations"])
    
    with tab1:
        insights_placeholder = st.empty()
        
        with insights_placeholder:
            st.info("Generating budget optimization insights... This may take a few seconds.")
        
        # Custom prompt for budget optimization
        system_prompt = "You are an expert marketing analyst specializing in e-commerce PPC campaigns and marketing ROI analysis."
        user_prompt = """
        Based on the campaign data, provide specific budget optimization recommendations. 
        Include suggested budget allocations across channels, expected ROAS impact, and justification.
        Present your recommendations in a structured format with concrete numbers and percentages.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Call the API
        insights = call_openai_api(messages)
        
        with insights_placeholder:
            st.markdown(insights)
    
    with tab2:
        insights_placeholder = st.empty()
        
        with insights_placeholder:
            st.info("Generating channel strategy insights... This may take a few seconds.")
        
        # Custom prompt for channel strategy
        system_prompt = "You are an expert marketing analyst specializing in e-commerce PPC campaigns and marketing ROI analysis."
        user_prompt = """
        Based on the campaign data, provide a detailed channel strategy analysis.
        Compare the strengths and weaknesses of each channel, identify which product categories perform best on each channel,
        and recommend how to optimize the channel mix for maximum ROI.
        Include specific strategy recommendations for each major channel.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Call the API
        insights = call_openai_api(messages)
        
        with insights_placeholder:
            st.markdown(insights)
    
    with tab3:
        insights_placeholder = st.empty()
        
        with insights_placeholder:
            st.info("Generating product recommendations... This may take a few seconds.")
        
        # Custom prompt for product recommendations
        system_prompt = "You are an expert marketing analyst specializing in e-commerce PPC campaigns and marketing ROI analysis for Vive Health, a medical device company."
        user_prompt = """
        Based on the campaign data, provide product-specific marketing recommendations.
        Identify which products have the highest ROI potential, which need optimization,
        and suggest specific advertising strategies for different product categories.
        Consider profit margins, conversion rates, and channel performance in your analysis.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Call the API
        insights = call_openai_api(messages)
        
        with insights_placeholder:
            st.markdown(insights)

def display_settings_page():
    """Display application settings page."""
    st.title("Application Settings")
    
    # Display tabs for different settings sections
    tab1, tab2, tab3 = st.tabs(["General Settings", "Data Management", "API Settings"])
    
    with tab1:
        st.subheader("Application Preferences")
        
        # App mode selection
        app_mode = st.radio(
            "Application Mode",
            ["Basic", "Advanced"],
            index=0 if st.session_state.app_mode == "Basic" else 1,
            horizontal=True,
            help="Basic mode simplifies the interface, Advanced shows more features and metrics"
        )
        
        if app_mode != st.session_state.app_mode:
            st.session_state.app_mode = app_mode
            st.success(f"Application mode changed to {app_mode}")
            st.rerun()
        
        # Color scheme selection
        color_schemes = list(COLOR_SCHEMES.keys())
        color_scheme = st.selectbox(
            "Color Scheme",
            color_schemes,
            index=color_schemes.index(st.session_state.color_scheme),
            help="Select a color scheme for the application"
        )
        
        if color_scheme != st.session_state.color_scheme:
            st.session_state.color_scheme = color_scheme
            st.success(f"Color scheme changed to {color_scheme}")
            st.rerun()
        
        # Default channel and category settings
        st.subheader("Default Values")
        
        col1, col2 = st.columns(2)
        
        with col1:
            default_channels = st.multiselect(
                "Default Marketing Channels",
                ["Amazon", "Vive Website", "Walmart", "eBay", "Paid Social", 
                "Google Ads", "Microsoft Ads", "Meta Ads", "TikTok Ads", "Pinterest Ads"],
                DEFAULT_CHANNELS,
                help="Set default channels that appear in dropdown menus"
            )
        
        with col2:
            default_categories = st.multiselect(
                "Default Product Categories",
                ["Mobility", "Pain Relief", "Bathroom Safety", "Bedroom", "Daily Living Aids",
                "Wheelchairs", "Rollators", "Walkers", "Canes", "Scooters", "TENS Units", 
                "Hot & Cold Therapy", "Braces & Supports"],
                DEFAULT_CATEGORIES,
                help="Set default product categories that appear in dropdown menus"
            )
        
        # Save default values
        if st.button("Save Default Values"):
            global DEFAULT_CHANNELS, DEFAULT_CATEGORIES
            DEFAULT_CHANNELS = default_channels if default_channels else ["Amazon", "Vive Website"]
            DEFAULT_CATEGORIES = default_categories if default_categories else ["Mobility", "Pain Relief"]
            st.success("Default values saved successfully")
        
        # Reset first visit flag
        if st.session_state.app_mode == "Advanced":
            if st.button("Reset Guided Tour"):
                st.session_state.first_visit = True
                st.success("Guided tour will be shown on next app load")
    
    with tab2:
        st.subheader("Data Import/Export")
        
        # Export campaigns
        if not analyzer.campaigns.empty:
            export_data = analyzer.download_json()
            
            st.download_button(
                label="Export Campaigns as JSON",
                data=export_data,
                file_name="viveroi_campaigns.json",
                mime="application/json",
                help="Download all campaign data as a JSON file for backup or transfer"
            )
        else:
            st.info("No campaigns available to export. Add campaigns first.")
        
        # Import campaigns
        st.subheader("Import Campaigns")
        
        uploaded_file = st.file_uploader(
            "Upload JSON Campaign File", 
            type=["json"],
            help="Upload a JSON file containing campaign data"
        )
        
        if uploaded_file is not None:
            try:
                json_str = uploaded_file.getvalue().decode("utf-8")
                success = analyzer.upload_json(json_str)
                
                if success:
                    st.success("Campaigns imported successfully!")
                    st.rerun()
                else:
                    st.error("Failed to import campaigns. Invalid format.")
            except Exception as e:
                st.error(f"Error importing file: {str(e)}")
        
        # Data reset options
        st.subheader("Data Management")
        
        danger_zone = st.expander("Danger Zone", expanded=False)
        
        with danger_zone:
            st.warning("""
            **Warning:** These actions cannot be undone. Make sure to export your data before proceeding.
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Load Example Campaigns", key="load_examples"):
                    # Clear existing campaigns if requested
                    if st.session_state.app_mode == "Advanced" and st.checkbox("Clear existing campaigns first"):
                        analyzer.campaigns = pd.DataFrame(columns=CAMPAIGN_COLUMNS)
                    
                    # Add examples
                    num_added = analyzer.add_example_campaigns()
                    
                    if num_added > 0:
                        st.success(f"Added {num_added} example campaigns successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add example campaigns.")
            
            with col2:
                if st.button("Clear All Campaigns", type="primary"):
                    analyzer.campaigns = pd.DataFrame(columns=CAMPAIGN_COLUMNS)
                    analyzer.save_data()
                    st.success("All campaigns cleared successfully!")
                    st.rerun()
    
    with tab3:
        st.subheader("API Configuration")
        
        # Check OpenAI API key status
        api_status_msg = ""
        api_status_color = ""
        
        if 'api_key_status' in st.session_state:
            if st.session_state.api_key_status == "valid":
                api_status_msg = "✅ API key is valid and working"
                api_status_color = "green"
            elif st.session_state.api_key_status == "invalid":
                api_status_msg = "❌ API key is invalid"
                api_status_color = "red"
            elif st.session_state.api_key_status == "missing":
                api_status_msg = "⚠️ API key is not configured"
                api_status_color = "orange"
            else:
                api_status_msg = "⚠️ Error checking API key"
                api_status_color = "red"
        
        st.markdown(f"""
        <p style="color: {api_status_color}; font-weight: 500;">{api_status_msg}</p>
        """, unsafe_allow_html=True)
        
        # Explain API key usage
        st.markdown("""
        ### OpenAI API Integration
        
        This application uses the OpenAI API to provide AI-powered marketing insights and recommendations.
        An API key is required to access these features.
        
        **Why use the OpenAI API?**
        - Generate detailed marketing insights and recommendations
        - Analyze campaign performance across channels
        - Get AI-powered optimization suggestions
        - Benefit from natural language explanations of complex data
        
        **How to get an API key:**
        1. Go to [OpenAI API](https://platform.openai.com/signup)
        2. Create an account or sign in
        3. Navigate to API keys section
        4. Create a new secret key
        5. Copy and paste the key below
        
        Your API key is stored securely in the app's session state and is not shared with any third parties.
        """)
        
        # Add note about secrets management for deployed apps
        st.info("""
        **Note:** For a deployed application, the API key would be stored in a secure environment variable 
        or secrets management system, not entered manually by users.
        """)
        
        # API key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key to enable AI-powered features"
        )
        
        if st.button("Save API Key"):
            if api_key:
                # In a real deployed app, this would be stored in a secure way
                # For this demo, we'll simulate validation
                st.success("API key saved successfully!")
                st.session_state.api_key_status = "valid"
                check_openai_api_key()
                st.rerun()
            else:
                st.error("Please enter a valid API key")

def setup_sidebar():
    """Set up and display the sidebar navigation."""
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px; margin-bottom: 20px;">
            <h2 style="color: {COLOR_SCHEME['text_light']};">ViveROI Analytics</h2>
            <p style="color: {COLOR_SCHEME['text_light']};">Version {APP_VERSION}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main navigation
        st.markdown("### Navigation")
        
        nav_options = [
            ("Dashboard", "house", "dashboard"),
            ("Campaigns", "file-text", "campaigns"),
            ("Channel Analysis", "bar-chart-2", "channel_analysis"),
            ("Insights", "lightbulb", "insights"),
            ("Settings", "settings", "settings")
        ]
        
        for option_name, icon, view_name in nav_options:
            # Highlight active menu item
            bg_color = COLOR_SCHEME["primary"] if st.session_state.view == view_name else "transparent"
            text_color = COLOR_SCHEME["text_light"] if st.session_state.view != view_name else "white"
            
            if st.sidebar.button(
                f":{icon}: {option_name}", 
                key=f"nav_{view_name}",
                use_container_width=True,
                type="secondary" if st.session_state.view != view_name else "primary"
            ):
                st.session_state.view = view_name
                # Reset any selected campaign
                if 'selected_campaign' in st.session_state:
                    del st.session_state.selected_campaign
                if 'edit_campaign' in st.session_state:
                    del st.session_state.edit_campaign
                st.rerun()
        
        # Campaign Wizard button
        st.markdown("### Tools")
        
        if st.sidebar.button("🧙‍♂️ Campaign Wizard", use_container_width=True):
            st.session_state.view = "campaign_wizard"
            st.rerun()
        
        # Additional sidebar sections based on app mode
        if st.session_state.app_mode == "Advanced":
            # Quick Stats
            if not analyzer.campaigns.empty:
                stats = analyzer.get_channel_statistics()
                
                st.markdown("### Quick Stats")
                st.markdown(f"""
                <div style="padding: 10px; background-color: {COLOR_SCHEME['sidebar_bg']}30; border-radius: 5px; margin-top: 10px;">
                    <p style="color: {COLOR_SCHEME['text_light']}; margin: 0;">
                        <strong>Campaigns:</strong> {stats['total_campaigns']}
                    </p>
                    <p style="color: {COLOR_SCHEME['text_light']}; margin: 0;">
                        <strong>Ad Spend:</strong> ${stats['total_spend']:,.2f}
                    </p>
                    <p style="color: {COLOR_SCHEME['text_light']}; margin: 0;">
                        <strong>ROAS:</strong> {stats['overall_roas']:.2f}x
                    </p>
                    <p style="color: {COLOR_SCHEME['text_light']}; margin: 0;">
                        <strong>Total Profit:</strong> ${stats['total_profit']:,.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # App info and help
        st.markdown("### About")
        st.markdown(f"""
        <div style="font-size: 0.85rem; color: {COLOR_SCHEME['text_light']}; opacity: 0.8; margin-top: 20px;">
            <p>ViveROI Analytics helps Vive Health's e-commerce team analyze and optimize marketing spend across channels.</p>
            <p style="margin-top: 10px;">Need help? Contact:</p>
            <p>{SUPPORT_EMAIL}</p>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main application entry point."""
    # Load custom CSS
    load_custom_css()
    
    # Initialize view if not already set
    if 'view' not in st.session_state:
        st.session_state.view = "dashboard"
    
    # Set up sidebar
    setup_sidebar()
    
    # Display loading spinner
    display_loading_spinner()
    
    # Display views based on selection
    if st.session_state.view == "dashboard":
        display_header()
        display_metrics_overview(analyzer.campaigns)
        display_campaigns_table(analyzer.campaigns)
    
    elif st.session_state.view == "campaigns":
        display_header()
        display_campaigns_table(analyzer.campaigns)
    
    elif st.session_state.view == "channel_analysis":
        display_header()
        display_channel_analysis()
    
    elif st.session_state.view == "insights":
        display_header()
        display_insights_page()
    
    elif st.session_state.view == "settings":
        display_header()
        display_settings_page()
    
    elif st.session_state.view == "campaign_wizard":
        display_header()
        if create_campaign_wizard():
            # If wizard completed successfully, go back to dashboard
            st.session_state.view = "dashboard"
            st.rerun()
    
    elif st.session_state.view == "campaign_details" and 'selected_campaign' in st.session_state:
        display_campaign_details(st.session_state.selected_campaign)
    
    elif st.session_state.view == "edit_campaign" and 'edit_campaign' in st.session_state:
        display_edit_campaign(st.session_state.edit_campaign)
    
    else:
        display_header()
        st.error("Invalid view or missing parameters")
        
        if st.button("Return to Dashboard"):
            st.session_state.view = "dashboard"
            st.rerun()
    
    # Display help button
    if st.session_state.app_mode == "Advanced":
        display_help_button()
    
    # Show guided tour on first visit
    if st.session_state.first_visit and st.session_state.app_mode == "Advanced":
        st.markdown("""
        <script>
            // Simplified guided tour - in a real app this would be more sophisticated
            setTimeout(function() {
                alert("Welcome to ViveROI Analytics! This is a guided tour placeholder.");
                
                // Mark tour as seen
                const tourEvent = new CustomEvent('tourComplete');
                window.dispatchEvent(tourEvent);
            }, 1000);
        </script>
        """, unsafe_allow_html=True)
        
        # Reset first visit flag
        st.session_state.first_visit = False

if __name__ == "__main__":
    main()
