import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import io
import os
from typing import Dict, Any, Optional

# Import custom modules
from swmm_model import SWMMModel
from parameter_defaults import get_default_parameters
from validation import validate_parameters, get_validation_messages
from visualization import create_results_plots, create_parameter_summary

# Set page configuration
st.set_page_config(
    page_title="SWMM5 Watershed Runoff Modeling",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'model' not in st.session_state:
    st.session_state.model = SWMMModel()
if 'parameters' not in st.session_state:
    st.session_state.parameters = get_default_parameters()
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None
if 'validation_messages' not in st.session_state:
    st.session_state.validation_messages = []

def main():
    st.title("🌊 SWMM5 Watershed Runoff Modeling Application")
    st.markdown("*Comprehensive parameter input, validation, and simulation capabilities*")
    
    # Sidebar for navigation and quick actions
    with st.sidebar:
        st.header("Model Controls")
        
        # Model actions
        if st.button("🔄 Reset All Parameters", type="secondary"):
            st.session_state.parameters = get_default_parameters()
            st.session_state.simulation_results = None
            st.session_state.validation_messages = []
            st.rerun()
        
        if st.button("📊 Run Simulation", type="primary"):
            run_simulation()
        
        # Export options
        st.header("Export Options")
        if st.button("📥 Export SWMM5 .inp File"):
            export_inp_file()
        
        if st.button("📄 Export Parameters CSV"):
            export_parameters_csv()
        
        # Model information
        st.header("Model Information")
        st.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Validation status
        validation_messages = get_validation_messages(st.session_state.parameters)
        if validation_messages:
            st.error(f"⚠️ {len(validation_messages)} validation issues found")
        else:
            st.success("✅ All parameters validated")
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📍 Subcatchments", 
        "🏞️ Surface Properties", 
        "💧 Infiltration", 
        "🌡️ Climate Data",
        "📊 Results",
        "📋 Summary"
    ])
    
    with tab1:
        subcatchment_parameters()
    
    with tab2:
        surface_properties()
    
    with tab3:
        infiltration_parameters()
    
    with tab4:
        climate_parameters()
    
    with tab5:
        results_display()
    
    with tab6:
        parameter_summary()

def subcatchment_parameters():
    st.header("Subcatchment Parameters")
    st.markdown("Configure basic geometry and outlet connections for watershed subcatchments.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Geometry")
        
        # Area input
        area = st.number_input(
            "Area (acres)",
            min_value=0.1,
            max_value=10000.0,
            value=st.session_state.parameters['subcatchment']['area'],
            step=0.1,
            help="Total subcatchment area in acres"
        )
        st.session_state.parameters['subcatchment']['area'] = area
        
        # Width input
        width = st.number_input(
            "Width (feet)",
            min_value=10.0,
            max_value=5000.0,
            value=st.session_state.parameters['subcatchment']['width'],
            step=10.0,
            help="Flow width perpendicular to flow direction"
        )
        st.session_state.parameters['subcatchment']['width'] = width
        
        # Slope input
        slope = st.number_input(
            "Slope (%)",
            min_value=0.1,
            max_value=50.0,
            value=st.session_state.parameters['subcatchment']['slope'],
            step=0.1,
            help="Average surface slope percentage"
        )
        st.session_state.parameters['subcatchment']['slope'] = slope
    
    with col2:
        st.subheader("Outlet Configuration")
        
        # Outlet selection
        outlet_type = st.selectbox(
            "Outlet Type",
            ["Node", "Subcatchment"],
            index=0 if st.session_state.parameters['subcatchment']['outlet_type'] == "Node" else 1,
            help="Type of outlet receiving runoff"
        )
        st.session_state.parameters['subcatchment']['outlet_type'] = outlet_type
        
        # Outlet name
        outlet_name = st.text_input(
            "Outlet Name",
            value=st.session_state.parameters['subcatchment']['outlet_name'],
            help="Name of the downstream node or subcatchment"
        )
        st.session_state.parameters['subcatchment']['outlet_name'] = outlet_name
        
        # Curb length
        curb_length = st.number_input(
            "Curb Length (feet)",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.parameters['subcatchment']['curb_length'],
            step=10.0,
            help="Total length of curbing (optional)"
        )
        st.session_state.parameters['subcatchment']['curb_length'] = curb_length
    
    # Validation display
    validation_messages = validate_parameters(st.session_state.parameters, 'subcatchment')
    if validation_messages:
        st.error("⚠️ **Validation Issues:**")
        for msg in validation_messages:
            st.error(f"• {msg}")

