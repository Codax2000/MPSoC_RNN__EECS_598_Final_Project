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
You should be able to run Vivado based in the `vivado_project` folder, which is the toplevel folder for the FPGA design. Note that only the project structure and the source files are kept when you push due to the .gitignore file, so you will have to recompile upon cloning or pulling from the repository.

When opening the project for the first time, you should navigate to the `vivado_project` folder and open the `vivado_project.xpr` file, and Vivado should open the rest. To test that the project runs correctly, run the `sim_1` simulation, which runs a simple 8-bit adder that has an output register, and you should see this waveform:

![Vivado adder waveform](pictures/simulation_waveforms/simple_adder_tb_waveform.png)

## Best Practices

### Python Style
- Up to use, but probably stick to `flake8` linting standards
- Please make sure you have function and file comments

### Vivado Best Practices
- Kindly use Vivado to create files. It manages the directory for you and stores it in the `vivado_project.srcs` folder.
- Git only tracks the `.xpr` project file and the `vivado_project.srcs` folder. If there are any other folders that Git starts tracking (except for eventual physical constraints), please add them to the .gitignore file.
- Have a separate simulation set for each simulation you want to run. This ensures you can still go back and debug if a higher-level simulation goes wrong.
- Use Vivado IP where possible, especially with multiply-accumulate functions. Vivado has a DSP slice macro that can make life much easier.