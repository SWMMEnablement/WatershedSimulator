# SWMM5 Watershed Runoff Modeling Application

## Overview

This is a Streamlit-based web application for SWMM5 (Storm Water Management Model) watershed runoff modeling. The application provides a comprehensive interface for parameter input, validation, and simulation of urban stormwater systems. It allows users to configure watershed characteristics, run simulations, and visualize results through interactive plots.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for its simplicity in creating data science web applications
- **UI Components**: Native Streamlit widgets for parameter input, sidebar navigation, and results display
- **Visualization**: Plotly for interactive charts and graphs
- **State Management**: Streamlit's session state for maintaining application state across user interactions

### Backend Architecture
- **Core Engine**: Python-based SWMM5 model wrapper
- **File Processing**: Temporary file system for SWMM input/output files
- **Data Processing**: Pandas and NumPy for data manipulation and analysis
- **Validation Layer**: Custom validation system for parameter constraints

### Modular Design
The application follows a modular architecture with separate concerns:
- `app.py`: Main application entry point and UI orchestration
- `swmm_model.py`: SWMM5 model wrapper and simulation engine
- `parameter_defaults.py`: Default parameter configurations
- `validation.py`: Parameter validation logic
- `visualization.py`: Plotting and visualization functions

## Key Components

### 1. Parameter Management System
- **Default Parameters**: Predefined watershed characteristics for common scenarios
- **Categories**: Organized into subcatchment, surface, infiltration, and climate parameters
- **Validation**: Real-time parameter validation with detailed error messages
- **Persistence**: Session-based parameter storage

### 2. SWMM5 Model Integration
- **Input File Generation**: Automatic creation of SWMM5 input files from parameters
- **Simulation Engine**: Wrapper for SWMM5 execution
- **Result Processing**: Parsing and structuring of simulation outputs
- **Temporary File Management**: Secure handling of input/output files

### 3. Visualization System
- **Interactive Plots**: Multi-panel dashboards using Plotly
- **Real-time Updates**: Dynamic chart updates based on parameter changes
- **Export Capabilities**: Result visualization and data export features

### 4. Validation Framework
- **Parameter Constraints**: Physics-based validation rules
- **Cross-parameter Validation**: Consistency checks across related parameters
- **User Feedback**: Clear error messages and suggestions

## Data Flow

1. **Parameter Input**: Users configure watershed parameters through Streamlit interface
2. **Validation**: Parameters are validated against physical constraints and relationships
3. **Model Creation**: SWMM5 input file is generated from validated parameters
4. **Simulation**: SWMM5 model is executed with the generated input file
5. **Result Processing**: Simulation outputs are parsed and structured
6. **Visualization**: Results are displayed through interactive plots and summaries

## External Dependencies

### Core Dependencies
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualization library
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **SWMM5**: Storm Water Management Model engine (external executable)

### File System Dependencies
- **Temporary Directory**: For SWMM input/output file storage
- **Input File Templates**: SWMM5 input file generation
- **Result File Parsing**: Output file processing capabilities

## Deployment Strategy

### Development Environment
- **Local Development**: Streamlit development server
- **File Storage**: Temporary file system for model files
- **Configuration**: Environment-based settings

### Production Considerations
- **Containerization**: Docker-ready architecture
- **File Management**: Temporary file cleanup and security
- **Performance**: Efficient parameter validation and model execution
- **Scaling**: Session-based architecture suitable for multiple users

## Changelog

- July 08, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.