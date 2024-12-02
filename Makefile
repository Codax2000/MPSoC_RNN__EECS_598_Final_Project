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

#####
# Should be no need to modify after here
#####
.PHONY: dve clean nuke

dve:	 
	$(VCS) $(DESIGN_DIR) $(TESTBENCH) -o dve -R -gui -debug_acccess+all -kdb | tee dve.log

clean:
	rm -rvf simv *.daidir csrc vcs.key program.out \
	syn_simv syn_simv.daidir syn_program.out \
	dve *.vpd *.vcd *.dump ucli.key \
        inter.fsdb novas* verdiLog	

nuke:	clean
	rm -rvf *.vg *.rep *.db *.chk *.log *.out *.ddc *.svf DVEfiles/
