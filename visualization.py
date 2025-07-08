"""
Visualization functions for SWMM5 watershed modeling results and parameters.
Creates interactive plots and charts using Plotly for results display.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

def create_results_plots(results: Dict[str, Any]) -> go.Figure:
    """
    Create comprehensive results visualization plots.
    
    Args:
        results: Dictionary containing simulation results
        
    Returns:
        Plotly figure with multiple subplots
    """
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Hydrograph', 'Rainfall Pattern', 'Cumulative Runoff', 'Flow Duration'),
        specs=[[{"secondary_y": True}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]],
        horizontal_spacing=0.08,
        vertical_spacing=0.12
    )
    
    if 'time_series' in results:
        time_series = results['time_series']
        time = time_series['time']
        rainfall = time_series['rainfall']
        runoff = time_series['runoff']
        
        # Subplot 1: Hydrograph with rainfall
        fig.add_trace(
            go.Scatter(
                x=time,
                y=runoff,
                mode='lines',
                name='Runoff',
                line=dict(color='blue', width=2),
                fill='tozeroy',
                fillcolor='rgba(0,100,255,0.1)'
            ),
            row=1, col=1
        )
        
        # Add rainfall as secondary y-axis
        fig.add_trace(
            go.Bar(
                x=time,
                y=rainfall,
                name='Rainfall',
                marker_color='rgba(128,128,128,0.6)',
                yaxis='y2'
            ),
            row=1, col=1, secondary_y=True
        )
        
        # Subplot 2: Rainfall pattern
        fig.add_trace(
            go.Scatter(
                x=time,
                y=rainfall,
                mode='lines+markers',
                name='Rainfall Intensity',
                line=dict(color='gray', width=2),
                marker=dict(size=4)
            ),
            row=1, col=2
        )
        
        # Subplot 3: Cumulative runoff
        cumulative_runoff = np.cumsum(runoff) * 0.25 / 3600  # Convert to acre-feet
        fig.add_trace(
            go.Scatter(
                x=time,
                y=cumulative_runoff,
                mode='lines',
                name='Cumulative Runoff',
                line=dict(color='green', width=2),
                fill='tozeroy',
                fillcolor='rgba(0,255,0,0.1)'
            ),
            row=2, col=1
        )
        
        # Subplot 4: Flow duration curve
        sorted_flows = np.sort(runoff)[::-1]  # Sort in descending order
        exceedance_prob = np.arange(1, len(sorted_flows) + 1) / len(sorted_flows) * 100
        
        fig.add_trace(
            go.Scatter(
                x=exceedance_prob,
                y=sorted_flows,
                mode='lines',
                name='Flow Duration',
                line=dict(color='red', width=2)
            ),
            row=2, col=2
        )
    
    # Update layout
    fig.update_layout(
        title_text="SWMM5 Simulation Results",
        title_x=0.5,
        showlegend=True,
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Update x-axis titles
    fig.update_xaxes(title_text="Time (hours)", row=1, col=1)
    fig.update_xaxes(title_text="Time (hours)", row=1, col=2)
    fig.update_xaxes(title_text="Time (hours)", row=2, col=1)
    fig.update_xaxes(title_text="Exceedance Probability (%)", row=2, col=2)
    
    # Update y-axis titles
    fig.update_yaxes(title_text="Runoff (cfs)", row=1, col=1)
    fig.update_yaxes(title_text="Rainfall (in/hr)", row=1, col=2)
    fig.update_yaxes(title_text="Cumulative Runoff (acre-ft)", row=2, col=1)
    fig.update_yaxes(title_text="Flow (cfs)", row=2, col=2)
    
    # Update secondary y-axis
    fig.update_yaxes(title_text="Rainfall (in/hr)", secondary_y=True, row=1, col=1)
    
    return fig

def create_parameter_summary(parameters: Dict[str, Any]) -> go.Figure:
    """
    Create parameter summary visualization.
    
    Args:
        parameters: Dictionary containing model parameters
        
    Returns:
        Plotly figure with parameter summary
    """
    # Create subplots for parameter visualization
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Subcatchment Properties', 'Surface Characteristics', 
                       'Infiltration Parameters', 'Climate Settings'),
        specs=[[{"type": "xy"}, {"type": "xy"}],
               [{"type": "xy"}, {"type": "xy"}]],
        horizontal_spacing=0.1,
        vertical_spacing=0.15
    )
    
    # Subplot 1: Subcatchment properties (bar chart)
    subcatch = parameters.get('subcatchment', {})
    subcatch_params = ['Area (acres)', 'Width (feet)', 'Slope (%)']
    subcatch_values = [
        subcatch.get('area', 0),
        subcatch.get('width', 0),
        subcatch.get('slope', 0)
    ]
    
    fig.add_trace(
        go.Bar(
            x=subcatch_params,
            y=subcatch_values,
            name='Subcatchment',
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
        ),
        row=1, col=1
    )
    
    # Subplot 2: Surface characteristics (pie chart for imperviousness)
    surface = parameters.get('surface', {})
    pct_impervious = surface.get('pct_impervious', 0)
    pct_pervious = 100 - pct_impervious
    
    fig.add_trace(
        go.Pie(
            labels=['Impervious', 'Pervious'],
            values=[pct_impervious, pct_pervious],
            name="Surface Types",
            marker_colors=['#d62728', '#2ca02c']
        ),
        row=1, col=2
    )
    
    # Subplot 3: Infiltration parameters (depends on method)
    infiltration = parameters.get('infiltration', {})
    method = infiltration.get('method', 'Horton')
    
    if method == 'Horton':
        horton = infiltration.get('horton', {})
        infilt_params = ['Max Rate', 'Min Rate', 'Decay Constant', 'Drying Time']
        infilt_values = [
            horton.get('max_rate', 0),
            horton.get('min_rate', 0),
            horton.get('decay_constant', 0),
            horton.get('drying_time', 0)
        ]
    elif method == 'Green-Ampt':
        ga = infiltration.get('green_ampt', {})
        infilt_params = ['Suction Head', 'Conductivity', 'Initial Deficit']
        infilt_values = [
            ga.get('suction_head', 0),
            ga.get('conductivity', 0),
            ga.get('initial_deficit', 0)
        ]
    else:
        infilt_params = ['Parameter 1', 'Parameter 2', 'Parameter 3']
        infilt_values = [1, 2, 3]
    
    fig.add_trace(
        go.Scatter(
            x=infilt_params,
            y=infilt_values,
            mode='lines+markers',
            name=f'{method} Infiltration',
            line=dict(color='purple', width=2),
            marker=dict(size=8)
        ),
        row=2, col=1
    )
    
    # Subplot 4: Climate settings (gauge for evaporation)
    climate = parameters.get('climate', {})
    evap_value = climate.get('evap_constant', 0)
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=evap_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Evaporation (in/day)"},
            gauge={
                'axis': {'range': [None, 1.0]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 0.2], 'color': "lightgray"},
                    {'range': [0.2, 0.4], 'color': "gray"},
                    {'range': [0.4, 1.0], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.5
                }
            }
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text="Parameter Summary Dashboard",
        title_x=0.5,
        showlegend=False,
        height=700,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_sensitivity_analysis(base_parameters: Dict[str, Any], 
                              sensitivity_results: Dict[str, Any]) -> go.Figure:
    """
    Create sensitivity analysis visualization.
    
    Args:
        base_parameters: Base parameter values
        sensitivity_results: Results from sensitivity analysis
        
    Returns:
        Plotly figure showing sensitivity analysis
    """
    fig = go.Figure()
    
    # Example sensitivity analysis plot
    parameters = list(sensitivity_results.keys())
    sensitivities = list(sensitivity_results.values())
    
    fig.add_trace(
        go.Bar(
            x=parameters,
            y=sensitivities,
            name='Sensitivity',
            marker_color=['red' if x > 0.5 else 'blue' for x in sensitivities]
        )
    )
    
    fig.update_layout(
        title="Parameter Sensitivity Analysis",
        xaxis_title="Parameters",
        yaxis_title="Sensitivity Index",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_comparison_plot(results_list: List[Dict[str, Any]], 
                          labels: List[str]) -> go.Figure:
    """
    Create comparison plot for multiple simulation results.
    
    Args:
        results_list: List of simulation results
        labels: Labels for each result set
        
    Returns:
        Plotly figure comparing results
    """
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set1
    
    for i, (results, label) in enumerate(zip(results_list, labels)):
        if 'time_series' in results:
            time_series = results['time_series']
            time = time_series['time']
            runoff = time_series['runoff']
            
            fig.add_trace(
                go.Scatter(
                    x=time,
                    y=runoff,
                    mode='lines',
                    name=label,
                    line=dict(color=colors[i % len(colors)], width=2)
                )
            )
    
    fig.update_layout(
        title="Simulation Results Comparison",
        xaxis_title="Time (hours)",
        yaxis_title="Runoff (cfs)",
        legend=dict(x=0.7, y=0.9),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_parameter_distribution(parameters: Dict[str, Any]) -> go.Figure:
    """
    Create parameter distribution visualization.
    
    Args:
        parameters: Dictionary of parameter values
        
    Returns:
        Plotly figure showing parameter distributions
    """
    # Create violin plots for parameter distributions
    fig = go.Figure()
    
    # Example: Show distribution of surface parameters
    surface = parameters.get('surface', {})
    
    # Create sample data for visualization (in practice, this would come from uncertainty analysis)
    manning_n_data = np.random.normal(surface.get('n_imperv', 0.012), 0.002, 100)
    
    fig.add_trace(
        go.Violin(
            y=manning_n_data,
            name="Manning's n (Imperv)",
            box_visible=True,
            meanline_visible=True
        )
    )
    
    fig.update_layout(
        title="Parameter Distribution Analysis",
        yaxis_title="Parameter Value",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_validation_plot(observed_data: pd.DataFrame, 
                          simulated_data: pd.DataFrame) -> go.Figure:
    """
    Create validation plot comparing observed vs simulated data.
    
    Args:
        observed_data: Observed flow data
        simulated_data: Simulated flow data
        
    Returns:
        Plotly figure showing validation results
    """
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Time Series Comparison', 'Scatter Plot'),
        vertical_spacing=0.1
    )
    
    # Time series comparison
    fig.add_trace(
        go.Scatter(
            x=observed_data.index,
            y=observed_data['flow'],
            mode='lines',
            name='Observed',
            line=dict(color='black', width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=simulated_data.index,
            y=simulated_data['flow'],
            mode='lines',
            name='Simulated',
            line=dict(color='red', width=2, dash='dash')
        ),
        row=1, col=1
    )
    
    # Scatter plot
    fig.add_trace(
        go.Scatter(
            x=observed_data['flow'],
            y=simulated_data['flow'],
            mode='markers',
            name='Observed vs Simulated',
            marker=dict(color='blue', size=6)
        ),
        row=2, col=1
    )
    
    # Add 1:1 line
    max_val = max(observed_data['flow'].max(), simulated_data['flow'].max())
    fig.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            name='1:1 Line',
            line=dict(color='gray', dash='dash')
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title="Model Validation Results",
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_xaxes(title_text="Time", row=1, col=1)
    fig.update_xaxes(title_text="Observed Flow (cfs)", row=2, col=1)
    fig.update_yaxes(title_text="Flow (cfs)", row=1, col=1)
    fig.update_yaxes(title_text="Simulated Flow (cfs)", row=2, col=1)
    
    return fig

def create_uncertainty_bands(results: Dict[str, Any], 
                           uncertainty_bounds: Dict[str, Any]) -> go.Figure:
    """
    Create uncertainty visualization with confidence bands.
    
    Args:
        results: Base simulation results
        uncertainty_bounds: Upper and lower bounds for uncertainty
        
    Returns:
        Plotly figure with uncertainty bands
    """
    fig = go.Figure()
    
    if 'time_series' in results:
        time_series = results['time_series']
        time = time_series['time']
        runoff = time_series['runoff']
        
        # Add uncertainty bounds
        upper_bound = uncertainty_bounds.get('upper', runoff * 1.2)
        lower_bound = uncertainty_bounds.get('lower', runoff * 0.8)
        
        # Add confidence band
        fig.add_trace(
            go.Scatter(
                x=np.concatenate([time, time[::-1]]),
                y=np.concatenate([upper_bound, lower_bound[::-1]]),
                fill='toself',
                fillcolor='rgba(0,100,255,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='95% Confidence Interval'
            )
        )
        
        # Add main result
        fig.add_trace(
            go.Scatter(
                x=time,
                y=runoff,
                mode='lines',
                name='Best Estimate',
                line=dict(color='blue', width=2)
            )
        )
    
    fig.update_layout(
        title="Simulation Results with Uncertainty",
        xaxis_title="Time (hours)",
        yaxis_title="Runoff (cfs)",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig
