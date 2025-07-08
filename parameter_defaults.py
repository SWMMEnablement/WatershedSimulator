"""
Default parameter values for SWMM5 watershed modeling.
These defaults are based on typical watershed characteristics and
can be used as starting points for model configuration.
"""

from typing import Dict, Any

def get_default_parameters() -> Dict[str, Any]:
    """
    Get default parameter values for SWMM5 watershed modeling.
    
    Returns:
        Dictionary containing default parameter values organized by category.
    """
    return {
        'subcatchment': {
            'area': 10.0,  # acres
            'width': 500.0,  # feet
            'slope': 2.0,  # percent
            'outlet_type': 'Node',
            'outlet_name': 'J1',
            'curb_length': 0.0  # feet
        },
        
        'surface': {
            'pct_impervious': 50.0,  # percent
            'n_imperv': 0.012,  # Manning's n for impervious areas
            'n_perv': 0.15,  # Manning's n for pervious areas
            'dstore_imperv': 0.05,  # inches
            'dstore_perv': 0.2,  # inches
            'pct_zero_imperv': 25.0,  # percent
            'subarea_routing': 'OUTLET'  # OUTLET, IMPERV, or PERV
        },
        
        'infiltration': {
            'method': 'Horton',
            'horton': {
                'max_rate': 3.0,  # in/hr
                'min_rate': 0.5,  # in/hr
                'decay_constant': 2.0,  # 1/hr
                'drying_time': 14.0  # days
            },
            'green_ampt': {
                'suction_head': 6.0,  # inches
                'conductivity': 1.0,  # in/hr
                'initial_deficit': 0.3  # fraction
            },
            'curve_number': {
                'curve_number': 75,  # SCS curve number
                'conductivity': 1.0,  # in/hr
                'drying_time': 14.0  # days
            },
            'modified_horton': {
                'max_rate': 3.0,  # in/hr
                'min_rate': 0.5,  # in/hr
                'decay_constant': 2.0,  # 1/hr
                'drying_time': 14.0,  # days
                'max_volume': 2.0  # inches
            },
            'modified_green_ampt': {
                'suction_head': 6.0,  # inches
                'conductivity': 1.0,  # in/hr
                'initial_deficit': 0.3,  # fraction
                'redistribution_factor': 1.0
            }
        },
        
        'climate': {
            'evap_method': 'Constant',
            'evap_constant': 0.2,  # in/day
            'monthly_evap': [0.1, 0.12, 0.15, 0.18, 0.22, 0.25, 
                           0.28, 0.26, 0.22, 0.18, 0.14, 0.11],  # in/day for each month
            'recovery_factor': 1.0,  # fraction
            'temp_method': 'None',
            'wind_speed': 10.0,  # mph
            'snow_enabled': False,
            'snow_temp_threshold': 32.0,  # °F
            'snow_melt_coeff': 0.5
        },
        
        'lid_controls': {
            'enabled': False,
            'bioretention_cell': {
                'surface': {
                    'berm_height': 6.0,  # inches
                    'vegetation_volume': 0.0,  # fraction
                    'surface_roughness': 0.1,  # Manning's n
                    'surface_slope': 1.0  # percent
                },
                'soil': {
                    'thickness': 24.0,  # inches
                    'porosity': 0.45,  # fraction
                    'field_capacity': 0.15,  # fraction
                    'wilting_point': 0.05,  # fraction
                    'conductivity': 1.0,  # inches/hr
                    'conductivity_slope': 10.0,  # unitless
                    'suction_head': 6.0  # inches
                },
                'storage': {
                    'thickness': 12.0,  # inches
                    'void_ratio': 0.5,  # fraction
                    'seepage_rate': 0.5,  # inches/hr
                    'clogging_factor': 0.0  # volumes treated before clogging
                },
                'drain': {
                    'drain_coefficient': 0.0,  # drainage coefficient
                    'drain_exponent': 0.5,  # drainage exponent
                    'offset_height': 0.0,  # inches
                    'delay': 0.0  # hours
                }
            },
            'green_roof': {
                'surface': {
                    'berm_height': 0.0,  # inches
                    'vegetation_volume': 0.0,  # fraction
                    'surface_roughness': 0.1,  # Manning's n
                    'surface_slope': 2.0  # percent
                },
                'soil': {
                    'thickness': 4.0,  # inches
                    'porosity': 0.45,  # fraction
                    'field_capacity': 0.15,  # fraction
                    'wilting_point': 0.05,  # fraction
                    'conductivity': 2.0,  # inches/hr
                    'conductivity_slope': 10.0,  # unitless
                    'suction_head': 6.0  # inches
                },
                'drainage_mat': {
                    'thickness': 1.0,  # inches
                    'void_fraction': 0.5,  # fraction
                    'roughness': 0.1,  # Manning's n
                    'initial_moisture': 0.0  # initial moisture content
                }
            },
            'infiltration_trench': {
                'surface': {
                    'berm_height': 6.0,  # inches
                    'vegetation_volume': 0.0,  # fraction
                    'surface_roughness': 0.1,  # Manning's n
                    'surface_slope': 1.0  # percent
                },
                'storage': {
                    'thickness': 36.0,  # inches
                    'void_ratio': 0.5,  # fraction
                    'seepage_rate': 0.5,  # inches/hr
                    'clogging_factor': 0.0  # volumes treated before clogging
                },
                'drain': {
                    'drain_coefficient': 0.0,  # drainage coefficient
                    'drain_exponent': 0.5,  # drainage exponent
                    'offset_height': 0.0,  # inches
                    'delay': 0.0  # hours
                }
            },
            'permeable_pavement': {
                'surface': {
                    'berm_height': 0.0,  # inches
                    'vegetation_volume': 0.0,  # fraction
                    'surface_roughness': 0.01,  # Manning's n
                    'surface_slope': 1.0  # percent
                },
                'pavement': {
                    'thickness': 4.0,  # inches
                    'void_ratio': 0.15,  # fraction
                    'impervious_fraction': 0.0,  # fraction
                    'permeability': 100.0,  # inches/hr
                    'clogging_factor': 0.0  # volumes treated before clogging
                },
                'storage': {
                    'thickness': 12.0,  # inches
                    'void_ratio': 0.5,  # fraction
                    'seepage_rate': 0.5,  # inches/hr
                    'clogging_factor': 0.0  # volumes treated before clogging
                },
                'drain': {
                    'drain_coefficient': 0.0,  # drainage coefficient
                    'drain_exponent': 0.5,  # drainage exponent
                    'offset_height': 0.0,  # inches
                    'delay': 0.0  # hours
                }
            },
            'rain_barrel': {
                'surface': {
                    'berm_height': 48.0,  # inches (barrel height)
                    'vegetation_volume': 0.0,  # fraction
                    'surface_roughness': 0.01,  # Manning's n
                    'surface_slope': 0.0  # percent
                },
                'drain': {
                    'drain_coefficient': 0.0,  # drainage coefficient
                    'drain_exponent': 0.5,  # drainage exponent
                    'offset_height': 0.0,  # inches
                    'delay': 0.0  # hours
                }
            },
            'vegetative_swale': {
                'surface': {
                    'berm_height': 6.0,  # inches
                    'vegetation_volume': 0.2,  # fraction
                    'surface_roughness': 0.15,  # Manning's n
                    'surface_slope': 2.0,  # percent
                    'side_slope': 33.0  # percent (3:1 slope)
                }
            },
            'rain_garden': {
                'surface': {
                    'berm_height': 6.0,  # inches
                    'vegetation_volume': 0.0,  # fraction
                    'surface_roughness': 0.1,  # Manning's n
                    'surface_slope': 1.0  # percent
                },
                'soil': {
                    'thickness': 18.0,  # inches
                    'porosity': 0.45,  # fraction
                    'field_capacity': 0.15,  # fraction
                    'wilting_point': 0.05,  # fraction
                    'conductivity': 1.0,  # inches/hr
                    'conductivity_slope': 10.0,  # unitless
                    'suction_head': 6.0  # inches
                },
                'storage': {
                    'thickness': 12.0,  # inches
                    'void_ratio': 0.5,  # fraction
                    'seepage_rate': 0.5,  # inches/hr
                    'clogging_factor': 0.0  # volumes treated before clogging
                }
            },
            'rooftop_disconnection': {
                'surface': {
                    'berm_height': 0.0,  # inches
                    'vegetation_volume': 0.0,  # fraction
                    'surface_roughness': 0.1,  # Manning's n
                    'surface_slope': 1.0  # percent
                },
                'drain': {
                    'drain_coefficient': 0.0,  # drainage coefficient
                    'drain_exponent': 0.5,  # drainage exponent
                    'offset_height': 0.0,  # inches
                    'delay': 0.0  # hours
                }
            }
        },
        
        'lid_usage': {
            'enabled': False,
            'subcatchment_assignments': {
                'S1': {
                    'lid_type': 'bioretention_cell',
                    'number_replicate': 1,
                    'area': 1000.0,  # sq ft
                    'width': 50.0,  # ft
                    'initial_saturation': 0.0,  # fraction
                    'from_imperv': 100.0,  # percent
                    'to_perv': 0.0,  # percent
                    'report_file': '',
                    'drain_to': '',
                    'drain_subcatch': ''
                }
            }
        }
    }