def surface_properties():
    st.header("Surface Properties")
    st.markdown("Configure surface characteristics including imperviousness and roughness coefficients.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Impervious Area Properties")
        
        # Percent impervious
        pct_impervious = st.slider(
            "% Impervious",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.parameters['surface']['pct_impervious'],
            step=1.0,
            help="Percentage of impervious area (0-100%)"
        )
        st.session_state.parameters['surface']['pct_impervious'] = pct_impervious
        
        # Manning's n for impervious areas
        n_imperv = st.number_input(
            "Manning's n - Impervious",
            min_value=0.01,
            max_value=0.10,
            value=st.session_state.parameters['surface']['n_imperv'],
            step=0.001,
            format="%.3f",
            help="Manning's roughness coefficient for impervious areas (typically 0.01-0.04)"
        )
        st.session_state.parameters['surface']['n_imperv'] = n_imperv
        
        # Depression storage for impervious areas
        dstore_imperv = st.number_input(
            "Depression Storage - Impervious (inches)",
            min_value=0.0,
            max_value=0.5,
            value=st.session_state.parameters['surface']['dstore_imperv'],
            step=0.01,
            format="%.3f",
            help="Depression storage depth for impervious areas"
        )
        st.session_state.parameters['surface']['dstore_imperv'] = dstore_imperv
        
        # Percent zero impervious
        pct_zero_imperv = st.slider(
            "% Zero Impervious",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.parameters['surface']['pct_zero_imperv'],
            step=1.0,
            help="Percentage of impervious area with zero depression storage"
        )
        st.session_state.parameters['surface']['pct_zero_imperv'] = pct_zero_imperv
    
    with col2:
        st.subheader("Pervious Area Properties")
        
        # Manning's n for pervious areas
        n_perv = st.number_input(
            "Manning's n - Pervious",
            min_value=0.05,
            max_value=1.0,
            value=st.session_state.parameters['surface']['n_perv'],
            step=0.01,
            format="%.3f",
            help="Manning's roughness coefficient for pervious areas (typically 0.10-0.80)"
        )
        st.session_state.parameters['surface']['n_perv'] = n_perv
        
        # Depression storage for pervious areas
        dstore_perv = st.number_input(
            "Depression Storage - Pervious (inches)",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.parameters['surface']['dstore_perv'],
            step=0.01,
            format="%.3f",
            help="Depression storage depth for pervious areas"
        )
        st.session_state.parameters['surface']['dstore_perv'] = dstore_perv
        
        # Subarea routing
        subarea_routing = st.selectbox(
            "Subarea Routing",
            ["OUTLET", "IMPERV", "PERV"],
            index=["OUTLET", "IMPERV", "PERV"].index(st.session_state.parameters['surface']['subarea_routing']),
            help="How pervious runoff routes to outlet"
        )
        st.session_state.parameters['surface']['subarea_routing'] = subarea_routing
    
    # Surface type suggestions
    st.subheader("Surface Type Recommendations")
    surface_type = st.selectbox(
        "Select Surface Type for Default Values",
        ["Custom", "Residential", "Commercial", "Industrial", "Forest", "Agricultural"],
        help="Apply typical values for different surface types"
    )
    
    if surface_type != "Custom":
        if st.button(f"Apply {surface_type} Defaults"):
            apply_surface_defaults(surface_type)
    
    # Validation display
    validation_messages = validate_parameters(st.session_state.parameters, 'surface')
    if validation_messages:
        st.error("⚠️ **Validation Issues:**")
        for msg in validation_messages:
            st.error(f"• {msg}")

