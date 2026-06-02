# Watershed Simulator

A Streamlit-based web application for **SWMM5 watershed runoff modeling**, parameter exploration, validation, and interactive visualization of urban stormwater behavior.

**Repository:** [SWMMEnablement/WatershedSimulator](https://github.com/SWMMEnablement/WatershedSimulator)  
**Replit app:** [replit.com/@robertdickinson/WatershedSimulator](https://replit.com/@robertdickinson/WatershedSimulator)

---

## Overview

Watershed Simulator is a Python application built around **EPA SWMM5-style watershed runoff modeling**. It provides a web interface for configuring watershed parameters, validating them against physical and logical constraints, running simulations, and visualizing the resulting runoff behavior through interactive charts. [page:48]

The application is implemented with **Streamlit** and organized as a modular modeling tool rather than a single script. The documented architecture separates the user interface, model wrapper, parameter defaults, validation rules, and visualization logic into dedicated Python modules. [page:48]

---

## Main capabilities

- Configure watershed and runoff parameters through a browser-based interface. [page:48]
- Validate parameter combinations before running a simulation. [page:48]
- Automatically generate SWMM-style model input from the selected parameters. [page:48]
- Execute a SWMM5-based simulation workflow through a Python wrapper. [page:48]
- Parse and structure simulation results for analysis. [page:48]
- Visualize hydrographs and related outputs with interactive Plotly charts. [page:48]
- Export simulation results and parameter sets. [page:47]
- Explore **green infrastructure / LID** behavior with dedicated controls and validation. [page:48]

---

## Why this repo is useful

This project gives users a focused way to experiment with watershed-runoff behavior without manually editing model input files. It is useful for demonstrating how changes in subcatchment, surface, infiltration, climate, and LID parameters affect runoff response. [page:48]

Because the interface is interactive and the model workflow is wrapped in a web app, the repository is well suited for engineering education, rapid sensitivity testing, and simple scenario-based exploration of urban stormwater processes. [page:48]

---

## System architecture

The project documentation describes a modular architecture with five primary Python modules: [page:48]

| File | Role |
|---|---|
| `app.py` | Main Streamlit application and UI orchestration. [page:48] |
| `swmm_model.py` | SWMM5 model wrapper and simulation engine. [page:48] |
| `parameter_defaults.py` | Default parameter sets for common watershed scenarios. [page:48] |
| `validation.py` | Parameter validation logic and consistency checks. [page:48] |
| `visualization.py` | Plotting and result-visualization functions. [page:48] |

This separation makes the code easier to maintain and extend than a single monolithic modeling script. [page:48]

---

## User workflow

The documented data flow is: [page:48]

1. **Parameter input** through the Streamlit interface. [page:48]  
2. **Validation** against physical constraints and parameter relationships. [page:48]  
3. **Model creation**, where a SWMM5 input file is generated from the validated parameters. [page:48]  
4. **Simulation**, where the generated model is executed through the SWMM wrapper. [page:48]  
5. **Result processing**, where outputs are parsed and structured for plotting. [page:48]  
6. **Visualization**, where runoff results are displayed through interactive charts and summaries. [page:48]  

This workflow makes the app useful both as a teaching tool and as a practical sandbox for quick runoff experiments. [page:48]

---

## Parameter system

The application includes a structured parameter-management system with defaults, categories, validation, and session persistence. The project documentation explicitly lists parameter organization into **subcatchment**, **surface**, **infiltration**, and **climate** groups, with real-time feedback to help users stay within reasonable bounds. [page:48]

This means the interface is not just a collection of input fields. It is designed to help users understand which parameters belong together and where physically inconsistent settings should be flagged before a model run. [page:48]

---

## LID and green infrastructure support

One of the most important parts of the app is its **Low Impact Development (LID)** system. The documentation describes support for **eight SWMM5 LID types**, full layer-based parameter configuration, subcatchment assignment of LID practices, and validation rules for logical consistency. [page:48]

The listed LID/green infrastructure coverage includes:

- bio-retention cells,
- green roofs,
- permeable pavement,
- infiltration trenches,
- rain barrels,
- vegetative swales,
- rain gardens,
- rooftop disconnection. [page:48]

The LID implementation also includes configurable layers such as **surface**, **soil**, **storage**, **pavement**, **drainage mat**, and **underdrain**. This makes the repository especially relevant for stormwater modelers evaluating green-infrastructure behavior. [page:48]

---

## Visualization

The visualization layer uses **Plotly** for interactive charts and graphs. The documentation describes multi-panel dashboards, dynamic chart updates, and a dedicated runoff line graph with peak annotations. [page:48]

GitHub commit history also shows several visualization-focused improvements, including a runoff hydrograph with more prominent axis labeling and a simplified line graph for runoff over time. Those updates suggest the plotting layer has been refined for clarity, not just correctness. [page:47]

---

## Interface features

The app is built on **native Streamlit widgets** and uses:

- parameter-input forms,
- sidebar navigation,
- results display areas,
- session-state persistence,
- interactive charts,
- and visual theming. [page:48]

The GitHub history also shows UI improvements such as **dark mode** and a **water-themed background**, which indicates that usability and visual presentation have been part of the project’s evolution. [page:47]

---

## Tech stack

GitHub reports the repository is **100% Python**, and the project documentation describes the following main dependencies and design choices: [page:47][page:48]

| Layer | Technology |
|---|---|
| Web framework | Streamlit. [page:48] |
| Plotting | Plotly. [page:48] |
| Data processing | Pandas and NumPy. [page:48] |
| Modeling engine | SWMM5 external executable via Python wrapper. [page:48] |
| State management | Streamlit session state. [page:48] |
| File handling | Temporary files for SWMM input/output processing. [page:48] |

The architecture is therefore best understood as a Python data/science web application that wraps a SWMM-style simulation workflow. [page:48]

---

## Repository structure

```text
WatershedSimulator/
├── .streamlit/                    # Streamlit configuration
├── attached_assets/               # Images and supporting assets
├── .replit                        # Replit runtime configuration
├── LID_Code_Examples.md           # LID-related code examples
├── LID_Implementation_Summary.md  # LID feature summary
├── app.py                         # Main Streamlit application
├── app_documentation.json         # Structured app documentation
├── parameter_defaults.py          # Default model parameters
├── pyproject.toml                 # Python project configuration
├── replit.md                      # Project architecture and notes
├── swmm_model.py                  # SWMM wrapper / simulation engine
├── uv.lock                        # Dependency lockfile
├── validation.py                  # Input validation logic
└── visualization.py               # Plotting and result display
```

This file structure shows a compact but well-separated architecture, with modeling, validation, visualization, and LID-specific documentation all present in the root. [page:47][page:48]

---

## Running locally

### Prerequisites

- Python 3.x
- A working Streamlit environment
- Required Python dependencies from `pyproject.toml`
- Access to a SWMM5 executable if the wrapper depends on an external engine in your environment. [page:48]

### Install dependencies

Use your preferred Python environment manager with the project configuration in `pyproject.toml` and `uv.lock`.

For a typical setup:

```bash
pip install -r requirements.txt
```

or install directly from the configured project environment.

### Start the app

```bash
streamlit run app.py
```

The documentation describes the app as a Streamlit development-server workflow, with local execution and temporary-file handling for SWMM model files. [page:48]

---

## Recent changes

The project changelog in `replit.md` records several notable milestones on **July 8, 2025**: [page:48]

- initial setup of the watershed modeling application,
- addition of a runoff line-graph visualization,
- automatic simulation on startup for immediate results,
- and comprehensive LID controls and usage support for all eight LID types. [page:48]

The GitHub commit history also shows later improvements such as dark mode, export enhancements, startup-performance improvements, and refreshed image assets. [page:47]

---

## Deployment notes

The documentation describes the app as suitable for both **local development** and **production deployment**, with attention to:

- temporary file cleanup,
- secure handling of generated input/output files,
- efficient parameter validation,
- and a session-based architecture that can support multiple users. [page:48]

It is also described as **Docker-ready**, which suggests the design is compatible with containerized deployment if the environment is configured correctly. [page:48]

---

## Documentation

The most important project docs currently in the repository are:

- `replit.md` — architectural overview, module roles, data flow, dependencies, deployment notes, and changelog. [page:48]
- `app_documentation.json` — structured app documentation artifact. [page:47]
- `LID_Code_Examples.md` — LID-related implementation examples. [page:47]
- `LID_Implementation_Summary.md` — summary of LID functionality. [page:47]

Since GitHub currently shows the **Add a README** prompt for this repository, adding this file would immediately make the purpose and structure of the project clearer to visitors and collaborators. [page:47]

---

## Intended audience

Watershed Simulator is especially useful for:

- SWMM users exploring runoff sensitivity,
- stormwater engineers studying watershed-response behavior,
- educators demonstrating urban hydrology concepts,
- and engineers evaluating LID/green-infrastructure scenarios in a simplified modeling environment. [page:48]

---

## License

Add the appropriate license here if the repository is intended for public reuse.