def get_surface_type_defaults() -> Dict[str, Dict[str, float]]:
    """
    Get default surface parameters for different land use types.
    
    Returns:
        Dictionary with surface type defaults.
    """
    return {
        'residential': {
            'pct_impervious': 35.0,
            'n_imperv': 0.012,
            'n_perv': 0.15,
            'dstore_imperv': 0.05,
            'dstore_perv': 0.2,
            'pct_zero_imperv': 25.0
        },
        'commercial': {
            'pct_impervious': 85.0,
            'n_imperv': 0.013,
            'n_perv': 0.20,
            'dstore_imperv': 0.06,
            'dstore_perv': 0.3,
            'pct_zero_imperv': 10.0
        },
        'industrial': {
            'pct_impervious': 75.0,
            'n_imperv': 0.015,
            'n_perv': 0.25,
            'dstore_imperv': 0.08,
            'dstore_perv': 0.25,
            'pct_zero_imperv': 20.0
        },
        'forest': {
            'pct_impervious': 5.0,
            'n_imperv': 0.011,
            'n_perv': 0.40,
            'dstore_imperv': 0.04,
            'dstore_perv': 0.5,
            'pct_zero_imperv': 0.0
        },
        'agricultural': {
            'pct_impervious': 10.0,
            'n_imperv': 0.012,
            'n_perv': 0.30,
            'dstore_imperv': 0.05,
            'dstore_perv': 0.4,
            'pct_zero_imperv': 5.0
        }
    }

