# DC-Resource Intelligence Platform

This is a student GeoAI Hackathon project completed as part of a Data Science BootCamp. It is a UI demo prototype for a future environmental-monitoring concept around anonymised U.S. locations. My contribution focused on turning prepared satellite-derived indicators and scores into an interactive Streamlit dashboard.

## Project Highlights

- Explores monthly environmental conditions at 10 anonymised demonstration locations from 2020 to 2026.
- Uses land-surface temperature, vegetation, water, built-up area, precipitation, and soil-moisture indicators.
- Uses prepared Environmental Change Index (ECI), Environmental Stress Score (ESS), current risk, and 6- and 12-month risk outlooks.
- Lets users filter the dashboard by date and location, then review hotspot details across multiple pages.

## Project Layout

- `app_demo2.py` - Main Streamlit dashboard application.
- `geosentinel_monthly_dashboard_data.csv` - Monthly demonstration dataset used by the dashboard.
- `requirements.txt` - Python dependencies for running the project.
- `runtime.txt` - Recommended Python runtime for deployment.
- `tests/test_data_schema.py` - Automated check for the required CSV structure.

## Setup

```bash
git clone https://github.com/suchanya-pangam/DC-Resource.git
cd DC-Resource
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app_demo2.py
```

On Windows, activate the environment with `.venv\\Scripts\\activate`. Open the local address shown by Streamlit in your browser.

Before changing the demonstration CSV, run the schema check:

```bash
python -m unittest discover -s tests -v
```

## Workflow

1. Use the prepared monthly satellite-derived indicators and scoring outputs for selected data-center locations.
2. Organise ECI, ESS, current risk, and forecast values for comparison across locations and dates.
3. Present the results in an interactive Streamlit dashboard for easier exploration.

## Project Purpose

This Hackathon project demonstrates a possible decision-support workflow for data-center environmental monitoring. The idea is to bring satellite-derived environmental indicators and prepared scoring outputs into one dashboard, so users can compare locations, explore changes over time, and identify potential hotspots more easily.

The current version is a demo prototype. It shows how a future system could use regularly updated data to support early monitoring and planning. It is not a live operational monitoring system, a connection to a real data-center provider, or a recommendation tool for real-world actions.

## Potential Users and Use Cases

The project explores how one dashboard could support different users in a future environmental-monitoring workflow.

- **Site operations teams** could use location-level environmental signals to review potential heat or water-stress conditions and prepare monitoring or cooling plans earlier.
- **Sustainability and ESG teams** could use the location comparisons to explore environmental context around facilities and support sustainability planning discussions.
- **Operations managers and decision makers** could use hotspot rankings and time-based views to compare locations and prioritise which areas need further review.

In a future implementation, regularly updated satellite data could feed the same workflow and provide a starting point for early-warning monitoring. Any operational decision would still need validated data, local context, and review by the responsible team.

## Live Dashboard

Explore the interactive Streamlit dashboard here: [Open DC-Resource Intelligence Platform](https://dc-resource-e3tvpyepky7plk8expnpbz.streamlit.app).

## Data

The included CSV is an anonymised demonstration dataset prepared for this Hackathon project using publicly available satellite-derived data through Google Earth Engine. It contains monthly environmental indicators and precomputed score values. Provider names have been removed, location labels are generic, and coordinates are rounded to an approximate regional level. It does not contain operational data from a data-center provider or personal information.

The project PDF identifies Google Earth Engine as the data platform, but does not record the original collection IDs or source URLs. For that reason, this repository does not claim a specific underlying dataset. Please treat the CSV as demonstration data and do not reuse it as a verified source dataset.

## How the Dashboard Uses Scores

ECI, ESS, risk, and forecast values were prepared for the Hackathon project. The dashboard uses them to compare locations, rank potential hotspots, and demonstrate how environmental signals could be presented in one place. These scores are for the project prototype and are not standardised operational metrics or validated measures of real data-center risk.

## License

The project code uses the MIT License. The included demonstration dataset may have separate source-data terms, so please check the original data sources before reusing it.
