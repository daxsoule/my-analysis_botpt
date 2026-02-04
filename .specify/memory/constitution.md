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

This linear approximation ignores seawater compressibility, temperature, and salinity effects.
For differential measurements these factors largely cancel between stations.

## Instrument Drift Considerations

BPRs exhibit long-term drift (typically 1-10 cm/year). The differential measurement
(uplift_F - uplift_E) cancels common-mode drift affecting both sensors equally.

**Limitations:**
- Any **differential drift** between MJ03E and MJ03F would appear as a spurious trend
- This analysis does **not** apply drift corrections
- Long-term trends should be validated against campaign pressure measurements (ROV-based calibrations) when available
- The OOI team performs periodic calibrations; check data quality notes for specific time periods

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

## Differential Uplift Figure

![Differential Uplift at Axial Seamount](outputs/figures/differential_uplift.png)

The figure shows differential uplift at Axial Seamount from 2015-2026, referenced to the 2015 pre-eruption threshold:

- **Y-axis**: Uplift relative to 2015 threshold (0 = threshold level)
- **Red solid line**: 2015 eruption threshold
- **Red dashed lines**: Historical threshold range (±30 cm based on 2011 vs 2015 difference)
- **Blue line**: Daily mean differential uplift

### Key Features Visible

1. **April 2015 Eruption**: Sharp deflation of ~1.4 m (differential) following the eruption
2. **Post-eruption recovery**: Steady re-inflation from 2015-2026
3. **Current state** (early 2026): ~0.2 m above the 2015 threshold

### Interpretation

The volcano has re-inflated past the 2015 pre-eruption level, entering the historical threshold range where previous eruptions have occurred. However, eruption thresholds vary between cycles, and "the pattern could change."

## Validation Against Published Data

### Comparison with Axial Research Team Results

Our uncorrected analysis was compared against the Axial team's drift-corrected results for the period 2022-Oct 2025:

| Metric | Axial Team (corrected) | Our Analysis (uncorrected) | Difference |
|--------|------------------------|---------------------------|------------|
| 2022 value | ~2.2 m | 1.29 m | 0.9 m |
| Oct 2025 value | ~2.6 m | 1.55 m | 1.05 m |
| Change 2022→Oct 2025 | ~0.4 m | 0.26 m | 0.14 m |

Reference: https://axial.ceoas.oregonstate.edu/Blog_images/Axial-corrected-NANO-DIFF-uplift-2022-Oct2025.png

### Discrepancy Analysis

The ~1 m offset and ~35% rate difference are likely due to:

1. **Drift corrections**: The Axial team applies corrections using campaign pressure measurements (ROV-based calibrations). Our analysis uses raw, uncorrected data.

2. **Pressure-to-depth conversion**: We use a simple linear factor (0.670 m/psi). The Axial team may use a more sophisticated equation of state.

3. **Additional corrections**: The Axial team may apply tidal models, oceanographic adjustments, or other corrections not included here.

### Implications

- **Relative patterns** (inflation/deflation timing, rate changes) are reliable
- **Absolute values** should be treated with caution and validated against published results
- For publication-quality work, drift corrections using campaign calibration data are recommended

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
| `differential_uplift.png` | Differential uplift referenced to 2015 threshold with ±30 cm historical range |

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
