# Axial Seamount Differential Uplift Analysis

## Development Conventions

### Package Management
- **Use `uv`** for Python dependency management
- Add packages with: `uv add <package>`
- Run scripts with: `uv run python <script.py>`
- Dependencies are tracked in `pyproject.toml`

### Code Organization
- **Prefer scripts over notebooks** for reproducible analysis
- Notebooks are for documentation and exploration only
- Scripts go in the project root (e.g., `analysis.py`)
- All scripts should be runnable via `uv run python <script.py>`

## Research Context

This project calculates differential uplift between two Bottom Pressure Recorders (NANO-BPRs) at Axial Seamount.

### Sign Convention (IMPORTANT)

**Uplift_F - Uplift_E** (Central Caldera uplift minus Eastern Caldera uplift)

Since BPR measures water depth (which DECREASES when seafloor rises), we compute:
```
differential = -(depth_F - depth_E) = depth_E - depth_F
```

This is equivalent to `uplift_F - uplift_E` and matches the Axial research team's geophysical convention (see https://axial.ceoas.oregonstate.edu/axial_blog.html):
- **Increasing values** = inflation (uplift at caldera center)
- **Decreasing values** = deflation (subsidence at caldera center)

## Data Sources

| Station | Location | Path |
|---------|----------|------|
| MJ03E | Eastern Caldera (reference) | `/home/jovyan/ooi/kdata/RS03ECAL-MJ03E-06-BOTPTA302-streamed-botpt_nano_sample_15s/` |
| MJ03F | Central Caldera (max uplift) | `/home/jovyan/ooi/kdata/RS03CCAL-MJ03F-05-BOTPTA301-streamed-botpt_nano_sample_15s/` |

- **Format**: netCDF files
- **Time period**: 2015-01-01 to 2026-01-16

## Technical Environment

- **Language**: Python 3.12
- **Package manager**: uv
- **Key packages**: xarray, pandas, matplotlib, netcdf4, pyarrow
- **Working directory**: `/home/jovyan/repos/specKitScience/my-analysis_botpt/`

## Pressure-to-Depth Conversion

`depth_m = (pressure_psia - 14.7) * 0.670`

## Quality Control: Spike Removal

Spikes are removed using Median Absolute Deviation (MAD), which is more robust to outliers than standard deviation.

### Algorithm

1. Calculate rolling median over 24-hour centered window
2. Compute absolute deviation from rolling median for each point
3. Calculate rolling MAD (median of absolute deviations)
4. Scale MAD by 1.4826 to approximate standard deviation (for normal distributions, std ≈ 1.4826 × MAD)
5. Flag points where deviation > threshold × scaled_MAD
6. Replace flagged points with NaN

### Thresholds

| Data | Threshold | Rationale |
|------|-----------|-----------|
| Individual station depth | 5.0 | Conservative; catches obvious sensor glitches |
| Differential signal | 3.5 | More aggressive; catches glitches that appear when one sensor spikes but not the other |

### Why MAD over Standard Deviation?

- Standard deviation is sensitive to extreme values—a single large spike inflates the std, making other spikes harder to detect
- MAD uses medians, so outliers have minimal influence on the threshold calculation

## Eruption Threshold Reference

The 2015 pre-eruption differential is used as a reference threshold for forecasting. Key observations:
- **2015 eruption threshold**: ~30 cm higher than the 2011 threshold
- **Threshold uncertainty**: ±30 cm bands reflect this variability
- **Forecasting caveat**: "the pattern could change" (per Axial research team)

## Outputs

All outputs in the `outputs/` directory:

### Data Products (`outputs/data/`)

| File | Description |
|------|-------------|
| `differential_uplift_hourly.parquet` | Hourly cleaned data with `depth_mj03e_m`, `depth_mj03f_m`, `differential_m` |
| `differential_uplift_daily.parquet` | Daily averaged data with same columns |

### Figures (`outputs/figures/`)

| File | Description |
|------|-------------|
| `depth_mj03e.png` | Time series of Eastern Caldera depth (meters) |
| `depth_mj03f.png` | Time series of Central Caldera depth (meters) |
| `differential_uplift.png` | Differential uplift (MJ03F - MJ03E) with 2015 threshold and ±30 cm uncertainty bands |

### Usage

```python
import pandas as pd
bpr = pd.read_parquet('outputs/data/differential_uplift_daily.parquet')
other = pd.read_parquet('other_instrument.parquet')
merged = bpr.join(other, how='inner')
```

## Project Structure

```
my-analysis_botpt/
├── .gitignore
├── .venv/                          # uv virtual environment
├── pyproject.toml                  # uv dependencies
├── uv.lock                         # Locked dependencies
├── analysis.py                     # Main analysis script
├── .specify/
│   ├── features/001-differential-uplift/
│   │   ├── plan.md
│   │   ├── spec.md
│   │   └── tasks.md
│   └── memory/
│       └── constitution.md         # This document
└── outputs/
    ├── constitution.pdf
    ├── data/
    │   ├── differential_uplift_daily.parquet
    │   └── differential_uplift_hourly.parquet
    ├── figures/
    │   ├── depth_mj03e.png
    │   ├── depth_mj03f.png
    │   └── differential_uplift.png
    └── notebooks/                  # Documentation only
        ├── README.md
        ├── differential_uplift_analysis.ipynb
        └── environment.yml
```

## Running the Analysis

```bash
# Install dependencies (first time)
uv sync

# Run analysis
uv run python analysis.py
```

## References

- Nooner, S. L., & Chadwick, W. W. (2016). Inflation-predictable behavior and co-eruption deformation at Axial Seamount. *Science*, 354(6318), 1399-1403.
- Axial Seamount Blog: https://axial.ceoas.oregonstate.edu/axial_blog.html
- OOI Cabled Array: https://oceanobservatories.org/array/cabled-array/

## Notes

- Swap xarray dimensions: `ds.swap_dims({'obs': 'time'})`
