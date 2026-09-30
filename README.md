# CycloneShield AI 🌪️

## Track 5 — Cyclone Impact & Infrastructure Vulnerability Forecaster

CycloneShield AI is an interactive Streamlit prototype for assessing cyclone hazard, exposure, and infrastructure vulnerability.

### Features
- Cyclone scenario controls
- Explainable 0–100 risk score
- Low / Moderate / High / Critical classification
- Interactive risk map
- Infrastructure exposure table
- Top vulnerability drivers
- Preparedness recommendations
- Deployment-ready Streamlit setup

### Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Deployment
Deploy `app.py` with `requirements.txt` on Streamlit Community Cloud.

### Model
The prototype combines normalized hazard and exposure indicators using transparent weights:
- Wind intensity: 27%
- Rainfall: 18%
- Storm surge: 18%
- Impact duration: 8%
- Population exposure: 10%
- Infrastructure vulnerability: 10%
- Low elevation: 5%
- Coastal exposure: 4%
- Preparedness provides a reduction factor

This is a hackathon prototype, not an official emergency warning system.

### Future scope
Real-time IMD/NOAA/JTWC feeds, OpenStreetMap infrastructure, satellite data, historical validation, ML-based forecasting, uncertainty estimates, and evacuation routing.
