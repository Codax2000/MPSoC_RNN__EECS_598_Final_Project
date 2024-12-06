# make          <- runs dve

all:	dve

##### 
# Modify starting here
#####

TB_NAME = cordic_divide_tb.sv
TESTBENCH = $(shell find . -name $(TB_NAME))
# Uncomment if you have a limited number of files to compile, better to not though if possible
DESIGN_NAME = afb_linear_handshake.sv
DESIGN_DIR = $(shell find . -name $(DESIGN_NAME))
# Uncomment to compile the whole design_sources directory, currently broken due to memory
# DESIGN_DIR = $(shell find ./hdl_design/hdl_design.srcs/design_sources -name "*.sv" -o -name "*.v")
VCS = SW_VCS=2023.12-SP2-1 vcs -sverilog +vc -Mupdate -line -full64 +define+SYNOPSIS

# Synthesis variables
export MK_COURSE_NAME = EECS598-002

# your top-level module name
export MK_DESIGN_NAME = lstm_layer

# CPU core usage, capped at 6
export MK_USE_NUM_CORES = 4

# memory library selection
export MK_MEM_SUFFIX = typ_1d05_25

#####
# Should be no need to modify after here
#####
.PHONY: dve clean nuke memgen

dve:	 
	$(VCS) $(DESIGN_DIR) $(TESTBENCH) -o dve -R -gui -debug_acccess+all -kdb | tee dve.log

syn: 
	-mkdir -p logs
	dc_shell -f synth_scripts/synth.tcl | tee logs/synth.log
	-mkdir -p temp_files
	-mv alib-52 temp_files/
	-mv *_dclib temp_files/
	-mv command.log temp_files/
	-mv default.svf temp_files/
	-mkdir -p export
	-cp -f memory/db/*_${MK_MEM_SUFFIX}_ccs.db export/ 2>>/dev/null
	
memgen:
	cd hdl_design/pdk_mem; ./memgen.sh; cd ../..

clean:
	rm -rvf simv *.daidir csrc vcs.key program.out \
	syn_simv syn_simv.daidir syn_program.out \
	dve *.vpd *.vcd *.dump ucli.key \
        inter.fsdb novas* verdiLog \
	hdl_design/pdk_mem/db hdl_design/pdk_mem/results results \
	reports verdi_config_file default.svf filenames.log logs \
	temp_files export

nuke:	clean
	rm -rvf *.vg *.rep *.db *.chk *.log *.out *.ddc *.svf DVEfiles/