def get_soil_type_defaults() -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Get default infiltration parameters for different soil types.
    
    Returns:
        Dictionary with soil type defaults for each infiltration method.
    """
    return {
        'sand': {
            'horton': {
                'max_rate': 8.0,
                'min_rate': 0.5,
                'decay_constant': 4.0,
                'drying_time': 7.0
            },
            'green_ampt': {
                'suction_head': 2.0,
                'conductivity': 5.0,
                'initial_deficit': 0.4
            },
            'curve_number': {
                'curve_number': 65,
                'conductivity': 5.0,
                'drying_time': 7.0
            }
        },
        'loamy_sand': {
            'horton': {
                'max_rate': 6.0,
                'min_rate': 0.4,
                'decay_constant': 3.5,
                'drying_time': 10.0
            },
            'green_ampt': {
                'suction_head': 3.0,
                'conductivity': 3.0,
                'initial_deficit': 0.35
            },
            'curve_number': {
                'curve_number': 70,
                'conductivity': 3.0,
                'drying_time': 10.0
            }
        },
        'sandy_loam': {
            'horton': {
                'max_rate': 4.0,
                'min_rate': 0.3,
                'decay_constant': 3.0,
                'drying_time': 12.0
            },
            'green_ampt': {
                'suction_head': 4.0,
                'conductivity': 2.0,
                'initial_deficit': 0.3
            },
            'curve_number': {
                'curve_number': 75,
                'conductivity': 2.0,
                'drying_time': 12.0
            }
        },
        'loam': {
            'horton': {
                'max_rate': 3.0,
                'min_rate': 0.2,
                'decay_constant': 2.0,
                'drying_time': 14.0
            },
            'green_ampt': {
                'suction_head': 6.0,
                'conductivity': 1.0,
                'initial_deficit': 0.3
            },
            'curve_number': {
                'curve_number': 80,
                'conductivity': 1.0,
                'drying_time': 14.0
            }
        },
        'silt_loam': {
            'horton': {
                'max_rate': 2.0,
                'min_rate': 0.15,
                'decay_constant': 1.5,
                'drying_time': 16.0
            },
            'green_ampt': {
                'suction_head': 8.0,
                'conductivity': 0.7,
                'initial_deficit': 0.25
            },
            'curve_number': {
                'curve_number': 82,
                'conductivity': 0.7,
                'drying_time': 16.0
            }
        },
        'clay_loam': {
            'horton': {
                'max_rate': 1.5,
                'min_rate': 0.1,
                'decay_constant': 1.2,
                'drying_time': 18.0
            },
            'green_ampt': {
                'suction_head': 10.0,
                'conductivity': 0.4,
                'initial_deficit': 0.22
            },
            'curve_number': {
                'curve_number': 85,
                'conductivity': 0.4,
                'drying_time': 18.0
            }
        },
        'clay': {
            'horton': {
                'max_rate': 1.0,
                'min_rate': 0.05,
                'decay_constant': 1.0,
                'drying_time': 21.0
            },
            'green_ampt': {
                'suction_head': 12.0,
                'conductivity': 0.2,
                'initial_deficit': 0.2
            },
            'curve_number': {
                'curve_number': 90,
                'conductivity': 0.2,
                'drying_time': 21.0
            }
        }
    }

def get_typical_ranges() -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Get typical parameter ranges for validation.
    
    Returns:
        Dictionary with typical parameter ranges.
    """
    return {
        'subcatchment': {
            'area': {'min': 0.1, 'max': 10000.0, 'units': 'acres'},
            'width': {'min': 10.0, 'max': 5000.0, 'units': 'feet'},
            'slope': {'min': 0.1, 'max': 50.0, 'units': 'percent'},
            'curb_length': {'min': 0.0, 'max': 50000.0, 'units': 'feet'}
        },
        'surface': {
            'pct_impervious': {'min': 0.0, 'max': 100.0, 'units': 'percent'},
            'n_imperv': {'min': 0.01, 'max': 0.10, 'units': 'dimensionless'},
            'n_perv': {'min': 0.05, 'max': 1.0, 'units': 'dimensionless'},
            'dstore_imperv': {'min': 0.0, 'max': 0.5, 'units': 'inches'},
            'dstore_perv': {'min': 0.0, 'max': 2.0, 'units': 'inches'},
            'pct_zero_imperv': {'min': 0.0, 'max': 100.0, 'units': 'percent'}
        },
        'infiltration': {
            'horton': {
                'max_rate': {'min': 0.1, 'max': 50.0, 'units': 'in/hr'},
                'min_rate': {'min': 0.01, 'max': 10.0, 'units': 'in/hr'},
                'decay_constant': {'min': 0.1, 'max': 20.0, 'units': '1/hr'},
                'drying_time': {'min': 1.0, 'max': 30.0, 'units': 'days'}
            },
            'green_ampt': {
                'suction_head': {'min': 0.5, 'max': 20.0, 'units': 'inches'},
                'conductivity': {'min': 0.01, 'max': 10.0, 'units': 'in/hr'},
                'initial_deficit': {'min': 0.01, 'max': 0.5, 'units': 'fraction'}
            },
            'curve_number': {
                'curve_number': {'min': 30, 'max': 100, 'units': 'dimensionless'},
                'conductivity': {'min': 0.01, 'max': 10.0, 'units': 'in/hr'},
                'drying_time': {'min': 1.0, 'max': 30.0, 'units': 'days'}
            }
        },
        'climate': {
            'evap_constant': {'min': 0.0, 'max': 1.0, 'units': 'in/day'},
            'recovery_factor': {'min': 0.0, 'max': 1.0, 'units': 'fraction'},
            'wind_speed': {'min': 0.0, 'max': 50.0, 'units': 'mph'},
            'snow_temp_threshold': {'min': 20.0, 'max': 40.0, 'units': '°F'},
            'snow_melt_coeff': {'min': 0.1, 'max': 2.0, 'units': 'dimensionless'}
        }
    }

