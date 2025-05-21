import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import uuid
import json
import time
import base64
import io
import logging
import requests
import os
from typing import Dict, List, Tuple, Optional, Any, Union

# ============================================================================
# Configuration and Setup
# ============================================================================

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vive_roi")

# App constants
APP_VERSION = "1.0.0"
SUPPORT_EMAIL = "alexander.popoff@vivehealth.com"

# Define color scheme
COLOR_SCHEME = {
    "primary": "#00a3e0",     # Vive blue
    "secondary": "#6cc24a",   # Vive green
    "tertiary": "#f7941d",    # Vive orange
    "positive": "#6cc24a",    # Green for positive metrics
    "warning": "#f7941d",     # Orange for warning metrics
    "negative": "#d9534f",    # Red for negative metrics
    "background": "#f8f9fa",  # Light background
    "text": "#333333"         # Dark text
}

# Define default channels and categories
DEFAULT_CHANNELS = [
    "Amazon PPC", 
    "Amazon DSP", 
    "Vive Website", 
    "Google Ads", 
    "Walmart", 
    "eBay", 
    "Paid Social"
]

DEFAULT_CATEGORIES = [
    "Mobility", 
    "Pain Relief", 
    "Bathroom Safety", 
    "Sleep & Comfort", 
    "Fitness & Recovery", 
    "Daily Living Aids",
    "Respiratory Care"
]

# Configure Streamlit page
st.set_page_config(
    page_title="ViveROI | Medical Device Marketing Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import Data Format Specification
IMPORT_COLUMNS = {
    'required': [
        {'name': 'campaign_name', 'aliases': ['Campaign Name', 'Campaign'], 'type': 'string', 'description': 'Descriptive name for the campaign'},
        {'name': 'product_name', 'aliases': ['Product Name', 'Product'], 'type': 'string', 'description': 'Name of the advertised product'},
        {'name': 'channel', 'aliases': ['Channel', 'Platform'], 'type': 'string', 'description': 'Marketing channel (e.g., Amazon PPC, Website)'},
        {'name': 'ad_spend', 'aliases': ['Ad Spend', 'Spend', 'Cost'], 'type': 'float', 'description': 'Total amount spent on ads'},
        {'name': 'revenue', 'aliases': ['Revenue', 'Sales'], 'type': 'float', 'description': 'Total revenue from the campaign'}
    ],
    'recommended': [
        {'name': 'category', 'aliases': ['Category', 'Product Category'], 'type': 'string', 'description': 'Product category'},
        {'name': 'impressions', 'aliases': ['Impressions', 'Impr.'], 'type': 'int', 'description': 'Number of ad impressions'},
        {'name': 'clicks', 'aliases': ['Clicks'], 'type': 'int', 'description': 'Number of clicks on ads'},
        {'name': 'conversions', 'aliases': ['Conversions', 'Orders', 'Sales'], 'type': 'int', 'description': 'Number of conversions'},
        {'name': 'start_date', 'aliases': ['Start Date', 'From Date'], 'type': 'date', 'description': 'Campaign start date (YYYY-MM-DD)'},
        {'name': 'end_date', 'aliases': ['End Date', 'To Date'], 'type': 'date', 'description': 'Campaign end date (YYYY-MM-DD)'}
    ],
    'optional': [
        {'name': 'product_cost', 'aliases': ['Product Cost', 'Cost of Goods', 'COGS'], 'type': 'float', 'description': 'Cost to produce/acquire the product'},
        {'name': 'selling_price', 'aliases': ['Selling Price', 'Price', 'Product Price'], 'type': 'float', 'description': 'Product selling price'},
        {'name': 'shipping_cost', 'aliases': ['Shipping Cost', 'Shipping'], 'type': 'float', 'description': 'Cost to ship the product'},
        {'name': 'amazon_fees', 'aliases': ['Amazon Fees', 'Marketplace Fees', 'Fees'], 'type': 'float', 'description': 'Amazon or marketplace fees'},
        {'name': 'target_acos', 'aliases': ['Target ACoS', 'Target'], 'type': 'float', 'description': 'Target Advertising Cost of Sale percentage'},
        {'name': 'notes', 'aliases': ['Notes', 'Comments'], 'type': 'string', 'description': 'Additional notes about the campaign'}
    ]
}

# Formula Explanations - Used in Help Section
FORMULA_EXPLANATIONS = {
    'avg_cpc': {
        'name': 'Average Cost Per Click (Avg. CPC)',
        'formula': 'Ad Spend ÷ Clicks',
        'description': 'The average amount paid for each click on your ad.',
        'benchmark': 'For medical devices, ranges typically from $0.75 to $2.50 depending on specialty and competition.'
    },
    'ctr': {
        'name': 'Click-Through Rate (CTR)',
        'formula': '(Clicks ÷ Impressions) × 100%',
        'description': 'The percentage of impressions that resulted in a click.',
        'benchmark': 'Good CTR for medical devices on Amazon ranges from 0.3% to 0.7%.'
    },
    'conversion_rate': {
        'name': 'Conversion Rate',
        'formula': '(Conversions ÷ Clicks) × 100%',
        'description': 'The percentage of clicks that resulted in a conversion/sale.',
        'benchmark': 'Medical device conversion rates on Amazon typically range from 3% to 8%.'
    },
    'acos': {
        'name': 'Advertising Cost of Sale (ACoS)',
        'formula': '(Ad Spend ÷ Revenue) × 100%',
        'description': 'The percentage of revenue spent on advertising. Lower is better.',
        'benchmark': 'Target ACoS for medical devices typically ranges from 15% to 30%.'
    },
    'roas': {
        'name': 'Return on Ad Spend (ROAS)',
        'formula': 'Revenue ÷ Ad Spend',
        'description': 'The revenue generated for each dollar spent on advertising. Higher is better.',
        'benchmark': 'Good ROAS for medical devices is typically 3x or higher.'
    },
    'profit': {
        'name': 'Profit',
        'formula': 'Revenue - (Product Cost + Shipping Cost + Amazon Fees + Ad Spend)',
        'description': 'The total profit after accounting for all costs.',
        'benchmark': 'Depends on your business model and margins.'
    },
    'profit_margin': {
        'name': 'Profit Margin',
        'formula': '(Profit ÷ Revenue) × 100%',
        'description': 'The percentage of revenue that is profit.',
        'benchmark': 'Healthy profit margins for medical devices typically range from 30% to 60%.'
    },
    'breakeven_acos': {
        'name': 'Breakeven ACoS',
        'formula': '[(Selling Price - (Product Cost + Shipping + Amazon Fees)) ÷ Selling Price] × 100%',
        'description': 'The ACoS at which you neither make nor lose money.',
        'benchmark': 'Varies based on your product costs and selling price, but typically 25-40% for medical devices.'
    },
    'performance_score': {
        'name': 'Performance Score',
        'formula': '(ROAS Score × 0.35) + (ACoS Score × 0.3) + (Conversion Rate Score × 0.15) + (Profit Margin Score × 0.2)',
        'description': 'A weighted score (0-100) based on key performance metrics.',
        'benchmark': 'Scores above 70 are excellent, 50-70 are good, below 50 need improvement.'
    }
}

# Example campaigns for demonstration
EXAMPLE_CAMPAIGNS = [
    {
        "campaign_name": "Amazon PPC - Mobility Scooters",
        "product_name": "Vive Mobility Scooter",
        "channel": "Amazon PPC",
        "category": "Mobility",
        "ad_spend": 5000,
        "clicks": 4200,
        "impressions": 102000,
        "conversions": 126,
        "revenue": 31500,
        "start_date": "2024-04-01",
        "end_date": "2024-04-30",
        "product_cost": 125,
        "selling_price": 250,
        "shipping_cost": 0,
        "amazon_fees": 37.50,
        "target_acos": 18,
        "notes": "Auto-targeting campaign for mobility scooters"
    },
    {
        "campaign_name": "Amazon PPC - TENS Units",
        "product_name": "Vive TENS Unit",
        "channel": "Amazon PPC",
        "category": "Pain Relief",
        "ad_spend": 2800,
        "clicks": 3500,
        "impressions": 78000,
        "conversions": 175,
        "revenue": 13125,
        "start_date": "2024-04-01",
        "end_date": "2024-04-30",
        "product_cost": 28,
        "selling_price": 75,
        "shipping_cost": 0,
        "amazon_fees": 11.25,
        "target_acos": 20,
        "notes": "Keyword-targeted campaign for TENS units"
    },
    {
        "campaign_name": "Amazon PPC - Bathroom Safety",
        "product_name": "Vive Shower Chair",
        "channel": "Amazon PPC",
        "category": "Bathroom Safety",
        "ad_spend": 1500,
        "clicks": 1200,
        "impressions": 28000,
        "conversions": 45,
        "revenue": 5850,
        "start_date": "2024-04-01",
        "end_date": "2024-04-30",
        "product_cost": 52,
        "selling_price": 130,
        "shipping_cost": 0,
        "amazon_fees": 19.50,
        "target_acos": 30,
        "notes": "Amazon Sponsored Products campaign for shower chairs"
    }
]

# Required columns for campaigns DataFrame
CAMPAIGN_COLUMNS = [
    'uid', 'campaign_name', 'product_name', 'channel', 'category', 
    'ad_spend', 'clicks', 'impressions', 'conversions', 'revenue', 
    'start_date', 'end_date', 'avg_cpc', 'ctr', 'conversion_rate', 
    'acos', 'roas', 'product_cost', 'selling_price', 'shipping_cost', 
    'amazon_fees', 'profit', 'profit_margin', 'target_acos', 
    'performance_score', 'timestamp', 'notes'
]

# Initialize session states
if 'campaigns' not in st.session_state:
    st.session_state.campaigns = pd.DataFrame(columns=CAMPAIGN_COLUMNS)

if 'view' not in st.session_state:
    st.session_state.view = "dashboard"

if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

if 'selected_campaign' not in st.session_state:
    st.session_state.selected_campaign = None

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

if 'amazon_chat_messages' not in st.session_state:
    st.session_state.amazon_chat_messages = []
    
# Settings defaults
if 'settings' not in st.session_state:
    st.session_state.settings = {
        'default_target_acos': {
            'Amazon PPC': 20,
            'Amazon DSP': 25,
            'Vive Website': 25,
            'Walmart': 30,
            'eBay': 30,
            'Paid Social': 35,
            'Google Ads': 30
        },
        'date_range': 30,  # Default past 30 days
        'ai_model': 'gpt-4o',  # Default AI model
        'theme_color': 'vive',  # Default theme
        'show_performance_score': True  # Whether to show performance scores
    }

# Initialize OpenAI API connection status
if 'openai_api_connected' not in st.session_state:
    st.session_state.openai_api_connected = False
    
# ============================================================================
# Utility Functions
# ============================================================================

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning a default if divisor is zero."""
    try:
        if b == 0:
            return default
        return a / b
    except Exception as e:
        logger.error(f"Error in safe_divide: {str(e)}")
        return default

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

def calculate_performance_score(roas: float, acos: float, conversion_rate: float, 
                              target_acos: float, profit_margin: float) -> Optional[float]:
    """Calculate a weighted performance score for a campaign."""
    try:
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
    """Show a toast notification to the user."""
    toast_types = {
        "success": "#6cc24a",
        "error": "#d9534f",
        "warning": "#f7941d",
        "info": "#5bc0de"
    }
    toast_color = toast_types.get(type, toast_types["info"])
    
    st.markdown(f"""
    <div style="position: fixed; bottom: 20px; right: 20px; padding: 12px 24px; 
              background-color: {toast_color}; color: white; border-radius: 8px; 
              box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 9999;">
        {message}
    </div>
    <script>
        setTimeout(function() {{
            document.querySelector('div[style*="position: fixed"]').style.display = 'none';
        }}, 3000);
    </script>
    """, unsafe_allow_html=True)

def to_excel(df: pd.DataFrame):
    """Convert dataframe to Excel file for download."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
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
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        # Set column widths
        for i, col in enumerate(df.columns):
            column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, column_width)
    
    output.seek(0)
    return output

