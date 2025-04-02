import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

# =============================================================================
# Utility Functions
# =============================================================================

def display_tooltip(text, tooltip):
    # For simplicity, we just concatenate the tooltip text.
    return f"{text} (hover for info: {tooltip})"

def get_device_risk_color(device_class):
    if device_class == "Class I":
        return "#00796b"  # Green
    elif device_class == "Class II":
        return "#ff8f00"  # Amber
    elif device_class == "Class III":
        return "#c62828"  # Red
    return "#000000"  # Default Black

def get_color_scale(value, min_val, max_val, reverse=False):
    # A simple dummy function to return a hex color based on the value.
    # Replace with your actual color-scaling logic if needed.
    return "#000000"

def format_percent(value):
    return f"{value:.2f}%"

def format_currency(value):
    return f"${value:,.2f}"

# =============================================================================
# Dummy Optimizer Class (Placeholder for ROI calculations)
# =============================================================================

class ReturnOptimizer:
    def __init__(self):
        self.scenarios = pd.DataFrame(columns=[
            "uid", "scenario_name", "roi", "break_even_days", "net_benefit",
            "solution", "solution_cost", "regulatory_cost", "reduction_rate",
            "additional_cost_per_item", "margin_before", "avg_sale_price",
            "margin_after", "timestamp", "sku", "sales_30", "sales_channel",
            "returns_30", "device_class", "regulatory_impact", "adverse_events",
            "sales_365", "returns_365", "tag"
        ])
        self.uid_counter = 1
    
    def add_scenario(self, scenario_name, sku, sales_30, avg_sale_price, sales_channel, returns_30, solution, solution_cost,
                     additional_cost_per_item, current_unit_cost, reduction_rate, sales_365, returns_365, tag, device_class,
                     regulatory_impact, adverse_events, regulatory_cost):
        # Dummy ROI calculations (replace with your own logic)
        roi = 100  # Example ROI value
        break_even_days = 90
        net_benefit = 10000
        margin_before = avg_sale_price - current_unit_cost
        margin_after = margin_before + additional_cost_per_item
        scenario = {
            "uid": self.uid_counter,
            "scenario_name": scenario_name,
            "roi": roi,
            "break_even_days": break_even_days,
            "net_benefit": net_benefit,
            "solution": solution,
            "solution_cost": solution_cost,
            "regulatory_cost": regulatory_cost,
            "reduction_rate": reduction_rate,
            "additional_cost_per_item": additional_cost_per_item,
            "margin_before": margin_before,
            "avg_sale_price": avg_sale_price,
            "margin_after": margin_after,
            "timestamp": datetime.now(),
            "sku": sku,
            "sales_30": sales_30,
            "sales_channel": sales_channel,
            "returns_30": returns_30,
            "device_class": device_class,
            "regulatory_impact": regulatory_impact,
            "adverse_events": adverse_events,
            "sales_365": sales_365,
            "returns_365": returns_365,
            "tag": tag
        }
        self.scenarios = pd.concat([self.scenarios, pd.DataFrame([scenario])], ignore_index=True)
        self.uid_counter += 1
        return True, "Scenario added successfully"
    
    def get_scenario(self, uid):
        df = self.scenarios[self.scenarios["uid"] == uid]
        if not df.empty:
            return df.iloc[0].to_dict()
        return None

# =============================================================================
# Navigation and Page Display Functions
# =============================================================================

def navigate_to(page):
    st.session_state.page = page
    st.experimental_rerun()

def display_main_navigation():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "ROI", "Risk", "FMEA", "Reports", "Help", "Wizard"])
    st.session_state.page = page

def display_dashboard():
    st.title("Dashboard")
    st.write("Dashboard content goes here.")

def display_view_scenario():
    st.title("View Scenario")
    st.write("Scenario details...")

def display_roi_analysis():
    st.title("ROI Analysis")
    st.write("ROI analysis content goes here.")

def display_risk_management():
    st.title("Risk Management")
    st.write("Risk management content goes here.")

def display_fmea():
    st.title("FMEA")
    st.write("FMEA content goes here.")

def display_reports():
    st.title("Reports")
    st.write("Reports content goes here.")

def display_help():
    st.title("Help & Documentation")
    st.write("Help content goes here.")

def display_progress_tracker():
    step = st.session_state.get("workflow_step", 1)
    st.write(f"Progress: Step {step}")

# =============================================================================
# Wizard Functions
# =============================================================================

