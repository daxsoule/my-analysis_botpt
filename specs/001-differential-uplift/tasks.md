# Tasks: Differential Uplift 2015

**Spec**: `specs/001-differential-uplift/spec.md`
**Plan**: `specs/001-differential-uplift/plan.md`
**Generated**: 2026-01-24

## Format

```text
- [ ] T### Description with file path or specific action
```

---

## Phase 1: Setup

**Purpose**: Verify environment and clean up old files

- [ ] T001 Verify requirements.txt has necessary packages (xarray, pandas, matplotlib, netcdf4)
- [ ] T002 Remove old `.specify/scripts/` files from previous iteration

**Checkpoint**: Environment ready, project root clean

---

## Phase 2: Implementation

**Purpose**: Create the analysis script

- [ ] T003 Create `analysis.py` with data loading for MJ03E and MJ03F (2015 only)
- [ ] T004 Add pressure-to-depth conversion: `depth_m = (pressure_psia - 14.7) * 0.670`
- [ ] T005 Add plotting function for MJ03E depth time series
- [ ] T006 Add plotting function for MJ03F depth time series
- [ ] T007 Add plotting function for differential uplift (MJ03F - MJ03E)
- [ ] T008 Run `analysis.py` and verify execution completes without errors

**Checkpoint**: Script runs, three PNG files generated

---

## Phase 3: Verification

**Purpose**: Confirm outputs are correct

- [ ] T009 QC: Verify `depth_mj03e_2015.png` exists and shows reasonable depth values (~1500-1600m)
- [ ] T010 QC: Verify `depth_mj03f_2015.png` exists and shows reasonable depth values (~1500-1600m)
- [ ] T011 QC: Verify `differential_uplift_2015.png` exists and shows expected uplift pattern

**Checkpoint**: All three plots visually verified

---

## Dependencies

```text
Phase 1 (Setup)
     ↓
Phase 2 (Implementation)
     ↓
Phase 3 (Verification)
```

---

## Completion Criteria

- [ ] Three PNG files in project root:
  - `depth_mj03e_2015.png`
  - `depth_mj03f_2015.png`
  - `differential_uplift_2015.png`
- [ ] Plots show 2015 data with depth in meters
- [ ] Script is reproducible (can delete outputs and regenerate)