# ============================================================================
# API Integration Functions
# ============================================================================

def test_openai_connection() -> bool:
    """Test connection to OpenAI API."""
    try:
        # Check if API key is in streamlit secrets
        if 'openai_api_key' in st.secrets:
            api_key = st.secrets['openai_api_key']
            
            # Simple test request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo", 
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 5
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Successfully connected to OpenAI API")
                return True
            else:
                logger.error(f"Failed to connect to OpenAI API: {response.status_code}")
                return False
        else:
            logger.warning(f"OpenAI API key not found in streamlit secrets. Please contact {SUPPORT_EMAIL}")
            return False
    except Exception as e:
        logger.error(f"Error testing OpenAI connection: {str(e)}")
        return False

def call_openai_api(messages, model=None, max_tokens=800):
    """Call OpenAI API with messages."""
    try:
        if model is None:
            model = st.session_state.settings.get('ai_model', 'gpt-4o')
        
        api_key = st.secrets.get('openai_api_key', '')
        if not api_key:
            logger.warning(f"OpenAI API key not found. Please contact {SUPPORT_EMAIL}")
            return f"AI tools not currently available. Please contact {SUPPORT_EMAIL} to resolve this issue."
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
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
            return f"Error: AI assistant encountered a problem (HTTP {response.status_code}). Please contact {SUPPORT_EMAIL} to resolve this issue."
    
    except Exception as e:
        logger.exception(f"Error calling OpenAI API: {str(e)}")
        return f"Error: The AI assistant encountered an unexpected problem. Please contact {SUPPORT_EMAIL} to resolve this issue."

def get_campaign_recommendations(plan_data):
    """Generate AI-powered campaign recommendations based on product and goals."""
    try:
        # Create system prompt with context
        system_prompt = """You are an expert medical device marketing strategist specializing in Amazon PPC campaign planning for Vive Health.
        Provide detailed, actionable recommendations for campaign structure, targeting, and optimization.
        Focus on advanced strategies specific to Vive Health's medical device portfolio. Assume the user has experience with Amazon PPC basics
        and needs more advanced insights. Your recommendations should be specific to the particular medical device category involved.
        
        Vive Health's product categories include mobility aids, pain relief devices, bathroom safety equipment, sleep & comfort products,
        fitness & recovery items, daily living aids, and respiratory care devices. Each category has unique customer needs, search behaviors,
        and regulatory considerations on Amazon.
        
        Ask clarifying questions if specific product information would help you provide more targeted advice. Focus on advanced techniques that
        go beyond standard practices.
        """
        
        # Create user prompt with plan data
        user_prompt = f"""
        I need recommendations for a Vive Health marketing campaign with the following details:
        
        Product: {plan_data['product']['name']} (Category: {plan_data['product']['category']})
        Price: ${plan_data['product']['price']:.2f}
        Cost: ${plan_data['product']['cost']:.2f}
        Profit Margin: {plan_data['product']['profit_margin']:.2f}%
        
        Budget: ${plan_data['campaign']['budget']:.2f}
        Duration: {plan_data['campaign']['duration']} days
        Primary Goal: {plan_data['campaign']['primary_goal']}
        Target Audience: {', '.join(plan_data['campaign']['target_audience'])}
        
        Competition Level: {plan_data['market']['competition_level']}
        Seasonality: {plan_data['market']['seasonality']}
        
        Please provide detailed, actionable recommendations for:
        1. Advanced channel and budget allocation strategy
        2. Sophisticated keyword strategy specific to this medical device
        3. Bidding strategy optimization beyond basic ACoS targets
        4. Advanced campaign structure and targeting approaches
        5. Detailed creative recommendations specific to Vive Health's brand and this product
        
        Focus on advanced techniques that experienced marketers might not be implementing. Include relevant
        compliance considerations for medical devices in this category.
        """
        
        # Create messages for API call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Get AI response
        return call_openai_api(messages, max_tokens=1200)
    except Exception as e:
        logger.error(f"Error getting campaign recommendations: {str(e)}")
        return f"Error generating campaign recommendations. Please contact {SUPPORT_EMAIL} for assistance."

