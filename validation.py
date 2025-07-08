"""
Parameter validation functions for SWMM5 watershed modeling.
Provides comprehensive validation of input parameters with detailed error messages.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np

def validate_parameters(parameters: Dict[str, Any], category: Optional[str] = None) -> List[str]:
    """
    Validate SWMM5 parameters and return list of validation messages.
    
    Args:
        parameters: Dictionary of parameter values
        category: Optional category to validate (if None, validates all)
        
    Returns:
        List of validation error messages
    """
    messages = []
    
    if category is None or category == 'subcatchment':
        messages.extend(validate_subcatchment_parameters(parameters.get('subcatchment', {})))
    
    if category is None or category == 'surface':
        messages.extend(validate_surface_parameters(parameters.get('surface', {})))
    
    if category is None or category == 'infiltration':
        messages.extend(validate_infiltration_parameters(parameters.get('infiltration', {})))
    
    if category is None or category == 'climate':
        messages.extend(validate_climate_parameters(parameters.get('climate', {})))
    
    if category is None or category == 'lid_controls':
        messages.extend(validate_lid_controls(parameters.get('lid_controls', {})))
    
    if category is None or category == 'lid_usage':
        messages.extend(validate_lid_usage(parameters.get('lid_usage', {})))
    
    # Cross-parameter validation
    if category is None:
        messages.extend(validate_cross_parameters(parameters))
    
    return messages

def validate_subcatchment_parameters(params: Dict[str, Any]) -> List[str]:
    """Validate subcatchment parameters."""
    messages = []
    
    # Area validation
    area = params.get('area', 0)
    if area <= 0:
        messages.append("Subcatchment area must be greater than 0")
    elif area > 10000:
        messages.append("Subcatchment area is unusually large (>10,000 acres)")
    elif area < 0.1:
        messages.append("Subcatchment area is unusually small (<0.1 acres)")
    
    # Width validation
    width = params.get('width', 0)
    if width <= 0:
        messages.append("Subcatchment width must be greater than 0")
    elif width > 5000:
        messages.append("Subcatchment width is unusually large (>5,000 feet)")
    elif width < 10:
        messages.append("Subcatchment width is unusually small (<10 feet)")
    
    # Slope validation
    slope = params.get('slope', 0)
    if slope <= 0:
        messages.append("Subcatchment slope must be greater than 0")
    elif slope > 50:
        messages.append("Subcatchment slope is unusually steep (>50%)")
    elif slope < 0.1:
        messages.append("Subcatchment slope is unusually flat (<0.1%)")
    
    # Outlet validation
    outlet_name = params.get('outlet_name', '').strip()
    if not outlet_name:
        messages.append("Outlet name is required")
    elif len(outlet_name) > 16:
        messages.append("Outlet name must be 16 characters or less")
    
    # Curb length validation
    curb_length = params.get('curb_length', 0)
    if curb_length < 0:
        messages.append("Curb length cannot be negative")
    
    # Check area-width relationship
    if area > 0 and width > 0:
        length = (area * 43560) / width  # Convert acres to sq ft
        if length < width:
            messages.append("Implied subcatchment length is less than width - check area/width relationship")
    
    return messages

def validate_surface_parameters(params: Dict[str, Any]) -> List[str]:
    """Validate surface parameters."""
    messages = []
    
    # Percent impervious validation
    pct_impervious = params.get('pct_impervious', 0)
    if pct_impervious < 0 or pct_impervious > 100:
        messages.append("Percent impervious must be between 0 and 100")
    
    # Manning's n validation
    n_imperv = params.get('n_imperv', 0)
    if n_imperv < 0.01 or n_imperv > 0.10:
        messages.append("Manning's n for impervious areas should be between 0.01 and 0.10")
    
    n_perv = params.get('n_perv', 0)
    if n_perv < 0.05 or n_perv > 1.0:
        messages.append("Manning's n for pervious areas should be between 0.05 and 1.0")
    
    # Check that pervious n is greater than impervious n
    if n_perv > 0 and n_imperv > 0 and n_perv <= n_imperv:
        messages.append("Manning's n for pervious areas should be greater than impervious areas")
    
    # Depression storage validation
    dstore_imperv = params.get('dstore_imperv', 0)
    if dstore_imperv < 0 or dstore_imperv > 0.5:
        messages.append("Depression storage for impervious areas should be between 0 and 0.5 inches")
    
    dstore_perv = params.get('dstore_perv', 0)
    if dstore_perv < 0 or dstore_perv > 2.0:
        messages.append("Depression storage for pervious areas should be between 0 and 2.0 inches")
    
    # Check that pervious depression storage is greater than impervious
    if dstore_perv > 0 and dstore_imperv > 0 and dstore_perv <= dstore_imperv:
        messages.append("Depression storage for pervious areas should be greater than impervious areas")
    
    # Percent zero impervious validation
    pct_zero_imperv = params.get('pct_zero_imperv', 0)
    if pct_zero_imperv < 0 or pct_zero_imperv > 100:
        messages.append("Percent zero impervious must be between 0 and 100")
    
    # Check logical relationship
    if pct_impervious == 0 and pct_zero_imperv > 0:
        messages.append("Percent zero impervious should be 0 when there is no impervious area")
    
    # Subarea routing validation
    subarea_routing = params.get('subarea_routing', '')
    if subarea_routing not in ['OUTLET', 'IMPERV', 'PERV']:
        messages.append("Subarea routing must be OUTLET, IMPERV, or PERV")
    
    return messages

def validate_infiltration_parameters(params: Dict[str, Any]) -> List[str]:
    """Validate infiltration parameters."""
    messages = []
    
    method = params.get('method', '')
    if method not in ['Horton', 'Green-Ampt', 'Curve Number', 'Modified Horton', 'Modified Green-Ampt']:
        messages.append("Invalid infiltration method")
        return messages
    
    if method == 'Horton' or method == 'Modified Horton':
        messages.extend(validate_horton_parameters(params.get('horton', {})))
        if method == 'Modified Horton':
            messages.extend(validate_modified_horton_parameters(params.get('modified_horton', {})))
    
    elif method == 'Green-Ampt' or method == 'Modified Green-Ampt':
        messages.extend(validate_green_ampt_parameters(params.get('green_ampt', {})))
        if method == 'Modified Green-Ampt':
            messages.extend(validate_modified_green_ampt_parameters(params.get('modified_green_ampt', {})))
    
    elif method == 'Curve Number':
        messages.extend(validate_curve_number_parameters(params.get('curve_number', {})))
    
    return messages

def validate_horton_parameters(params: Dict[str, Any]) -> List[str]:
    """Validate Horton infiltration parameters."""
    messages = []
    
    max_rate = params.get('max_rate', 0)
    min_rate = params.get('min_rate', 0)
    decay_constant = params.get('decay_constant', 0)
    drying_time = params.get('drying_time', 0)
    
    if max_rate <= 0:
        messages.append("Maximum infiltration rate must be greater than 0")
    elif max_rate > 50:
        messages.append("Maximum infiltration rate is unusually high (>50 in/hr)")
    
    if min_rate <= 0:
        messages.append("Minimum infiltration rate must be greater than 0")
    elif min_rate > 10:
        messages.append("Minimum infiltration rate is unusually high (>10 in/hr)")
    
    if max_rate > 0 and min_rate > 0 and min_rate >= max_rate:
        messages.append("Minimum infiltration rate must be less than maximum rate")
    
    if decay_constant <= 0:
        messages.append("Decay constant must be greater than 0")
    elif decay_constant > 20:
        messages.append("Decay constant is unusually high (>20 1/hr)")
    
    if drying_time <= 0:
        messages.append("Drying time must be greater than 0")
    elif drying_time > 30:
        messages.append("Drying time is unusually long (>30 days)")
    
    return messages

def validate_modified_horton_parameters(params: Dict[str, Any]) -> List[str]:
    """Validate Modified Horton infiltration parameters."""
    messages = []
    
    max_volume = params.get('max_volume', 0)
    if max_volume <= 0:
        messages.append("Maximum infiltration volume must be greater than 0")
    elif max_volume > 10:
        messages.append("Maximum infiltration volume is unusually high (>10 inches)")
    
    return messages

def validate_green_ampt_parameters(params: Dict[str, Any]) -> List[str]:
    """Validate Green-Ampt infiltration parameters."""
    messages = []
    
    suction_head = params.get('suction_head', 0)
    conductivity = params.get('conductivity', 0)
    initial_deficit = params.get('initial_deficit', 0)
    
    if suction_head <= 0:
        messages.append("Suction head must be greater than 0")
    elif suction_head > 20:
        messages.append("Suction head is unusually high (>20 inches)")
    
    if conductivity <= 0:
        messages.append("Hydraulic conductivity must be greater than 0")
    elif conductivity > 10:
        messages.append("Hydraulic conductivity is unusually high (>10 in/hr)")
    
    if initial_deficit <= 0 or initial_deficit > 0.5:
        messages.append("Initial deficit must be between 0 and 0.5")
    
    return messages

def validate_modified_green_ampt_parameters(params: Dict[str, Any]) -> List[str]:
    """Validate Modified Green-Ampt infiltration parameters."""
    messages = []
    
    redistribution_factor = params.get('redistribution_factor', 0)
    if redistribution_factor <= 0:
        messages.append("Redistribution factor must be greater than 0")
    elif redistribution_factor > 2:
        messages.append("Redistribution factor is unusually high (>2)")
    
    return messages

def validate_curve_number_parameters(params: Dict[str, Any]) -> List[str]:
    """Validate Curve Number infiltration parameters."""
    messages = []
    
    curve_number = params.get('curve_number', 0)
    conductivity = params.get('conductivity', 0)
    drying_time = params.get('drying_time', 0)
    
    if curve_number < 30 or curve_number > 100:
        messages.append("Curve number must be between 30 and 100")
    
    if conductivity <= 0:
        messages.append("Hydraulic conductivity must be greater than 0")
    elif conductivity > 10:
        messages.append("Hydraulic conductivity is unusually high (>10 in/hr)")
    
    if drying_time <= 0:
        messages.append("Drying time must be greater than 0")
    elif drying_time > 30:
        messages.append("Drying time is unusually long (>30 days)")
    
    return messages

def validate_climate_parameters(params: Dict[str, Any]) -> List[str]:
    """Validate climate parameters."""
    messages = []
    
    evap_method = params.get('evap_method', '')
    if evap_method not in ['Constant', 'Monthly', 'Time Series', 'Temperature']:
        messages.append("Invalid evaporation method")
    
    if evap_method == 'Constant':
        evap_constant = params.get('evap_constant', 0)
        if evap_constant < 0 or evap_constant > 1.0:
            messages.append("Constant evaporation rate should be between 0 and 1.0 in/day")
    
    elif evap_method == 'Monthly':
        monthly_evap = params.get('monthly_evap', [])
        if len(monthly_evap) != 12:
            messages.append("Monthly evaporation must have 12 values")
        else:
            for i, val in enumerate(monthly_evap):
                if val < 0 or val > 1.0:
                    messages.append(f"Monthly evaporation for month {i+1} should be between 0 and 1.0 in/day")
    
    recovery_factor = params.get('recovery_factor', 0)
    if recovery_factor < 0 or recovery_factor > 1.0:
        messages.append("Recovery factor must be between 0 and 1.0")
    
    temp_method = params.get('temp_method', '')
    if temp_method not in ['None', 'File', 'Time Series']:
        messages.append("Invalid temperature method")
    
    if temp_method != 'None':
        wind_speed = params.get('wind_speed', 0)
        if wind_speed < 0 or wind_speed > 50:
            messages.append("Wind speed should be between 0 and 50 mph")
    
    # Snow parameters
    snow_enabled = params.get('snow_enabled', False)
    if snow_enabled:
        snow_temp_threshold = params.get('snow_temp_threshold', 0)
        if snow_temp_threshold < 20 or snow_temp_threshold > 40:
            messages.append("Snow temperature threshold should be between 20 and 40°F")
        
        snow_melt_coeff = params.get('snow_melt_coeff', 0)
        if snow_melt_coeff <= 0 or snow_melt_coeff > 2.0:
            messages.append("Snow melt coefficient should be between 0 and 2.0")
    
    return messages

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
            
            surface_roughness = surface.get('surface_roughness', 0)
            if surface_roughness < 0.01 or surface_roughness > 0.4:
                messages.append(f"{lid_type}: Surface roughness should be between 0.01 and 0.4")
            
            surface_slope = surface.get('surface_slope', 0)
            if surface_slope < 0 or surface_slope > 10:
                messages.append(f"{lid_type}: Surface slope should be between 0 and 10%")
        
        # Soil layer validation
        if 'soil' in lid_params:
            soil = lid_params['soil']
            
            thickness = soil.get('thickness', 0)
            if thickness < 2 or thickness > 48:
                messages.append(f"{lid_type}: Soil thickness should be between 2 and 48 inches")
            
            porosity = soil.get('porosity', 0)
            field_capacity = soil.get('field_capacity', 0)
            wilting_point = soil.get('wilting_point', 0)
            
            if porosity < 0.3 or porosity > 0.7:
                messages.append(f"{lid_type}: Porosity should be between 0.3 and 0.7")
            
            if field_capacity < 0.05 or field_capacity > 0.4:
                messages.append(f"{lid_type}: Field capacity should be between 0.05 and 0.4")
            
            if wilting_point < 0.01 or wilting_point > 0.2:
                messages.append(f"{lid_type}: Wilting point should be between 0.01 and 0.2")
            
            # Check logical relationships
            if field_capacity >= porosity:
                messages.append(f"{lid_type}: Field capacity must be less than porosity")
            
            if wilting_point >= field_capacity:
                messages.append(f"{lid_type}: Wilting point must be less than field capacity")
            
            conductivity = soil.get('conductivity', 0)
            if conductivity < 0.1 or conductivity > 10:
                messages.append(f"{lid_type}: Conductivity should be between 0.1 and 10 in/hr")
        
        # Storage layer validation
        if 'storage' in lid_params:
            storage = lid_params['storage']
            
            thickness = storage.get('thickness', 0)
            if thickness < 6 or thickness > 48:
                messages.append(f"{lid_type}: Storage thickness should be between 6 and 48 inches")
            
            void_ratio = storage.get('void_ratio', 0)
            if void_ratio < 0.3 or void_ratio > 0.7:
                messages.append(f"{lid_type}: Storage void ratio should be between 0.3 and 0.7")
            
            seepage_rate = storage.get('seepage_rate', 0)
            if seepage_rate < 0 or seepage_rate > 5:
                messages.append(f"{lid_type}: Seepage rate should be between 0 and 5 in/hr")
        
        # Pavement layer validation (for permeable pavement)
        if 'pavement' in lid_params:
            pavement = lid_params['pavement']
            
            thickness = pavement.get('thickness', 0)
            if thickness < 2 or thickness > 8:
                messages.append(f"{lid_type}: Pavement thickness should be between 2 and 8 inches")
            
            void_ratio = pavement.get('void_ratio', 0)
            if void_ratio < 0.1 or void_ratio > 0.3:
                messages.append(f"{lid_type}: Pavement void ratio should be between 0.1 and 0.3")
            
            permeability = pavement.get('permeability', 0)
            if permeability < 10 or permeability > 1000:
                messages.append(f"{lid_type}: Permeability should be between 10 and 1000 in/hr")
        
        # Drain layer validation
        if 'drain' in lid_params:
            drain = lid_params['drain']
            
            drain_coefficient = drain.get('drain_coefficient', 0)
            if drain_coefficient > 0:  # Only validate if drain is enabled
                if drain_coefficient < 0.1 or drain_coefficient > 10:
                    messages.append(f"{lid_type}: Drain coefficient should be between 0.1 and 10")
                
                drain_exponent = drain.get('drain_exponent', 0)
                if drain_exponent < 0.1 or drain_exponent > 2:
                    messages.append(f"{lid_type}: Drain exponent should be between 0.1 and 2")
    
    return messages

def validate_lid_usage(params: Dict[str, Any]) -> List[str]:
    """Validate LID usage parameters."""
    messages = []
    
    if not params.get('enabled', False):
        return messages  # Skip validation if LID usage is disabled
    
    assignments = params.get('subcatchment_assignments', {})
    
    for subcatch_id, assignment in assignments.items():
        # Validate subcatchment ID
        if not subcatch_id or not subcatch_id.strip():
            messages.append("Subcatchment ID cannot be empty")
        
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
        
        width = assignment.get('width', 0)
        if width < 10 or width > 200:
            messages.append(f"{subcatch_id}: LID width should be between 10 and 200 ft")
        
        initial_saturation = assignment.get('initial_saturation', 0)
        if initial_saturation < 0 or initial_saturation > 1:
            messages.append(f"{subcatch_id}: Initial saturation should be between 0 and 1")
        
        from_imperv = assignment.get('from_imperv', 0)
        if from_imperv < 0 or from_imperv > 100:
            messages.append(f"{subcatch_id}: From impervious should be between 0 and 100%")
        
        to_perv = assignment.get('to_perv', 0)
        if to_perv < 0 or to_perv > 100:
            messages.append(f"{subcatch_id}: To pervious should be between 0 and 100%")
        
        # Check logical consistency
        if area > 0 and width > 0:
            length = area / width
            aspect_ratio = length / width
            if aspect_ratio > 10:
                messages.append(f"{subcatch_id}: LID aspect ratio is high (>10:1) - consider adjusting area/width")
    
    return messages

def validate_cross_parameters(parameters: Dict[str, Any]) -> List[str]:
    """Validate relationships between parameter categories."""
    messages = []
    
    # Check consistency between subcatchment and surface parameters
    subcatch = parameters.get('subcatchment', {})
    surface = parameters.get('surface', {})
    
    area = subcatch.get('area', 0)
    width = subcatch.get('width', 0)
    pct_impervious = surface.get('pct_impervious', 0)
    
    # Check if the subcatchment configuration is reasonable
    if area > 0 and width > 0:
        length = (area * 43560) / width  # Convert acres to sq ft
        aspect_ratio = length / width
        
        if aspect_ratio > 10:
            messages.append("Warning: Subcatchment aspect ratio is high (>10:1) - consider adjusting area/width")
        elif aspect_ratio < 0.1:
            messages.append("Warning: Subcatchment aspect ratio is low (<0.1:1) - consider adjusting area/width")
    
    # Check infiltration method appropriateness
    infiltration = parameters.get('infiltration', {})
    method = infiltration.get('method', '')
    
    if method == 'Curve Number' and pct_impervious > 95:
        messages.append("Curve Number method may not be appropriate for highly impervious areas (>95%)")
    
    # Check LID consistency
    lid_controls = parameters.get('lid_controls', {})
    lid_usage = parameters.get('lid_usage', {})
    
    if lid_usage.get('enabled', False) and not lid_controls.get('enabled', False):
        messages.append("LID usage is enabled but LID controls are disabled")
    
    if lid_controls.get('enabled', False):
        assignments = lid_usage.get('subcatchment_assignments', {})
        for subcatch_id, assignment in assignments.items():
            lid_type = assignment.get('lid_type', '')
            if lid_type not in lid_controls:
                messages.append(f"LID type '{lid_type}' used in {subcatch_id} but not defined in controls")
            
            # Check if LID area is reasonable compared to subcatchment area
            lid_area = assignment.get('area', 0) * assignment.get('number_replicate', 1)
            subcatch_area_sqft = area * 43560  # Convert acres to sq ft
            
            if lid_area > subcatch_area_sqft * 0.5:  # LID area > 50% of subcatchment
                messages.append(f"{subcatch_id}: LID area ({lid_area:.0f} sq ft) is large compared to subcatchment area")
    
    # Check climate/evaporation consistency
    climate = parameters.get('climate', {})
    evap_method = climate.get('evap_method', '')
    
    if evap_method == 'Temperature' and climate.get('temp_method', '') == 'None':
        messages.append("Temperature method selected for evaporation but no temperature data method specified")
    
    return messages

def get_validation_messages(parameters: Dict[str, Any]) -> List[str]:
    """
    Get all validation messages for the current parameters.
    
    Args:
        parameters: Dictionary of parameter values
        
    Returns:
        List of validation messages
    """
    return validate_parameters(parameters)

def get_parameter_warnings(parameters: Dict[str, Any]) -> List[str]:
    """
    Get parameter warnings (non-critical issues).
    
    Args:
        parameters: Dictionary of parameter values
        
    Returns:
        List of warning messages
    """
    warnings = []
    
    # Check for unusual but valid parameter combinations
    subcatch = parameters.get('subcatchment', {})
    surface = parameters.get('surface', {})
    
    area = subcatch.get('area', 0)
    pct_impervious = surface.get('pct_impervious', 0)
    
    # Large area warnings
    if area > 1000:
        warnings.append("Large subcatchment area (>1000 acres) - consider subdividing for better accuracy")
    
    # Imperviousness warnings
    if pct_impervious > 90:
        warnings.append("Very high imperviousness (>90%) - verify this is correct for the land use")
    elif pct_impervious < 5:
        warnings.append("Very low imperviousness (<5%) - verify this is correct for the land use")
    
    # Infiltration warnings
    infiltration = parameters.get('infiltration', {})
    method = infiltration.get('method', '')
    
    if method == 'Horton':
        horton = infiltration.get('horton', {})
        max_rate = horton.get('max_rate', 0)
        min_rate = horton.get('min_rate', 0)
        
        if max_rate > 0 and min_rate > 0:
            ratio = max_rate / min_rate
            if ratio > 50:
                warnings.append("High max/min infiltration rate ratio (>50) - verify parameters")
    
    return warnings

def check_parameter_consistency(parameters: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Check consistency between parameter groups.
    
    Args:
        parameters: Dictionary of parameter values
        
    Returns:
        Dictionary with consistency check results
    """
    consistency = {
        'errors': [],
        'warnings': [],
        'info': []
    }
    
    # Add parameter consistency checks
    subcatch = parameters.get('subcatchment', {})
    surface = parameters.get('surface', {})
    infiltration = parameters.get('infiltration', {})
    
    # Check area-width relationship
    area = subcatch.get('area', 0)
    width = subcatch.get('width', 0)
    
    if area > 0 and width > 0:
        length = (area * 43560) / width
        consistency['info'].append(f"Implied subcatchment length: {length:.0f} feet")
        
        if length > 5000:
            consistency['warnings'].append("Very long subcatchment (>5000 ft) - consider subdividing")
    
    # Check imperviousness with infiltration
    pct_impervious = surface.get('pct_impervious', 0)
    method = infiltration.get('method', '')
    
    if pct_impervious > 80 and method in ['Horton', 'Green-Ampt']:
        consistency['info'].append(f"High imperviousness with {method} infiltration - infiltration will be limited")
    
    return consistency