def infiltration_parameters():
    st.header("Infiltration Parameters")
    st.markdown("Configure infiltration method and associated parameters.")
    
    # Infiltration method selection
    infiltration_method = st.selectbox(
        "Infiltration Method",
        ["Horton", "Green-Ampt", "Curve Number", "Modified Horton", "Modified Green-Ampt"],
        index=["Horton", "Green-Ampt", "Curve Number", "Modified Horton", "Modified Green-Ampt"].index(
            st.session_state.parameters['infiltration']['method']
        ),
        help="Select the infiltration calculation method"
    )
    st.session_state.parameters['infiltration']['method'] = infiltration_method
    
    # Method-specific parameters
    if infiltration_method == "Horton":
        horton_parameters()
    elif infiltration_method == "Green-Ampt":
        green_ampt_parameters()
    elif infiltration_method == "Curve Number":
        curve_number_parameters()
    elif infiltration_method == "Modified Horton":
        modified_horton_parameters()
    elif infiltration_method == "Modified Green-Ampt":
        modified_green_ampt_parameters()
    
    # Soil type recommendations
    st.subheader("Soil Type Recommendations")
    soil_type = st.selectbox(
        "Select Soil Type for Default Values",
        ["Custom", "Sand", "Loamy Sand", "Sandy Loam", "Loam", "Silt Loam", "Clay Loam", "Clay"],
        help="Apply typical infiltration values for different soil types"
    )
    
    if soil_type != "Custom":
        if st.button(f"Apply {soil_type} Defaults"):
            apply_soil_defaults(soil_type, infiltration_method)
    
    # Validation display
    validation_messages = validate_parameters(st.session_state.parameters, 'infiltration')
    if validation_messages:
        st.error("⚠️ **Validation Issues:**")
        for msg in validation_messages:
            st.error(f"• {msg}")

def horton_parameters():
    st.subheader("Horton Infiltration Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_rate = st.number_input(
            "Max Infiltration Rate (in/hr)",
            min_value=0.1,
            max_value=50.0,
            value=st.session_state.parameters['infiltration']['horton']['max_rate'],
            step=0.1,
            help="Maximum infiltration rate"
        )
        st.session_state.parameters['infiltration']['horton']['max_rate'] = max_rate
        
        min_rate = st.number_input(
            "Min Infiltration Rate (in/hr)",
            min_value=0.01,
            max_value=10.0,
            value=st.session_state.parameters['infiltration']['horton']['min_rate'],
            step=0.01,
            help="Minimum/final infiltration rate"
        )
        st.session_state.parameters['infiltration']['horton']['min_rate'] = min_rate
    
    with col2:
        decay_constant = st.number_input(
            "Decay Constant (1/hr)",
            min_value=0.1,
            max_value=20.0,
            value=st.session_state.parameters['infiltration']['horton']['decay_constant'],
            step=0.1,
            help="Rate of decrease from max to min rate"
        )
        st.session_state.parameters['infiltration']['horton']['decay_constant'] = decay_constant
        
        drying_time = st.number_input(
            "Drying Time (days)",
            min_value=1.0,
            max_value=30.0,
            value=st.session_state.parameters['infiltration']['horton']['drying_time'],
            step=1.0,
            help="Time for soil to dry after saturation"
        )
        st.session_state.parameters['infiltration']['horton']['drying_time'] = drying_time