def display_wizard():
    st.title("Guided Workflow")
    display_progress_tracker()
    if st.session_state.workflow_step == 1:
        display_wizard_step1()
    elif st.session_state.workflow_step == 2:
        display_wizard_step2()
    elif st.session_state.workflow_step == 3:
        display_wizard_step3()
    elif st.session_state.workflow_step == 4:
        display_wizard_step4()

def display_wizard_step1():
    st.header("Step 1: Device Classification")
    tab1, tab2 = st.tabs(["Questionnaire Classification", "Manual Classification"])
    with tab1:
        if "classification_questions" not in st.session_state:
            st.session_state.classification_questions = {
                "step1": {
                    "question": "What is the device's primary intended use?",
                    "type": "radio",
                    "options": [
                        "Diagnostic or monitoring only (no therapeutic function)",
                        "Therapeutic or treatment",
                        "Life-supporting or life-sustaining",
                        "Implantable",
                        "Combination product (contains drug/biologic)"
                    ],
                    "next_step": {
                        "Diagnostic or monitoring only (no therapeutic function)": "step2_diagnostic",
                        "Therapeutic or treatment": "step2_therapeutic",
                        "Life-supporting or life-sustaining": "step_lifesupport",
                        "Implantable": "step_implantable",
                        "Combination product (contains drug/biologic)": "step_combination"
                    },
                    "info": "The primary intended use determines the initial risk category and regulatory pathway."
                }
            }
            st.session_state.classification_results = None
            st.session_state.current_classification_step = "step1"
            st.session_state.classification_answers = {}
        if "device_name" not in st.session_state:
            st.session_state.device_name = ""
        device_name = st.text_input("Device Name", value=st.session_state.device_name, key="wizard_device_name")
        st.session_state.device_name = device_name
        st.info("Please complete the classification questionnaire to continue the workflow.")
        if st.button("Open Complete Classification Tool"):
            navigate_to("Risk")
    with tab2:
        st.subheader("Manual Classification")
        col1, col2 = st.columns(2)
        with col1:
            device_class = st.selectbox("Device Classification", ["Class I", "Class II", "Class III"], key="wizard_manual_class")
            regulatory_path = st.selectbox("Regulatory Pathway", ["510(k) Exempt", "510(k)", "De Novo", "PMA", "Other"], key="wizard_reg_path")
        with col2:
            device_name_manual = st.text_input("Device Name", key="wizard_manual_device_name")
            device_description = st.text_area("Brief Description", key="wizard_device_desc")
        if st.button("Save Classification and Continue"):
            if not device_name_manual:
                st.error("Device Name is required")
            else:
                color = get_device_risk_color(device_class)
                st.session_state.device_classification = {
                    "name": device_name_manual,
                    "class": device_class,
                    "color": color,
                    "explanation": f"Manual classification as {device_class} device.",
                    "submission_path": regulatory_path
                }
                st.success(f"Saved classification for {device_name_manual} as {device_class}")
                st.session_state.workflow_step = 2
                st.experimental_rerun()

