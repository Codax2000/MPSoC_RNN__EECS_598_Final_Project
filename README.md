# EECS 598 Group Project
Version control for EECS 598 at UMich (go blue!)

## Installation Instructions
You should have Anaconda (Miniconda recommended) and Xilinx Vivado installed. We are designing for the ZCU102 development board.

### Python environment setup and testing
Create a new environment for running the required Python scripts, using:
```
cd python_scripts
conda env create -f environment.yml
```

After that, you can use it by running `conda activate eecs598` on the command line. To test the installation, run:
```
cd test_install
python main.py
```
You should see the output:
```
Foo runs, import successful
Main runs, installation successful!
```

### Vivado setup and testing
You should be able to run Vivado based in the hdl\_design folder, which is the toplevel folder for the FPGA design. Note that only the project structure and the source files are kept when you push due to the .gitignore file, so you will have to recompile upon cloning or pulling from the repository.