def get_climate_defaults_by_region() -> Dict[str, Dict[str, Any]]:
    """
    Get default climate parameters for different regions.
    
    Returns:
        Dictionary with regional climate defaults.
    """
    return {
        'arid': {
            'evap_constant': 0.4,
            'monthly_evap': [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 
                           0.5, 0.48, 0.42, 0.35, 0.28, 0.22],
            'recovery_factor': 0.8,
            'snow_enabled': False
        },
        'humid': {
            'evap_constant': 0.15,
            'monthly_evap': [0.08, 0.1, 0.12, 0.15, 0.18, 0.2, 
                           0.22, 0.2, 0.18, 0.15, 0.12, 0.1],
            'recovery_factor': 1.0,
            'snow_enabled': False
        },
        'temperate': {
            'evap_constant': 0.2,
            'monthly_evap': [0.1, 0.12, 0.15, 0.18, 0.22, 0.25, 
                           0.28, 0.26, 0.22, 0.18, 0.14, 0.11],
            'recovery_factor': 1.0,
            'snow_enabled': True,
            'snow_temp_threshold': 32.0,
            'snow_melt_coeff': 0.5
        },
        'tropical': {
            'evap_constant': 0.25,
            'monthly_evap': [0.2, 0.22, 0.25, 0.28, 0.3, 0.32, 
                           0.35, 0.33, 0.3, 0.28, 0.25, 0.22],
            'recovery_factor': 0.9,
            'snow_enabled': False
        }
    }

