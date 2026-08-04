# 🌶️ Crop + pest model demo (i.e. CropGuard)

**A modular process-based crop growth and pest risk model for decision support**

CropGuard is an open-source prototype that integrates crop growth simulation and disease risk assessment into a modular decision-support framework.

The project aims to demonstrate how weather-driven crop growth can be coupled with environmental disease risk to support precision crop protection and intelligent agricultural management.

---

## Overview

CropGuard follows a modular workflow:

```text
Weather
    │
    ▼
Thermal Time (Growing Degree Days)
    │
    ▼
Crop Phenology
    │
    ▼
Leaf Area Index (LAI)
    │
    ▼
Biomass Accumulation
    │
    ▼
Host Susceptibility
    │
    ▼
Environmental Suitability
    │
    ▼
Disease Risk Assessment
    │
    ▼
Management Recommendation
```

The project is intentionally designed in independent modules so that each component can be improved or replaced without affecting the remaining workflow.

---

# Project Structure

```text
CropGuard/

│
├── data/
│     weather.csv
│
├── output/
│     model outputs
│
├── R/
│     weather_module.R
│     phenology_module.R
│     biomass_module.R
│     disease_risk_module.R
│
├── Python/
│
├── docs/
│
└── README.md
```

---

# Workflow

## Module 1 — Weather

Generate or import daily weather data.

### Inputs

- Daily minimum temperature
- Daily maximum temperature
- Relative humidity
- Rainfall
- Solar radiation

### Outputs

- Weather dataframe

---

## Module 2 — Crop Phenology

Estimate crop developmental stage using Growing Degree Days (GDD).

Workflow

```text
Temperature
      │
      ▼
Daily GDD
      │
      ▼
Cumulative GDD
      │
      ▼
Growth Stage
```

Outputs

- Mean temperature
- Daily GDD
- Cumulative GDD
- Crop growth stage

---

## Module 3 — Crop Growth

Estimate canopy development and biomass production.

Workflow

```text
Cumulative GDD
      │
      ▼
Leaf Area Index
      │
      ▼
Radiation Interception
      │
      ▼
Intercepted Radiation
      │
      ▼
Daily Biomass
      │
      ▼
Cumulative Biomass
```

Current assumptions

- Logistic LAI development
- Beer–Lambert radiation interception
- Radiation Use Efficiency (RUE) biomass production

Outputs

- LAI
- Radiation interception
- Daily biomass
- Cumulative biomass

---

## Module 4 — Disease Risk

Estimate environmental disease risk using weather conditions and crop status.

Workflow

```text
Temperature
Humidity
Rainfall
Growth Stage
        │
        ▼
Suitability Functions
        │
        ▼
Disease Risk Index
        │
        ▼
Risk Classification
        │
        ▼
Management Recommendation
```

Outputs

- Temperature suitability
- Humidity suitability
- Rainfall suitability
- Host susceptibility
- Disease risk index
- Risk level
- Management recommendation

---

# Model Philosophy

CropGuard is **not** intended to be a complete epidemiological model.

Instead, it is a modular prototype demonstrating how

- weather,
- crop growth,
- host susceptibility,
- and environmental suitability

can be integrated into a transparent decision-support framework.

Each module is independent and can later be replaced with

- APSIM
- DSSAT
- WOFOST
- machine learning models
- remote sensing
- pathogen population dynamics
- digital twin frameworks

without changing the overall architecture.

---

# Current Assumptions

Current implementation assumes

- potential crop growth
- no water limitation
- no nutrient limitation
- no pest damage feedback
- simplified disease suitability functions
- simplified host susceptibility

Therefore, the disease module currently represents an **environmental disease risk index**, rather than a complete mechanistic epidemic model.

---

# Future Development

Planned improvements include

- Real weather station data
- APSIM coupling
- Soil water balance
- Nitrogen dynamics
- Pathogen population module
- Disease severity simulation
- Yield loss estimation
- UAV and remote sensing integration
- Machine learning assisted parameter calibration
- AI-assisted crop protection recommendation
- Streamlit web application

---

# Why this project?

This project serves as

- a learning platform for scientific programming in R and Python;
- a demonstration of process-based agricultural modelling;
- an open-source framework for integrating crop growth and plant protection;
- a prototype for future intelligent agricultural decision-support systems.

---

# License

MIT License

---

# Author

Hongyu Sun

Postdoctoral Researcher

Forest Zoology, INRAE

Former PhD, Wageningen University & Research
