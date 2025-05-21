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
SUPPORT_EMAIL = "support@vivemedical.com"

# Configure Streamlit page
st.set_page_config(
    page_title="ViveROI | Medical Device Marketing Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Default Values and Constants
# ============================================================================

# Default channels with focus on Amazon
DEFAULT_CHANNELS = ["Amazon PPC", "Amazon DSP", "Vive Website", "Walmart", "eBay", "Paid Social", "Google Ads"]

# Medical device specific categories
DEFAULT_CATEGORIES = [
    "Mobility", "Pain Relief", "Bathroom Safety", "Bedroom", 
    "Daily Living Aids", "Orthopedic Supports", "Respiratory",
    "Rehabilitation", "Wound Care", "Compression Therapy"
]

# Base color scheme
COLOR_SCHEME = {
    "primary": "#00a3e0",    # Vive blue 
    "secondary": "#6cc24a",  # Vive green
    "tertiary": "#f7941d",   # Vive orange
    "positive": "#6cc24a",   # Success/good metrics
    "negative": "#d9534f",   # Warning/poor metrics
    "warning": "#f7941d",    # Caution/medium metrics
    "neutral": "#5bc0de",    # Info color
    "background": "#f5f8ff", # Light blue background
    "text_dark": "#333333",  # Dark text
    "text_light": "#ffffff", # Light text
    "amazon": "#ff9900",     # Amazon orange
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
# AI Integration Functions
# ============================================================================

def call_openai_api(messages, model="gpt-4o", temperature=0.7, max_tokens=1500):
    """Call the OpenAI API with the given messages."""
    st.session_state.is_loading = True
    
    try:
        # Check if API key is configured in Streamlit secrets
        if 'openai_api_key' in st.secrets:
            api_key = st.secrets['openai_api_key']
        else:
            # For demo/testing without a real API key
            logger.warning("OpenAI API key not found in Streamlit secrets, using simulated response")
            time.sleep(1.5)
            st.session_state.is_loading = False
            return generate_simulated_response(messages)
            
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        payload = {
            "model": model, 
            "messages": messages, 
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
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
            return f"Error: AI assistant encountered a problem (HTTP {response.status_code}). Please try again later."
            
    except Exception as e:
        logger.exception(f"Error calling OpenAI API: {str(e)}")
        st.session_state.is_loading = False
        return f"Error: The AI assistant encountered an unexpected problem. Please try again later."

def generate_simulated_response(messages):
    """Generate a simulated response for demonstration when API key is missing."""
    # Extract the latest user message
    user_message = "Unknown query"
    for msg in reversed(messages):
        if msg["role"] == "user":
            user_message = msg["content"]
            break
    
    # Generate response based on keywords in the user message
    if "roi" in user_message.lower() or "return on investment" in user_message.lower():
        return """Based on the campaign data, I recommend optimizing your ad spend on Amazon PPC for mobility products which currently show the highest ROAS at 6.3x.

Consider:
1. Increasing budget allocation by 15-20% for top-performing Amazon campaigns
2. Reviewing keyword performance for TENS units to identify high-converting search terms
3. Testing higher bids on top-performing keywords to maintain position and visibility

The data indicates Amazon campaigns are outperforming website PPC by approximately 25% in terms of ROAS."""
    
    elif "acos" in user_message.lower():
        return """Your ACoS performance varies significantly across channels:
- Amazon PPC campaigns are averaging 15-21% ACoS, which is better than your target
- Website PPC campaigns are showing higher ACoS (25.12%), slightly above target

Consider optimizing the Bathroom Safety campaign by:
* Implementing negative keywords to reduce wasted spend
* Refining keyword match types to more exact matching
* Testing product image and description improvements to increase conversion rate

A 10% reduction in ACoS for the Bathroom Safety campaign could increase your profit margin by approximately 7.5%."""
    
    elif "keyword" in user_message.lower() or "targeting" in user_message.lower():
        return """For medical device PPC keyword targeting, I recommend:

1. Use a mix of precise medical terminology and layperson terms (e.g., both "orthopedic supports" and "back brace")
2. Include symptom-based keywords (e.g., "pain relief," "mobility assistance")
3. Implement negative keywords for non-commercial search terms
4. For your mobility products, focus on specific use cases like "getting in and out of bath"

Your highest-converting keywords currently appear to be specific product attributes like "adjustable," "lightweight," and "portable" combined with the product category."""
    
    elif "medical device" in user_message.lower() or "healthcare" in user_message.lower():
        return """For medical device marketing, particularly in your product categories:

1. Focus on educational content that explains product benefits and proper usage
2. Leverage customer testimonials (while being careful with medical claims - always include appropriate disclaimers)
3. Highlight your product certifications and compliance to build trust
4. Consider targeting specific conditions related to your products (e.g., mobility limitations, chronic pain)

For Amazon specifically:
- Ensure product descriptions clearly state indications for use
- Include detailed specification measurements relevant to medical needs
- Use A+ content to explain how the product works
- Consider bundling complementary medical devices to increase average order value

The best-performing medical device categories currently are Mobility Aids (6.3x ROAS) and Pain Management (4.69x ROAS)."""
    
    elif "amazon listing" in user_message.lower() or "product listing" in user_message.lower():
        return """Based on your Amazon listings for medical devices, here are my recommendations:

1. **Title Optimization**: Your current titles are keyword-stuffed and difficult to read. Structure them as: [Brand] + [Product Type] + [2-3 Key Features] + [Size/Variant]

2. **Enhanced Brand Content**: Add comparison charts between your device models, usage diagrams, and detailed specification tables.

3. **Secondary Images**: Include infographics highlighting key measurements, weight capacity, and specific medical benefits. Show the product from multiple angles and in different usage scenarios.

4. **Bullet Points**: Lead with benefits before features. For example, instead of "Adjustable height 32-38 inches" say "Customizable comfort with adjustable height (32-38 inches) for users of all statures."

5. **Search Terms**: For medical devices, include both technical terms healthcare professionals might use and simpler terms patients would search for.

Note: Remember to review all medical claims for compliance with Amazon's policies and healthcare regulations before implementation."""
    
    else:
        return """Based on your medical device marketing campaign performance data, I've identified several optimization opportunities:

1. Amazon PPC campaigns are your strongest performers with ROAS of 4.69-6.30x
2. The Pain Relief category shows the highest conversion rate at 5.00%
3. Bathroom Safety products have potential but need optimization

Recommended actions:
- Shift 15% of budget from lower-performing channels to Amazon PPC
- Improve product listings for Bathroom Safety with more detailed specifications and better imagery
- Test different bid strategies for your top-performing keywords
- Implement product targeting ads for complementary medical devices

These adjustments could improve your overall marketing ROI by approximately 18-22% based on current performance metrics.

Remember to ensure all marketing claims remain compliant with medical device regulations."""

def get_ai_campaign_insights(campaign_data: pd.DataFrame, specific_campaign: Optional[str] = None):
    """Get AI-powered insights for marketing campaigns."""
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
        system_prompt += f" - Spend: ${row['ad_spend']:,.2f}\n"
        system_prompt += f" - Revenue: ${row['revenue']:,.2f}\n"
        system_prompt += f" - ROAS: {channel_roas:.2f}x\n"
        system_prompt += f" - ACoS: {channel_acos:.2f}%\n"
        system_prompt += f" - Conversion Rate: {channel_conv_rate:.2f}%\n\n"
    
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
        
        if 'ctr' in campaign:
            system_prompt += f"CTR: {campaign['ctr']:.2f}%\n"
        else:
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
        recommendations in percentages or dollar terms when possible. Be concise, actionable, and specific to the medical device industry. 
        Remember to include gentle reminders about regulatory compliance where relevant."""
    else:
        user_prompt = """Please analyze our overall marketing campaign performance across channels. What are the top 3-5 recommendations to
        optimize our marketing spend and improve ROI? Provide specific, actionable insights based on the data. Include expected impact
        of recommendations in percentages or dollar terms when possible. Be concise and focus on specific actions we should take.
        Remember to include gentle reminders about regulatory compliance for medical device marketing where relevant."""
    
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
        return f"Error generating insights: {str(e)}\n\nPlease try again later."

def get_amazon_chat_response(messages_history):
    """Get AI responses for the Amazon marketing assistant chat."""
    # Prepare system message with Amazon marketing and medical device context
    system_message = f"""You are an expert Amazon marketing consultant specializing in medical devices.
    You help the quality manager at a medical device company optimize their PPC campaigns and product listings.
    
    You understand the unique challenges of medical device marketing on Amazon:
    - Regulatory constraints (FDA, Amazon policies, etc.)
    - Balancing technical specifications with user benefits
    - Healthcare professional vs. end-user targeting
    - Importance of compliance with Amazon's terms
    
    Provide specific, actionable advice tailored to medical device marketing on Amazon. Your expertise covers:
    - Amazon PPC campaign optimization (Sponsored Products, Sponsored Brands, Sponsored Display)
    - Keyword and ASIN targeting strategies
    - Listing optimization for medical devices
    - A+ Content best practices for healthcare products
    - Review management within compliance guidelines
    - Amazon's medical device policies and requirements
    
    Be helpful, specific, and actionable in your responses. Focus on Amazon-specific strategies for medical devices.
    Provide gentle reminders about regulatory compliance where relevant, but don't overemphasize them.
    Current date: {datetime.datetime.now().strftime('%Y-%m-%d')}"""
    
    # Prepare all messages including system and history
    all_messages = [{"role": "system", "content": system_message}]
    all_messages.extend(messages_history)
    
    # Get response from OpenAI
    response = call_openai_api(all_messages, max_tokens=1500)
    return response

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

# Initialize analyzer
analyzer = MarketingAnalyzer()

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
        height=400
    )
    
    st.plotly_chart(conversion_funnel, use_container_width=True)
    
    # Get AI insights for this campaign
    st.markdown("## AI Analysis")
    
    with st.spinner("Generating AI insights..."):
        insights = get_ai_campaign_insights(analyzer.campaigns, campaign['campaign_name'])
        st.markdown(insights)
    
    # Action buttons
    st.markdown("## Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Edit Campaign"):
            st.session_state.view = "edit_campaign"
            st.rerun()
            
    with col2:
        if st.button("Delete Campaign"):
            if analyzer.delete_campaign(campaign_uid):
                show_toast("Campaign deleted successfully", "success")
                st.session_state.view = "all_campaigns"
                st.rerun()
            else:
                st.error("Failed to delete campaign")
                
    with col3:
        if st.button("Back to All Campaigns"):
            st.session_state.view = "all_campaigns"
            st.rerun()

# ============================================================================
# UI Components - AI Assistants
# ============================================================================

def display_amazon_assistant():
    """Display the Amazon marketing assistant chat interface."""
    st.title("Amazon Marketing Assistant")
    
    st.markdown("""
    This AI-powered assistant specializes in Amazon marketing for medical devices. Ask questions about:
    
    - Amazon PPC campaign optimization
    - ACOS, ROAS, and bidding strategies
    - Keyword and product targeting
    - Listing optimization for medical devices
    - A+ Content best practices
    - Amazon's medical device policies
    """)
    
    # Display message history
    messages = st.session_state.amazon_chat_messages
    
    if messages:
        for message in messages:
            if message["role"] == "user":
                st.chat_message("user").markdown(message["content"])
            else:
                st.chat_message("assistant").markdown(message["content"])
    
    # Chat input
    prompt = st.chat_input("Ask about Amazon marketing for medical devices...")
    
    if prompt:
        # Add user message to chat history
        st.session_state.amazon_chat_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        st.chat_message("user").markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_amazon_chat_response(st.session_state.amazon_chat_messages)
                st.markdown(response)
                st.session_state.amazon_chat_messages.append({"role": "assistant", "content": response})
    
    # Add a back button
    if st.button("← Back to Dashboard", key="back_from_assistant"):
        st.session_state.view = "dashboard"
        st.rerun()

# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application function."""
    # Load custom CSS
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton button {
        background-color: #00a3e0;
        color: white;
        font-weight: 500;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #0082b3;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom: 20px;">
            <h1 style="color: {COLOR_SCHEME['primary']};">ViveROI</h1>
            <p style="color: white;">Medical Device Marketing Analytics</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Navigation")
        
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.view = "dashboard"
            st.rerun()
            
        if st.button("➕ Add Campaign", use_container_width=True):
            st.session_state.view = "add_campaign"
            st.rerun()
            
        if st.button("📋 All Campaigns", use_container_width=True):
            st.session_state.view = "all_campaigns"
            st.rerun()
            
        if st.button("💬 Amazon Assistant", use_container_width=True):
            st.session_state.view = "assistant"
            st.rerun()
        
        st.markdown("---")
        
        # Data management
        st.markdown("### Data Management")
        
        if st.button("Add Example Data", use_container_width=True):
            num_added = analyzer.add_example_campaigns()
            st.success(f"Added {num_added} example campaigns.")
            st.rerun()
            
        # File uploader for importing data
        uploaded_file = st.file_uploader("Import Campaign Data", type=["csv", "xlsx"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    data = pd.read_csv(uploaded_file)
                else:
                    data = pd.read_excel(uploaded_file)
                
                if not data.empty:
                    # Try to match columns or use reasonable defaults
                    for _, row in data.iterrows():
                        try:
                            # Extract required fields with error handling
                            campaign_name = row.get('campaign_name', row.get('Campaign Name', 'Unknown Campaign'))
                            product_name = row.get('product_name', row.get('Product Name', 'Unknown Product'))
                            channel = row.get('channel', row.get('Channel', 'Amazon PPC'))
                            category = row.get('category', row.get('Category', 'Mobility'))
                            
                            # Marketing metrics
                            ad_spend = float(row.get('ad_spend', row.get('Ad Spend', 0)))
                            clicks = int(row.get('clicks', row.get('Clicks', 0)))
                            impressions = int(row.get('impressions', row.get('Impressions', 0)))
                            conversions = int(row.get('conversions', row.get('Conversions', 0)))
                            revenue = float(row.get('revenue', row.get('Revenue', 0)))
                            
                            # Product economics
                            product_cost = float(row.get('product_cost', row.get('Product Cost', 0)))
                            selling_price = float(row.get('selling_price', row.get('Selling Price', 0)))
                            shipping_cost = float(row.get('shipping_cost', row.get('Shipping Cost', 0)))
                            amazon_fees = float(row.get('amazon_fees', row.get('Amazon Fees', 0)))
                            
                            # Dates
                            start_date = row.get('start_date', row.get('Start Date', datetime.datetime.now().strftime('%Y-%m-%d')))
                            end_date = row.get('end_date', row.get('End Date', datetime.datetime.now().strftime('%Y-%m-%d')))
                            
                            # Add the campaign
                            analyzer.add_campaign(
                                campaign_name, product_name, channel, category,
                                ad_spend, clicks, impressions, conversions, revenue,
                                start_date, end_date, product_cost, selling_price,
                                shipping_cost, amazon_fees, 0, None
                            )
                        except Exception as e:
                            st.error(f"Error processing row: {str(e)}")
                            continue
                    
                    st.success(f"Imported {len(data)} campaigns.")
                    st.rerun()
                else:
                    st.error("Uploaded file contains no data.")
            except Exception as e:
                st.error(f"Error importing data: {str(e)}")
                
        st.markdown("---")
        st.caption(f"ViveROI v{APP_VERSION}")
        st.caption("© 2024 Vive Health")
    
    # Main content area based on current view
    if st.session_state.view == "dashboard":
        display_dashboard(analyzer.campaigns)
        
    elif st.session_state.view == "add_campaign":
        add_campaign_form()
        
    elif st.session_state.view == "all_campaigns":
        display_all_campaigns(analyzer.campaigns)
        
    elif st.session_state.view == "campaign_details":
        if st.session_state.selected_campaign:
            display_campaign_details(st.session_state.selected_campaign)
        else:
            st.error("No campaign selected.")
            st.session_state.view = "all_campaigns"
            st.rerun()
            
    elif st.session_state.view == "assistant":
        display_amazon_assistant()
        
    else:
        # Fallback to dashboard
        display_dashboard(analyzer.campaigns)

if __name__ == "__main__":
    main()
