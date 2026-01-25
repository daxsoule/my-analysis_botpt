# Differential Uplift Analysis Tasks

## Phase 1: Data Loading

- [ ] **T001**: Create output directory structure
  - Script: `.specify/scripts/00_setup.py`
  - Creates: `outputs/intermediate/`, `outputs/data/`, `outputs/figures/`

- [ ] **T002**: Load and concatenate MJ03E NetCDF files
  - Script: `.specify/scripts/01_load_data.py`
  - Input: `/home/jovyan/ooi/kdata/RS03ECAL-MJ03E-06-BOTPTA302-streamed-botpt_nano_sample_15s/*.nc`
  - Output: `outputs/intermediate/mj03e_raw.zarr`

- [ ] **T003**: Load and concatenate MJ03F NetCDF files
  - Script: `.specify/scripts/01_load_data.py`
  - Input: `/home/jovyan/ooi/kdata/RS03CCAL-MJ03F-05-BOTPTA301-streamed-botpt_nano_sample_15s/*.nc`
  - Output: `outputs/intermediate/mj03f_raw.zarr`

- [ ] **T004**: QC - Verify raw data loaded correctly
  - Check time range covers 2014-2018
  - Check pressure variable exists
  - Report data coverage statistics

## Phase 2: Processing

- [ ] **T005**: Process MJ03E data (convert, QC, resample)
  - Script: `.specify/scripts/02_process_data.py`
  - Convert psia to meters
  - Apply range checks (1500-1600m)
  - Spike detection (>3 sigma)
  - Resample to 1-hour averages
  - Output: `outputs/intermediate/mj03e_processed.zarr`

- [ ] **T006**: Process MJ03F data (convert, QC, resample)
  - Script: `.specify/scripts/02_process_data.py`
  - Same processing as T005
  - Output: `outputs/intermediate/mj03f_processed.zarr`

- [ ] **T007**: QC - Verify processed data
  - Check depth values in expected range
  - Check hourly resampling
  - Report percentage of flagged/removed data

## Phase 3: Analysis

- [ ] **T008**: Calculate differential uplift
  - Script: `.specify/scripts/03_calculate.py`
  - Align time series
  - Calculate: MJ03F - MJ03E
  - Output: `outputs/data/differential_uplift_2014-2018.parquet`

- [ ] **T009**: QC - Verify differential uplift
  - Check for April 2015 eruption signal (rapid deflation)
  - Verify no large gaps in combined time series
  - Summary statistics

## Phase 4: Visualization

- [ ] **T010**: Generate MJ03E depth time series figure
  - Script: `.specify/scripts/04_visualize.py`
  - Output: `outputs/figures/depth_mj03e_2014-2018.png`

- [ ] **T011**: Generate MJ03F depth time series figure
  - Script: `.specify/scripts/04_visualize.py`
  - Output: `outputs/figures/depth_mj03f_2014-2018.png`

- [ ] **T012**: Generate differential uplift time series figure
  - Script: `.specify/scripts/04_visualize.py`
  - Output: `outputs/figures/differential_uplift_2014-2018.png`

- [ ] **T013**: QC - Verify figures meet publication standards
  - 300 DPI resolution
  - Axis labels with units
  - Readable fonts (min 8pt)

## Phase 5: Finalization

- [ ] **T014**: Clean up intermediate files (optional)
  - Remove `outputs/intermediate/` zarr files if space needed

- [ ] **T015**: Document any decisions in research.md
  - Record QC thresholds used
  - Note any data issues encountered
