# Differential Uplift Analysis Plan

## Pipeline Overview

```
Raw NetCDF files (15s samples)
        │
        ▼
┌─────────────────────┐
│ 01_load_data.py     │  Load and concatenate NetCDF files with Dask
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ 02_process_data.py  │  Convert psia→meters, QC, resample to 1hr
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ 03_calculate.py     │  Calculate differential uplift, export parquet
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ 04_visualize.py     │  Generate publication-quality figures
└─────────────────────┘
```

## Script Details

### 01_load_data.py

**Purpose**: Load all NetCDF files for both stations using Dask for parallel I/O

**Inputs**:
- MJ03E: `/home/jovyan/ooi/kdata/RS03ECAL-MJ03E-06-BOTPTA302-streamed-botpt_nano_sample_15s/*.nc`
- MJ03F: `/home/jovyan/ooi/kdata/RS03CCAL-MJ03F-05-BOTPTA301-streamed-botpt_nano_sample_15s/*.nc`

**Outputs**:
- `outputs/intermediate/mj03e_raw.zarr`
- `outputs/intermediate/mj03f_raw.zarr`

**Key operations**:
- Use `xarray.open_mfdataset()` with Dask backend
- Swap dims: `obs` → `time`
- Filter to 2014-01-01 to 2018-12-31
- Save as zarr for efficient intermediate storage

### 02_process_data.py

**Purpose**: Apply quality control and convert to depth

**Inputs**: Zarr files from step 01

**Outputs**:
- `outputs/intermediate/mj03e_processed.zarr`
- `outputs/intermediate/mj03f_processed.zarr`

**Key operations**:
- Convert pressure (psia) to depth (m): `depth_m = (pressure_psia - 14.7) * 0.670`
- Range check: flag values outside 1500-1600m
- Spike detection: flag >3 sigma from 24hr rolling mean
- Remove flagged values
- Resample to 1-hour averages

### 03_calculate.py

**Purpose**: Calculate differential uplift and export final dataset

**Inputs**: Processed zarr files from step 02

**Outputs**:
- `outputs/data/differential_uplift_2014-2018.parquet`

**Key operations**:
- Align time series (inner join on time)
- Calculate: `differential_uplift = depth_mj03f - depth_mj03e`
- Export to parquet with columns: `depth_mj03e`, `depth_mj03f`, `differential_uplift`

### 04_visualize.py

**Purpose**: Generate publication-quality figures

**Inputs**: `outputs/data/differential_uplift_2014-2018.parquet`

**Outputs**:
- `outputs/figures/depth_mj03e_2014-2018.png`
- `outputs/figures/depth_mj03f_2014-2018.png`
- `outputs/figures/differential_uplift_2014-2018.png`

**Key operations**:
- matplotlib with publication settings (300 DPI, 7" width)
- Magma colormap where applicable
- Axis labels with units
- Date formatting on x-axis

## Environment

- Python 3.12
- Package manager: uv
- Dask cluster: minimum 8 workers
- Key packages: xarray, dask, pandas, matplotlib

## Directory Structure

```
outputs/
├── intermediate/          # Zarr files (can be deleted after completion)
│   ├── mj03e_raw.zarr
│   ├── mj03f_raw.zarr
│   ├── mj03e_processed.zarr
│   └── mj03f_processed.zarr
├── data/
│   └── differential_uplift_2014-2018.parquet
└── figures/
    ├── depth_mj03e_2014-2018.png
    ├── depth_mj03f_2014-2018.png
    └── differential_uplift_2014-2018.png
```
