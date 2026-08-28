# GeoWater Analysis

**A geospatial water resource monitoring system for Telangana.** Combines district
rainfall with dam storage capacity into a single drought index, and renders it as an
interactive choropleth map of all 33 districts.

Final year project · B.Tech CSE (AI & ML), B V Raju Institute of Technology

---

## The problem

Assessing drought risk from rainfall alone is misleading. A district can receive poor
rainfall and still be secure if it has substantial reservoir storage — and a district
with good rainfall but no storage stays vulnerable the moment the monsoon is late.
Rainfall and storage have to be read together.

This project combines both into one comparable score per district, per year, so
districts can be ranked against each other rather than assessed in isolation.

## Method

Each district-year is scored in three steps:

| Step | Output | Description |
|---|---|---|
| 1 | `Rain Score` | Monsoon rainfall (June–September), normalised to 0–100 |
| 2 | `Dam Score` | Dam storage capacity in MCM, normalised to 0–100 |
| 3 | `Water Availability` | The two scores combined |
| | `Drought Percentage` | `100 − Water Availability` |

Rainfall is aggregated over the monsoon window only, and averages are computed both
across all days and across rainy days alone — a district with the same total rainfall
delivered in fewer, heavier events has a different water-retention profile from one
with steady rain.

**Coverage:** 33 districts × 2 years (2024, 2025) = 66 district-year records.

## Findings

Mean drought percentage was **40.5% in 2024** and **39.7% in 2025** — broadly flat
statewide, but hiding large movements at district level.

**Most drought-affected (2024)**

| District | Drought % | Rainfall | Dam capacity |
|---|---|---|---|
| Hyderabad | 62.1% | 731 mm | 0.9 MCM |
| Jangaon | 61.4% | 767 mm | 0 MCM |
| Hanumakonda | 60.3% | 786 mm | 0 MCM |

**Most drought-affected (2025)**

| District | Drought % | Rainfall | Dam capacity |
|---|---|---|---|
| Jogulamba Gadwal | 64.3% | 528 mm | 197 MCM |
| Nalgonda | 60.0% | 454 mm | 11,472 MCM |
| Ranga Reddy | 60.0% | 652 mm | 46 MCM |

**Largest year-on-year swings**

| District | 2024 | 2025 | Change |
|---|---|---|---|
| Mahabubabad | 17.4% | 45.0% | **+27.6** |
| Mulugu | 0.0% | 22.7% | **+22.7** |
| Medak | 49.3% | 19.4% | **−30.0** |
| Kamareddy | 28.1% | 1.9% | **−26.2** |

The urban and peri-urban districts around Hyderabad — Hyderabad itself, Jangaon,
Hanumakonda, Ranga Reddy — score worst consistently, and the reason is visible in the
inputs: effectively zero reservoir storage, so they depend entirely on rainfall in the
year it falls.

**A limitation worth stating:** Nalgonda in 2025 scores 60% drought despite holding
11,472 MCM of storage — by far the largest in the state — because rainfall was only
454 mm. The composite weights rainfall heavily enough that storage cannot compensate
for a poor monsoon. Whether that reflects reality or is an artefact of the
normalisation is the most useful thing to examine next.

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens a choropleth of Telangana. Districts are shaded by drought category;
clicking one opens its rainfall and storage detail.

## Structure

```
├── app.py                            Streamlit application (map + district detail)
├── data/
│   ├── drought_Output.xlsx           Final scored dataset — 66 district-year rows
│   └── Telangana.geojson             District boundaries (33 features)
├── notebooks/
│   ├── 01_Data_Preparation.ipynb     Cleaning and joining rainfall + capacity data
│   └── 02_Drought_Calculation.ipynb  District aggregation and drought scoring
└── requirements.txt
```

**On the notebooks:** they document how `drought_Output.xlsx` was derived. They are not
runnable as-is from this repository, because the raw source dataset (~16 MB of daily
district rainfall records) is not committed here. The scored output they produce is
included, so the application runs without them.

## Built with

Python · pandas · NumPy · GeoPandas · Plotly · Streamlit
