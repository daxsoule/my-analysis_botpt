# Axial Seamount Differential Uplift Analysis

## Research Context

This project calculates differential uplift between two Bottom Pressure Recorders (NANO-BPRs) at Axial Seamount. The analysis subtracts depth at MJ03F (Central Caldera) from MJ03E (Eastern Caldera) to show relative vertical displacement.

## Data Sources

| Station | Location | Path |
|---------|----------|------|
| MJ03E | Eastern Caldera | `/home/jovyan/ooi/kdata/RS03ECAL-MJ03E-06-BOTPTA302-streamed-botpt_nano_sample_15s/` |
| MJ03F | Central Caldera | `/home/jovyan/ooi/kdata/RS03CCAL-MJ03F-05-BOTPTA301-streamed-botpt_nano_sample_15s/` |

- **Format**: netCDF files
- **Time period**: 2015-01-01 to 2026-01-16

## Technical Environment

- **Language**: Python 3.12
- **Key packages**: xarray, pandas, matplotlib
- **Working directory**: `/home/jovyan/repos/specKitScience/my-analysis_botpt/`

## Pressure-to-Depth Conversion

`depth_m = (pressure_psia - 14.7) * 0.670`

## Outputs

All outputs in the project root directory:

| File | Description |
|------|-------------|
| `depth_mj03e.png` | Time series of Eastern Caldera depth (meters) |
| `depth_mj03f.png` | Time series of Central Caldera depth (meters) |
| `differential_uplift.png` | Time series of MJ03E - MJ03F depth difference, with red horizontal line marking 2015 high |

## Notes

- Swap xarray dimensions: `ds.swap_dims({'obs': 'time'})`
