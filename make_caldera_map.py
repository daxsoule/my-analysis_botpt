#!/usr/bin/env python3
"""
make_caldera_map.py - Generate shaded relief map of Axial Seamount caldera

Creates a publication-quality bathymetric map showing the summit caldera
with shaded relief illumination, depth contours, and instrument locations.

Usage:
    uv run python make_caldera_map.py
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from pathlib import Path

# Paths
BATHY_PATH = Path("/home/jovyan/my_data/axial/axial_bathy/MBARI_AxialSeamount_V2506_AUV_Summit_AUVOverShip_Topo1mSq.grd")
OUTPUT_DIR = Path("/home/jovyan/repos/specKitScience/my-analysis_botpt/outputs/figures")

# BPR station locations (verified from OOI NetCDF metadata)
STATIONS = {
    "MJ03F": {"lon": -130.008772, "lat": 45.95485, "label": "MJ03F\n(Central Caldera)"},
    "MJ03E": {"lon": -129.974113, "lat": 45.939888, "label": "MJ03E\n(Eastern Caldera)"},
}

# Vent field locations (from user-provided coordinates, converted to decimal degrees)
# Format: degrees + minutes/60
VENTS = {
    "ASHES": {"lon": -(130 + 0.8203/60), "lat": 45 + 56.0186/60},           # 45°56.0186'N, 130°00.8203'W
    "Coquille": {"lon": -(129 + 59.5793/60), "lat": 45 + 55.0448/60},       # 45°55.0448'N, 129°59.5793'W
    "Int'l District": {"lon": -(129 + 58.7394/60), "lat": 45 + 55.5786/60}, # 45°55.5786'N, 129°58.7394'W
    "Trevi": {"lon": -(129 + 59.023/60), "lat": 45 + 56.777/60},            # 45°56.777'N, 129°59.023'W
}


# Caldera extent for zoom (approximate rim coordinates)
# Center caldera with 2 km buffer (~0.018° lat, ~0.026° lon at this latitude)
CALDERA_CENTER = {"lon": -129.99, "lat": 45.945}
BUFFER_KM = 2.5  # km buffer around caldera
# At 46°N: 1° lat ≈ 111 km, 1° lon ≈ 77 km
LAT_PER_KM = 1 / 111.0
LON_PER_KM = 1 / 77.0


def load_bathymetry(path: Path, subsample: int = 1, extent: dict = None) -> tuple:
    """Load bathymetry data, optionally subsampling and clipping to extent."""
    print(f"Loading bathymetry from {path.name}...")
    ds = xr.open_dataset(path)

    # Clip to extent if provided
    if extent:
        ds = ds.sel(lon=slice(extent['lon_min'], extent['lon_max']),
                    lat=slice(extent['lat_min'], extent['lat_max']))
        print(f"  Clipped to extent: {extent['lon_min']:.3f} to {extent['lon_max']:.3f}°E, "
              f"{extent['lat_min']:.3f} to {extent['lat_max']:.3f}°N")

    if subsample > 1:
        ds = ds.isel(lon=slice(None, None, subsample), lat=slice(None, None, subsample))
        print(f"  Subsampled by {subsample}x")

    lon = ds.coords['lon'].values
    lat = ds.coords['lat'].values
    z = ds['z'].values

    print(f"  Grid size: {len(lon)} x {len(lat)}")
    print(f"  Depth range: {np.nanmin(z):.0f} to {np.nanmax(z):.0f} m")

    ds.close()
    return lon, lat, z


def plot_caldera_map(lon, lat, z, output_path: Path, subsample: int = 1):
    """Create shaded relief map of the caldera with annotations."""

    print("Creating shaded relief map...")

    # Set up figure
    fig, ax = plt.subplots(figsize=(10, 10))

    # Create meshgrid for contours
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    # Create shaded relief
    ls = LightSource(azdeg=315, altdeg=45)
    z_min, z_max = np.nanpercentile(z, [2, 98])

    rgb = ls.shade(z, cmap=plt.cm.terrain, blend_mode='soft',
                   vmin=z_min, vmax=z_max)

    # Plot shaded relief
    ax.imshow(rgb, extent=[lon.min(), lon.max(), lat.min(), lat.max()],
              origin='lower', aspect='equal')

    # Add depth contours
    print("  Adding depth contours...")
    contour_levels = np.arange(-2200, -1400, 50)
    cs = ax.contour(lon_grid, lat_grid, z, levels=contour_levels,
                    colors='black', linewidths=0.5, alpha=0.6)
    # Label contours
    ax.clabel(cs, levels=contour_levels[::2], fontsize=7, fmt='%d m', inline=True)

    # Add vent locations
    print("  Adding vent locations...")
    # Label offsets to avoid overlap
    label_offsets = {
        "ASHES": (-60, 5),
        "Coquille": (-65, -5),
        "Int'l District": (10, -5),
        "Trevi": (10, 5),
    }
    for name, info in VENTS.items():
        ax.plot(info['lon'], info['lat'], 'yo', markersize=10,
                markeredgecolor='black', markeredgewidth=1.5, zorder=8)
        offset = label_offsets.get(name, (10, 5))
        ax.annotate(name, (info['lon'], info['lat']),
                    xytext=offset, textcoords='offset points',
                    fontsize=8, style='italic', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow',
                             alpha=0.8, edgecolor='none'),
                    zorder=11)

    # Add BPR station markers
    print("  Adding BPR stations...")
    for station, info in STATIONS.items():
        ax.plot(info['lon'], info['lat'], 'r^', markersize=14,
                markeredgecolor='white', markeredgewidth=2, zorder=10)
        # Position labels
        if station == "MJ03F":
            offset = (12, 8)
        else:
            offset = (12, -15)
        ax.annotate(info['label'], (info['lon'], info['lat']),
                    xytext=offset, textcoords='offset points',
                    fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                             alpha=0.9, edgecolor='gray'),
                    zorder=12)

    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=plt.cm.terrain,
                                norm=plt.Normalize(vmin=z_min, vmax=z_max))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label('Depth (m)', fontsize=11)

    # Labels and title
    ax.set_xlabel('Longitude', fontsize=11)
    ax.set_ylabel('Latitude', fontsize=11)
    ax.set_title('Axial Seamount Caldera', fontsize=14, fontweight='bold')

    # Add scale bar (1 km)
    scale_lon = lon.min() + 0.005
    scale_lat = lat.min() + 0.005
    scale_length = 1.0 * LON_PER_KM  # 1 km in degrees longitude
    ax.plot([scale_lon, scale_lon + scale_length], [scale_lat, scale_lat],
            'k-', linewidth=4)
    ax.text(scale_lon + scale_length/2, scale_lat + 0.003, '1 km',
            ha='center', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9))

    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='^', color='w', markerfacecolor='red',
               markersize=12, markeredgecolor='white', markeredgewidth=1.5,
               label='BPR Stations'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow',
               markersize=10, markeredgecolor='black', markeredgewidth=1.5,
               label='Vent Fields'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10,
              framealpha=0.95)

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', color='white')

    plt.tight_layout()

    # Save
    resolution_note = f"_{subsample}x" if subsample > 1 else ""
    output_file = output_path / f"caldera_map{resolution_note}.png"
    plt.savefig(output_file, dpi=600, facecolor='white', bbox_inches='tight')
    plt.close()

    print(f"Saved: {output_file}")
    return output_file


def main():
    print("=" * 60)
    print("Axial Seamount Caldera Map")
    print("=" * 60)
    print("\nVent coordinates provided by user.")
    print("BPR station coordinates verified from OOI data.\n")

    # Center on MJ03F, trimmed extent
    # MJ03F location: lon=-130.008772, lat=45.95485
    # At 46°N: 1 km ≈ 0.009° lat, 1 km ≈ 0.013° lon
    center_lon = -130.008772  # MJ03F longitude
    center_lat = 45.95485     # MJ03F latitude
    half_width = 0.064        # ~5 km half-width (trimmed 2 km per side)
    half_height = 0.061       # ~6.8 km half-height (trimmed 1 km per side)

    extent = {
        'lon_min': center_lon - half_width,
        'lon_max': center_lon + half_width,
        'lat_min': center_lat - half_height,
        'lat_max': center_lat + half_height,
    }

    # Generate full resolution version (1m)
    print("Generating full resolution map (1m)...")
    subsample = 1

    lon, lat, z = load_bathymetry(BATHY_PATH, subsample=subsample, extent=extent)
    output_file = plot_caldera_map(lon, lat, z, OUTPUT_DIR, subsample=subsample)

    print("\nDone!")


if __name__ == "__main__":
    main()
