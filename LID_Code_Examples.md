# LID Implementation Code Examples

## 1. LID Controls Parameter Interface (app.py)

### Main LID Controls Function
```python
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
    
    # Configure parameters for selected LID type
    lid_params = st.session_state.parameters['lid_controls'][selected_lid]
    
    # Surface layer configuration example
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
```

### LID Usage Configuration Function
```python
def lid_usage_parameters():
    """LID Usage configuration interface."""
    st.header("📊 LID Usage Configuration")
    st.markdown("Configure how LID controls are applied to subcatchments.")
    
    # Check if LID controls are enabled
    if not st.session_state.parameters.get('lid_controls', {}).get('enabled', False):
        st.warning("LID controls must be enabled first. Please enable them in the LID Controls tab.")
        return
    
    # Add new assignment interface
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
        
        if st.button("Add LID Assignment"):
            assignments[subcatch_id] = {
                'lid_type': lid_type,
                'number_replicate': number_replicate,
                'area': area,
                'width': width,
                'initial_saturation': initial_saturation / 100.0,
                'from_imperv': from_imperv,
                'to_perv': to_perv,
                'drain_to': drain_to if drain_to else '',
                'drain_subcatch': drain_subcatch if drain_subcatch else ''
            }
            st.success(f"Added LID assignment for subcatchment {subcatch_id}")
            st.rerun()
```

## 2. LID Type Definitions (parameter_defaults.py)

### LID Type Dictionary
```python
def get_lid_type_defaults() -> Dict[str, str]:
    """Get available LID control types and their descriptions."""
    return {
        'bioretention_cell': 'Bio-retention Cell - Vegetated depression with filtration',
        'green_roof': 'Green Roof - Vegetated roof system with drainage',
        'infiltration_trench': 'Infiltration Trench - Gravel-filled trench for infiltration',
        'permeable_pavement': 'Permeable Pavement - Porous paving with gravel storage',
        'rain_barrel': 'Rain Barrel - Container for roof runoff collection',
        'vegetative_swale': 'Vegetative Swale - Grass-lined channel for conveyance',
        'rain_garden': 'Rain Garden - Shallow depression with vegetation',
        'rooftop_disconnection': 'Rooftop Disconnection - Redirect roof runoff to landscaping'
    }
```

### Layer Definitions
```python
def get_lid_layer_definitions() -> Dict[str, Dict[str, str]]:
    """Get layer definitions for each LID type."""
    return {
        'bioretention_cell': {
            'surface': 'Surface layer with ponding and vegetation',
            'soil': 'Engineered soil layer for filtration',
            'storage': 'Gravel storage layer for temporary storage',
            'drain': 'Optional underdrain system'
        },
        'green_roof': {
            'surface': 'Surface layer with vegetation',
            'soil': 'Growing medium layer',
            'drainage_mat': 'Drainage layer for water removal'
        },
        'permeable_pavement': {
            'surface': 'Surface layer',
            'pavement': 'Porous pavement layer',
            'storage': 'Gravel storage layer',
            'drain': 'Optional underdrain system'
        }
        # ... more layer definitions
    }
```

## 3. LID Validation Functions (validation.py)

### LID Controls Validation
```python
def validate_lid_controls(params: Dict[str, Any]) -> List[str]:
    """Validate LID controls parameters."""
    messages = []
    
    if not params.get('enabled', False):
        return messages  # Skip validation if LID controls are disabled
    
    # Validate each LID type
    for lid_type, lid_params in params.items():
        if lid_type == 'enabled' or not isinstance(lid_params, dict):
            continue
            
        # Surface layer validation
        if 'surface' in lid_params:
            surface = lid_params['surface']
            
            berm_height = surface.get('berm_height', 0)
            if berm_height < 0 or berm_height > 12:
                messages.append(f"{lid_type}: Berm height should be between 0 and 12 inches")
            
            vegetation_volume = surface.get('vegetation_volume', 0)
            if vegetation_volume < 0 or vegetation_volume > 0.3:
                messages.append(f"{lid_type}: Vegetation volume should be between 0 and 0.3")
        
        # Soil layer validation with logical relationships
        if 'soil' in lid_params:
            soil = lid_params['soil']
            
            porosity = soil.get('porosity', 0)
            field_capacity = soil.get('field_capacity', 0)
            wilting_point = soil.get('wilting_point', 0)
            
            # Check logical relationships
            if field_capacity >= porosity:
                messages.append(f"{lid_type}: Field capacity must be less than porosity")
            
            if wilting_point >= field_capacity:
                messages.append(f"{lid_type}: Wilting point must be less than field capacity")
    
    return messages
```

### LID Usage Validation
```python
def validate_lid_usage(params: Dict[str, Any]) -> List[str]:
    """Validate LID usage parameters."""
    messages = []
    
    if not params.get('enabled', False):
        return messages  # Skip validation if LID usage is disabled
    
    assignments = params.get('subcatchment_assignments', {})
    
    for subcatch_id, assignment in assignments.items():
        # Validate LID type
        lid_type = assignment.get('lid_type', '')
        valid_lid_types = ['bioretention_cell', 'green_roof', 'infiltration_trench', 
                          'permeable_pavement', 'rain_barrel', 'vegetative_swale', 
                          'rain_garden', 'rooftop_disconnection']
        if lid_type not in valid_lid_types:
            messages.append(f"{subcatch_id}: Invalid LID type '{lid_type}'")
        
        # Validate numeric parameters
        number_replicate = assignment.get('number_replicate', 0)
        if number_replicate < 1 or number_replicate > 100:
            messages.append(f"{subcatch_id}: Number of replicates should be between 1 and 100")
        
        area = assignment.get('area', 0)
        if area < 100 or area > 10000:
            messages.append(f"{subcatch_id}: LID area should be between 100 and 10,000 sq ft")
    
    return messages
```

