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
from visualization import create_results_plots, create_parameter_summary, create_runoff_line_graph

# Set page configuration
st.set_page_config(
    page_title="SWMM5 Watershed Runoff Modeling",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for water-themed dark mode
st.markdown("""
<style>
    /* Water-themed background gradient */
    .stApp {
        background: linear-gradient(180deg, #0a1929 0%, #0d2847 30%, #0a3d62 60%, #1a5276 100%);
        background-attachment: fixed;
    }
    
    /* Animated water wave effect at bottom */
    .stApp::before {
        content: "";
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 150px;
        background: linear-gradient(180deg, transparent, rgba(0, 180, 216, 0.1));
        pointer-events: none;
        z-index: 0;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d2847 0%, #0a3d62 100%);
        border-right: 1px solid rgba(0, 180, 216, 0.3);
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #00b4d8 !important;
        text-shadow: 0 0 10px rgba(0, 180, 216, 0.3);
    }
    
    /* Card/container styling */
    [data-testid="stVerticalBlock"] > div {
        border-radius: 10px;
    }
    
    /* Input fields styling */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background-color: rgba(13, 40, 71, 0.8) !important;
        border: 1px solid rgba(0, 180, 216, 0.3) !important;
        color: #e0f7fa !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%);
        border: none;
        color: white;
        box-shadow: 0 4px 15px rgba(0, 180, 216, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0096c7 0%, #023e8a 100%);
        box-shadow: 0 6px 20px rgba(0, 180, 216, 0.5);
        transform: translateY(-2px);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(13, 40, 71, 0.5);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #90caf9;
        border-radius: 8px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 180, 216, 0.2) !important;
        color: #00b4d8 !important;
    }
    
    /* Slider styling */
    .stSlider > div > div > div > div {
        background-color: #00b4d8 !important;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background-color: rgba(0, 180, 136, 0.2);
        border: 1px solid #00b488;
    }
    
    .stError {
        background-color: rgba(255, 82, 82, 0.2);
        border: 1px solid #ff5252;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #00b4d8 !important;
    }
    
    /* DataFrame styling */
    .stDataFrame {
        background-color: rgba(13, 40, 71, 0.5);
        border-radius: 10px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(0, 180, 216, 0.1);
        border-radius: 8px;
    }
    
    /* Info box styling */
    .stInfo {
        background-color: rgba(0, 180, 216, 0.1);
        border: 1px solid rgba(0, 180, 216, 0.3);
    }
    
    /* Plotly chart background */
    .js-plotly-plot .plotly .bg {
        fill: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'model' not in st.session_state:
    st.session_state.model = SWMMModel()
if 'parameters' not in st.session_state:
    st.session_state.parameters = get_default_parameters()
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None
if 'validation_messages' not in st.session_state:
    st.session_state.validation_messages = []
if 'auto_run_done' not in st.session_state:
    st.session_state.auto_run_done = False

def main():
    st.title("🌊 SWMM5 Watershed Runoff Modeling Application")
    st.markdown("*Comprehensive parameter input, validation, and simulation capabilities*")
    
    # Auto-run simulation on first load with default parameters
    if not st.session_state.auto_run_done:
        with st.spinner('Running initial simulation with default parameters...'):
            try:
                model = st.session_state.model
                model.create_input_file(st.session_state.parameters)
                results = model.run_simulation()
                st.session_state.simulation_results = results
                st.session_state.auto_run_done = True
            except Exception as e:
                st.session_state.auto_run_done = True  # Prevent infinite loop
                st.error(f"Initial simulation failed: {str(e)}")
    
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
        st.header("📥 Export Options")
        
        with st.expander("Export Files", expanded=True):
            st.markdown("**Native SWMM Format**")
            if st.button("📥 Download SWMM .INP File", key="export_inp"):
                export_inp_file()
            
            st.markdown("**Civil 3D Compatible**")
            if st.button("🗺️ Export to LandXML", key="export_landxml"):
                export_landxml()
            
            st.markdown("**Spreadsheet Analysis**")
            if st.button("📊 Download Results CSV", key="export_results_csv"):
                export_results_csv()
            
            if st.button("📄 Download Parameters CSV", key="export_params_csv"):
                export_parameters_csv()
            
            st.markdown("**Documentation**")
            if st.button("📋 Generate PDF Report", key="export_pdf"):
                export_pdf_report()
        
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📍 Subcatchments", 
        "🏞️ Surface Properties", 
        "💧 Infiltration", 
        "🌡️ Climate Data",
        "🌿 LID Controls",
        "📊 LID Usage",
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
        lid_controls_parameters()
    
    with tab6:
        lid_usage_parameters()
    
    with tab7:
        results_display()
    
    with tab8:
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
        st.info("No simulation results available. Click 'Run Simulation' in the sidebar to generate results.")
        
        # Add a prominent button to run simulation
        if st.button("🚀 Run Simulation Now", type="primary"):
            run_simulation()
            st.rerun()
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
    st.subheader("Runoff Hydrograph")
    if 'time_series' in results:
        # Create the main runoff line graph
        runoff_fig = create_runoff_line_graph(results)
        st.plotly_chart(runoff_fig, use_container_width=True)
        
        # Option to show comprehensive plots
        if st.checkbox("Show Detailed Analysis Plots"):
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

def export_landxml():
    """Export watershed data to LandXML format for Civil 3D compatibility."""
    try:
        params = st.session_state.parameters
        timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        # Create LandXML content
        landxml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<LandXML xmlns="http://www.landxml.org/schema/LandXML-1.2" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.landxml.org/schema/LandXML-1.2 http://www.landxml.org/schema/LandXML-1.2/LandXML-1.2.xsd"
         date="{datetime.now().strftime('%Y-%m-%d')}" 
         time="{datetime.now().strftime('%H:%M:%S')}"
         version="1.2">
  <Units>
    <Imperial areaUnit="acre" linearUnit="foot" volumeUnit="cubicFeet" 
              flowUnit="cubicFeetPerSecond" temperatureUnit="fahrenheit"/>
  </Units>
  <Project name="SWMM5 Watershed Model">
    <Feature code="SWMM5Export" source="SWMM5 Modeling Application">
      <Property label="ExportDate" value="{timestamp}"/>
      <Property label="Application" value="SWMM5 Watershed Runoff Modeling"/>
    </Feature>
  </Project>
  <Watersheds>
    <Watershed name="Subcatchment_1" area="{params['subcatchment']['area']}" 
               desc="SWMM5 Subcatchment Export">
      <Outlet refName="{params['subcatchment']['outlet_name']}" 
              outletType="{params['subcatchment']['outlet_type']}"/>
      <Watershed name="Contributing_Area">
        <WatershedCatchment area="{params['subcatchment']['area']}" 
                           width="{params['subcatchment']['width']}"
                           slope="{params['subcatchment']['slope']}">
          <SurfaceProperties>
            <Property label="PercentImpervious" value="{params['surface']['pct_impervious']}"/>
            <Property label="ManningsN_Impervious" value="{params['surface']['n_imperv']}"/>
            <Property label="ManningsN_Pervious" value="{params['surface']['n_perv']}"/>
            <Property label="DepressionStorage_Impervious" value="{params['surface']['dstore_imperv']}"/>
            <Property label="DepressionStorage_Pervious" value="{params['surface']['dstore_perv']}"/>
          </SurfaceProperties>
          <InfiltrationProperties>
            <Property label="Method" value="{params['infiltration']['method']}"/>
          </InfiltrationProperties>
        </WatershedCatchment>
      </Watershed>
    </Watershed>
  </Watersheds>
  <PipeNetworks>
    <PipeNetwork name="Storm_Drainage_System" desc="SWMM5 Drainage Network">
      <Structs>
        <Struct name="{params['subcatchment']['outlet_name']}" 
                desc="Outlet Node" structType="outfall">
          <Feature code="SWMM_Outlet"/>
        </Struct>
      </Structs>
    </PipeNetwork>
  </PipeNetworks>
</LandXML>'''
        
        st.download_button(
            label="Download LandXML File",
            data=landxml_content,
            file_name=f"watershed_landxml_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml",
            mime="application/xml"
        )
        st.success("LandXML file ready for download!")
        
    except Exception as e:
        st.error(f"LandXML export failed: {str(e)}")

def export_results_csv():
    """Export simulation results as CSV file."""
    try:
        results = st.session_state.simulation_results
        
        if results is None:
            st.warning("No simulation results available. Please run a simulation first.")
            return
        
        # Create results DataFrame
        results_data = []
        
        # Add time series data if available
        if 'time_series' in results:
            for i, time_point in enumerate(results['time_series'].get('time', [])):
                row = {'Time (min)': time_point}
                if 'runoff' in results['time_series']:
                    row['Runoff (cfs)'] = results['time_series']['runoff'][i] if i < len(results['time_series']['runoff']) else ''
                if 'infiltration' in results['time_series']:
                    row['Infiltration (in/hr)'] = results['time_series']['infiltration'][i] if i < len(results['time_series']['infiltration']) else ''
                if 'evaporation' in results['time_series']:
                    row['Evaporation (in/day)'] = results['time_series']['evaporation'][i] if i < len(results['time_series']['evaporation']) else ''
                results_data.append(row)
        
        if results_data:
            df = pd.DataFrame(results_data)
            csv_content = df.to_csv(index=False)
            
            st.download_button(
                label="Download Results CSV",
                data=csv_content,
                file_name=f"simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            st.success("Results CSV ready for download!")
        else:
            # Create summary results if no time series
            summary_data = []
            if 'summary' in results:
                for key, value in results['summary'].items():
                    summary_data.append({'Metric': key, 'Value': value})
            
            if summary_data:
                df = pd.DataFrame(summary_data)
                csv_content = df.to_csv(index=False)
                
                st.download_button(
                    label="Download Results Summary CSV",
                    data=csv_content,
                    file_name=f"results_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                st.success("Results summary CSV ready for download!")
            else:
                st.warning("No results data available to export.")
        
    except Exception as e:
        st.error(f"Results CSV export failed: {str(e)}")

def export_pdf_report():
    """Generate PDF report of model parameters and results."""
    try:
        from fpdf import FPDF
        
        params = st.session_state.parameters
        results = st.session_state.simulation_results
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Helvetica', 'B', 20)
        pdf.set_text_color(0, 102, 153)
        pdf.cell(0, 15, 'SWMM5 Watershed Runoff Model Report', ln=True, align='C')
        
        # Subtitle
        pdf.set_font('Helvetica', '', 12)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
        pdf.ln(10)
        
        # Subcatchment Parameters Section
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(0, 80, 120)
        pdf.cell(0, 10, '1. Subcatchment Parameters', ln=True)
        pdf.set_draw_color(0, 180, 216)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, f"Area: {params['subcatchment']['area']} acres", ln=True)
        pdf.cell(0, 7, f"Width: {params['subcatchment']['width']} feet", ln=True)
        pdf.cell(0, 7, f"Slope: {params['subcatchment']['slope']}%", ln=True)
        pdf.cell(0, 7, f"Outlet: {params['subcatchment']['outlet_name']} ({params['subcatchment']['outlet_type']})", ln=True)
        pdf.ln(5)
        
        # Surface Properties Section
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(0, 80, 120)
        pdf.cell(0, 10, '2. Surface Properties', ln=True)
        pdf.set_draw_color(0, 180, 216)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, f"Percent Impervious: {params['surface']['pct_impervious']}%", ln=True)
        pdf.cell(0, 7, f"Manning's n (Impervious): {params['surface']['n_imperv']}", ln=True)
        pdf.cell(0, 7, f"Manning's n (Pervious): {params['surface']['n_perv']}", ln=True)
        pdf.cell(0, 7, f"Depression Storage (Impervious): {params['surface']['dstore_imperv']} inches", ln=True)
        pdf.cell(0, 7, f"Depression Storage (Pervious): {params['surface']['dstore_perv']} inches", ln=True)
        pdf.ln(5)
        
        # Infiltration Parameters Section
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(0, 80, 120)
        pdf.cell(0, 10, '3. Infiltration Parameters', ln=True)
        pdf.set_draw_color(0, 180, 216)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, f"Method: {params['infiltration']['method']}", ln=True)
        
        # Method-specific parameters
        method = params['infiltration']['method'].lower().replace(' ', '_').replace('-', '_')
        if 'horton' in method and 'horton' in params['infiltration']:
            pdf.cell(0, 7, f"Max Rate: {params['infiltration']['horton']['max_rate']} in/hr", ln=True)
            pdf.cell(0, 7, f"Min Rate: {params['infiltration']['horton']['min_rate']} in/hr", ln=True)
            pdf.cell(0, 7, f"Decay Constant: {params['infiltration']['horton']['decay_constant']} 1/hr", ln=True)
        elif 'green' in method and 'green_ampt' in params['infiltration']:
            pdf.cell(0, 7, f"Suction Head: {params['infiltration']['green_ampt']['suction_head']} inches", ln=True)
            pdf.cell(0, 7, f"Conductivity: {params['infiltration']['green_ampt']['conductivity']} in/hr", ln=True)
        elif 'curve' in method and 'curve_number' in params['infiltration']:
            pdf.cell(0, 7, f"Curve Number: {params['infiltration']['curve_number']['curve_number']}", ln=True)
        pdf.ln(5)
        
        # LID Controls Section (if enabled)
        if params.get('lid_controls', {}).get('enabled', False):
            pdf.set_font('Helvetica', 'B', 14)
            pdf.set_text_color(0, 80, 120)
            pdf.cell(0, 10, '4. LID Controls', ln=True)
            pdf.set_draw_color(0, 180, 216)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            
            pdf.set_font('Helvetica', '', 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 7, "LID Controls: Enabled", ln=True)
            
            # List configured LID types
            lid_types = {
                'bio_retention': 'Bio-retention Cell',
                'green_roof': 'Green Roof',
                'infiltration_trench': 'Infiltration Trench',
                'permeable_pavement': 'Permeable Pavement',
                'rain_barrel': 'Rain Barrel',
                'vegetative_swale': 'Vegetative Swale',
                'rain_garden': 'Rain Garden',
                'rooftop_disconnection': 'Rooftop Disconnection'
            }
            for lid_key, lid_name in lid_types.items():
                if lid_key in params.get('lid_controls', {}):
                    pdf.cell(0, 7, f"  - {lid_name}: Configured", ln=True)
            pdf.ln(5)
        
        # Simulation Results Section
        if results:
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.set_text_color(0, 80, 120)
            pdf.cell(0, 10, '5. Simulation Results Summary', ln=True)
            pdf.set_draw_color(0, 180, 216)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            
            pdf.set_font('Helvetica', '', 11)
            pdf.set_text_color(0, 0, 0)
            
            if 'summary' in results:
                for key, value in results['summary'].items():
                    clean_key = key.replace('_', ' ').title()
                    pdf.cell(0, 7, f"{clean_key}: {value}", ln=True)
            
            if 'peak_runoff' in results:
                pdf.cell(0, 7, f"Peak Runoff: {results['peak_runoff']:.4f} cfs", ln=True)
            if 'total_runoff' in results:
                pdf.cell(0, 7, f"Total Runoff Volume: {results['total_runoff']:.4f} acre-ft", ln=True)
            if 'runoff_coefficient' in results:
                pdf.cell(0, 7, f"Runoff Coefficient: {results['runoff_coefficient']:.3f}", ln=True)
        
        # Footer
        pdf.set_y(-30)
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 10, 'Generated by SWMM5 Watershed Runoff Modeling Application', align='C')
        
        # Generate PDF bytes
        pdf_output = pdf.output()
        
        st.download_button(
            label="Download PDF Report",
            data=bytes(pdf_output),
            file_name=f"swmm5_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )
        st.success("PDF report ready for download!")
        
    except Exception as e:
        st.error(f"PDF report generation failed: {str(e)}")

def lid_controls_parameters():
    """LID Controls configuration interface."""
    st.header("🌿 LID Controls Configuration")
    st.markdown("Configure Low Impact Development (LID) controls for green infrastructure modeling.")
    
    # Import LID helper functions
    from parameter_defaults import get_lid_type_defaults, get_lid_layer_definitions
    
    # Enable/disable LID controls
    lid_enabled = st.checkbox(
        "Enable LID Controls",
        value=st.session_state.parameters.get('lid_controls', {}).get('enabled', False),
        help="Enable LID controls for green infrastructure modeling"
    )
    st.session_state.parameters['lid_controls']['enabled'] = lid_enabled
    
    if not lid_enabled:
        st.info("LID controls are disabled. Enable them to configure green infrastructure practices.")
        return
    
    # Get available LID types
    lid_types = get_lid_type_defaults()
    layer_definitions = get_lid_layer_definitions()
    
    # Select LID type to configure
    selected_lid = st.selectbox(
        "Select LID Type to Configure",
        options=list(lid_types.keys()),
        format_func=lambda x: lid_types[x],
        help="Choose the LID type to configure parameters for"
    )
    
    st.subheader(f"Configure {lid_types[selected_lid]}")
    
    # Display layer information
    st.info(f"**Layers for {lid_types[selected_lid]}:**")
    for layer, description in layer_definitions[selected_lid].items():
        st.write(f"• **{layer.title()}**: {description}")
    
    # Configure parameters for selected LID type
    lid_params = st.session_state.parameters['lid_controls'][selected_lid]
    
    # Surface layer (common to all LID types)
    if 'surface' in lid_params:
        with st.expander("Surface Layer Parameters", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                berm_height = st.number_input(
                    "Berm Height (inches)",
                    min_value=0.0,
                    max_value=12.0,
                    value=lid_params['surface']['berm_height'],
                    step=0.5,
                    help="Maximum ponding depth before overflow"
                )
                lid_params['surface']['berm_height'] = berm_height
                
                vegetation_volume = st.number_input(
                    "Vegetation Volume Fraction",
                    min_value=0.0,
                    max_value=0.3,
                    value=lid_params['surface']['vegetation_volume'],
                    step=0.01,
                    help="Volume occupied by stems and leaves"
                )
                lid_params['surface']['vegetation_volume'] = vegetation_volume
            
            with col2:
                surface_roughness = st.number_input(
                    "Surface Roughness (Manning's n)",
                    min_value=0.01,
                    max_value=0.4,
                    value=lid_params['surface']['surface_roughness'],
                    step=0.01,
                    help="Manning's roughness coefficient"
                )
                lid_params['surface']['surface_roughness'] = surface_roughness
                
                surface_slope = st.number_input(
                    "Surface Slope (%)",
                    min_value=0.0,
                    max_value=10.0,
                    value=lid_params['surface']['surface_slope'],
                    step=0.1,
                    help="Surface slope for drainage"
                )
                lid_params['surface']['surface_slope'] = surface_slope
                
                # Side slope for vegetative swales
                if selected_lid == 'vegetative_swale':
                    side_slope = st.number_input(
                        "Side Slope (%)",
                        min_value=10.0,
                        max_value=100.0,
                        value=lid_params['surface']['side_slope'],
                        step=1.0,
                        help="Side slope of trapezoidal cross-section"
                    )
                    lid_params['surface']['side_slope'] = side_slope
    
    # Soil layer (for applicable LID types)
    if 'soil' in lid_params:
        with st.expander("Soil Layer Parameters", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                thickness = st.number_input(
                    "Soil Thickness (inches)",
                    min_value=2.0,
                    max_value=48.0,
                    value=lid_params['soil']['thickness'],
                    step=1.0,
                    help="Depth of soil layer"
                )
                lid_params['soil']['thickness'] = thickness
                
                porosity = st.number_input(
                    "Porosity",
                    min_value=0.3,
                    max_value=0.7,
                    value=lid_params['soil']['porosity'],
                    step=0.01,
                    help="Total void volume fraction"
                )
                lid_params['soil']['porosity'] = porosity
                
                field_capacity = st.number_input(
                    "Field Capacity",
                    min_value=0.05,
                    max_value=0.4,
                    value=lid_params['soil']['field_capacity'],
                    step=0.01,
                    help="Moisture content after drainage"
                )
                lid_params['soil']['field_capacity'] = field_capacity
            
            with col2:
                wilting_point = st.number_input(
                    "Wilting Point",
                    min_value=0.01,
                    max_value=0.2,
                    value=lid_params['soil']['wilting_point'],
                    step=0.01,
                    help="Minimum moisture for plant survival"
                )
                lid_params['soil']['wilting_point'] = wilting_point
                
                conductivity = st.number_input(
                    "Conductivity (in/hr)",
                    min_value=0.1,
                    max_value=10.0,
                    value=lid_params['soil']['conductivity'],
                    step=0.1,
                    help="Saturated hydraulic conductivity"
                )
                lid_params['soil']['conductivity'] = conductivity
                
                conductivity_slope = st.number_input(
                    "Conductivity Slope",
                    min_value=1.0,
                    max_value=30.0,
                    value=lid_params['soil']['conductivity_slope'],
                    step=1.0,
                    help="Slope of log(conductivity) vs moisture curve"
                )
                lid_params['soil']['conductivity_slope'] = conductivity_slope
                
                suction_head = st.number_input(
                    "Suction Head (inches)",
                    min_value=1.0,
                    max_value=20.0,
                    value=lid_params['soil']['suction_head'],
                    step=0.5,
                    help="Green-Ampt suction head parameter"
                )
                lid_params['soil']['suction_head'] = suction_head
    
    # Pavement layer (for permeable pavement)
    if 'pavement' in lid_params:
        with st.expander("Pavement Layer Parameters", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                thickness = st.number_input(
                    "Pavement Thickness (inches)",
                    min_value=2.0,
                    max_value=8.0,
                    value=lid_params['pavement']['thickness'],
                    step=0.5,
                    help="Thickness of porous pavement"
                )
                lid_params['pavement']['thickness'] = thickness
                
                void_ratio = st.number_input(
                    "Void Ratio",
                    min_value=0.1,
                    max_value=0.3,
                    value=lid_params['pavement']['void_ratio'],
                    step=0.01,
                    help="Volume of voids relative to solids"
                )
                lid_params['pavement']['void_ratio'] = void_ratio
            
            with col2:
                impervious_fraction = st.number_input(
                    "Impervious Surface Fraction",
                    min_value=0.0,
                    max_value=0.5,
                    value=lid_params['pavement']['impervious_fraction'],
                    step=0.01,
                    help="Ratio of impervious material"
                )
                lid_params['pavement']['impervious_fraction'] = impervious_fraction
                
                permeability = st.number_input(
                    "Permeability (in/hr)",
                    min_value=10.0,
                    max_value=1000.0,
                    value=lid_params['pavement']['permeability'],
                    step=10.0,
                    help="Hydraulic conductivity of pavement"
                )
                lid_params['pavement']['permeability'] = permeability
                
                clogging_factor = st.number_input(
                    "Clogging Factor",
                    min_value=0.0,
                    max_value=1000.0,
                    value=lid_params['pavement']['clogging_factor'],
                    step=10.0,
                    help="Pavement volumes treated before full clogging"
                )
                lid_params['pavement']['clogging_factor'] = clogging_factor
    
    # Storage layer (for applicable LID types)
    if 'storage' in lid_params:
        with st.expander("Storage Layer Parameters", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                thickness = st.number_input(
                    "Storage Thickness (inches)",
                    min_value=6.0,
                    max_value=48.0,
                    value=lid_params['storage']['thickness'],
                    step=1.0,
                    help="Depth of storage/gravel layer"
                )
                lid_params['storage']['thickness'] = thickness
                
                void_ratio = st.number_input(
                    "Storage Void Ratio",
                    min_value=0.3,
                    max_value=0.7,
                    value=lid_params['storage']['void_ratio'],
                    step=0.01,
                    help="Volume of voids relative to solids"
                )
                lid_params['storage']['void_ratio'] = void_ratio
            
            with col2:
                seepage_rate = st.number_input(
                    "Seepage Rate (in/hr)",
                    min_value=0.0,
                    max_value=5.0,
                    value=lid_params['storage']['seepage_rate'],
                    step=0.1,
                    help="Infiltration rate into native soil"
                )
                lid_params['storage']['seepage_rate'] = seepage_rate
                
                clogging_factor = st.number_input(
                    "Storage Clogging Factor",
                    min_value=0.0,
                    max_value=1000.0,
                    value=lid_params['storage']['clogging_factor'],
                    step=10.0,
                    help="Storage volumes treated before clogging"
                )
                lid_params['storage']['clogging_factor'] = clogging_factor
    
    # Drainage mat layer (for green roofs)
    if 'drainage_mat' in lid_params:
        with st.expander("Drainage Mat Parameters", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                thickness = st.number_input(
                    "Drainage Mat Thickness (inches)",
                    min_value=0.5,
                    max_value=3.0,
                    value=lid_params['drainage_mat']['thickness'],
                    step=0.1,
                    help="Thickness of drainage mat"
                )
                lid_params['drainage_mat']['thickness'] = thickness
                
                void_fraction = st.number_input(
                    "Void Fraction",
                    min_value=0.3,
                    max_value=0.7,
                    value=lid_params['drainage_mat']['void_fraction'],
                    step=0.01,
                    help="Ratio of void volume to total volume"
                )
                lid_params['drainage_mat']['void_fraction'] = void_fraction
            
            with col2:
                roughness = st.number_input(
                    "Roughness (Manning's n)",
                    min_value=0.05,
                    max_value=0.4,
                    value=lid_params['drainage_mat']['roughness'],
                    step=0.01,
                    help="Manning's n for horizontal flow"
                )
                lid_params['drainage_mat']['roughness'] = roughness
                
                initial_moisture = st.number_input(
                    "Initial Moisture Content",
                    min_value=0.0,
                    max_value=1.0,
                    value=lid_params['drainage_mat']['initial_moisture'],
                    step=0.01,
                    help="Initial moisture content"
                )
                lid_params['drainage_mat']['initial_moisture'] = initial_moisture
    
    # Drain layer (for applicable LID types)
    if 'drain' in lid_params:
        with st.expander("Underdrain Parameters", expanded=False):
            enable_drain = st.checkbox(
                "Enable Underdrain System",
                value=lid_params['drain']['drain_coefficient'] > 0,
                help="Enable underdrain system for this LID control"
            )
            
            if enable_drain:
                col1, col2 = st.columns(2)
                
                with col1:
                    drain_coefficient = st.number_input(
                        "Drain Coefficient",
                        min_value=0.1,
                        max_value=10.0,
                        value=max(0.1, lid_params['drain']['drain_coefficient']),
                        step=0.1,
                        help="Flow coefficient for power function"
                    )
                    lid_params['drain']['drain_coefficient'] = drain_coefficient
                    
                    drain_exponent = st.number_input(
                        "Drain Exponent",
                        min_value=0.1,
                        max_value=2.0,
                        value=lid_params['drain']['drain_exponent'],
                        step=0.1,
                        help="Exponent in power function (0.5 for orifice)"
                    )
                    lid_params['drain']['drain_exponent'] = drain_exponent
                
                with col2:
                    offset_height = st.number_input(
                        "Offset Height (inches)",
                        min_value=0.0,
                        max_value=12.0,
                        value=lid_params['drain']['offset_height'],
                        step=0.5,
                        help="Distance above storage layer bottom"
                    )
                    lid_params['drain']['offset_height'] = offset_height
                    
                    delay = st.number_input(
                        "Delay (hours)",
                        min_value=0.0,
                        max_value=24.0,
                        value=lid_params['drain']['delay'],
                        step=0.5,
                        help="Time to drain system after rainfall ends"
                    )
                    lid_params['drain']['delay'] = delay
            else:
                lid_params['drain']['drain_coefficient'] = 0.0

def lid_usage_parameters():
    """LID Usage configuration interface."""
    st.header("📊 LID Usage Configuration")
    st.markdown("Configure how LID controls are applied to subcatchments.")
    
    # Check if LID controls are enabled
    if not st.session_state.parameters.get('lid_controls', {}).get('enabled', False):
        st.warning("LID controls must be enabled first. Please enable them in the LID Controls tab.")
        return
    
    # Enable/disable LID usage
    lid_usage_enabled = st.checkbox(
        "Enable LID Usage",
        value=st.session_state.parameters.get('lid_usage', {}).get('enabled', False),
        help="Enable LID usage to apply LID controls to subcatchments"
    )
    st.session_state.parameters['lid_usage']['enabled'] = lid_usage_enabled
    
    if not lid_usage_enabled:
        st.info("LID usage is disabled. Enable it to apply LID controls to subcatchments.")
        return
    
    # Get available LID types
    from parameter_defaults import get_lid_type_defaults
    lid_types = get_lid_type_defaults()
    
    # Current assignments
    assignments = st.session_state.parameters['lid_usage']['subcatchment_assignments']
    
    st.subheader("Subcatchment LID Assignments")
    
    # Add new assignment
    with st.expander("Add New LID Assignment", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subcatch_id = st.text_input(
                "Subcatchment ID",
                value="S1",
                help="ID of the subcatchment to apply LID to"
            )
            
            lid_type = st.selectbox(
                "LID Type",
                options=list(lid_types.keys()),
                format_func=lambda x: lid_types[x],
                help="Type of LID control to apply"
            )
        
        with col2:
            number_replicate = st.number_input(
                "Number of Replicates",
                min_value=1,
                max_value=100,
                value=1,
                help="Number of replicate LID units"
            )
            
            area = st.number_input(
                "Area (sq ft)",
                min_value=100.0,
                max_value=10000.0,
                value=1000.0,
                step=100.0,
                help="Area of each LID unit"
            )
        
        with col3:
            width = st.number_input(
                "Width (ft)",
                min_value=10.0,
                max_value=200.0,
                value=50.0,
                step=5.0,
                help="Width of LID unit"
            )
            
            initial_saturation = st.number_input(
                "Initial Saturation (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=5.0,
                help="Initial saturation of LID unit"
            )
        
        # Flow routing parameters
        col4, col5 = st.columns(2)
        
        with col4:
            from_imperv = st.number_input(
                "From Impervious (%)",
                min_value=0.0,
                max_value=100.0,
                value=100.0,
                step=5.0,
                help="Percent of impervious area runoff treated"
            )
            
            to_perv = st.number_input(
                "To Pervious (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=5.0,
                help="Percent of LID outflow sent to pervious area"
            )
        
        with col5:
            drain_to = st.text_input(
                "Drain To",
                value="",
                help="Node or subcatchment to receive underdrain flow (optional)"
            )
            
            drain_subcatch = st.text_input(
                "Drain Subcatchment",
                value="",
                help="Subcatchment receiving underdrain flow (optional)"
            )
        
        if st.button("Add LID Assignment"):
            assignments[subcatch_id] = {
                'lid_type': lid_type,
                'number_replicate': number_replicate,
                'area': area,
                'width': width,
                'initial_saturation': initial_saturation / 100.0,
                'from_imperv': from_imperv,
                'to_perv': to_perv,
                'report_file': '',
                'drain_to': drain_to if drain_to else '',
                'drain_subcatch': drain_subcatch if drain_subcatch else ''
            }
            st.success(f"Added LID assignment for subcatchment {subcatch_id}")
            st.rerun()
    
    # Display current assignments
    if assignments:
        st.subheader("Current LID Assignments")
        
        for subcatch_id, assignment in assignments.items():
            with st.expander(f"Subcatchment {subcatch_id} - {lid_types[assignment['lid_type']]}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**LID Type:** {lid_types[assignment['lid_type']]}")
                    st.write(f"**Number of Units:** {assignment['number_replicate']}")
                    st.write(f"**Area:** {assignment['area']:.0f} sq ft")
                
                with col2:
                    st.write(f"**Width:** {assignment['width']:.0f} ft")
                    st.write(f"**Initial Saturation:** {assignment['initial_saturation']*100:.1f}%")
                    st.write(f"**From Impervious:** {assignment['from_imperv']:.1f}%")
                
                with col3:
                    st.write(f"**To Pervious:** {assignment['to_perv']:.1f}%")
                    if assignment['drain_to']:
                        st.write(f"**Drain To:** {assignment['drain_to']}")
                    if assignment['drain_subcatch']:
                        st.write(f"**Drain Subcatchment:** {assignment['drain_subcatch']}")
                
                if st.button(f"Remove Assignment", key=f"remove_{subcatch_id}"):
                    del assignments[subcatch_id]
                    st.success(f"Removed LID assignment for subcatchment {subcatch_id}")
                    st.rerun()
    else:
        st.info("No LID assignments configured. Add assignments above to apply LID controls to subcatchments.")

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