def display_help_page():
    """Display condensed help and documentation page."""
    st.title("Help & Documentation")
    
    st.markdown("""
    ## ViveROI Marketing Analytics Dashboard
    
    This dashboard helps track, analyze, and optimize medical device marketing campaigns across
    multiple channels with a focus on Amazon advertising.
    """)
    
    # Create tabs for different help sections
    help_tabs = st.tabs([
        "Getting Started", 
        "Campaign Management", 
        "Analytics & AI Features",
        "FAQs"
    ])
    
    # Getting Started tab
    with help_tabs[0]:
        st.markdown("""
        ### Getting Started
        
        #### Adding Campaigns
        
        1. Click **Add New Campaign** from the dashboard
        2. Fill in the campaign details
        3. Save the campaign to see performance metrics
        
        #### Importing Campaign Data
        
        1. Go to the sidebar
        2. Upload your CSV or Excel file
        3. Review and confirm import
        
        #### Using Example Data
        
        Click **Add Example Data** in the sidebar to explore with sample data.
        """)
    
    # Campaign Management tab
    with help_tabs[1]:
        st.markdown("""
        ### Campaign Management
        
        - **Add Campaign**: Create new campaigns with detailed metrics
        - **View All Campaigns**: Search, filter, and manage campaigns
        - **Campaign Details**: View performance metrics, profit calculations, and AI insights
        - **Campaign Planner**: Create data-driven campaign plans with budget allocation
        
        The dashboard automatically calculates ROAS, ACoS, profit margins, and other key metrics.
        """)
        
    # Analytics & AI Features tab
    with help_tabs[2]:
        st.markdown("""
        ### Analytics & AI Features
        
        - **Dashboard Analytics**: Channel comparisons, top campaigns, category analysis
        - **Campaign Insights**: AI-powered performance analysis and recommendations
        - **Amazon Marketing Assistant**: Expert advice for Amazon PPC and listing optimization
        - **Campaign Planner**: AI recommendations for new campaigns
        
        The AI features are specifically tailored for medical device marketing with a focus on
        Amazon Advertising and Vive Health's product categories.
        """)
    
    # FAQs tab
    with help_tabs[3]:
        st.markdown("""
        ### Frequently Asked Questions
        
        **Q: How is my data stored?**  
        A: All data is stored in your local Streamlit session.
        
        **Q: What AI model is used?**  
        A: OpenAI's models provide the AI features. The default is GPT-4o.
        
        **Q: How can I export my campaign data?**  
        A: Use the "Download Excel Report" or "Download CSV Data" buttons.
        
        **Q: What's a good ACoS target for Vive Health products?**  
        A: Typically 15-25% for established products, 25-35% for newer products.
        
        **Q: AI features not working?**  
        A: Contact {SUPPORT_EMAIL} for assistance.
        """)
    
    # Add a back button
    if st.button("← Back to Dashboard"):
        st.session_state.view = "dashboard"
        st.rerun()

def get_historical_insights(historical_data):
    """Generate AI-powered insights based on historical campaign data."""
    try:
        # Create system prompt with context
        system_prompt = """You are an expert medical device marketing strategist specializing in e-commerce for Vive Health.
        Analyze the historical campaign data for this product category and provide specific, advanced insights and recommendations.
        Focus on extracting actionable learnings from past campaigns that can be applied to future ones, going beyond common sense or 
        basic marketing principles.
        
        Assume the user has experience with fundamental marketing concepts and needs sophisticated insights specific to their medical 
        device category on Amazon. Ask clarifying questions about the product if additional details would help provide more targeted advice.
        
        Your recommendations should be specific to Vive Health's medical device categories and Amazon's marketplace environment.
        """
        
        # Create user prompt with historical data
        user_prompt = f"""
        Please analyze the historical campaign data for {historical_data['category']} products and provide advanced insights:
        
        **Category Metrics:**
        - Average Conversion Rate: {historical_data['avg_metrics']['conversion_rate']:.2f}%
        - Average CTR: {historical_data['avg_metrics']['ctr']:.2f}%
        - Average ACoS: {historical_data['avg_metrics']['acos']:.2f}%
        - Average ROAS: {historical_data['avg_metrics']['roas']:.2f}x
        - Average CPC: ${historical_data['avg_metrics']['cpc']:.2f}
        
        **Top Performing Campaign:**
        - Name: {historical_data['top_campaign']['name']}
        - Channel: {historical_data['top_campaign']['channel']}
        - ROAS: {historical_data['top_campaign']['roas']:.2f}x
        - ACoS: {historical_data['top_campaign']['acos']:.2f}%
        - Conversion Rate: {historical_data['top_campaign']['conversion_rate']:.2f}%
        
        Based on this data from {historical_data['campaign_count']} campaigns in the {historical_data['category']} category, please provide:
        
        1. Advanced factors that made the top campaign successful beyond basic optimizations
        2. Sophisticated recommendations for future campaigns that go beyond common practices
        3. Target metrics and advanced bidding strategies based on historical performance
        4. Category-specific insights for {historical_data['category']} products that competitors might miss
        5. Advanced optimization techniques for Vive Health's listings in this category
        
        I have experience with basic campaign optimization. Please focus on advanced strategies and 
        ask me clarifying questions if you need more information about our specific product within this category.
        """
        
        # Create messages for API call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Get AI response
        return call_openai_api(messages, model=st.session_state.settings['ai_model'], max_tokens=1000)
    except Exception as e:
        logger.error(f"Error getting historical insights: {str(e)}")
        return f"Error generating historical insights. Please contact {SUPPORT_EMAIL} for assistance."