def green_ampt_parameters():
    st.subheader("Green-Ampt Infiltration Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        suction_head = st.number_input(
            "Suction Head (inches)",
            min_value=0.5,
            max_value=20.0,
            value=st.session_state.parameters['infiltration']['green_ampt']['suction_head'],
            step=0.1,
            help="Soil capillary suction head"
        )
        st.session_state.parameters['infiltration']['green_ampt']['suction_head'] = suction_head
        
        conductivity = st.number_input(
            "Conductivity (in/hr)",
            min_value=0.01,
            max_value=10.0,
            value=st.session_state.parameters['infiltration']['green_ampt']['conductivity'],
            step=0.01,
            help="Saturated hydraulic conductivity"
        )
        st.session_state.parameters['infiltration']['green_ampt']['conductivity'] = conductivity
    
    with col2:
        initial_deficit = st.number_input(
            "Initial Deficit (fraction)",
            min_value=0.01,
            max_value=0.5,
            value=st.session_state.parameters['infiltration']['green_ampt']['initial_deficit'],
            step=0.01,
            help="Initial soil moisture deficit"
        )
        st.session_state.parameters['infiltration']['green_ampt']['initial_deficit'] = initial_deficit

def curve_number_parameters():
    st.subheader("Curve Number Infiltration Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        curve_number = st.number_input(
            "Curve Number",
            min_value=30,
            max_value=100,
            value=st.session_state.parameters['infiltration']['curve_number']['curve_number'],
            step=1,
            help="SCS curve number (30-100)"
        )
        st.session_state.parameters['infiltration']['curve_number']['curve_number'] = curve_number
        
        conductivity = st.number_input(
            "Conductivity (in/hr)",
            min_value=0.01,
            max_value=10.0,
            value=st.session_state.parameters['infiltration']['curve_number']['conductivity'],
            step=0.01,
            help="Saturated hydraulic conductivity"
        )
        st.session_state.parameters['infiltration']['curve_number']['conductivity'] = conductivity
    
    with col2:
        drying_time = st.number_input(
            "Drying Time (days)",
            min_value=1.0,
            max_value=30.0,
            value=st.session_state.parameters['infiltration']['curve_number']['drying_time'],
            step=1.0,
            help="Time for soil to dry after saturation"
        )
        st.session_state.parameters['infiltration']['curve_number']['drying_time'] = drying_time

def modified_horton_parameters():
    st.subheader("Modified Horton Infiltration Parameters")
    horton_parameters()
    
    max_volume = st.number_input(
        "Max Volume (inches)",
        min_value=0.1,
        max_value=10.0,
        value=st.session_state.parameters['infiltration']['modified_horton']['max_volume'],
        step=0.1,
        help="Maximum infiltration volume"
    )
    st.session_state.parameters['infiltration']['modified_horton']['max_volume'] = max_volume

def modified_green_ampt_parameters():
    st.subheader("Modified Green-Ampt Infiltration Parameters")
    green_ampt_parameters()
    
    redistribution_factor = st.number_input(
        "Redistribution Factor",
        min_value=0.1,
        max_value=2.0,
        value=st.session_state.parameters['infiltration']['modified_green_ampt']['redistribution_factor'],
        step=0.1,
        help="Soil moisture redistribution factor"
    )
    st.session_state.parameters['infiltration']['modified_green_ampt']['redistribution_factor'] = redistribution_factor

