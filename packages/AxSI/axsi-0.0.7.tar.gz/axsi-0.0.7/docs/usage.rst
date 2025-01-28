Usage Guide
===========

Overview
--------

This documentation provides details on how to use the AxSI parser for analyzing MRI data using various input parameters.

Run from Command Line
---------------------

To execute the program via the command line, use the following syntax:

.. code-block:: bash

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

Required Arguments:
~~~~~~~~~~~~~~~~~~~

- **--subj-folder**: Path to the subject folder
- **--data**: Path to the data file
- **--bval**: Path to the bval file
- **--bvec**: Path to the bvec file
- **--mask**: Path to the mask file

Optional Arguments:
~~~~~~~~~~~~~~~~~~~

- **--small-delta** *(default: 15)*: Gradient duration in milliseconds.
- **--big-delta** *(default: 45)*: Time to scan (time interval) in milliseconds.
- **--gmax** *(default: 7.9)*: Gradient maximum amplitude in G/cm.
- **--gamma-val** *(default: 4257)*: Gyromagnetic ratio.
- **`--num-processes-pred`** *(default: 1)*: Number of processes to run in parallel in prediction step.
- **`--num-threads-pred`** *(default: 1)*: Number of threads to run in parallel in prediction step.
- **`--num-processes-axsi`** *(default: 1)*: Number of processes to run in parallel in AxSI step.
- **`--num-threads-axsi`** *(default: 1)*: Number of threads to run in parallel in AxSI step.
- **--linear-lsq-method** *(default: R-quadprog)*: Method for linear least squares. **Choices**: `R-quadprog`, `gurobi`, `scipy`, `cvxpy`
- **--nonlinear-lsq-method** *(default: R-minpack)*: Method for linear least squares. **Choices**: `R-minpack`, `scipy`, `lsq-axsi`
- **--debug-mod**: Enable debug mode. If not provided, debug mode is disabled by default.