def get_product_specific_insights(product_analysis):
    """Generate AI-powered insights specific to an individual product."""
    try:
        # Create system prompt with context
        system_prompt = """You are an expert Amazon marketing specialist focusing on Vive Health's medical device portfolio.
        Analyze the performance data for this specific product across all campaigns and provide detailed, advanced insights and recommendations.
        Focus on concrete, sophisticated advice that leverages the unique attributes of this Vive Health product.
        
        Assume the user has experience with Amazon advertising basics and needs more advanced, product-specific strategies. Ask clarifying
        questions about the product if additional details would help you provide more targeted advice.
        
        Your expertise should cover advanced Amazon PPC strategies, sophisticated keyword optimization, advanced listing enhancements,
        competitive positioning, and compliance considerations specific to medical devices in Vive Health's product categories.
        """
        
        # Create user prompt with product data
        user_prompt = f"""
        Please analyze the performance data for our Vive Health {product_analysis['product']['name']} and provide advanced product-specific recommendations:
        
        **Product Details:**
        - Name: {product_analysis['product']['name']}
        - Category: {product_analysis['product']['category']}
        - Price: ${product_analysis['product']['price']:.2f}
        - Cost: ${product_analysis['product']['cost']:.2f}
        - Profit Margin: {product_analysis['product']['profit_margin']:.2f}%
        
        **Overall Performance:**
        - Total Ad Spend: ${product_analysis['performance']['total_spend']:.2f}
        - Total Revenue: ${product_analysis['performance']['total_revenue']:.2f}
        - Total Profit: ${product_analysis['performance']['total_profit']:.2f}
        - Overall ROAS: {product_analysis['performance']['overall_roas']:.2f}x
        - Overall ACoS: {product_analysis['performance']['overall_acos']:.2f}%
        - Average Conversion Rate: {product_analysis['performance']['avg_conversion_rate']:.2f}%
        
        **Channel Performance:**
        {', '.join([f"{c['channel']}: ROAS {c['roas']:.2f}x, ACoS {c['acos']:.2f}%" for c in product_analysis['channel_performance']])}
        
        Based on this data for our {product_analysis['product']['name']}, please provide:
        
        1. Advanced optimization strategies for keywords, listing content, and targeting beyond basic recommendations
        2. Sophisticated channel strategy beyond simple budget allocation
        3. Advanced bidding techniques tailored specifically to this product's performance metrics
        4. Competitive positioning opportunities in the {product_analysis['product']['category']} category
        5. Advanced conversion rate optimization techniques specific to this medical device
        
        I'm familiar with basic optimization techniques. Please focus on advanced strategies that could give us an edge,
        and feel free to ask clarifying questions about the product if that would help improve your recommendations.
        """
        
        # Create messages for API call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Get AI response
        return call_openai_api(messages, model=st.session_state.settings['ai_model'], max_tokens=1000)
    except Exception as e:
        logger.error(f"Error getting product-specific insights: {str(e)}")
        return f"Error generating product insights. Please contact {SUPPORT_EMAIL} for assistance."

def display_settings_page():
    """Display the settings page for the dashboard."""
    st.title("Settings")
    
    st.markdown("""
    Configure dashboard settings to customize your experience. Changes will be applied to the current session.
    """)
    
    tabs = st.tabs(["General", "AI Settings", "Import/Export", "Default Values", "About"])
    
    # General Settings
    with tabs[0]:
        st.subheader("General Settings")
        
        # Theme settings
        st.markdown("### Theme")
        theme_options = {"vive": "Vive Health", "amazon": "Amazon", "default": "Default"}
        selected_theme = st.selectbox(
            "Theme Color",
            options=list(theme_options.keys()),
            format_func=lambda x: theme_options[x],
            index=list(theme_options.keys()).index(st.session_state.settings['theme_color'])
        )
        st.session_state.settings['theme_color'] = selected_theme
        
        # Date range default
        st.markdown("### Date Range")
        default_date_range = st.slider(
            "Default Date Range (days)",
            min_value=7,
            max_value=90,
            value=st.session_state.settings['date_range'],
            step=1,
            help="Default date range for new campaigns"
        )
        st.session_state.settings['date_range'] = default_date_range
        
        # Display settings
        st.markdown("### Display Settings")
        show_performance_score = st.checkbox(
            "Show Performance Score",
            value=st.session_state.settings['show_performance_score'],
            help="Show calculated performance score in campaign tables"
        )
        st.session_state.settings['show_performance_score'] = show_performance_score
    
    # AI Settings
    with tabs[1]:
        st.subheader("AI Settings")
        
        # API connection status
        if st.session_state.get('openai_api_connected', False):
            st.success("✅ Connected to OpenAI API")
        else:
            st.error("❌ Not connected to OpenAI API")
            st.markdown(f"""
            OpenAI API key is required for AI features but not found or not valid.
            Please contact {SUPPORT_EMAIL} for assistance.
            """)
        
        # AI model selection
        st.markdown("### Model Selection")
        model_options = {
            "gpt-4o": "GPT-4o (Recommended)",
            "gpt-3.5-turbo": "GPT-3.5 Turbo (Faster)",
            "gpt-4-turbo": "GPT-4 Turbo (Alternative)"
        }
        selected_model = st.selectbox(
            "AI Model",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            index=list(model_options.keys()).index(st.session_state.settings['ai_model']) if st.session_state.settings['ai_model'] in model_options else 0,
            help="Select the OpenAI model to use for AI features"
        )
        st.session_state.settings['ai_model'] = selected_model
        
        # Test connection button
        if st.button("Test API Connection"):
            with st.spinner("Testing API connection..."):
                is_connected = test_openai_connection()
                st.session_state.openai_api_connected = is_connected
                if is_connected:
                    st.success("Successfully connected to OpenAI API!")
                else:
                    st.error(f"Failed to connect to OpenAI API. Please contact {SUPPORT_EMAIL} for assistance.")
    
    # Import/Export Settings
    with tabs[2]:
        st.subheader("Import/Export Settings")
        
        # Column mapping
        st.markdown("### Column Mapping")
        st.info("These settings affect how column names are mapped when importing data.")
        
        # Example mapping settings - could be expanded
        st.markdown("#### Amazon Advertising Column Mapping")
        st.markdown("The importer will try to map these common Amazon Advertising column names to our internal format:")
        
        mapping_df = pd.DataFrame([
            {"Amazon Column": "Campaign Name", "Maps To": "campaign_name"},
            {"Amazon Column": "Advertised SKU", "Maps To": "product_name"},
            {"Amazon Column": "Ad Group", "Maps To": "ad_group"},
            {"Amazon Column": "Spend", "Maps To": "ad_spend"},
            {"Amazon Column": "Sales", "Maps To": "revenue"},
            {"Amazon Column": "ACoS", "Maps To": "acos"},
            {"Amazon Column": "ROAS", "Maps To": "roas"},
            {"Amazon Column": "CTR", "Maps To": "ctr"},
            {"Amazon Column": "Impressions", "Maps To": "impressions"},
            {"Amazon Column": "Clicks", "Maps To": "clicks"},
            {"Amazon Column": "Orders", "Maps To": "conversions"}
        ])
        st.table(mapping_df)
    
    # Default Values
    with tabs[3]:
        st.subheader("Default Values")
        
        # Default target ACoS by channel
        st.markdown("### Default Target ACoS by Channel")
        st.info("These values are used as defaults when adding new campaigns.")
        
        # Create a form for updating target ACoS values
        with st.form("default_acos_form"):
            updated_targets = {}
            
            # Create 2 columns to display the settings more compactly
            col1, col2 = st.columns(2)
            
            channels = list(st.session_state.settings['default_target_acos'].keys())
            half = len(channels) // 2 + len(channels) % 2
            
            for i, channel in enumerate(channels):
                # Use the first column for the first half, second column for the second half
                with col1 if i < half else col2:
                    updated_targets[channel] = st.number_input(
                        f"{channel} Target ACoS (%)",
                        min_value=5.0,
                        max_value=50.0,
                        value=float(st.session_state.settings['default_target_acos'].get(channel, 25.0)),
                        step=1.0,
                        help=f"Default target ACoS for {channel} campaigns"
                    )
            
            save_targets = st.form_submit_button("Save Target ACoS Values")
            
            if save_targets:
                st.session_state.settings['default_target_acos'] = updated_targets
                st.success("Default target ACoS values saved!")
    
    # About
    with tabs[4]:
        st.subheader("About ViveROI")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"""
            <div style="text-align: center; border-radius: 50%; background-color: {COLOR_SCHEME['primary']}; 
                        width: 100px; height: 100px; display: flex; justify-content: center; align-items: center; 
                        margin: 0 auto;">
                <h1 style="color: white; margin: 0;">V</h1>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            ### ViveROI Marketing Analytics Dashboard
            **Version:** {APP_VERSION}
            
            A specialized dashboard for medical device marketing analytics, with a focus on Amazon advertising performance.
            
            Developed for quality managers and marketing teams to optimize PPC campaigns and maximize ROI.
            """)
        
        st.markdown(f"""
        ### Features
        
        - Campaign performance tracking and analysis
        - AI-powered marketing insights for medical devices
        - Amazon marketing assistant specialized for Vive Health products
        - Channel and category performance comparisons
        - Profit and ROI calculations
        
        ### Support
        
        For questions or support, contact {SUPPORT_EMAIL}
        """)
    
    # Add a back button
    if st.button("← Back to Dashboard"):
        st.session_state.view = "dashboard"
        st.rerun()