def climate_parameters():
    st.header("Climate Parameters")
    st.markdown("Configure evaporation and temperature data for the simulation.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evaporation")
        
        evap_method = st.selectbox(
            "Evaporation Method",
            ["Constant", "Monthly", "Time Series", "Temperature"],
            index=["Constant", "Monthly", "Time Series", "Temperature"].index(
                st.session_state.parameters['climate']['evap_method']
            ),
            help="Method for calculating evaporation"
        )
        st.session_state.parameters['climate']['evap_method'] = evap_method
        
        if evap_method == "Constant":
            evap_constant = st.number_input(
                "Evaporation Rate (in/day)",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.parameters['climate']['evap_constant'],
                step=0.01,
                help="Constant evaporation rate"
            )
            st.session_state.parameters['climate']['evap_constant'] = evap_constant
        
        elif evap_method == "Monthly":
            st.write("Monthly Evaporation Rates (in/day)")
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            monthly_evap = st.session_state.parameters['climate']['monthly_evap']
            for i, month in enumerate(months):
                monthly_evap[i] = st.number_input(
                    f"{month}",
                    min_value=0.0,
                    max_value=1.0,
                    value=monthly_evap[i],
                    step=0.01,
                    key=f"evap_{month}"
                )
        
        # Recovery factor
        recovery_factor = st.number_input(
            "Recovery Factor",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.parameters['climate']['recovery_factor'],
            step=0.01,
            help="Fraction of evaporation from dry surfaces"
        )
        st.session_state.parameters['climate']['recovery_factor'] = recovery_factor
    
    with col2:
        st.subheader("Temperature")
        
        temp_method = st.selectbox(
            "Temperature Method",
            ["None", "File", "Time Series"],
            index=["None", "File", "Time Series"].index(
                st.session_state.parameters['climate']['temp_method']
            ),
            help="Method for temperature data input"
        )
        st.session_state.parameters['climate']['temp_method'] = temp_method
        
        if temp_method != "None":
            wind_speed = st.number_input(
                "Wind Speed (mph)",
                min_value=0.0,
                max_value=50.0,
                value=st.session_state.parameters['climate']['wind_speed'],
                step=0.1,
                help="Average wind speed for evaporation calculations"
            )
            st.session_state.parameters['climate']['wind_speed'] = wind_speed
        
        # Snow parameters
        st.subheader("Snow Parameters (Optional)")
        
        snow_enabled = st.checkbox(
            "Enable Snow Modeling",
            value=st.session_state.parameters['climate']['snow_enabled'],
            help="Include snow accumulation and melting"
        )
        st.session_state.parameters['climate']['snow_enabled'] = snow_enabled
        
        if snow_enabled:
            snow_temp_threshold = st.number_input(
                "Snow Temperature Threshold (°F)",
                min_value=20.0,
                max_value=40.0,
                value=st.session_state.parameters['climate']['snow_temp_threshold'],
                step=1.0,
                help="Temperature threshold for snow/rain"
            )
            st.session_state.parameters['climate']['snow_temp_threshold'] = snow_temp_threshold
            
            snow_melt_coeff = st.number_input(
                "Snow Melt Coefficient",
                min_value=0.1,
                max_value=2.0,
                value=st.session_state.parameters['climate']['snow_melt_coeff'],
                step=0.1,
                help="Snow melt rate coefficient"
            )
            st.session_state.parameters['climate']['snow_melt_coeff'] = snow_melt_coeff
    
    # Validation display
    validation_messages = validate_parameters(st.session_state.parameters, 'climate')
    if validation_messages:
        st.error("⚠️ **Validation Issues:**")
        for msg in validation_messages:
            st.error(f"• {msg}")

def results_display():
    st.header("Simulation Results")
    
    if st.session_state.simulation_results is None:
        st.info("No simulation results available. Please run a simulation first.")
        return
    
    results = st.session_state.simulation_results
    
    # Results summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Peak Runoff",
            f"{results['peak_runoff']:.2f} cfs",
            help="Maximum runoff rate during simulation"
        )
    
    with col2:
        st.metric(
            "Total Volume",
            f"{results['total_volume']:.2f} acre-ft",
            help="Total runoff volume"
        )
    
    with col3:
        st.metric(
            "Peak Time",
            f"{results['peak_time']:.1f} min",
            help="Time to peak runoff"
        )
    
    with col4:
        st.metric(
            "Runoff Coefficient",
            f"{results['runoff_coefficient']:.3f}",
            help="Ratio of runoff to precipitation"
        )
    
    # Results visualization
    if 'time_series' in results:
        fig = create_results_plots(results)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results table
    st.subheader("Detailed Results")
    if 'detailed_results' in results:
        st.dataframe(results['detailed_results'])

