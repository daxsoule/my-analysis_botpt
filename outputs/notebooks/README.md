# Differential Uplift Analysis Notebook

This folder contains a fully reproducible Jupyter notebook for analyzing Bottom Pressure Recorder (BPR) data from Axial Seamount.

## Contents

- `differential_uplift_analysis.ipynb` - Annotated analysis notebook
- `environment.yml` - Conda environment specification
- `README.md` - This file

## Quick Start

1. **Create the conda environment:**
   ```bash
   conda env create -f environment.yml
   conda activate axial-bpr-analysis
   ```

2. **Launch Jupyter:**
   ```bash
   jupyter lab
   ```

3. **Open the notebook** and update the data paths in the Configuration section to point to your local OOI data.

4. **Run all cells** to reproduce the analysis.

## Data Requirements

You will need access to OOI BPR data from:
- RS03ECAL-MJ03E-06-BOTPTA302 (Eastern Caldera)
- RS03CCAL-MJ03F-05-BOTPTA301 (Central Caldera)

Data can be obtained from the OOI Data Portal: https://ooinet.oceanobservatories.org/

## Outputs

The notebook generates:
- `differential_uplift_hourly.parquet` - Cleaned hourly data
- `differential_uplift_daily.parquet` - Daily averaged data
- Inline visualizations of the volcanic deformation signal

## Citation

If you use this analysis, please cite the OOI facility and relevant publications on Axial Seamount deformation.
