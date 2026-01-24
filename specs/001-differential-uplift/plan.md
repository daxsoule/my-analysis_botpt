# Analysis Plan: Differential Uplift 2015

**Spec**: `specs/001-differential-uplift/spec.md`
**Created**: 2026-01-24
**Status**: Draft

## Summary

Calculate differential uplift between MJ03E (Eastern Caldera) and MJ03F (Central Caldera) bottom pressure recorders at Axial Seamount for 2015. Load netCDF data, convert pressure to depth, compute the difference (MJ03F - MJ03E), and generate three time series plots.

## Analysis Environment

**Language/Version**: Python 3.12
**Key Packages**: xarray, pandas, matplotlib, netcdf4
**Environment File**: `requirements.txt` (exists)

## Compute Environment

**Where will this run?**
- [x] Shared server (JupyterHub)

**Data scale**: ~800MB (two netCDF files covering 2015)

**Timeline pressure**: None specified

## Constitution Check

- [x] Data sources match those defined in constitution
- [x] Coordinate systems/units are consistent (psia → meters)
- [x] Figure standards will be followed (PNG output)
- [x] Quality checks are incorporated (N/A - simplified scope)

**Issues to resolve**: None

## Project Structure

```text
my-analysis_botpt/
├── specs/001-differential-uplift/
│   ├── plan.md              # This file
│   └── tasks.md             # Task breakdown
├── analysis.py              # Single script for full pipeline
├── requirements.txt         # Dependencies
├── depth_mj03e_2015.png     # Output: Eastern Caldera depth
├── depth_mj03f_2015.png     # Output: Central Caldera depth
└── differential_uplift_2015.png  # Output: Differential uplift
```

**Structure notes**: All scripts and outputs in project root per user request. Single script since analysis is straightforward.

## Data Pipeline

### Stage 1: Load Data
- **Input**: netCDF files from `/home/jovyan/ooi/kdata/`
  - MJ03E: `RS03ECAL-MJ03E-06-BOTPTA302-streamed-botpt_nano_sample_15s/`
  - MJ03F: `RS03CCAL-MJ03F-05-BOTPTA301-streamed-botpt_nano_sample_15s/`
- **Processing**:
  - Open files covering 2015 (files span ~1 year each)
  - Swap dimensions from `obs` to `time`
  - Filter to 2015-01-01 through 2015-12-31
- **Output**: In-memory xarray datasets

### Stage 2: Convert Pressure to Depth
- **Input**: Pressure data in psia
- **Processing**: `depth_m = (pressure_psia - 14.7) * 0.670`
- **Output**: Depth arrays in meters

### Stage 3: Generate Plots
- **Input**: Depth time series for both stations
- **Output**: Three PNG files in project root
  1. `depth_mj03e_2015.png` - MJ03E depth vs time
  2. `depth_mj03f_2015.png` - MJ03F depth vs time
  3. `differential_uplift_2015.png` - (MJ03F - MJ03E) vs time

## Script Plan

| Script | Purpose | Inputs | Outputs |
|--------|---------|--------|---------|
| `analysis.py` | Full pipeline: load, convert, plot | netCDF files | 3 PNG figures |

## Dependencies

```text
Load MJ03E data ─┬─→ Convert to depth ─┬─→ Plot MJ03E depth
                 │                     │
Load MJ03F data ─┴─→ Convert to depth ─┼─→ Plot MJ03F depth
                                       │
                                       └─→ Calculate difference ─→ Plot differential uplift
```

**Parallel opportunities**: MJ03E and MJ03F loading can happen in parallel. All three plots can be generated once data is loaded.

## Open Questions

None - scope is well-defined.

## Notes

- 2015 data spans two netCDF files per station (one ending Oct 2015, one starting Oct 2015)
- Existing `.specify/scripts/` files are from earlier iteration with different scope - will create fresh `analysis.py` in project root
