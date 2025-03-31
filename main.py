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
import os
from typing import Dict, List, Optional, Union, Tuple
import base64
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_option_menu import option_menu

# Set page config
st.set_page_config(
    page_title="KaizenROI | Smart Return Optimization Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Montserrat:wght@300;400;500;600;700&display=swap');
    
    body, .stApp {
        background-color: #f8f9fa;
        font-family: 'Poppins', sans-serif;
        color: #2c3e50;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f8f9fa;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #fff;
        border-radius: 4px 4px 0 0;
        border: 1px solid #e6e9ef;
        border-bottom: none;
        padding: 10px 16px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1abc9c !important;
        color: white !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        color: #1e3a8a;
    }
    
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-left: 4px solid #1abc9c;
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 600;
        color: #1e3a8a;
    }
    
    .metric-label {
        font-size: 14px;
        color: #64748b;
    }
    
    .stDataFrame thead tr th {
        background-color: #1abc9c;
        color: white;
        font-weight: 500;
    }
    
    .stDataFrame tbody tr:nth-of-type(even) {
        background-color: #f8f9fa;
    }
    
    .stButton>button {
        background-color: #1abc9c;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: #16a085;
    }
    
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 10px 15px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    
    .warning-box {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 10px 15px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 10px 15px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    </style>
    """, unsafe_allow_html=True)

load_css()

# Define utility functions
def validate_input(value: float, min_value: float = 0.0) -> float:
    """Validate numerical input."""
    if value is None:
        return min_value
    try:
        value = float(value)
        return max(value, min_value)
    except (ValueError, TypeError):
        return min_value

def format_currency(value: float) -> str:
    """Format value as currency."""
    if value is None:
        return "$0.00"
    return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    """Format value as percentage."""
    if value is None:
        return "0.00%"
    return f"{value:.2f}%"

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safely divide two numbers."""
    if b == 0 or b is None:
        return default
    return a / b

def create_metric_html(label: str, value: str, delta: Optional[str] = None, delta_color: str = "normal") -> str:
    """Create HTML for metric display."""
    delta_html = ""
    if delta:
        color = "red" if delta_color == "inverse" and delta.startswith("+") else "green"
        color = "green" if delta_color == "inverse" and delta.startswith("-") else color
        color = "red" if delta_color == "normal" and delta.startswith("-") else color
        color = "green" if delta_color == "normal" and delta.startswith("+") else color
        delta_html = f'<span style="color: {color}; font-size: 14px;">{delta}</span>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-value">{value} {delta_html}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

# Define the ReturnOptimizer class (improved from ReturnRxSimple)
class ReturnOptimizer:
    """Handles return optimization scenarios and calculations."""
    
    def __init__(self):
        """Initialize with empty dataframe and default settings."""
        self.scenarios = pd.DataFrame(columns=[
            'uid', 'scenario_name', 'sku', 'sales_30', 'avg_sale_price',
            'sales_channel', 'returns_30', 'return_rate', 'solution', 'solution_cost',
            'additional_cost_per_item', 'current_unit_cost', 'reduction_rate',
            'return_cost_30', 'return_cost_annual', 'revenue_impact_30',
            'revenue_impact_annual', 'new_unit_cost', 'savings_30',
            'annual_savings', 'break_even_days', 'break_even_months',
            'roi', 'score', 'timestamp', 'annual_additional_costs', 'net_benefit',
            'margin_before', 'margin_after', 'margin_after_amortized',
            'sales_365', 'returns_365', 'category', 'tags'
        ])
        self.settings = {
            "currency_symbol": "$",
            "time_frame": 30,  # Days
            "color_theme": "viridis"
        }
    
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
                     sales_365: float = 0.0, 
                     returns_365: float = 0.0,
                     category: str = "",
                     tags: List[str] = None) -> Tuple[bool, str]:
        """
        Add a new scenario with detailed calculations.
        
        Args:
            scenario_name: Name of the scenario
            sku: Product SKU
            sales_30: 30-day sales quantity
            avg_sale_price: Average sale price
            sales_channel: Sales channel name
            returns_30: 30-day returns quantity
            solution: Description of proposed solution
            solution_cost: One-time cost of implementing solution
            additional_cost_per_item: Additional cost per item after solution
            current_unit_cost: Current unit cost
            reduction_rate: Expected percentage reduction in returns
            sales_365: Annual sales quantity (optional)
            returns_365: Annual returns quantity (optional)
            category: Category for grouping
            tags: List of tags for filtering
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate inputs
            if not sku:
                return False, "SKU is required"
            
            sales_30 = validate_input(sales_30)
            avg_sale_price = validate_input(avg_sale_price)
            returns_30 = validate_input(returns_30)
            current_unit_cost = validate_input(current_unit_cost)
            additional_cost_per_item = validate_input(additional_cost_per_item)
            solution_cost = validate_input(solution_cost)
            reduction_rate = validate_input(reduction_rate)
            sales_365 = validate_input(sales_365)
            returns_365 = validate_input(returns_365)
            
            # Validate business logic
            if returns_30 > sales_30:
                return False, "Returns cannot exceed sales"
            
            # Use default scenario name if empty
            if not scenario_name:
                scenario_name = f"Scenario {len(self.scenarios) + 1}"
                
            # Generate UID
            uid = str(uuid.uuid4())[:8]
            
            # Calculate metrics
            return_rate = safe_divide(returns_30, sales_30) * 100
            amortized_solution_cost = safe_divide(solution_cost, (sales_30 * 12))

            return_cost_30 = returns_30 * current_unit_cost
            return_cost_annual = return_cost_30 * 12
            revenue_impact_30 = returns_30 * avg_sale_price
            revenue_impact_annual = revenue_impact_30 * 12
            new_unit_cost = current_unit_cost + additional_cost_per_item

            avoided_returns = returns_30 * (reduction_rate / 100)
            avoided_returns_annual = avoided_returns * 12
            savings_30 = avoided_returns * (avg_sale_price - new_unit_cost)
            annual_savings = savings_30 * 12
            annual_additional_costs = additional_cost_per_item * sales_30 * 12
            net_benefit = annual_savings - annual_additional_costs

            # Calculate ROI metrics
            roi = net_benefit / solution_cost if solution_cost > 0 else None
            monthly_net_benefit = net_benefit / 12 if net_benefit > 0 else 0
            break_even_days = solution_cost / (monthly_net_benefit / 30) if monthly_net_benefit > 0 else None
            break_even_months = solution_cost / monthly_net_benefit if monthly_net_benefit > 0 else None
            
            # Calculate score - weight ROI higher and penalize long break-even periods
            score = (roi * 100 - break_even_days / 3) if roi is not None and break_even_days is not None else None

            # Calculate margins
            margin_before = avg_sale_price - current_unit_cost
            margin_before_percentage = safe_divide(margin_before, avg_sale_price) * 100
            margin_after = avg_sale_price - new_unit_cost
            margin_after_percentage = safe_divide(margin_after, avg_sale_price) * 100
            margin_after_amortized = margin_after - amortized_solution_cost
            margin_after_amortized_percentage = safe_divide(margin_after_amortized, avg_sale_price) * 100
            
            # Handle tags
            if tags is None:
                tags = []
                
            # Create new scenario dictionary
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
                'margin_before_percentage': margin_before_percentage,
                'margin_after': margin_after,
                'margin_after_percentage': margin_after_percentage,
                'margin_after_amortized': margin_after_amortized,
                'margin_after_amortized_percentage': margin_after_amortized_percentage,
                'sales_365': sales_365,
                'returns_365': returns_365,
                'avoided_returns': avoided_returns,
                'avoided_returns_annual': avoided_returns_annual,
                'category': category,
                'tags': ','.join(tags)
            }

            # Add to dataframe
            self.scenarios = pd.concat([self.scenarios, pd.DataFrame([new_row])], ignore_index=True)
            return True, f"Scenario '{scenario_name}' added successfully"
            
        except Exception as e:
            return False, f"Error adding scenario: {str(e)}"
    
    def update_scenario(self, uid: str, **kwargs) -> Tuple[bool, str]:
        """Update an existing scenario."""
        try:
            if uid not in self.scenarios['uid'].values:
                return False, f"Scenario with UID {uid} not found"
                
            # Get index of scenario
            idx = self.scenarios[self.scenarios['uid'] == uid].index[0]
            
            # Update values
            for key, value in kwargs.items():
                if key in self.scenarios.columns:
                    self.scenarios.at[idx, key] = value
            
            # Recalculate metrics
            self.recalculate_scenario(uid)
            return True, f"Scenario updated successfully"
            
        except Exception as e:
            return False, f"Error updating scenario: {str(e)}"
    
    def delete_scenario(self, uid: str) -> Tuple[bool, str]:
        """Delete a scenario by UID."""
        try:
            if uid not in self.scenarios['uid'].values:
                return False, f"Scenario with UID {uid} not found"
                
            # Delete scenario
            self.scenarios = self.scenarios[self.scenarios['uid'] != uid]
            return True, f"Scenario deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting scenario: {str(e)}"
    
    def recalculate_scenario(self, uid: str) -> None:
        """Recalculate metrics for a scenario."""
        if uid not in self.scenarios['uid'].values:
            return
            
        idx = self.scenarios[self.scenarios['uid'] == uid].index[0]
        scenario = self.scenarios.loc[idx].to_dict()
        
        # Extract base values
        sales_30 = scenario['sales_30']
        avg_sale_price = scenario['avg_sale_price']
        returns_30 = scenario['returns_30']
        current_unit_cost = scenario['current_unit_cost']
        additional_cost_per_item = scenario['additional_cost_per_item']
        solution_cost = scenario['solution_cost']
        reduction_rate = scenario['reduction_rate']
        
        # Recalculate
        return_rate = safe_divide(returns_30, sales_30) * 100
        amortized_solution_cost = safe_divide(solution_cost, (sales_30 * 12))

        return_cost_30 = returns_30 * current_unit_cost
        return_cost_annual = return_cost_30 * 12
        revenue_impact_30 = returns_30 * avg_sale_price
        revenue_impact_annual = revenue_impact_30 * 12
        new_unit_cost = current_unit_cost + additional_cost_per_item

        avoided_returns = returns_30 * (reduction_rate / 100)
        avoided_returns_annual = avoided_returns * 12
        savings_30 = avoided_returns * (avg_sale_price - new_unit_cost)
        annual_savings = savings_30 * 12
        annual_additional_costs = additional_cost_per_item * sales_30 * 12
        net_benefit = annual_savings - annual_additional_costs

        roi = safe_divide(net_benefit, solution_cost)
        monthly_net_benefit = net_benefit / 12 if net_benefit > 0 else 0
        break_even_days = safe_divide(solution_cost, (monthly_net_benefit / 30))
        break_even_months = safe_divide(solution_cost, monthly_net_benefit)
        
        score = (roi * 100 - break_even_days / 3) if roi and break_even_days else None

        margin_before = avg_sale_price - current_unit_cost
        margin_before_percentage = safe_divide(margin_before, avg_sale_price) * 100
        margin_after = avg_sale_price - new_unit_cost
        margin_after_percentage = safe_divide(margin_after, avg_sale_price) * 100
        margin_after_amortized = margin_after - amortized_solution_cost
        margin_after_amortized_percentage = safe_divide(margin_after_amortized, avg_sale_price) * 100
        
        # Update scenario
        updates = {
            'return_rate': return_rate,
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
            'annual_additional_costs': annual_additional_costs,
            'net_benefit': net_benefit,
            'margin_before': margin_before,
            'margin_before_percentage': margin_before_percentage,
            'margin_after': margin_after,
            'margin_after_percentage': margin_after_percentage,
            'margin_after_amortized': margin_after_amortized,
            'margin_after_amortized_percentage': margin_after_amortized_percentage,
            'avoided_returns': avoided_returns,
            'avoided_returns_annual': avoided_returns_annual
        }
        
        for key, value in updates.items():
            self.scenarios.at[idx, key] = value
    
    def get_scenario(self, uid: str) -> Optional[Dict]:
        """Get a scenario by UID."""
        if uid not in self.scenarios['uid'].values:
            return None
        return self.scenarios[self.scenarios['uid'] == uid].iloc[0].to_dict()
    
    def get_all_scenarios(self) -> pd.DataFrame:
        """Get all scenarios."""
        return self.scenarios.copy()
    
    def export_scenarios_csv(self) -> str:
        """Export scenarios as CSV string."""
        return self.scenarios.to_csv(index=False)
    
    def export_scenarios_excel(self) -> bytes:
        """Export scenarios as Excel bytes."""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            self.scenarios.to_excel(writer, sheet_name='Scenarios', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Scenarios']
            
            # Add formatting
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#1abc9c',
                'color': 'white',
                'border': 1
            })
            
            # Write headers with formatting
            for col_num, value in enumerate(self.scenarios.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Auto-adjust column width
            for i, col in enumerate(self.scenarios.columns):
                max_len = max(
                    self.scenarios[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet.set_column(i, i, max_len)
        
        return output.getvalue()
    
    def export_scenarios_json(self) -> str:
        """Export scenarios as JSON string."""
        return self.scenarios.to_json(orient='records')
    
    def import_scenarios_csv(self, csv_data: str) -> Tuple[bool, str]:
        """Import scenarios from CSV string."""
        try:
            df = pd.read_csv(io.StringIO(csv_data))
            required_cols = ['sku', 'sales_30', 'avg_sale_price', 'returns_30', 'solution_cost']
            
            if not all(col in df.columns for col in required_cols):
                return False, "CSV is missing required columns"
                
            # Validate and clean data
            self.scenarios = pd.concat([self.scenarios, df], ignore_index=True)
            
            # Regenerate UIDs to avoid conflicts
            for idx in range(len(df)):
                self.scenarios.at[len(self.scenarios) - len(df) + idx, 'uid'] = str(uuid.uuid4())[:8]
                
            # Recalculate all metrics
            for uid in self.scenarios['uid'].values[-len(df):]:
                self.recalculate_scenario(uid)
                
            return True, f"Successfully imported {len(df)} scenarios"
            
        except Exception as e:
            return False, f"Error importing scenarios: {str(e)}"
    
    def import_scenarios_json(self, json_data: str) -> Tuple[bool, str]:
        """Import scenarios from JSON string."""
        try:
            data = json.loads(json_data)
            df = pd.DataFrame(data)
            
            required_cols = ['sku', 'sales_30', 'avg_sale_price', 'returns_30', 'solution_cost']
            if not all(col in df.columns for col in required_cols):
                return False, "JSON is missing required columns"
                
            # Validate and clean data
            self.scenarios = pd.concat([self.scenarios, df], ignore_index=True)
            
            # Regenerate UIDs to avoid conflicts
            for idx in range(len(df)):
                self.scenarios.at[len(self.scenarios) - len(df) + idx, 'uid'] = str(uuid.uuid4())[:8]
                
            # Recalculate all metrics
            for uid in self.scenarios['uid'].values[-len(df):]:
                self.recalculate_scenario(uid)
                
            return True, f"Successfully imported {len(df)} scenarios"
            
        except Exception as e:
            return False, f"Error importing scenarios: {str(e)}"
    
    def compare_scenarios(self, uids: List[str]) -> Optional[pd.DataFrame]:
        """Compare multiple scenarios side by side."""
        if not all(uid in self.scenarios['uid'].values for uid in uids):
            return None
            
        comparison_df = self.scenarios[self.scenarios['uid'].isin(uids)].copy()
        return comparison_df
    
    def get_top_scenarios(self, metric: str = 'roi', n: int = 5, ascending: bool = False) -> pd.DataFrame:
        """Get top scenarios by a specific metric."""
        if metric not in self.scenarios.columns:
            return pd.DataFrame()
            
        return self.scenarios.sort_values(by=metric, ascending=ascending).head(n)
    
    def get_recommendations(self) -> List[Dict]:
        """Generate recommendations based on scenario analysis."""
        recommendations = []
        
        # If we have scenarios
        if not self.scenarios.empty:
            # Recommend high ROI scenarios
            high_roi = self.get_top_scenarios(metric='roi', n=1)
            if not high_roi.empty and high_roi['roi'].iloc[0] > 1:
                recommendations.append({
                    'title': 'Best ROI Opportunity',
                    'scenario': high_roi['scenario_name'].iloc[0],
                    'metric': f"ROI: {high_roi['roi'].iloc[0]:.2f}x",
                    'description': f"The '{high_roi['solution'].iloc[0]}' solution for {high_roi['sku'].iloc[0]} offers the highest return on investment."
                })
            
            # Recommend quick break-even scenarios
            quick_breakeven = self.get_top_scenarios(metric='break_even_days', n=1, ascending=True)
            if not quick_breakeven.empty and quick_breakeven['break_even_days'].iloc[0] < 90:
                recommendations.append({
                    'title': 'Quickest Break-Even',
                    'scenario': quick_breakeven['scenario_name'].iloc[0],
                    'metric': f"{quick_breakeven['break_even_days'].iloc[0]:.0f} days",
                    'description': f"The '{quick_breakeven['solution'].iloc[0]}' solution for {quick_breakeven['sku'].iloc[0]} has the fastest payback period."
                })
            
            # Recommend highest net benefit
            best_benefit = self.get_top_scenarios(metric='net_benefit', n=1)
            if not best_benefit.empty and best_benefit['net_benefit'].iloc[0] > 0:
                recommendations.append({
                    'title': 'Highest Annual Benefit',
                    'scenario': best_benefit['scenario_name'].iloc[0],
                    'metric': f"${best_benefit['net_benefit'].iloc[0]:,.2f}/year",
                    'description': f"The '{best_benefit['solution'].iloc[0]}' solution for {best_benefit['sku'].iloc[0]} generates the highest annual financial benefit."
                })
            
            # Find scenarios with declining margins
            margin_decline = self.scenarios[self.scenarios['margin_after'] < self.scenarios['margin_before']]
            if not margin_decline.empty:
                recommendations.append({
                    'title': 'Margin Alert',
                    'scenario': margin_decline['scenario_name'].iloc[0],
                    'metric': 'Margin Decline',
                    'description': f"{len(margin_decline)} scenario(s) show margin decline after implementation. Review these carefully."
                })
        
        return recommendations
    
    def generate_sample_scenarios(self) -> None:
        """Generate sample scenarios for demonstration."""
        # Clear existing scenarios
        self.scenarios = pd.DataFrame(columns=self.scenarios.columns)
        
        # Example 1: High ROI packaging improvement
        self.add_scenario(
            "Premium Packaging", "PREMIUM-BOX", 500, 79.99, "Website",
            50, "Enhanced packaging with QR instructions", 3500, 1.25,
            22.50, 30, 6000, 600, "Home Goods", ["packaging", "premium"]
        )
        
        # Example 2: Size guide improvement
        self.add_scenario(
            "Size Guide Update", "APPAREL-001", 1200, 45.50, "Amazon",
            240, "Interactive size guide on product page", 1500, 0,
            12.75, 22, 14000, 2800, "Apparel", ["size guide", "website"]
        )
        
        # Example 3: Product quality improvement
        self.add_scenario(
            "Quality Improvement", "TECH-101", 300, 129.99, "Retail",
            45, "Component upgrade to reduce failures", 8000, 4.50,
            38.25, 60, 3600, 540, "Electronics", ["quality", "hardware"]
        )
        
        # Example 4: Customer service enhancement
        self.add_scenario(
            "Follow-up Service", "MULTI-SKU", 850, 65.75, "Multi-channel",
            85, "Post-purchase support program", 4500, 2.25,
            18.50, 15, 10000, 1000, "All Categories", ["customer service"]
        )

# Initialize app
if "app" not in st.session_state:
    st.session_state.app = ReturnOptimizer()
app = st.session_state.app

# Create the sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/dvilasuero/KaizenROI/main/logo.png", width=200)
    
    # Navigation
    selected = option_menu(
        "Navigation",
        ["Dashboard", "Add Scenario", "Analyze", "Compare", "Export/Import", "Settings", "Help"],
        icons=["house", "plus-circle", "graph-up", "bar-chart", "download", "gear", "question-circle"],
        menu_icon="list",
        default_index=0,
    )
    
    # Quick Stats
    if not app.scenarios.empty:
        st.subheader("Quick Stats")
        st.markdown(f"**Scenarios:** {len(app.scenarios)}")
        
        if 'roi' in app.scenarios.columns:
            avg_roi = app.scenarios['roi'].mean()
            st.markdown(f"**Avg ROI:** {avg_roi:.2f}x")
        
        if 'net_benefit' in app.scenarios.columns:
            total_benefit = app.scenarios['net_benefit'].sum()
            st.markdown(f"**Total Benefit:** ${total_benefit:,.2f}/year")
    
    # Sample data button
    if st.button("Load Sample Data"):
        app.generate_sample_scenarios()
        st.success("Sample scenarios loaded!")

# Main content
if selected == "Dashboard":
    st.title("📊 KaizenROI Dashboard")
    st.markdown("#### Smart Return Optimization Suite")
    
    if app.scenarios.empty:
        st.info("No scenarios yet. Add a scenario or load sample data from the sidebar to get started.")
        
        # Show intro
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("### Welcome to KaizenROI")
            st.markdown("""
            KaizenROI helps you evaluate return reduction investments with precision. Use this tool to:
            
            - Calculate ROI for return reduction initiatives
            - Compare different scenarios and solutions
            - Visualize financial impact and break-even points
            - Make data-driven decisions for your business
            
            Get started by adding your first scenario or loading sample data from the sidebar.
            """)
        with col2:
            st.image("https://raw.githubusercontent.com/dvilasuero/KaizenROI/main/dashboard_preview.png", use_column_width=True)
    else:
        # Show key metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_investment = app.scenarios['solution_cost'].sum()
            st.markdown(create_metric_html("Total Investment", format_currency(total_investment)), unsafe_allow_html=True)
        
        with col2:
            total_annual_benefit = app.scenarios['net_benefit'].sum()
            st.markdown(create_metric_html("Annual Benefit", format_currency(total_annual_benefit)), unsafe_allow_html=True)
        
        with col3:
            avg_roi = app.scenarios['roi'].mean()
            st.markdown(create_metric_html("Average ROI", f"{avg_roi:.2f}x"), unsafe_allow_html=True)
        
        with col4:
            weighted_avg_breakeven = (app.scenarios['solution_cost'] * app.scenarios['break_even_days']).sum() / app.scenarios['solution_cost'].sum() if app.scenarios['solution_cost'].sum() > 0 else 0
            st.markdown(create_metric_html("Avg Break-even", f"{weighted_avg_breakeven:.0f} days"), unsafe_allow_html=True)
        
        # ROI Visualization
        st.subheader("ROI Analysis")
        
        # Prepare data for visualization
        viz_df = app.scenarios.sort_values('roi', ascending=False).copy()
        viz_df = viz_df.head(10)  # Show top 10 for readability
        
        # Create ROI chart
        fig = px.bar(
            viz_df,
            x='scenario_name',
            y='roi',
            color='roi',
            color_continuous_scale='viridis',
            title="Return on Investment by Scenario",
            labels={'roi': 'ROI (x)', 'scenario_name': 'Scenario'},
            height=400
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Financial Impact & Break-even Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Financial Impact")
            impact_fig = px.bar(
                viz_df,
                x='scenario_name',
                y=['annual_savings', 'annual_additional_costs'],
                barmode='group',
                title="Annual Financial Impact",
                labels={
                    'scenario_name': 'Scenario',
                    'value': 'Amount ($)',
                    'variable': 'Metric'
                },
                height=400,
                color_discrete_map={
                    'annual_savings': '#2ecc71',
                    'annual_additional_costs': '#e74c3c'
                }
            )
            impact_fig.update_layout(xaxis_tickangle=-45, legend_title="")
            st.plotly_chart(impact_fig, use_container_width=True)
        
        with col2:
            st.subheader("Break-even Analysis")
            breakeven_fig = px.scatter(
                viz_df,
                x='solution_cost',
                y='break_even_days',
                size='net_benefit',
                color='roi',
                color_continuous_scale='viridis',
                hover_name='scenario_name',
                title="Investment vs. Break-even Time",
                labels={
                    'solution_cost': 'Investment ($)',
                    'break_even_days': 'Break-even (days)',
                    'net_benefit': 'Annual Benefit'
                },
                height=400
            )
            st.plotly_chart(breakeven_fig, use_container_width=True)
        
        # Recommendations
        st.subheader("Recommendations")
        recommendations = app.get_recommendations()
        
        if recommendations:
            rec_cols = st.columns(len(recommendations))
            for i, rec in enumerate(recommendations):
                with rec_cols[i]:
                    st.markdown(f"**{rec['title']}**")
                    st.markdown(f"*{rec['scenario']}*")
                    st.markdown(f"**{rec['metric']}**")
                    st.markdown(rec['description'])
        else:
            st.info("No recommendations available yet. Add more scenarios to get insights.")
        
        # Recent scenarios
        st.subheader("Recent Scenarios")
        recent_df = app.scenarios.sort_values('timestamp', ascending=False).head(5)
        
        # Show only relevant columns
        display_cols = ['scenario_name', 'sku', 'solution', 'solution_cost', 'roi', 'break_even_days', 'net_benefit']
        st.dataframe(recent_df[display_cols], use_container_width=True)

elif selected == "Add Scenario":
    st.title("➕ Add New Scenario")
    st.markdown("Enter details about your return reduction initiative to analyze its ROI and financial impact.")
    
    with st.form("input_form"):
        # Layout in two columns for better space utilization
        col1, col2 = st.columns(2)
        
        # Basic Information
        st.subheader("Basic Information")
        scenario_name = col1.text_input("Scenario Name", help="A descriptive name for this scenario")
        sku = col2.text_input("SKU/Product", help="Product SKU or identifier")
        category = col1.text_input("Category (optional)", help="Product category for grouping")
        sales_channel = col2.text_input("Sales Channel", help="Primary sales channel (e.g., Amazon, Website)")
        
        # Sales and Return Data
        st.subheader("Sales & Return Data")
        sales_30 = col1.number_input("30-day Sales (units)", min_value=0.0, help="Number of units sold in the last 30 days")
        returns_30 = col2.number_input("30-day Returns (units)", min_value=0.0, help="Number of units returned in the last 30 days")
        sales_365 = col1.number_input("Annual Sales (optional)", min_value=0.0, help="Number of units sold annually, if known")
        returns_365 = col2.number_input("Annual Returns (optional)", min_value=0.0, help="Number of units returned annually, if known")
        
        # Financial Data
        st.subheader("Financial Data")
        avg_sale_price = col1.number_input("Average Sale Price ($)", min_value=0.0, help="Average selling price per unit")
        current_unit_cost = col2.number_input("Current Unit Cost ($)", min_value=0.0, help="Current cost to produce each unit")
        
        # Solution Details
        st.subheader("Solution Details")
        solution = col1.text_input("Proposed Solution", help="Brief description of your return reduction initiative")
        solution_cost = col2.number_input("Implementation Cost ($)", min_value=0.0, help="One-time cost to implement the solution")
        additional_cost_per_item = col1.number_input("Additional Cost per Item ($)", min_value=0.0, help="Any additional cost per unit after implementing the solution")
        reduction_rate = col2.slider("Estimated Return Reduction (%)", 0, 100, 10, help="Estimated percentage reduction in returns")
        
        # Advanced Options
        with st.expander("Advanced Options"):
            tags = st.text_input("Tags (comma separated)", help="Add tags for filtering scenarios")
            
        # Submit button
        submit = st.form_submit_button("Add Scenario")
        
        if submit:
            # Validate form
            if not sku:
                st.error("SKU/Product is required")
            elif sales_30 <= 0:
                st.error("Sales must be greater than zero")
            elif returns_30 > sales_30:
                st.error("Returns cannot exceed sales")
            else:
                # Process tags
                tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
                
                # Add scenario
                success, message = app.add_scenario(
                    scenario_name, sku, sales_30, avg_sale_price, sales_channel,
                    returns_30, solution, solution_cost, additional_cost_per_item,
                    current_unit_cost, reduction_rate, sales_365, returns_365,
                    category, tag_list
                )
                
                if success:
                    st.success(message)
                    
                    # Preview the added scenario
                    st.subheader("Scenario Preview")
                    
                    # Get the newly added scenario
                    new_scenario = app.scenarios.iloc[-1]
                    
                    # Show key metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("ROI", f"{new_scenario['roi']:.2f}x" if new_scenario['roi'] else "N/A")
                    col2.metric("Break-even", f"{new_scenario['break_even_days']:.0f} days" if new_scenario['break_even_days'] else "N/A")
                    col3.metric("Annual Benefit", f"${new_scenario['net_benefit']:,.2f}" if new_scenario['net_benefit'] else "N/A")
                    
                    # Show financial impact
                    impact_data = {
                        'Metric': ['Current Margin', 'New Margin', 'Annual Savings', 'Annual Extra Cost', 'Net Benefit'],
                        'Value': [
                            new_scenario['margin_before'],
                            new_scenario['margin_after'],
                            new_scenario['annual_savings'],
                            new_scenario['annual_additional_costs'],
                            new_scenario['net_benefit']
                        ]
                    }
                    impact_df = pd.DataFrame(impact_data)
                    
                    # Set colors
                    colors = ['#3498db', '#2ecc71' if new_scenario['margin_after'] >= new_scenario['margin_before'] else '#e74c3c', 
                             '#2ecc71', '#e74c3c', '#3498db']
                    
                    fig = px.bar(
                        impact_df,
                        x='Metric',
                        y='Value',
                        title="Financial Impact",
                        color='Metric',
                        color_discrete_sequence=colors
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(message)
    
    # Add quick example button outside the form
    if st.button("▶️ Run Example Scenario"):
        success, message = app.add_scenario(
            "Example ROI Case", "SKU123", 400, 50, "Amazon",
            40, "Better packaging", 2000, 2, 18, 25, 4800, 450
        )
        if success:
            st.success("Example scenario added!")
        else:
            st.error(message)

elif selected == "Analyze":
    st.title("📈 Analyze Scenarios")
    
    if app.scenarios.empty:
        st.info("No scenarios yet. Add a scenario or load sample data from the sidebar to start analysis.")
    else:
        # Filters
        with st.expander("Filters", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            # Filter by category
            categories = ['All'] + list(app.scenarios['category'].unique())
            selected_category = col1.selectbox("Category", categories)
            
            # Filter by ROI range
            min_roi, max_roi = 0.0, float(app.scenarios['roi'].max() * 1.2) if not app.scenarios['roi'].isna().all() else 5.0
            roi_range = col2.slider("ROI Range", min_roi, max_roi, (min_roi, max_roi))
            
            # Filter by solution cost
            min_cost, max_cost = 0.0, float(app.scenarios['solution_cost'].max() * 1.2)
            cost_range = col3.slider("Solution Cost Range", min_cost, max_cost, (min_cost, max_cost))
            
            # Advanced search
            search_term = st.text_input("Search by SKU, Solution, or Scenario Name")
        
        # Apply filters
        filtered_df = app.scenarios.copy()
        
        if selected_category != 'All':
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        
        filtered_df = filtered_df[
            (filtered_df['roi'] >= roi_range[0]) &
            (filtered_df['roi'] <= roi_range[1]) &
            (filtered_df['solution_cost'] >= cost_range[0]) &
            (filtered_df['solution_cost'] <= cost_range[1])
        ]
        
        if search_term:
            filtered_df = filtered_df[
                filtered_df['sku'].str.contains(search_term, case=False, na=False) |
                filtered_df['solution'].str.contains(search_term, case=False, na=False) |
                filtered_df['scenario_name'].str.contains(search_term, case=False, na=False)
            ]
        
        # Show analysis
        if filtered_df.empty:
            st.warning("No scenarios match your filters. Try adjusting the filter criteria.")
        else:
            st.subheader(f"Analysis Results ({len(filtered_df)} scenarios)")
            
            # Tabs for different analyses
            tab1, tab2, tab3, tab4 = st.tabs(["ROI Analysis", "Financial Impact", "Return Reduction", "Margin Analysis"])
            
            with tab1:
                # ROI Analysis
                st.markdown("### ROI Comparison")
                
                # Sort by ROI
                roi_df = filtered_df.sort_values('roi', ascending=False)
                
                # Create combined chart
                roi_fig = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=("Return on Investment", "Break-even Period"),
                    specs=[[{"type": "bar"}, {"type": "bar"}]]
                )
                
                # ROI Bar
                roi_fig.add_trace(
                    go.Bar(
                        x=roi_df['scenario_name'],
                        y=roi_df['roi'],
                        marker_color='#1abc9c',
                        name="ROI"
                    ),
                    row=1, col=1
                )
                
                # Break-even Bar
                roi_fig.add_trace(
                    go.Bar(
                        x=roi_df['scenario_name'],
                        y=roi_df['break_even_days'] / 30,  # Convert to months for better visualization
                        marker_color='#f39c12',
                        name="Break-even (months)"
                    ),
                    row=1, col=2
                )
                
                roi_fig.update_layout(height=500, bargap=0.2)
                roi_fig.update_xaxes(tickangle=-45)
                
                st.plotly_chart(roi_fig, use_container_width=True)
                
                # ROI vs Investment scatter plot
                st.markdown("### ROI vs. Investment")
                scatter_fig = px.scatter(
                    roi_df,
                    x='solution_cost',
                    y='roi',
                    size='net_benefit',
                    color='break_even_days',
                    color_continuous_scale='viridis',
                    hover_name='scenario_name',
                    labels={
                        'solution_cost': 'Investment ($)',
                        'roi': 'ROI (x)',
                        'break_even_days': 'Break-even (days)',
                        'net_benefit': 'Annual Benefit ($)'
                    },
                    height=500
                )
                st.plotly_chart(scatter_fig, use_container_width=True)
            
            with tab2:
                # Financial Impact
                st.markdown("### Financial Impact Analysis")
                
                # Sort by net benefit
                benefit_df = filtered_df.sort_values('net_benefit', ascending=False)
                
                # Stacked financial impact
                impact_fig = go.Figure()
                
                # Annual savings
                impact_fig.add_trace(
                    go.Bar(
                        x=benefit_df['scenario_name'],
                        y=benefit_df['annual_savings'],
                        name="Annual Savings",
                        marker_color='#2ecc71'
                    )
                )
                
                # Annual additional costs (negative)
                impact_fig.add_trace(
                    go.Bar(
                        x=benefit_df['scenario_name'],
                        y=-benefit_df['annual_additional_costs'],
                        name="Annual Additional Costs",
                        marker_color='#e74c3c'
                    )
                )
                
                # Net benefit line
                impact_fig.add_trace(
                    go.Scatter(
                        x=benefit_df['scenario_name'],
                        y=benefit_df['net_benefit'],
                        mode='lines+markers',
                        name="Net Benefit",
                        line=dict(color='#3498db', width=3)
                    )
                )
                
                impact_fig.update_layout(
                    barmode='relative',
                    title="Annual Financial Impact by Scenario",
                    xaxis_title="Scenario",
                    yaxis_title="Amount ($)",
                    height=500
                )
                impact_fig.update_xaxes(tickangle=-45)
                
                st.plotly_chart(impact_fig, use_container_width=True)
                
                # Revenue impact chart
                st.markdown("### Revenue Impact")
                revenue_fig = px.bar(
                    benefit_df,
                    x='scenario_name',
                    y=['revenue_impact_annual', 'return_cost_annual'],
                    barmode='group',
                    title="Annual Revenue and Cost Impact from Returns",
                    labels={
                        'scenario_name': 'Scenario',
                        'value': 'Amount ($)',
                        'variable': 'Metric'
                    },
                    height=400,
                    color_discrete_map={
                        'revenue_impact_annual': '#9b59b6',
                        'return_cost_annual': '#e67e22'
                    }
                )
                revenue_fig.update_layout(xaxis_tickangle=-45, legend_title="")
                st.plotly_chart(revenue_fig, use_container_width=True)
            
            with tab3:
                # Return Reduction Analysis
                st.markdown("### Return Rate Analysis")
                
                # Create data for visualization
                return_data = []
                for _, row in filtered_df.iterrows():
                    return_data.append({
                        'scenario': row['scenario_name'],
                        'state': 'Current',
                        'rate': row['return_rate']
                    })
                    return_data.append({
                        'scenario': row['scenario_name'],
                        'state': 'Projected',
                        'rate': row['return_rate'] * (1 - row['reduction_rate']/100)
                    })
                
                return_rate_df = pd.DataFrame(return_data)
                
                # Create return rate chart
                return_fig = px.bar(
                    return_rate_df,
                    x='scenario',
                    y='rate',
                    color='state',
                    barmode='group',
                    title="Return Rate: Current vs. Projected",
                    labels={
                        'scenario': 'Scenario',
                        'rate': 'Return Rate (%)',
                        'state': 'State'
                    },
                    height=500,
                    color_discrete_map={
                        'Current': '#e74c3c',
                        'Projected': '#2ecc71'
                    }
                )
                return_fig.update_layout(xaxis_tickangle=-45)
                
                st.plotly_chart(return_fig, use_container_width=True)
                
                # Return reduction visualization
                st.markdown("### Return Reduction Impact")
                
                # Prepare data
                impact_df = filtered_df.sort_values('avoided_returns_annual', ascending=False)
                
                # Create chart
                avoided_fig = go.Figure()
                
                # Avoided returns
                avoided_fig.add_trace(
                    go.Bar(
                        x=impact_df['scenario_name'],
                        y=impact_df['avoided_returns_annual'],
                        name="Returns Avoided Annually",
                        marker_color='#3498db'
                    )
                )
                
                # Reduction percentage
                avoided_fig.add_trace(
                    go.Scatter(
                        x=impact_df['scenario_name'],
                        y=impact_df['reduction_rate'],
                        mode='lines+markers',
                        name="Reduction Rate (%)",
                        yaxis='y2',
                        line=dict(color='#f39c12', width=3)
                    )
                )
                
                avoided_fig.update_layout(
                    title="Annual Returns Avoided by Scenario",
                    xaxis_title="Scenario",
                    yaxis_title="Returns Avoided (units)",
                    yaxis2=dict(
                        title="Reduction Rate (%)",
                        titlefont=dict(color="#f39c12"),
                        tickfont=dict(color="#f39c12"),
                        overlaying="y",
                        side="right"
                    ),
                    height=500,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                avoided_fig.update_xaxes(tickangle=-45)
                
                st.plotly_chart(avoided_fig, use_container_width=True)
            
            with tab4:
                # Margin Analysis
                st.markdown("### Margin Analysis")
                
                # Prepare data for margin chart
                margin_data = []
                for _, row in filtered_df.iterrows():
                    margin_data.append({
                        'scenario': row['scenario_name'],
                        'type': 'Current Margin',
                        'value': row['margin_before']
                    })
                    margin_data.append({
                        'scenario': row['scenario_name'],
                        'type': 'New Margin',
                        'value': row['margin_after']
                    })
                    margin_data.append({
                        'scenario': row['scenario_name'],
                        'type': 'Amortized Margin',
                        'value': row['margin_after_amortized']
                    })
                
                margin_df = pd.DataFrame(margin_data)
                
                # Create margin comparison chart
                margin_fig = px.bar(
                    margin_df,
                    x='scenario',
                    y='value',
                    color='type',
                    barmode='group',
                    title="Margin Comparison by Scenario",
                    labels={
                        'scenario': 'Scenario',
                        'value': 'Margin ($)',
                        'type': 'Margin Type'
                    },
                    height=500,
                    color_discrete_map={
                        'Current Margin': '#3498db',
                        'New Margin': '#2ecc71',
                        'Amortized Margin': '#9b59b6'
                    }
                )
                margin_fig.update_layout(xaxis_tickangle=-45)
                
                st.plotly_chart(margin_fig, use_container_width=True)
                
                # Margin percentage chart
                st.markdown("### Margin Percentage Analysis")
                
                # Prepare percentage data
                pct_data = []
                for _, row in filtered_df.iterrows():
                    pct_data.append({
                        'scenario': row['scenario_name'],
                        'type': 'Current Margin',
                        'value': row['margin_before_percentage']
                    })
                    pct_data.append({
                        'scenario': row['scenario_name'],
                        'type': 'New Margin',
                        'value': row['margin_after_percentage']
                    })
                    pct_data.append({
                        'scenario': row['scenario_name'],
                        'type': 'Amortized Margin',
                        'value': row['margin_after_amortized_percentage']
                    })
                
                pct_df = pd.DataFrame(pct_data)
                
                # Create margin percentage chart
                pct_fig = px.bar(
                    pct_df,
                    x='scenario',
                    y='value',
                    color='type',
                    barmode='group',
                    title="Margin Percentage by Scenario",
                    labels={
                        'scenario': 'Scenario',
                        'value': 'Margin (%)',
                        'type': 'Margin Type'
                    },
                    height=500,
                    color_discrete_map={
                        'Current Margin': '#3498db',
                        'New Margin': '#2ecc71',
                        'Amortized Margin': '#9b59b6'
                    }
                )
                pct_fig.update_layout(xaxis_tickangle=-45)
                
                st.plotly_chart(pct_fig, use_container_width=True)
            
            # Scenario details table
            st.subheader("Scenario Details")
            
            # Select columns to display
            display_cols = [
                'scenario_name', 'sku', 'solution', 'solution_cost', 'return_rate',
                'reduction_rate', 'roi', 'break_even_days', 'net_benefit'
            ]
            
            # Format the display dataframe
            display_df = filtered_df[display_cols].copy()
            display_df['return_rate'] = display_df['return_rate'].apply(lambda x: f"{x:.2f}%")
            display_df['reduction_rate'] = display_df['reduction_rate'].apply(lambda x: f"{x:.0f}%")
            display_df['roi'] = display_df['roi'].apply(lambda x: f"{x:.2f}x" if not pd.isna(x) else "N/A")
            display_df['break_even_days'] = display_df['break_even_days'].apply(lambda x: f"{x:.0f}" if not pd.isna(x) else "N/A")
            display_df['net_benefit'] = display_df['net_benefit'].apply(lambda x: f"${x:,.2f}")
            display_df['solution_cost'] = display_df['solution_cost'].apply(lambda x: f"${x:,.2f}")
            
            # Rename columns for display
            display_df.columns = [
                'Scenario', 'SKU', 'Solution', 'Cost', 'Return Rate',
                'Reduction', 'ROI', 'Break-even (days)', 'Annual Benefit'
            ]
            
            st.dataframe(display_df, use_container_width=True)
            
            # Download current filtered data
            csv_data = filtered_df.to_csv(index=False).encode()
            st.download_button(
                "📥 Download Filtered Data",
                data=csv_data,
                file_name="kaizenroi_analysis.csv",
                mime="text/csv"
            )
            
            # Add option to create PDF report
            if st.button("📊 Generate PDF Report"):
                st.info("Report generation would be implemented here in a production version.")

elif selected == "Compare":
    st.title("🔄 Compare Scenarios")
    st.markdown("Select scenarios to compare side-by-side")
    
    if app.scenarios.empty:
        st.info("No scenarios yet. Add a scenario or load sample data from the sidebar.")
    else:
        # Get all scenario names for selection
        scenario_options = app.scenarios['scenario_name'].tolist()
        
        # Let user select scenarios to compare
        selected_scenarios = st.multiselect("Select scenarios to compare", scenario_options)
        
        if selected_scenarios:
            # Get UIDs for selected scenarios
            selected_uids = app.scenarios[app.scenarios['scenario_name'].isin(selected_scenarios)]['uid'].tolist()
            
            # Get comparison dataframe
            comparison_df = app.compare_scenarios(selected_uids)
            
            if comparison_df is not None and not comparison_df.empty:
                st.subheader("Side-by-Side Comparison")
                
                # Create tabs for different comparison views
                tab1, tab2, tab3 = st.tabs(["Key Metrics", "Financial Impact", "Detailed Comparison"])
                
                with tab1:
                    # Key metrics comparison
                    metrics = ['roi', 'break_even_days', 'net_benefit', 'return_rate', 'reduction_rate']
                    metric_labels = ['ROI (x)', 'Break-even (days)', 'Annual Benefit ($)', 'Return Rate (%)', 'Reduction (%)']
                    
                    # Prepare data for visualization
                    comparison_metrics = pd.melt(
                        comparison_df,
                        id_vars=['scenario_name'],
                        value_vars=metrics,
                        var_name='metric',
                        value_name='value'
                    )
                    
                    # Create mapping for metric labels
                    metric_map = dict(zip(metrics, metric_labels))
                    comparison_metrics['metric'] = comparison_metrics['metric'].map(metric_map)
                    
                    # Create comparison chart
                    fig = px.bar(
                        comparison_metrics,
                        x='metric',
                        y='value',
                        color='scenario_name',
                        barmode='group',
                        height=500,
                        labels={
                            'metric': 'Metric',
                            'value': 'Value',
                            'scenario_name': 'Scenario'
                        }
                    )
                    
                    # Adjust layout for readability
                    fig.update_layout(
                        title="Key Metrics Comparison",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show percentage differences
                    if len(selected_scenarios) == 2:
                        st.subheader("Percentage Difference")
                        
                        # Calculate percentage differences
                        diff_data = []
                        for metric in metrics:
                            if comparison_df[metric].iloc[0] != 0:
                                pct_diff = ((comparison_df[metric].iloc[1] - comparison_df[metric].iloc[0]) / 
                                            comparison_df[metric].iloc[0] * 100)
                                diff_data.append({
                                    'Metric': metric_map[metric],
                                    'Difference (%)': pct_diff
                                })
                        
                        if diff_data:
                            diff_df = pd.DataFrame(diff_data)
                            
                            # Create percentage difference chart
                            diff_fig = px.bar(
                                diff_df,
                                x='Metric',
                                y='Difference (%)',
                                color='Difference (%)',
                                color_continuous_scale='RdBu',
                                color_continuous_midpoint=0,
                                height=300
                            )
                            
                            st.plotly_chart(diff_fig, use_container_width=True)
                
                with tab2:
                    # Financial impact comparison
                    st.markdown("### Financial Impact Comparison")
                    
                    # Create radar chart for financial metrics
                    financial_metrics = [
                        'annual_savings', 'annual_additional_costs', 'net_benefit',
                        'solution_cost', 'margin_after_amortized'
                    ]
                    
                    # Normalize the data for better visualization
                    radar_df = comparison_df.copy()
                    for metric in financial_metrics:
                        max_val = radar_df[metric].max()
                        if max_val > 0:
                            radar_df[metric] = radar_df[metric] / max_val * 100
                    
                    # Create radar chart
                    radar_fig = go.Figure()
                    
                    for i, row in radar_df.iterrows():
                        radar_fig.add_trace(go.Scatterpolar(
                            r=[row[m] for m in financial_metrics],
                            theta=[m.replace('_', ' ').title() for m in financial_metrics],
                            fill='toself',
                            name=row['scenario_name']
                        ))
                    
                    radar_fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )
                        ),
                        title="Financial Metrics Comparison (Normalized)",
                        height=500
                    )
                    
                    st.plotly_chart(radar_fig, use_container_width=True)
                    
                    # Show actual values in a bar chart
                    st.markdown("### Actual Financial Values")
                    
                    # Prepare data
                    financial_data = pd.melt(
                        comparison_df,
                        id_vars=['scenario_name'],
                        value_vars=financial_metrics,
                        var_name='metric',
                        value_name='value'
                    )
                    
                    # Create nicer labels
                    financial_data['metric'] = financial_data['metric'].apply(
                        lambda x: ' '.join(word.capitalize() for word in x.split('_'))
                    )
                    
                    # Create bar chart
                    financial_fig = px.bar(
                        financial_data,
                        x='metric',
                        y='value',
                        color='scenario_name',
                        barmode='group',
                        height=500,
                        labels={
                            'metric': 'Metric',
                            'value': 'Amount ($)',
                            'scenario_name': 'Scenario'
                        }
                    )
                    
                    # Format layout
                    financial_fig.update_layout(
                        xaxis_tickangle=-45,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(financial_fig, use_container_width=True)
                
                with tab3:
                    # Detailed side-by-side comparison
                    st.markdown("### Detailed Comparison")
                    
                    # Transpose the dataframe for side-by-side comparison
                    comparison_display = comparison_df.set_index('scenario_name').T
                    
                    # Define metrics to display and their order
                    display_metrics = [
                        'sku', 'sales_30', 'returns_30', 'return_rate', 'solution',
                        'solution_cost', 'additional_cost_per_item', 'reduction_rate',
                        'roi', 'break_even_days', 'break_even_months', 'net_benefit',
                        'annual_savings', 'annual_additional_costs', 'margin_before',
                        'margin_after', 'margin_after_amortized'
                    ]
                    
                    # Filter and order metrics
                    display_metrics = [m for m in display_metrics if m in comparison_display.index]
                    comparison_display = comparison_display.loc[display_metrics]
                    
                    # Define nicer row labels
                    row_labels = {
                        'sku': 'SKU',
                        'sales_30': '30-day Sales (units)',
                        'returns_30': '30-day Returns (units)',
                        'return_rate': 'Return Rate (%)',
                        'solution': 'Solution',
                        'solution_cost': 'Solution Cost ($)',
                        'additional_cost_per_item': 'Additional Cost per Item ($)',
                        'reduction_rate': 'Return Reduction (%)',
                        'roi': 'ROI (x)',
                        'break_even_days': 'Break-even (days)',
                        'break_even_months': 'Break-even (months)',
                        'net_benefit': 'Annual Net Benefit ($)',
                        'annual_savings': 'Annual Savings ($)',
                        'annual_additional_costs': 'Annual Additional Costs ($)',
                        'margin_before': 'Current Margin ($)',
                        'margin_after': 'New Margin ($)',
                        'margin_after_amortized': 'Amortized Margin ($)'
                    }
                    
                    # Rename the index
                    comparison_display.index = [row_labels.get(idx, idx) for idx in comparison_display.index]
                    
                    # Format numeric values
                    for idx in comparison_display.index:
                        if 'Cost' in idx or 'Margin' in idx or 'Benefit' in idx or 'Savings' in idx:
                            comparison_display.loc[idx] = comparison_display.loc[idx].apply(
                                lambda x: f"${x:,.2f}" if not pd.isna(x) else "N/A"
                            )
                        elif 'ROI' in idx:
                            comparison_display.loc[idx] = comparison_display.loc[idx].apply(
                                lambda x: f"{x:.2f}x" if not pd.isna(x) else "N/A"
                            )
                        elif 'days' in idx.lower() or 'months' in idx.lower():
                            comparison_display.loc[idx] = comparison_display.loc[idx].apply(
                                lambda x: f"{x:.1f}" if not pd.isna(x) else "N/A"
                            )
                        elif '%' in idx:
                            comparison_display.loc[idx] = comparison_display.loc[idx].apply(
                                lambda x: f"{x:.2f}%" if not pd.isna(x) else "N/A"
                            )
                    
                    # Display the comparison table
                    st.dataframe(comparison_display, use_container_width=True)
                    
                    # Provide option to download comparison
                    csv_comparison = comparison_df.to_csv(index=False).encode()
                    st.download_button(
                        "📥 Download Comparison",
                        data=csv_comparison,
                        file_name="kaizenroi_comparison.csv",
                        mime="text/csv"
                    )
        else:
            st.info("Select at least one scenario to compare.")
            
            # Show available scenarios
            st.subheader("Available Scenarios")
            
            # Display a preview of available scenarios
            preview_cols = ['scenario_name', 'sku', 'solution', 'roi', 'net_benefit']
            preview_df = app.scenarios[preview_cols].copy()
            preview_df['roi'] = preview_df['roi'].apply(lambda x: f"{x:.2f}x" if not pd.isna(x) else "N/A")
            preview_df['net_benefit'] = preview_df['net_benefit'].apply(lambda x: f"${x:,.2f}")
            
            # Rename columns for display
            preview_df.columns = ['Scenario', 'SKU', 'Solution', 'ROI', 'Annual Benefit']
            
            st.dataframe(preview_df, use_container_width=True)

elif selected == "Export/Import":
    st.title("📤 Export & Import")
    st.markdown("Export your scenarios or import from external sources")
    
    # Create tabs for export and import
    tab1, tab2 = st.tabs(["Export Data", "Import Data"])
    
    with tab1:
        st.subheader("Export Scenarios")
        
        if app.scenarios.empty:
            st.info("No scenarios to export. Add a scenario or load sample data from the sidebar.")
        else:
            # Export format selection
            export_format = st.radio(
                "Select export format",
                ["CSV", "Excel", "JSON"],
                horizontal=True
            )
            
            # Filter options
            with st.expander("Export Filters (Optional)"):
                # Filter by category
                categories = ['All'] + list(app.scenarios['category'].unique())
                export_category = st.selectbox("Category", categories, key="export_category")
                
                # Filter by date range
                export_date_range = st.date_input(
                    "Date range (if applicable)",
                    value=[datetime.now().date(), datetime.now().date()],
                    key="export_date_range"
                )
                
                # Search term
                export_search = st.text_input("Search term", key="export_search")
            
            # Apply filters
            export_df = app.scenarios.copy()
            
            if export_category != 'All':
                export_df = export_df[export_df['category'] == export_category]
            
            if export_search:
                export_df = export_df[
                    export_df['sku'].str.contains(export_search, case=False, na=False) |
                    export_df['solution'].str.contains(export_search, case=False, na=False) |
                    export_df['scenario_name'].str.contains(export_search, case=False, na=False)
                ]
            
            # Show export preview
            st.subheader(f"Export Preview ({len(export_df)} scenarios)")
            
            preview_cols = ['scenario_name', 'sku', 'solution', 'roi', 'net_benefit']
            preview_df = export_df[preview_cols].copy()
            
            st.dataframe(preview_df, use_container_width=True)
            
            # Export data
            if export_format == "CSV":
                csv_data = export_df.to_csv(index=False).encode()
                st.download_button(
                    "📥 Download CSV",
                    data=csv_data,
                    file_name="kaizenroi_export.csv",
                    mime="text/csv"
                )
            elif export_format == "Excel":
                excel_data = app.export_scenarios_excel()
                st.download_button(
                    "📊 Download Excel",
                    data=excel_data,
                    file_name="kaizenroi_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            elif export_format == "JSON":
                json_data = app.export_scenarios_json()
                st.download_button(
                    "📋 Download JSON",
                    data=json_data,
                    file_name="kaizenroi_export.json",
                    mime="application/json"
                )
    
    with tab2:
        st.subheader("Import Scenarios")
        
        # Import format selection
        import_format = st.radio(
            "Select import format",
            ["CSV", "Excel", "JSON"],
            horizontal=True
        )
        
        # Import options
        import_action = st.radio(
            "Import action",
            ["Append to existing scenarios", "Replace existing scenarios"],
            horizontal=True
        )
        
        # File uploader
        uploaded_file = st.file_uploader(f"Upload {import_format} file", type=[import_format.lower()])
        
        if uploaded_file is not None:
            try:
                # Process uploaded file
                if import_action == "Replace existing scenarios":
                    app.scenarios = pd.DataFrame(columns=app.scenarios.columns)
                
                if import_format == "CSV":
                    csv_data = uploaded_file.read().decode()
                    success, message = app.import_scenarios_csv(csv_data)
                elif import_format == "Excel":
                    df = pd.read_excel(uploaded_file)
                    csv_data = df.to_csv(index=False)
                    success, message = app.import_scenarios_csv(csv_data)
                elif import_format == "JSON":
                    json_data = uploaded_file.read().decode()
                    success, message = app.import_scenarios_json(json_data)
                
                if success:
                    st.success(message)
                    
                    # Show import results
                    st.subheader("Imported Scenarios")
                    
                    # Display the imported scenarios
                    preview_cols = ['scenario_name', 'sku', 'solution', 'roi', 'net_benefit']
                    preview_df = app.scenarios[preview_cols].copy()
                    
                    st.dataframe(preview_df, use_container_width=True)
                else:
                    st.error(message)
            except Exception as e:
                st.error(f"Error importing file: {str(e)}")
        
        # Example templates
        with st.expander("Download Import Templates"):
            st.markdown("Use these templates to prepare your import files:")
            
            # Create template dataframes
            template_df = pd.DataFrame({
                'scenario_name': ['Example Scenario'],
                'sku': ['SKU123'],
                'sales_30': [400],
                'avg_sale_price': [50],
                'sales_channel': ['Amazon'],
                'returns_30': [40],
                'solution': ['Better packaging'],
                'solution_cost': [2000],
                'additional_cost_per_item': [2],
                'current_unit_cost': [18],
                'reduction_rate': [25]
            })
            
            # CSV template
            csv_template = template_df.to_csv(index=False).encode()
            st.download_button(
                "📥 CSV Template",
                data=csv_template,
                file_name="kaizenroi_template.csv",
                mime="text/csv"
            )
            
            # Excel template
            excel_template = io.BytesIO()
            with pd.ExcelWriter(excel_template, engine='xlsxwriter') as writer:
                template_df.to_excel(writer, index=False, sheet_name='Scenarios')
            
            st.download_button(
                "📊 Excel Template",
                data=excel_template.getvalue(),
                file_name="kaizenroi_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # JSON template
            json_template = template_df.to_json(orient='records')
            st.download_button(
                "📋 JSON Template",
                data=json_template,
                file_name="kaizenroi_template.json",
                mime="application/json"
            )

elif selected == "Settings":
    st.title("⚙️ Settings")
    st.markdown("Configure application settings and preferences")
    
    # App settings
    st.subheader("Application Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        currency_symbol = st.text_input("Currency Symbol", app.settings["currency_symbol"])
        
        color_theme = st.selectbox(
            "Color Theme",
            ["viridis", "plasma", "inferno", "magma", "cividis", "turbo"],
            index=["viridis", "plasma", "inferno", "magma", "cividis", "turbo"].index(app.settings["color_theme"])
        )
    
    with col2:
        time_frame = st.number_input("Default Time Frame (days)", min_value=1, value=app.settings["time_frame"])
        
        # Add dummy field for layout balance
        st.text_input("Company Name (optional)", "")
    
    # Save settings button
    if st.button("Save Settings"):
        app.settings["currency_symbol"] = currency_symbol
        app.settings["color_theme"] = color_theme
        app.settings["time_frame"] = time_frame
        
        st.success("Settings saved successfully!")
    
    # Data management
    st.subheader("Data Management")
    
    data_action = st.radio(
        "Select action",
        ["Backup all data", "Clear all data"],
        horizontal=True
    )
    
    if data_action == "Backup all data":
        if app.scenarios.empty:
            st.warning("No data to backup. Add scenarios first.")
        else:
            # Create backup in multiple formats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_data = app.export_scenarios_csv().encode()
                st.download_button(
                    "📥 Backup as CSV",
                    data=csv_data,
                    file_name=f"kaizenroi_backup_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                excel_data = app.export_scenarios_excel()
                st.download_button(
                    "📊 Backup as Excel",
                    data=excel_data,
                    file_name=f"kaizenroi_backup_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col3:
                json_data = app.export_scenarios_json()
                st.download_button(
                    "📋 Backup as JSON",
                    data=json_data,
                    file_name=f"kaizenroi_backup_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
    
    elif data_action == "Clear all data":
        st.warning("⚠️ This will delete all scenarios. This action cannot be undone.")
        
        if st.button("Clear All Data"):
            # Clear the dataframe
            app.scenarios = pd.DataFrame(columns=app.scenarios.columns)
            st.success("All data has been cleared.")
    
    # Advanced settings
    with st.expander("Advanced Settings"):
        st.markdown("These settings are for advanced users only.")
        
        # Add advanced options here
        decimal_places = st.slider("Decimal places for calculations", 1, 5, 2)
        
        # Example of a more complex setting
        calculation_option = st.selectbox(
            "ROI Calculation Method",
            ["Standard (Net Benefit / Cost)", "Alternative (Gross Benefit / Cost)"]
        )
        
        if st.button("Save Advanced Settings"):
            st.success("Advanced settings saved!")

elif selected == "Help":
    st.title("❓ Help & Documentation")
    st.markdown("Learn how to use KaizenROI to optimize your return investments")
    
    # Create tabs for different help sections
    tab1, tab2, tab3, tab4 = st.tabs(["Getting Started", "Formulas & Calculations", "FAQ", "About"])
    
    with tab1:
        st.markdown("### Getting Started with KaizenROI")
        st.markdown("""
        Welcome to KaizenROI, a powerful tool for evaluating return reduction investments with precision.
        
        #### Quick Start Guide:
        
        1. **Add a Scenario** - Go to the "Add Scenario" tab and enter your data:
           - Basic product information (SKU, sales data)
           - Return metrics (current return rate)
           - Solution details (cost, expected reduction)
           
        2. **View Analysis** - Navigate to the "Dashboard" to see an overview of your scenarios.
        
        3. **Compare Solutions** - Use the "Compare" tab to evaluate multiple scenarios side-by-side.
        
        4. **Export Results** - Share your analysis via the "Export/Import" tab.
        
        #### Sample Data
        
        Not sure where to start? Click the "Load Sample Data" button in the sidebar to see example scenarios.
        """)
        
        # Add video tutorial placeholder
        st.image("https://via.placeholder.com/640x360.png?text=Video+Tutorial+(Coming+Soon)", use_column_width=True)
        
        # Add links to additional resources
        st.markdown("#### Additional Resources")
        st.markdown("""
        - [KaizenROI Documentation](https://example.com)
        - [Return Optimization Best Practices](https://example.com)
        - [Contact Support](mailto:support@kaizenroi.com)
        """)
    
    with tab2:
        st.markdown("### Formulas & Calculations")
        st.markdown("""
        KaizenROI uses the following formulas to calculate return on investment and related metrics:
        
        #### Basic Metrics
        
        - **Return Rate** = Returns ÷ Sales
        - **Avoided Returns** = Returns × Reduction %
        - **New Unit Cost** = Current Unit Cost + Additional Cost per Item
        
        #### Financial Metrics
        
        - **Savings from Avoided Returns** = Avoided Returns × (Sale Price - New Unit Cost)
        - **Annual Additional Costs** = Additional Cost per Item × Annual Sales
        - **Net Benefit** = Annual Savings - Annual Additional Costs
        
        #### ROI Metrics
        
        - **ROI** = Net Benefit ÷ Solution Cost
        - **Break-even (days)** = Solution Cost ÷ (Monthly Net Benefit ÷ 30)
        - **Break-even (months)** = Solution Cost ÷ Monthly Net Benefit
        
        #### Margin Metrics
        
        - **Current Margin** = Sale Price - Current Unit Cost
        - **New Margin** = Sale Price - New Unit Cost
        - **Amortized Solution Cost** = Solution Cost ÷ (Monthly Sales × 12)
        - **Amortized Margin** = New Margin - Amortized Solution Cost
        """)
        
        # Create example calculation
        st.markdown("### Example Calculation")
        
        example_data = {
            "Sales (30 days)": 400,
            "Returns (30 days)": 40,
            "Sale Price": "$50.00",
            "Current Unit Cost": "$18.00",
            "Solution Cost": "$2,000.00",
            "Additional Cost per Item": "$2.00",
            "Expected Reduction": "25%"
        }
        
        example_results = {
            "Return Rate": "10.0%",
            "Avoided Returns (annual)": "120 units",
            "Annual Savings": "$3,600.00",
            "Annual Additional Costs": "$9,600.00",
            "Net Benefit": "-$6,000.00",
            "ROI": "-3.0x",
            "Break-even": "N/A"
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Input Values")
            for key, value in example_data.items():
                st.markdown(f"**{key}:** {value}")
        
        with col2:
            st.markdown("#### Results")
            for key, value in example_results.items():
                st.markdown(f"**{key}:** {value}")
        
        # Add interactive calculator
        with st.expander("Interactive Calculator"):
            st.markdown("Try out different values to see how they affect the ROI:")
            
            calc_col1, calc_col2 = st.columns(2)
            
            with calc_col1:
                calc_sales = st.number_input("Monthly Sales", min_value=0, value=400)
                calc_returns = st.number_input("Monthly Returns", min_value=0, max_value=calc_sales, value=40)
                calc_price = st.number_input("Sale Price", min_value=0.0, value=50.0)
            
            with calc_col2:
                calc_cost = st.number_input("Current Unit Cost", min_value=0.0, value=18.0)
                calc_solution = st.number_input("Solution Cost", min_value=0.0, value=2000.0)
                calc_additional = st.number_input("Additional Cost per Item", min_value=0.0, value=2.0)
            
            calc_reduction = st.slider("Expected Reduction (%)", 0, 100, 25)
            
            if st.button("Calculate"):
                # Calculate metrics
                return_rate = safe_divide(calc_returns, calc_sales) * 100
                avoided_returns = calc_returns * (calc_reduction / 100)
                avoided_returns_annual = avoided_returns * 12
                
                new_unit_cost = calc_cost + calc_additional
                savings_30 = avoided_returns * (calc_price - new_unit_cost)
                annual_savings = savings_30 * 12
                
                annual_additional_costs = calc_additional * calc_sales * 12
                net_benefit = annual_savings - annual_additional_costs
                
                roi = safe_divide(net_benefit, calc_solution)
                monthly_net_benefit = net_benefit / 12
                break_even_days = safe_divide(calc_solution, (monthly_net_benefit / 30))
                
                # Display results
                st.markdown("### Calculator Results")
                
                result_col1, result_col2, result_col3 = st.columns(3)
                
                with result_col1:
                    st.metric("Return Rate", f"{return_rate:.2f}%")
                    st.metric("Annual Avoided Returns", f"{avoided_returns_annual:.0f} units")
                
                with result_col2:
                    st.metric("Annual Savings", f"${annual_savings:,.2f}")
                    st.metric("Annual Additional Costs", f"${annual_additional_costs:,.2f}")
                
                with result_col3:
                    st.metric("ROI", f"{roi:.2f}x" if roi is not None else "N/A")
                    st.metric("Break-even", f"{break_even_days:.0f} days" if break_even_days is not None and break_even_days > 0 else "N/A")
    
    with tab3:
        st.markdown("### Frequently Asked Questions")
        
        # Define FAQ items
        faqs = [
            {
                "question": "What is KaizenROI?",
                "answer": "KaizenROI is a decision-support tool designed to help businesses evaluate return reduction initiatives based on financial metrics like ROI, break-even time, and margin impact."
            },
            {
                "question": "How accurate are the calculations?",
                "answer": "The calculations are based on the data you provide and standard financial formulas. The accuracy depends on the quality of your input data and the accuracy of your estimated return reduction rate."
            },
            {
                "question": "Can I save my work?",
                "answer": "Yes, you can export your scenarios in CSV, Excel, or JSON format from the Export/Import tab. You can also import them later to continue your analysis."
            },
            {
                "question": "How do I determine the expected reduction rate?",
                "answer": "The expected reduction rate is your estimate of how much your solution will reduce returns. This can be based on historical data, industry benchmarks, or pilot tests. You can create multiple scenarios with different reduction rates to see how sensitive your ROI is to this estimate."
            },
            {
                "question": "What is the difference between margin and amortized margin?",
                "answer": "Regular margin is simply sale price minus unit cost. Amortized margin includes the one-time solution cost spread across all units sold during a 12-month period, giving you a more complete picture of profitability."
            },
            {