## 4. SWMM Model Integration (swmm_model.py)

### LID Controls Section Generation
```python
def _generate_lid_controls(self, parameters: Dict[str, Any]) -> str:
    """Generate LID controls section."""
    content = []
    content.append("[LID_CONTROLS]")
    content.append(";;Name             Type/Layer       Parameters")
    content.append(";;---------------------------------------------------------")
    
    lid_controls = parameters.get('lid_controls', {})
    
    # Generate each LID control based on enabled types
    for lid_type, lid_params in lid_controls.items():
        if lid_type == 'enabled':
            continue
            
        control_name = lid_type.upper()
        
        # Bio-retention Cell
        if lid_type == 'bioretention_cell':
            content.append(f"{control_name}     BC")
            # Surface layer
            surface = lid_params.get('surface', {})
            content.append(f"{control_name}     SURFACE       {surface.get('berm_height', 6.0)} {surface.get('vegetation_volume', 0.0)} {surface.get('surface_roughness', 0.1)} {surface.get('surface_slope', 1.0)} 0")
            # Soil layer
            soil = lid_params.get('soil', {})
            content.append(f"{control_name}     SOIL          {soil.get('thickness', 24.0)} {soil.get('porosity', 0.45)} {soil.get('field_capacity', 0.15)} {soil.get('wilting_point', 0.05)} {soil.get('conductivity', 1.0)} {soil.get('conductivity_slope', 10.0)} {soil.get('suction_head', 6.0)}")
            # Storage layer
            storage = lid_params.get('storage', {})
            content.append(f"{control_name}     STORAGE       {storage.get('thickness', 12.0)} {storage.get('void_ratio', 0.5)} {storage.get('seepage_rate', 0.5)} {storage.get('clogging_factor', 0.0)}")
            # Drain layer (if enabled)
            drain = lid_params.get('drain', {})
            if drain.get('drain_coefficient', 0.0) > 0:
                content.append(f"{control_name}     DRAIN         {drain.get('drain_coefficient', 0.0)} {drain.get('drain_exponent', 0.5)} {drain.get('offset_height', 0.0)} {drain.get('delay', 0.0)}")
        
        # Green Roof
        elif lid_type == 'green_roof':
            content.append(f"{control_name}     GR")
            # Surface layer
            surface = lid_params.get('surface', {})
            content.append(f"{control_name}     SURFACE       {surface.get('berm_height', 0.0)} {surface.get('vegetation_volume', 0.0)} {surface.get('surface_roughness', 0.1)} {surface.get('surface_slope', 2.0)} 0")
            # Soil layer
            soil = lid_params.get('soil', {})
            content.append(f"{control_name}     SOIL          {soil.get('thickness', 4.0)} {soil.get('porosity', 0.45)} {soil.get('field_capacity', 0.15)} {soil.get('wilting_point', 0.05)} {soil.get('conductivity', 2.0)} {soil.get('conductivity_slope', 10.0)} {soil.get('suction_head', 6.0)}")
            # Drainage mat
            drainage = lid_params.get('drainage_mat', {})
            content.append(f"{control_name}     DRAINMAT      {drainage.get('thickness', 1.0)} {drainage.get('void_fraction', 0.5)} {drainage.get('roughness', 0.1)} {drainage.get('initial_moisture', 0.0)}")
    
    content.append("")
    return "\n".join(content)
```

### LID Usage Section Generation
```python
def _generate_lid_usage(self, parameters: Dict[str, Any]) -> str:
    """Generate LID usage section."""
    content = []
    content.append("[LID_USAGE]")
    content.append(";;Subcatchment   LID Process     Number  Area       Width     InitSat   FromImp   ToPerv   RptFile   DrainTo")
    content.append(";;-------------------------------------------------------------------------------------------------")
    
    lid_usage = parameters.get('lid_usage', {})
    
    if lid_usage.get('enabled', False):
        assignments = lid_usage.get('subcatchment_assignments', {})
        
        for subcatch_id, assignment in assignments.items():
            lid_type = assignment.get('lid_type', '').upper()
            content.append(f"{subcatch_id}           {lid_type}           {assignment.get('number_replicate', 1)}       {assignment.get('area', 1000.0)}       {assignment.get('width', 50.0)}       {assignment.get('initial_saturation', 0.0)}       {assignment.get('from_imperv', 100.0)}       {assignment.get('to_perv', 0.0)}       {assignment.get('report_file', '')}       {assignment.get('drain_to', '')}")
    
    content.append("")
    return "\n".join(content)
```

## 5. Integration with Main Application

### Navigation Updates (app.py)
```python
# In main() function, add LID tabs to navigation
if page == "LID Controls":
    lid_controls_parameters()
elif page == "LID Usage":
    lid_usage_parameters()
```

### Validation Integration (validation.py)
```python
# In validate_parameters() function
if category is None or category == 'lid_controls':
    messages.extend(validate_lid_controls(parameters.get('lid_controls', {})))

if category is None or category == 'lid_usage':
    messages.extend(validate_lid_usage(parameters.get('lid_usage', {})))
```

## Key Features Implemented:

1. **Complete LID Control System**: 8 LID types with proper layer structures
2. **Dynamic Parameter Interface**: Forms adapt based on selected LID type
3. **Comprehensive Validation**: Range checks and logical consistency validation
4. **SWMM Integration**: Automatic generation of LID sections in SWMM input files
5. **Usage Assignment**: Flexible system for assigning LID controls to subcatchments
6. **Real-time Feedback**: Immediate validation and parameter updates

This implementation provides a complete framework for modeling Low Impact Development practices in urban stormwater management systems using SWMM5.