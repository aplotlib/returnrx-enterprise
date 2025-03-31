theta=categories_display,
                fill='toself',
                name=row['product_category']
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            height=500,
            title="Category Comparison by Key Metrics"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # Product lifecycle stage analysis
    if 'product_lifecycle_stage' in filtered_df.columns and len(filtered_df['product_lifecycle_stage'].unique()) > 1:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">🔄</span>
            <h3 class="section-title">Product Lifecycle Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Group by lifecycle stage
        lifecycle_data = filtered_df.groupby('product_lifecycle_stage').agg({
            'roi': 'mean',
            'net_benefit': 'sum',
            'development_cost': 'sum',
            'estimated_return_reduction': 'mean',
            'sales_increase': 'mean',
            'payback_period': 'mean'
        }).reset_index()
        
        # Ensure lifecycle stages are in correct order
        lifecycle_order = ["Introduction", "Growth", "Maturity", "Decline"]
        lifecycle_data['product_lifecycle_stage'] = pd.Categorical(
            lifecycle_data['product_lifecycle_stage'], 
            categories=lifecycle_order, 
            ordered=True
        )
        lifecycle_data = lifecycle_data.sort_values('product_lifecycle_stage')
        
        # Create comparison chart
        fig_lifecycle = go.Figure()
        
        # Add ROI bars
        fig_lifecycle.add_trace(go.Bar(
            x=lifecycle_data['product_lifecycle_stage'],
            y=lifecycle_data['roi'],
            name='ROI (%)',
            marker_color=COLOR_SCHEME['positive']
        ))
        
        # Add sales increase line
        fig_lifecycle.add_trace(go.Scatter(
            x=lifecycle_data['product_lifecycle_stage'],
            y=lifecycle_data['sales_increase'],
            name='Sales Increase (%)',
            mode='lines+markers',
            marker=dict(size=10),
            line=dict(width=3, color=COLOR_SCHEME['neutral']),
            yaxis='y2'
        ))
        
        # Configure axes
        fig_lifecycle.update_layout(
            yaxis=dict(
                title='ROI (%)',
                side='left',
                titlefont=dict(color=COLOR_SCHEME['positive']),
                tickfont=dict(color=COLOR_SCHEME['positive'])
            ),
            yaxis2=dict(
                title='Sales Increase (%)',
                side='right',
                overlaying='y',
                titlefont=dict(color=COLOR_SCHEME['neutral']),
                tickfont=dict(color=COLOR_SCHEME['neutral'])
            ),
            title="ROI and Sales Impact by Product Lifecycle Stage",
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig_lifecycle, use_container_width=True)
    
    # Development cost vs. net benefit analysis
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">💵</span>
        <h3 class="section-title">Investment vs. Return Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Scatter plot of development cost vs. net benefit
    fig_cost_benefit = px.scatter(
        filtered_df,
        x="development_cost",
        y="net_benefit",
        color="payback_period",
        size="bubble_size",
        color_continuous_scale="RdYlGn_r",  # Reversed scale - lower payback is better
        hover_name="scenario_name",
        text="product_name",
        labels={
            "development_cost": "Development Cost ($)",
            "net_benefit": "Annual Net Benefit ($)",
            "payback_period": "Payback Period (years)"
        },
        title="Development Cost vs. Annual Net Benefit"
    )
    
    # Add 1:1 reference line
    max_val = max(
        filtered_df['development_cost'].max(),
        filtered_df['net_benefit'].max()
    )
    
    fig_cost_benefit.add_shape(
        type="line",
        x0=0, y0=0,
        x1=max_val, y1=max_val,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    # Add annotation for 1:1 line
    fig_cost_benefit.add_annotation(
        x=max_val*0.7,
        y=max_val*0.7,
        text="1:1 Line (1-year payback)",
        showarrow=False,
        textangle=-45,
        font=dict(color="gray", size=10)
    )
    
    fig_cost_benefit.update_layout(height=600)
    st.plotly_chart(fig_cost_benefit, use_container_width=True)
    
    # Investment recommendations
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🎯</span>
        <h3 class="section-title">Investment Recommendations</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Find the best scenarios by different metrics
    best_roi = filtered_df.loc[filtered_df['roi'].idxmax()]
    best_npv = filtered_df.loc[filtered_df['npv'].fillna(-float('inf')).idxmax()]
    
    # Find quickest payback
    payback_df = filtered_df[filtered_df['payback_period'].notna()]
    quickest_payback = payback_df.loc[payback_df['payback_period'].idxmin()] if not payback_df.empty else None
    
    # Best sales impact
    best_sales = filtered_df.loc[filtered_df['sales_impact_annual'].idxmax()]
    
    # Best return reduction
    best_return = filtered_df.loc[(filtered_df['estimated_return_reduction'] * filtered_df['return_rate']).idxmax()]
    
    # Display recommendations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="product-card highlight-box">
            <div class="product-header">
                <strong>Best ROI Upgrade</strong>
            </div>
            <p><strong>{}</strong> - {}</p>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">{:.1f}%</div>
                    <div class="stat-label">ROI</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${:,.2f}</div>
                    <div class="stat-label">Dev. Cost</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${:,.2f}</div>
                    <div class="stat-label">Annual Net Benefit</div>
                </div>
            </div>
        </div>
        """.format(
            best_roi['scenario_name'],
            best_roi['upgrade_solution'],
            best_roi['roi'],
            best_roi['development_cost'],
            best_roi['net_benefit']
        ), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="product-card highlight-box">
            <div class="product-header">
                <strong>Best NPV Upgrade</strong>
            </div>
            <p><strong>{}</strong> - {}</p>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">${:,.2f}</div>
                    <div class="stat-label">NPV</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{:.1f}%</div>
                    <div class="stat-label">ROI</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{:.2f} years</div>
                    <div class="stat-label">Payback Period</div>
                </div>
            </div>
        </div>
        """.format(
            best_npv['scenario_name'],
            best_npv['upgrade_solution'],
            best_npv['npv'],
            best_npv['roi'],
            best_npv['payback_period'] if pd.notna(best_npv['payback_period']) else 'N/A'
        ), unsafe_allow_html=True)
    
    with col2:
        if quickest_payback is not None:
            st.markdown("""
            <div class="product-card highlight-box">
                <div class="product-header">
                    <strong>Quickest Payback Upgrade</strong>
                </div>
                <p><strong>{}</strong> - {}</p>
                <div class="product-stats">
                    <div class="stat-item">
                        <div class="stat-value">{:.2f} years</div>
                        <div class="stat-label">Payback Period</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{:.1f}%</div>
                        <div class="stat-label">ROI</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${:,.2f}</div>
                        <div class="stat-label">Development Cost</div>
                    </div>
                </div>
            </div>
            """.format(
                quickest_payback['scenario_name'],
                quickest_payback['upgrade_solution'],
                quickest_payback['payback_period'],
                quickest_payback['roi'],
                quickest_payback['development_cost']
            ), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="product-card highlight-box">
            <div class="product-header">
                <strong>Best Sale/Return Impact Upgrade</strong>
            </div>
            <p><strong>{}</strong> - {}</p>
            <div class="product-stats">
                <div class="stat-item">
                    <div class="stat-value">{:.1f}%</div>
                    <div class="stat-label">Sales Increase</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{:.1f}%</div>
                    <div class="stat-label">Return Reduction</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{:.1f}%</div>
                    <div class="stat-label">ROI</div>
                </div>
            </div>
        </div>
        """.format(
            best_sales['scenario_name'] if best_sales['sales_increase'] > best_return['estimated_return_reduction'] else best_return['scenario_name'],
            best_sales['upgrade_solution'] if best_sales['sales_increase'] > best_return['estimated_return_reduction'] else best_return['upgrade_solution'],
            best_sales['sales_increase'],
            best_return['estimated_return_reduction'],
            best_sales['roi'] if best_sales['sales_increase'] > best_return['estimated_return_reduction'] else best_return['roi']
        ), unsafe_allow_html=True)

def display_what_if_analysis():
    """Interactive what-if scenario analysis for product upgrades"""
    st.subheader("Product Upgrade What-If Analysis")
    
    # Get base scenario
    if not optimizer.scenarios.empty:
        # Let user select a base scenario
        scenario_names = optimizer.scenarios['scenario_name'].tolist()
        base_scenario_name = st.selectbox("Select base scenario for what-if analysis", scenario_names)
        
        # Get the selected scenario
        base_scenario = optimizer.scenarios[optimizer.scenarios['scenario_name'] == base_scenario_name].iloc[0]
        
        # Create a more tailored what-if analysis using tabs
        tabs = st.tabs(["Upgrade Parameters", "Financial Impacts", "Sales/Return Impacts", "Production Timeline"])
        
        # Store what-if parameters in session state to share between tabs
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
        
        # Tab 1: Upgrade Parameters
        with tabs[0]:
            st.markdown("### Adjust Upgrade Parameters")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Development cost change
                st.session_state.whatif_params['development_cost_change'] = st.slider(
                    "Development Cost Change (%)", 
                    min_value=-50, 
                    max_value=100, 
                    value=st.session_state.whatif_params['development_cost_change'],
                    help="Adjust the one-time cost required to implement the upgrade. For example, -20% means the upgrade costs 20% less than estimated."
                )
                
                # Unit cost change adjustment
                st.session_state.whatif_params['unit_cost_change_adjust'] = st.slider(
                    "Unit Cost Change Adjustment ($)", 
                    min_value=-max(2, abs(base_scenario['unit_cost_change']*2)), 
                    max_value=max(2, abs(base_scenario['unit_cost_change']*2)), 
                    value=st.session_state.whatif_params['unit_cost_change_adjust'],
                    step=0.05,
                    help="Adjust how much the upgrade affects the unit production cost. Positive means increased cost, negative means savings."
                )
                
                # Implementation time change
                st.session_state.whatif_params['implementation_time_change'] = st.slider(
                    "Implementation Time Change (months)", 
                    min_value=-max(3, base_scenario['time_to_implement']), 
                    max_value=12, 
                    value=st.session_state.whatif_params['implementation_time_change'],
                    help="Adjust how long it takes to implement the product upgrade. Negative means faster implementation."
                )
            
            with col2:
                # Return reduction adjustment
                st.session_state.whatif_params['return_reduction_adjust'] = st.slider(
                    "Return Reduction Adjustment (%)", 
                    min_value=-base_scenario['estimated_return_reduction'], 
                    max_value=min(50, 100 - base_scenario['estimated_return_reduction']), 
                    value=st.session_state.whatif_params['return_reduction_adjust'],
                    help="Adjust how effective the upgrade is at reducing returns. For example, +10% means the upgrade reduces returns by 10% more than originally estimated."
                )
                
                # Sales increase adjustment
                st.session_state.whatif_params['sales_increase_adjust'] = st.slider(
                    "Sales Increase Adjustment (%)", 
                    min_value=-base_scenario['sales_increase'], 
                    max_value=50, 
                    value=st.session_state.whatif_params['sales_increase_adjust'],
                    help="Adjust the projected sales increase from the upgrade. For example, +5% means the upgrade increases sales by 5% more than originally estimated."
                )
                
                # Return processing cost change
                st.session_state.whatif_params['return_processing_change'] = st.slider(
                    "Return Processing Cost Change (%)", 
                    min_value=-50, 
                    max_value=50, 
                    value=st.session_state.whatif_params['return_processing_change'],
                    help="Adjust the cost to process each return. This affects the value of each avoided return."
                )
                
                # Price change
                st.session_state.whatif_params['price_change'] = st.slider(
                    "Product Price Change (%)", 
                    min_value=-25, 
                    max_value=25, 
                    value=st.session_state.whatif_params['price_change'],
                    help="Adjust the product's sales price. This affects both revenue and the value of avoided returns."
                )
            
            # Calculate new values based on adjusted parameters
            new_development_cost = base_scenario['development_cost'] * (1 + st.session_state.whatif_params['development_cost_change']/100)
            new_unit_cost_change = base_scenario['unit_cost_change'] + st.session_state.whatif_params['unit_cost_change_adjust']
            new_reduction_rate = base_scenario['estimated_return_reduction'] + st.session_state.whatif_params['return_reduction_adjust']
            new_sales_increase = base_scenario['sales_increase'] + st.session_state.whatif_params['sales_increase_adjust']
            new_return_processing_cost = base_scenario['return_processing_cost'] * (1 + st.session_state.whatif_params['return_processing_change']/100)
            new_implementation_time = max(1, base_scenario['time_to_implement'] + st.session_state.whatif_params['implementation_time_change'])
            new_avg_price = base_scenario['avg_sale_price'] * (1 + st.session_state.whatif_params['price_change']/100)
            
            # Display comparison table
            st.markdown("### Parameter Comparison")
            
            comparison_data = {
                "Parameter": [
                    "Development Cost ($)",
                    "Unit Cost Change ($)",
                    "Return Reduction (%)",
                    "Sales Increase (%)",
                    "Return Processing Cost ($)",
                    "Implementation Time (months)",
                    "Average Price ($)"
                ],
                "Original": [
                    base_scenario['development_cost'],
                    base_scenario['unit_cost_change'],
                    base_scenario['estimated_return_reduction'],
                    base_scenario['sales_increase'],
                    base_scenario['return_processing_cost'],
                    base_scenario['time_to_implement'],
                    base_scenario['avg_sale_price']
                ],
                "New": [
                    new_development_cost,
                    new_unit_cost_change,
                    new_reduction_rate,
                    new_sales_increase,
                    new_return_processing_cost,
                    new_implementation_time,
                    new_avg_price
                ]
            }
            
            # Format for display
            comparison_df = pd.DataFrame(comparison_data)
            
            # Format currencies
            for i, param in enumerate(comparison_df["Parameter"]):
                if "Cost" in param or "Price" in param:
                    comparison_df.loc[i, "Original"] = f"${comparison_df.loc[i, 'Original']:,.2f}"
                    comparison_df.loc[i, "New"] = f"${float(comparison_df.loc[i, 'New']):,.2f}"
                elif "%" in param:
                    comparison_df.loc[i, "Original"] = f"{comparison_df.loc[i, 'Original']:.1f}%"
                    comparison_df.loc[i, "New"] = f"{float(comparison_df.loc[i, 'New']):.1f}%"
            
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        # Tab 2: Financial Impacts
        with tabs[1]:
            st.markdown("### Financial Impact Analysis")
            
            # Recalculate key metrics with new parameters
            # Get the parameter values
            development_cost = base_scenario['development_cost'] * (1 + st.session_state.whatif_params['development_cost_change']/100)
            unit_cost_change = base_scenario['unit_cost_change'] + st.session_state.whatif_params['unit_cost_change_adjust']
            reduction_rate = base_scenario['estimated_return_reduction'] + st.session_state.whatif_params['return_reduction_adjust']
            sales_increase = base_scenario['sales_increase'] + st.session_state.whatif_params['sales_increase_adjust']
            return_processing_cost = base_scenario['return_processing_cost'] * (1 + st.session_state.whatif_params['return_processing_change']/100)
            implementation_time = max(1, base_scenario['time_to_implement'] + st.session_state.whatif_params['implementation_time_change'])
            avg_price = base_scenario['avg_sale_price'] * (1 + st.session_state.whatif_params['price_change']/100)
            
            # Calculate original avoided returns and financial impact
            original_avoided_monthly = base_scenario['current_returns'] * (base_scenario['estimated_return_reduction'] / 100)
            original_savings_per_avoided = base_scenario['avg_sale_price'] + base_scenario['return_processing_cost'] - base_scenario['current_unit_cost']
            original_monthly_return_savings = original_avoided_monthly * original_savings_per_avoided
            
            original_additional_sales = base_scenario['current_unit_sales'] * (base_scenario['sales_increase'] / 100)
            original_margin_after = base_scenario['avg_sale_price'] - (base_scenario['current_unit_cost'] + base_scenario['unit_cost_change'])
            original_monthly_sales_benefit = original_additional_sales * original_margin_after
            
            original_additional_costs = base_scenario['unit_cost_change'] * (
                base_scenario['current_unit_sales'] - base_scenario['current_returns'] + original_avoided_monthly + original_additional_sales
            )
            
            original_monthly_net = original_monthly_return_savings + original_monthly_sales_benefit - original_additional_costs
            original_annual_net = original_monthly_net * 12
            
            # Calculate new financial impact
            new_avoided_monthly = base_scenario['current_returns'] * (reduction_rate / 100)
            new_savings_per_avoided = avg_price + return_processing_cost - base_scenario['current_unit_cost']
            new_monthly_return_savings = new_avoided_monthly * new_savings_per_avoided
            
            new_additional_sales = base_scenario['current_unit_sales'] * (sales_increase / 100)
            new_margin_after = avg_price - (base_scenario['current_unit_cost'] + unit_cost_change)
            new_monthly_sales_benefit = new_additional_sales * new_margin_after
            
            new_additional_costs = unit_cost_change * (
                base_scenario['current_unit_sales'] - base_scenario['current_returns'] + new_avoided_monthly + new_additional_sales
            )
            
            new_monthly_net = new_monthly_return_savings + new_monthly_sales_benefit - new_additional_costs
            new_annual_net = new_monthly_net * 12
            
            # Calculate ROI metrics
            if base_scenario['development_cost'] > 0 and original_annual_net > 0:
                original_roi = (original_annual_net / base_scenario['development_cost']) * 100
                original_payback = base_scenario['development_cost'] / original_monthly_net / 12
            else:
                original_roi = 0
                original_payback = None
            
            if development_cost > 0 and new_annual_net > 0:
                new_roi = (new_annual_net / development_cost) * 100
                new_payback = development_cost / new_monthly_net / 12
            else:
                new_roi = 0
                new_payback = None
            
            # Create financial comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Return Reduction Impact")
                
                metrics_data = {
                    "Metric": [
                        "Monthly Avoided Returns",
                        "Savings per Avoided Return",
                        "Monthly Return Savings"
                    ],
                    "Original": [
                        f"{original_avoided_monthly:.1f} units",
                        f"${original_savings_per_avoided:.2f}",
                        f"${original_monthly_return_savings:.2f}"
                    ],
                    "New": [
                        f"{new_avoided_monthly:.1f} units",
                        f"${new_savings_per_avoided:.2f}",
                        f"${new_monthly_return_savings:.2f}"
                    ],
                    "Change": [
                        f"{(new_avoided_monthly - original_avoided_monthly):.1f} units",
                        f"${(new_savings_per_avoided - original_savings_per_avoided):.2f}",
                        f"${(new_monthly_return_savings - original_monthly_return_savings):.2f}"
                    ]
                }
                
                metrics_df = pd.DataFrame(metrics_data)
                st.dataframe(metrics_df, use_container_width=True, hide_index=True)
                
                return_impact = (new_monthly_return_savings - original_monthly_return_savings) * 12
                
                # Chart comparing original and new return impact
                fig_return = go.Figure()
                
                categories = ['Avoided Returns', 'Monthly Return Savings']
                original_values = [original_avoided_monthly, original_monthly_return_savings]
                new_values = [new_avoided_monthly, new_monthly_return_savings]
                
                fig_return.add_trace(go.Bar(
                    x=categories,
                    y=original_values,
                    name='Original',
                    marker_color=COLOR_SCHEME['neutral']
                ))
                
                fig_return.add_trace(go.Bar(
                    x=categories,
                    y=new_values,
                    name='New',
                    marker_color=COLOR_SCHEME['positive']
                ))
                
                fig_return.update_layout(
                    title="Return Reduction Impact Comparison",
                    barmode='group',
                    height=400,
                    yaxis=dict(title='Value')
                )
                
                st.plotly_chart(fig_return, use_container_width=True)
            
            with col2:
                st.markdown("#### Sales Growth Impact")
                
                sales_metrics = {
                    "Metric": [
                        "Monthly Additional Sales",
                        "Margin per Unit",
                        "Monthly Sales Benefit"
                    ],
                    "Original": [
                        f"{original_additional_sales:.1f} units",
                        f"${original_margin_after:.2f}",
                        f"${original_monthly_sales_benefit:.2f}"
                    ],
                    "New": [
                        f"{new_additional_sales:.1f} units",
                        f"${new_margin_after:.2f}",
                        f"${new_monthly_sales_benefit:.2f}"
                    ],
                    "Change": [
                        f"{(new_additional_sales - original_additional_sales):.1f} units",
                        f"${(new_margin_after - original_margin_after):.2f}",
                        f"${(new_monthly_sales_benefit - original_monthly_sales_benefit):.2f}"
                    ]
                }
                
                sales_df = pd.DataFrame(sales_metrics)
                st.dataframe(sales_df, use_container_width=True, hide_index=True)
                
                sales_impact = (new_monthly_sales_benefit - original_monthly_sales_benefit) * 12
                
                # Chart comparing original and new sales impact
                fig_sales = go.Figure()
                
                categories = ['Additional Sales', 'Monthly Sales Benefit']
                original_values = [original_additional_sales, original_monthly_sales_benefit]
                new_values = [new_additional_sales, new_monthly_sales_benefit]
                
                fig_sales.add_trace(go.Bar(
                    x=categories,
                    y=original_values,
                    name='Original',
                    marker_color=COLOR_SCHEME['neutral']
                ))
                
                fig_sales.add_trace(go.Bar(
                    x=categories,
                    y=new_values,
                    name='New',
                    marker_color=COLOR_SCHEME['positive']
                ))
                
                fig_sales.update_layout(
                    title="Sales Growth Impact Comparison",
                    barmode='group',
                    height=400,
                    yaxis=dict(title='Value')
                )
                
                st.plotly_chart(fig_sales, use_container_width=True)
            
            # Overall financial impact
            st.markdown("#### Overall Financial Impact")
            
            # Summary metrics table
            summary_data = {
                "Metric": [
                    "Monthly Return Savings",
                    "Monthly Sales Benefit",
                    "Monthly Additional Costs",
                    "Monthly Net Benefit",
                    "Annual Net Benefit",
                    "Return on Investment",
                    "Payback Period"
                ],
                "Original": [
                    f"${original_monthly_return_savings:.2f}",
                    f"${original_monthly_sales_benefit:.2f}",
                    f"${original_additional_costs:.2f}",
                    f"${original_monthly_net:.2f}",
                    f"${original_annual_net:.2f}",
                    f"{original_roi:.1f}%" if original_roi is not None else "N/A",
                    f"{original_payback:.2f} years" if original_payback is not None else "N/A"
                ],
                "New": [
                    f"${new_monthly_return_savings:.2f}",
                    f"${new_monthly_sales_benefit:.2f}",
                    f"${new_additional_costs:.2f}",
                    f"${new_monthly_net:.2f}",
                    f"${new_annual_net:.2f}",
                    f"{new_roi:.1f}%" if new_roi is not None else "N/A",
                    f"{new_payback:.2f} years" if new_payback is not None else "N/A"
                ]
            }
            
            # Calculate percent changes
            summary_data["Change"] = [
                f"{((new_monthly_return_savings / original_monthly_return_savings) - 1) * 100:.1f}%" if original_monthly_return_savings > 0 else "N/A",
                f"{((new_monthly_sales_benefit / original_monthly_sales_benefit) - 1) * 100:.1f}%" if original_monthly_sales_benefit > 0 else "N/A",
                f"{((new_additional_costs / original_additional_costs) - 1) * 100:.1f}%" if original_additional_costs > 0 else "N/A",
                f"{((new_monthly_net / original_monthly_net) - 1) * 100:.1f}%" if original_monthly_net > 0 else "N/A",
                f"{((new_annual_net / original_annual_net) - 1) * 100:.1f}%" if original_annual_net > 0 else "N/A",
                f"{((new_roi / original_roi) - 1) * 100:.1f}%" if original_roi is not None and original_roi > 0 and new_roi is not None else "N/A",
                f"{((new_payback / original_payback) - 1) * 100:.1f}%" if original_payback is not None and new_payback is not None else "N/A"
            ]
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            # Waterfall chart
            st.markdown("#### Impact Breakdown")
            
            # Create waterfall chart data
            waterfall_data = [
                {"Factor": "Original Net Benefit", "Impact": original_monthly_net, "Type": "Total"},
                {"Factor": "Return Reduction", "Impact": new_monthly_return_savings - original_monthly_return_savings, "Type": "Increase" if new_monthly_return_savings > original_monthly_return_savings else "Decrease"},
                {"Factor": "Sales Growth", "Impact": new_monthly_sales_benefit - original_monthly_sales_benefit, "Type": "Increase" if new_monthly_sales_benefit > original_monthly_sales_benefit else "Decrease"},
                {"Factor": "Additional Costs", "Impact": original_additional_costs - new_additional_costs, "Type": "Increase" if original_additional_costs > new_additional_costs else "Decrease"},
                {"Factor": "New Net Benefit", "Impact": new_monthly_net, "Type": "Total"}
            ]
            
            waterfall_df = pd.DataFrame(waterfall_data)
            
            # Create the waterfall chart
            fig_waterfall = go.Figure(go.Waterfall(
                name="Monthly Net Benefit Changes",
                orientation="v",
                measure=["absolute"] + ["relative"] * 3 + ["total"],
                x=waterfall_df["Factor"],
                y=waterfall_df["Impact"],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                decreasing={"marker": {"color": COLOR_SCHEME["negative"]}},
                increasing={"marker": {"color": COLOR_SCHEME["positive"]}},
                totals={"marker": {"color": COLOR_SCHEME["primary"]}}
            ))
            
            fig_waterfall.update_layout(
                title="Monthly Net Benefit Impact Analysis",
                showlegend=False,
                height=500
            )
            
            st.plotly_chart(fig_waterfall, use_container_width=True)
            
            # Compare ROI and payback
            col1, col2 = st.columns(2)
            
            with col1:
                # ROI comparison
                roi_change = ((new_roi / original_roi) - 1) * 100 if original_roi > 0 and new_roi is not None else 0
                
                st.metric(
                    "Return on Investment",
                    f"{new_roi:.1f}%" if new_roi is not None else "N/A",
                    f"{roi_change:.1f}%" if original_roi > 0 and new_roi is not None else None,
                    delta_color="normal" if roi_change >= 0 else "inverse"
                )
            
            with col2:
                # Payback comparison
                if original_payback is not None and new_payback is not None:
                    payback_change = ((new_payback / original_payback) - 1) * 100
                    
                    st.metric(
                        "Payback Period",
                        f"{new_payback:.2f} years",
                        f"{payback_change:.1f}%",
                        delta_color="inverse"  # Inverse because lower payback is better
                    )
                else:
                    st.metric(
                        "Payback Period",
                        "N/A",
                        None
                    )
        
        # Tab 3: Sales/Return Impacts
        with tabs[2]:
            st.markdown("### Product Performance Analysis")
            
            # Extract parameters
            reduction_rate = base_scenario['estimated_return_reduction'] + st.session_state.whatif_params['return_reduction_adjust']
            sales_increase = base_scenario['sales_increase'] + st.session_state.whatif_params['sales_increase_adjust']
            
            # Calculate impacts on returns and sales
            original_return_rate = base_scenario['return_rate']
            new_return_rate = original_return_rate * (1 - reduction_rate/100)
            
            original_monthly_sales = base_scenario['current_unit_sales']
            new_monthly_sales = original_monthly_sales * (1 + sales_increase/100)
            
            original_monthly_returns = base_scenario['current_returns']
            new_monthly_returns = new_monthly_sales * (new_return_rate/100)
            
            monthly_returns_change = new_monthly_returns - original_monthly_returns
            monthly_returns_percent_change = (monthly_returns_change / original_monthly_returns) * 100
            
            # Create before/after comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Return Rate Impact")
                
                # Create return rate comparison chart
                return_data = {
                    "Metric": ["Return Rate", "Monthly Returns", "Annual Returns"],
                    "Before": [
                        f"{original_return_rate:.2f}%",
                        f"{original_monthly_returns:.1f} units",
                        f"{original_monthly_returns * 12:.1f} units"
                    ],
                    "After": [
                        f"{new_return_rate:.2f}%",
                        f"{new_monthly_returns:.1f} units",
                        f"{new_monthly_returns * 12:.1f} units"
                    ],
                    "Change": [
                        f"{(new_return_rate - original_return_rate):.2f}%",
                        f"{monthly_returns_change:.1f} units",
                        f"{monthly_returns_change * 12:.1f} units"
                    ]
                }
                
                return_df = pd.DataFrame(return_data)
                st.dataframe(return_df, use_container_width=True, hide_index=True)
                
                # Return rate chart
                fig_return_rate = go.Figure()
                
                # Add return rate bars
                fig_return_rate.add_trace(go.Bar(
                    x=["Before", "After"],
                    y=[original_return_rate, new_return_rate],
                    name="Return Rate (%)",
                    marker_color=[COLOR_SCHEME["negative"], COLOR_SCHEME["positive"]],
                    text=[f"{original_return_rate:.2f}%", f"{new_return_rate:.2f}%"],
                    textposition="auto"
                ))
                
                fig_return_rate.update_layout(
                    title="Return Rate Before vs After Upgrade",
                    height=400,
                    yaxis=dict(title="Return Rate (%)")
                )
                
                st.plotly_chart(fig_return_rate, use_container_width=True)
            
            with col2:
                st.markdown("#### Sales Volume Impact")
                
                # Create sales volume comparison chart
                sales_data = {
                    "Metric": ["Monthly Sales", "Annual Sales", "Sales Growth"],
                    "Before": [
                        f"{original_monthly_sales:.1f} units",
                        f"{original_monthly_sales * 12:.1f} units",
                        "N/A"
                    ],
                    "After": [
                        f"{new_monthly_sales:.1f} units",
                        f"{new_monthly_sales * 12:.1f} units",
                        f"{sales_increase:.2f}%"
                    ],
                    "Change": [
                        f"{(new_monthly_sales - original_monthly_sales):.1f} units",
                        f"{(new_monthly_sales - original_monthly_sales) * 12:.1f} units",
                        f"{sales_increase:.2f}%"
                    ]
                }
                
                sales_df = pd.DataFrame(sales_data)
                st.dataframe(sales_df, use_container_width=True, hide_index=True)
                
                # Sales volume chart
                fig_sales = go.Figure()
                
                # Add sales volume bars
                fig_sales.add_trace(go.Bar(
                    x=["Before", "After"],
                    y=[original_monthly_sales, new_monthly_sales],
                    name="Monthly Sales (units)",
                    marker_color=[COLOR_SCHEME["neutral"], COLOR_SCHEME["positive"]],
                    text=[f"{original_monthly_sales:.1f}", f"{new_monthly_sales:.1f}"],
                    textposition="auto"
                ))
                
                fig_sales.update_layout(
                    title="Monthly Sales Before vs After Upgrade",
                    height=400,
                    yaxis=dict(title="Monthly Sales (units)")
                )
                
                st.plotly_chart(fig_sales, use_container_width=True)
            
            # Combined impact
            st.markdown("#### Combined Impact on Unit Economics")
            
            # Calculate unit economics
            price_change = st.session_state.whatif_params['price_change']
            unit_cost_change = base_scenario['unit_cost_change'] + st.session_state.whatif_params['unit_cost_change_adjust']
            
            original_price = base_scenario['avg_sale_price']
            new_price = original_price * (1 + price_change/100)
            
            original_unit_cost = base_scenario['current_unit_cost']
            new_unit_cost = original_unit_cost + unit_cost_change
            
            original_margin = original_price - original_unit_cost
            new_margin = new_price - new_unit_cost
            
            original_margin_percent = (original_margin / original_price) * 100
            new_margin_percent = (new_margin / new_price) * 100
            
            # Calculate total revenue and profit impact
            original_monthly_revenue = original_monthly_sales * original_price
            new_monthly_revenue = new_monthly_sales * new_price
            
            original_monthly_profit = original_monthly_sales * original_margin
            new_monthly_profit = new_monthly_sales * new_margin
            
            revenue_change = new_monthly_revenue - original_monthly_revenue
            profit_change = new_monthly_profit - original_monthly_profit
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Monthly Revenue",
                    f"${new_monthly_revenue:.2f}",
                    f"{((new_monthly_revenue / original_monthly_revenue) - 1) * 100:.1f}%",
                    delta_color="normal"
                )
            
            with col2:
                st.metric(
                    "Monthly Profit",
                    f"${new_monthly_profit:.2f}",
                    f"{((new_monthly_profit / original_monthly_profit) - 1) * 100:.1f}%",
                    delta_color="normal"
                )
            
            with col3:
                st.metric(
                    "Unit Margin",
                    f"${new_margin:.2f} ({new_margin_percent:.1f}%)",
                    f"{((new_margin / original_margin) - 1) * 100:.1f}%",
                    delta_color="normal" if new_margin >= original_margin else "inverse"
                )
            
            # Create unit economics comparison chart
            fig_unit = go.Figure()
            
            # Add price, cost, and margin bars
            categories = ["Price", "Unit Cost", "Margin"]
            original_values = [original_price, original_unit_cost, original_margin]
            new_values = [new_price, new_unit_cost, new_margin]
            
            fig_unit.add_trace(go.Bar(
                x=categories,
                y=original_values,
                name="Before",
                marker_color=COLOR_SCHEME["neutral"]
            ))
            
            fig_unit.add_trace(go.Bar(
                x=categories,
                y=new_values,
                name="After",
                marker_color=COLOR_SCHEME["positive"]
            ))
            
            fig_unit.update_layout(
                title="Unit Economics Before vs After Upgrade",
                barmode="group",
                height=400,
                yaxis=dict(title="Amount ($)")
            )
            
            st.plotly_chart(fig_unit, use_container_width=True)
        
        # Tab 4: Production Timeline
        with tabs[3]:
            st.markdown("### Implementation Timeline Analysis")
            
            # Get implementation time parameters
            original_time = base_scenario['time_to_implement']
            new_time = max(1, original_time + st.session_state.whatif_params['implementation_time_change'])
            
            # Calculate development cost
            original_dev_cost = base_scenario['development_cost']
            new_dev_cost = original_dev_cost * (1 + st.session_state.whatif_params['development_cost_change']/100)
            
            # Calculate monthly net benefit
            original_monthly_net = base_scenario['monthly_net_benefit']
            
            # Recalculate monthly net with new parameters
            reduction_rate = base_scenario['estimated_return_reduction'] + st.session_state.whatif_params['return_reduction_adjust']
            sales_increase = base_scenario['sales_increase'] + st.session_state.whatif_params['sales_increase_adjust']
            unit_cost_change = base_scenario['unit_cost_change'] + st.session_state.whatif_params['unit_cost_change_adjust']
            avg_price = base_scenario['avg_sale_price'] * (1 + st.session_state.whatif_params['price_change']/100)
            return_processing_cost = base_scenario['return_processing_cost'] * (1 + st.session_state.whatif_params['return_processing_change']/100)
            
            # Calculate new monthly net benefit
            new_avoided_monthly = base_scenario['current_returns'] * (reduction_rate / 100)
            new_savings_per_avoided = avg_price + return_processing_cost - base_scenario['current_unit_cost']
            new_monthly_return_savings = new_avoided_monthly * new_savings_per_avoided
            
            new_additional_sales = base_scenario['current_unit_sales'] * (sales_increase / 100)
            new_margin_after = avg_price - (base_scenario['current_unit_cost'] + unit_cost_change)
            new_monthly_sales_benefit = new_additional_sales * new_margin_after
            
            new_additional_costs = unit_cost_change * (
                base_scenario['current_unit_sales'] - base_scenario['current_returns'] + new_avoided_monthly + new_additional_sales
            )
            
            new_monthly_net = new_monthly_return_savings + new_monthly_sales_benefit - new_additional_costs
            
            # Calculate time to breakeven
            if original_monthly_net > 0:
                original_breakeven_months = original_dev_cost / original_monthly_net
                original_total_time = original_time + original_breakeven_months
            else:
                original_breakeven_months = float('inf')
                original_total_time = float('inf')
            
            if new_monthly_net > 0:
                new_breakeven_months = new_dev_cost / new_monthly_net
                new_total_time = new_time + new_breakeven_months
            else:
                new_breakeven_months = float('inf')
                new_total_time = float('inf')
            
            # Display timeline comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Timeline Comparison")
                
                timeline_data = {
                    "Metric": [
                        "Implementation Time",
                        "Breakeven Time (after implementation)",
                        "Total Time to ROI Positive"
                    ],
                    "Original": [
                        f"{original_time} months",
                        f"{original_breakeven_months:.1f} months" if original_breakeven_months != float('inf') else "Never",
                        f"{original_total_time:.1f} months" if original_total_time != float('inf') else "Never"
                    ],
                    "New": [
                        f"{new_time} months",
                        f"{new_breakeven_months:.1f} months" if new_breakeven_months != float('inf') else "Never",
                        f"{new_total_time:.1f} months" if new_total_time != float('inf') else "Never"
                    ],
                    "Change": [
                        f"{new_time - original_time} months",
                        f"{new_breakeven_months - original_breakeven_months:.1f} months" if original_breakeven_months != float('inf') and new_breakeven_months != float('inf') else "N/A",
                        f"{new_total_time - original_total_time:.1f} months" if original_total_time != float('inf') and new_total_time != float('inf') else "N/A"
                    ]
                }
                
                timeline_df = pd.DataFrame(timeline_data)
                st.dataframe(timeline_df, use_container_width=True, hide_index=True)
                
                # Show key metrics
                st.markdown("#### Key Timeline Metrics")
                
                time_diff = new_total_time - original_total_time if original_total_time != float('inf') and new_total_time != float('inf') else None
                
                st.metric(
                    "Total Time to Positive ROI",
                    f"{new_total_time:.1f} months" if new_total_time != float('inf') else "Never",
                    f"{time_diff:.1f} months" if time_diff is not None else None,
                    delta_color="inverse"  # Inverse because shorter time is better
                )
                
                # Calculate opportunity cost
                if original_monthly_net > 0:
                    opportunity_cost = original_monthly_net * (new_time - original_time) if new_time > original_time else 0
                    
                    st.metric(
                        "Opportunity Cost of Delayed Implementation",
                        f"${opportunity_cost:.2f}",
                        None
                    )
            
            with col2:
                st.markdown("#### Timeline Visualization")
                
                # Create timeline visualization
                # First, create data for Gantt-like chart
                
                # Original timeline
                original_timeline = [
                    dict(Task="Original", Start=0, Finish=original_time, Resource="Implementation"),
                    dict(Task="Original", Start=original_time, Finish=original_time + original_breakeven_months if original_breakeven_months != float('inf') else 36, Resource="Breakeven")
                ]
                
                # New timeline
                new_timeline = [
                    dict(Task="New", Start=0, Finish=new_time, Resource="Implementation"),
                    dict(Task="New", Start=new_time, Finish=new_time + new_breakeven_months if new_breakeven_months != float('inf') else 36, Resource="Breakeven")
                ]
                
                # Combined timeline data
                timeline_chart_data = pd.DataFrame(original_timeline + new_timeline)
                
                # Create Gantt-like chart using a bar chart
                fig_timeline = px.timeline(
                    timeline_chart_data,
                    x_start="Start",
                    x_end="Finish",
                    y="Task",
                    color="Resource",
                    color_discrete_map={
                        "Implementation": COLOR_SCHEME["warning"],
                        "Breakeven": COLOR_SCHEME["positive"]
                    },
                    labels={"Task": "Scenario", "Start": "Month", "Finish": "Month"},
                    title="Implementation and Breakeven Timeline"
                )
                
                fig_timeline.update_yaxes(autorange="reversed")
                fig_timeline.update_layout(height=300)
                
                st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Cumulative cash flow chart
                st.markdown("#### Cumulative Cash Flow")
                
                # Generate monthly cash flows for both scenarios
                months = list(range(37))  # 0-36 months
                
                # Original cash flows
                original_cash_flows = [-original_dev_cost]  # Initial investment
                original_cum_cash_flow = [-original_dev_cost]
                
                # New cash flows
                new_cash_flows = [-new_dev_cost]  # Initial investment
                new_cum_cash_flow = [-new_dev_cost]
                
                # For each future month
                for month in range(1, 37):
                    # Original scenario
                    if month <= original_time:
                        original_cf = 0
                    else:
                        original_cf = original_monthly_net
                    
                    original_cash_flows.append(original_cf)
                    original_cum_cash_flow.append(original_cum_cash_flow[-1] + original_cf)
                    
                    # New scenario
                    if month <= new_time:
                        new_cf = 0
                    else:
                        new_cf = new_monthly_net
                    
                    new_cash_flows.append(new_cf)
                    new_cum_cash_flow.append(new_cum_cash_flow[-1] + new_cf)
                
                # Create cash flow chart
                fig_cash_flow = go.Figure()
                
                # Add original cumulative cash flow
                fig_cash_flow.add_trace(go.Scatter(
                    x=months,
                    y=original_cum_cash_flow,
                    name="Original",
                    mode="lines",
                    line=dict(width=3, color=COLOR_SCHEME["neutral"])
                ))
                
                # Add new cumulative cash flow
                fig_cash_flow.add_trace(go.Scatter(
                    x=months,
                    y=new_cum_cash_flow,
                    name="New",
                    mode="lines",
                    line=dict(width=3, color=COLOR_SCHEME["positive"])
                ))
                
                # Add horizontal line at y=0
                fig_cash_flow.add_shape(
                    type="line",
                    x0=0, y0=0,
                    x1=36, y1=0,
                    line=dict(color="black", width=1, dash="dash")
                )
                
                # Configure chart
                fig_cash_flow.update_layout(
                    title="Cumulative Cash Flow Comparison",
                    xaxis_title="Month",
                    yaxis_title="Cumulative Cash Flow ($)",
                    height=400,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    )
                )
                
                st.plotly_chart(fig_cash_flow, use_container_width=True)
        
        # Option to save as new scenario
        st.markdown("### Save What-If Scenario")
        
        new_name = st.text_input("New Scenario Name", 
                               value=f"{base_scenario_name} (What-If)", 
                               help="Name for the new scenario if you choose to save it")
        
        if st.button("Save as New Scenario"):
            # Get all the updated values
            development_cost = base_scenario['development_cost'] * (1 + st.session_state.whatif_params['development_cost_change']/100)
            unit_cost_change = base_scenario['unit_cost_change'] + st.session_state.whatif_params['unit_cost_change_adjust']
            reduction_rate = base_scenario['estimated_return_reduction'] + st.session_state.whatif_params['return_reduction_adjust']
            sales_increase = base_scenario['sales_increase'] + st.session_state.whatif_params['sales_increase_adjust']
            return_processing_cost = base_scenario['return_processing_cost'] * (1 + st.session_state.whatif_params['return_processing_change']/100)
            implementation_time = max(1, base_scenario['time_to_implement'] + st.session_state.whatif_params['implementation_time_change'])
            avg_price = base_scenario['avg_sale_price'] * (1 + st.session_state.whatif_params['price_change']/100)
            
            # Recalculate annual values based on new pricing
            annual_unit_sales = base_scenario['annual_unit_sales']
            annual_returns = base_scenario['annual_returns']
            
            # Call add_scenario with the new values
            success, message = optimizer.add_scenario(
                new_name, base_scenario['product_name'], base_scenario['product_category'],
                base_scenario['current_unit_sales'], avg_price, base_scenario['sales_channel'],
                base_scenario['current_returns'], base_scenario['upgrade_solution'], development_cost,
                unit_cost_change, base_scenario['current_unit_cost'], reduction_rate,
                sales_increase, base_scenario['product_lifecycle_stage'], annual_unit_sales,
                annual_returns, return_processing_cost, implementation_time
            )
            
            if success:
                st.success(f"What-if scenario saved as '{new_name}'!")
            else:
                st.error(message)
    else:
        st.info("Add scenarios first to use the what-if analysis tool.")

def display_settings():
    """Display app settings and data management options"""
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
                file_name="kaizenroi_scenarios.json",
                mime="application/json"
            )
            
            # Export as Excel
            excel_data = io.BytesIO()
            with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
                optimizer.scenarios.to_excel(writer, index=False, sheet_name='Scenarios')
            
            st.download_button(
                "Export as Excel Spreadsheet",
                data=excel_data.getvalue(),
                file_name="kaizenroi_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Export as CSV
            csv_data = optimizer.scenarios.to_csv(index=False).encode()
            st.download_button(
                "Export as CSV",
                data=csv_data,
                file_name="kaizenroi_export.csv",
                mime="text/csv"
            )
        
        # Import data
        st.markdown("#### Import Data")
        uploaded_file = st.file_uploader("Upload scenario data (JSON)", type=["json"])
        
        if uploaded_file is not None:
            json_str = uploaded_file.read().decode("utf-8")
            if optimizer.upload_json(json_str):
                st.success("Data imported successfully!")
            else:
                st.error("Failed to import data. Please check the file format.")
    
    with col2:
        st.markdown("### App Settings")
        
        # Reset data
        st.markdown("#### Data Management")
        if st.button("Add Example Scenarios"):
            count = optimizer.add_example_scenarios()
            st.success(f"Added {count} example scenarios!")
        
        if st.button("Clear All Data"):
            confirm = st.checkbox("I understand this will delete all scenarios")
            if confirm:
                optimizer.scenarios = pd.DataFrame(columns=optimizer.scenarios.columns)
                optimizer.save_data()
                st.success("All data cleared!")
                st.experimental_rerun()

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <p class="logo-icon">🔄</p>
        <p class="logo-text">KaizenROI</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## Navigation")
    
    # Navigation options
    nav_option = st.radio(
        "Go to:",
        ["Dashboard", "Add New Scenario", "Portfolio Analysis", "What-If Analysis", "Settings"],
        index=0
    )
    
    st.markdown("---")
    
    # Help section
    with st.expander("📘 Help & Formulas"):
        st.markdown("""
        ### Key Terms
        - **Return Rate**: Percentage of products returned
        - **Return Processing Cost**: Cost to handle each return (customer service, shipping, inspection)
        - **Return Reduction**: Estimated percentage reduction in returns after product upgrade
        - **Sales Increase**: Estimated percentage increase in sales from the upgrade
        - **Break-even**: Time to recover the development investment
        - **ROI**: Return on investment (net benefit / development cost)
        - **NPV**: Net Present Value of future cash flows at 10% discount rate
        - **Payback Period**: Total time to recoup investment including implementation time
        
        ### Key Formulas
        - Return Rate = (Returns / Sales) × 100%
        - Avoided Returns = Returns × Reduction Rate
        - Savings per Avoided Return = Sale Price + Return Processing Cost - Unit Cost
        - Additional Sales = Current Sales × Sales Increase %
        - Sales Benefit = Additional Sales × Margin per Unit
        - Net Benefit = Return Savings + Sales Benefit - Additional Costs
        - ROI = (Net Benefit / Development Cost) × 100%
        """)
    
    with st.expander("🔎 Understanding Product Upgrade ROI"):
        st.markdown("""
        ### Product Upgrade ROI Analysis
        
        Product upgrades typically impact ROI through two main mechanisms:
        
        1. **Return Rate Reduction**: Improving product quality, clearer descriptions, better size guides, etc. can significantly reduce costly returns.
        
        2. **Sales Growth**: Enhanced products often experience higher sales volumes through improved customer satisfaction, word-of-mouth, and review ratings.
        
        The most successful product upgrades positively impact both dimensions simultaneously, creating a compounding effect on ROI.
        
        ### Maximizing Product Upgrade ROI
        
        - **Low-Cost, High-Impact Improvements**: Prioritize changes that require minimal investment but address top return reasons.
        
        - **Focus on Production Efficiency**: When possible, design upgrades that reduce per-unit costs while improving quality.
        
        - **Accelerate Implementation**: Faster implementation means quicker payback and less opportunity cost.
        
        - **Target Growth-Stage Products**: Products in the growth phase of their lifecycle typically see the highest ROI from upgrades.
        """)
    
    # Footer
    st.markdown("---")
    st.caption("KaizenROI v2.0 | Product Upgrade ROI Analyzer")
    st.caption("© 2025 KaizenROI Analytics")

# Main content
display_header()

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
    
    elif nav_option == "What-If Analysis":
        display_what_if_analysis()
    
    elif nav_option == "Settings":
        display_settings()

# Entry point for setup.py
def main():
    """Entry point for the application."""
    # The Streamlit script is already executing, so this function is just a noop when run directly
    pass

if __name__ == "__main__":
    main()
