#!/usr/bin/env python3
"""
analysis.py - Differential uplift analysis for Axial Seamount

Loads BPR data from MJ03E and MJ03F, converts pressure to depth,
computes differential uplift, and generates figures.

Sign Convention:
    We compute -(depth_F - depth_E) which is equivalent to (uplift_F - uplift_E).
    This matches the Axial research team's geophysical convention where:
    - Positive values = inflation (uplift at caldera center relative to rim)
    - Negative values = deflation (subsidence at caldera center relative to rim)

    The figure references data to the 2015 pre-eruption threshold, so:
    - 0 = the 2015 eruption threshold
    - Values above 0 = inflated beyond the 2015 threshold
    - Values below 0 = deflated relative to threshold

Instrument Drift:
    BPRs exhibit long-term drift (typically 1-10 cm/year). The differential
    measurement (F minus E) cancels common-mode drift affecting both sensors.
    Any differential drift between sensors would appear as a spurious trend.
    This analysis does not apply drift corrections; users should validate
    long-term trends against campaign pressure measurements when available.

Usage:
    uv run python analysis.py
"""

import re
from pathlib import Path
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Data paths
MJ03E_PATH = Path("/home/jovyan/ooi/kdata/RS03ECAL-MJ03E-06-BOTPTA302-streamed-botpt_nano_sample_15s")
MJ03F_PATH = Path("/home/jovyan/ooi/kdata/RS03CCAL-MJ03F-05-BOTPTA301-streamed-botpt_nano_sample_15s")

# Output directories
OUTPUT_DIR = Path("/home/jovyan/repos/specKitScience/my-analysis_botpt/outputs")
DATA_DIR = OUTPUT_DIR / "data"
FIGURES_DIR = OUTPUT_DIR / "figures"

# Time range
TIME_START = "2015-01-01"
TIME_END = "2026-01-16"
TIME_START_YEAR = 2015
TIME_END_YEAR = 2026


def pressure_to_depth(pressure_psia):
    """Convert pressure in psia to depth in meters."""
    return (pressure_psia - 14.7) * 0.670


def remove_spikes(series: pd.Series, window_hours: int = 24, threshold: float = 5.0) -> pd.Series:
    """Remove spikes using rolling median and MAD (median absolute deviation).

    MAD is more robust to outliers than standard deviation.

    Args:
        series: Hourly depth time series
        window_hours: Rolling window size in hours
        threshold: Number of MADs for spike threshold

    Returns:
        Series with spikes replaced by NaN
    """
    cleaned = series.copy()

    # Use median (robust to outliers)
    rolling_median = cleaned.rolling(window=window_hours, center=True, min_periods=1).median()

    # Calculate MAD (median absolute deviation) - more robust than std
    deviation = (cleaned - rolling_median).abs()
    rolling_mad = deviation.rolling(window=window_hours, center=True, min_periods=1).median()

    # Scale MAD to be comparable to std (for normal distribution, std ≈ 1.4826 * MAD)
    scaled_mad = 1.4826 * rolling_mad

    # Flag values more than threshold MADs from rolling median
    is_spike = deviation > (threshold * scaled_mad)

    n_spikes = is_spike.sum()
    if n_spikes > 0:
        print(f"    Removed {n_spikes} spikes ({100*n_spikes/len(series):.2f}%)")
        cleaned[is_spike] = pd.NA

    return cleaned


def filter_files_by_time_range(nc_files: list[Path]) -> list[Path]:
    """Filter NetCDF files to those covering the target time range (15s data only)."""
    filtered = []
    pattern = re.compile(r"_15s_(\d{4})\d{4}T\d{6}-(\d{4})\d{4}T")

    for f in nc_files:
        # Only include 15s sample files
        if "_15s_" not in f.name:
            continue

        match = pattern.search(f.name)
        if match:
            start_year = int(match.group(1))
            end_year = int(match.group(2))
            # Include file if it overlaps with our time range
            if start_year <= TIME_END_YEAR and end_year >= TIME_START_YEAR:
                filtered.append(f)

    return sorted(filtered)


