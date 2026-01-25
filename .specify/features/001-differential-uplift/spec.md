# Differential Uplift Analysis Specification

## Objective

Calculate and visualize differential uplift between two Bottom Pressure Recorders (MJ03F - MJ03E) at Axial Seamount to characterize volcanic deformation patterns.

## Inputs

### Data Sources

| Station | Location | Path |
|---------|----------|------|
| MJ03E | Eastern Caldera | `/home/jovyan/ooi/kdata/RS03ECAL-MJ03E-06-BOTPTA302-streamed-botpt_nano_sample_15s/` |
| MJ03F | Central Caldera | `/home/jovyan/ooi/kdata/RS03CCAL-MJ03F-05-BOTPTA301-streamed-botpt_nano_sample_15s/` |

- **File format**: NetCDF
- **File pattern**: `deployment0001_*_<starttime>-<endtime>.nc`
- **Time period**: 2014-01-01 to 2018-12-31

### Key Variables

- `time`: CF-compliant timestamp (seconds since 1900-01-01)
- `bottom_pressure`: Pressure in psia (pounds per square inch absolute)

## Processing Steps

1. **Load data** using Dask (minimum 8 workers) for parallel processing
2. **Convert pressure to depth**: `depth_m = (pressure_psia - 14.7) * 0.670`
3. **Quality control**:
   - Range check: flag values outside 1500-1600m
   - Spike detection: flag values >3 sigma from rolling mean
   - Time consistency: check for gaps, duplicates, non-monotonic time
4. **Resample** to 1-hour averages
5. **Calculate differential uplift**: `MJ03F_depth - MJ03E_depth`
6. **Export** cleaned data to parquet format

## Outputs

### Data Products

| File | Description |
|------|-------------|
| `outputs/data/differential_uplift_2014-2018.parquet` | Cleaned, hourly DataFrame with columns: `depth_mj03e`, `depth_mj03f`, `differential_uplift` |

### Visualizations

| File | Description |
|------|-------------|
| `outputs/figures/depth_mj03e_2014-2018.png` | Time series of MJ03E depth (meters) |
| `outputs/figures/depth_mj03f_2014-2018.png` | Time series of MJ03F depth (meters) |
| `outputs/figures/differential_uplift_2014-2018.png` | Time series of differential uplift |

### Figure Standards

- Format: PNG, 300 DPI
- Color palette: Magma (colorblind-safe)
- Dimensions: 7" width (double column)
- Required: axis labels with units, timestamps

## Validation Criteria

- Depth values in range 1500-1600m (Axial caldera floor)
- No duplicate timestamps
- Monotonically increasing time
- Differential uplift should show volcanic inflation/deflation cycles
- Known eruptions (April 2015) should appear as rapid deflation signals