def parameter_summary():
    st.header("Parameter Summary")
    st.markdown("Review all model parameters and their current values.")
    
    # Create parameter summary visualization
    fig = create_parameter_summary(st.session_state.parameters)
    st.plotly_chart(fig, use_container_width=True)
    
    # Parameter tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Subcatchment Parameters")
        subcatch_data = {
            'Parameter': ['Area', 'Width', 'Slope', 'Outlet Type', 'Outlet Name'],
            'Value': [
                f"{st.session_state.parameters['subcatchment']['area']} acres",
                f"{st.session_state.parameters['subcatchment']['width']} feet",
                f"{st.session_state.parameters['subcatchment']['slope']}%",
                st.session_state.parameters['subcatchment']['outlet_type'],
                st.session_state.parameters['subcatchment']['outlet_name']
            ]
        }
        st.dataframe(pd.DataFrame(subcatch_data))
        
        st.subheader("Surface Parameters")
        surface_data = {
            'Parameter': ['% Impervious', 'Manning n (Imperv)', 'Manning n (Perv)', 
                         'Dstore (Imperv)', 'Dstore (Perv)', 'Subarea Routing'],
            'Value': [
                f"{st.session_state.parameters['surface']['pct_impervious']}%",
                f"{st.session_state.parameters['surface']['n_imperv']:.3f}",
                f"{st.session_state.parameters['surface']['n_perv']:.3f}",
                f"{st.session_state.parameters['surface']['dstore_imperv']:.3f} in",
                f"{st.session_state.parameters['surface']['dstore_perv']:.3f} in",
                st.session_state.parameters['surface']['subarea_routing']
            ]
        }
        st.dataframe(pd.DataFrame(surface_data))
    
    with col2:
        st.subheader("Infiltration Parameters")
        method = st.session_state.parameters['infiltration']['method']
        infiltration_data = {'Parameter': ['Method'], 'Value': [method]}
        
        if method == 'Horton':
            infiltration_data['Parameter'].extend(['Max Rate', 'Min Rate', 'Decay Constant', 'Drying Time'])
            infiltration_data['Value'].extend([
                f"{st.session_state.parameters['infiltration']['horton']['max_rate']} in/hr",
                f"{st.session_state.parameters['infiltration']['horton']['min_rate']} in/hr",
                f"{st.session_state.parameters['infiltration']['horton']['decay_constant']} 1/hr",
                f"{st.session_state.parameters['infiltration']['horton']['drying_time']} days"
            ])
        
        st.dataframe(pd.DataFrame(infiltration_data))
        
        st.subheader("Climate Parameters")
        climate_data = {
            'Parameter': ['Evaporation Method', 'Recovery Factor', 'Temperature Method', 'Snow Enabled'],
            'Value': [
                st.session_state.parameters['climate']['evap_method'],
                f"{st.session_state.parameters['climate']['recovery_factor']:.2f}",
                st.session_state.parameters['climate']['temp_method'],
                'Yes' if st.session_state.parameters['climate']['snow_enabled'] else 'No'
            ]
        }
        st.dataframe(pd.DataFrame(climate_data))

def run_simulation():
    """Run SWMM5 simulation with current parameters."""
    try:
        with st.spinner("Running SWMM5 simulation..."):
            # Validate parameters first
            validation_messages = get_validation_messages(st.session_state.parameters)
            if validation_messages:
                st.error("Cannot run simulation with validation errors. Please fix the issues first.")
                return
            
            # Create and run simulation
            model = st.session_state.model
            model.create_input_file(st.session_state.parameters)
            results = model.run_simulation()
            
            st.session_state.simulation_results = results
            st.success("Simulation completed successfully!")
            
    except Exception as e:
        st.error(f"Simulation failed: {str(e)}")