def load_station(data_path: Path, station_name: str) -> pd.Series:
    """Load pressure data for a station, filtered to time range, resampled to hourly."""
    all_files = sorted(data_path.glob("*.nc"))
    nc_files = filter_files_by_time_range(all_files)

    print(f"{station_name}: Loading {len(nc_files)} files")

    hourly_chunks = []

    for i, f in enumerate(nc_files):
        if i % 50 == 0:
            print(f"  Processing file {i+1}/{len(nc_files)}...")

        # Load single file
        ds = xr.open_dataset(f, engine="netcdf4")
        ds = ds.swap_dims({"obs": "time"})

        # Filter to time range
        ds = ds.sel(time=slice(TIME_START, TIME_END))

        if len(ds.time) == 0:
            ds.close()
            continue

        # Get pressure, convert to depth, resample to hourly (reduces memory)
        pressure = ds["bottom_pressure"].values
        time = ds["time"].values
        ds.close()

        # Create series and resample
        depth = pressure_to_depth(pressure)
        series = pd.Series(depth, index=pd.DatetimeIndex(time))
        hourly = series.resample("1h").mean()
        hourly_chunks.append(hourly)

    # Concatenate all chunks
    result = pd.concat(hourly_chunks).sort_index()
    result = result[~result.index.duplicated(keep="first")]

    print(f"{station_name}: {len(result)} hourly observations")

    # Remove spikes using 24-hour rolling window, MAD threshold
    result = remove_spikes(result, window_hours=24, threshold=5.0)

    return result


def plot_depth(depth: pd.Series, station: str, filename: str, color: str):
    """Plot depth time series for a single station."""
    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(depth.index, depth.values, color=color, linewidth=0.5)
    ax.set_xlabel("Date")
    ax.set_ylabel("Depth (m)")
    ax.set_title(f"{station} Depth")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.invert_yaxis()  # Depth increases downward
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=150)
    plt.close()
    print(f"Saved: figures/{filename}")