def get_lid_type_defaults() -> Dict[str, str]:
    """
    Get available LID control types and their descriptions.
    
    Returns:
        Dictionary mapping LID type names to descriptions.
    """
    return {
        'bioretention_cell': 'Bio-retention Cell - Vegetated depression with engineered soil',
        'green_roof': 'Green Roof - Vegetated roof system with drainage layer',
        'infiltration_trench': 'Infiltration Trench - Gravel-filled trench for runoff capture',
        'permeable_pavement': 'Permeable Pavement - Porous paving with gravel storage',
        'rain_barrel': 'Rain Barrel - Container for roof runoff collection',
        'vegetative_swale': 'Vegetative Swale - Grass-lined channel for conveyance',
        'rain_garden': 'Rain Garden - Shallow depression with vegetation',
        'rooftop_disconnection': 'Rooftop Disconnection - Redirect roof runoff to landscaping'
    }

def get_lid_layer_definitions() -> Dict[str, Dict[str, str]]:
    """
    Get layer definitions for each LID type.
    
    Returns:
        Dictionary mapping LID types to their required layers.
    """
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
        'infiltration_trench': {
            'surface': 'Surface layer for ponding',
            'storage': 'Gravel storage layer',
            'drain': 'Optional underdrain system'
        },
        'permeable_pavement': {
            'surface': 'Surface layer',
            'pavement': 'Porous pavement layer',
            'storage': 'Gravel storage layer',
            'drain': 'Optional underdrain system'
        },
        'rain_barrel': {
            'surface': 'Barrel storage surface',
            'drain': 'Outlet/drain system'
        },
        'vegetative_swale': {
            'surface': 'Vegetated surface with trapezoidal cross-section'
        },
        'rain_garden': {
            'surface': 'Surface layer with ponding',
            'soil': 'Soil layer for infiltration',
            'storage': 'Optional storage layer'
        },
        'rooftop_disconnection': {
            'surface': 'Surface layer for routing',
            'drain': 'Roof drain system'
        }
    }