def get_amazon_chat_response(messages_history):
    """Get AI responses for the Amazon marketing assistant chat."""
    # Prepare system message with Amazon marketing and medical device context
    system_message = f"""You are an expert Amazon marketing consultant specializing in medical devices for Vive Health.
    You help the quality manager at Vive Health optimize their PPC campaigns and product listings.
    
    Vive Health sells medical devices in categories including mobility aids, pain relief devices, bathroom safety equipment,
    sleep & comfort products, fitness & recovery items, daily living aids, and respiratory care devices.
    
    You understand the unique challenges of medical device marketing on Amazon:
    - Regulatory constraints (FDA, Amazon policies, etc.)
    - Balancing technical specifications with user benefits
    - Healthcare professional vs. end-user targeting
    - Competitive landscape in the medical device space
    - Importance of compliance with Amazon's terms for medical devices
    
    Provide specific, actionable advanced advice tailored to medical device marketing on Amazon. Assume the user
    has experience with basic Amazon marketing concepts and needs more sophisticated guidance.
    
    Your expertise covers:
    - Advanced Amazon PPC campaign strategies (Sponsored Products, Sponsored Brands, Sponsored Display)
    - Sophisticated keyword and ASIN targeting beyond basic approaches
    - Advanced listing optimization techniques for medical devices 
    - A+ Content optimization specific to medical devices
    - Review management within compliance guidelines
    - Competitive positioning against other medical device sellers
    
    Ask clarifying questions about specific products if that would help provide more targeted advice.
    Be direct and focus on practical, advanced strategies rather than general principles the user likely
    already knows. Provide specific examples relevant to Vive Health products when possible.
    
    Current date: {datetime.datetime.now().strftime('%Y-%m-%d')}"""
    
    # Prepare all messages including system and history
    all_messages = [{"role": "system", "content": system_message}]
    all_messages.extend(messages_history)
    
    # Get response from OpenAI
    return call_openai_api(all_messages, max_tokens=1500)

def analyze_imported_file(file_data):
    """Analyze an imported file and provide AI insights about the data quality and content."""
    # Create a basic analysis of the file
    analysis = {
        'columns': [],
        'row_count': 0,
        'data_quality': {},
        'metrics': {},
        'summary': ""
    }
    
    try:
        # Basic analysis
        analysis['row_count'] = len(file_data)
        analysis['columns'] = file_data.columns.tolist()
        
        # Check data quality
        for col in file_data.columns:
            missing = file_data[col].isna().sum()
            pct_missing = (missing / len(file_data)) * 100 if len(file_data) > 0 else 0
            analysis['data_quality'][col] = {
                'missing_values': missing,
                'pct_missing': pct_missing,
                'unique_values': file_data[col].nunique(),
                'dtype': str(file_data[col].dtype)
            }
        
        # Extract key metrics if available
        if 'ad_spend' in file_data.columns and 'revenue' in file_data.columns:
            total_spend = file_data['ad_spend'].sum()
            total_revenue = file_data['revenue'].sum()
            analysis['metrics']['total_spend'] = total_spend
            analysis['metrics']['total_revenue'] = total_revenue
            analysis['metrics']['overall_roas'] = safe_divide(total_revenue, total_spend)
        
        if 'ad_spend' in file_data.columns and 'revenue' in file_data.columns:
            analysis['metrics']['overall_acos'] = safe_divide(file_data['ad_spend'].sum() * 100, file_data['revenue'].sum())
        
        if 'clicks' in file_data.columns and 'conversions' in file_data.columns:
            analysis['metrics']['overall_conversion_rate'] = safe_divide(file_data['conversions'].sum() * 100, file_data['clicks'].sum())
        
        if 'impressions' in file_data.columns and 'clicks' in file_data.columns:
            analysis['metrics']['overall_ctr'] = safe_divide(file_data['clicks'].sum() * 100, file_data['impressions'].sum())
        
        # Summarize the data
        if len(file_data) > 0:
            # Get unique channels if available
            channels = file_data['channel'].unique().tolist() if 'channel' in file_data.columns else []
            channel_str = f"Channels: {', '.join(channels)}" if channels else "No channel data found"
            
            # Get date range if available
            date_info = ""
            if 'start_date' in file_data.columns and 'end_date' in file_data.columns:
                min_date = pd.to_datetime(file_data['start_date'].min())
                max_date = pd.to_datetime(file_data['end_date'].max())
                date_info = f"Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
            
            # Basic summary
            analysis['summary'] = f"""
            Data contains {len(file_data)} campaigns with {len(file_data.columns)} data fields.
            {channel_str}
            {date_info}
            """
            
            # Add performance summary if metrics available
            if 'metrics' in analysis and analysis['metrics']:
                metrics = analysis['metrics']
                if 'overall_roas' in metrics:
                    analysis['summary'] += f"\nOverall ROAS: {metrics['overall_roas']:.2f}x"
                if 'overall_acos' in metrics:
                    analysis['summary'] += f"\nOverall ACoS: {metrics['overall_acos']:.2f}%"
                if 'overall_conversion_rate' in metrics:
                    analysis['summary'] += f"\nAverage Conversion Rate: {metrics['overall_conversion_rate']:.2f}%"
        
        return analysis
    
    except Exception as e:
        logger.error(f"Error analyzing imported file: {str(e)}")
        analysis['summary'] = f"Error analyzing file: {str(e)}"
        return analysis

