# Usage Guide

## Overview

This documentation provides details on how to use the AxSI parser for analyzing MRI data using various input parameters.

## Run from Command Line

To execute the program via the command line, use the following syntax:

```bash
AxSI_main.py \
  --subj-folder /path/to/subject_folder \
  --data /path/to/data.nii.gz \
  --bval /path/to/bval.bval \
  --bvec /path/to/bvec.bvec \
  --mask /path/to/mask.nii.gz \
  --small-delta 20 \
  --big-delta 50 \
  --gmax 8.0 \
  --gamma-val 4258 \
  --num-processes-pred 35 \
  --num-threads-axsi 35 \
  --linear-lsq-method gurobi \
  --nonlinear-lsq-method scipy \
  --debug-mode
```

### Required Arguments

- **`--subj-folder`**: Path to the subject folder
- **`--data`**: Path to the data file
- **`--bval`**: Path to the bval file
- **`--bvec`**: Path to the bvec file
- **`--mask`**: Path to the mask file

### Optional Arguments

- **`--small-delta`** *(default: 15)*: Gradient duration in milliseconds.
- **`--big-delta`** *(default: 45)*: Time to scan (time interval) in milliseconds.
- **`--gmax`** *(default: 7.9)*: Gradient maximum amplitude in G/cm.
- **`--gamma-val`** *(default: 4257)*: Gyromagnetic ratio.
- **`--num-processes-pred`** *(default: 1)*: Number of processes to run in parallel in prediction step.
- **`--num-threads-pred`** *(default: 1)*: Number of threads to run in parallel in prediction step.
- **`--num-processes-axsi`** *(default: 1)*: Number of processes to run in parallel in AxSI step.
- **`--num-threads-axsi`** *(default: 1)*: Number of threads to run in parallel in AxSI step.
- **`--linear-lsq-method`** *(default: R-quadprog)*: Method for linear least squares. **Choices
  **: `R-quadprog`, `gurobi`, `scipy`, `cvxpy`
- **`--nonlinear-lsq-method`** *(default: R-minpack)*: Method for nonlinear least squares. **Choices
  **: `R-minpack`, `scipy`, `lsq-axsi`
- **`--debug-mode`**: Enable debug mode. If not provided, debug mode is disabled by default.


# NIfTI Viewer

## Overview

This is a Dash-based web application that allows users to interactively visualize slices of 3D or 4D NIfTI files (
commonly used in neuroimaging). Users can select slices along different axes, apply various color maps, and visualize
data dynamically using sliders for timepoints (in 4D data) and slice indices.

## Features

### Input File Handling

- The NIfTI file path is provided as a command-line argument using `argparse`.
- The script loads and processes the provided file using the `nibabel` library.

### Visualization

- Supports visualization along three axes: axial, sagittal, and coronal.
- Provides several color maps (e.g., gray, viridis, plasma) for the visualization.
- Interactive user interface for exploring slices.

### 4D Data Support

- If the input NIfTI file contains 4D data (e.g., time-series or multi-volume data), a slider lets users navigate
  through different timepoints.

### User Controls

- Dropdown menus to select the viewing axis and color map.
- Sliders for selecting specific slices and timepoints.

### Output

- The visualization is rendered as an interactive plot using Plotly.

## Getting Started

Run the script from the command line, providing the NIfTI file path as an argument:

```bash
nifti_viewer.py --nifti_file /path/to/your/file.nii.gz
```

### Example

```bash
nifti_viewer.py --nifti_file example_data/pasi.nii.gz
```

The app runs at [http://127.0.0.1:8050](http://127.0.0.1:8050) by default, displaying the interactive visualization.



Python version
--------------

This project is currently using Python 3.12

Installation
------------

It is recommended to use **virtualenv** to create a clean python environment.

To install lsqAxSI, use **pip**:

    pip install AxSI



Execution
---------

The main script shipped with this project is **AxSI.py**, see its options by running:

    AxSI_main.py -h