def export_inp_file():
    """Export SWMM5 input file."""
    try:
        model = st.session_state.model
        inp_content = model.generate_inp_content(st.session_state.parameters)
        
        st.download_button(
            label="Download SWMM5 .inp File",
            data=inp_content,
            file_name=f"watershed_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.inp",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Export failed: {str(e)}")

def export_parameters_csv():
    """Export parameters as CSV file."""
    try:
        # Flatten parameters for CSV export
        flattened_params = []
        for category, params in st.session_state.parameters.items():
            if isinstance(params, dict):
                for key, value in params.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            flattened_params.append({
                                'Category': category,
                                'Parameter': f"{key}.{subkey}",
                                'Value': subvalue
                            })
                    else:
                        flattened_params.append({
                            'Category': category,
                            'Parameter': key,
                            'Value': value
                        })
        
        df = pd.DataFrame(flattened_params)
        csv_content = df.to_csv(index=False)
        
        st.download_button(
            label="Download Parameters CSV",
            data=csv_content,
            file_name=f"watershed_parameters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Export failed: {str(e)}")

def apply_surface_defaults(surface_type):
    """Apply default values for different surface types."""
    defaults = {
        'Residential': {
            'pct_impervious': 35.0,
            'n_imperv': 0.012,
            'n_perv': 0.15,
            'dstore_imperv': 0.05,
            'dstore_perv': 0.2
        },
        'Commercial': {
            'pct_impervious': 85.0,
            'n_imperv': 0.013,
            'n_perv': 0.20,
            'dstore_imperv': 0.06,
            'dstore_perv': 0.3
        },
        'Industrial': {
            'pct_impervious': 75.0,
            'n_imperv': 0.015,
            'n_perv': 0.25,
            'dstore_imperv': 0.08,
            'dstore_perv': 0.25
        },
        'Forest': {
            'pct_impervious': 5.0,
            'n_imperv': 0.011,
            'n_perv': 0.40,
            'dstore_imperv': 0.04,
            'dstore_perv': 0.5
        },
        'Agricultural': {
            'pct_impervious': 10.0,
            'n_imperv': 0.012,
            'n_perv': 0.30,
            'dstore_imperv': 0.05,
            'dstore_perv': 0.4
        }
    }
    
    if surface_type in defaults:
        for key, value in defaults[surface_type].items():
            st.session_state.parameters['surface'][key] = value
        st.success(f"Applied {surface_type} surface defaults")
        st.rerun()

def apply_soil_defaults(soil_type, infiltration_method):
    """Apply default infiltration values for different soil types."""
    # Soil type defaults for different infiltration methods
    defaults = {
        'Sand': {
            'Horton': {'max_rate': 8.0, 'min_rate': 0.5, 'decay_constant': 4.0, 'drying_time': 7},
            'Green-Ampt': {'suction_head': 2.0, 'conductivity': 5.0, 'initial_deficit': 0.4},
            'Curve Number': {'curve_number': 65, 'conductivity': 5.0, 'drying_time': 7}
        },
        'Loam': {
            'Horton': {'max_rate': 3.0, 'min_rate': 0.2, 'decay_constant': 2.0, 'drying_time': 14},
            'Green-Ampt': {'suction_head': 6.0, 'conductivity': 1.0, 'initial_deficit': 0.3},
            'Curve Number': {'curve_number': 75, 'conductivity': 1.0, 'drying_time': 14}
        },
        'Clay': {
            'Horton': {'max_rate': 1.0, 'min_rate': 0.05, 'decay_constant': 1.0, 'drying_time': 21},
            'Green-Ampt': {'suction_head': 12.0, 'conductivity': 0.2, 'initial_deficit': 0.2},
            'Curve Number': {'curve_number': 85, 'conductivity': 0.2, 'drying_time': 21}
        }
    }
    
    if soil_type in defaults and infiltration_method in defaults[soil_type]:
        method_key = infiltration_method.lower().replace('-', '_').replace(' ', '_')
        for key, value in defaults[soil_type][infiltration_method].items():
            st.session_state.parameters['infiltration'][method_key][key] = value
        st.success(f"Applied {soil_type} soil defaults for {infiltration_method}")
        st.rerun()

if __name__ == "__main__":
    main()