def display_wizard_step2():
    st.header("Step 2: Risk Assessment")
    if "device_classification" not in st.session_state:
        st.warning("No device classification found. Please complete Step 1 first.")
        if st.button("Go Back to Step 1"):
            st.session_state.workflow_step = 1
            st.experimental_rerun()
        return
    device = st.session_state.device_classification
    st.markdown(f"""
    **Device Classification Summary**  
    **Device:** {device['name']}  
    **Classification:** <span style="color: {device['color']};">{device['class']}</span>  
    **Regulatory Pathway:** {device['submission_path']}  
    """, unsafe_allow_html=True)
    st.markdown("Now, let's conduct a risk assessment for your device.")
    with st.form("wizard_risk_form"):
        st.subheader("Risk Assessment")
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name", value=device['name'])
            product_id = st.text_input("Product/SKU ID")
            assessment_date = st.date_input("Assessment Date", datetime.now())
            device_class = st.selectbox("Device Classification", ["Class I", "Class II", "Class III"],
                                        index=["Class I", "Class II", "Class III"].index(device['class']))
        with col2:
            st.write(display_tooltip("Risk Scores (0-10)", "Higher scores indicate higher risk. Follow ISO 14971 guidelines."))
            safety_score = st.slider("Patient Safety Risk", 0, 10, 5, key="wizard_safety")
            compliance_score = st.slider("Regulatory Compliance Risk", 0, 10, 5, key="wizard_compliance")
            logistics_score = st.slider("Supply Chain/Logistics Risk", 0, 10, 5, key="wizard_logistics")
            financial_score = st.slider("Financial/Business Risk", 0, 10, 5, key="wizard_financial")
        notes = st.text_area("Risk Notes & Mitigations", key="wizard_risk_notes")
        submitted = st.form_submit_button("Save Risk Assessment and Continue")
        if submitted:
            if not product_name:
                st.error("Product name is required")
            else:
                weighted_risk = (safety_score * 0.4 + compliance_score * 0.3 +
                                 logistics_score * 0.15 + financial_score * 0.15)
                if weighted_risk > 7:
                    risk_level = "High Risk"
                    risk_color = "#c62828"  # Red
                elif weighted_risk > 4:
                    risk_level = "Moderate Risk"
                    risk_color = "#ff8f00"  # Amber
                else:
                    risk_level = "Low Risk"
                    risk_color = "#00796b"  # Green
                new_row = {
                    'product_name': product_name,
                    'product_id': product_id,
                    'safety_score': safety_score,
                    'compliance_score': compliance_score,
                    'logistics_score': logistics_score,
                    'financial_score': financial_score,
                    'weighted_risk': weighted_risk,
                    'risk_level': risk_level,
                    'risk_color': risk_color,
                    'timestamp': assessment_date,
                    'notes': notes,
                    'device_class': device_class
                }
                if "risk_matrix_data" not in st.session_state:
                    st.session_state.risk_matrix_data = pd.DataFrame(columns=[
                        'product_name', 'product_id', 'safety_score', 'compliance_score', 
                        'logistics_score', 'financial_score', 'weighted_risk', 'risk_level', 
                        'risk_color', 'timestamp', 'notes', 'device_class'
                    ])
                st.session_state.risk_matrix_data = pd.concat([st.session_state.risk_matrix_data,
                                                               pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.current_risk_assessment = new_row
                st.success(f"Risk assessment saved for {product_name}")
                st.session_state.workflow_step = 3
                st.experimental_rerun()

def display_wizard_step3():
    st.header("Step 3: ROI Analysis")
    if "device_classification" not in st.session_state:
        st.warning("No device classification found. Please complete Step 1 first.")
        if st.button("Go Back to Step 1"):
            st.session_state.workflow_step = 1
            st.experimental_rerun()
        return
    if "current_risk_assessment" not in st.session_state:
        st.warning("No risk assessment found. Please complete Step 2 first.")
        if st.button("Go Back to Step 2"):
            st.session_state.workflow_step = 2
            st.experimental_rerun()
        return
    col1, col2 = st.columns(2)
    device = st.session_state.device_classification
    risk = st.session_state.current_risk_assessment
    with col1:
        st.markdown(f"**Device Classification**: {device['name']} - <span style='color: {device['color']};'>{device['class']}</span>", unsafe_allow_html=True)
        st.markdown(f"**Regulatory Pathway:** {device['submission_path']}")
    with col2:
        st.markdown(f"**Risk Level:** <span style='color: {risk['risk_color']};'>{risk['risk_level']}</span>", unsafe_allow_html=True)
        st.markdown(f"**Safety:** {risk['safety_score']}/10, **Compliance:** {risk['compliance_score']}/10")
    st.markdown("Now, let's analyze the ROI for potential improvements.")
    with st.form("wizard_roi_form"):
        st.subheader("ROI Analysis")
        col1, col2 = st.columns(2)
        with col1:
            scenario_name = st.text_input("Scenario Name", value=f"{risk['product_name']} Improvement")
            sku = st.text_input("Product SKU", value=risk.get('product_id', ""))
            sales_channel = st.selectbox("Sales Channel", options=["Hospital", "Direct to Provider", "Distributor", "Retail", "Online", "Other"])
            device_class = st.selectbox("Device Classification", ["Class I", "Class II", "Class III"],
                                        index=["Class I", "Class II", "Class III"].index(risk['device_class']),
                                        disabled=True)
            regulatory_impact = st.selectbox("Regulatory Impact", options=["No impact", "Letter to File", "Special 510(k)", "New submission"])
        with col2:
            sales_30 = st.number_input("Monthly Sales Volume (units)", min_value=0, value=100)
            avg_sale_price = st.number_input("Average Sales Price ($)", min_value=0.0, value=100.0, step=0.01, format="%.2f")
            returns_30 = st.number_input("Monthly Returns (units)", min_value=0, max_value=int(sales_30), value=min(10, int(sales_30)))
            current_unit_cost = st.number_input("Current Unit Cost ($)", min_value=0.0, max_value=avg_sale_price, value=min(50.0, avg_sale_price/2), step=0.01, format="%.2f")
            if sales_30 > 0:
                return_rate = (returns_30 / sales_30) * 100
            else:
                return_rate = 0
            st.markdown(f"**Return Rate:** {return_rate:.2f}%")
        st.markdown("### Proposed Solution")
        default_solution = ""
        if risk['risk_level'] == "High Risk":
            if risk['safety_score'] >= 8:
                default_solution = "Implement design improvements to address high safety risks and reduce potential hazards."
            elif risk['compliance_score'] >= 8:
                default_solution = "Update documentation and conduct additional testing to address compliance concerns."
        elif risk['risk_level'] == "Moderate Risk":
            default_solution = "Improve quality control process and update user instructions to address moderate risk factors."
        solution = st.text_area("Solution Description", value=default_solution)
        col1, col2, col3 = st.columns(3)
        with col1:
            solution_cost = st.number_input("Implementation Cost ($)", min_value=0.0, value=5000.0, step=100.0, format="%.2f")
            additional_cost_per_item = st.number_input("Additional Cost Per Unit ($)", value=0.0, step=0.01, format="%.2f")
        with col2:
            reduction_rate = st.slider("Expected Return Rate Reduction (%)", min_value=0, max_value=100, value=30)
            regulatory_cost = st.number_input("Regulatory Submission Cost ($)", min_value=0.0, value=0.0, step=100.0, format="%.2f")
        with col3:
            sales_365 = st.number_input("Annual Sales Volume (optional)", min_value=0, value=0)
            returns_365 = st.number_input("Annual Returns (optional)", min_value=0, value=0)
            adverse_events = st.number_input("Annual Adverse Events", min_value=0, value=0)
        tag = st.selectbox("Category Tag", options=["Packaging", "Instructions for Use", "Design Improvement", "Manufacturing Process", "Quality Control", "Software Update", "Materials Change", "Other"])
        submitted = st.form_submit_button("Calculate ROI and Continue")
        if submitted:
            if "optimizer" not in st.session_state or st.session_state.optimizer is None:
                st.session_state.optimizer = ReturnOptimizer()
            if not scenario_name:
                st.error("Scenario Name is required")
            elif not sku:
                st.error("Product SKU is required")
            elif sales_30 <= 0:
                st.error("Monthly Sales must be greater than zero")
            elif avg_sale_price <= 0:
                st.error("Average Sales Price must be greater than zero")
            elif returns_30 > sales_30:
                st.error("Monthly Returns cannot exceed Monthly Sales")
            elif current_unit_cost >= avg_sale_price:
                st.warning("Current Unit Cost is greater than or equal to Average Sales Price. This may result in negative margins.")
                proceed = st.checkbox("Proceed with negative margin")
                if not proceed:
                    st.stop()
            success, message = st.session_state.optimizer.add_scenario(
                scenario_name, sku, sales_30, avg_sale_price, sales_channel, returns_30,
                solution, solution_cost, additional_cost_per_item, current_unit_cost,
                reduction_rate, sales_365, returns_365, tag, device_class, regulatory_impact,
                adverse_events, regulatory_cost
            )
            if success:
                st.success(message)
                new_uid = st.session_state.optimizer.scenarios.sort_values('timestamp', ascending=False).iloc[0]['uid']
                st.session_state.wizard_scenario_uid = new_uid
                st.session_state.workflow_step = 4
                st.experimental_rerun()
            else:
                st.error(message)

def display_wizard_step4():
    st.header("Step 4: Final Report & Summary")
    if "device_classification" not in st.session_state:
        st.warning("No device classification found. Please complete Step 1 first.")
        if st.button("Go Back to Step 1"):
            st.session_state.workflow_step = 1
            st.experimental_rerun()
        return
    if "current_risk_assessment" not in st.session_state:
        st.warning("No risk assessment found. Please complete Step 2 first.")
        if st.button("Go Back to Step 2"):
            st.session_state.workflow_step = 2
            st.experimental_rerun()
        return
    if "wizard_scenario_uid" not in st.session_state:
        st.warning("No ROI scenario found. Please complete Step 3 first.")
        if st.button("Go Back to Step 3"):
            st.session_state.workflow_step = 3
            st.experimental_rerun()
        return
    device = st.session_state.device_classification
    risk = st.session_state.current_risk_assessment
    scenario = st.session_state.optimizer.get_scenario(st.session_state.wizard_scenario_uid)
    if not scenario:
        st.error("Error retrieving ROI scenario data.")
        if st.button("Go Back to Step 3"):
            st.session_state.workflow_step = 3
            st.experimental_rerun()
        return
    st.subheader("Workflow Summary")
    st.markdown(f"""
    **1. Device Classification**  
    **Device Name:** {device['name']}  
    **Classification:** <span style="color: {device['color']};">{device['class']}</span>  
    **Regulatory Pathway:** {device['submission_path']}  
    """, unsafe_allow_html=True)
    st.markdown(f"""
    **2. Risk Assessment**  
    **Product Name:** {risk['product_name']}  
    **Risk Level:** <span style="color: {risk['risk_color']};">{risk['risk_level']} ({risk['weighted_risk']:.1f})</span>  
    **Safety Score:** {risk['safety_score']}/10  
    **Compliance Score:** {risk['compliance_score']}/10  
    **Logistics Score:** {risk['logistics_score']}/10  
    **Financial Score:** {risk['financial_score']}/10  
    """, unsafe_allow_html=True)
    roi_color = get_color_scale(scenario['roi'], 0, 200)
    days_color = get_color_scale(scenario['break_even_days'], 0, 365, reverse=True)
    st.markdown(f"""
    **3. ROI Analysis: {scenario['scenario_name']}**  
    **Proposed Solution:** *{scenario['solution']}*  
    **ROI:** <span style="color: {roi_color};">{format_percent(scenario['roi'])}</span>  
    **Breakeven Days:** <span style="color: {days_color};">{int(scenario['break_even_days']) if not pd.isna(scenario['break_even_days']) else 'N/A'} days</span>  
    **Net Benefit:** {format_currency(scenario['net_benefit'])}  
    **Implementation Cost:** {format_currency(scenario['solution_cost'])}  
    **Regulatory Cost:** {format_currency(scenario['regulatory_cost'])}  
    **Return Reduction:** {format_percent(scenario['reduction_rate'])}  
    **Additional Unit Cost:** {format_currency(scenario['additional_cost_per_item'])}  
    **Margin Before:** {format_currency(scenario['margin_before'])} ({format_percent((scenario['margin_before']/scenario['avg_sale_price'])*100)})  
    **Margin After:** {format_currency(scenario['margin_after'])} ({format_percent((scenario['margin_after']/scenario['avg_sale_price'])*100)})  
    """, unsafe_allow_html=True)
    recommendations = []
    if not pd.isna(scenario['roi']) and scenario['roi'] > 100:
        recommendations.append("⭐ The proposed solution shows a strong ROI (>100%) and should be considered for implementation.")
    elif not pd.isna(scenario['roi']) and scenario['roi'] > 50:
        recommendations.append("✅ The solution shows a positive ROI and may be worthwhile to implement.")
    elif not pd.isna(scenario['roi']) and scenario['roi'] > 0:
        recommendations.append("ℹ The solution shows a moderate ROI. Consider optimizing costs or exploring alternative solutions.")
    else:
        recommendations.append("⚠ The solution does not show a positive ROI. Re-evaluate costs and benefits before proceeding.")
    if not pd.isna(scenario['break_even_days']):
        if scenario['break_even_days'] < 90:
            recommendations.append("⭐ The solution has a very quick breakeven time (<90 days), indicating low financial risk.")
        elif scenario['break_even_days'] < 180:
            recommendations.append("✅ The solution has a reasonable breakeven time (<6 months).")
        elif scenario['break_even_days'] < 365:
            recommendations.append("ℹ The solution takes several months to break even. Monitor implementation costs carefully.")
        else:
            recommendations.append("⚠ The solution has a long breakeven period (>1 year). Consider shorter-term alternatives.")
    if risk['risk_level'] == "High Risk" and (pd.isna(scenario['roi']) or scenario['roi'] < 50):
        recommendations.append("🚨 Device has high risk but the solution shows limited financial return. Regulatory/safety concerns may still justify implementation.")
    elif risk['risk_level'] == "High Risk" and not pd.isna(scenario['roi']) and scenario['roi'] > 50:
        recommendations.append("⭐ Device has high risk and the solution shows good financial return. Strongly recommended for implementation.")
    elif risk['risk_level'] == "Moderate Risk" and not pd.isna(scenario['roi']) and scenario['roi'] > 50:
        recommendations.append("✅ Device has moderate risk and the solution shows good financial return. Recommended for implementation.")
    st.subheader("Recommendations")
    for rec in recommendations:
        st.markdown(rec)
    st.subheader("Export Complete Analysis")
    export_format = st.radio("Export Format", ["Excel", "PDF Report", "CSV"])
    if export_format == "Excel":
        if st.button("Generate Excel Report"):
            buffer = io.BytesIO()
            try:
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    summary_data = {
                        'Category': ['Device Name', 'Device Class', 'Regulatory Pathway', 'Risk Level', 'Risk Score', 'Safety Score', 'Compliance Score', 'Solution', 'Implementation Cost', 'ROI', 'Breakeven Days', 'Net Benefit'],
                        'Value': [device['name'], device['class'], device['submission_path'], risk['risk_level'],
                                  f"{risk['weighted_risk']:.1f}", f"{risk['safety_score']}/10", f"{risk['compliance_score']}/10",
                                  scenario['solution'], format_currency(scenario['solution_cost']),
                                  format_percent(scenario['roi']),
                                  str(int(scenario['break_even_days']) if not pd.isna(scenario['break_even_days']) else 'N/A'),
                                  format_currency(scenario['net_benefit'])]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name="Executive_Summary", index=False)
                    workbook = writer.book
                    worksheet = writer.sheets["Executive_Summary"]
                    header_format = workbook.add_format({'bold': True, 'bg_color': '#0055a5', 'font_color': 'white', 'border': 1})
                    for col_num, value in enumerate(summary_df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column('A:A', 20)
                    worksheet.set_column('B:B', 40)
                    scenario_df = pd.DataFrame([scenario])
                    scenario_df.to_excel(writer, sheet_name="ROI_Analysis", index=False)
                    risk_df = pd.DataFrame([risk])
                    risk_df.to_excel(writer, sheet_name="Risk_Assessment", index=False)
                    rec_data = {'Recommendation': recommendations}
                    rec_df = pd.DataFrame(rec_data)
                    rec_df.to_excel(writer, sheet_name="Recommendations", index=False)
                st.download_button(label="Download Complete Analysis", data=buffer.getvalue(),
                                   file_name=f"{device['name']}_Complete_Analysis.xlsx", mime="application/vnd.ms-excel")
            except Exception as e:
                st.error(f"Error generating Excel report: {str(e)}")
    elif export_format == "PDF Report":
        st.info("PDF export functionality requires additional setup. Please use Excel export for a complete report.")
    elif export_format == "CSV":
        if st.button("Generate CSV Report"):
            scenario_df = pd.DataFrame([scenario])
            csv = scenario_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download ROI Analysis (CSV)", data=csv,
                               file_name=f"{device['name']}_ROI_Analysis.csv", mime="text/csv")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Return to Dashboard"):
            st.session_state.current_wizard_mode = False
            navigate_to("Dashboard")
    with col2:
        if st.button("Start New Analysis"):
            st.session_state.workflow_step = 1
            if "current_risk_assessment" in st.session_state:
                del st.session_state.current_risk_assessment
            if "device_classification" in st.session_state:
                del st.session_state.device_classification
            if "wizard_scenario_uid" in st.session_state:
                del st.session_state.wizard_scenario_uid
            st.experimental_rerun()
    with col3:
        if st.button("View ROI Details"):
            st.session_state.view_scenario = True
            st.session_state.selected_scenario = st.session_state.wizard_scenario_uid
            navigate_to("ROI")

# =============================================================================
# Main App Function
# =============================================================================

def main():
    if "optimizer" not in st.session_state:
        st.session_state.optimizer = None
    if "workflow_step" not in st.session_state:
        st.session_state.workflow_step = 1
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"
    display_main_navigation()
    if st.session_state.page == "Dashboard":
        display_dashboard()
    elif st.session_state.page == "ROI":
        if st.session_state.get("view_scenario", False):
            display_view_scenario()
        else:
            display_roi_analysis()
    elif st.session_state.page == "Risk":
        display_risk_management()
    elif st.session_state.page == "FMEA":
        display_fmea()
    elif st.session_state.page == "Reports":
        display_reports()
    elif st.session_state.page == "Help":
        display_help()
    elif st.session_state.page == "Wizard":
        display_wizard()

if __name__ == "__main__":
    main()