def get_import_recommendations(file_analysis):
    """Generate AI-powered recommendations for the imported data."""
    try:
        # Create system prompt with context
        system_prompt = """You are an expert marketing analyst specializing in PPC campaign analysis for Vive Health's medical devices.
        Provide detailed, actionable insights about the data being imported based on the file analysis.
        Focus on specific patterns, opportunities, and potential issues in the data that might not be immediately obvious."""
        
        # Add file analysis
        prompt = f"""
        Here's an analysis of imported marketing campaign data for Vive Health medical devices:
        
        File contains {file_analysis['row_count']} campaigns with columns: {', '.join(file_analysis['columns'])}.
        
        """
        
        # Add metrics if available
        if 'metrics' in file_analysis and file_analysis['metrics']:
            metrics = file_analysis['metrics']
            prompt += "Key metrics:\n"
            if 'total_spend' in metrics:
                prompt += f"- Total ad spend: ${metrics['total_spend']:,.2f}\n"
            if 'total_revenue' in metrics:
                prompt += f"- Total revenue: ${metrics['total_revenue']:,.2f}\n"
            if 'overall_roas' in metrics:
                prompt += f"- Overall ROAS: {metrics['overall_roas']:.2f}x\n"
            if 'overall_acos' in metrics:
                prompt += f"- Overall ACoS: {metrics['overall_acos']:.2f}%\n"
            if 'overall_conversion_rate' in metrics:
                prompt += f"- Average conversion rate: {metrics['overall_conversion_rate']:.2f}%\n"
        
        # Add data quality issues
        missing_data = []
        for col, quality in file_analysis['data_quality'].items():
            if quality['pct_missing'] > 5:
                missing_data.append(f"{col} ({quality['pct_missing']:.1f}% missing)")
        
        if missing_data:
            prompt += f"\nColumns with significant missing data: {', '.join(missing_data)}"
        
        prompt += """
        
        Based on this analysis, please provide:
        1. A detailed assessment of the data quality and any critical issues that need addressing
        2. Specific observations about campaign performance metrics (if available)
        3. Advanced recommendations for what to analyze first based on potential opportunities
        4. Any patterns or anomalies that should be investigated
        
        Focus on insights relevant to Vive Health's medical device marketing on Amazon.
        Provide specific, actionable recommendations rather than general advice.
        """
        
        # Create messages for API call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Get AI response
        return call_openai_api(messages, max_tokens=800)
    except Exception as e:
        logger.error(f"Error getting import recommendations: {str(e)}")
        return f"File import complete. {file_analysis['row_count']} campaigns analyzed. For AI-powered analysis, please contact {SUPPORT_EMAIL}."

# ============================================================================
# Data Management Class
# ============================================================================

class MarketingAnalyzer:
    """Class to manage marketing campaigns and perform analytics."""
    
    def __init__(self):
        """Initialize the MarketingAnalyzer."""
        self.load_data()
        
    def load_data(self):
        """Load data from session state."""
        self.campaigns = st.session_state.campaigns
    
    def save_data(self):
        """Save data to session state."""
        st.session_state.campaigns = self.campaigns
    
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
        """Add a new marketing campaign with calculated metrics."""
        try:
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
                if "amazon" in channel.lower():
                    target_acos = 20
                elif "website" in channel.lower():
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
                'timestamp': datetime.datetime.now(),
                'notes': notes
            }
            
            # Add to dataframe
            self.campaigns = pd.concat([self.campaigns, pd.DataFrame([new_row])], ignore_index=True)
            self.save_data()
            
            return True, "Campaign added successfully!"
            
        except Exception as e:
            logger.error(f"Error adding campaign: {str(e)}")
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
            for example in EXAMPLE_CAMPAIGNS:
                success, _ = self.add_campaign(**example)
                if success:
                    added += 1
            return added
        except Exception as e:
            logger.error(f"Error adding example campaigns: {str(e)}")
            return added
    
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
                    'best_channel': None,
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
                'clicks': 'sum'
            }).reset_index()
            
            # Calculate channel metrics
            channel_stats['roas'] = channel_stats.apply(lambda x: safe_divide(x['revenue'], x['ad_spend']), axis=1)
            channel_stats['acos'] = channel_stats.apply(lambda x: safe_divide(x['ad_spend'] * 100, x['revenue']), axis=1)
            
            # Find best channel
            if not channel_stats.empty:
                best_idx = channel_stats['roas'].idxmax()
                stats['best_channel'] = {
                    'name': channel_stats.loc[best_idx, 'channel'],
                    'roas': channel_stats.loc[best_idx, 'roas']
                }
            
            # Store channel data
            for _, channel in channel_stats.iterrows():
                stats['channels'].append({
                    'name': channel['channel'],
                    'ad_spend': channel['ad_spend'],
                    'revenue': channel['revenue'],
                    'profit': channel['profit'],
                    'roas': channel['roas'],
                    'acos': channel['acos']
                })
            
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
                'best_channel': None,
                'channels': [],
                'error': str(e)
            }

# ============================================================================
# UI Components - Dashboard
# ============================================================================

def display_header():
    """Display app header with logo and navigation."""
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px">
            <h2 style="font-size: 24px; margin: 0; color: {COLOR_SCHEME['primary']};">ViveROI</h2>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.title("Medical Device Marketing Analytics")
        st.caption("Optimize ad spend, track campaign performance, and maximize ROI across e-commerce platforms")
        
    with col3:
        st.markdown(f"""
        <div style="text-align: right; padding: 10px">
            <p style="margin: 0; color: gray; font-size: 0.8rem;">v{APP_VERSION}</p>
            <p style="margin: 0; font-weight: 500; color: {COLOR_SCHEME['primary']};">Quality Management</p>
        </div>
        """, unsafe_allow_html=True)

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
        st.metric(
            "Total Ad Spend", 
            f"${stats['total_spend']:,.2f}", 
            help="Total advertising spend across all campaigns"
        )
        
    with col2:
        # Determine ROAS color based on value
        roas_delta = None
        if stats['overall_roas'] >= 4:
            roas_delta = "Excellent"
        elif stats['overall_roas'] >= 2:
            roas_delta = "Good"
        else:
            roas_delta = "Needs Improvement"
            
        st.metric(
            "Overall ROAS", 
            f"{stats['overall_roas']:.2f}x",
            roas_delta,
            help="Return on Ad Spend (Revenue ÷ Ad Spend)"
        )
        
    with col3:
        # Determine ACoS color based on value
        acos_delta = None
        if stats['overall_acos'] <= 20:
            acos_delta = "Excellent"
        elif stats['overall_acos'] <= 30:
            acos_delta = "Good" 
        else:
            acos_delta = "Needs Improvement"
            
        st.metric(
            "Overall ACoS", 
            f"{stats['overall_acos']:.2f}%",
            acos_delta,
            help="Advertising Cost of Sale (Ad Spend ÷ Revenue × 100%)"
        )
        
    with col4:
        st.metric(
            "Total Profit", 
            f"${stats['total_profit']:,.2f}",
            help="Total profit after ad costs and all fees"
        )
    
    # Display best performing channel if available
    if stats['best_channel']:
        st.success(f"Best performing channel: **{stats['best_channel']['name']}** with ROAS of **{stats['best_channel']['roas']:.2f}x**")

