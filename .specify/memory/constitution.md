# Axial Seamount Differential Uplift Analysis

## Research Context

This project investigates volcanic deformation behavior at Axial Seamount by calculating differential uplift between two Bottom Pressure Recorders (NANO-BPRs) deployed on the OOI Regional Cabled Array (RCA). The analysis subtracts depth measurements from the BPR at MJ03F (Central Caldera, highest inflation rate) from MJ03E (Eastern Caldera, lowest inflation rate) to isolate relative vertical displacement signals.

Understanding differential uplift patterns helps characterize magma chamber dynamics and may contribute to eruption forecasting at this actively deforming submarine volcano.
<!-- What scientific questions does this project address? How does it fit
     into the broader research program? Who are the intended users of
     the outputs? -->

## Core Principles

### I. Reproducibility

Analysis should be fully reproducible from raw data to final outputs.
Scripts run without manual intervention. Random seeds are fixed and
documented. Environment dependencies are explicit (requirements.txt,
environment.yml, or equivalent).

### II. Data Integrity

Raw data is immutable - all transformations produce new files, never
overwrite sources. Data lineage is traceable through the analysis chain.
Missing or suspect values are flagged, not silently dropped or filled.

### III. Provenance

Every output links back to: the code that produced it, the input data,
and key parameter choices. Figures and tables can be regenerated from
tracked artifacts. If you can't trace how a number was made, it doesn't
belong in the paper.

## Data Sources

### OOI-RCA Bottom Pressure Recorders

| Station | Node | Location | Description |
|---------|------|----------|-------------|
| MJ03E | Eastern Caldera | RS03ECAL | Lower inflation rate reference |
| MJ03F | Central Caldera | RS03CCAL | Higher inflation rate target |

- **Access**: Local netCDF files
- **Local paths**:
  - Eastern Caldera: `/home/jovyan/ooi/kdata/RS03ECAL-MJ03E-06-BOTPTA302-streamed-botpt_nano_sample/`
  - Central Caldera: `/home/jovyan/ooi/kdata/RS03CCAL-MJ03F-05-BOTPTA301-streamed-botpt_nano_sample/`
- **Temporal coverage**: 2014-08-29 to 2026-01-22 (ongoing)
- **File pattern**: `deployment0001_*_<starttime>-<endtime>.nc`
- **Known issues**: [TODO: any data gaps or quality concerns]
<!-- For each major data source:
     - Name and brief description
     - Access method (URL, API, local path)
     - Spatial/temporal coverage
     - Update frequency (if applicable)
     - Known quality issues or limitations
     - Contact or documentation link -->

## Technical Environment

- **Language**: Python 3.12
- **Package manager**: uv
- **Key packages**:
  - xarray (netCDF handling, time series)
  - pandas (data manipulation)
  - matplotlib (static plotting)
  - hvplot (interactive plotting)
  - seaborn (statistical visualization)
- **Compute environment**: JupyterHub
- **Data storage**: `/home/jovyan/ooi/kdata/`
- **Version control**: Git + GitHub
<!-- - Language and version (e.g., Python 3.11)
     - Key packages and versions
     - Compute environment (laptop, cluster, cloud)
     - Data storage locations
     - Version control practices -->

## Coordinate Systems & Units

Following standard OOI conventions:

- **Time**: UTC, CF-compliant (seconds since 1900-01-01)
- **Pressure/Depth**: psia (pounds per square inch absolute) from NANO-BPR; convert to meters for analysis
- **Coordinates**: WGS84 (EPSG:4326) for lat/lon
- **Missing data**: NaN or CF-standard `_FillValue` attributes
- **Calendar**: Standard Gregorian
<!-- - Spatial reference system(s) with EPSG codes
     - Time zone and calendar conventions
     - Standard units for key variables
     - Missing data conventions (NaN, -9999, etc.) -->

## Figure Standards

- **Target**: Publication quality
- **Color palette**: Magma (colorblind-safe, perceptually uniform)
- **File format**: PNG, 300 DPI minimum
- **Dimensions**: Single column (3.5") or double column (7") width
- **Font**: Sans-serif, minimum 8pt for labels
- **Required elements**: Axis labels with units, colorbars where applicable, timestamps
<!-- - Color palette (prefer colorblind-safe)
     - Standard dimensions for publication
     - Required elements (scale bars, colorbars, uncertainty)
     - File formats and resolution (e.g., PDF for vectors, 300dpi PNG) -->

## Quality Checks

- **Range checks**: Flag values outside expected seafloor depth range (~1500-1600m for Axial caldera)
- **Spike detection**: Statistical threshold (>3 sigma from rolling mean) to identify outliers
- **Outlier handling**: Flag for manual visual inspection before removal
- **Temporal consistency**: Check for time gaps, duplicate timestamps, non-monotonic time
- **Cross-instrument validation**: Compare MJ03E and MJ03F for correlated signals (tides, seismic events)
<!-- - Range and sanity checks for key variables
     - Spatial/temporal consistency checks
     - Comparison against reference or validation data
     - How suspect data is flagged and handled -->

## Project Notes

### Technical Notes

- **xarray convention**: Always swap dimensions so `obs` is replaced with `time` (e.g., `ds.swap_dims({'obs': 'time'})`)

### Constraints

- [TODO: collaborators, deadlines, data restrictions if any]

---

## Session Checkpoint

**Status**: Constitution in progress - defining specific outputs

**Next prompt**: What outputs do you want from this analysis?
1. **Data products** - e.g., concatenated DataFrame, differential uplift time series, resampled data?
2. **Visualizations** - e.g., interactive time series, static publication figures, comparison plots?
3. **Time period** - full record (2014-present) or a specific range?
<!-- - Collaborator agreements or data sharing restrictions
     - Publication timelines or embargo periods
     - Any other project-specific constraints -->
