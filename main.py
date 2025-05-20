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
import base64
import xlsxwriter
from fpdf import FPDF

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("viveroi_analytics")

# Suppress warnings
warnings.filterwarnings('ignore')

# Version info
APP_VERSION = "1.2.0"
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
        "text_dark": "#f8f9fa", # Inverted for dark mode
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

# Define medical device categories for AI assistant
MEDICAL_DEVICE_CATEGORIES = [
    "Mobility Aids", "Pain Management", "Orthopedic Supports", "Respiratory Devices",
    "Bathroom Safety", "Bedroom Aids", "Daily Living Aids", "Diagnostics",
    "Rehabilitation Equipment", "Wound Care", "Compression Therapy", "Patient Monitoring",
    "Diabetes Management", "Incontinence Care", "Cold & Hot Therapy", "Vision Aids",
    "Hearing Aids", "Electrotherapy", "Bariatric Equipment", "Pediatric Care"
]

# Define Amazon listing categories and topics for the new AI assistant
AMAZON_LISTING_TOPICS = [
    "Product Title Optimization", "Bullet Points Enhancement", "Product Description", 
    "Backend Keywords", "Image Optimization", "A+ Content", "Inventory Management", 
    "Pricing Strategy", "Review Management", "Competitive Analysis", "Brand Registry", 
    "Sponsored Products", "Sponsored Brands", "Sponsored Display", "Amazon DSP",
    "Listing Compliance", "Search Term Optimization", "Variation Setup",
    "Best Seller Rank Improvement", "Amazon Storefront"
]

# =============================================================================
# Custom CSS Styling
# =============================================================================

