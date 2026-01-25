#!/usr/bin/env python3
"""
analysis.py - Differential uplift analysis for Axial Seamount (2015)

Loads BPR data from MJ03E and MJ03F, converts pressure to depth,
and generates three time series plots.
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

# Output directory (project root)
OUTPUT_DIR = Path("/home/jovyan/repos/specKitScience/my-analysis_botpt")

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

    for f in nc_files:
        print(f"  Processing {f.name}...")

        # Load single file
        ds = xr.open_dataset(f, engine="netcdf4")
        ds = ds.swap_dims({"obs": "time"})

        # Filter to 2015
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
    ax.set_title(f"{station} Depth - 2015")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.invert_yaxis()  # Depth increases downward
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300)
    plt.close()
    print(f"Saved: {filename}")


def compute_differential(depth_e: pd.Series, depth_f: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute differential uplift and return hourly and daily DataFrames.

    Returns:
        Tuple of (hourly_df, daily_df) with columns for both stations and differential
    """
    # Align on common time index
    combined = pd.DataFrame({
        "depth_mj03e_m": depth_e,
        "depth_mj03f_m": depth_f
    }).dropna()

    # Calculate differential depth: MJ03E - MJ03F (per constitution)
    # Positive values = MJ03E deeper than MJ03F (Central Caldera uplifted)
    combined["differential_m"] = combined["depth_mj03e_m"] - combined["depth_mj03f_m"]

    # Remove spikes from the differential signal
    print("  Filtering spikes from differential signal...")
    combined["differential_m"] = remove_spikes(combined["differential_m"], window_hours=24, threshold=3.5)

    # Create daily version
    daily = combined.resample("1D").mean()

    return combined, daily


def export_parquet(hourly_df: pd.DataFrame, daily_df: pd.DataFrame):
    """Export cleaned data to Parquet files for easy integration with other datasets."""
    hourly_path = OUTPUT_DIR / "differential_uplift_hourly.parquet"
    daily_path = OUTPUT_DIR / "differential_uplift_daily.parquet"

    hourly_df.to_parquet(hourly_path)
    daily_df.to_parquet(daily_path)

    print(f"Exported: {hourly_path.name} ({len(hourly_df)} rows)")
    print(f"Exported: {daily_path.name} ({len(daily_df)} rows)")


def plot_differential(daily_df: pd.DataFrame, filename: str):
    """Plot differential uplift from daily DataFrame."""
    uplift_daily = daily_df["differential_m"]

    # Find 2015 high value for reference line
    uplift_2015 = uplift_daily["2015"]
    high_2015 = uplift_2015.max()

    # Set up publication-quality figure (two-column width: 6" x 3")
    plt.rcParams.update({
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
    })

    fig, ax = plt.subplots(figsize=(6, 3))

    # Plot the data
    ax.plot(uplift_daily.index, uplift_daily.values,
            color="#2E86AB", linewidth=1, label="Daily mean")

    # Add red horizontal line for 2015 high
    ax.axhline(y=high_2015, color="red", linestyle="-", linewidth=1.5,
               label=f"2015 high ({high_2015:.2f} m)")

    # Add red dashed lines at +/- 20 cm from 2015 high
    ax.axhline(y=high_2015 + 0.20, color="red", linestyle="--", linewidth=1, alpha=0.7)
    ax.axhline(y=high_2015 - 0.20, color="red", linestyle="--", linewidth=1, alpha=0.7)

    # Labels and title
    ax.set_xlabel("Year")
    ax.set_ylabel("Differential Depth (m)")
    ax.set_title("Differential Uplift (MJ03E − MJ03F)")

    # Format x-axis for multi-year data
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator())

    # Clean up the plot
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)
    ax.legend(loc="lower right", framealpha=0.9, fontsize=9)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300, facecolor="white", edgecolor="none")
    plt.close()

    # Reset rcParams
    plt.rcParams.update(plt.rcParamsDefault)

    print(f"Saved: {filename}")


def main():
    print("=" * 60)
    print("Differential Uplift Analysis - Axial Seamount")
    print(f"Time range: {TIME_START} to {TIME_END}")
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
