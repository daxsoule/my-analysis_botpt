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
TIME_END = "2015-12-31"


def pressure_to_depth(pressure_psia):
    """Convert pressure in psia to depth in meters."""
    return (pressure_psia - 14.7) * 0.670


def filter_files_by_year(nc_files: list[Path], year: int) -> list[Path]:
    """Filter NetCDF files to those covering the target year (15s data only)."""
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
            if start_year <= year and end_year >= year:
                filtered.append(f)

    return sorted(filtered)


def load_station(data_path: Path, station_name: str) -> pd.Series:
    """Load pressure data for a station, filtered to 2015, resampled to hourly."""
    all_files = sorted(data_path.glob("*.nc"))
    nc_files = filter_files_by_year(all_files, 2015)

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


def plot_differential(depth_e: pd.Series, depth_f: pd.Series, filename: str):
    """Plot differential uplift (MJ03F - MJ03E)."""
    fig, ax = plt.subplots(figsize=(10, 4))

    # Align on common time index
    combined = pd.DataFrame({"e": depth_e, "f": depth_f}).dropna()
    differential = combined["f"] - combined["e"]

    ax.plot(differential.index, differential.values, color="purple", linewidth=0.5)
    ax.set_xlabel("Date")
    ax.set_ylabel("Differential Depth (m)")
    ax.set_title("Differential Uplift (MJ03F - MJ03E) - 2015")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300)
    plt.close()
    print(f"Saved: {filename}")


def main():
    print("=" * 60)
    print("Differential Uplift Analysis - Axial Seamount 2015")
    print("=" * 60)

    # Load data (processes file by file to manage memory)
    print("\nLoading MJ03E (Eastern Caldera)...")
    depth_e = load_station(MJ03E_PATH, "MJ03E")

    print("\nLoading MJ03F (Central Caldera)...")
    depth_f = load_station(MJ03F_PATH, "MJ03F")

    # Generate plots
    print("\nGenerating plots...")
    plot_depth(depth_e, "MJ03E (Eastern Caldera)", "depth_mj03e_2015.png", "blue")
    plot_depth(depth_f, "MJ03F (Central Caldera)", "depth_mj03f_2015.png", "red")
    plot_differential(depth_e, depth_f, "differential_uplift_2015.png")

    print("\nDone!")


if __name__ == "__main__":
    main()