def display_dashboard(df: pd.DataFrame):
    """Display the main dashboard."""
    display_header()
    
    # Add quick actions
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Add New Campaign"):
            st.session_state.view = "add_campaign"
            st.rerun()
    with col2:
        if st.button("📋 View All Campaigns"):
            st.session_state.view = "all_campaigns"
            st.rerun()
    with col3:
        if st.button("💬 Marketing Assistant"):
            st.session_state.view = "assistant"
            st.rerun()
    with col4:
        if st.button("📊 Advanced Analytics"):
            st.session_state.view = "analytics"
            st.rerun()
    
    # Display metrics overview
    display_metrics_overview(df)
    
    # Display campaign performance charts
    st.subheader("Campaign Performance")
    
    # Channel performance comparison
    if not df.empty:
        tab1, tab2, tab3 = st.tabs(["Channel Comparison", "Campaign Performance", "Category Analysis"])
        
        with tab1:
            # Prepare channel data
            channel_data = df.groupby('channel').agg({
                'ad_spend': 'sum',
                'revenue': 'sum',
                'profit': 'sum',
                'conversions': 'sum',
                'clicks': 'sum'
            }).reset_index()
            
            channel_data['roas'] = channel_data.apply(lambda x: safe_divide(x['revenue'], x['ad_spend']), axis=1)
            channel_data['acos'] = channel_data.apply(lambda x: safe_divide(x['ad_spend'] * 100, x['revenue']), axis=1)
            channel_data['cpa'] = channel_data.apply(lambda x: safe_divide(x['ad_spend'], x['conversions']), axis=1)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # ROAS by channel
                fig = px.bar(
                    channel_data, 
                    x='channel', 
                    y='roas',
                    title="ROAS by Channel",
                    labels={'roas': 'ROAS (x)', 'channel': 'Channel'},
                    color='roas',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    range_color=[1, 6]
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                # ACoS by channel
                fig = px.bar(
                    channel_data, 
                    x='channel', 
                    y='acos',
                    title="ACoS by Channel",
                    labels={'acos': 'ACoS (%)', 'channel': 'Channel'},
                    color='acos',
                    color_continuous_scale=['green', 'yellow', 'red'],
                    range_color=[10, 40]
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Top campaigns by ROAS
            top_campaigns = df.sort_values('roas', ascending=False).head(5)
            
            # Campaign performance chart
            fig = px.bar(
                top_campaigns,
                x='campaign_name',
                y=['roas', 'conversion_rate'],
                title="Top 5 Campaigns by ROAS",
                labels={'value': 'Value', 'campaign_name': 'Campaign', 'variable': 'Metric'},
                barmode='group'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Campaign details table
            st.subheader("Top Performing Campaigns")
            top_df = top_campaigns[['campaign_name', 'channel', 'ad_spend', 'revenue', 'roas', 'acos', 'profit', 'profit_margin']]
            top_df = top_df.rename(columns={
                'campaign_name': 'Campaign',
                'channel': 'Channel',
                'ad_spend': 'Ad Spend',
                'revenue': 'Revenue',
                'roas': 'ROAS',
                'acos': 'ACoS',
                'profit': 'Profit',
                'profit_margin': 'Margin'
            })
            
            # Format the values
            top_df['Ad Spend'] = top_df['Ad Spend'].apply(lambda x: f"${x:,.2f}")
            top_df['Revenue'] = top_df['Revenue'].apply(lambda x: f"${x:,.2f}")
            top_df['ROAS'] = top_df['ROAS'].apply(lambda x: f"{x:.2f}x")
            top_df['ACoS'] = top_df['ACoS'].apply(lambda x: f"{x:.2f}%")
            top_df['Profit'] = top_df['Profit'].apply(lambda x: f"${x:,.2f}")
            top_df['Margin'] = top_df['Margin'].apply(lambda x: f"{x:.2f}%")
            
            st.table(top_df)
        
        with tab3:
            # Category analysis
            category_data = df.groupby('category').agg({
                'ad_spend': 'sum',
                'revenue': 'sum',
                'profit': 'sum',
                'conversions': 'sum'
            }).reset_index()
            
            category_data['roas'] = category_data.apply(lambda x: safe_divide(x['revenue'], x['ad_spend']), axis=1)
            
            # Category performance chart
            fig = px.pie(
                category_data,
                values='revenue',
                names='category',
                title="Revenue by Category",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add campaigns to see performance charts and analytics.")
        
        # Add example data button
        if st.button("Add Example Data for Demonstration"):
            num_added = analyzer.add_example_campaigns()
            st.success(f"Added {num_added} example campaigns. Refresh the dashboard to see the data.")
            st.rerun()
    
    # AI Insights section
    st.subheader("AI-Powered Marketing Insights")
    
    if not df.empty:
        with st.spinner("Generating insights..."):
            insights = get_ai_campaign_insights(df)
            st.markdown(insights)
            
        # Add export options
        st.subheader("Export Options")
        col1, col2 = st.columns(2)
        with col1:
            excel_data = to_excel(df)
            st.download_button(
                label="Download Excel Report",
                data=excel_data,
                file_name=f"marketing_report_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col2:
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            st.download_button(
                label="Download CSV Data",
                data=csv,
                file_name=f"marketing_data_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.warning("Add campaign data to receive AI-powered marketing insights.")

# ============================================================================
# UI Components - Campaign Management
# ============================================================================

def add_campaign_form():
    """Display form for adding a new campaign."""
    st.subheader("Add New Marketing Campaign")
    
    with st.form(key="campaign_form"):
        # Basic Information
        st.markdown("### Campaign Information")
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("Campaign Name", help="A descriptive name for this marketing campaign")
            product_name = st.text_input("Product Name", help="The product being advertised")
            
            # Channel selection with Amazon options prioritized
            channel = st.selectbox(
                "Marketing Channel",
                DEFAULT_CHANNELS,
                help="The platform or channel where the campaign is running"
            )
            
        with col2:
            category = st.selectbox(
                "Product Category",
                DEFAULT_CATEGORIES,
                help="The category this product belongs to"
            )
            
            start_date = st.date_input(
                "Start Date",
                datetime.datetime.now() - datetime.timedelta(days=30),
                help="When the campaign started"
            )
            
            end_date = st.date_input(
                "End Date",
                datetime.datetime.now(),
                help="When the campaign ended"
            )
        
        # Marketing Metrics
        st.markdown("### Marketing Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ad_spend = st.number_input(
                "Ad Spend ($)",
                min_value=0.0,
                format="%.2f",
                help="Total amount spent on ads"
            )
            
            impressions = st.number_input(
                "Impressions",
                min_value=0,
                help="Total number of ad impressions"
            )
            
        with col2:
            clicks = st.number_input(
                "Clicks",
                min_value=0,
                help="Total number of clicks on ads"
            )
            
            conversions = st.number_input(
                "Conversions",
                min_value=0,
                help="Total number of conversions or sales"
            )
            
        with col3:
            revenue = st.number_input(
                "Revenue ($)",
                min_value=0.0,
                format="%.2f",
                help="Total revenue generated from the campaign"
            )
            
            target_acos = st.number_input(
                "Target ACoS (%)",
                min_value=0.0,
                max_value=100.0,
                format="%.2f",
                value=20.0 if "amazon" in channel.lower() else 25.0,
                help="Target Advertising Cost of Sales percentage"
            )
        
        # Product Economics
        st.markdown("### Product Economics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            product_cost = st.number_input(
                "Product Cost ($)",
                min_value=0.0,
                format="%.2f",
                help="Cost to produce or acquire the product"
            )
            
            selling_price = st.number_input(
                "Selling Price ($)",
                min_value=0.0,
                format="%.2f",
                help="Price the product is sold for"
            )
            
        with col2:
            shipping_cost = st.number_input(
                "Shipping Cost ($)",
                min_value=0.0,
                format="%.2f",
                value=0.0,
                help="Cost to ship the product"
            )
            
            amazon_fees = st.number_input(
                "Amazon Fees ($)",
                min_value=0.0,
                format="%.2f",
                value=0.0,
                help="Amazon referral and FBA fees if applicable"
            )
            
        with col3:
            notes = st.text_area(
                "Campaign Notes",
                help="Additional details about the campaign"
            )
        
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
            
            # Metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Avg. CPC", f"${avg_cpc:.2f}")
                st.metric("CTR", f"{ctr:.2f}%")
                
            with col2:
                st.metric("Conversion Rate", f"{conversion_rate:.2f}%")
                st.metric("ACoS", f"{acos:.2f}%")
                
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
            <div style="padding: 10px; border-radius: 5px; background-color: {color}25; border-left: 4px solid {color};">
                <strong>Campaign Assessment:</strong> {assessment} - ROAS of {roas:.2f}x 
                {f"with ACoS {acos:.2f}% vs target {target_acos:.2f}%" if target_acos > 0 else ""}
                and profit margin of {profit_margin:.2f}%
            </div>
            """, unsafe_allow_html=True)
        
        # Submit button
        submitted = st.form_submit_button("Save Campaign")
        
        if submitted:
            # Basic validation
            if not campaign_name:
                st.error("Campaign Name is required")
                return
                
            if not product_name:
                st.error("Product Name is required")
                return
                
            if ad_spend <= 0:
                st.error("Ad Spend must be greater than zero")
                return
            
            # Set loading state
            st.session_state.is_loading = True
            
            # Add the campaign
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
                
                # Get AI insights for the new campaign
                if "campaign" in locals():
                    with st.spinner("Generating AI insights for your campaign..."):
                        insights = get_ai_campaign_insights(analyzer.campaigns, campaign_name)
                        st.markdown("### AI Analysis")
                        st.markdown(insights)
                
                st.success("Campaign added successfully! Go to dashboard to see overall performance.")
                
                # Add buttons for next actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Add Another Campaign"):
                        st.session_state.view = "add_campaign"
                        st.rerun()
                        
                with col2:
                    if st.button("View All Campaigns"):
                        st.session_state.view = "all_campaigns"
                        st.rerun()
                        
                with col3:
                    if st.button("Return to Dashboard"):
                        st.session_state.view = "dashboard"
                        st.rerun()
            else:
                st.error(message)
    
    # Add a back button
    if st.button("← Back to Dashboard"):
        st.session_state.view = "dashboard"
        st.rerun()

def display_all_campaigns(df: pd.DataFrame):
    """Display and manage all campaigns."""
    st.title("All Marketing Campaigns")
    
    if df.empty:
        st.info("No campaigns found. Add campaigns to see them here.")
        
        if st.button("Add New Campaign"):
            st.session_state.view = "add_campaign"
            st.rerun()
            
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
    
    # Add filter options
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
            'Profit (High to Low)': 'profit'
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
                             'revenue', 'roas', 'acos', 'conversion_rate', 'profit', 'profit_margin']].copy()
    
    # Format columns
    display_df['ad_spend'] = display_df['ad_spend'].apply(lambda x: f"${x:,.2f}")
    display_df['revenue'] = display_df['revenue'].apply(lambda x: f"${x:,.2f}")
    display_df['roas'] = display_df['roas'].apply(lambda x: f"{x:.2f}x")
    display_df['acos'] = display_df['acos'].apply(lambda x: f"{x:.2f}%")
    display_df['conversion_rate'] = display_df['conversion_rate'].apply(lambda x: f"{x:.2f}%")
    display_df['profit'] = display_df['profit'].apply(lambda x: f"${x:,.2f}")
    display_df['profit_margin'] = display_df['profit_margin'].apply(lambda x: f"{x:.2f}%")
    
    # Rename columns for display
    display_df.columns = ['UID', 'Campaign Name', 'Channel', 'Product', 'Ad Spend', 
                        'Revenue', 'ROAS', 'ACoS', 'Conv. Rate', 'Profit', 'Margin']
    
    # Display the table
    st.dataframe(display_df, hide_index=True)
    
    # Campaign action section
    st.subheader("Campaign Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        campaign_uid = st.text_input("Campaign UID for Actions", 
                                    help="Enter the UID of the campaign you want to take action on")
    
    with col2:
        action = st.selectbox("Select Action", 
                             ["View Details", "Edit Campaign", "Get AI Analysis", "Delete Campaign"])
    
    with col3:
        if st.button("Execute Action"):
            if not campaign_uid:
                st.error("Please enter a Campaign UID")
            elif campaign_uid not in df['uid'].values:
                st.error("Campaign not found with that UID")
            else:
                # Execute the selected action
                if action == "View Details":
                    st.session_state.selected_campaign = campaign_uid
                    st.session_state.view = "campaign_details"
                    st.rerun()
                    
                elif action == "Edit Campaign":
                    st.session_state.selected_campaign = campaign_uid
                    st.session_state.view = "edit_campaign"
                    st.rerun()
                    
                elif action == "Get AI Analysis":
                    campaign = analyzer.get_campaign(campaign_uid)
                    if campaign:
                        with st.spinner("Generating AI insights..."):
                            insights = get_ai_campaign_insights(analyzer.campaigns, campaign['campaign_name'])
                            st.subheader(f"AI Analysis for {campaign['campaign_name']}")
                            st.markdown(insights)
                    else:
                        st.error("Failed to retrieve campaign data")
                        
                elif action == "Delete Campaign":
                    if analyzer.delete_campaign(campaign_uid):
                        show_toast("Campaign deleted successfully", "success")
                        st.rerun()
                    else:
                        st.error("Failed to delete campaign")
    
    # Add export options
    st.subheader("Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        excel_data = to_excel(filtered_df)
        st.download_button(
            label="Download Excel Report",
            data=excel_data,
            file_name=f"campaign_report_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    with col2:
        csv = filtered_df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        st.download_button(
            label="Download CSV Data",
            data=csv,
            file_name=f"campaign_data_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Add a back button
    if st.button("← Back to Dashboard"):
        st.session_state.view = "dashboard"
        st.rerun()

def display_campaign_details(campaign_uid: str):
    """Display detailed view of a campaign."""
    campaign = analyzer.get_campaign(campaign_uid)
    
    if not campaign:
        st.error("Campaign not found. It may have been deleted.")
        
        if st.button("Back to Dashboard"):
            st.session_state.view = "dashboard"
            st.rerun()
            
        return
    
    # Header with back button
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("← Back"):
            st.session_state.view = "all_campaigns"
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
        **Amazon Fees:** ${campaign['amazon_fees']:,.2f}
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
                'bar': {'color': COLOR_SCHEME['primary']},
                'steps': [
                    {'range': [0, 2], 'color': COLOR_SCHEME['negative']},
                    {'range': [2, 4], 'color': COLOR_SCHEME['warning']},
                    {'range': [4, 8], 'color': COLOR_SCHEME['positive']}
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
                'bar': {'color': COLOR_SCHEME['primary']},
                'steps': [
                    {'range': [0, campaign['target_acos']], 'color': COLOR_SCHEME['positive']},
                    {'range': [campaign['target_acos'], campaign['target_acos']*1.5], 'color': COLOR_SCHEME['warning']},
                    {'range': [campaign['target_acos']*1.5, 50], 'color': COLOR_SCHEME['negative']}
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
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Conversion funnel chart
    funnel_values = [campaign['impressions'], campaign['clicks'], campaign['conversions']]
    funnel_text = [
        f"Impressions: {campaign['impressions']:,}",
        f"Clicks: {campaign['clicks']:,} (CTR: {campaign['ctr']:.2f}%)",
        f"Conversions: {campaign['conversions']:,} (CR: {campaign['conversion_rate']:.2f}%)"
    ]
    
    conversion_funnel = go.Figure(go.Funnel(
        y = ["Impressions", "Clicks", "Conversions"],
        x = funnel_values,
        textinfo = "text",
        text = funnel_text,
        marker = {
            "color": [
                COLOR_SCHEME['primary'],
                COLOR_SCHEME['secondary'],
                COLOR_SCHEME['tertiary']
            ]
        },
        connector = {"line": {"color": "royalblue", "dash": "dot", "width": 3}}
    ))
    
    conversion_funnel.update_layout(
        title="Conversion Funnel",