def compute_differential(depth_e: pd.Series, depth_f: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute differential uplift and return hourly and daily DataFrames.

    Sign convention for DEPTH difference:
    We compute -(depth_F - depth_E) = depth_E - depth_F

    This gives intuitive interpretation:
    - Positive/increasing = inflation (F is shallower, uplifted)
    - Negative/decreasing = deflation (F is deeper, subsided)

    Note: The Axial team's "F minus E" convention refers to uplift/displacement,
    not depth. Since depth_F decreases when F uplifts, we negate to match
    their sign convention for the geophysical signal.

    Returns:
        Tuple of (hourly_df, daily_df) with columns for both stations and differential
    """
    # Align on common time index
    combined = pd.DataFrame({
        "depth_mj03e_m": depth_e,
        "depth_mj03f_m": depth_f
    }).dropna()

    # Calculate differential: -(depth_F - depth_E) so positive = inflation
    # Equivalent to: uplift_F - uplift_E (Axial team convention)
    combined["differential_m"] = -(combined["depth_mj03f_m"] - combined["depth_mj03e_m"])

    # Remove spikes from the differential signal
    print("  Filtering spikes from differential signal...")
    combined["differential_m"] = remove_spikes(combined["differential_m"], window_hours=24, threshold=3.5)

    # Create daily version
    daily = combined.resample("1D").mean()

    return combined, daily


def export_parquet(hourly_df: pd.DataFrame, daily_df: pd.DataFrame):
    """Export cleaned data to Parquet files for easy integration with other datasets."""
    hourly_path = DATA_DIR / "differential_uplift_hourly.parquet"
    daily_path = DATA_DIR / "differential_uplift_daily.parquet"

    hourly_df.to_parquet(hourly_path)
    daily_df.to_parquet(daily_path)

    print(f"Exported: data/{hourly_path.name} ({len(hourly_df)} rows)")
    print(f"Exported: data/{daily_path.name} ({len(daily_df)} rows)")


def plot_differential(daily_df: pd.DataFrame, filename: str):
    """Plot differential uplift with eruption threshold and annotations.

    Data is referenced to the 2015 pre-eruption threshold, so:
    - 0 = the 2015 eruption threshold
    - Positive values = inflation above threshold
    - Negative values = deflation below threshold

    The plotted quantity is (uplift_F - uplift_E), equivalent to -(depth_F - depth_E).
    This matches the Axial team convention where positive = inflation at caldera center.
    """
    uplift_daily = daily_df["differential_m"]

    # Find 2015 pre-eruption high (before April 24, 2015 eruption)
    # This becomes our reference datum (threshold = 0)
    pre_eruption = uplift_daily["2015-01-01":"2015-04-23"]
    threshold_2015 = pre_eruption.max()

    # Reference all data to the 2015 threshold
    # Now: 0 = threshold, positive = above threshold, negative = below
    uplift_referenced = uplift_daily - threshold_2015

    # Find post-eruption low for deflation magnitude (in referenced coordinates)
    post_eruption = uplift_referenced["2015-04-24":"2015-06-01"]
    low_2015_ref = post_eruption.min()
    deflation_magnitude = -low_2015_ref  # Make positive for display

    # Current state relative to threshold
    current_value = uplift_referenced.iloc[-1]

    print(f"  2015 eruption threshold (reference datum): {threshold_2015:.2f} m (raw)")
    print(f"  Co-eruption deflation: {deflation_magnitude:.2f} m below threshold")
    print(f"  Current state: {current_value:+.2f} m relative to threshold")
    print(f"  (Note: Total deflation at MJ03F was ~2.4 m; differential is smaller")
    print(f"   because MJ03E also deflects ~1.0 m, consistent with caldera-wide deformation)")

    # Publication-quality figure settings
    plt.rcParams.update({
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
    })

    fig, ax = plt.subplots(figsize=(12, 5))

    # Plot the referenced data
    ax.plot(uplift_referenced.index, uplift_referenced.values,
            color="#2E86AB", linewidth=1, label="Daily mean")

    # Add reference line at threshold (0)
    ax.axhline(y=0, color="red", linestyle="-", linewidth=1.5,
               label="2015 eruption threshold")

    # Add threshold uncertainty bands (±30 cm, based on 2011 vs 2015 threshold difference)
    ax.axhline(y=0.30, color="red", linestyle="--", linewidth=1, alpha=0.7)
    ax.axhline(y=-0.30, color="red", linestyle="--", linewidth=1, alpha=0.7,
               label="Historical threshold range (±30 cm)")

    # Add annotation for the 2015 eruption
    eruption_date = pd.Timestamp("2015-04-24")
    ax.annotate("2015 Eruption\n(Apr 24)",
                xy=(eruption_date, low_2015_ref),
                xytext=(pd.Timestamp("2016-03-01"), low_2015_ref + 0.15),
                fontsize=9, ha='left',
                arrowprops=dict(arrowstyle='->', color='gray', lw=1))

    # Add annotation for deflation magnitude
    ax.annotate(f"Deflation: {deflation_magnitude:.2f} m",
                xy=(pd.Timestamp("2015-07-01"), low_2015_ref / 2),
                xytext=(pd.Timestamp("2016-03-01"), low_2015_ref / 2 - 0.15),
                fontsize=9, ha='left', color='gray',
                arrowprops=dict(arrowstyle='->', color='gray', lw=0.8))

    # Labels and title
    # Title reflects that this is uplift_F - uplift_E (positive = inflation at center)
    ax.set_xlabel("Year")
    ax.set_ylabel("Uplift Relative to 2015 Threshold (m)")
    ax.set_title("Differential Uplift at Axial Seamount")

    # Format x-axis for multi-year data
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator())

    # Clean up the plot
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=9)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=150, facecolor="white", edgecolor="none")
    plt.close()

    # Reset rcParams
    plt.rcParams.update(plt.rcParamsDefault)

    print(f"Saved: figures/{filename}")


def main():
    print("=" * 60)
    print("Differential Uplift Analysis - Axial Seamount")
    print(f"Time range: {TIME_START} to {TIME_END}")
    print("Convention: Positive = inflation at caldera center")
    print("=" * 60)

    # Load data (processes file by file to manage memory)
    print("\nLoading MJ03E (Eastern Caldera)...")
    depth_e = load_station(MJ03E_PATH, "MJ03E")

    print("\nLoading MJ03F (Central Caldera)...")
    depth_f = load_station(MJ03F_PATH, "MJ03F")

    # Compute differential uplift
    print("\nComputing differential uplift...")
    hourly_df, daily_df = compute_differential(depth_e, depth_f)

    # Export to Parquet
    print("\nExporting data...")
    export_parquet(hourly_df, daily_df)

    # Generate plots
    print("\nGenerating plots...")
    plot_depth(depth_e, "MJ03E (Eastern Caldera)", "depth_mj03e.png", "blue")
    plot_depth(depth_f, "MJ03F (Central Caldera)", "depth_mj03f.png", "red")
    plot_differential(daily_df, "differential_uplift.png")

    print("\nDone!")


if __name__ == "__main__":
    main()