def load_custom_css():
    """Load custom CSS styling for the application"""
    st.markdown(f"""
    <style>
        /* Dark Mode Detection */
        @media (prefers-color-scheme: dark) {{
            .streamlit-container {{
                background-color: #1E1E1E;
            }}
            .custom-card {{
                background-color: #2E2E2E !important;
                color: #E0E0E0 !important;
            }}
            .custom-text {{
                color: #E0E0E0 !important;
            }}
            .custom-title {{
                color: #FFFFFF !important;
            }}
            .custom-subtitle {{
                color: #CCCCCC !important;
            }}
            .custom-border {{
                border-color: #444444 !important;
            }}
        }}
        
        /* Main styling */
        body, .stApp {{
            background-color: {COLOR_SCHEME["background"]};
            color: {COLOR_SCHEME["text_dark"]};
            font-family: 'Inter', sans-serif;
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            font-weight: 600;
            color: {COLOR_SCHEME["primary"]};
        }}
        
        /* Button styling */
        .stButton>button {{
            background-color: {COLOR_SCHEME["secondary"]};
            color: white;
            border-radius: 6px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            margin-bottom: 10px; /* Added for spacing */
            white-space: nowrap; /* Prevent text wrapping */
            min-width: 120px; /* Minimum width for button consistency */
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
            border-radius: 6px;
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
            border-radius: 8px;
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
            border-radius: 8px;
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
            font-size: 1.75rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.5rem;
        }}
        
        .metric-label {{
            font-size: 0.9rem;
            color: #64748b;
            font-weight: 500;
        }}
        
        /* Enhanced Metric Card */
        .enhanced-metric {{
            background-color: {COLOR_SCHEME["card_bg"]};
            border-radius: 8px;
            padding: 1.25rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            transition: all 0.3s;
            height: 100%;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
            margin-bottom: 15px; /* Added spacing */
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
            font-size: 1.75rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.5rem;
        }}
        
        .enhanced-metric .trend {{
            font-size: 0.85rem;
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
            border-radius: 6px;
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
            border-radius: 6px 6px 0px 0px;
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
            border-radius: 6px;
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
            border-radius: 0 6px 6px 0;
            margin: 1rem 0;
        }}
        
        .warning-box {{
            background-color: rgba(255, 193, 7, 0.1);
            border-left: 5px solid {COLOR_SCHEME["warning"]};
            padding: 1rem;
            border-radius: 0 6px 6px 0;
            margin: 1rem 0;
        }}
        
        .success-box {{
            background-color: rgba(40, 167, 69, 0.1);
            border-left: 5px solid {COLOR_SCHEME["positive"]};
            padding: 1rem;
            border-radius: 0 6px 6px 0;
            margin: 1rem 0;
        }}
        
        .danger-box {{
            background-color: rgba(220, 53, 69, 0.1);
            border-left: 5px solid {COLOR_SCHEME["negative"]};
            padding: 1rem;
            border-radius: 0 6px 6px 0;
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
            border-radius: 8px;
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
            font-size: 20px;
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
            font-size: 16px;
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
        
        /* Chat container */
        .chat-container {{
            display: flex;
            flex-direction: column;
            height: 70vh;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .chat-messages {{
            flex-grow: 1;
            overflow-y: auto;
            padding: 16px;
            background-color: #f8f9fa;
        }}
        
        .chat-input {{
            display: flex;
            padding: 8px;
            background-color: white;
            border-top: 1px solid #e2e8f0;
        }}
        
        .message {{
            max-width: 80%;
            margin-bottom: 12px;
            padding: 10px 14px;
            border-radius: 15px;
            position: relative;
        }}
        
        .message.user {{
            background-color: {COLOR_SCHEME["primary"]};
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 0;
        }}
        
        .message.assistant {{
            background-color: #e2e8f0;
            border-bottom-left-radius: 0;
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
        
        /* Make dataframe more compact */
        .stDataFrame table {{
            font-size: 0.9rem;
        }}
        
        .stDataFrame [data-testid="StyledDataFrameDataCell"] {{
            padding: 6px 8px !important;
        }}
        
        /* Fix for overlapping text */
        .row-widget.stButton {{
            margin-bottom: 12px;
        }}
        
        /* Improve spacing in columns */
        [data-testid="column"] {{
            padding: 0.5rem;
        }}
        
        /* Make plotly charts more compact */
        .stPlotlyChart {{
            margin-bottom: 1rem;
        }}
        
        /* Fix expander padding */
        .streamlit-expanderContent {{
            padding: 0.5rem 1rem;
        }}
        
        /* Amazon Listing Enhancement Chat styling */
        .amazon-chat-container {{
            display: flex;
            flex-direction: column;
            height: 70vh;
            border: 1px solid #f0c14b;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .amazon-chat-header {{
            background-color: #232f3e;
            color: white;
            padding: 12px 16px;
            font-weight: 500;
            display: flex;
            align-items: center;
        }}
        
        .amazon-chat-header .logo {{
            color: #ff9900;
            font-size: 1.2rem;
            margin-right: 10px;
        }}
        
        .amazon-chat-messages {{
            flex-grow: 1;
            overflow-y: auto;
            padding: 16px;
            background-color: #f8f9fa;
        }}
        
        .amazon-chat-input {{
            display: flex;
            padding: 12px;
            background-color: white;
            border-top: 1px solid #e2e8f0;
            align-items: center;
        }}
        
        .amazon-message {{
            max-width: 80%;
            margin-bottom: 16px;
            padding: 12px 16px;
            border-radius: 15px;
            position: relative;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }}
        
        .amazon-message.user {{
            background-color: #232f3e;
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 0;
        }}
        
        .amazon-message.assistant {{
            background-color: #fcfcfc;
            border: 1px solid #e2e8f0;
            border-bottom-left-radius: 0;
        }}
        
        .amazon-suggestion-chips {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
            margin-bottom: 15px;
        }}
        
        .amazon-suggestion-chip {{
            background-color: #f0f2f5;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 6px 12px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .amazon-suggestion-chip:hover {{
            background-color: #e1e4e8;
            border-color: #d0d7de;
        }}
        
        /* Fix for sidebar button spacing and alignment */
        [data-testid="stSidebar"] .stButton > button {{
            margin-bottom: 12px;
            width: 100%;
            text-align: left;
            display: flex;
            align-items: center;
        }}
        
        /* Fix for form field spacing */
        .stForm > div > div > div {{
            margin-bottom: 15px !important;
        }}
        
        /* Fix for button row spacing */
        .stHorizontal > div > .stButton > button {{
            margin-right: 10px;
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

# =============================================================================
# Export Functions
# =============================================================================

def to_excel(df: pd.DataFrame):
    """
    Convert dataframe to Excel file in memory and return for download
    """
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Campaigns', index=False)
    
    # Format the Excel sheet
    workbook = writer.book
    worksheet = writer.sheets['Campaigns']
    
    # Add formats
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1
    })
    
    currency_format = workbook.add_format({'num_format': '$#,##0.00'})
    percent_format = workbook.add_format({'num_format': '0.00%'})
    date_format = workbook.add_format({'num_format': 'mm/dd/yyyy'})
    
    # Apply header format
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    
    # Apply column formats
    for i, col in enumerate(df.columns):
        column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
        worksheet.set_column(i, i, column_width)
        
        # Apply specific formats based on column name
        if col in ['ad_spend', 'revenue', 'profit', 'product_cost', 'selling_price', 'shipping_cost', 'amazon_fees']:
            worksheet.set_column(i, i, None, currency_format)
        elif col in ['acos', 'ctr', 'conversion_rate', 'profit_margin']:
            worksheet.set_column(i, i, None, percent_format)
        elif col in ['start_date', 'end_date']:
            worksheet.set_column(i, i, None, date_format)
    
    writer.close()
    output.seek(0)
    return output

def create_campaign_pdf(campaign_data: Dict[str, Any], analyzer) -> bytes:
    """Create a PDF report for a campaign."""
    pdf = FPDF()
    pdf.add_page()
    
    # Set fonts
    pdf.set_font("Arial", "B", 16)
    
    # Header
    pdf.cell(190, 10, "Campaign Report", ln=True, align="C")
    pdf.cell(190, 10, campaign_data['campaign_name'], ln=True, align="C")
    pdf.line(10, 30, 200, 30)
    pdf.ln(5)
    
    # Campaign basics
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "Campaign Information", ln=True)
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(60, 6, "Product:", border=0)
    pdf.cell(130, 6, campaign_data['product_name'], ln=True, border=0)
    
    pdf.cell(60, 6, "Channel:", border=0)
    pdf.cell(130, 6, campaign_data['channel'], ln=True, border=0)
    
    pdf.cell(60, 6, "Category:", border=0)
    pdf.cell(130, 6, campaign_data['category'], ln=True, border=0)
    
    pdf.cell(60, 6, "Date Range:", border=0)
    pdf.cell(130, 6, f"{campaign_data['start_date']} to {campaign_data['end_date']}", ln=True, border=0)
    
    pdf.ln(5)
    
    # Performance metrics
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "Performance Metrics", ln=True)
    pdf.set_font("Arial", "", 10)
    
    metrics = [
        ("Ad Spend", f"${campaign_data['ad_spend']:,.2f}"),
        ("Impressions", f"{campaign_data['impressions']:,}"),
        ("Clicks", f"{campaign_data['clicks']:,}"),
        ("Conversions", f"{campaign_data['conversions']:,}"),
        ("Revenue", f"${campaign_data['revenue']:,.2f}"),
        ("ROAS", f"{campaign_data['roas']:.2f}x"),
        ("ACoS", f"{campaign_data['acos']:.2f}%"),
        ("Target ACoS", f"{campaign_data['target_acos']:.2f}%"),
        ("Conversion Rate", f"{campaign_data['conversion_rate']:.2f}%"),
        # Calculate CTR if not in campaign_data
        ("CTR", f"{campaign_data.get('ctr', safe_divide(campaign_data['clicks'] * 100, campaign_data['impressions'])):.2f}%"),
        ("Avg. CPC", f"${campaign_data['avg_cpc']:.2f}"),
    ]
    
    for i, (label, value) in enumerate(metrics):
        # Create a two-column layout with 2 metrics per row
        if i % 2 == 0:
            pdf.cell(40, 6, label, border=0)
            pdf.cell(50, 6, value, border=0)
        else:
            pdf.cell(40, 6, label, border=0)
            pdf.cell(50, 6, value, ln=True, border=0)
    
    # Add a line break if we ended on an odd item
    if len(metrics) % 2 != 0:
        pdf.ln()
    
    pdf.ln(5)
    
    # Economics
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "Economics", ln=True)
    pdf.set_font("Arial", "", 10)
    
    economics = [
        ("Product Cost", f"${campaign_data['product_cost']:,.2f}"),
        ("Selling Price", f"${campaign_data['selling_price']:,.2f}"),
        ("Shipping Cost", f"${campaign_data['shipping_cost']:,.2f}"),
        ("Platform Fees", f"${campaign_data['amazon_fees']:,.2f}"),
        ("Profit", f"${campaign_data['profit']:,.2f}"),
        ("Profit Margin", f"{campaign_data['profit_margin']:.2f}%"),
    ]
    
    for i, (label, value) in enumerate(economics):
        if i % 2 == 0:
            pdf.cell(40, 6, label, border=0)
            pdf.cell(50, 6, value, border=0)
        else:
            pdf.cell(40, 6, label, border=0)
            pdf.cell(50, 6, value, ln=True, border=0)
    
    if len(economics) % 2 != 0:
        pdf.ln()
    
    pdf.ln(5)
    
    # Assessment
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "Performance Assessment", ln=True)
    pdf.set_font("Arial", "", 10)
    
    # Determine assessment
    if campaign_data['roas'] >= 4:
        assessment = "Excellent"
    elif campaign_data['roas'] >= 3:
        assessment = "Good"
    elif campaign_data['roas'] >= 2:
        assessment = "Average"
    else:
        assessment = "Poor"
    
    pdf.multi_cell(190, 6, f"Campaign Performance: {assessment}", border=0)
    pdf.multi_cell(190, 6, f"Performance Score: {campaign_data['performance_score']:.1f}/100", border=0)
    
    # Calculate channel averages for comparison
    channel_data = analyzer.campaigns[analyzer.campaigns['channel'] == campaign_data['channel']]
    if not channel_data.empty:
        avg_roas = channel_data['roas'].mean()
        avg_acos = channel_data['acos'].mean()
        avg_conv_rate = channel_data['conversion_rate'].mean()
        
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f"Comparison to {campaign_data['channel']} Average", ln=True)
        pdf.set_font("Arial", "", 10)
        
        comparisons = [
            ("ROAS", f"{campaign_data['roas']:.2f}x", f"{avg_roas:.2f}x"),
            ("ACoS", f"{campaign_data['acos']:.2f}%", f"{avg_acos:.2f}%"),
            ("Conversion Rate", f"{campaign_data['conversion_rate']:.2f}%", f"{avg_conv_rate:.2f}%"),
        ]
        
        for label, value, avg in comparisons:
            pdf.cell(40, 6, label, border=0)
            pdf.cell(50, 6, value, border=0)
            pdf.cell(50, 6, f"Avg: {avg}", ln=True, border=0)
    
    # Notes
    if campaign_data.get('notes'):
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "Campaign Notes", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(190, 6, campaign_data['notes'], border=0)
    
    # Footer
    pdf.set_y(-15)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, f"ViveROI Analytics | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C")
    
    return pdf.output(dest='S').encode('latin1')

# --- AI ASSISTANT FUNCTIONS ---
def check_openai_api_key():
    """Check if OpenAI API key is available and valid."""
    try:
        api_key = st.secrets["openai_api_key"]
        
        if not api_key:
            st.session_state.api_key_status = "missing"
            logger.warning("OpenAI API key not found in secrets")
            return False
        
        # Verify the API key is valid with a simple test request
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
        logger.exception(f"Error checking OpenAI API key: {str(e)}")
        return False

def call_openai_api(messages, model="gpt-4o", temperature=0.7, max_tokens=1500):
    """Call the OpenAI API with the given messages."""
    st.session_state.is_loading = True
    try:
        api_key = st.secrets.get("openai_api_key", None)
        
        if not api_key:
            logger.warning("OpenAI API key not found in secrets, using simulated response")
            time.sleep(1.5)
            st.session_state.is_loading = False
            return generate_simulated_response(messages)
        
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
        logger.exception(f"Error calling OpenAI API: {str(e)}")
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

    elif "medical device" in user_message.lower() or "healthcare" in user_message.lower():
        return """For medical device marketing, particularly in your product categories:

1. Focus on educational content that explains product benefits and proper usage
2. Leverage testimonials and case studies to build trust with healthcare professionals and patients
3. Implement product comparison campaigns highlighting your unique features versus competitors
4. Consider targeting specific conditions related to your products (e.g., mobility limitations, chronic pain)

For healthcare PPC specifically:
- Use medical terminology alongside layman's terms in your keyword strategy
- Ensure compliance with all advertising regulations for medical devices
- Include healthcare professional targeting alongside patient/caregiver audiences
- Build landing pages with detailed product specifications and validation data

The best-performing medical device categories currently are Mobility Aids (6.3x ROAS) and Pain Management (4.69x ROAS)."""

    elif "amazon listing" in user_message.lower() or "product listing" in user_message.lower():
        return """Based on your Amazon listings, here are my top recommendations:

1. **Title Optimization**: Your current titles are keyword-stuffed and difficult to read. Restructure them to front-load your most important search terms while maintaining readability. For medical devices, prioritize clear product identification and main benefits.

2. **Enhanced Brand Content**: Your A+ content is underutilized. Add comparison charts between your models, more lifestyle imagery showing the products in use, and detailed specification tables.

3. **Secondary Images**: Add infographics highlighting key measurements, weight capacity, and medical benefits. Also include images showing the product from multiple angles and in different usage scenarios.

4. **Bullet Points**: Restructure to lead with benefits before features. For example, instead of "Adjustable height 32-38 inches" say "Customizable comfort with adjustable height (32-38 inches) for users of all statures."

5. **Backend Keywords**: You're missing important synonyms and common misspellings in your backend search terms. Add condition-specific terms that shoppers might use.

Implementing these changes could potentially improve your conversion rate by 15-25% based on industry benchmarks for medical devices."""

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
    system_prompt = """You are an expert marketing analyst for Vive Health, specializing in e-commerce PPC campaigns 
    and marketing ROI analysis for medical devices. Provide detailed, actionable insights based on the campaign data."""
    
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
        
        # FIX: Check if 'ctr' exists before using it
        if 'ctr' in campaign:
            system_prompt += f"CTR: {campaign['ctr']:.2f}%\n"
        else:
            # Calculate CTR on the fly if it doesn't exist
            calculated_ctr = safe_divide(campaign['clicks'] * 100, campaign['impressions'])
            system_prompt += f"CTR: {calculated_ctr:.2f}%\n"
            
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
        
        user_prompt = f"""Please analyze this {campaign['channel']} campaign for {campaign['product_name']} and provide specific recommendations to improve its performance. 
        Focus on optimizing ROAS, ACoS, and profit margin. What specific actions should we take? Include expected impact of your 
        recommendations in percentages or dollar terms when possible. Be concise, actionable, and specific to the medical device industry."""
    else:
        user_prompt = """Please analyze our overall marketing campaign performance across channels. What are the top 3-5 recommendations to 
        optimize our marketing spend and improve ROI? Provide specific, actionable insights based on the data. Include expected impact 
        of recommendations in percentages or dollar terms when possible. Be concise and focus on specific actions we should take."""
    
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

def get_ai_medical_device_chat_response(messages_history):
    """Get AI responses for the medical device marketing assistant chat."""
    # Prepare system message with medical device marketing context
    system_message = f"""You are an expert marketing consultant specializing in medical devices and healthcare marketing. 
    Your role is to help a quality manager at a medical device company with marketing strategy, PPC advertising, 
    and campaign optimization.

    You have deep knowledge of various medical device categories including:
    {', '.join(MEDICAL_DEVICE_CATEGORIES)}

    You understand the unique challenges of medical device marketing:
    - Regulatory constraints (FDA, HIPAA, etc.)
    - Complex buyer journey with multiple stakeholders
    - Balance between technical specifications and user benefits
    - Importance of education and clinical evidence
    - Targeting both healthcare professionals and end users
    
    Provide specific, actionable advice tailored to medical device marketing. Use your knowledge of PPC platforms, 
    healthcare keywords, and medical device marketing best practices to give detailed recommendations.
    
    Current date: {datetime.now().strftime('%Y-%m-%d')}

    Be helpful, specific, and actionable in your responses. Focus specifically on medical device marketing rather than 
    general marketing advice where possible."""
    
    # Prepare all messages including system and history
    all_messages = [{"role": "system", "content": system_message}]
    all_messages.extend(messages_history)
    
    # Get response from OpenAI
    response = call_openai_api(all_messages, max_tokens=1500)
    return response

def get_amazon_listing_assistant_response(messages_history):
    """Get AI responses for Amazon listing optimization assistant."""
    # Prepare system message for Amazon listing optimization context
    system_message = f"""You are an expert Amazon Listing Optimization Specialist with deep experience in e-commerce and 
    specifically Amazon's A9 algorithm and product listing requirements. Your role is to help sellers optimize their 
    product listings to improve visibility, conversion rates, and overall sales performance.

    You have specialized expertise in:
    {', '.join(AMAZON_LISTING_TOPICS)}

    You understand Amazon SEO, best practices for:
    - Product title optimization for both algorithm and human readability
    - Creating compelling bullet points that highlight benefits and features
    - Writing product descriptions that convert
    - Strategic keyword research and implementation
    - A+ Content creation and enhancement
    - Image optimization for main and secondary images
    - Amazon advertising strategy integration with listings
    - Review management and strategies for getting more positive reviews
    - Pricing strategy and competitive positioning
    
    For medical device products, you understand the special considerations:
    - Compliance with Amazon's restricted product policies
    - FDA regulations and how to properly present medical claims
    - The importance of clear usage instructions and safety information
    - How to effectively communicate technical specifications to both professionals and consumers
    
    Current date: {datetime.now().strftime('%Y-%m-%d')}

    Be concrete, actionable, and specific in your recommendations. Provide examples where possible, and explain the 
    reasoning behind each suggestion. Focus on proven strategies that work specifically on Amazon rather than 
    general e-commerce advice."""
    
    # Prepare all messages including system and history
    all_messages = [{"role": "system", "content": system_message}]
    all_messages.extend(messages_history)
    
    # Get response from OpenAI
    response = call_openai_api(all_messages, max_tokens=2000, temperature=0.5)
    return response

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
                    
                    # FIX: Check if 'ctr' exists before using it
                    if 'ctr' in campaign:
                        sim_ctr = max(0, campaign['ctr'] * np.random.uniform(
                            1 - param_variations['ctr']/100,
                            1 + param_variations['ctr']/100
                        ))
                    else:
                        # Calculate CTR on the fly if it doesn't exist
                        current_ctr = safe_divide(campaign['clicks'] * 100, campaign['impressions'])
                        sim_ctr = max(0, current_ctr * np.random.uniform(
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
            
            # FIX: Check if 'ctr' exists before using it
            if 'ctr' in campaign:
                new_ctr = campaign['ctr'] * (1 + ctr_change / 100)
            else:
                # Calculate CTR on the fly if it doesn't exist
                current_ctr = safe_divide(campaign['clicks'] * 100, campaign['impressions'])
                new_ctr = current_ctr * (1 + ctr_change / 100)
                
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

# Chat history for the medical devices marketing assistant
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Chat history for the Amazon listing assistant
if 'amazon_chat_messages' not in st.session_state:
    st.session_state.amazon_chat_messages = []

# =============================================================================
# UI Component Functions
# =============================================================================

def display_header():
    """Display app header with logo and navigation."""
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px">
            <h1 style="font-size: 28px; margin: 0; color: {COLOR_SCHEME["primary"]};">ViveROI</h1>
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
                    'clicks': clicks,))
                    'impressions': impressions,
                    'conversions': conversions,
                    'revenue': revenue,
